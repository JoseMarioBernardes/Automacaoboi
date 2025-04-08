from django.urls import path
from .views import lista_precos, exportar_excel, executar_migracoes, criar_admin

urlpatterns = [
    path('', lista_precos, name='lista_precos'),
    path('exportar-excel/', exportar_excel, name='exportar_excel'),
    path('migrar/', executar_migracoes),
    path('criar-admin/', criar_admin),
]
