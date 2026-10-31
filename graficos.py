"""
Proyecto: Tipo de cambio, inflación y actividad en Argentina (2017-2026)
PASO 2: gráficos. Lee datos/datos_unidos.csv y guarda 4 imágenes en la carpeta "resultados".
"""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

BASE = Path(__file__).parent
SALIDA = BASE / "resultados"
SALIDA.mkdir(exist_ok=True)  # crea la carpeta si no existe

datos = pd.read_csv(BASE / "datos" / "datos_unidos.csv", parse_dates=["indice_tiempo"], index_col="indice_tiempo")

FUENTE = "Fuente: INDEC y Banco Nación, vía datos.gob.ar. Elaboración propia."
AZUL, NARANJA, GRIS = "#1f4e79", "#d9822b", "#7f7f7f"

plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False, "font.size": 10})


def guardar(fig, nombre):
    fig.text(0.01, 0.01, FUENTE, fontsize=8, color=GRIS)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(SALIDA / nombre, dpi=150)
    plt.close(fig)
    print("Guardado:", nombre)


# --- Gráfico 1: inflación vs devaluación (variación interanual) ---
fig, ax = plt.subplots(figsize=(9, 4.5))
ax.plot(datos.index, datos["inflacion_interanual"], color=AZUL, label="Inflación (IPC)")
ax.plot(datos.index, datos["devaluacion_interanual"], color=NARANJA, label="Tipo de cambio")
ax.set_title("Inflación y tipo de cambio: variación interanual")
ax.set_ylabel("% respecto del mismo mes del año anterior")
ax.legend(frameon=False)
guardar(fig, "1_inflacion_vs_tipo_cambio.png")

# --- Gráfico 2: IPC y tipo de cambio con base 100 = enero 2017 (escala logarítmica) ---
base100 = datos[["ipc", "tipo_cambio"]] / datos[["ipc", "tipo_cambio"]].iloc[0] * 100
fig, ax = plt.subplots(figsize=(9, 4.5))
ax.plot(base100.index, base100["ipc"], color=AZUL, label="Precios (IPC)")
ax.plot(base100.index, base100["tipo_cambio"], color=NARANJA, label="Tipo de cambio")
ax.set_yscale("log")  # en log, una misma pendiente significa el mismo ritmo de crecimiento
ax.set_title("Precios y tipo de cambio acumulados (enero 2017 = 100, escala log)")
ax.set_ylabel("Índice")
ax.legend(frameon=False)
guardar(fig, "2_precios_y_tipo_cambio_base100.png")

# --- Gráfico 3: actividad económica (EMAE), variación interanual ---
act = datos["actividad_interanual"].dropna()
fig, ax = plt.subplots(figsize=(9, 4.5))
colores = [AZUL if v >= 0 else NARANJA for v in act]
ax.bar(act.index, act.values, width=25, color=colores)
ax.axhline(0, color=GRIS, linewidth=0.8)
ax.set_title("Actividad económica (EMAE): variación interanual")
ax.set_ylabel("%")
guardar(fig, "3_actividad_emae_interanual.png")

# --- Gráfico 4: dispersión devaluación mensual vs inflación mensual ---
fig, ax = plt.subplots(figsize=(6.5, 5))
ax.scatter(datos["devaluacion_mensual"], datos["inflacion_mensual"], color=AZUL, alpha=0.7)
dic23 = datos.loc["2023-12-01"]
ax.annotate("Dic-2023", (dic23["devaluacion_mensual"], dic23["inflacion_mensual"]),
            textcoords="offset points", xytext=(-55, -5))
ax.set_title("Devaluación e inflación, variación mensual")
ax.set_xlabel("Variación mensual del tipo de cambio (%)")
ax.set_ylabel("Variación mensual del IPC (%)")
guardar(fig, "4_dispersion_mensual.png")