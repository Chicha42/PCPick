from django.contrib import admin
from .models import CPU, GPU, RAM, Motherboard, PriceHistory

@admin.register(CPU)
class CPUAdmin(admin.ModelAdmin):
    list_display = ('name', 'socket', 'price', 'benchmark_score')
    search_fields = ('name', 'socket')

@admin.register(GPU)
class GPUAdmin(admin.ModelAdmin):
    list_display = ('name', 'pcie_version', 'price', 'benchmark_score')
    search_fields = ('name',)

@admin.register(RAM)
class RAMAdmin(admin.ModelAdmin):
    list_display = ('name', 'ram_type', 'ram_capacity', 'ram_bar_count', 'price')
    search_fields = ('name', 'ram_type')

@admin.register(Motherboard)
class MotherboardAdmin(admin.ModelAdmin):
    list_display = ('name', 'socket', 'ram_type', 'pcie_version', 'ram_slots', 'price')
    search_fields = ('name', 'socket')

@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
    list_display = ( 'component_id', 'component_type', 'price', 'date_checked')
    list_filter = ('component_type', 'date_checked')