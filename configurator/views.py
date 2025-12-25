from django.shortcuts import render
from components.models import CPU, GPU, RAM, Motherboard
from decimal import Decimal

def index(request):
    context = {}
    if request.method == "POST":
        budget_str = request.POST.get('budget', 0)
        try:
            total_budget = Decimal(budget_str)
        except ValueError:
            return render(request, 'configurator/index.html', {'error': 'Введите число'})

        core_budget = total_budget * Decimal('0.80')
        gpu = GPU.objects.filter(price__lte=core_budget * Decimal('0.35')).order_by('-benchmark_score').first()
        cpu = CPU.objects.filter(price__lte=core_budget * Decimal('0.15')).order_by('-benchmark_score').first()

        if gpu and cpu:
            remaining_for_platform = core_budget - (gpu.price + cpu.price)

            mb = Motherboard.objects.filter(
                socket=cpu.socket,
                pcie_version__gte=gpu.pcie_version,
                price__lte=remaining_for_platform * Decimal('0.25')
            ).first()

            if mb:
                ram_budget = remaining_for_platform - mb.price
                ram = RAM.objects.filter(
                    ram_type=mb.ram_type,
                    ram_bar_count__lte=mb.ram_slots,
                    price__lte=ram_budget
                ).order_by('-price').first()

                if ram:
                    context['build'] = {
                        'cpu': cpu,
                        'gpu': gpu,
                        'motherboard': mb,
                        'ram': ram,
                        'total_price': cpu.price + gpu.price + mb.price + ram.price
                    }
                else:
                    context['error'] = 'Не удалось подобрать подходящую оперативную память.'
            else:
                context['error'] = 'Не удалось подобрать подходящую материнскую плату.'
        else:
            context['error'] = 'Не удалось подобрать подходящий процессор или видеокарту.'

    return render(request, 'configurator/index.html', context)