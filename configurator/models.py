from django.contrib.auth.models import User
from django.db import models
from components.models import CPU, GPU, Motherboard, RAM


class Build(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    cpu = models.ForeignKey(CPU, on_delete=models.PROTECT)
    gpu = models.ForeignKey(GPU, on_delete=models.PROTECT)
    mb = models.ForeignKey(Motherboard, on_delete=models.PROTECT)
    ram = models.ForeignKey(RAM, on_delete=models.PROTECT)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        username = self.user.username if self.user else "Guest"
        return f"Build {self.id} by {username}. Total price: {self.total_price} руб."

    class Meta:
        verbose_name = "PC Build"
        verbose_name_plural = "PC Builds"