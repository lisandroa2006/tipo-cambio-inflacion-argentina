"""
Proyecto: Tipo de cambio, inflación y actividad en Argentina (2017-2026)
PASO 3: regresión del traspaso del tipo de cambio a precios (pass-through).

Modelo:  inflación_mensual(t) = a + b0*devaluación(t) + b1*devaluación(t-1) + b2*devaluación(t-2) + error
La suma b0+b1+b2 mide cuántos puntos de inflación se agregan, en tres meses,
por cada punto de devaluación.
"""
from pathlib import Path

import pandas as pd
import statsmodels.api as sm

BASE = Path(__file__).parent
SALIDA = BASE / "resultados"
SALIDA.mkdir(exist_ok=True)

datos = pd.read_csv(BASE / "datos" / "datos_unidos.csv", parse_dates=["indice_tiempo"], index_col="indice_tiempo")

# 1) Rezagos: el efecto del dólar sobre los precios no es inmediato, se reparte en varios meses.
#    shift(1) corre la serie un mes hacia adelante: en la fila de marzo queda el valor de febrero.
datos["dev_rezago1"] = datos["devaluacion_mensual"].shift(1)
datos["dev_rezago2"] = datos["devaluacion_mensual"].shift(2)
explicativas = ["devaluacion_mensual", "dev_rezago1", "dev_rezago2"]

# 2) Quedarnos solo con los meses completos (los primeros meses quedan con vacíos por los rezagos)
muestra = datos.dropna(subset=["inflacion_mensual"] + explicativas)


def estimar(df):
    """Regresión por mínimos cuadrados (OLS) con errores estándar robustos (HC1)."""
    X = sm.add_constant(df[explicativas])  # agrega la constante "a"
    return sm.OLS(df["inflacion_mensual"], X).fit(cov_type="HC1")


# 3) Dos versiones: con todos los meses, y sin diciembre de 2023 (un caso extremo)
modelo_completo = estimar(muestra)
modelo_sin_dic23 = estimar(muestra.drop(pd.Timestamp("2023-12-01")))

# 4) Mostrar y guardar resultados
lineas = []
for nombre, modelo in [("TODOS LOS MESES", modelo_completo), ("SIN DICIEMBRE 2023", modelo_sin_dic23)]:
    traspaso = modelo.params[explicativas].sum()
    lineas.append(f"===== {nombre} (n = {int(modelo.nobs)}) =====")
    lineas.append(str(modelo.summary().tables[1]))
    lineas.append(f"R2 = {modelo.rsquared:.3f}")
    lineas.append(f"Traspaso acumulado a 3 meses (b0+b1+b2) = {traspaso:.2f}")
    lineas.append(f"  -> 10 puntos de devaluación se asocian a {traspaso * 10:.1f} puntos de inflación acumulada\n")

texto = "\n".join(lineas)
print(texto)
(SALIDA / "regresion.txt").write_text(texto, encoding="utf-8")
print("Guardado: resultados/regresion.txt")