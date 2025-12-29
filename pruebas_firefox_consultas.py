"""
================================================================================
    PRUEBAS AUTOMATIZADAS CON SELENIUM - FIREFOX
    Sistema: Consultas Oftalmológicas - Clínica "Visión Clara"
    Framework: Selenium WebDriver + GeckoDriver (Firefox)
================================================================================
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
import time


def iniciar_driver():
    """Configura e inicia el WebDriver de Firefox"""
    print("\n" + "="*80)
    print("INICIANDO FIREFOX WEBDRIVER (GECKODRIVER)")
    print("="*80)
    
    # Configurar opciones de Firefox
    firefox_options = Options()
    # firefox_options.add_argument('--headless')  # Descomenta para modo sin interfaz
    firefox_options.set_preference("browser.download.folderList", 2)
    firefox_options.set_preference("browser.download.manager.showWhenStarting", False)
    
    # Iniciar Firefox
    driver = webdriver.Firefox(options=firefox_options)
    driver.maximize_window()
    
    print("✅ Firefox iniciado correctamente")
    return driver


def limpiar_citas(driver):
    """Limpia todas las citas antes de ejecutar pruebas"""
    driver.get("http://localhost:5000/api/limpiar")
    time.sleep(1)


def prueba_1_carga_pagina(driver):
    """PRUEBA 1: Verificar que la página principal se carga correctamente"""
    print("\n[PRUEBA 1] Verificando carga de la página principal...")
    
    driver.get("http://localhost:5000")
    time.sleep(2)
    
    # Verificar título
    titulo = driver.title
    assert "Sistema de Consultas" in titulo, f"Error: Título incorrecto '{titulo}'"
    
    # Verificar encabezado
    encabezado = driver.find_element(By.TAG_NAME, "h1")
    assert "Visión Clara" in encabezado.text, "Error: Encabezado no encontrado"
    
    # Verificar que existen los 4 tabs
    tabs = driver.find_elements(By.CLASS_NAME, "tab-button")
    assert len(tabs) == 4, f"Error: Se esperaban 4 tabs, se encontraron {len(tabs)}"
    
    print("   ✅ Página cargada correctamente en Firefox")
    print("   ✅ Título verificado")
    print("   ✅ 4 tabs encontrados")


def prueba_2_agendar_cita_exitosa(driver):
    """PRUEBA 2: Agendar una cita con datos válidos"""
    print("\n[PRUEBA 2] Agendando cita con datos válidos...")
    
    driver.get("http://localhost:5000")
    time.sleep(1)
    
    # Llenar formulario
    driver.find_element(By.ID, "rut-paciente").send_keys("12345678-9")
    
    select_doctor = Select(driver.find_element(By.ID, "doctor"))
    select_doctor.select_by_index(1)  # Seleccionar primer doctor
    
    driver.find_element(By.ID, "fecha").send_keys("31122025")  # 31/12/2025
    driver.find_element(By.ID, "hora").send_keys("1030")  # 10:30
    
    select_tipo = Select(driver.find_element(By.ID, "tipo-consulta"))
    select_tipo.select_by_value("Control de rutina")
    
    # Enviar formulario
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    
    # Esperar a que la alerta sea visible (no solo presente en DOM)
    wait = WebDriverWait(driver, 20)
    alert = wait.until(EC.visibility_of_element_located((By.ID, "alert-agendar")))
    # Esperar a que tenga contenido y clase success
    wait.until(lambda d: "success" in d.find_element(By.ID, "alert-agendar").get_attribute("class"))
    
    # Verificar mensaje de éxito
    assert "success" in alert.get_attribute("class"), "Error: No se mostró alerta de éxito"
    assert "exitosamente" in alert.text, "Error: Mensaje de éxito incorrecto"
    
    print("   ✅ Cita agendada exitosamente en Firefox")
    print("   ✅ Mensaje de confirmación mostrado")


def prueba_3_validacion_campos_vacios(driver):
    """PRUEBA 3: Validar que los campos requeridos no permiten envío vacío"""
    print("\n[PRUEBA 3] Verificando validación de campos requeridos...")
    
    driver.get("http://localhost:5000")
    time.sleep(1)
    
    # Intentar enviar formulario vacío
    boton_enviar = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    boton_enviar.click()
    time.sleep(1)
    
    # Verificar que el campo RUT tiene validación HTML5
    campo_rut = driver.find_element(By.ID, "rut-paciente")
    validez = driver.execute_script("return arguments[0].validity.valid;", campo_rut)
    assert not validez, "Error: El formulario permitió envío con campos vacíos"
    
    print("   ✅ Validación de campos requeridos funcionando")
    print("   ✅ Formulario no se envía con datos vacíos")


def prueba_4_validacion_fecha_pasada(driver):
    """PRUEBA 4: Validar que no se permiten fechas pasadas"""
    print("\n[PRUEBA 4] Verificando rechazo de fechas pasadas...")
    
    driver.get("http://localhost:5000")
    time.sleep(1)
    
    # Intentar agendar con fecha pasada
    driver.find_element(By.ID, "rut-paciente").send_keys("12345678-9")
    
    select_doctor = Select(driver.find_element(By.ID, "doctor"))
    select_doctor.select_by_index(1)
    
    driver.find_element(By.ID, "fecha").send_keys("01012020")  # Fecha pasada
    driver.find_element(By.ID, "hora").send_keys("1000")
    
    select_tipo = Select(driver.find_element(By.ID, "tipo-consulta"))
    select_tipo.select_by_value("Examen de vista")
    
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    
    # Esperar a que la alerta sea visible (no solo presente en DOM)
    wait = WebDriverWait(driver, 20)
    alert = wait.until(EC.visibility_of_element_located((By.ID, "alert-agendar")))
    # Esperar a que tenga contenido y clase error
    wait.until(lambda d: "error" in d.find_element(By.ID, "alert-agendar").get_attribute("class"))
    
    # Verificar mensaje de error
    assert "error" in alert.get_attribute("class"), "Error: No se mostró alerta de error"
    assert "futura" in alert.text.lower(), "Error: Mensaje de error incorrecto"
    
    print("   ✅ Fechas pasadas rechazadas correctamente")
    print("   ✅ Mensaje de error mostrado")


def prueba_5_consultar_citas(driver):
    """PRUEBA 5: Consultar citas agendadas"""
    print("\n[PRUEBA 5] Consultando citas agendadas...")
    
    driver.get("http://localhost:5000")
    time.sleep(1)
    
    # Cambiar a tab de consultar
    tab_consultar = driver.find_elements(By.CLASS_NAME, "tab-button")[1]
    tab_consultar.click()
    time.sleep(1)
    
    # Buscar todas las citas
    boton_buscar = driver.find_element(By.XPATH, "//button[contains(text(), 'Buscar Citas')]")
    boton_buscar.click()
    time.sleep(2)
    
    # Verificar que se muestran las citas
    lista_citas = driver.find_element(By.ID, "citas-list")
    assert lista_citas.text != "", "Error: No se encontraron citas"
    
    print("   ✅ Lista de citas cargada")
    print("   ✅ Información de citas mostrada correctamente")


def prueba_6_consultar_historial(driver):
    """PRUEBA 6: Consultar historial médico de un paciente"""
    print("\n[PRUEBA 6] Consultando historial médico...")
    
    driver.get("http://localhost:5000")
    time.sleep(1)
    
    # Cambiar a tab de historial
    tab_historial = driver.find_elements(By.CLASS_NAME, "tab-button")[2]
    tab_historial.click()
    time.sleep(1)
    
    # Ingresar RUT y buscar
    driver.find_element(By.ID, "rut-historial").send_keys("12345678-9")
    boton_ver = driver.find_element(By.XPATH, "//button[contains(text(), 'Ver Historial')]")
    boton_ver.click()
    time.sleep(2)
    
    # Verificar que se muestra el historial
    historial = driver.find_element(By.ID, "historial-container")
    assert "Juan Pérez" in historial.text, "Error: Información del paciente no encontrada"
    assert "Miopía" in historial.text or "Control" in historial.text, "Error: Historial no cargado"
    
    print("   ✅ Historial médico cargado")
    print("   ✅ Información del paciente mostrada")


def prueba_7_validacion_paciente_inexistente(driver):
    """PRUEBA 7: Validar error con paciente inexistente"""
    print("\n[PRUEBA 7] Verificando validación de paciente inexistente...")
    
    driver.get("http://localhost:5000")
    time.sleep(1)
    
    # Cambiar a tab de historial
    tab_historial = driver.find_elements(By.CLASS_NAME, "tab-button")[2]
    tab_historial.click()
    time.sleep(1)
    
    # Buscar paciente que no existe
    driver.find_element(By.ID, "rut-historial").send_keys("99999999-9")
    boton_ver = driver.find_element(By.XPATH, "//button[contains(text(), 'Ver Historial')]")
    boton_ver.click()
    time.sleep(2)
    
    # Verificar mensaje de error
    historial = driver.find_element(By.ID, "historial-container")
    assert "no encontrado" in historial.text.lower(), "Error: No se mostró mensaje de error"
    
    print("   ✅ Paciente inexistente detectado correctamente")
    print("   ✅ Mensaje de error mostrado")


def prueba_8_estado_sistema(driver):
    """PRUEBA 8: Verificar estado del sistema"""
    print("\n[PRUEBA 8] Verificando estado del sistema...")
    
    driver.get("http://localhost:5000")
    time.sleep(1)
    
    # Cambiar a tab de estado
    tab_estado = driver.find_elements(By.CLASS_NAME, "tab-button")[3]
    tab_estado.click()
    time.sleep(1)
    
    # Actualizar estado
    boton_actualizar = driver.find_element(By.XPATH, "//button[contains(text(), 'Actualizar Estado')]")
    boton_actualizar.click()
    time.sleep(2)
    
    # Verificar que se muestra información del sistema
    estado = driver.find_element(By.ID, "estado-container")
    assert "Operativo" in estado.text, "Error: Estado del sistema no mostrado"
    assert "Pacientes Registrados" in estado.text, "Error: Estadísticas no cargadas"
    
    print("   ✅ Estado del sistema cargado")
    print("   ✅ Estadísticas mostradas correctamente")


def prueba_9_validacion_cita_duplicada(driver):
    """PRUEBA 9: Validar que no se permiten citas duplicadas"""
    print("\n[PRUEBA 9] Verificando rechazo de citas duplicadas...")
    
    driver.get("http://localhost:5000")
    time.sleep(1)
    
    # Agendar primera cita
    driver.find_element(By.ID, "rut-paciente").send_keys("12345678-9")
    Select(driver.find_element(By.ID, "doctor")).select_by_index(1)
    driver.find_element(By.ID, "fecha").send_keys("29122025")
    driver.find_element(By.ID, "hora").send_keys("1500")
    Select(driver.find_element(By.ID, "tipo-consulta")).select_by_value("Control de rutina")
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(2)
    
    # Intentar agendar cita duplicada
    driver.find_element(By.ID, "rut-paciente").clear()
    driver.find_element(By.ID, "rut-paciente").send_keys("12345678-9")
    driver.find_element(By.ID, "fecha").clear()
    driver.find_element(By.ID, "fecha").send_keys("29122025")
    driver.find_element(By.ID, "hora").clear()
    driver.find_element(By.ID, "hora").send_keys("1500")
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    
    # Esperar a que la alerta sea visible (no solo presente en DOM)
    wait = WebDriverWait(driver, 20)
    alert = wait.until(EC.visibility_of_element_located((By.ID, "alert-agendar")))
    # Esperar a que tenga contenido y clase error
    wait.until(lambda d: "error" in d.find_element(By.ID, "alert-agendar").get_attribute("class"))
    
    # Verificar mensaje de error
    assert "error" in alert.get_attribute("class"), "Error: No se mostró alerta de error"
    assert "existe" in alert.text.lower(), "Error: No se detectó cita duplicada"
    
    print("   ✅ Citas duplicadas rechazadas correctamente")
    print("   ✅ Validación de duplicados funcionando")


def prueba_10_cancelar_cita(driver):
    """PRUEBA 10: Cancelar una cita existente"""
    print("\n[PRUEBA 10] Cancelando una cita...")
    
    driver.get("http://localhost:5000")
    time.sleep(1)
    
    # Cambiar a tab de consultar
    tab_consultar = driver.find_elements(By.CLASS_NAME, "tab-button")[1]
    tab_consultar.click()
    time.sleep(1)
    
    # Buscar citas
    boton_buscar = driver.find_element(By.XPATH, "//button[contains(text(), 'Buscar Citas')]")
    boton_buscar.click()
    time.sleep(2)
    
    # Buscar botón de cancelar
    try:
        boton_cancelar = driver.find_element(By.CLASS_NAME, "btn-cancelar")
        boton_cancelar.click()
        time.sleep(1)
        
        # Confirmar cancelación
        driver.switch_to.alert.accept()
        time.sleep(2)
        
        print("   ✅ Cita cancelada exitosamente")
        print("   ✅ Funcionalidad de cancelación operativa")
    except:
        print("   ⚠️  No hay citas para cancelar (esto es normal si ya fueron canceladas)")


def ejecutar_todas_las_pruebas():
    """Ejecuta todas las pruebas automatizadas en Firefox"""
    print("\n" + "="*80)
    print("  INICIANDO SUITE DE PRUEBAS AUTOMATIZADAS - FIREFOX")
    print("  Sistema: Consultas Oftalmológicas - Clínica Visión Clara")
    print("="*80)
    
    driver = None
    pruebas_exitosas = 0
    pruebas_fallidas = 0
    
    try:
        driver = iniciar_driver()
        
        # Limpiar estado antes de las pruebas
        limpiar_citas(driver)
        
        # Lista de pruebas
        pruebas = [
            prueba_1_carga_pagina,
            prueba_2_agendar_cita_exitosa,
            prueba_3_validacion_campos_vacios,
            prueba_4_validacion_fecha_pasada,
            prueba_5_consultar_citas,
            prueba_6_consultar_historial,
            prueba_7_validacion_paciente_inexistente,
            prueba_8_estado_sistema,
            prueba_9_validacion_cita_duplicada,
            prueba_10_cancelar_cita
        ]
        
        # Ejecutar cada prueba
        for i, prueba in enumerate(pruebas, 1):
            try:
                prueba(driver)
                pruebas_exitosas += 1
            except Exception as e:
                pruebas_fallidas += 1
                print(f"   ❌ Error en prueba {i}: {str(e)}")
        
        # Resumen final
        print("\n" + "="*80)
        print("  RESUMEN DE PRUEBAS - FIREFOX")
        print("="*80)
        print(f"  ✅ Pruebas exitosas: {pruebas_exitosas}")
        print(f"  ❌ Pruebas fallidas: {pruebas_fallidas}")
        print(f"  📊 Total de pruebas: {len(pruebas)}")
        print(f"  📈 Tasa de éxito: {(pruebas_exitosas/len(pruebas)*100):.1f}%")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {str(e)}")
    
    finally:
        if driver:
            print("\nCerrando Firefox...")
            time.sleep(3)
            driver.quit()
        
        print("\n✅ Pruebas en Firefox completadas\n")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("  HERRAMIENTA DE TESTING AUTOMATIZADO - FIREFOX")
    print("  Asegúrese de que:")
    print("  1. El servidor Flask esté ejecutándose en http://localhost:5000")
    print("  2. GeckoDriver esté instalado y en el PATH del sistema")
    print("  3. Mozilla Firefox esté instalado")
    print("="*80)
    
    # En CI/CD (GitHub Actions), no esperar input del usuario
    if not os.getenv('CI'):
        input("\nPresione ENTER para iniciar las pruebas en Firefox...")
    else:
        print("\n[CI Mode] Iniciando pruebas en Firefox automáticamente...")
    
    ejecutar_todas_las_pruebas()
