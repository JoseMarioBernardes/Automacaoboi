from django.db import models

class PrecoBoi(models.Model):
    data = models.DateField()
    preco = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.data} - R$ {self.preco}"