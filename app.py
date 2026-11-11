"""
Tarea Streamlit · Herramientas de Visualización
================================================

Informe analítico de una sola página construido con los cinco archivos de
`datos_practica` (datos inventados, entregados en clase). Los cinco archivos
no comparten llave, así que no se cruzan entre sí: se leen como cinco capítulos
de la misma empresa ficticia, unidos por una pregunta:

    "Vendemos más con casi la misma publicidad. ¿De dónde sale ese
     crecimiento y qué podría frenarlo?"

Capítulos
    1. Crecimiento .... 01_ventas_mensuales.csv
    2. Productos ...... 05_productos.csv
    3. Clientes ....... 03_clientes.csv
    4. Ciudad y canal . 02_clientes_por_ciudad_canal.csv
    5. Entregas ....... 04_entregas.csv

Reglas que sigue cada gráfico (reto del PDF de la clase)
    - El título afirma un hallazgo que se puede negar, no nombra un tema.
    - Cada gráfico cierra con una frase de LÍMITE: lo que NO se puede concluir.
    - Se evitan las trampas señaladas: nada de doble eje (se usa un índice
      base 100 o paneles separados), ingreso = precio × unidades, barras
      ordenadas, mismos bins y mismo eje X al comparar grupos.

Ejecutar:  streamlit run app.py
"""

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

# ──────────────────────────────────────────────────────────────────────────────
# 0. Configuración, paleta y estilo
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Crecer sin gastar más · Informe",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

DATA = Path(__file__).parent / "data"

# Paleta: tinta + grises recesivos + tres tonos categóricos validados
# (azul, naranja, aguamarina: los tres primeros de una paleta probada para
# daltonismo). El azul es el color de "lo que importa"; el gris es contexto.
INK = "#1C1B19"
INK_2 = "#55534E"
MUTED = "#8C8A83"
GRID = "#E6E2D8"
CONTEXT = "#C9C5BA"
BG = "#FAF8F3"
AZUL = "#2a78d6"
NARANJA = "#eb6834"
AQUA = "#1baf7a"
SECUENCIAL = ["#EEF4FC", "#C6DBF5", "#8DB8EA", "#4F8FDD", "#2a78d6", "#1B4F8F"]

FONT = "Inter, 'Segoe UI', sans-serif"
SERIF = "Fraunces, Georgia, serif"
PLOT_CONFIG = {"displayModeBar": False, "locale": "es"}

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,650&family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"], .stMarkdown, p, li, label { font-family: 'Inter', 'Segoe UI', sans-serif; }
[data-testid="stSidebar"], [data-testid="collapsedControl"], header[data-testid="stHeader"] { display: none; }
.block-container { max-width: 1120px; padding-top: 2.2rem; padding-bottom: 4rem; }

/* Portada */
.kicker { font-size: .78rem; letter-spacing: .14em; text-transform: uppercase; color: #2a78d6; font-weight: 600; }
.hero-title { font-family: 'Fraunces', Georgia, serif; font-weight: 650; font-size: clamp(2rem, 4.4vw, 3.3rem);
              line-height: 1.08; color: #1C1B19; margin: .35rem 0 .8rem 0; letter-spacing: -.01em; }
.hero-title em { font-style: normal; color: #2a78d6; }
.hero-sub { font-size: 1.12rem; color: #55534E; max-width: 760px; line-height: 1.55; }

/* Tarjetas de cifras */
.kpis { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 14px; margin: 1.8rem 0 1rem 0; }
.kpi { background: #FFFFFF; border: 1px solid #E6E2D8; border-radius: 14px; padding: 16px 18px; }
.kpi .lab { font-size: .78rem; color: #8C8A83; text-transform: uppercase; letter-spacing: .08em; }
.kpi .val { font-family: 'Fraunces', Georgia, serif; font-size: 2.05rem; font-weight: 650; color: #1C1B19; line-height: 1.1; margin-top: 4px; white-space: nowrap; }
.kpi .ctx { font-size: .86rem; color: #55534E; margin-top: 4px; }
.kpi .up { color: #1a7f55; font-weight: 600; }
@media (max-width: 760px) { .kpis { grid-template-columns: repeat(2, minmax(0, 1fr)); } }

/* Índice de capítulos */
.toc { display: flex; flex-wrap: wrap; gap: 8px; margin: .6rem 0 2.2rem 0; }
.toc a { text-decoration: none; font-size: .86rem; color: #1C1B19; background: #F1EEE6; border-radius: 999px; padding: 6px 14px; }
.toc a:hover { background: #2a78d6; color: #fff; }
.toc a b { color: #2a78d6; margin-right: 6px; }
.toc a:hover b { color: #fff; }

/* Capítulos */
.chapter { border-top: 1px solid #E6E2D8; margin-top: 3.2rem; padding-top: 2rem; }
.ch-num { font-family: 'Fraunces', Georgia, serif; font-size: .95rem; color: #2a78d6; font-weight: 650; }
.ch-q { font-size: .95rem; color: #8C8A83; margin-left: 10px; }
.claim { font-family: 'Fraunces', Georgia, serif; font-weight: 650; font-size: clamp(1.45rem, 2.6vw, 2rem);
         line-height: 1.2; color: #1C1B19; margin: .4rem 0 .5rem 0; }
.lead { color: #55534E; font-size: 1.02rem; line-height: 1.6; max-width: 820px; }
.lead b { color: #1C1B19; }
.chart-t { font-weight: 600; color: #1C1B19; font-size: 1rem; margin: 1.1rem 0 0 0; }
.chart-s { color: #8C8A83; font-size: .86rem; margin: 2px 0 0 0; }
.limit { border-left: 3px solid #eb6834; background: #FFF6F1; padding: 10px 14px; border-radius: 0 10px 10px 0;
         color: #55534E; font-size: .9rem; margin: .4rem 0 0 0; }
.limit b { color: #b4461a; }

/* Cierre */
.close-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; margin-top: 1rem; }
.close-card { background: #fff; border: 1px solid #E6E2D8; border-radius: 14px; padding: 18px; }
.close-card h4 { font-family: 'Fraunces', Georgia, serif; font-size: 1.1rem; margin: 0 0 .4rem 0; color: #1C1B19; }
.close-card p { color: #55534E; font-size: .92rem; line-height: 1.5; margin: 0; }
@media (max-width: 760px) { .close-grid { grid-template-columns: 1fr; } }
.foot { color: #8C8A83; font-size: .82rem; margin-top: 3rem; border-top: 1px solid #E6E2D8; padding-top: 1rem; }

/* Controles */
div[data-testid="stSegmentedControl"] button p { font-size: .85rem; }
</style>
""",
    unsafe_allow_html=True,
)


# ──────────────────────────────────────────────────────────────────────────────
# Utilidades
# ──────────────────────────────────────────────────────────────────────────────
def num(x: float, dec: int = 0) -> str:
    """Formato colombiano: punto de miles, coma decimal."""
    s = f"{x:,.{dec}f}"
    return s.replace(",", "§").replace(".", ",").replace("§", ".")


def pct(x: float, dec: int = 0) -> str:
    return f"{num(x * 100, dec)} %"  # espacio que no se rompe entre número y %


def html(s: str) -> None:
    st.markdown(s, unsafe_allow_html=True)


def chapter(anchor: str, n: str, pregunta: str, claim: str, lead: str) -> None:
    html(
        f"""<div class="chapter" id="{anchor}">
<span class="ch-num">{n}</span><span class="ch-q">{pregunta}</span>
<div class="claim">{claim}</div>
<p class="lead">{lead}</p></div>"""
    )


def chart_title(t: str, s: str = "") -> None:
    html(f'<p class="chart-t">{t}</p>' + (f'<p class="chart-s">{s}</p>' if s else ""))


def limit(t: str) -> None:
    html(f'<p class="limit"><b>Límite ·</b> {t}</p>')


def style(fig: go.Figure, height: int = 380, legend: bool = True) -> go.Figure:
    """Plantilla común: fondo limpio, grilla recesiva, una sola tipografía."""
    fig.update_layout(
        height=height,
        margin=dict(l=8, r=16, t=16, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT, size=13, color=INK_2),
        hoverlabel=dict(bgcolor="white", bordercolor=GRID, font=dict(family=FONT, size=13, color=INK)),
        showlegend=legend,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, title=None,
                    font=dict(size=12, color=INK_2)),
    )
    fig.update_xaxes(showgrid=False, linecolor=CONTEXT, tickcolor=CONTEXT, ticks="outside",
                     title_font=dict(size=12, color=MUTED), zeroline=False)
    fig.update_yaxes(gridcolor=GRID, zeroline=False, linecolor="rgba(0,0,0,0)",
                     title_font=dict(size=12, color=MUTED))
    return fig


def show(fig: go.Figure) -> None:
    st.plotly_chart(fig, use_container_width=True, config=PLOT_CONFIG)


# ──────────────────────────────────────────────────────────────────────────────
# 1. Datos (los CSV ya vienen limpios; solo se derivan métricas)
# ──────────────────────────────────────────────────────────────────────────────
@st.cache_data
def cargar():
    leer = lambda f: pd.read_csv(DATA / f, encoding="utf-8-sig")
    ventas = leer("01_ventas_mensuales.csv")
    canal = leer("02_clientes_por_ciudad_canal.csv")
    clientes = leer("03_clientes.csv")
    entregas = leer("04_entregas.csv")
    productos = leer("05_productos.csv")

    ventas["fecha"] = pd.to_datetime(ventas["fecha"])
    ventas["anio"] = ventas["fecha"].dt.year
    base_v, base_p = ventas.loc[0, "ventas_millones"], ventas.loc[0, "publicidad_millones"]
    ventas["idx_ventas"] = ventas["ventas_millones"] / base_v * 100
    ventas["idx_pub"] = ventas["publicidad_millones"] / base_p * 100
    ventas["rendimiento"] = ventas["ventas_millones"] / ventas["publicidad_millones"]

    # Trampa del archivo 05: unidades no es ingreso. Ingreso = precio × unidades.
    productos["ingreso"] = productos["precio"] * productos["unidades"]
    productos["ganancia"] = productos["ingreso"] * productos["margen_pct"] / 100

    clientes["valor"] = clientes["compras"] * clientes["gasto_medio"]

    canal["pct_ciudad"] = canal["clientes"] / canal.groupby("ciudad")["clientes"].transform("sum")
    return ventas, canal, clientes, entregas, productos


ventas, canal, clientes, entregas, productos = cargar()

# Cifras que alimentan los titulares (se calculan, no se escriben a mano)
anual = ventas.groupby("anio")[["ventas_millones", "publicidad_millones"]].sum()
crec_v = anual.loc[2025, "ventas_millones"] / anual.loc[2024, "ventas_millones"] - 1
crec_p = anual.loc[2025, "publicidad_millones"] / anual.loc[2024, "publicidad_millones"] - 1
rend = ventas.groupby("anio").apply(lambda d: d["ventas_millones"].sum() / d["publicidad_millones"].sum())
tot_clientes = canal["clientes"].sum()
por_ciudad = canal.groupby("ciudad")["clientes"].sum().sort_values(ascending=False)
share_bog = por_ciudad.iloc[0] / tot_clientes
med_tipo = entregas.groupby("tipo")["tiempo_horas"].median()

# ──────────────────────────────────────────────────────────────────────────────
# PORTADA
# ──────────────────────────────────────────────────────────────────────────────
html(
    f"""
<div class="kicker">Informe analítico · Empresa de tecnología, muebles y papelería · 2024–2025</div>
<div class="hero-title">Vendemos un <em>{pct(crec_v)} más</em> con apenas un {pct(crec_p)} más de publicidad.<br>
¿Quién sostiene ese crecimiento?</div>
<p class="hero-sub">Cinco preguntas, en orden: cuánto crecimos, qué vendemos, quién nos compra,
dónde están y cómo les llega el pedido. Cada gráfico responde una de ellas, y cada respuesta
termina con su límite: lo que estos datos <b>no</b> permiten afirmar.</p>

<div class="kpis">
  <div class="kpi"><div class="lab">Ventas 2025</div><div class="val">${num(anual.loc[2025, 'ventas_millones'])} M</div>
       <div class="ctx"><span class="up">▲ {pct(crec_v)}</span> frente a 2024</div></div>
  <div class="kpi"><div class="lab">Ventas por $1 de publicidad</div><div class="val">${num(rend.loc[2025], 1)}</div>
       <div class="ctx">era ${num(rend.loc[2024], 1)} en 2024</div></div>
  <div class="kpi"><div class="lab">Clientes</div><div class="val">{num(tot_clientes)}</div>
       <div class="ctx">{pct(share_bog)} están en Bogotá</div></div>
  <div class="kpi"><div class="lab">Entrega más rápida</div><div class="val">{num(med_tipo['Moto'], 1)} h</div>
       <div class="ctx">en moto; la bicicleta tarda {num(med_tipo['Bicicleta'], 1)} h</div></div>
</div>

<div class="toc">
  <a href="#crecimiento"><b>01</b>Crecimiento</a>
  <a href="#productos"><b>02</b>Productos</a>
  <a href="#clientes"><b>03</b>Clientes</a>
  <a href="#canales"><b>04</b>Ciudad y canal</a>
  <a href="#entregas"><b>05</b>Entregas</a>
  <a href="#cierre"><b>→</b>Conclusiones</a>
</div>
"""
)

# ──────────────────────────────────────────────────────────────────────────────
# CAPÍTULO 1 · CRECIMIENTO
# ──────────────────────────────────────────────────────────────────────────────
ult = ventas.iloc[-1]
chapter(
    "crecimiento", "01", "¿Cómo evolucionaron las ventas y qué pasó con la publicidad?",
    f"Las ventas casi se duplicaron (+{num(ult.idx_ventas - 100)} %); la publicidad apenas se movió (+{num(ult.idx_pub - 100)} %)",
    f"De enero de 2024 a diciembre de 2025 las ventas pasaron de <b>${num(ventas.ventas_millones.iloc[0])} M</b> a "
    f"<b>${num(ult.ventas_millones)} M</b> al mes. Para compararlas con la publicidad, que se mueve en otra escala, "
    "las dos series se llevan a un <b>índice con base enero 2024 = 100</b>: así ambas comparten un solo eje y "
    "se ve quién creció más, sin el truco del doble eje.",
)

vista = st.segmented_control(
    "Vista", ["Índice (ene 2024 = 100)", "Valores en millones"], default="Índice (ene 2024 = 100)",
    key="vista_ventas", label_visibility="collapsed",
)

if vista == "Valores en millones":
    chart_title("Ventas y publicidad mensuales, en millones de pesos",
                "Dos paneles con su propia escala: se comparan las formas, no las alturas")
    fig = make_subplots(rows=1, cols=2, horizontal_spacing=0.08,
                        subplot_titles=("Ventas (millones $)", "Publicidad (millones $)"))
    fig.add_trace(go.Scatter(x=ventas.mes, y=ventas.ventas_millones, mode="lines+markers", name="Ventas",
                             line=dict(color=AZUL, width=2.5), marker=dict(size=6),
                             hovertemplate="%{x}<br><b>$%{y:.0f} M</b> en ventas<extra></extra>"), 1, 1)
    fig.add_trace(go.Scatter(x=ventas.mes, y=ventas.publicidad_millones, mode="lines+markers", name="Publicidad",
                             line=dict(color=NARANJA, width=2.5), marker=dict(size=6),
                             hovertemplate="%{x}<br><b>$%{y:.1f} M</b> en publicidad<extra></extra>"), 1, 2)
    fig.update_yaxes(rangemode="tozero")
    fig.update_xaxes(tickvals=list(ventas.mes[::3]), tickangle=0)
    fig.update_annotations(font=dict(size=13, color=INK_2), x=0, xanchor="left", selector=dict(text="Ventas (millones $)"))
    fig.update_annotations(font=dict(size=13, color=INK_2), selector=dict(text="Publicidad (millones $)"))
    style(fig, 380, legend=False)
else:
    chart_title("Índice de ventas y de publicidad (enero 2024 = 100)",
                "Un valor de 180 significa 80 % por encima de enero de 2024")
    fig = go.Figure()
    fig.add_hline(y=100, line=dict(color=CONTEXT, width=1, dash="dot"))
    fig.add_trace(go.Scatter(
        x=ventas.mes, y=ventas.idx_pub, name="Publicidad", mode="lines",
        line=dict(color=NARANJA, width=2.5), customdata=ventas.publicidad_millones,
        hovertemplate="Publicidad: <b>%{y:.0f}</b> (%{customdata:.1f} M)<extra></extra>"))
    fig.add_trace(go.Scatter(
        x=ventas.mes, y=ventas.idx_ventas, name="Ventas", mode="lines",
        line=dict(color=AZUL, width=3), customdata=ventas.ventas_millones,
        fill="tonexty", fillcolor="rgba(42,120,214,0.08)",
        hovertemplate="Ventas: <b>%{y:.0f}</b> (%{customdata:.0f} M)<extra></extra>"))
    for y, txt, col in [(ult.idx_ventas, f"Ventas {num(ult.idx_ventas)}", AZUL),
                        (ult.idx_pub, f"Publicidad {num(ult.idx_pub)}", NARANJA)]:
        fig.add_annotation(x=ult.mes, y=y, text=f"<b>{txt}</b>", showarrow=False, xanchor="left",
                           xshift=8, font=dict(color=col, size=13))
    fig.add_annotation(x="mar 2025", y=128, text="La brecha que se abre<br>es el crecimiento<br>que no explica la publicidad",
                       showarrow=False, font=dict(size=12, color=INK_2), align="center")
    style(fig, 400)
    fig.update_layout(hovermode="x unified", margin=dict(r=110))
    fig.update_xaxes(tickvals=list(ventas.mes[::3]),
                     ticktext=[m.replace(" ", "<br>") for m in ventas.mes[::3]])
    fig.update_yaxes(title="Índice (ene 2024 = 100)", range=[80, 195])
show(fig)

r_vp = ventas["ventas_millones"].corr(ventas["publicidad_millones"])
limit(
    f"ventas y publicidad tienen una correlación de {num(r_vp, 2)}, pero ambas suben con el tiempo: "
    "esa correlación no prueba que la publicidad cause las ventas. Tampoco sabemos si los precios cambiaron "
    "(las ventas están en pesos corrientes) ni qué otras acciones comerciales hubo."
)

# ──────────────────────────────────────────────────────────────────────────────
# CAPÍTULO 2 · PRODUCTOS
# ──────────────────────────────────────────────────────────────────────────────
top_u = productos.loc[productos.unidades.idxmax()]
top_g = productos.loc[productos.ganancia.idxmax()]
rank_u_g = int(productos.ganancia.rank(ascending=False)[productos.unidades.idxmax()])
chapter(
    "productos", "02", "¿Qué producto deja más y cuál se vende más?",
    f"El {top_u.producto.lower()} es el que más se vende; el {top_g.producto.lower()}, el que más deja",
    f"El <b>{top_u.producto.lower()}</b> mueve {num(top_u.unidades)} unidades, pero a ${num(top_u.precio)} cada una "
    f"queda en el puesto {rank_u_g} de 12 en ganancia. Contar unidades engaña: lo que entra a caja es "
    "<b>precio × unidades</b> (ingreso) y lo que queda es <b>ingreso × margen</b> (ganancia). "
    "Cambia la métrica y mira cómo se reordena el ranking.",
)

CAT_COL = {"Tecnología": AZUL, "Muebles": NARANJA, "Papelería": AQUA}
c1, c2 = st.columns([1.35, 1], gap="large")
with c1:
    metrica = st.segmented_control("Métrica", ["Ganancia", "Ingreso", "Unidades"], default="Ganancia",
                                   key="metrica_prod", label_visibility="collapsed") or "Ganancia"
    col_m = {"Ganancia": "ganancia", "Ingreso": "ingreso", "Unidades": "unidades"}[metrica]
    sub = {"ganancia": "Ganancia = precio × unidades × margen",
           "ingreso": "Ingreso = precio × unidades",
           "unidades": "Unidades vendidas en el periodo"}[col_m]
    chart_title(f"Productos ordenados por {metrica.lower()}", sub)
    d = productos.sort_values(col_m)
    fig = go.Figure()
    for cat, g in d.groupby("categoria", sort=False):
        fig.add_trace(go.Bar(
            y=g.producto, x=g[col_m], orientation="h", name=cat, marker_color=CAT_COL[cat],
            text=[("$" if col_m != "unidades" else "") + num(v) for v in g[col_m]], textposition="outside",
            textfont=dict(color=INK_2, size=12), cliponaxis=False,
            customdata=np.stack([g.precio, g.unidades, g.margen_pct, g.ingreso, g.ganancia], axis=1),
            hovertemplate="<b>%{y}</b><br>Precio $%{customdata[0]:,.0f} · %{customdata[1]:,.0f} unidades"
                          "<br>Ingreso $%{customdata[3]:,.0f} · margen %{customdata[2]} %"
                          "<br>Ganancia <b>$%{customdata[4]:,.0f}</b><extra></extra>"))
    style(fig, 440)
    fig.update_layout(barmode="overlay", bargap=0.28)
    fig.update_yaxes(categoryorder="array", categoryarray=list(d.producto), gridcolor="rgba(0,0,0,0)")
    fig.update_xaxes(visible=False, range=[0, d[col_m].max() * 1.18])
    show(fig)

with c2:
    cat = productos.groupby("categoria")[["ingreso", "ganancia"]].sum()
    cat_s = cat / cat.sum()
    cat_s = cat_s.sort_values("ganancia")
    chart_title("Papelería pesa poco en ingreso y mucho en ganancia",
                "Participación de cada categoría en el total")
    fig = go.Figure()
    for c, row in cat_s.iterrows():
        fig.add_trace(go.Scatter(x=[row.ingreso, row.ganancia], y=[c, c], mode="lines",
                                 line=dict(color=CONTEXT, width=3), showlegend=False, hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=cat_s.ingreso, y=cat_s.index, mode="markers+text", name="% del ingreso",
                             marker=dict(size=14, color="white", line=dict(color=INK_2, width=2)),
                             text=[pct(v) for v in cat_s.ingreso], textposition="bottom center",
                             textfont=dict(size=11, color=MUTED),
                             hovertemplate="%{y}: %{x:.0%} del ingreso<extra></extra>"))
    fig.add_trace(go.Scatter(x=cat_s.ganancia, y=cat_s.index, mode="markers+text", name="% de la ganancia",
                             marker=dict(size=16, color=[CAT_COL[c] for c in cat_s.index], line=dict(color="white", width=2)),
                             text=[pct(v) for v in cat_s.ganancia], textposition="top center",
                             textfont=dict(size=12, color=INK),
                             hovertemplate="%{y}: %{x:.0%} de la ganancia<extra></extra>"))
    style(fig, 440)
    fig.update_xaxes(tickformat=".0%", range=[0.1, 0.56], showgrid=True, gridcolor=GRID, title="Participación")
    fig.update_yaxes(gridcolor="rgba(0,0,0,0)")
    show(fig)

limit(
    "no hay fecha ni costos fijos: el margen es el que reporta el archivo y la ganancia es una estimación "
    "(ingreso × margen). Tampoco sabemos si estos 12 productos son todo el catálogo ni si el periodo coincide "
    "con el de las ventas mensuales."
)

# ──────────────────────────────────────────────────────────────────────────────
# CAPÍTULO 3 · CLIENTES
# ──────────────────────────────────────────────────────────────────────────────
SEG_COL = {"Frecuente": AZUL, "Regular": NARANJA, "Ocasional": AQUA}
SEG_ORD = ["Frecuente", "Regular", "Ocasional"]
PLURAL = {"Frecuente": "frecuentes", "Regular": "regulares", "Ocasional": "ocasionales"}
r_glob = clientes["compras"].corr(clientes["gasto_medio"])
r_seg = clientes.groupby("segmento").apply(lambda d: d["compras"].corr(d["gasto_medio"]))
val_seg = clientes.groupby("segmento")["valor"].sum()
top_seg = val_seg.idxmax()
ventaja = val_seg.max() / val_seg.drop(top_seg).mean() - 1

chapter(
    "clientes", "03", "¿Hay grupos de clientes? ¿Cómo se relacionan compras y gasto?",
    "«Quien más compra, menos gasta» es un espejismo: lo fabrican los segmentos",
    f"Mirando a los 180 clientes juntos, la correlación entre número de compras y gasto medio es "
    f"<b>{num(r_glob, 2)}</b>: fuerte y negativa. Pero dentro de cada segmento casi desaparece "
    f"(entre {num(r_seg.min(), 2)} y {num(r_seg.max(), 2)}). La relación no está en los clientes, "
    "está en cómo están agrupados: son tres perfiles distintos, no una regla general. "
    "Cambia la vista para verlo.",
)

c1, c2 = st.columns([1.35, 1], gap="large")
with c1:
    modo = st.segmented_control("Vista clientes", ["Todos juntos", "Por segmento"], default="Todos juntos",
                                key="vista_cli", label_visibility="collapsed") or "Todos juntos"
    rng = np.random.default_rng(7)
    jit = clientes["compras"] + rng.uniform(-0.3, 0.3, len(clientes))  # temblor: las compras son enteras
    fig = go.Figure()
    xs = np.linspace(clientes.compras.min(), clientes.compras.max(), 50)
    if modo == "Todos juntos":
        chart_title(f"Una sola nube: correlación de {num(r_glob, 2)}",
                    "Cada punto es un cliente · gasto medio por compra")
        fig.add_trace(go.Scatter(x=jit, y=clientes.gasto_medio, mode="markers", name="Clientes",
                                 marker=dict(size=9, color=MUTED, opacity=0.55, line=dict(color="white", width=1)),
                                 customdata=clientes[["cliente", "segmento", "compras"]],
                                 hovertemplate="%{customdata[0]} · %{customdata[1]}<br>%{customdata[2]} compras · "
                                               "$%{y:.2f} por compra<extra></extra>"))
        b = np.polyfit(clientes.compras, clientes.gasto_medio, 1)
        fig.add_trace(go.Scatter(x=xs, y=np.polyval(b, xs), mode="lines", name="Tendencia global",
                                 line=dict(color=INK, width=2.5), hoverinfo="skip"))
    else:
        chart_title("Tres nubes planas: dentro de cada grupo no hay relación",
                    "Cada punto es un cliente · línea = tendencia dentro del segmento")
        for s in SEG_ORD:
            g = clientes[clientes.segmento == s]
            fig.add_trace(go.Scatter(x=jit[g.index], y=g.gasto_medio, mode="markers", name=f"{s} (r = {num(r_seg[s], 2)})",
                                     legendgroup=s, marker=dict(size=9, color=SEG_COL[s], opacity=0.6, line=dict(color="white", width=1)),
                                     customdata=g[["cliente", "segmento", "compras"]],
                                     hovertemplate="%{customdata[0]} · %{customdata[1]}<br>%{customdata[2]} compras · "
                                                   "$%{y:.2f} por compra<extra></extra>"))
            b = np.polyfit(g.compras, g.gasto_medio, 1)
            xx = np.linspace(g.compras.min(), g.compras.max(), 20)
            fig.add_trace(go.Scatter(x=xx, y=np.polyval(b, xx), mode="lines", legendgroup=s, showlegend=False,
                                     line=dict(color=SEG_COL[s], width=3), hoverinfo="skip"))
    style(fig, 430)
    fig.update_xaxes(title="Número de compras", range=[0, clientes.compras.max() + 1.5])
    fig.update_yaxes(title="Gasto medio por compra ($)", rangemode="tozero")
    show(fig)

with c2:
    chart_title(f"Los {PLURAL[top_seg]} dejan {pct(ventaja)} más que los otros segmentos",
                "Valor total por cliente = compras × gasto medio · cada punto es un cliente")
    fig = go.Figure()
    for s in SEG_ORD:
        g = clientes[clientes.segmento == s]
        fig.add_trace(go.Box(y=g.valor, name=s, marker_color=SEG_COL[s], boxpoints="all", jitter=0.45,
                             pointpos=0, marker=dict(size=5, opacity=0.45), line=dict(width=2),
                             fillcolor="rgba(255,255,255,0)", boxmean=False,
                             hovertemplate=f"<b>{s}</b><br>Valor: $%{{y:,.0f}}<extra></extra>"))
        fig.add_annotation(x=s, y=g.valor.max(), yshift=18, showarrow=False,
                           text=f"<b>Total ${num(val_seg[s] / 1000, 1)} mil</b>", font=dict(size=12, color=INK))
    style(fig, 430, legend=False)
    fig.update_yaxes(title="Valor por cliente ($)", rangemode="tozero")
    show(fig)

edad_min = int(clientes.edad.min())
limit(
    "no sabemos con qué criterio se asignó el segmento: si se definió a partir de las compras, la paradoja "
    f"es en parte circular. Además hay clientes de {edad_min} años, lo que sugiere que la edad no es de quien "
    "paga o que hay errores de captura. Los 60 clientes por segmento son una muestra balanceada, no la "
    "proporción real de la base."
)

# ──────────────────────────────────────────────────────────────────────────────
# CAPÍTULO 4 · CIUDAD Y CANAL
# ──────────────────────────────────────────────────────────────────────────────
app_lider = canal.loc[canal.groupby("ciudad")["clientes"].idxmax()].set_index("ciudad")["canal"]
excep = [c for c, k in app_lider.items() if k != "App"]
tel = canal[canal.canal == "Teléfono"]["clientes"].sum() / tot_clientes
chapter(
    "canales", "04", "¿Dónde están los clientes y por qué canal llegan?",
    f"Bogotá concentra {num(share_bog * 10)} de cada 10 clientes; la App lidera en todas las ciudades"
    + (f" menos {', '.join(excep)}" if excep else ""),
    f"Los {num(tot_clientes)} clientes se reparten de forma muy desigual: Bogotá suma "
    f"<b>{num(por_ciudad.iloc[0])}</b>, más que Cali, Barranquilla y Cartagena juntas. Para comparar el "
    "<b>canal</b> entre ciudades de tamaños tan distintos, el mapa de calor muestra el porcentaje "
    f"<b>dentro de cada ciudad</b>, no el conteo. El teléfono ya es marginal en todas partes ({pct(tel)}).",
)

c1, c2 = st.columns([1, 1.25], gap="large")
with c1:
    chart_title("Clientes por ciudad", "Total de clientes, de mayor a menor")
    d = por_ciudad.sort_values()
    fig = go.Figure(go.Bar(
        y=d.index, x=d.values, orientation="h",
        marker_color=[AZUL if c == por_ciudad.index[0] else CONTEXT for c in d.index],
        text=[f"{num(v)}  ·  {pct(v / tot_clientes)}" for v in d.values], textposition="outside",
        textfont=dict(color=INK_2, size=12), cliponaxis=False,
        hovertemplate="<b>%{y}</b><br>%{x:,} clientes<extra></extra>"))
    style(fig, 360, legend=False)
    fig.update_xaxes(visible=False, range=[0, d.max() * 1.35])
    fig.update_yaxes(gridcolor="rgba(0,0,0,0)")
    show(fig)

with c2:
    chart_title("Mezcla de canales dentro de cada ciudad", "Porcentaje de los clientes de la ciudad · cada fila suma 100 %")
    ord_canal = canal.groupby("canal")["clientes"].sum().sort_values(ascending=False).index.tolist()
    m = canal.pivot(index="ciudad", columns="canal", values="pct_ciudad").loc[por_ciudad.index, ord_canal]
    n = canal.pivot(index="ciudad", columns="canal", values="clientes").loc[por_ciudad.index, ord_canal]
    txt = [[f"<b>{pct(v)}</b>" if v == row.max() else pct(v) for v in row] for _, row in m.iterrows()]
    fig = go.Figure(go.Heatmap(
        z=m.values, x=m.columns, y=m.index, text=txt, texttemplate="%{text}",
        textfont=dict(size=13), colorscale=[[i / 5, c] for i, c in enumerate(SECUENCIAL)],
        zmin=0, zmax=0.45, xgap=3, ygap=3, customdata=n.values,
        colorbar=dict(title=dict(text="% ciudad", font=dict(size=11)), tickformat=".0%", thickness=10, len=0.8),
        hovertemplate="<b>%{y} · %{x}</b><br>%{z:.0%} de la ciudad<br>%{customdata:,} clientes<extra></extra>"))
    style(fig, 360, legend=False)
    fig.update_yaxes(autorange="reversed", gridcolor="rgba(0,0,0,0)")
    fig.update_xaxes(side="top", ticks="", linecolor="rgba(0,0,0,0)")
    show(fig)

limit(
    "contar clientes no es contar ventas: no sabemos cuánto compra cada canal ni cada ciudad. "
    "Un cliente podría usar varios canales, y el archivo no dice en qué fecha se tomó el conteo."
)

# ──────────────────────────────────────────────────────────────────────────────
# CAPÍTULO 5 · ENTREGAS
# ──────────────────────────────────────────────────────────────────────────────
TIP_COL = {"Moto": AZUL, "Carro": NARANJA, "Bicicleta": AQUA}
TIP_ORD = ["Moto", "Carro", "Bicicleta"]
r_td = entregas.groupby("tipo").apply(lambda d: d["tiempo_horas"].corr(d["distancia_km"]))
chapter(
    "entregas", "05", "¿Cuánto tardan las entregas y depende del medio de transporte?",
    f"La moto entrega en la mitad del tiempo que la bicicleta, y la distancia casi no cambia nada",
    f"Tiempo mediano: <b>moto {num(med_tipo['Moto'], 1)} h</b>, carro {num(med_tipo['Carro'], 1)} h y "
    f"bicicleta {num(med_tipo['Bicicleta'], 1)} h. La bicicleta además es la más <b>impredecible</b>: su cola "
    "llega a más de 9 horas. Si el crecimiento sigue, este es el cuello de botella. "
    "Mueve la promesa de entrega y mira qué medio la cumple.",
)

c1, c2 = st.columns([1.35, 1], gap="large")
with c1:
    chart_title("Distribución del tiempo de entrega por medio",
                "Mismo eje y mismos intervalos de media hora en los tres paneles · línea = mediana")
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.06)
    for i, t in enumerate(TIP_ORD, start=1):
        g = entregas[entregas.tipo == t]
        fig.add_trace(go.Histogram(x=g.tiempo_horas, xbins=dict(start=0, end=10, size=0.5), name=t,
                                   marker=dict(color=TIP_COL[t], line=dict(color=BG, width=2)),
                                   hovertemplate=f"<b>{t}</b><br>%{{x}} h: %{{y}} entregas<extra></extra>"), i, 1)
        fig.add_vline(x=g.tiempo_horas.median(), line=dict(color=INK, width=1.5, dash="dot"), row=i, col=1)
        fig.add_annotation(text=f"<b>{t}</b> · mediana {num(g.tiempo_horas.median(), 1)} h", x=9.9, xanchor="right",
                           y=1, yref=f"y{'' if i == 1 else i} domain", yanchor="top", showarrow=False,
                           font=dict(size=12, color=INK), row=i, col=1)
    style(fig, 440, legend=False)
    fig.update_xaxes(range=[0, 10], dtick=1)
    fig.update_xaxes(title="Horas", row=3, col=1)
    fig.update_yaxes(title=None, nticks=3)
    show(fig)

with c2:
    promesa = st.slider("Promesa de entrega al cliente (horas)", 1.0, 8.0, 3.0, 0.5, key="promesa")
    cumple = entregas.assign(ok=entregas.tiempo_horas <= promesa).groupby("tipo")["ok"].mean().reindex(TIP_ORD)
    chart_title(f"Entregas que llegan en {num(promesa, 1)} h o menos", "Porcentaje de entregas de cada medio")
    fig = go.Figure(go.Bar(
        x=cumple.index, y=cumple.values, marker_color=[TIP_COL[t] for t in cumple.index],
        text=[pct(v) for v in cumple.values], textposition="outside", textfont=dict(size=15, color=INK),
        cliponaxis=False, width=0.55,
        hovertemplate="<b>%{x}</b><br>%{y:.0%} cumple la promesa<extra></extra>"))
    style(fig, 360, legend=False)
    fig.update_yaxes(range=[0, 1.12], tickformat=".0%", dtick=0.25)
    show(fig)

chart_title("Tiempo frente a distancia: no hay pendiente",
            f"Correlación dentro de cada medio: moto {num(r_td['Moto'], 2)}, carro {num(r_td['Carro'], 2)}, "
            f"bicicleta {num(r_td['Bicicleta'], 2)}")
fig = make_subplots(rows=1, cols=3, shared_yaxes=True, horizontal_spacing=0.03, subplot_titles=TIP_ORD)
for i, t in enumerate(TIP_ORD, start=1):
    g = entregas[entregas.tipo == t]
    fig.add_trace(go.Scatter(x=g.distancia_km, y=g.tiempo_horas, mode="markers", name=t,
                             marker=dict(size=8, color=TIP_COL[t], opacity=0.6, line=dict(color="white", width=1)),
                             hovertemplate=f"<b>{t}</b><br>%{{x}} km · %{{y}} h<extra></extra>"), 1, i)
style(fig, 280, legend=False)
fig.update_xaxes(range=[0, 17.5], title="Distancia (km)")
fig.update_yaxes(title="Horas", col=1)
fig.update_annotations(font=dict(size=13, color=INK))
show(fig)

limit(
    "el medio de transporte no se asignó al azar: la bicicleta recorre distancias medianas mayores "
    f"({num(entregas[entregas.tipo == 'Bicicleta'].distancia_km.median(), 1)} km frente a "
    f"{num(entregas[entregas.tipo == 'Moto'].distancia_km.median(), 1)} km en moto), así que no se puede decir que "
    "cambiar bicicletas por motos reduzca el tiempo a la mitad. Que la distancia no pese sugiere que el tiempo "
    "incluye esperas (alistamiento, despacho) que el archivo no separa."
)

# ──────────────────────────────────────────────────────────────────────────────
# CIERRE
# ──────────────────────────────────────────────────────────────────────────────
html(
    f"""
<div class="chapter" id="cierre">
<span class="ch-num">→</span><span class="ch-q">Conclusiones</span>
<div class="claim">Crecemos con eficiencia; la ganancia y la entrega son donde hay que mirar</div>
</div>
<div class="close-grid">
  <div class="close-card"><h4>Qué sabemos</h4>
    <p>Las ventas crecieron {pct(crec_v)} con {pct(crec_p)} más de publicidad. La ganancia se concentra en
    tecnología y papelería, no en lo que más unidades mueve. Bogotá y la App son el centro del negocio.</p></div>
  <div class="close-card"><h4>Qué haríamos</h4>
    <p>Medir por ganancia, no por unidades. Cuidar a los clientes regulares, que son los que más valor dejan.
    Revisar la entrega en bicicleta antes de que el crecimiento la sature.</p></div>
  <div class="close-card"><h4>Qué no podemos afirmar</h4>
    <p>Que la publicidad cause las ventas, que los segmentos sean naturales o que cambiar de vehículo reduzca
    el tiempo. Los cinco archivos no se cruzan entre sí: son cinco miradas, no un solo modelo.</p></div>
</div>
<div class="foot">
<b>Fuente:</b> datos de práctica del curso Herramientas de Visualización (archivos 01 a 05, datos inventados con fines
académicos). Ventas y publicidad en millones de pesos corrientes; precios y gasto en la unidad monetaria del archivo. Cálculos propios: índice base enero 2024 = 100; ingreso = precio × unidades;
ganancia = ingreso × margen; valor del cliente = compras × gasto medio.<br>
Maestría en Analítica · Tarea Streamlit
</div>
"""
)
