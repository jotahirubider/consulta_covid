# -*- coding: utf-8 -*-
import time, re, os
os.chdir("//woody/asan/Servicios/EnfermeriaMedPreventiva/prev_dev/consulta_covid/path")
import numpy as np
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.constants import RVN_USER, RVN_PASS, NO_PAGE_MSG, SIP_ERROR_MSG, INFO_GRIPE
from utils.win_fun import TaskKill
from selenium.common.exceptions import (
    JavascriptException,
    NoSuchElementException,
    TimeoutException,
    UnexpectedAlertPresentException,
    ElementNotInteractableException,
    InvalidElementStateException,
    NoSuchWindowException,
    NoAlertPresentException)

class RVN():
    def __init__(self):
        self.sip = int()
        self.nombre = ""
        self.edad = ""
        self.fecha_nac = ""
        self.telefono = ""
        self.pobl = ""
        self.prov = ""
        self.n_dosis = 0
        self.marca = ""
        self.fecha = ""
        self.grupo_riesgo = ""
        self.df = pd.DataFrame()
        self.df[["SIP","NOMBRE","Nº Dosis","MARCA","FECHA DOSIS",
            "TELEFONO","GRUPO_RIESGO","FECHA_NAC","POBLACION"
            ,"PROVINCIA"]] = np.nan
        self.kill = TaskKill()
    def change_to_window(self, identificador):
        
        """Cambiar a la ventana deseada. Identificador es una cadena de texto
        única en la página deseada"""
        for i in range(len(self.driver.window_handles)):
            self.driver.switch_to.window(self.driver.window_handles[i])
            if identificador in self.driver.page_source:
                self.driver.minimize_window()
                break
    
    def check_no_page_error(self):
        self.driver.switch_to.window(self.driver.window_handles[-1])
        if NO_PAGE_MSG in self.driver.page_source:
            self.driver.close()
            raise PageNotAvailable

    def get_main_page(self):
        """Ir a página principal"""
        time.sleep(1)
        self.driver.execute_script("arguments[0].click();",
          self.driver.find_element_by_id("fila0_sel"))
        self.change_to_window("busccent")
        time.sleep(0.5)
        # CUIDADO SI CAMBIA EL HOSPITAL DE CAMPAÑA
        self.driver.execute_script("cambiaCentro(4829,'HOSPITAL DE CAMPAÑA VALENCIA','223240')")
        self.change_to_window("selpac")
        time.sleep(0.5)
        
    def ver_acto_vacunal(self,clave_acto_vacunal):
        try:
            for j in range(2):
                self.driver.find_element_by_xpath('//a[contains(@href,"%s")]' % clave_acto_vacunal).click()
        except Exception:
            time.sleep(0.1)
    
    def obtener_datos_paciente(self):
        tel_fecha_nac_loc = self.driver.find_element_by_xpath('//*[contains(text(), "Teléfono:")]/..')
        try:
            telefono = re.search("\d{9}", tel_fecha_nac_loc.text).group(0)
        except AttributeError:
            telefono = "No Registrado"
        fecha_nac = re.search("\d+/\d+/\d+", tel_fecha_nac_loc.text).group(0)
        fecha_nac = pd.to_datetime(fecha_nac,format="%d/%m/%Y")
        edad = int((pd.to_datetime("today")-fecha_nac).days /365)
        name_loc = self.driver.find_element_by_xpath('//*[contains(text(), "Nombre:")]/..')
        nombre = " ".join(re.findall(
            pattern = "[A-Z]+",
            string= re.sub(
                "Nombre:|Código Postal:","",name_loc.text)))
        prov_loc = self.driver.find_element_by_xpath("//*[contains(text(),'Provincia:')]/..")
        pobl_loc = self.driver.find_element_by_xpath("//*[contains(text(),'Población:')]/..")
        prov = re.findall("\w+", prov_loc.text)[-1]
        if not (prov=="VALENCIA" or prov=="CASTELLON" or prov=="ALICANTE"):
            prov = "DESCONOCIDO"
        pobl = re.findall("\w+", pobl_loc.text)
        pobl = pobl[pobl.index("Población")+1:]
        if type(pobl) is list:
            if len(pobl) >0:
                pobl  = pobl[0]
            else:
                pobl = "DESCONOCIDO"
        return nombre,fecha_nac,edad,telefono,pobl,prov
    
    
    def save(self,row):
        self.df.loc[row,"SIP"] = int(self.sip)
        self.df.loc[row,"NOMBRE"] = self.nombre
        self.df.loc[row,"TELEFONO"] = self.telefono
        self.df.loc[row,"FECHA_NAC"] = self.fecha_nac
        self.df.loc[row,"POBLACION"] = self.pobl
        self.df.loc[row,"PROVINCIA"] = self.prov
        try:
            self.df.loc[row,"Nº Dosis"] = self.n_dosis
            self.df.loc[row,"MARCA"] = self.marca
            self.df.loc[row,"FECHA DOSIS"] = self.fecha
            self.df.loc[row,"GRUPO_RIESGO"] = self.grupo_riesgo
        except NameError:
            self.df.loc[row,"Nº Dosis"] = 0
            self.df.loc[row,"MARCA"] = "No vacunado"
            self.df.loc[row,"FECHA DOSIS"] = np.nan
            self.df.loc[row,"GRUPO_RIESGO"] = np.nan
    
    def consultar_rvn(self):
        # Ir a página de RVN
        self.driver.minimize_window()
        self.driver.get("http://rvn.sp.san.gva.es/")
        #Esto no es de este archivo BORRAR
        user = self.wait.until(EC.visibility_of_element_located(
            (By.NAME, "user")))
        user.clear()
        user.send_keys(RVN_USER)
        password = self.wait.until(EC.visibility_of_element_located(
            (By.NAME, "password")))
        password.clear()
        password.send_keys(RVN_PASS)
        self.driver.find_element_by_xpath("//*[contains(text(),'Entrar')]").click()
        self.change_to_window("PortalSIV")
        main_window_id = self.driver.window_handles[0]
        # Ir a página principal
        self.get_main_page()
        self.change_to_window("selpac")
        self.driver.find_element_by_name("SIP").clear()
        self.driver.find_element_by_name("SIP").send_keys(self.sip)
        self.wait.until(EC.visibility_of_element_located(
            (By.XPATH,'//*[contains(text(), "Siguiente")]'))).click()
        try:
            alert = self.driver.switch_to.alert
            alert.dismiss()
        except NoAlertPresentException:
            alert = False
        if alert:
            return SIP_ERROR_MSG
        # time.sleep(0.5)
        self.change_to_window("selvac")
        self.nombre,self.fecha_nac,self.edad,self.telefono,self.pobl,self.prov = self.obtener_datos_paciente()
        try:
            self.driver.execute_script("verHistorialVentana()")
            # time.sleep(0.5)
        except JavascriptException: 
            time.sleep(0.1)  
        self.check_no_page_error()
        self.change_to_window("histvacxs")
        if RVN_USER in INFO_GRIPE:
            if "GRIPE" in self.driver.page_source:
                data_gripe = self.driver.find_element_by_xpath(
                    "//*[contains(text(),'GRIPE')]/..").text
                fecha_gripe = re.search("\d+/\d+/\d+", data_gripe).group(0)
            else:
                fecha_gripe = "NO VACUNADO"
        if "Vacunacion frente a SARS-CoV-2" in self.driver.page_source:
            vacunas = self.driver.find_elements_by_xpath(
                '//*[contains(text(), "Vacunacion frente a SARS-CoV-2")]/..'
                )
            claves_vacunas = list(map(lambda x: x.get_attribute("CLAVEACTOVACUNAL"),vacunas))
            row = 0
            for i in claves_vacunas:
                if row > 0:
                    self.change_to_window("selvac")
                    try:
                        self.driver.execute_script("verHistorialVentana()")
                        # time.sleep(0.5)
                    except JavascriptException: 
                        time.sleep(0.1)  
                    self.check_no_page_error()
                    self.change_to_window("histvacxs")
                self.ver_acto_vacunal(i)
                self.change_to_window("regNoedit")    
                self.n_dosis = str(int(self.driver.find_element_by_name("DOSIS1").get_attribute("value")))
                self.marca = self.driver.find_element_by_name("LAB").get_attribute("value")
                fecha = self.driver.find_element_by_name("FechaVacV").get_attribute("value")
                fecha = pd.to_datetime(fecha,format="%d/%m/%Y")
                self.fecha = fecha.strftime("%d/%m/%Y")
                self.grupo_riesgo = self.driver.find_element_by_id("tabla_actividades").text
                self.save(row)
                row += 1
                self.driver.execute_script("pulsadoVolver();")
        else: 
            self.df = pd.DataFrame()
        if RVN_USER in INFO_GRIPE:
            return self.df, fecha_gripe
        else:
            return self.df

    def consulta_unica(self, sip):
        if RVN_USER is None or RVN_PASS is None:
            return "Faltan credenciales."
        self.sip = sip
        while True:
            try:
                self.kill.ie()
                self.driver = webdriver.Ie()
                self.wait= WebDriverWait(self.driver,30)
                self.driver.implicitly_wait(0)
                self.driver.delete_all_cookies()
                return self.consultar_rvn()
            except:
                pass
            finally:
                self.driver.quit()
                self.kill.iedriver()
            