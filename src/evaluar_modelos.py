# -*- coding: utf-8 -*-
"""
evaluar_modelos.py
==================
Version script (reproducible fuera de Colab) del pipeline de evaluacion.

Carga los 3 modelos preentrenados de Hugging Face, ejecuta inferencia sobre el
dataset de sentimiento en espanol, calcula metricas (accuracy, precision,
recall, F1) y mide la latencia. Guarda los resultados en la carpeta `results/`.

Uso:
    python src/evaluar_modelos.py \
        --datos data/dataset_sentimiento_es.csv \
        --salida results/

Requiere: transformers, torch, scikit-learn, pandas  (ver requirements.txt)
Se recomienda ejecutar con GPU; tambien funciona en CPU (mas lento).
"""

import argparse
import json
import os
import time

import pandas as pd
import torch
from transformers import pipeline

from utils_metricas import normalizar_etiqueta, calcular_metricas

# ---------------------------------------------------------------------------
# Modelos a comparar (id de Hugging Face Hub)
# ---------------------------------------------------------------------------
MODELOS = {
    "RoBERTuito (es)": "pysentimiento/robertuito-sentiment-analysis",
    "DistilBERT-multi (destilado)": "lxyuan/distilbert-base-multilingual-cased-sentiments-student",
    "XLM-RoBERTa (multi)": "cardiffnlp/twitter-xlm-roberta-base-sentiment",
}


def medir_latencia(clf, textos, repeticiones=3):
    """Latencia media por muestra (ms) con batch=1, promediando varias pasadas."""
    # Calentamiento (descarta la primera ejecucion, que incluye compilacion/caches)
    _ = clf(textos[0])
    tiempos = []
    for _ in range(repeticiones):
        inicio = time.perf_counter()
        for t in textos:
            _ = clf(t)
        tiempos.append(time.perf_counter() - inicio)
    mejor = min(tiempos)
    return (mejor / len(textos)) * 1000.0  # ms por muestra


def evaluar_modelo(nombre, model_id, textos, y_true, device):
    print(f"\n=== {nombre}  ({model_id}) ===")
    clf = pipeline("text-classification", model=model_id, tokenizer=model_id,
                   device=device, truncation=True, max_length=256)

    # Inferencia completa (medimos tiempo total)
    inicio = time.perf_counter()
    predicciones = clf(list(textos), batch_size=16)
    tiempo_total = time.perf_counter() - inicio

    y_pred = [normalizar_etiqueta(p["label"]) for p in predicciones]
    metricas = calcular_metricas(list(y_true), y_pred)

    # Latencia por muestra (batch=1)
    lat_ms = medir_latencia(clf, list(textos))

    metricas.update({
        "modelo": nombre,
        "model_id": model_id,
        "latencia_ms_por_muestra": lat_ms,
        "tiempo_total_inferencia_s": tiempo_total,
        "throughput_muestras_por_s": len(textos) / tiempo_total,
        "n_ejemplos": len(textos),
    })

    print(f"Accuracy : {metricas['accuracy']:.4f}")
    print(f"F1 macro : {metricas['f1_macro']:.4f}")
    print(f"Precision macro: {metricas['precision_macro']:.4f} | "
          f"Recall macro: {metricas['recall_macro']:.4f}")
    print(f"Latencia : {lat_ms:.2f} ms/muestra  "
          f"(throughput {metricas['throughput_muestras_por_s']:.1f} muestras/s)")
    print(metricas["classification_report"])

    # liberar memoria GPU entre modelos
    del clf
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    return metricas


def main():
    parser = argparse.ArgumentParser(description="Evaluacion comparativa de modelos de sentimiento.")
    parser.add_argument("--datos", default="data/dataset_sentimiento_es.csv")
    parser.add_argument("--salida", default="results/")
    args = parser.parse_args()

    os.makedirs(args.salida, exist_ok=True)

    df = pd.read_csv(args.datos)
    textos = df["texto"].tolist()
    y_true = df["etiqueta"].tolist()

    device = 0 if torch.cuda.is_available() else -1
    print(f"Dispositivo: {'GPU (cuda:0)' if device == 0 else 'CPU'}")
    print(f"Ejemplos: {len(textos)}")

    resumen = []
    detalle = {}
    for nombre, model_id in MODELOS.items():
        m = evaluar_modelo(nombre, model_id, textos, y_true, device)
        resumen.append({
            "modelo": m["modelo"],
            "model_id": m["model_id"],
            "accuracy": round(m["accuracy"], 4),
            "precision_macro": round(m["precision_macro"], 4),
            "recall_macro": round(m["recall_macro"], 4),
            "f1_macro": round(m["f1_macro"], 4),
            "latencia_ms_por_muestra": round(m["latencia_ms_por_muestra"], 2),
            "throughput_muestras_por_s": round(m["throughput_muestras_por_s"], 1),
        })
        # guardar detalle (sin la matriz numpy, que se serializa aparte)
        detalle[nombre] = {
            "model_id": m["model_id"],
            "accuracy": m["accuracy"],
            "precision_macro": m["precision_macro"],
            "recall_macro": m["recall_macro"],
            "f1_macro": m["f1_macro"],
            "latencia_ms_por_muestra": m["latencia_ms_por_muestra"],
            "confusion_matrix": m["confusion_matrix"].tolist(),
            "labels": m["labels"],
        }

    tabla = pd.DataFrame(resumen).sort_values("f1_macro", ascending=False)
    ruta_csv = os.path.join(args.salida, "tabla_resumen.csv")
    ruta_json = os.path.join(args.salida, "resultados_detalle.json")
    tabla.to_csv(ruta_csv, index=False)
    with open(ruta_json, "w", encoding="utf-8") as f:
        json.dump(detalle, f, ensure_ascii=False, indent=2)

    print("\n================ TABLA RESUMEN ================")
    print(tabla.to_string(index=False))
    print(f"\nGuardado: {ruta_csv}")
    print(f"Guardado: {ruta_json}")


if __name__ == "__main__":
    main()
