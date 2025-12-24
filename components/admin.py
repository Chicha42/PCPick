from django.contrib import admin
from .models import CPU, GPU, RAM, Motherboard, PriceHistory

admin.site.register(CPU)
admin.site.register(GPU)
admin.site.register(RAM)
admin.site.register(Motherboard)
admin.site.register(PriceHistory)