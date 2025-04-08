from django.shortcuts import render
from .models import PrecoBoi
from datetime import datetime
from openpyxl import Workbook
from django.http import HttpResponse
import statistics
from django.core.management import call_command
from django.contrib.auth import get_user_model

def lista_precos(request):
    precos = PrecoBoi.objects.all()

    inicio = request.GET.get("inicio")
    fim = request.GET.get("fim")

    if inicio:
        precos = precos.filter(data__gte=inicio)
    if fim:
        precos = precos.filter(data__lte=fim)

    precos = precos.order_by("data")
    datas = [p.data.strftime("%Y-%m-%d") for p in precos]
    precos_valores = [float(p.preco.replace(",", ".")) for p in precos]

    media_movel = []
    media_datas = []
    media_valores = []

    if len(precos) >= 5:
        for i in range(4, len(precos)):
            ultimos_5 = precos[i-4:i+1]
            data_media = ultimos_5[-1].data.strftime("%Y-%m-%d")
            valores = [float(p.preco.replace(",", ".")) for p in ultimos_5]
            media = round(statistics.mean(valores), 2)

            media_movel.append({'data': data_media, 'media': media})
            media_datas.append(data_media)
            media_valores.append(media)

    context = {
        "precos": precos[::-1],
        "datas": datas,
        "precos_valores": precos_valores,
        'media_movel': media_movel,
        'media_datas': media_datas,
        'media_valores': media_valores,
    }
    return render(request, "dashboard/lista_precos.html", context)

def exportar_excel(request):
    precos = PrecoBoi.objects.all()

    inicio = request.GET.get("inicio")
    fim = request.GET.get("fim")

    if inicio:
        precos = precos.filter(data__gte=inicio)
    if fim:
        precos = precos.filter(data__lte=fim)

    precos = precos.order_by("data")

    # Criar workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Preços do Boi SP"

    # Cabeçalhos
    ws.append(['Data', 'Preço'])

    for p in precos:
        ws.append([p.data.strftime("%Y-%m-%d"), p.preco])

    # Resposta HTTP
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="precos_boi.xlsx"'

    wb.save(response)
    return response

def executar_migracoes(request):
    try:
        call_command("migrate")
        return HttpResponse("✅ Migrações aplicadas com sucesso.")
    except Exception as e:
        return HttpResponse(f"❌ Erro ao aplicar migrações: {e}")

def criar_admin(request):
    try:
        User = get_user_model()
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@email.com', 'admin123')
            return HttpResponse("✅ Superusuário criado com sucesso. Usuário: admin / Senha: admin123")
        else:
            return HttpResponse("ℹ️ Superusuário já existe.")
    except Exception as e:
        return HttpResponse(f"❌ Erro ao criar superusuário: {e}")
