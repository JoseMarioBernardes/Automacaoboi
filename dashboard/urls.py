from django.urls import path
from .views import lista_precos, exportar_excel

urlpatterns = [
    path('', lista_precos, name='lista_precos'),
    path('exportar-excel/', exportar_excel, name='exportar_excel'),
]
