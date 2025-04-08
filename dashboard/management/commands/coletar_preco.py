from django.core.management.base import BaseCommand
from dashboard.models import PrecoBoi
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from django.core.mail import send_mail
from django.conf import settings
import sqlite3

class Command(BaseCommand):
    help = 'Executa o scraper de preço do boi SP e envia um e-mail de confirmação'

    def handle(self, *args, **kwargs):
        preco = None
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get("https://portal.datagro.com/pt/livestock")

        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Indicador do Boi SP')]"))
            )

            elemento = driver.find_element(By.XPATH, "//*[contains(text(), 'Indicador do Boi SP')]")
            linha = elemento.find_element(By.XPATH, "./ancestor::tr")
            colunas = linha.find_elements(By.TAG_NAME, "td")
            preco = colunas[-1].text.strip()

        except Exception as e:
            driver.quit()
            self.stderr.write(self.style.ERROR(f"Erro ao capturar o preço: {e}"))
            send_mail(
                subject='❌ Erro no scraper do Preço do Boi',
                message=f"Ocorreu um erro ao capturar os dados do site:\n\n{str(e)}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['diretoria@confinamentomariopinto.com'],
                fail_silently=False,
            )
            return

        driver.quit()

        if preco:
            PrecoBoi.objects.create(data=datetime.now().date(), preco=preco)
            self.stdout.write(self.style.SUCCESS(f"Preço do boi SP salvo: R$ {preco}"))

            send_mail(
                subject='✅ Scraper executado com sucesso - Preço do Boi SP',
                message=f"O scraper foi executado e o preço de hoje ({datetime.now().date()}) foi salvo com sucesso: R$ {preco}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['diretoria@confinamentomariopinto.com'],
                fail_silently=False,
            )
        else:
            self.stderr.write(self.style.WARNING("Preço não encontrado."))
            send_mail(
                subject='⚠️ Scraper executado, mas sem preço encontrado',
                message='O scraper foi executado, mas não conseguiu localizar o preço do boi SP no site.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['diretoria@confinamentomariopinto.com'],
                fail_silently=False,
            )
