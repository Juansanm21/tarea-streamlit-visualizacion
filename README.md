# Crecer sin gastar más · Tarea Streamlit

Informe analítico de una sola página hecho en **Streamlit** para la materia *Herramientas de Visualización* (Maestría en Analítica).

Usa los cinco archivos de `datos_practica` (datos inventados entregados en clase) como cinco capítulos de una misma empresa ficticia, con un hilo conductor:

> Vendemos un 34 % más con apenas un 11 % más de publicidad. ¿Quién sostiene ese crecimiento?

| Capítulo | Archivo | Pregunta |
|---|---|---|
| 01 Crecimiento | `01_ventas_mensuales.csv` | ¿Cómo evolucionaron las ventas y qué pasó con la publicidad? |
| 02 Productos | `05_productos.csv` | ¿Qué producto deja más y cuál se vende más? |
| 03 Clientes | `03_clientes.csv` | ¿Hay grupos de clientes? ¿Cómo se relacionan compras y gasto? |
| 04 Ciudad y canal | `02_clientes_por_ciudad_canal.csv` | ¿Dónde están los clientes y por qué canal llegan? |
| 05 Entregas | `04_entregas.csv` | ¿Cuánto tardan las entregas y depende del medio de transporte? |

Cada gráfico tiene un título que afirma un hallazgo, y cada capítulo cierra con una frase de **límite** (lo que los datos no permiten concluir).

## Ejecutar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Estructura

```
app.py                 # la aplicación (todo el código está aquí)
data/                  # los cinco CSV de práctica
.streamlit/config.toml # tema claro
requirements.txt
```
