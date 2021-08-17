# -*- coding: utf-8 -*-
# Importations
import os
os.chdir("//woody/asan/Servicios/EnfermeriaMedPreventiva/prev_dev/consulta_covid/path")
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import Select
import pandas as pd
from tkinter import simpledialog, messagebox
import tkinter as tk
from utils.constants import (REDMIVA_TESTS,REDMIVA_LAST_PAGE_MSG,AVE_PASS,
                             AVE_PASS,ELEMENT_FOUND_MSG,NO_DATA_MSG,
                             REDMIVA_USER,REDMIVA_PASS, 
                             REDMIVA_NO_RESULTS_MSG,RUTA_GECKODRIVER_LOG)
from selenium.common.exceptions import (
    NoSuchElementException
    )
from utils.win_fun import TaskKill
# Test SIP 

class REDMIVA():
    def __init__(self):
        self.options = Options()
        self.options.headless = True
        self.kill = TaskKill()
        self.pruebas = ""

    def consultar_redmiva(self,sip):
        try:
            if REDMIVA_USER is None or REDMIVA_PASS is None:
                return "Faltan credenciales."
            self.sip = sip
            if not self.sip: 
                return "No se ha ingresado ningún SIP."
            self.driver = webdriver.Firefox(options=self.options,service_log_path=RUTA_GECKODRIVER_LOG)
            self.wait= WebDriverWait(self.driver,30)
            self.driver.implicitly_wait(0)
            self.driver.get("https://redmiva.sp.san.gva.es/redmiva/inicio/menu.faces")
            self.wait.until(EC.visibility_of_element_located(
                (By.ID, "_idJsp2:datosUsuario:portal")
                 )).send_keys(REDMIVA_USER)
            self.wait.until(EC.visibility_of_element_located(
                (By.ID, "_idJsp2:datosUsuario:usuario")
                 )).send_keys(REDMIVA_PASS)
            self.wait.until(EC.visibility_of_element_located((
               By.XPATH, "//*[@value='Aceptar']"))).click()
            self.wait.until(EC.visibility_of_element_located((
               By.XPATH, "//*[@value='Búsqueda de pruebas por SIP']"))).click()
            fecha_desde = self.wait.until(EC.visibility_of_element_located(
                (By.ID, "myform:fechaDesde")))
            fecha_desde.clear()
            fecha_desde.send_keys("01/01/2020")
            self.driver.find_element_by_id("myform:sipPac").send_keys(sip)
            self.wait.until(EC.visibility_of_element_located((
               By.XPATH, "//*[@value='Buscar']"))).click()
            if REDMIVA_NO_RESULTS_MSG in self.driver.page_source:
                redmiva = pd.DataFrame()
            else:
                self.wait.until(EC.visibility_of_element_located(
                    (By.XPATH, "//*[contains(text(),'Ver')]"))).click()
                redmiva = pd.DataFrame()
                while True:
                    try:
                        tb = self.driver.find_element_by_id("_idJsp2:tablaPruebas").get_attribute("outerHTML")
                        tb=pd.read_html(tb,header=0)[0]
                        redmiva = redmiva.append(tb)
                    except NoSuchElementException:
                        self.wait.until(EC.visibility_of_element_located((
                            By.XPATH, "//*[@title='Ir a la solicitud siguiente']"))).click()
                    if REDMIVA_LAST_PAGE_MSG in self.driver.page_source:
                        break
                    else:
                        self.wait.until(EC.visibility_of_element_located((
                            By.XPATH, "//*[@title='Ir a la solicitud siguiente']"))).click()
                redmiva = redmiva[redmiva.columns.drop(redmiva.filter(regex="Técnica|Nº Resultados|Acción|Id.Pru."))]
            self.driver.quit()
            self.kill.geckodriver()
            return redmiva
        except Exception:
            return "Error de consulta en REDMIVA"
