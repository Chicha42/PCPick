from django.db import models


class CPU(models.Model):
    name = models.CharField(max_length=128)
    socket = models.CharField(max_length=128)
    benchmark_score = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    url = models.URLField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "CPU"
        verbose_name_plural = "CPUs"

class GPU(models.Model):
    name = models.CharField(max_length=128)
    pcie_version = models.FloatField()
    benchmark_score = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    url = models.URLField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "GPU"
        verbose_name_plural = "GPUs"

class RAM(models.Model):
    name = models.CharField(max_length=128)
    ram_type = models.CharField(max_length=128)
    ram_capacity = models.PositiveIntegerField()
    ram_bar_count = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    url = models.URLField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "RAM"
        verbose_name_plural = "RAM"

class Motherboard(models.Model):
    name = models.CharField(max_length=128)
    socket = models.CharField(max_length=128)
    ram_type = models.CharField(max_length=128)
    pcie_version = models.FloatField()
    ram_slots = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    url = models.URLField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Motherboard"
        verbose_name_plural = "Motherboards"

class PriceHistory(models.Model):
    component_id = models.PositiveIntegerField()
    component_type = models.CharField(max_length=128)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    date_checked = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.component_type} ({self.component_id}) - {self.price}"

    class Meta:
        verbose_name = "Price History"
        verbose_name_plural = "Price History"