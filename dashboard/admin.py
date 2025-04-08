from django.contrib import admin
from .models import PrecoBoi

@admin.register(PrecoBoi)
class PrecoBoiAdmin(admin.ModelAdmin):
    list_display = ("data", "preco")
    ordering = ("-data",)