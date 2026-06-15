# results/

Esta carpeta almacena los **resultados generados** al ejecutar el notebook o el
script `src/evaluar_modelos.py`. Su contenido se crea automáticamente y, por eso,
está excluido del control de versiones (ver `.gitignore`), salvo este README.

Archivos que se generan aquí:

| Archivo | Descripción |
|---------|-------------|
| `tabla_resumen.csv` | Tabla comparativa con accuracy, precision, recall, F1 macro, latencia y throughput de los 3 modelos. |
| `resultados_detalle.json` | Métricas detalladas y matrices de confusión por modelo. |
| `fig_precision.png` | Gráfica de barras: F1 macro vs. accuracy por modelo. |
| `fig_tradeoff.png` | Dispersión latencia vs. F1 (trade-off eficiencia/precisión). |
| `fig_matrices_confusion.png` | Matrices de confusión de los 3 modelos. |

Para regenerarlos:

```bash
python src/evaluar_modelos.py --datos data/dataset_sentimiento_es.csv --salida results/
```

o ejecutando el cuaderno `notebooks/analisis_comparativo_sentimiento.ipynb` en Colab.
