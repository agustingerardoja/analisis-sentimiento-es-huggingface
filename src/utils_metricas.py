# -*- coding: utf-8 -*-
"""
utils_metricas.py
=================
Funciones auxiliares compartidas por el notebook y por `evaluar_modelos.py`:

  * normalizar_etiqueta(): unifica los distintos espacios de etiquetas que
    devuelven los modelos a un esquema comun {POS, NEU, NEG}.
  * calcular_metricas(): accuracy, precision, recall y F1 (macro y por clase).

Mantener esta logica en un solo lugar evita inconsistencias entre el notebook
y los scripts.
"""

from typing import List, Dict
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    classification_report,
    confusion_matrix,
)

# Esquema canonico de etiquetas usado en todo el proyecto.
ETIQUETAS_CANONICAS = ["NEG", "NEU", "POS"]

# Mapa de normalizacion. Cada modelo expone sus etiquetas de forma distinta:
#   - pysentimiento/robertuito  -> POS / NEU / NEG
#   - lxyuan/distilbert-...      -> positive / neutral / negative
#   - cardiffnlp/twitter-xlm-... -> Positive / Neutral / Negative
# Se normaliza a minusculas y se mapea al esquema canonico.
_MAPA_NORMALIZACION = {
    "pos": "POS", "positive": "POS", "positivo": "POS",
    "neu": "NEU", "neutral": "NEU", "neutro": "NEU",
    "neg": "NEG", "negative": "NEG", "negativo": "NEG",
    # Algunos modelos pueden exponer LABEL_0/1/2; se incluye por robustez.
    "label_0": "NEG", "label_1": "NEU", "label_2": "POS",
}


def normalizar_etiqueta(etiqueta: str) -> str:
    """Convierte la etiqueta cruda de un modelo al esquema canonico {NEG,NEU,POS}."""
    clave = str(etiqueta).strip().lower()
    if clave not in _MAPA_NORMALIZACION:
        raise ValueError(
            f"Etiqueta no reconocida: '{etiqueta}'. "
            f"Agregue el mapeo correspondiente en utils_metricas._MAPA_NORMALIZACION."
        )
    return _MAPA_NORMALIZACION[clave]


def calcular_metricas(y_true: List[str], y_pred: List[str]) -> Dict:
    """
    Calcula las metricas estandar de clasificacion.

    Devuelve un diccionario con accuracy, precision/recall/F1 macro y ponderado,
    el reporte por clase y la matriz de confusion.
    """
    accuracy = accuracy_score(y_true, y_pred)
    p_macro, r_macro, f1_macro, _ = precision_recall_fscore_support(
        y_true, y_pred, average="macro", labels=ETIQUETAS_CANONICAS, zero_division=0
    )
    p_w, r_w, f1_w, _ = precision_recall_fscore_support(
        y_true, y_pred, average="weighted", labels=ETIQUETAS_CANONICAS, zero_division=0
    )
    reporte = classification_report(
        y_true, y_pred, labels=ETIQUETAS_CANONICAS, zero_division=0, digits=4
    )
    matriz = confusion_matrix(y_true, y_pred, labels=ETIQUETAS_CANONICAS)
    return {
        "accuracy": accuracy,
        "precision_macro": p_macro,
        "recall_macro": r_macro,
        "f1_macro": f1_macro,
        "precision_weighted": p_w,
        "recall_weighted": r_w,
        "f1_weighted": f1_w,
        "classification_report": reporte,
        "confusion_matrix": matriz,
        "labels": ETIQUETAS_CANONICAS,
    }
