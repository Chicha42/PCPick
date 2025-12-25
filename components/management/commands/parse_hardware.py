from django.core.management import BaseCommand
import requests
from bs4 import BeautifulSoup
from components.models import CPU, GPU, Motherboard, RAM, PriceHistory


class Command(BaseCommand):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36'}
    base_url = 'https://www.regard.ru/'

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

    def get_benchmark_score(self, tbody, name):
        """Вспомогательный метод для получения бенчмарка из videocardbenchmark.net и cpubenchmark.net"""
        benchmark_score = 0
        for row in tbody:
            row_name = row.find('a').text if row.find('a') is not None else ''
            if row_name.lower() == name.lower():
                benchmark_score = int(row.find_all('td')[1].text.replace(',', ''))
                break
        return benchmark_score

    def handle(self, *args, **options):
        self.parse_cpus()
        self.parse_gpus()
        self.parse_ram()
        self.parse_motherboards()

    def parse_cpus(self):
        url = 'https://www.regard.ru/catalog/1001/processory'
        items = self.get_items(url)
        cpus_tbody = self.get_tbody('https://www.cpubenchmark.net/cpu_list.php')

        for item in items:
            url_name = item.find('a', class_='CardText_link__C_fPZ')
            name = ' '.join(url_name.text.split()[1:-1]).replace(' - ', '-')
            url = self.base_url + url_name.attrs['href']
            socket = item.find('p', class_='CardText_text__fZPl_').text.split(',')[0]
            price = item.find('span', class_='Price_price__m2aSe').text.split()[:-1]
            price = float(''.join(price))
            benchmark_score = self.get_benchmark_score(cpus_tbody, name)
            cpu_obj, created = CPU.objects.update_or_create(url=url, defaults={'socket': socket, 'benchmark_score': benchmark_score, 'price': price, 'name': name})
            PriceHistory.objects.create(component_id=cpu_obj.id, component_type='cpu', price=price)

    def parse_gpus(self):
        url = 'https://www.regard.ru/catalog/1013/videokarty'
        items = self.get_items(url)
        manufacturers = ["Acer", "AFOX", "ASRock", "ASUS", "Biostar", "CBR", "Gigabyte", "HP", "INNO3D", "Maxsun", "MSI", "Palit", "PNY", "Sapphire", "Zotac"]
        pcie_versions = ['5.0', '4.0']
        gpus_tbody = self.get_tbody('https://www.videocardbenchmark.net/gpu_list.php')

        for item in items:
            url_name = item.find('a', class_='CardText_link__C_fPZ')

            name = ''
            for manufacturer in manufacturers:
                name = url_name.text
                if manufacturer in name:
                    name = ' '.join(name.split(f" {manufacturer}")[0].split()[2:])
                    break

            url = self.base_url + url_name.attrs['href']
            description = item.find('p', class_='CardText_text__fZPl_').text

            pcie_version = 0.0
            for pcie in pcie_versions:
                if pcie in description:
                    pcie_version = float(pcie)

            price = item.find('span', class_='Price_price__m2aSe').text.split()[:-1]
            price = float(''.join(price))
            benchmark_score = self.get_benchmark_score(gpus_tbody, name)
            gpu_obj, created = GPU.objects.update_or_create(url=url, defaults={'pcie_version': pcie_version, 'benchmark_score': benchmark_score,'price':price ,'name': name})
            PriceHistory.objects.create(component_id=gpu_obj.id, component_type='gpu', price=price)

    def parse_ram(self):
        url = 'https://www.regard.ru/catalog/1010/operativnaya-pamyat'
        items = self.get_items(url)
        ram_types = ['DDR5', 'DDR4', 'DDR3', 'DDR2']
        ram_bar_counts = {'2 модуля': 2, '4 модуля': 4}

        for item in items:
            url_name = item.find('a', class_='CardText_link__C_fPZ')
            name = url_name.text.split(' (')[0].split('z ')[-1]
            url = self.base_url + url_name.attrs['href']
            description = item.find('p', class_='CardText_text__fZPl_').text
            ram_bar_count = ''

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

    def parse_motherboards(self):
        url = 'https://www.regard.ru/catalog/1000/materinskie-platy'
        items = self.get_items(url)
        sockets = ["AM4", "AM5", "LGA 1200", "LGA 1700", "LGA 1851", "LGA 775"]
        ram_types = ['DDR5', 'DDR4', 'DDR3', 'DDR2']
        pcie_versions = ['5.0', '4.0']
        ram_slots_versions = ['4xDDR', '2xDDR']

        for item in items:
            url_name = item.find('a', class_='CardText_link__C_fPZ')
            name = ' '.join(url_name.text.split()[2:-1])
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