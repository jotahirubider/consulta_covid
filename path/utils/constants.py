import os, getpass
def get_dict_from_text():
    """Obtiene credenciales de archivo credentials.txt ubicado
    en ruta de usuario"""
    user = getpass.getuser()
    ruta = "C:/Users/%s/credentials.txt" % user
    d = {}
    with open(ruta) as f:
        for line in f:
            (key, val) = line.split()
            d[key] = val
    return d
try:
    AVE_USER = os.environ["AVE_USER"]
except KeyError:
    try:
        credentials = get_dict_from_text()
        AVE_USER = credentials.get("AVE_USER")
    except ValueError:
        AVE_USER = None
try:
    AVE_PASS = os.environ["AVE_PASS"]
except KeyError:
    try:
        credentials = get_dict_from_text()
        AVE_PASS = credentials.get("AVE_PASS")
    except ValueError:
        AVE_PASS = None
try:
    RVN_USER = os.environ["RVN_USER"]
except KeyError:
    try:
        credentials = get_dict_from_text()
        RVN_USER = credentials.get("RVN_USER")
    except ValueError:
        RVN_USER = None
try:
    RVN_PASS = os.environ["RVN_PASS"]
except KeyError:
    try:
        credentials = get_dict_from_text()
        RVN_PASS = credentials.get("RVN_PASS")
    except ValueError:
        RVN_PASS = None
try:
    REDMIVA_USER = os.environ["REDMIVA_USER"]
except KeyError:
    try:
        credentials = get_dict_from_text()
        REDMIVA_USER = credentials.get("REDMIVA_USER")
    except ValueError:
        REDMIVA_USER = None
try:
    REDMIVA_PASS = os.environ["REDMIVA_PASS"]
except KeyError:
    try:
        credentials = get_dict_from_text()
        REDMIVA_PASS = credentials.get("REDMIVA_PASS")
    except ValueError:
        REDMIVA_PASS = None        

NO_CREDENTIALS_MSG = "Faltan credenciales."
NO_DATA_MSG = "No hay datos a mostrar."
ELEMENT_FOUND_MSG = "CSV"
REDMIVA_NO_RESULTS_MSG = "No existen resultados con los filtros aplicados."
REDMIVA_LAST_PAGE_MSG = "Se encuentra en la última solicitud del listado"
REDMIVA_TESTS = {"pcr":"RNA Coronavirus SARS-CoV-2 Covid-19",
                 "antigeno":""}
NO_PAGE_MSG = "Esta página no se puede mostrar"
ERROR_FILENAME = "error.log"
SIP_ERROR_MSG = "Error en número de SIP."
RUTA_GECKODRIVER_LOG = "C:/Users/%s/geckodriver.log" % getpass.getuser()