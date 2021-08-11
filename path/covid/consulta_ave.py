# -*- coding: utf-8 -*-
# Importations
import os
os.chdir("//woody/asan/Servicios/EnfermeriaMedPreventiva/prev_dev/path")
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import Select
import pandas as pd
from utils.constants import ELEMENT_FOUND_MSG,NO_DATA_MSG,AVE_USER,AVE_PASS,RUTA_GECKODRIVER_LOG
from utils.win_fun import TaskKill

class AVE():
    def __init__(self):
        self.options = Options()
        self.options.headless = True
        self.kill = TaskKill()
        self.infeccion = ""

    def consultar_ave(self,sip):
        """Consulta declaración en AVE según número de SIP
        Devuelve una tupla con las variables (infeccion, tabla)"""
        try:
            if AVE_USER is None or AVE_PASS is None:
                return "Faltan credenciales."
            self.sip = sip
            if not self.sip: 
                return "No se ha ingresado ningún SIP."
            self.kill.firefox()
            self.driver = webdriver.Firefox(options=self.options,log_path=RUTA_GECKODRIVER_LOG)
            self.wait= WebDriverWait(self.driver,30)
            self.driver.implicitly_wait(0)
            self.driver.delete_all_cookies()
            self.driver.get("https://ave.sp.san.gva.es/ave/")
            self.driver.find_element_by_name("usuario").send_keys(AVE_USER)
            self.driver.find_element_by_name("password").send_keys(AVE_PASS)
            self.driver.execute_script("validar();")
            self.driver.get("https://ave.sp.san.gva.es/ave/gestion_datos/busca_encuestas.jsp")
            self.wait.until(EC.visibility_of_element_located((
                By.ID,"enfermedad")))
            select = Select(self.driver.find_element_by_id("enfermedad"))
            select.select_by_visible_text("CORONAVIRUS")
            self.driver.find_element_by_id("num_social2").send_keys(self.sip)
            self.driver.execute_script("validar();")
            self.wait.until(EC.visibility_of_element_located((
                By.XPATH,"//*[@name='bimprimir']")))
            self.wait.until(EC.visibility_of_element_located(
                (
                 By.CSS_SELECTOR,
                 """
                 #tablas,
                 td.TexNoEfa
                 """)
                ))
            if ELEMENT_FOUND_MSG in self.driver.page_source:
                self.infeccion = "SI"
                tb=self.driver.find_element_by_id("tablas").get_attribute("outerHTML")
                tb=pd.read_html(tb,header=0)[0]
                tb = tb.filter(regex="SIP|NOMBRE|APELLIDO|FECHA INSERCIÓN")
                tb = tb[tb.columns.drop(tb.filter(regex="COMPLETA"))]
                tb["NOMBRE"] = tb[tb.columns[1:4]].apply(
                    lambda x: " ".join(x.dropna().astype(str)),
                    axis=1)
                tb = tb[tb.columns.drop(tb.filter(regex="APELLIDO"))]  
            elif NO_DATA_MSG in self.driver.page_source:
                self.infeccion = "NO"
                tb=pd.DataFrame()
            self.driver.quit()
            self.kill.geckodriver()
            return self.infeccion, tb
        except Exception:
            return "Error de consulta de AVE"