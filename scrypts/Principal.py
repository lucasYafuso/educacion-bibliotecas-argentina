#ESTE SCRIPT CONTIENE 4 BLOQUES: FUNCIONES DE GQM, LIMPIEZA DE DATOS, CONSULTAS DE SQL Y VISUALIZACION DE DATOS
# EN CADA BLOQUE SE IMPORTARAN LAS FUNCIONES DESARROLLADAS EN LA NOTEBOOK DETERMINADA.


#Importes de algunas librerias
import importlib
import sys
from pathlib import Path

path="C:/Users/FLORES/Documents/Nacho/Labo de datos/TP 1/"  #cambiar el path a donde esten guardados los archivos

PROJECT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_DIR))   # permite importaciones relativas


modules_to_run = [
    "dataframes",      # genera los CSV base
    "consultasSQL",    # corre las queries y guarda resultados
    "Graficos",        # produce los gráficos finales
]


for mod in modules_to_run:
    print(f"\n--> Ejecutando {mod}.py …")
    if mod in sys.modules:
        importlib.reload(sys.modules[mod])     # ya estaba: recarga
    else:
        importlib.import_module(mod)           # primera vez: importa

print("\nFlujo completo terminado: CSV y gráficos generados.")
