from django.core.management.base import BaseCommand
from dashboard.models import PrecoBoi
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from django.core.mail import send_mail
from django.conf import settings

class Command(BaseCommand):
    help = 'Executa o scraper sem navegador para pegar o preço do boi SP e envia um e-mail de confirmação'

    def handle(self, *args, **kwargs):
        url = "https://portal.datagro.com/pt/livestock"
        headers = {"User-Agent": "Mozilla/5.0"}

        try:
            response = requests.get(url, headers=headers, timeout=20)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            linha = soup.find("td", string=lambda x: x and "Indicador do Boi SP" in x)
            if linha:
                preco_td = linha.find_parent("tr").find_all("td")[-1]
                preco = preco_td.text.strip()

                # Salvar no banco
                PrecoBoi.objects.create(data=datetime.now().date(), preco=preco)
                self.stdout.write(self.style.SUCCESS(f"Preço salvo: R$ {preco}"))

                send_mail(
                    subject='✅ Scraper executado com sucesso - Preço do Boi SP',
                    message=f"Preço salvo para o dia {datetime.now().date()}: R$ {preco}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=['diretoria@confinamentomariopinto.com'],
                    fail_silently=False,
                )
            else:
                raise Exception("Indicador do Boi SP não encontrado na página.")

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Erro: {e}"))
            send_mail(
                subject='❌ Erro no scraper do Preço do Boi',
                message=f"Ocorreu um erro ao executar o scraper:\n\n{str(e)}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['diretoria@confinamentomariopinto.com'],
                fail_silently=False,
            )
