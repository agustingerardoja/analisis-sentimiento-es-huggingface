# Dataset de Evaluación — Análisis de Sentimiento en Español

Archivo: `dataset_sentimiento_es.csv`

## 1. Origen del dataset

Corpus **curado manualmente por los autores** del proyecto con fines académicos.
No se reutiliza ningún dataset con licencia restrictiva: las 120 frases son
originales y redactadas para este trabajo, inspiradas en el estilo de las
reseñas de productos, servicios y comentarios de redes sociales en español
(México / español neutro). Por ser contenido propio, el dataset puede
redistribuirse libremente junto con el repositorio.

El conjunto se genera de forma **determinística** mediante el script
`src/generar_dataset.py`; ejecutarlo siempre produce exactamente el mismo CSV
(mismos textos, mismos `id`, mismo orden), lo que garantiza la reproducibilidad.

> **Nota de diseño.** Los textos se redactaron sin acentos ortográficos para
> emular el registro informal de redes sociales —dominio para el que fueron
> entrenados RoBERTuito y el modelo de Cardiff NLP, donde es habitual omitir
> diacríticos—. Los modelos basados en *subword tokenization* son robustos a
> esta variación.

## 2. Estructura (diccionario de datos)

El archivo es un CSV codificado en **UTF-8**, con encabezado y separador coma.
Contiene 120 filas (sin contar el encabezado) y 6 columnas:

| Campo                 | Tipo     | Descripción                                                                 | Ejemplo |
|-----------------------|----------|-----------------------------------------------------------------------------|---------|
| `id`                  | texto    | Identificador único del ejemplo, formato `es-NNN`.                           | `es-001` |
| `texto`               | texto    | Opinión / reseña corta en español a clasificar.                             | `Me encanto este telefono! La bateria dura todo el dia...` |
| `etiqueta`            | categoría| Sentimiento de referencia (*gold label*). Valores: `POS`, `NEU`, `NEG`.     | `POS` |
| `dominio`             | categoría| Tema del comentario (electronica, restaurante, servicio, viajes, etc.).     | `electronica` |
| `longitud_caracteres` | entero   | Número de caracteres del campo `texto` (derivado).                          | `79` |
| `num_palabras`        | entero   | Número de palabras del campo `texto` (derivado).                            | `15` |

### Espacio de etiquetas

| Etiqueta | Significado | Nº de ejemplos |
|----------|-------------|----------------|
| `POS`    | Sentimiento positivo | 40 |
| `NEU`    | Sentimiento neutral / factual | 40 |
| `NEG`    | Sentimiento negativo | 40 |
| **Total**|             | **120** |

Dataset **perfectamente balanceado** (33.3 % por clase), de modo que el
*accuracy* y el *F1 macro* son directamente comparables sin sesgo de clase.

### Estadísticas descriptivas

- Longitud de `texto`: mínimo 47, máximo 95, promedio 62.2 caracteres.
- Dominios cubiertos: electronica, restaurante, compras, software, viajes,
  entretenimiento, ropa, servicio, educacion, hogar, salud, transporte.

## 3. Scripts reproducibles

| Script | Función |
|--------|---------|
| `src/generar_dataset.py` | Genera/regenera el CSV de forma determinística. |
| `src/evaluar_modelos.py` | Carga los 3 modelos, ejecuta inferencia sobre este CSV y calcula métricas + latencia (versión script del notebook). |
| `src/utils_metricas.py`  | Funciones auxiliares: normalización de etiquetas y cálculo de métricas. |

### Regenerar el dataset

```bash
python src/generar_dataset.py --salida data/dataset_sentimiento_es.csv
```

### Reproducir la evaluación completa (requiere GPU recomendado)

```bash
pip install -r requirements.txt
python src/evaluar_modelos.py --datos data/dataset_sentimiento_es.csv --salida results/
```

## 4. Limitaciones

- Tamaño reducido (120 ejemplos): adecuado como **conjunto de prueba** para
  comparar modelos preentrenados *zero-shot* (sin fine-tuning), pero insuficiente
  para entrenar o para conclusiones estadísticas definitivas. Para una evaluación
  más rigurosa se recomienda complementar con TASS 2020 o `mteb/amazon_reviews_multi`
  (subconjunto `es`).
- Etiquetas asignadas por los autores: aunque los casos se eligieron para ser
  poco ambiguos, la clase `NEU` es intrínsecamente la más difícil y subjetiva.
- Cobertura de dominios amplia pero no exhaustiva; no incluye ironía ni sarcasmo
  de forma deliberada (se evaluó como riesgo en el reporte).
