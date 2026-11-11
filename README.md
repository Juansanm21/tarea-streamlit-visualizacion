# Tablero de desempeño comercial

Tablero en Streamlit que resume las ventas, los productos, los clientes y las entregas de una empresa comercial entre 2024 y 2025.

**Ver el tablero:** https://desempeno-comercial.streamlit.app/

## Contenido

| Sección | Pregunta | Gráfico | Datos |
|---|---|---|---|
| Ventas y publicidad | ¿Las ventas crecen más que la inversión en publicidad? | Líneas (inicio = 100) | `01_ventas_mensuales.csv` |
| Productos | ¿Los productos más vendidos son los que más ganancia dejan? | Burbujas | `05_productos.csv` |
| Clientes | ¿Cómo compra cada tipo de cliente? | Radar | `03_clientes.csv` |
| Entregas | ¿Qué porcentaje de pedidos llega a tiempo según el medio de transporte? | Distribución acumulada | `04_entregas.csv` |

Al final se presentan las conclusiones con una recomendación por tema.

**Filtros:** periodo, categoría de producto, tipo de cliente, medio de entrega y plazo de entrega. Las cifras, los gráficos y los títulos se actualizan con cada selección.

## Estructura

```
tablero_desempeno_comercial.py   código del tablero
data/                            archivos CSV
assets/favicon.png               ícono de la pestaña
.streamlit/config.toml           tema de colores
requirements.txt                 librerías necesarias
```

## Ejecutar en local

```bash
pip install -r requirements.txt
streamlit run tablero_desempeno_comercial.py
```

## Datos

Los archivos son datos ficticios de práctica. Ingreso = precio × unidades; ganancia = ingreso × margen.

---

Juan Pablo Sánchez
