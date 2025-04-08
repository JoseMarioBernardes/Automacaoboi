from django.core.management.base import BaseCommand
from dashboard.models import PrecoBoi
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime

class Command(BaseCommand):
    help = "Coleta o preço do boi SP no site da Datagro e salva no banco"

    def handle(self, *args, **kwargs):
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get("https://portal.datagro.com/pt/livestock")

        preco = None
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Indicador do Boi SP')]"))
            )
            elemento = driver.find_element(By.XPATH, "//*[contains(text(), 'Indicador do Boi SP')]")
            linha = elemento.find_element(By.XPATH, "./ancestor::tr")
            colunas = linha.find_elements(By.TAG_NAME, "td")
            preco = colunas[-1].text.strip()
            self.stdout.write(self.style.SUCCESS(f"✅ Preço encontrado: R$ {preco}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Erro ao coletar o preço: {e}"))
        finally:
            driver.quit()

        if preco:
            data_hoje = datetime.now().date()
            # Evita duplicatas (um por dia)
            if not PrecoBoi.objects.filter(data=data_hoje).exists():
                PrecoBoi.objects.create(data=data_hoje, preco=preco)
                self.stdout.write(self.style.SUCCESS("✅ Preço salvo no banco de dados."))
            else:
                self.stdout.write(self.style.WARNING("⚠️ Preço já registrado para hoje."))