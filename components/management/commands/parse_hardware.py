import time
from django.core.management import BaseCommand
import requests
from bs4 import BeautifulSoup
from components.models import CPU, GPU, Motherboard, RAM, PriceHistory


class Command(BaseCommand):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36'}
    base_url = 'https://www.regard.ru/'
    STOP_WORDS = [
        'threadripper', 'xeon', 'epyc', 'quadro', 'tesla',
        'nvidia a', 'rtx a', 'ecc', 'registered', 'server', 'workstation', 'sodimm',
        'industrial', 'vPro', 'rdimm', 'buff', 'registered', 'box'
    ]

    def is_valid(self, name):
        """Вспомогательный метод для проверки наличия стоп-слов в названии"""
        return not any(word in name.lower() for word in self.STOP_WORDS)

    def get_items(self, url):
        """Вспомогательный метод для получения списка карточек"""
        response = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.find_all('div', class_='Card_wrap__hES44 Card_listing__nGjbk ListingRenderer_listingCard__DqY3k')

    def get_tbody(self, url):
        """Вспомогательный метод для получения тела таблицы"""
        response = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.find_all('tr')

    def create_bench_dict(self, tbody):
        """Вспомогательный метод для создания словаря бенчмарков из videocardbenchmark.net и cpubenchmark.net"""
        bench_dict = {}
        stop_words = ['laptop', 'mobile', 'design']

        for row in tbody:
            cells = row.find_all('td')
            if len(cells) < 2:
                continue

            link = cells[0].find('a')
            if not link:
                continue

            row_name = link.text.strip()

            if any(word in row_name.lower() for word in stop_words):
                continue

            score_text = cells[1].text.replace(',', '')

            if score_text.isdigit():
                bench_dict[row_name.lower()] = int(score_text)

        return bench_dict

    def get_benchmark_score(self, bench_dict, name):
        """Вспомогательный метод для получения бенчмарка из словаря"""
        benchmark_score = 0

        name_lower = name.lower()

        if name_lower in bench_dict:
            benchmark_score = bench_dict[name_lower]
            return benchmark_score

        for key in bench_dict.keys():
            if key in name_lower or name_lower in key:
                benchmark_score = bench_dict[key]
                break

        return benchmark_score

    def handle(self, *args, **options):
        self.parse_cpus()
        self.parse_gpus()
        self.parse_ram()
        self.parse_motherboards()

    def parse_cpus(self):
        cpus_tbody = self.get_tbody('https://www.cpubenchmark.net/cpu_list.php')
        bench_dict = self.create_bench_dict(cpus_tbody)
        for page in range(1,6):
            url = f'https://www.regard.ru/catalog/1001/processory?page={page}&q=eyJzb3J0IjpbIm9yZGVyQnlQcmljZSIsImRlc2MiXX0'
            items = self.get_items(url)

            for item in items:
                url_name = item.find('a', class_='CardText_link__C_fPZ')

                if not self.is_valid(url_name.text):
                    continue

                name = ' '.join(url_name.text.split()[1:-1]).replace(' - ', '-')
                url = self.base_url + url_name.attrs['href']
                socket = item.find('p', class_='CardText_text__fZPl_').text.split(',')[0]
                price = item.find('span', class_='Price_price__m2aSe').text.split()[:-1]
                price = float(''.join(price))
                benchmark_score = self.get_benchmark_score(bench_dict, name)
                cpu_obj, created = CPU.objects.update_or_create(url=url, defaults={'socket': socket, 'benchmark_score': benchmark_score, 'price': price, 'name': name})
                PriceHistory.objects.create(component_id=cpu_obj.id, component_type='cpu', price=price)
            time.sleep(1.5)

    def parse_gpus(self):
        manufacturers = ["Acer", "AFOX", "ASRock", "ASUS", "Biostar", "CBR", "Gigabyte", "HP", "INNO3D", "Maxsun", "MSI", "Palit", "PNY", "Sapphire", "Zotac"]
        pcie_versions = ['5.0', '4.0']
        gb_counts = ['32Gb', '24Gb', '20Gb', '16Gb', '12Gb', '10Gb', '8Gb', '6Gb', '4Gb', '2Gb', '1Gb', '512Mb']
        gpus_tbody = self.get_tbody('https://www.videocardbenchmark.net/gpu_list.php')
        bench_dict = self.create_bench_dict(gpus_tbody)

        for page in range(1,6):
            url = f'https://www.regard.ru/catalog/1013/videokarty?page={page}'
            items = self.get_items(url)

            for item in items:
                url_name = item.find('a', class_='CardText_link__C_fPZ')
                name = ''
                for manufacturer in manufacturers:
                    name = url_name.text
                    if manufacturer in name:
                        name = ' '.join(name.split(f" {manufacturer}")[0].split()[2:])
                        break

                for gb in gb_counts:
                    if gb in url_name.text:
                        name += f" {gb}"
                        break

                if not self.is_valid(name):
                    continue

                url = self.base_url + url_name.attrs['href']
                description = item.find('p', class_='CardText_text__fZPl_').text

                pcie_version = 0.0
                for pcie in pcie_versions:
                    if pcie in description:
                        pcie_version = float(pcie)

                price = item.find('span', class_='Price_price__m2aSe').text.split()[:-1]
                price = float(''.join(price))
                benchmark_score = self.get_benchmark_score(bench_dict, name)
                gpu_obj, created = GPU.objects.update_or_create(url=url, defaults={'pcie_version': pcie_version, 'benchmark_score': benchmark_score,'price':price ,'name': name})
                PriceHistory.objects.create(component_id=gpu_obj.id, component_type='gpu', price=price)
            time.sleep(1.5)

    def parse_ram(self):
        ram_types = ['DDR5', 'DDR4', 'DDR3', 'DDR2']
        ram_bar_counts = {'2 модуля': 2, '4 модуля': 4}

        for page in range(1,6):
            url = f'https://www.regard.ru/catalog/1010/operativnaya-pamyat?page={page}'
            items = self.get_items(url)

            for item in items:
                url_name = item.find('a', class_='CardText_link__C_fPZ')
                name = url_name.text.split(' (')[0].split('z ')[-1]

                if not self.is_valid(name):
                    continue

                url = self.base_url + url_name.attrs['href']
                description = item.find('p', class_='CardText_text__fZPl_').text

                ram_type = ''
                for t in ram_types:
                    if t in description:
                        ram_type = t
                        break

                ram_capacity = int(description.split()[0])

                ram_bar_count = 1
                for count in ram_bar_counts.keys():
                    if count in description:
                        ram_bar_count = ram_bar_counts[count]
                        break

                price = item.find('span', class_='Price_price__m2aSe').text.split()[:-1]
                price = float(''.join(price))
                ram_obj, created = RAM.objects.update_or_create(url=url, defaults={'ram_type': ram_type, 'ram_capacity': ram_capacity, 'ram_bar_count': ram_bar_count,'price': price ,'name': name})
                PriceHistory.objects.create(component_id=ram_obj.id, component_type='ram', price=price)
            time.sleep(1.5)

    def parse_motherboards(self):
        sockets = ["AM4", "AM5", "LGA 1200", "LGA 1700", "LGA 1851", "LGA 775"]
        ram_types = ['DDR5', 'DDR4', 'DDR3', 'DDR2']
        pcie_versions = ['5.0', '4.0']
        ram_slots_versions = ['4xDDR', '2xDDR']

        for page in range(1,6):
            url = f'https://www.regard.ru/catalog/1000/materinskie-platy?page={page}'
            items = self.get_items(url)

            for item in items:
                url_name = item.find('a', class_='CardText_link__C_fPZ')
                name = ' '.join(url_name.text.split()[2:-1])

                if not self.is_valid(name):
                    continue


                url = self.base_url + url_name.attrs['href']
                description = item.find('p', class_='CardText_text__fZPl_').text

                socket = ''
                for s in sockets:
                    if s in description:
                        socket = s
                        break

                ram_type = ''
                for r in ram_types:
                    if r in description:
                        ram_type = r
                        break

                pcie_version = 0.0
                for pcie in pcie_versions:
                    if pcie in description:
                        pcie_version = float(pcie)
                        break

                ram_slots = 0
                for rs in ram_slots_versions:
                    if rs in description:
                        ram_slots = int(rs[0])
                        break

                price = item.find('span', class_='Price_price__m2aSe').text.split()[:-1]
                price = float(''.join(price))
                mb_obj, created = Motherboard.objects.update_or_create(url=url, defaults={'socket': socket, 'ram_type': ram_type, 'pcie_version':pcie_version, 'ram_slots':ram_slots, 'price': price, 'name': name})
                PriceHistory.objects.create(component_id=mb_obj.id, component_type='mb', price=price)
            time.sleep(1.5)