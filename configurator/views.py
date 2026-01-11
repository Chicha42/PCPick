from decimal import Decimal

from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from components.models import CPU, GPU, RAM, Motherboard
from configurator.models import Build
from .forms import SignUpForm
from .utils import get_component_graph


def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = SignUpForm()
    return render(request, 'configurator/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'configurator/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('index')

@login_required
def my_builds(request):
    builds = Build.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'configurator/my_builds.html', {'builds': builds})
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
                        context['build'] = {'cpu': cpu, 'gpu': gpu, 'mb': mb, 'ram': ram, 'total_price': total_price}
                        context['cpu_graph'] = get_component_graph(cpu.id, 'cpu')
                        context['gpu_graph'] = get_component_graph(gpu.id, 'gpu')
                        context['ram_graph'] = get_component_graph(ram.id, 'ram')
                        context['mb_graph'] = get_component_graph(mb.id, 'mb')
                        context['total_budget'] = total_budget
                        context['remaining'] = total_budget - total_price
                        break
                else:
                    context['error'] = 'Не удалось подобрать подходящую оперативную память.'
            else:
                context['error'] = 'Не удалось подобрать подходящую материнскую плату.'
        else:
            context['error'] = 'Не удалось подобрать подходящий процессор или видеокарту.'

    return render(request, 'configurator/index.html', context)

@login_required
def save_build(request):
    if request.method == 'POST':
        Build.objects.create(
            user=request.user,
            cpu_id=request.POST.get('cpu_id'),
            gpu_id=request.POST.get('gpu_id'),
            ram_id=request.POST.get('ram_id'),
            mb_id=request.POST.get('mb_id'),
            total_price=Decimal(request.POST.get('total_price'))
        )
        return redirect('profile')
    return redirect('index')

@login_required
def profile_info(request):
    return render(request, 'configurator/profile_info.html', {'user': request.user})

def build_detail(request, pk):
    build = get_object_or_404(Build, pk=pk)
    user_build_number = Build.objects.filter(user=build.user, created_at__lte=build.created_at).count()

    context = {
        'build': build,
        'build_number': user_build_number,
        'cpu_graph': get_component_graph(build.cpu.id, 'cpu'),
        'gpu_graph': get_component_graph(build.gpu.id, 'gpu'),
        'ram_graph': get_component_graph(build.ram.id, 'ram'),
        'mb_graph': get_component_graph(build.mb.id, 'mb'),
    }
    return render(request, 'configurator/build_detail.html', context)

@login_required
def delete_build(request, pk):
    build = get_object_or_404(Build, pk=pk, user=request.user)
    if request.method == 'POST':
        build.delete()
    return redirect('profile')

@login_required
def edit_profile(request):
    if request.method == 'POST':
        user = request.user
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.save()
        messages.success(request, 'Данные успешно обновлены!')
        return redirect('profile_info')
    return render(request, 'configurator/edit_profile.html')

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Пароль успешно изменен!')
            return redirect('profile_info')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'configurator/change_password.html', {'form': form})