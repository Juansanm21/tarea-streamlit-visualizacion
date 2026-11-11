# Crecer sin gastar más · Tarea Streamlit

Informe analítico de una sola página hecho en **Streamlit** para la materia *Herramientas de Visualización* (Maestría en Analítica).

Informe de desempeño comercial en formato de tablero, construido con cuatro de los archivos de `datos_practica` (datos de práctica entregados en clase). Combina lectura guiada con filtros por periodo, categoría de producto, segmento de cliente y medio de entrega.

| Sección | Archivo | Gráfico |
|---|---|---|
| 01 Ventas y publicidad | `01_ventas_mensuales.csv` | Líneas con brecha sombreada (índice base 100) |
| 02 Rentabilidad por producto | `05_productos.csv` | Burbujas (unidades × margen, área = ganancia) |
| 03 Perfil de clientes | `03_clientes.csv` | Radar por segmento |
| 04 Entregas | `04_entregas.csv` | Distribución acumulada (% de pedidos entregados por hora) |

Cada sección presenta un hallazgo en el título y una limitación del análisis.

## Ejecutar localmente

```bash
pip install -r requirements.txt
streamlit run tablero_desempeno_comercial.py
```
