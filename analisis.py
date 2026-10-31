"""
Proyecto: Tipo de cambio, inflación y actividad en Argentina (2017-2026)
PASO 1: cargar los datos, unirlos por mes y calcular variaciones.
"""
from pathlib import Path

import pandas as pd

# Mostrar todas las columnas en la terminal (sin cortarlas con "...")
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)

# Carpeta "datos", ubicada al lado de este archivo
CARPETA = Path(__file__).parent / "datos"


def cargar(nombre_archivo, nombre_columna):
    """Lee un CSV de datos.gob.ar y devuelve una tabla con la fecha como índice."""
    df = pd.read_csv(CARPETA / nombre_archivo, parse_dates=["indice_tiempo"])
    df = df.set_index("indice_tiempo")   # la fecha pasa a ser el "nombre de fila"
    df.columns = [nombre_columna]        # le ponemos un nombre corto a la columna
    return df


# 1) Cargar las tres series
ipc = cargar("ipc.csv", "ipc")                    # índice de precios (base dic-2016 = 100)
tc = cargar("tipo_cambio.csv", "tipo_cambio")     # pesos por dólar, promedio mensual
emae = cargar("emae.csv", "emae")                 # índice de actividad económica

# 2) Unirlas por fecha. "inner" se queda solo con los meses que existen en las tres
datos = ipc.join([tc, emae], how="inner")

# 3) Calcular variaciones porcentuales
#    pct_change()   -> variación contra el mes anterior
#    pct_change(12) -> variación contra el mismo mes del año anterior (interanual)
datos["inflacion_mensual"] = datos["ipc"].pct_change() * 100
datos["devaluacion_mensual"] = datos["tipo_cambio"].pct_change() * 100
datos["inflacion_interanual"] = datos["ipc"].pct_change(12) * 100
datos["devaluacion_interanual"] = datos["tipo_cambio"].pct_change(12) * 100
datos["actividad_interanual"] = datos["emae"].pct_change(12) * 100

# 4) Revisar que todo esté bien
print("Período:", datos.index.min().strftime("%Y-%m"), "a", datos.index.max().strftime("%Y-%m"))
print("Cantidad de meses:", len(datos))
print("\nPrimeras filas:")
print(datos.head(3).round(2))
print("\nÚltimas filas:")
print(datos.tail(3).round(2))
print("\nResumen estadístico (variaciones mensuales):")
print(datos[["inflacion_mensual", "devaluacion_mensual"]].describe().round(2))

# 5) Guardar la tabla unida para usarla en el paso siguiente
datos.to_csv(CARPETA / "datos_unidos.csv")
print("\nGuardado: datos/datos_unidos.csv")