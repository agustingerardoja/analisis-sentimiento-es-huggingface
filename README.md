# Análisis comparativo de modelos preentrenados de Hugging Face — Sentimiento en español

[![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/agustingerardoja/analisis-sentimiento-es-huggingface/blob/main/notebooks/analisis_comparativo_sentimiento.ipynb)
[![Licencia: MIT](https://img.shields.io/badge/Licencia-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)

Selección, implementación y comparación de **tres modelos preentrenados** de Hugging Face
para **análisis de sentimiento en español** (NLP), prototipados en **Google Colab con GPU**.
El proyecto compara los modelos con métricas estándar (*accuracy, precision, recall, F1*),
mide su **latencia** y analiza el **trade-off eficiencia vs. precisión** para recomendar el
modelo más adecuado al caso de uso.

## 1. Descripción del proyecto

Clasificación de opiniones/reseñas en español en tres clases: **positivo (POS)**,
**neutral (NEU)** y **negativo (NEG)**. Se evalúan tres modelos de perfiles complementarios:

| Modelo (Hugging Face) | Base | Parámetros | Licencia | F1 macro (ref.) |
|------------------------|------|-----------:|----------|:---------------:|
| `pysentimiento/robertuito-sentiment-analysis` | RoBERTuito (12 capas) | ~108 M | No comercial / investigación | **0.705** (TASS 2020) |
| `lxyuan/distilbert-base-multilingual-cased-sentiments-student` | DistilBERT multiling. (6 capas) | ~135 M | Apache-2.0 | — (destilado) |
| `cardiffnlp/twitter-xlm-roberta-base-sentiment` | XLM-RoBERTa base (12 capas) | ~278 M | Académica (XLM-T, MIT) | 0.679 (InterTASS 2017) |

**Recomendación:** para un prototipo en español, **RoBERTuito** ofrece el mejor equilibrio
precisión/recursos. Para uso comercial o multilingüe, considerar **DistilBERT** (eficiencia +
Apache-2.0) o **XLM-RoBERTa** (robustez). El detalle está en
[`docs/Analisis_Comparativo_Modelos.docx`](docs/Analisis_Comparativo_Modelos.docx).

## 2. Estructura del repositorio

```
analisis-sentimiento-es-huggingface/
├── README.md                  # Este archivo
├── requirements.txt           # Dependencias
├── LICENSE                    # MIT (código y dataset propios)
├── data/
│   ├── dataset_sentimiento_es.csv   # Dataset de evaluación (120 ejemplos)
│   └── README_dataset.md            # Origen, diccionario de datos y limitaciones
├── notebooks/
│   └── analisis_comparativo_sentimiento.ipynb   # Cuaderno principal de Colab
├── src/
│   ├── generar_dataset.py     # Genera el dataset de forma determinística
│   ├── utils_metricas.py      # Normalización de etiquetas y métricas
│   ├── evaluar_modelos.py     # Evaluación completa (versión script del notebook)
│   ├── construir_notebook.py  # Reconstruye el .ipynb
│   └── construir_reporte_docx.py  # Genera el reporte Word
├── results/                   # Tablas y figuras generadas (al ejecutar)
└── docs/
    └── Analisis_Comparativo_Modelos.docx   # Reporte técnico comparativo
```

## 3. Entorno de ejecución

- **Recomendado:** Google Colab con **GPU NVIDIA T4** (gratuita).
- **Python:** 3.10 o superior.
- **Librerías:** `transformers>=4.40`, `huggingface_hub>=0.23`, `torch>=2.1`,
  `sentencepiece`, `accelerate`, `scikit-learn`, `pandas`, `matplotlib` (ver `requirements.txt`).
- En Colab, `torch` ya viene preinstalado; el notebook instala el resto en su primera celda.

## 4. Pasos de ejecución

### Opción A — Google Colab (recomendada)

1. Abre el notebook con el botón **“Abrir en Colab”** de arriba (o súbelo a Colab).
2. Menú **Entorno de ejecución → Cambiar tipo de entorno de ejecución → T4 GPU**.
3. (Opcional) Añade tu token de Hugging Face como secreto `HF_TOKEN` (panel 🔑).
4. Menú **Entorno de ejecución → Ejecutar todo**. Tiempo aprox.: **3–6 min**.

### Opción B — Local (con GPU recomendado)

```bash
git clone https://github.com/agustingerardoja/analisis-sentimiento-es-huggingface.git
cd analisis-sentimiento-es-huggingface
pip install -r requirements.txt

# (Re)generar el dataset
python src/generar_dataset.py --salida data/dataset_sentimiento_es.csv

# Ejecutar la evaluación completa de los 3 modelos
python src/evaluar_modelos.py --datos data/dataset_sentimiento_es.csv --salida results/
```

## 5. Dataset

Corpus original de **120 reseñas en español**, balanceado (40 POS / 40 NEU / 40 NEG),
curado por el autor. Origen, estructura de campos y limitaciones en
[`data/README_dataset.md`](data/README_dataset.md). Es **determinístico**: se regenera
idéntico con `src/generar_dataset.py`.

## 6. Métricas y metodología

- **Inferencia:** `pipeline` de Transformers, por lotes (batch=16), truncamiento a 256 tokens.
- **Métricas:** accuracy y precision/recall/F1 **macro** (scikit-learn).
- **Latencia:** ms/muestra con batch=1, descartando una pasada de calentamiento.
- **Ajuste mínimo:** normalización de etiquetas heterogéneas a `{NEG, NEU, POS}` y
  preprocesamiento de menciones/URLs (convención de modelos de Twitter).

Los resultados (tabla y figuras) se guardan en `results/` al ejecutar.

## 7. Conclusiones

- **No hay un único “mejor” modelo:** depende del contexto (idioma, licencia, latencia).
- **Precisión en español:** RoBERTuito lidera; XLM-RoBERTa queda cerca con robustez multilingüe;
  el DistilBERT destilado rinde por debajo, pero es el **más rápido** (6 capas).
- **Eficiencia:** lo decisivo es la profundidad (nº de capas), no solo los parámetros.
- **Licencia:** solo DistilBERT (Apache-2.0) habilita uso comercial sin fricción.
- **Recomendado:** **RoBERTuito** para el prototipo académico en español; alternativas según
  despliegue (comercial → DistilBERT; multilingüe → XLM-RoBERTa).

## 8. Riesgos y umbrales

- Umbrales sugeridos: F1 macro ≥ 0.65; latencia ≤ 50 ms/muestra (interactivo).
- Riesgos: ironía/sarcasmo, desajuste de dominio (tweets vs. reseñas), ambigüedad de la clase
  NEU, licencia no comercial de RoBERTuito y posible despublicación de modelos de terceros
  (mitigación: fijar el *commit hash* del modelo en el Hub). Detalle en el reporte Word.

## 9. Referencias

- Pérez et al. (2021). *pysentimiento*. arXiv:2106.09462.
- Pérez et al. (2022). *RoBERTuito*. LREC 2022.
- Barbieri et al. (2022). *XLM-T*. LREC 2022 / arXiv:2104.12250.
- Fichas de modelo en Hugging Face Hub (ver tabla en §1).

## 10. Licencia

Código y dataset propios bajo **MIT** (ver [LICENSE](LICENSE)). Los modelos preentrenados
conservan sus respectivas licencias.

---

*Autor:* Gerardo Jardínez Álvarez · *Maestría* · Actividad: selección e implementación de
modelos preentrenados de Hugging Face.
