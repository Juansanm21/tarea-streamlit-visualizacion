"""
Tarea Streamlit · Herramientas de Visualización
================================================

Informe de desempeño comercial en formato de tablero (una sola pantalla),
construido con los datos de práctica del curso. Cuatro secciones, cada una
con un gráfico tomado del cuaderno "Jupiter Dataviz" de la clase:

    Sección                 Archivo                    Gráfico (sección del cuaderno)
    1. Ventas ............. 01_ventas_mensuales.csv .. Líneas y áreas (7.1)
    2. Productos .......... 05_productos.csv ......... Burbujas (3.3 / 7.2)
    3. Clientes ........... 03_clientes.csv .......... Radar (3.11 / 7.7)
    4. Entregas ........... 04_entregas.csv .......... Distribución acumulada (4.1)

(02_clientes_por_ciudad_canal.csv no se usa: no aporta al mensaje del informe.)

Híbrido informe + tablero: la barra de filtros (periodo, categoría, tipo de
cliente, medio de entrega y plazo) recalcula indicadores, gráficos y títulos.
Los títulos se reescriben para que la afirmación siga siendo cierta con la
selección. El cierre resume las conclusiones sobre el total de los datos.

Decisiones de diseño
    - Sin doble eje: ventas y publicidad se comparan con un índice (inicio = 100).
    - Ingreso = precio × unidades; ganancia = ingreso × margen.
    - Burbujas escaladas por área y con escala fija entre filtros.
    - Textos escritos para un lector sin formación técnica.

Ejecutar:  python -m streamlit run app.py
"""

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ──────────────────────────────────────────────────────────────────────────────
# 1. Configuración, paleta y estilo
# ──────────────────────────────────────────────────────────────────────────────
BASE = Path(__file__).parent
st.set_page_config(page_title="Desempeño comercial 2024–2025", page_icon=str(BASE / "assets" / "favicon.png"),
                   layout="wide", initial_sidebar_state="collapsed")

DATA = BASE / "data"

# Paleta corporativa: azul marino (marca), azul acero (dato principal),
# verde y ocre (grupos), rojo vino solo para riesgos, grises para contexto.
FONDO, TINTA, TINTA_2, TENUE = "#F5F6F8", "#111827", "#374151", "#6B7280"
REJILLA, CONTEXTO = "#E5E7EB", "#CBD3DC"
MARINO, PRIMARIO, VERDE, OCRE, RIESGO = "#0B2545", "#1D4E89", "#3E8E7E", "#C99A2E", "#B23A48"
CATEGORIA_COL = {"Tecnología": PRIMARIO, "Muebles": OCRE, "Papelería": VERDE}
TIPO_COL = {"Frecuente": PRIMARIO, "Regular": VERDE, "Ocasional": OCRE}
MEDIO_COL = {"Moto": PRIMARIO, "Carro": "#8A99AD", "Bicicleta": RIESGO}
FUENTE = "'IBM Plex Sans', 'Segoe UI', sans-serif"
ALTO = 360                      # misma altura para los cuatro gráficos
PLOT_CONFIG = {"displayModeBar": False}


def rgba(hex_color: str, a: float) -> str:
    h = hex_color.lstrip("#")
    return f"rgba({int(h[0:2], 16)},{int(h[2:4], 16)},{int(h[4:6], 16)},{a})"


# Escala tipográfica (rem): 0.85 etiquetas · 1 texto · 1.3 títulos · 2 cifras · 2.4 portada
st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&display=swap');

html {{ font-size: 16px; }}
.stApp {{ background: {FONDO}; }}
html, body, .stApp, .stApp p, .stApp li, .stApp label, .stMarkdown, button {{ font-family: {FUENTE} !important; color: {TINTA}; }}
header[data-testid="stHeader"], [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"],
[data-testid="stToolbar"], [data-testid="stAppDeployButton"] {{ display: none; }}
.block-container {{ max-width: 100% !important; padding: 1.5rem 2.5rem 3rem 2.5rem !important; }}
@media (max-width: 800px) {{ .block-container {{ padding: 1rem !important; }} }}

/* Portada */
.hero {{ background: {MARINO}; border-radius: 14px; padding: 2rem 2.4rem; color: #fff;
        border-bottom: 4px solid {OCRE}; }}
.hero .tag {{ font-size: .85rem; letter-spacing: .12em; text-transform: uppercase; color: #9FB3C8; font-weight: 600; }}
.hero h1 {{ font-family: {FUENTE} !important; font-weight: 700; font-size: clamp(1.7rem, 2.4vw, 2.4rem); line-height: 1.2;
           color: #fff !important; margin: .5rem 0 .4rem 0; padding: 0; }}
.hero .sub {{ color: #C9D6E3 !important; font-size: 1.05rem; margin: 0 0 1.6rem 0; }}
.kpis {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 0; border-top: 1px solid rgba(255,255,255,.14); }}
.kpi {{ padding: 1.1rem 1.4rem 0 0; }}
.kpi + .kpi {{ padding-left: 1.4rem; border-left: 1px solid rgba(255,255,255,.14); }}
.kpi .v {{ font-weight: 700; font-size: clamp(1.7rem, 2.3vw, 2.2rem); line-height: 1.1; color: #fff; white-space: nowrap; }}
.kpi .l {{ font-size: 1rem; color: #DCE6F0; margin-top: .35rem; line-height: 1.35; }}
.kpi .d {{ font-size: .9rem; font-weight: 600; margin-top: .3rem; color: #E3C77A; }}
@media (max-width: 1000px) {{ .kpis {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
                             .kpi + .kpi {{ border-left: none; padding-left: 0; }} }}

/* Tarjetas: misma altura en cada fila */
[data-testid="stHorizontalBlock"]:has([class*="st-key-card_"]) {{ align-items: stretch; }}
[data-testid="stColumn"]:has(> [data-testid="stVerticalBlock"] > [class*="st-key-card_"]) > [data-testid="stVerticalBlock"] {{ height: 100%; }}
[class*="st-key-card_"] {{ height: 100%; background: #fff; border-radius: 14px; padding: 1.4rem 1.6rem 1rem 1.6rem;
                           box-shadow: 0 1px 2px rgba(17,24,39,.04), 0 6px 18px rgba(17,24,39,.05); border: 1px solid #ECEEF1; }}
.chip {{ font-size: .85rem; font-weight: 600; letter-spacing: .1em; text-transform: uppercase; color: {PRIMARIO}; }}
.titulo {{ font-weight: 700; font-size: 1.3rem; line-height: 1.3; color: {TINTA}; margin: .35rem 0 .35rem 0; }}
.texto {{ color: {TINTA_2}; font-size: 1rem; line-height: 1.55; margin: 0; min-height: 3.1em; }}
.texto b {{ color: {TINTA}; font-weight: 600; }}

/* Filtros */
.st-key-filtros {{ background: #fff; border-radius: 14px; padding: 1rem 1.6rem .6rem 1.6rem; border: 1px solid #ECEEF1;
                   box-shadow: 0 6px 18px rgba(17,24,39,.04); }}
[data-testid="stWidgetLabel"] p {{ font-size: .85rem !important; font-weight: 600 !important; letter-spacing: .06em;
                                   text-transform: uppercase; color: {TENUE} !important; }}
button[data-variant="segmented_control"] p, button[data-variant="pills"] p {{ font-size: .95rem !important; font-weight: 500; }}
button[data-variant="segmented_control"][data-selected="true"] {{ background: {PRIMARIO} !important; border-color: {PRIMARIO} !important; }}
button[data-variant="segmented_control"][data-selected="true"] p {{ color: #fff !important; }}
button[data-variant="pills"][data-selected="true"] {{ background: #E8EEF6 !important; border-color: {PRIMARIO} !important; }}
button[data-variant="pills"][data-selected="true"] p {{ color: {PRIMARIO} !important; font-weight: 600; }}
[data-testid="stSlider"] [role="slider"] {{ background: {PRIMARIO} !important; }}
[data-testid="stSliderThumbValue"] {{ font-size: .95rem; font-weight: 600; color: {TINTA} !important; }}
.st-key-limpiar button {{ border-radius: 8px; border-color: {REJILLA}; }}

/* Conclusiones */
.concl {{ background: {MARINO}; border-radius: 14px; padding: 2.2rem 2.4rem 2.4rem 2.4rem; color: #fff; border-top: 4px solid {OCRE}; }}
.concl .tag {{ font-size: .85rem; letter-spacing: .12em; text-transform: uppercase; color: #9FB3C8; font-weight: 600; }}
.concl h2 {{ font-family: {FUENTE} !important; font-weight: 700; font-size: clamp(1.5rem, 2vw, 2rem); color: #fff !important;
            margin: .4rem 0 1.6rem 0; padding: 0; line-height: 1.25; }}
.concl-grid {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 0; }}
.c-item {{ padding: 0 1.6rem 0 0; display: flex; flex-direction: column; }}
.c-item + .c-item {{ padding-left: 1.6rem; border-left: 1px solid rgba(255,255,255,.14); }}
.c-item .n {{ font-size: clamp(2.2rem, 3vw, 3rem); font-weight: 700; color: #E3C77A; line-height: 1; }}
.c-item .t {{ font-size: 1.12rem; font-weight: 600; color: #fff; margin: .7rem 0 .45rem 0; line-height: 1.35; }}
.c-item .p {{ font-size: 1rem; color: #C9D6E3; line-height: 1.55; flex: 1; }}
.c-item .r {{ margin-top: 1rem; padding-top: .8rem; border-top: 1px solid rgba(255,255,255,.14); font-size: .98rem;
             color: #fff; line-height: 1.5; }}
.c-item .r b {{ display: block; font-size: .8rem; letter-spacing: .1em; text-transform: uppercase; color: #E3C77A; margin-bottom: .2rem; }}
@media (max-width: 1000px) {{ .concl-grid {{ grid-template-columns: 1fr; gap: 1.6rem; }}
                             .c-item + .c-item {{ border-left: none; padding-left: 0; }} }}
</style>
""",
    unsafe_allow_html=True,
)


# ──────────────────────────────────────────────────────────────────────────────
# 2. Utilidades
# ──────────────────────────────────────────────────────────────────────────────
def num(x: float, dec: int = 0) -> str:
    """Formato colombiano: punto de miles, coma decimal."""
    return f"{x:,.{dec}f}".replace(",", "§").replace(".", ",").replace("§", ".")


def pct(x: float, dec: int = 0) -> str:
    return f"{num(x * 100, dec)} %"


def html(s: str) -> None:
    st.markdown(s, unsafe_allow_html=True)


def encabezado(chip: str, titulo: str, texto: str) -> None:
    html(f'<div class="chip">{chip}</div><div class="titulo">{titulo}</div><p class="texto">{texto}</p>')


def articulo(medio: str) -> str:
    return ("el " if medio == "Carro" else "la ") + medio.lower()


def estilo(fig: go.Figure, leyenda: bool = False) -> go.Figure:
    """Plantilla común para todos los gráficos."""
    fig.update_layout(
        template="plotly_white", height=ALTO, margin=dict(l=4, r=12, t=34, b=4),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FUENTE, size=14, color=TINTA_2), showlegend=leyenda,
        hoverlabel=dict(bgcolor=TINTA, bordercolor=TINTA, font=dict(family=FUENTE, size=14, color="#fff")),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, title=None, font=dict(size=14)),
    )
    fig.update_xaxes(showgrid=False, linecolor=REJILLA, zeroline=False, tickfont=dict(size=13, color=TENUE),
                     title_font=dict(size=13.5, color=TENUE))
    fig.update_yaxes(gridcolor=REJILLA, zeroline=False, tickfont=dict(size=13, color=TENUE),
                     title_font=dict(size=13.5, color=TENUE))
    return fig


def mostrar(fig: go.Figure) -> None:
    st.plotly_chart(fig, use_container_width=True, config=PLOT_CONFIG)


# ──────────────────────────────────────────────────────────────────────────────
# 3. Datos (vienen limpios; solo se derivan métricas)
# ──────────────────────────────────────────────────────────────────────────────
@st.cache_data
def cargar():
    leer = lambda f: pd.read_csv(DATA / f, encoding="utf-8-sig")
    ventas, clientes = leer("01_ventas_mensuales.csv"), leer("03_clientes.csv")
    entregas, productos = leer("04_entregas.csv"), leer("05_productos.csv")

    ventas["anio"] = pd.to_datetime(ventas["fecha"]).dt.year
    productos["ingreso"] = productos["precio"] * productos["unidades"]       # unidades ≠ ingreso
    productos["ganancia"] = productos["ingreso"] * productos["margen_pct"] / 100
    clientes["valor"] = clientes["compras"] * clientes["gasto_medio"]        # valor total por cliente
    return ventas, clientes, entregas, productos


ventas, clientes, entregas, productos = cargar()

# ──────────────────────────────────────────────────────────────────────────────
# 4. Portada (se llena al final, cuando ya se conocen los filtros)
# ──────────────────────────────────────────────────────────────────────────────
banda = st.empty()
st.write("")

# ──────────────────────────────────────────────────────────────────────────────
# 5. Filtros
# ──────────────────────────────────────────────────────────────────────────────
PERIODOS = ["Todo", "2024", "2025"]
CATEGORIAS = sorted(productos.categoria.unique())
TIPOS = ["Frecuente", "Regular", "Ocasional"]
MEDIOS = ["Moto", "Carro", "Bicicleta"]
PLURAL = {"Frecuente": "frecuentes", "Regular": "regulares", "Ocasional": "ocasionales"}
DEFAULTS = {"f_periodo": "Todo", "f_cat": CATEGORIAS, "f_seg": TIPOS, "f_medio": MEDIOS, "plazo": 3.0}
for k, val in DEFAULTS.items():
    st.session_state.setdefault(k, val)


def restablecer() -> None:
    for k, val in DEFAULTS.items():
        st.session_state[k] = val


with st.container(key="filtros"):
    f1, f2, f3, f4, f5, f6 = st.columns([2.3, 3.0, 3.1, 2.4, 1.7, .45], gap="small", vertical_alignment="bottom")
    with f1:
        periodo = st.segmented_control("Periodo", PERIODOS, key="f_periodo") or "Todo"
    with f2:
        cats = st.pills("Categoría de producto", CATEGORIAS, selection_mode="multi", key="f_cat")
    with f3:
        segs = st.pills("Tipo de cliente", TIPOS, selection_mode="multi", key="f_seg")
    with f4:
        medios = st.pills("Medio de entrega", MEDIOS, selection_mode="multi", key="f_medio")
    with f5:
        plazo = st.slider("Plazo (horas)", 1.0, 8.0, step=0.5, key="plazo")
    with f6:
        st.button(":material/restart_alt:", key="limpiar", on_click=restablecer, help="Restablecer filtros",
                  use_container_width=True)

# Una selección vacía equivale a "todos", para que el tablero nunca quede en blanco.
cats = [c for c in CATEGORIAS if c in (cats or CATEGORIAS)]
segs = [s for s in TIPOS if s in (segs or TIPOS)]
medios = [m for m in MEDIOS if m in (medios or MEDIOS)]
etiqueta_periodo = "2024 – 2025" if periodo == "Todo" else periodo

v = ventas if periodo == "Todo" else ventas[ventas.anio == int(periodo)]
v = v.assign(Ventas=v.ventas_millones / v.ventas_millones.iloc[0] * 100,            # índice: el primer mes
             Publicidad=v.publicidad_millones / v.publicidad_millones.iloc[0] * 100)  # del periodo vale 100
prod = productos[productos.categoria.isin(cats)]
cli = clientes[clientes.segmento.isin(segs)]
ent = entregas[entregas.tipo.isin(medios)]

anual = ventas.groupby("anio")[["ventas_millones", "publicidad_millones"]].sum()
crec_v = anual.loc[2025, "ventas_millones"] / anual.loc[2024, "ventas_millones"] - 1
crec_p = anual.loc[2025, "publicidad_millones"] / anual.loc[2024, "publicidad_millones"] - 1
rend = anual["ventas_millones"] / anual["publicidad_millones"]
top_g = prod.loc[prod.ganancia.idxmax()]
mas_vendido = prod.loc[prod.unidades.idxmax()]
st.write("")

# ──────────────────────────────────────────────────────────────────────────────
# 6. Fila 1 · Ventas (líneas con la diferencia sombreada) · Productos (burbujas)
# ──────────────────────────────────────────────────────────────────────────────
c1, c2 = st.columns(2, gap="medium")

with c1, st.container(key="card_ventas"):
    ini, ult = v.iloc[0], v.iloc[-1]
    adelante = ult.Ventas - ult.Publicidad > 10
    encabezado(
        "Ventas y publicidad",
        "Las ventas crecen más rápido que la publicidad" if adelante else "Ventas y publicidad crecen al mismo ritmo",
        f"Las dos líneas arrancan en 100 en {ini.mes}. Al cierre, las ventas llegan a <b>{num(ult.Ventas)}</b> "
        f"(crecieron {num(ult.Ventas - 100)}&nbsp;%) y la publicidad a <b>{num(ult.Publicidad)}</b> "
        f"(creció {num(ult.Publicidad - 100)}&nbsp;%).",
    )
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=v.mes, y=v.Publicidad, name="Publicidad", mode="lines",
                             line=dict(color="#9AA5B4", width=2.5), customdata=v.publicidad_millones,
                             hovertemplate="Publicidad: $%{customdata:.1f} millones<extra></extra>"))
    fig.add_trace(go.Scatter(x=v.mes, y=v.Ventas, name="Ventas", mode="lines", fill="tonexty",
                             fillcolor=rgba(PRIMARIO, .10), line=dict(color=PRIMARIO, width=3),
                             customdata=v.ventas_millones,
                             hovertemplate="Ventas: $%{customdata:.0f} millones<extra></extra>"))
    for serie, color in [("Ventas", PRIMARIO), ("Publicidad", TINTA_2)]:
        fig.add_trace(go.Scatter(x=[ult.mes], y=[ult[serie]], mode="markers", hoverinfo="skip", showlegend=False,
                                 marker=dict(size=10, color=color, line=dict(color="white", width=2))))
        fig.add_annotation(x=ult.mes, y=ult[serie], text=f"<b>{serie}  {num(ult[serie])}</b>", showarrow=False,
                           xanchor="left", xshift=10, font=dict(color=color, size=14))
    medio = v.iloc[int(len(v) * .83)]
    fig.add_annotation(x=medio.mes, y=(medio.Ventas + medio.Publicidad) / 2, text="diferencia a favor<br>de las ventas",
                       showarrow=False, font=dict(size=13, color=PRIMARIO))
    estilo(fig)
    paso = 3 if len(v) > 12 else 2
    fig.update_layout(hovermode="x unified", margin=dict(r=135))
    fig.update_xaxes(tickvals=list(v.mes[::paso]), ticktext=[m.replace(" ", "<br>") for m in v.mes[::paso]])
    techo = max(v.Ventas.max(), v.Publicidad.max())
    fig.update_yaxes(title=f"Crecimiento ({ini.mes} = 100)",
                     range=[min(85, v[["Ventas", "Publicidad"]].min().min() - 5), techo * 1.07])
    mostrar(fig)

with c2, st.container(key="card_productos"):
    if mas_vendido.name != top_g.name:
        titulo = "Vender más unidades no significa ganar más"
        texto = (f"Cada círculo es un producto; su tamaño es la ganancia que deja. El <b>{mas_vendido.producto.lower()}</b> "
                 f"es el más vendido, pero el <b>{top_g.producto.lower()}</b> es el que más dinero aporta.")
    else:
        titulo = f"El {top_g.producto.lower()} es el más vendido y el que más gana"
        texto = ("Cada círculo es un producto; su tamaño es la ganancia que deja. En esta selección, "
                 f"el <b>{top_g.producto.lower()}</b> lidera en unidades y en ganancia.")
    encabezado("Productos", titulo, texto)
    fig = go.Figure()
    POS_ETIQUETA = {"Escritorio": "middle left", "Estante": "top center", "Silla": "bottom right",
                    "Marcadores": "middle left", "Agenda": "top center", "Bolígrafo": "top center"}   # evita etiquetas encimadas
    escala = 2.0 * productos.ganancia.max() / 62 ** 2                   # área ∝ ganancia, escala fija
    for cat in cats:
        g = prod[prod.categoria == cat]
        fig.add_trace(go.Scatter(
            x=g.unidades, y=g.margen_pct, mode="markers+text", name=cat, text=g.producto,
            textposition=[POS_ETIQUETA.get(p, "middle right") for p in g.producto],
            textfont=dict(size=13, color=TINTA_2),
            marker=dict(size=g.ganancia, sizemode="area", sizeref=escala, sizemin=5,
                        color=rgba(CATEGORIA_COL[cat], .55), line=dict(color=CATEGORIA_COL[cat], width=1.5)),
            customdata=np.stack([g.precio, g.ganancia], axis=1),
            hovertemplate="<b>%{text}</b><br>%{x:,.0f} unidades vendidas<br>Margen: %{y} %"
                          "<br>Precio: $%{customdata[0]:,.0f}<br>Ganancia: $%{customdata[1]:,.0f}<extra></extra>"))
    estilo(fig, leyenda=True)
    fig.update_xaxes(type="log", title="Unidades vendidas", showgrid=True, gridcolor=REJILLA,
                     range=[np.log10(35), np.log10(12000)], tickvals=[100, 300, 1000, 3000, 10000],
                     ticktext=["100", "300", "1.000", "3.000", "10.000"])
    fig.update_yaxes(title="Margen de ganancia", range=[8, 70], ticksuffix=" %")
    mostrar(fig)

st.write("")

# ──────────────────────────────────────────────────────────────────────────────
# 7. Fila 2 · Clientes (radar) · Entregas (distribución acumulada)
# ──────────────────────────────────────────────────────────────────────────────
c3, c4 = st.columns(2, gap="medium")

with c3, st.container(key="card_clientes"):
    variables = {"compras": "Número de compras", "gasto_medio": "Gasto por compra",
                 "valor": "Valor total del cliente", "edad": "Edad"}
    perfil = clientes.groupby("segmento")[list(variables)].median()   # cliente típico de cada tipo
    indice = perfil / perfil.max() * 100                              # 100 = el tipo con el valor más alto
    top_s = perfil.loc[segs, "valor"].idxmax()
    encabezado(
        "Clientes",
        "Cada tipo de cliente compra de forma distinta" if len(segs) > 1 else f"Así compran los clientes {PLURAL[segs[0]]}",
        f"Cada figura es un tipo de cliente: cuanto más lejos del centro, más alto el valor. Los "
        f"<b>{PLURAL[top_s]}</b> son los que más dinero dejan en total: ${num(perfil.loc[top_s, 'valor'])} por cliente.",
    )
    fig = go.Figure()
    ejes = list(variables.values())
    for s in segs:
        fig.add_trace(go.Scatterpolar(
            r=list(indice.loc[s]) + [indice.loc[s].iloc[0]], theta=ejes + [ejes[0]], name=s, fill="toself",
            fillcolor=rgba(TIPO_COL[s], .14), line=dict(color=TIPO_COL[s], width=2.5), marker=dict(size=7),
            customdata=list(perfil.loc[s]) + [perfil.loc[s].iloc[0]],
            hovertemplate=f"<b>{s}</b><br>%{{theta}}: %{{customdata:,.0f}}<extra></extra>"))
    estilo(fig, leyenda=True)
    fig.update_layout(polar=dict(bgcolor="rgba(0,0,0,0)",
                                 radialaxis=dict(range=[0, 105], showticklabels=False, gridcolor=REJILLA, linecolor=REJILLA),
                                 angularaxis=dict(gridcolor=REJILLA, linecolor=REJILLA, tickfont=dict(size=14, color=TINTA_2))),
                      legend=dict(orientation="v", x=0, y=1, yanchor="top", xanchor="left"),
                      margin=dict(l=60, r=60, t=40, b=24))
    mostrar(fig)

with c4, st.container(key="card_entregas"):
    cumple = ent.assign(ok=ent.tiempo_horas <= plazo).groupby("tipo")["ok"].mean()
    mejor, peor = cumple.idxmax(), cumple.idxmin()
    p = num(plazo, 1).rstrip("0").rstrip(",")
    if len(medios) > 1:
        titulo = f"En {p} horas, {articulo(mejor)} entrega el {pct(cumple[mejor])}; {articulo(peor)}, el {pct(cumple[peor])}"
    else:
        titulo = f"En {p} horas, {articulo(medios[0])} entrega el {pct(cumple[medios[0]])} de los pedidos"
    encabezado(
        "Entregas",
        titulo,
        "Cada línea muestra qué parte de los pedidos ya se entregó a medida que pasan las horas. "
        "La línea punteada es el plazo elegido en los filtros.",
    )
    fig = go.Figure()
    for m in medios:
        t = np.sort(ent.loc[ent.tipo == m, "tiempo_horas"].to_numpy())
        y = np.arange(1, len(t) + 1) / len(t)
        fig.add_trace(go.Scatter(x=np.r_[0, t, 10], y=np.r_[0, y, 1], name=m, mode="lines", line_shape="hv",
                                 line=dict(color=MEDIO_COL[m], width=3),
                                 hovertemplate=f"{m}: %{{y:.0%}} entregado a las %{{x:.1f}} h<extra></extra>"))
        fig.add_trace(go.Scatter(x=[plazo], y=[cumple[m]], mode="markers", showlegend=False, hoverinfo="skip",
                                 marker=dict(size=12, color=MEDIO_COL[m], line=dict(color="white", width=2))))
        fig.add_annotation(x=plazo, y=cumple[m], text=f"<b>{pct(cumple[m])}</b>", showarrow=False, xanchor="right",
                           xshift=-12, bgcolor="rgba(255,255,255,.92)", borderpad=2,
                           font=dict(size=14, color=MEDIO_COL[m] if m != "Carro" else TINTA_2))
    fig.add_vline(x=plazo, line=dict(color=TINTA, width=1.5, dash="dash"))
    fig.add_annotation(x=plazo, y=1.0, yref="paper", yanchor="bottom", text=f"plazo: {p} h", showarrow=False,
                       xanchor="left", xshift=6, font=dict(size=13, color=TINTA))
    estilo(fig, leyenda=True)
    fig.update_layout(legend=dict(orientation="v", x=.98, y=.06, xanchor="right", yanchor="bottom",
                                  bgcolor="rgba(255,255,255,.9)"))
    fig.update_xaxes(title="Horas desde el pedido", range=[0, 10], dtick=1, showgrid=True, gridcolor=REJILLA)
    fig.update_yaxes(title="Pedidos entregados", range=[0, 1.04], tickformat=".0%", dtick=0.25)
    mostrar(fig)

# ──────────────────────────────────────────────────────────────────────────────
# 8. Portada, ya con los filtros aplicados
# ──────────────────────────────────────────────────────────────────────────────
a_tiempo = (ent.tiempo_horas <= plazo).mean()
v_tot, p_tot = v.ventas_millones.sum(), v.publicidad_millones.sum()
delta_v = "primer año analizado" if periodo == "2024" else f"▲ {pct(crec_v)} más que en 2024"
delta_r = "primer año analizado" if periodo == "2024" else f"en 2024 eran ${num(rend.loc[2024], 1)}"
p = num(plazo, 1).rstrip("0").rstrip(",")
banda.markdown(
    f"""
<div class="hero">
  <div class="tag">Informe de desempeño comercial · {etiqueta_periodo}</div>
  <h1>Las ventas crecieron {pct(crec_v)} en 2025, mientras la inversión en publicidad subió solo {pct(crec_p)}</h1>
  <p class="sub">Resumen de las ventas, los productos, los clientes y las entregas de la empresa.</p>
  <div class="kpis">
    <div class="kpi"><div class="v">${num(v_tot)} millones</div><div class="l">Ventas totales del periodo</div>
      <div class="d">{delta_v}</div></div>
    <div class="kpi"><div class="v">${num(v_tot / p_tot, 1)}</div><div class="l">Vendidos por cada $1 invertido en publicidad</div>
      <div class="d">{delta_r}</div></div>
    <div class="kpi"><div class="v">{top_g.producto}</div><div class="l">Producto que más ganancia deja</div>
      <div class="d">${num(top_g.ganancia)} de ganancia</div></div>
    <div class="kpi"><div class="v">{pct(a_tiempo)}</div><div class="l">Pedidos entregados en {p} horas o menos</div>
      <div class="d">{', '.join(m.lower() for m in medios)}</div></div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────────────────────────────────────
# 9. Conclusiones (sobre el total de los datos; no cambian con los filtros)
# ──────────────────────────────────────────────────────────────────────────────
st.write("")
st.write("")
rank_g = productos.sort_values("ganancia", ascending=False).producto.str.lower().tolist()
u_all = productos.loc[productos.unidades.idxmax()]
pos_u = rank_g.index(u_all.producto.lower()) + 1
val_tipo = clientes.groupby("segmento").valor.median()
seg_top = val_tipo.idxmax()
ok3 = (entregas.tiempo_horas <= 3).groupby(entregas.tipo).mean()
html(
    f"""
<div class="concl">
  <div class="tag">Conclusiones</div>
  <h2>La empresa crece de forma eficiente; el reto ahora es la rentabilidad y la entrega</h2>
  <div class="concl-grid">
    <div class="c-item"><div class="n">+{pct(crec_v)}</div>
      <div class="t">Las ventas crecen sin depender de más publicidad</div>
      <div class="p">Cada $1 invertido en publicidad pasó de generar ${num(rend.loc[2024], 1)} en ventas a
      ${num(rend.loc[2025], 1)}.</div>
      <div class="r"><b>Recomendación</b>Mantener el presupuesto e identificar qué campañas explican el crecimiento.</div></div>
    <div class="c-item"><div class="n">{pos_u}.º de {len(rank_g)}</div>
      <div class="t">El producto más vendido no es el más rentable</div>
      <div class="p">El {u_all.producto.lower()} es el que más se vende, pero ocupa el puesto {pos_u} de {len(rank_g)}
      en ganancia.</div>
      <div class="r"><b>Recomendación</b>Dar prioridad a los productos de mayor margen: {rank_g[0]}, {rank_g[1]} y {rank_g[2]}.</div></div>
    <div class="c-item"><div class="n">${num(val_tipo[seg_top])}</div>
      <div class="t">Los clientes {PLURAL[seg_top]} son los más valiosos</div>
      <div class="p">Dejan más dinero por cliente que los frecuentes, aunque compran menos veces.</div>
      <div class="r"><b>Recomendación</b>Diseñar ofertas distintas para cada tipo de cliente.</div></div>
    <div class="c-item"><div class="n">{num(ok3['Bicicleta'] * 100)} de 100</div>
      <div class="t">La bicicleta es el punto débil de la entrega</div>
      <div class="p">Solo {num(ok3['Bicicleta'] * 100)} de cada 100 pedidos en bicicleta llegan en 3 horas;
      en moto llegan {num(ok3['Moto'] * 100)}.</div>
      <div class="r"><b>Recomendación</b>Revisar rutas y asignación de bicicletas antes de que aumenten los pedidos.</div></div>
  </div>
</div>
"""
)
