import os, logging, platform,time
os.chdir("//woody/asan/Servicios/EnfermeriaMedPreventiva/prev_dev/path")
from utils.win_fun import TaskKill
from utils.constants import NO_CREDENTIALS_MSG, ERROR_FILENAME, SIP_ERROR_MSG
from covid.consulta_rvn import RVN
from covid.consulta_redmiva import REDMIVA
from covid.consulta_ave import AVE
consultar_rvn = RVN().consulta_unica
consultar_ave = AVE().consultar_ave
consultar_redmiva = REDMIVA().consultar_redmiva
from tkinter import simpledialog, messagebox
import tkinter as tk
import xerox
architecture = platform.architecture()[0]

if architecture == "64bit":
    from threading import Thread
    class ThreadWithReturnValue(Thread):
        def __init__(self, group=None, target=None, name=None,
                      args=(), kwargs={}, Verbose=None):
            Thread.__init__(self, group, target, name, args, kwargs)
            self._return = None
        def run(self):
            print(type(self._target))
            if self._target is not None:
                self._return = self._target(*self._args,
                                                    **self._kwargs)
        def join(self, *args):
            Thread.join(self, *args)
            return self._return

def consultar_redmiva_ave(sip):
    return  consultar_redmiva(sip), consultar_ave(sip)

class ConsultaCOVID:
    def __init__(self):
        root= tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        self.sip = str(simpledialog.askinteger("Consulta COVID-19","Ingrese SIP"))
        self.sip.replace(" ","")
        root.destroy()
        if (not self.sip) or self.sip == "None":
            os._exit(1)
    def run(self):
        try:
            if architecture == "64bit":
                t1 = ThreadWithReturnValue(target=consultar_redmiva_ave,args=(self.sip,))
                t2 = ThreadWithReturnValue(target=consultar_rvn,args=(self.sip,))
                t1.start()
                t2.start()
                print("".center(50,"-"))
                print("Iniciando consulta en RVN-AVE-REDMIVA...".ljust(50," "))
                print("".center(50,"-"))
                print("".center(50,"-"))
                print("Esperando resultados de RVN...".ljust(50," "))
                print("".center(50,"-"))
                vacunacion = t2.join()
                if str(vacunacion) == SIP_ERROR_MSG:
                    root= tk.Tk()
                    root.withdraw()
                    root.attributes("-topmost", True)
                    messagebox.showerror("Error","Error en el nº SIP.\nPor favor revíselo y vuelva a intentarlo.")
                    time.sleep(1)
                    kill = TaskKill()
                    kill.firefox()
                    kill.geckodriver()
                    os._exit(1)
                print("".center(50,"-"))
                print("Esperando resultados de AVE-REDMIVA...".ljust(50," "))
                print("".center(50,"-"))
                pruebas, infeccion = t1.join()
            elif architecture == "32bit":
                print("".center(50,"-"))
                print("Iniciando consulta en RVN-AVE-REDMIVA...".ljust(50," "))
                print("".center(50,"-"))
                print("".center(50,"-"))
                print("Esperando resultados de RVN...".ljust(50," "))
                print("".center(50,"-"))
                vacunacion = consultar_rvn(self.sip)
                if vacunacion == SIP_ERROR_MSG:
                    root= tk.Tk()
                    root.withdraw()
                    root.attributes("-topmost", True)
                    messagebox.showerror("Error","Error en el nº SIP. Por favor revíselo y vuelva a intentarlo")
                    os._exit(1)
                print("".center(50,"-"))
                print("Esperando resultados de REDMIVA...".ljust(50," "))
                print("".center(50,"-"))
                pruebas = consultar_redmiva(self.sip)
                print("".center(50,"-"))
                print("Esperando resultados de AVE...".ljust(50," "))
                print("".center(50,"-"))
                infeccion = consultar_ave(self.sip)
            if not str(vacunacion) == NO_CREDENTIALS_MSG:
                if not len(vacunacion)==0:
                    vacunacion = vacunacion.drop(columns=["TELEFONO",
                                                            "GRUPO_RIESGO",
                                                            "FECHA_NAC",
                                                            "PROVINCIA",
                                                            "POBLACION"])
                    nombre = vacunacion.loc[0,"NOMBRE"]
                    vacunacion = vacunacion.drop(columns=["NOMBRE","SIP"])
                else: 
                    nombre = ""
                    vacunacion = "NO VACUNADO"
            if not str(pruebas) == NO_CREDENTIALS_MSG:
                if len(pruebas) == 0:
                    pruebas = "SIN PRUEBAS"
                else:
                    pruebas = pruebas[pruebas["Determinación"].str.contains("SARS-CoV-2")]
                    pruebas = pruebas[~pruebas["1er. Resultado"].str.contains("Negativo")]
                    pruebas.loc[pruebas["Determinación"].str.contains("RNA Coronavirus"),"Determinación"] = "PCR SARS-CoV-2"
                    if len(pruebas)==0:
                        pruebas = "SIN PRUEBAS"
            if not str(infeccion) == NO_CREDENTIALS_MSG:
                infeccion, infeccion_datos = infeccion
                if infeccion == "SI":
                    infeccion_datos = infeccion_datos.drop(columns=["NOMBRE","SIP"])
                    infeccion_datos.columns = ["Fecha infección"]
                    infeccion_datos[["Nro. infección"]] = infeccion_datos.index + 1
                    infeccion_datos = infeccion_datos[["Nro. infección", "Fecha infección"]]
            else:
                infeccion_datos=""
            resultado = """{}{}

INFECCION (AVE): {}{}
MICROBIOLOGÍA (REDMIVA){}\n
VACUNAS{}
""".format(
"NOMBRE: " + nombre if not nombre=="" else "\n",
"SIP: " + self.sip if nombre=="" else "\nSIP: " + self.sip,
infeccion, 
"\n" if infeccion == "NO" else (infeccion_datos if isinstance(infeccion_datos,str) else "\n" + infeccion_datos.to_string(
    index=False, justify="left") + "\n"),

": " + pruebas if isinstance(pruebas, str) else "\n" + pruebas.to_string(  index=False, justify="left"),

": " + vacunacion if isinstance(vacunacion,str) else "\n" + vacunacion.to_string(index=False, justify="left")) + "\n"
            root= tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            msg = resultado + "¿Desea copiar el resultado al portapapeles?"
            print("".center(50,"-"))
            print("Resultados generados, disponibles en ventana emergente.".ljust(50," "))
            print("".center(50,"-"))
            answer = messagebox.askyesno("Búsqueda SIP %s" % self.sip, msg)
            if answer:
                xerox.copy(resultado)
            
        except Exception:
            logging.exception("EXCEPTION TRACEBACK")
            os._exit(1)
            
ConsultaCOVID().run()
