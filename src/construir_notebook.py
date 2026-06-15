# -*- coding: utf-8 -*-
"""
construir_notebook.py
=====================
Ensambla el notebook de Colab (.ipynb) de forma programatica para garantizar
JSON valido. El dataset se embebe inline importando las listas desde
generar_dataset.py (fuente unica de verdad).

Uso:
    python src/construir_notebook.py
Genera: notebooks/analisis_comparativo_sentimiento.ipynb
"""
import json
import os

from generar_dataset import POSITIVOS, NEUTRALES, NEGATIVOS

CELLS = []


def add_md(text):
    CELLS.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": text.strip("\n").splitlines(keepends=True),
    })


def add_code(text):
    CELLS.append({
        "cell_type": "code",
        "metadata": {},
        "execution_count": None,
        "outputs": [],
        "source": text.strip("\n").splitlines(keepends=True),
    })


def literal_lista(nombre, datos):
    """Genera el texto de una lista de tuplas (texto, dominio) como literal Python."""
    lineas = [f"{nombre} = [\n"]
    for texto, dominio in datos:
        lineas.append(f"    ({texto!r}, {dominio!r}),\n")
    lineas.append("]\n")
    return "".join(lineas)


# ===========================================================================
# 0. Portada
# ===========================================================================
add_md(r"""
# Análisis comparativo de modelos preentrenados de Hugging Face
## Caso de uso: Análisis de sentimiento en español (NLP)

**Maestría — Actividad: selección e implementación de modelos preentrenados.**

Este cuaderno implementa y compara **tres** modelos preentrenados de clasificación
de sentimiento en español, descargados de **Hugging Face Hub**, sobre un dataset
de evaluación balanceado de 120 reseñas/opiniones cortas (clases `POS`, `NEU`, `NEG`).

| # | Modelo (Hugging Face) | Base | Idioma | Licencia |
|---|------------------------|------|--------|----------|
| 1 | `pysentimiento/robertuito-sentiment-analysis` | RoBERTuito (RoBERTa-es) | Español | No comercial / investigación |
| 2 | `lxyuan/distilbert-base-multilingual-cased-sentiments-student` | DistilBERT multilingüe (destilado) | Multilingüe | Apache-2.0 |
| 3 | `cardiffnlp/twitter-xlm-roberta-base-sentiment` | XLM-RoBERTa base | Multilingüe | Académica (repo XLM-T, MIT) |

**Contenido del cuaderno**
1. Configuración de GPU
2. Instalación de dependencias
3. Autenticación en Hugging Face Hub
4. Carga del dataset
5. Carga de modelos y pipeline de inferencia
6. Métricas y normalización de etiquetas
7. Evaluación (inferencia + métricas + latencia)
8. Tablas y gráficas comparativas
9. Conclusiones parciales

> **Cómo ejecutar:** menú *Entorno de ejecución → Cambiar tipo de entorno de ejecución → T4 GPU*,
> luego *Entorno de ejecución → Ejecutar todo*. Tiempo aproximado: 3–6 minutos (incluye descarga de modelos).
""")

# ===========================================================================
# 1. GPU
# ===========================================================================
add_md(r"""
## 1. Configuración de GPU

Verificamos que el entorno tenga una GPU asignada (en Colab gratuito suele ser una
**NVIDIA T4**). Si `CUDA disponible: False`, activa la GPU en
*Entorno de ejecución → Cambiar tipo de entorno de ejecución → T4 GPU*.
""")
add_code(r"""
import torch

print("Versión de PyTorch:", torch.__version__)
print("CUDA disponible :", torch.cuda.is_available())
if torch.cuda.is_available():
    print("GPU             :", torch.cuda.get_device_name(0))
    print("Memoria total   : %.1f GB" % (torch.cuda.get_device_properties(0).total_memory / 1e9))
else:
    print(">> No hay GPU. El cuaderno funciona en CPU, pero la latencia será mucho mayor.")

# Detalle del hardware (ignora el error si no hay GPU)
!nvidia-smi -L
""")

# ===========================================================================
# 2. Dependencias
# ===========================================================================
add_md(r"""
## 2. Instalación de dependencias

`torch` ya viene preinstalado en Colab. Instalamos `transformers`, `huggingface_hub`
y **`sentencepiece`** (necesario para el *tokenizer* de XLM-RoBERTa). `scikit-learn`,
`pandas` y `matplotlib` también vienen en Colab; se incluyen por reproducibilidad.
""")
add_code(r"""
%pip -q install -U "transformers>=4.40" "huggingface_hub>=0.23" sentencepiece accelerate
%pip -q install -U scikit-learn pandas matplotlib

import transformers, sklearn, pandas as pd
print("transformers:", transformers.__version__)
print("scikit-learn:", sklearn.__version__)
print("pandas      :", pd.__version__)
""")

# ===========================================================================
# 3. Autenticación HF
# ===========================================================================
add_md(r"""
## 3. Autenticación en Hugging Face Hub

Los tres modelos son **públicos**, por lo que la autenticación es *opcional* para
descargarlos. Aun así, autenticarse es una **buena práctica** (evita límites de
descarga anónima y es obligatorio para modelos *gated* o privados).

Dos opciones:
- **A) Token en Secretos de Colab** (recomendado): panel 🔑 a la izquierda → añade un
  secreto `HF_TOKEN` con tu token de https://huggingface.co/settings/tokens.
- **B) Login interactivo:** descomenta `notebook_login()`.
""")
add_code(r"""
import os
from huggingface_hub import login

token = None
# Opción A: Secreto de Colab llamado HF_TOKEN
try:
    from google.colab import userdata
    token = userdata.get("HF_TOKEN")
except Exception:
    token = os.environ.get("HF_TOKEN")

if token:
    login(token=token)
    print("Autenticado en Hugging Face Hub mediante token.")
else:
    print("Sin token: se continuará en modo anónimo (suficiente para modelos públicos).")
    # Opción B (interactiva), descomenta si lo prefieres:
    # from huggingface_hub import notebook_login
    # notebook_login()
""")

# ===========================================================================
# 4. Dataset (embebido inline = self-contained)
# ===========================================================================
add_md(r"""
## 4. Carga del dataset

El dataset de evaluación se **embebe en el propio cuaderno** (mismas 120 frases del
archivo `data/dataset_sentimiento_es.csv` del repositorio), de modo que el notebook
es **autocontenido** y se puede ejecutar sin clonar nada. También se guarda una copia
en `data/` para trazabilidad.

- Origen: corpus original curado por los autores (ver `data/README_dataset.md`).
- Clases: `POS`, `NEU`, `NEG` — **balanceado** (40 por clase).
""")
add_code(
    literal_lista("POSITIVOS", POSITIVOS) + "\n"
    + literal_lista("NEUTRALES", NEUTRALES) + "\n"
    + literal_lista("NEGATIVOS", NEGATIVOS) + "\n"
    + r"""
import os
import pandas as pd

filas, idx = [], 1
for etiqueta, ejemplos in [("POS", POSITIVOS), ("NEU", NEUTRALES), ("NEG", NEGATIVOS)]:
    for texto, dominio in ejemplos:
        filas.append({"id": f"es-{idx:03d}", "texto": texto, "etiqueta": etiqueta,
                      "dominio": dominio, "longitud_caracteres": len(texto),
                      "num_palabras": len(texto.split())})
        idx += 1

df = pd.DataFrame(filas)
os.makedirs("data", exist_ok=True)
df.to_csv("data/dataset_sentimiento_es.csv", index=False, encoding="utf-8")

print("Total de ejemplos:", len(df))
print(df["etiqueta"].value_counts())
df.head()
""")

# ===========================================================================
# 5. Modelos + pipeline
# ===========================================================================
add_md(r"""
## 5. Carga de modelos y pipeline de inferencia

Definimos los tres modelos y una función que construye un `pipeline` de
`text-classification` sobre la GPU (`device=0`) o CPU (`device=-1`). Incluimos un
preprocesamiento ligero (reemplazo de menciones y URLs) recomendado por los modelos
entrenados con tweets.
""")
add_code(r"""
from transformers import pipeline

MODELOS = {
    "RoBERTuito (es)":              "pysentimiento/robertuito-sentiment-analysis",
    "DistilBERT-multi (destilado)": "lxyuan/distilbert-base-multilingual-cased-sentiments-student",
    "XLM-RoBERTa (multi)":          "cardiffnlp/twitter-xlm-roberta-base-sentiment",
}

DEVICE = 0 if torch.cuda.is_available() else -1

def preprocesar(texto):
    # Normaliza menciones @usuario y enlaces (convención de los modelos de Twitter)
    palabras = []
    for t in texto.split(" "):
        if t.startswith("@") and len(t) > 1:
            t = "@user"
        elif t.startswith("http"):
            t = "http"
        palabras.append(t)
    return " ".join(palabras)

def construir_pipeline(model_id):
    return pipeline("text-classification", model=model_id, tokenizer=model_id,
                    device=DEVICE, truncation=True, max_length=256)

# Prueba rápida con un modelo
demo = construir_pipeline(MODELOS["RoBERTuito (es)"])
print(demo("Que gran jugador es Messi"))
print(demo("El producto llego roto y nadie responde"))
del demo
if torch.cuda.is_available():
    torch.cuda.empty_cache()
""")

# ===========================================================================
# 6. Métricas
# ===========================================================================
add_md(r"""
## 6. Métricas y normalización de etiquetas

Cada modelo expone etiquetas distintas (`POS/NEU/NEG`, `positive/neutral/negative`,
`Positive/Neutral/Negative`). Esta es la única **decisión de ajuste mínimo** necesaria:
normalizar todas las salidas a un esquema canónico `{NEG, NEU, POS}` para poder
compararlas de forma homogénea. Después calculamos *accuracy*, *precision*, *recall*
y *F1* (macro y por clase).
""")
add_code(r"""
from sklearn.metrics import (accuracy_score, precision_recall_fscore_support,
                             classification_report, confusion_matrix)

ETIQUETAS = ["NEG", "NEU", "POS"]

_MAPA = {
    "pos": "POS", "positive": "POS", "positivo": "POS",
    "neu": "NEU", "neutral": "NEU", "neutro": "NEU",
    "neg": "NEG", "negative": "NEG", "negativo": "NEG",
    "label_0": "NEG", "label_1": "NEU", "label_2": "POS",
}

def normalizar_etiqueta(etiqueta):
    clave = str(etiqueta).strip().lower()
    if clave not in _MAPA:
        raise ValueError(f"Etiqueta no reconocida: {etiqueta!r}")
    return _MAPA[clave]

def calcular_metricas(y_true, y_pred):
    acc = accuracy_score(y_true, y_pred)
    p, r, f1, _ = precision_recall_fscore_support(
        y_true, y_pred, average="macro", labels=ETIQUETAS, zero_division=0)
    return {"accuracy": acc, "precision_macro": p, "recall_macro": r, "f1_macro": f1}

# Comprobación del normalizador
print([normalizar_etiqueta(x) for x in ["POS", "positive", "Negative", "NEU"]])
""")

# ===========================================================================
# 7. Evaluación + latencia
# ===========================================================================
add_md(r"""
## 7. Evaluación: inferencia, métricas y latencia

Para cada modelo:
1. Descargamos y construimos el pipeline.
2. Hacemos **inferencia por lotes** (`batch_size=16`) sobre las 120 frases.
3. Calculamos las métricas frente a las etiquetas de referencia.
4. Medimos la **latencia media por muestra** con `batch=1` (escenario de petición
   individual), descartando una pasada de calentamiento.
""")
add_code(r"""
import time

def medir_latencia(clf, textos, repeticiones=3):
    _ = clf(textos[0])  # calentamiento
    tiempos = []
    for _ in range(repeticiones):
        t0 = time.perf_counter()
        for t in textos:
            _ = clf(t)
        tiempos.append(time.perf_counter() - t0)
    return (min(tiempos) / len(textos)) * 1000.0  # ms/muestra

textos = [preprocesar(t) for t in df["texto"].tolist()]
y_true = df["etiqueta"].tolist()

resultados, detalle = [], {}
for nombre, model_id in MODELOS.items():
    print(f"\n=== {nombre}  ({model_id}) ===")
    clf = construir_pipeline(model_id)

    t0 = time.perf_counter()
    preds = clf(textos, batch_size=16)
    t_total = time.perf_counter() - t0

    y_pred = [normalizar_etiqueta(p["label"]) for p in preds]
    m = calcular_metricas(y_true, y_pred)
    lat = medir_latencia(clf, textos)

    print("Accuracy: %.4f | F1 macro: %.4f | Precisión: %.4f | Recall: %.4f"
          % (m["accuracy"], m["f1_macro"], m["precision_macro"], m["recall_macro"]))
    print("Latencia: %.2f ms/muestra | throughput lote: %.1f muestras/s"
          % (lat, len(textos) / t_total))
    print(classification_report(y_true, y_pred, labels=ETIQUETAS, zero_division=0, digits=4))

    resultados.append({"modelo": nombre, "accuracy": m["accuracy"],
                       "precision_macro": m["precision_macro"], "recall_macro": m["recall_macro"],
                       "f1_macro": m["f1_macro"], "latencia_ms": lat,
                       "throughput_muestras_s": len(textos) / t_total})
    detalle[nombre] = {"y_pred": y_pred,
                       "cm": confusion_matrix(y_true, y_pred, labels=ETIQUETAS)}
    del clf
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
""")

# ===========================================================================
# 8. Tablas y gráficas
# ===========================================================================
add_md(r"""
## 8. Tablas y gráficas comparativas

Resumimos los resultados en una tabla ordenada por *F1 macro* y los guardamos en
`results/`. Después graficamos: (a) F1 vs. accuracy, (b) latencia vs. F1
(trade-off eficiencia/precisión) y (c) matrices de confusión.
""")
add_code(r"""
import os
os.makedirs("results", exist_ok=True)

tabla = pd.DataFrame(resultados).sort_values("f1_macro", ascending=False).reset_index(drop=True)
tabla_fmt = tabla.copy()
for c in ["accuracy", "precision_macro", "recall_macro", "f1_macro"]:
    tabla_fmt[c] = tabla_fmt[c].map(lambda x: round(x, 4))
tabla_fmt["latencia_ms"] = tabla_fmt["latencia_ms"].map(lambda x: round(x, 2))
tabla_fmt["throughput_muestras_s"] = tabla_fmt["throughput_muestras_s"].map(lambda x: round(x, 1))

tabla_fmt.to_csv("results/tabla_resumen.csv", index=False)
print("Tabla guardada en results/tabla_resumen.csv")
tabla_fmt
""")
add_code(r"""
import matplotlib.pyplot as plt
import numpy as np

# (a) Barras: F1 macro y accuracy
fig, ax = plt.subplots(figsize=(8, 4.5))
x = np.arange(len(tabla)); w = 0.38
ax.bar(x - w/2, tabla["f1_macro"], w, label="F1 macro")
ax.bar(x + w/2, tabla["accuracy"], w, label="Accuracy")
ax.set_xticks(x); ax.set_xticklabels(tabla["modelo"], rotation=15, ha="right")
ax.set_ylim(0, 1); ax.set_ylabel("Puntuación"); ax.set_title("Precisión por modelo")
ax.legend(); ax.grid(axis="y", alpha=0.3)
plt.tight_layout(); plt.savefig("results/fig_precision.png", dpi=150); plt.show()
""")
add_code(r"""
# (b) Trade-off: latencia (ms) vs F1 macro
fig, ax = plt.subplots(figsize=(7, 5))
ax.scatter(tabla["latencia_ms"], tabla["f1_macro"], s=120)
for _, row in tabla.iterrows():
    ax.annotate(row["modelo"], (row["latencia_ms"], row["f1_macro"]),
                textcoords="offset points", xytext=(8, 6), fontsize=9)
ax.set_xlabel("Latencia (ms/muestra)  —  menor es mejor")
ax.set_ylabel("F1 macro  —  mayor es mejor")
ax.set_title("Trade-off eficiencia vs. precisión")
ax.grid(alpha=0.3)
plt.tight_layout(); plt.savefig("results/fig_tradeoff.png", dpi=150); plt.show()
""")
add_code(r"""
# (c) Matrices de confusión
fig, axes = plt.subplots(1, 3, figsize=(13, 4))
for ax, (nombre, d) in zip(axes, detalle.items()):
    cm = d["cm"]
    im = ax.imshow(cm, cmap="Blues")
    ax.set_title(nombre, fontsize=10)
    ax.set_xticks(range(3)); ax.set_xticklabels(ETIQUETAS)
    ax.set_yticks(range(3)); ax.set_yticklabels(ETIQUETAS)
    ax.set_xlabel("Predicho"); ax.set_ylabel("Real")
    for i in range(3):
        for j in range(3):
            ax.text(j, i, cm[i, j], ha="center", va="center",
                    color="white" if cm[i, j] > cm.max()/2 else "black")
plt.tight_layout(); plt.savefig("results/fig_matrices_confusion.png", dpi=150); plt.show()
""")

# ===========================================================================
# 9. Conclusiones parciales
# ===========================================================================
add_md(r"""
## 9. Conclusiones parciales

La siguiente celda genera conclusiones **a partir de los números reales** obtenidos
en esta ejecución (modelo más preciso, más rápido y mejor equilibrado).
""")
add_code(r"""
mejor_f1   = tabla.loc[tabla["f1_macro"].idxmax()]
mas_rapido = tabla.loc[tabla["latencia_ms"].idxmin()]

# Eficiencia = F1 por cada ms de latencia (mayor es mejor)
tabla["eficiencia_f1_por_ms"] = tabla["f1_macro"] / tabla["latencia_ms"]
mejor_equilibrio = tabla.loc[tabla["eficiencia_f1_por_ms"].idxmax()]

print("CONCLUSIONES PARCIALES (ejecución actual)")
print("-" * 55)
print(f"• Mayor F1 macro : {mejor_f1['modelo']}  (F1={mejor_f1['f1_macro']:.4f}, "
      f"acc={mejor_f1['accuracy']:.4f})")
print(f"• Más rápido     : {mas_rapido['modelo']}  ({mas_rapido['latencia_ms']:.2f} ms/muestra)")
print(f"• Mejor equilibrio precisión/latencia: {mejor_equilibrio['modelo']}")
print()
print("Lectura del trade-off:")
print("  - El modelo destilado (DistilBERT, 6 capas) maximiza velocidad.")
print("  - El modelo especializado en español (RoBERTuito) suele liderar en F1")
print("    sobre texto corto/informal en español.")
print("  - XLM-RoBERTa (270M) aporta robustez multilingüe a mayor costo de latencia.")
""")
add_md(r"""
### Síntesis

- **Calidad (F1/accuracy):** se espera que **RoBERTuito** lidere en español por estar
  especializado en el idioma y dominio (tweets), seguido de cerca por **XLM-RoBERTa**;
  el **DistilBERT destilado** queda por debajo al provenir de destilación *zero-shot*.
- **Eficiencia (latencia):** **DistilBERT** es el más rápido (la mitad de capas),
  ideal para alto volumen o dispositivos limitados.
- **Licencia:** solo **DistilBERT (Apache-2.0)** permite uso comercial sin fricción;
  RoBERTuito es de uso no comercial / investigación.
- **Recomendación (prototipo académico en español):** **RoBERTuito** por su mejor
  relación precisión/recursos en español. Para producción comercial o multilingüe,
  evaluar **XLM-RoBERTa** (precisión) o **DistilBERT** (eficiencia + licencia).

> Los valores definitivos provienen de la tabla generada arriba en *tu* ejecución.
> El reporte en Word (`docs/Analisis_Comparativo_Modelos.docx`) amplía criterios,
> trade-offs, umbrales y riesgos.
""")

# ===========================================================================
# Serializa el notebook
# ===========================================================================
notebook = {
    "cells": CELLS,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.10"},
        "colab": {"provenance": [], "gpuType": "T4", "toc_visible": True},
        "accelerator": "GPU",
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

os.makedirs("notebooks", exist_ok=True)
ruta = "notebooks/analisis_comparativo_sentimiento.ipynb"
with open(ruta, "w", encoding="utf-8") as f:
    json.dump(notebook, f, ensure_ascii=False, indent=1)
print(f"Notebook generado: {ruta}  ({len(CELLS)} celdas)")
