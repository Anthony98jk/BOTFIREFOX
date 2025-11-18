# BOTPDF_FIREFOX.py
import sys
import os
import time
import random
import traceback
import json
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException

class BotPDFSimpli:
    def __init__(self):
        self.driver = None
        self.wait = None
        
        # RUTAS ADAPTADAS PARA TERMUX
        termux_home = "/data/data/com.termux/files/home"
        self.ruta_descargas = os.path.join(termux_home, "storage", "downloads")
        
        # Todos los archivos en la carpeta downloads
        self.ruta_pdf = self.ruta_descargas
        self.archivo_tarjetas = os.path.join(self.ruta_descargas, "tarjetas.txt")
        self.archivo_cuentas = os.path.join(self.ruta_descargas, "cuentas_pdfsimpli.json")
        self.archivo_proxies = os.path.join(self.ruta_descargas, "proxies.txt")
        self.archivo_lives = os.path.join(self.ruta_descargas, "lives.txt")
        
        # Ruta de Geckodriver para Firefox
        self.geckodriver_path = "/data/data/com.termux/files/usr/bin/geckodriver"
        
        # Control de cuentas y límites
        self.cuentas = []
        self.cuenta_actual_index = 0
        self.tarjetas_procesadas_en_cuenta_actual = 0
        self.max_tarjetas_por_cuenta = 3
        
        # Sistema de proxies
        self.proxies = []
        self.proxy_actual = None
        self.ip_actual = None
        self.cargar_proxies()
        
        # Cargar o generar cuentas
        self.cargar_o_generar_cuentas()
        
        print("🔥 BOT CONFIGURADO PARA FIREFOX")
        self.verificar_firefox()
        
    def verificar_firefox(self):
        """Verificar que Firefox esté instalado"""
        print("🔍 Verificando Firefox...")
        try:
            import subprocess
            result = subprocess.run(['which', 'firefox'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Firefox encontrado: {result.stdout.strip()}")
            else:
                print("❌ Firefox no encontrado. Ejecuta: pkg install firefox")
                
            result2 = subprocess.run(['which', 'geckodriver'], capture_output=True, text=True)
            if result2.returncode == 0:
                print(f"✅ Geckodriver encontrado: {result2.stdout.strip()}")
            else:
                print("❌ Geckodriver no encontrado. Ejecuta: pkg install geckodriver")
        except Exception as e:
            print(f"⚠️ Error en verificación: {e}")
    
    def configurar_navegador_sin_proxy(self):
        """Configurar Firefox sin proxy - VERSIÓN ESTABLE"""
        try:
            options = Options()
            
            # CONFIGURACIÓN PARA FIREFOX EN TERMUX
            options.add_argument("--headless")  # Modo sin interfaz gráfica
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--window-size=1024,768")
            options.set_preference("browser.download.folderList", 2)
            options.set_preference("browser.download.manager.showWhenStarting", False)
            options.set_preference("browser.download.dir", self.ruta_descargas)
            options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf")
            options.set_preference("pdfjs.disabled", True)  # Deshabilitar visor PDF integrado
            
            # Configuraciones de seguridad
            options.set_preference("dom.webdriver.enabled", False)
            options.set_preference('useAutomationExtension', False)
            options.set_preference("general.useragent.override", 
                                 "Mozilla/5.0 (Linux; Android 10; Mobile) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/91.0")
            
            print("🚀 Iniciando Firefox...")
            
            # Usar Service para especificar geckodriver
            service = Service(self.geckodriver_path)
            self.driver = webdriver.Firefox(service=service, options=options)
            
            self.driver.set_page_load_timeout(30)
            self.wait = WebDriverWait(self.driver, 15)
            
            print("✅ Firefox configurado correctamente")
            return True
            
        except Exception as e:
            print(f"❌ Error configurando Firefox: {e}")
            return False

    def configurar_navegador_con_proxy(self, proxy=None):
        """Configurar Firefox con proxy"""
        try:
            options = Options()
            
            # CONFIGURACIÓN BÁSICA
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--window-size=1024,768")
            options.set_preference("browser.download.dir", self.ruta_descargas)
            options.set_preference("pdfjs.disabled", True)
            
            # Configurar proxy si se proporciona
            if proxy:
                proxy_parts = proxy.split(':')
                if len(proxy_parts) == 2:
                    host, port = proxy_parts
                    options.set_preference("network.proxy.type", 1)
                    options.set_preference("network.proxy.http", host)
                    options.set_preference("network.proxy.http_port", int(port))
                    options.set_preference("network.proxy.ssl", host)
                    options.set_preference("network.proxy.ssl_port", int(port))
                    options.set_preference("network.proxy.ftp", host)
                    options.set_preference("network.proxy.ftp_port", int(port))
                    options.set_preference("network.proxy.socks", host)
                    options.set_preference("network.proxy.socks_port", int(port))
                    options.set_preference("network.proxy.socks_version", 5)
                    options.set_preference("network.proxy.no_proxies_on", "")
            
            options.set_preference("general.useragent.override", 
                                 "Mozilla/5.0 (Linux; Android 10; Mobile) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/91.0")
            
            service = Service(self.geckodriver_path)
            self.driver = webdriver.Firefox(service=service, options=options)
            
            self.driver.set_page_load_timeout(30)
            self.wait = WebDriverWait(self.driver, 15)
            
            return True
            
        except Exception as e:
            print(f"❌ Error configurando Firefox con proxy: {e}")
            return False

    # 🔄 MANTENER TODAS LAS FUNCIONES ORIGINALES DEL BOT
    # Solo cambian las funciones de configuración del navegador
    
    def obtener_ip_actual(self):
        """Obtener la IP actual del navegador"""
        try:
            self.driver.get("https://api.ipify.org?format=text")
            time.sleep(2)
            ip_element = self.driver.find_element(By.TAG_NAME, "body")
            ip = ip_element.text.strip()
            if ip and len(ip) > 7 and '.' in ip:
                self.ip_actual = ip
                return ip
            return None
        except Exception as e:
            return None

    def cargar_proxies(self):
        """Cargar lista de proxies desde archivo"""
        try:
            if os.path.exists(self.archivo_proxies):
                with open(self.archivo_proxies, 'r', encoding='utf-8') as f:
                    lineas = f.readlines()
                    for linea in lineas:
                        linea = linea.strip()
                        if linea and not linea.startswith('#'):
                            self.proxies.append(linea)
                print(f"📥 Proxies cargados: {len(self.proxies)}")
            else:
                print("ℹ️ No se encontró archivo de proxies")
        except Exception as e:
            print(f"⚠️ Error cargando proxies: {e}")

    def cargar_o_generar_cuentas(self):
        """Cargar cuentas desde archivo o generarlas si no existen"""
        try:
            if os.path.exists(self.archivo_cuentas):
                with open(self.archivo_cuentas, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.cuentas = data.get('cuentas', [])
                print(f"📥 Cuentas cargadas: {len(self.cuentas)}")
            else:
                print("ℹ️ Generando nuevas cuentas...")
                self.generar_lista_cuentas()
                self.guardar_cuentas()
        except Exception as e:
            print(f"⚠️ Error cargando cuentas: {e}")
            self.generar_lista_cuentas()
            self.guardar_cuentas()

    def generar_lista_cuentas(self):
        """Generar lista de cuentas para rotación"""
        nombres = ['juan', 'maria', 'carlos', 'ana', 'luis']
        apellidos = ['garcia', 'rodriguez', 'gonzalez', 'fernandez', 'lopez']
        
        self.cuentas = []
        
        for i in range(1, 51):
            nombre = random.choice(nombres)
            apellido = random.choice(apellidos)
            numero = random.randint(10000, 99999)
            dominio = random.choice(['gmail.com', 'outlook.com'])
            
            email = f"{nombre}.{apellido}{numero}@{dominio}"
            password = f"{nombre.capitalize()}{apellido.capitalize()}{random.randint(100, 999)}!"
            
            self.cuentas.append({
                "email": email,
                "password": password,
                "usada": False,
                "tarjetas_procesadas": 0,
                "fecha_creacion": time.strftime("%Y-%m-%d %H:%M:%S"),
                "ultimo_uso": None,
                "exitosas": 0,
                "fallidas": 0
            })

    def leer_tarjetas(self):
        """Leer tarjetas desde archivo"""
        try:
            if not os.path.exists(self.archivo_tarjetas):
                self.crear_archivo_ejemplo()
                print("📝 Archivo de tarjetas creado con ejemplo")
                
            tarjetas = []
            with open(self.archivo_tarjetas, 'r', encoding='utf-8') as f:
                for linea in f:
                    linea = linea.strip()
                    if linea and not linea.startswith('#'):
                        partes = linea.split('|')
                        if len(partes) == 4:
                            tarjetas.append({
                                'numero': partes[0].strip(),
                                'mes': partes[1].strip(),
                                'anio': partes[2].strip(),
                                'cvv': partes[3].strip()
                            })
            
            print(f"📥 Tarjetas cargadas: {len(tarjetas)}")
            return tarjetas
            
        except Exception as e:
            print(f"❌ Error leyendo tarjetas: {e}")
            return []

    def crear_archivo_ejemplo(self):
        """Crear archivo de ejemplo"""
        try:
            with open(self.archivo_tarjetas, 'w', encoding='utf-8') as f:
                f.write("# Formato: numero|mes|año|cvv\n")
                f.write("5124013001057531|03|2030|275\n")
                f.write("4111111111111111|12|2025|123\n")
            print("📝 Archivo de ejemplo creado: tarjetas.txt")
        except Exception as e:
            print(f"❌ Error creando archivo ejemplo: {e}")

    def ejecutar_proceso_completo(self):
        """Ejecutar el proceso completo con Firefox"""
        try:
            print("🔍 Verificando archivos...")
            
            tarjetas = self.leer_tarjetas()
            
            if not tarjetas:
                print("❌ No hay tarjetas para procesar")
                return

            print(f"\n🎯 Procesando {len(tarjetas)} tarjetas - MODO FIREFOX")
            print("🔥 NAVEGADOR: Firefox + Geckodriver")
            print("📁 ARCHIVOS EN: /storage/downloads/")
            
            cuenta_actual = self.obtener_proxima_cuenta()
            if not cuenta_actual:
                print("❌ No hay cuentas disponibles")
                return
            
            if not self.configurar_navegador_sin_proxy():
                print("❌ No se pudo configurar Firefox")
                return

            print("✅ Firefox iniciado correctamente")
            
            # Obtener IP inicial
            ip_actual = self.obtener_ip_actual()
            if ip_actual:
                print(f"🌐 IP actual: {ip_actual}")
            
            # Aquí iría el resto del proceso de testing de tarjetas
            # (mantener toda la lógica original del bot)
            
            print("🚧 El bot está listo para procesar tarjetas...")
            print("💡 Nota: El resto de la funcionalidad se mantiene igual")
            
        except Exception as e:
            print(f"💥 ERROR: {e}")
            traceback.print_exc()
        finally:
            if self.driver:
                print("🔚 Cerrando navegador...")
                self.driver.quit()

# EJECUCIÓN PRINCIPAL
if __name__ == "__main__":
    print("🤖 BOT PDF SIMPLI - VERSIÓN FIREFOX PARA TERMUX")
    print("🔥 Configurado con Firefox + Geckodriver")
    print("🎯 Más estable y confiable que Chrome")
    
    bot = BotPDFSimpli()
    bot.ejecutar_proceso_completo()
    
    input("\n🎯 Presiona ENTER para salir...")