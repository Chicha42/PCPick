from django.shortcuts import render
from components.models import CPU, GPU, RAM, Motherboard
from decimal import Decimal
from components.models import PriceHistory
from .utils import get_graph
from configurator.models import Build


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

        if gpu:
            cpu_candidates = CPU.objects.filter(price__lte=core_budget * Decimal('0.15')).order_by('-benchmark_score')[:10]
            for cpu in cpu_candidates:
                platform_budget = core_budget - (cpu.price + gpu.price)
                if platform_budget <= 0:
                    continue

                mb = Motherboard.objects.filter(
                    socket=cpu.socket,
                    pcie_version__gte=gpu.pcie_version,
                    price__lte=platform_budget * Decimal('0.35')
                ).first()

                if mb:
                    ram_budget = platform_budget - mb.price
                    ram = RAM.objects.filter(
                        ram_type=mb.ram_type,
                        ram_bar_count__lte=mb.ram_slots,
                        price__lte=ram_budget
                    ).order_by('-ram_capacity', '-price').first()

                    if ram:
                        total_price = cpu.price + gpu.price + mb.price + ram.price
                        build_user = request.user if request.user.is_authenticated else None
                        new_build = Build.objects.create(user=build_user, cpu=cpu, gpu=gpu, mb=mb, ram=ram, total_price=total_price)
                        context['build'] = new_build
                        context['total_budget'] = total_budget
                        context['remaining'] = total_budget - total_price

                        cpu_history = PriceHistory.objects.filter(component_id=cpu.id, component_type='cpu').order_by('date_checked')
                        dates = [h.date_checked.strftime("%d.%m") for h in cpu_history]
                        prices = [float(h.price) for h in cpu_history]
                        if len(prices) > 1:
                            context['cpu_chart'] = get_graph(dates, prices)
                        break
                else:
                    context['error'] = 'Не удалось подобрать подходящую оперативную память.'
            else:
                context['error'] = 'Не удалось подобрать подходящую материнскую плату.'
        else:
            context['error'] = 'Не удалось подобрать подходящий процессор или видеокарту.'

    return render(request, 'configurator/index.html', context)