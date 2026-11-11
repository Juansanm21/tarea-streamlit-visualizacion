"""
Tarea Streamlit · Herramientas de Visualización
================================================

Informe de desempeño comercial en formato de tablero (una sola pantalla),
construido con los datos de práctica del curso. Cuatro secciones, cada una
con un gráfico tomado del cuaderno "Jupiter Dataviz" de la clase:

    Sección                 Archivo                    Gráfico (sección del cuaderno)
    1. Ventas ............. 01_ventas_mensuales.csv .. Líneas y áreas (7.1)
    2. Rentabilidad ....... 05_productos.csv ......... Burbujas (3.3 / 7.2)
    3. Clientes ........... 03_clientes.csv .......... Radar (3.11 / 7.7)
    4. Entregas ........... 04_entregas.csv .......... Raincloud: violín + puntos (4.3 / 7.3)

(02_clientes_por_ciudad_canal.csv no se usa: no aporta al mensaje del informe.)

Híbrido informe + tablero: la barra de filtros (periodo, categoría, segmento,
medio de entrega y plazo) recalcula indicadores, gráficos y títulos; los títulos
se reescriben para que la afirmación siga siendo cierta con la selección.

Reglas de cada gráfico (reto del PDF de la clase)
    - El título afirma un hallazgo verificable.
    - Cada sección cierra con una limitación.
    - Sin doble eje (índice base 100); ingreso = precio × unidades; burbujas
      escaladas por área; misma escala entre grupos.

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
st.set_page_config(page_title="Desempeño comercial 2024–2025", page_icon=str(Path(__file__).parent / "assets" / "favicon.png"), layout="wide",
                   initial_sidebar_state="collapsed")

DATA = Path(__file__).parent / "data"

# Paleta corporativa: azul marino (marca), azul acero (dato principal),
# verde y ocre (grupos), rojo vino solo para riesgos, grises para contexto.
FONDO, TINTA, TINTA_2, TENUE = "#F5F6F8", "#111827", "#4B5563", "#9CA3AF"
REJILLA, CONTEXTO = "#E5E7EB", "#CBD3DC"
MARINO, PRIMARIO, VERDE, OCRE, RIESGO = "#0B2545", "#1D4E89", "#3E8E7E", "#C99A2E", "#B23A48"
CATEGORIA_COL = {"Tecnología": PRIMARIO, "Muebles": OCRE, "Papelería": VERDE}
SEGMENTO_COL = {"Frecuente": PRIMARIO, "Regular": VERDE, "Ocasional": OCRE}
MEDIO_COL = {"Moto": PRIMARIO, "Carro": "#8A99AD", "Bicicleta": RIESGO}
FUENTE = "'Plus Jakarta Sans', 'Segoe UI', sans-serif"
ALTO = 340                      # misma altura para los cuatro gráficos
PLOT_CONFIG = {"displayModeBar": False}


def rgba(hex_color: str, a: float) -> str:
    h = hex_color.lstrip("#")
    return f"rgba({int(h[0:2], 16)},{int(h[2:4], 16)},{int(h[4:6], 16)},{a})"


st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

.stApp {{ background: {FONDO}; }}
html, body, .stApp, .stApp p, .stApp li, .stApp label, .stMarkdown {{ font-family: {FUENTE}; color: {TINTA}; }}
header[data-testid="stHeader"], [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"],
[data-testid="stToolbar"], [data-testid="stAppDeployButton"] {{ display: none; }}
.block-container {{ max-width: 100% !important; padding: 1.4rem 2.4rem 2.5rem 2.4rem !important; }}
@media (max-width: 800px) {{ .block-container {{ padding: 1rem !important; }} }}

/* Encabezado */
.hero {{ background: {MARINO}; border-radius: 14px; padding: 1.7rem 2.2rem; color: #fff;
        display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1.35fr); gap: 2.4rem; align-items: center;
        border-bottom: 4px solid {OCRE}; }}
.hero .tag {{ font-size: .72rem; letter-spacing: .14em; text-transform: uppercase; color: #9FB3C8; font-weight: 600; }}
.hero h1 {{ font-family: {FUENTE}; font-weight: 700; font-size: clamp(1.45rem, 2.1vw, 2.05rem); line-height: 1.22;
           color: #fff !important; margin: .5rem 0 .5rem 0; padding: 0; letter-spacing: -.015em; }}
.hero p {{ color: #C9D6E3 !important; font-size: .92rem; margin: 0; }}
.kpis {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; }}
.kpi {{ border-left: 1px solid rgba(255,255,255,.16); padding: 4px 0 4px 16px; }}
.kpi .v {{ font-weight: 700; font-size: clamp(1.35rem, 1.9vw, 1.9rem); line-height: 1.05; color: #fff; white-space: nowrap; }}
.kpi .l {{ font-size: .78rem; color: #9FB3C8; margin-top: 6px; line-height: 1.35; }}
.kpi .d {{ font-size: .74rem; font-weight: 600; margin-top: 6px; color: #E3C77A; }}
@media (max-width: 1100px) {{ .hero {{ grid-template-columns: 1fr; }} .kpis {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }} }}

/* Tarjetas: misma altura en cada fila */
[data-testid="stHorizontalBlock"]:has([class*="st-key-card_"]) {{ align-items: stretch; }}
[data-testid="stColumn"]:has(> [data-testid="stVerticalBlock"] > [class*="st-key-card_"]) > [data-testid="stVerticalBlock"] {{ height: 100%; }}
[class*="st-key-card_"] {{ height: 100%; background: #fff; border-radius: 14px; padding: 1.2rem 1.4rem .9rem 1.4rem;
                           box-shadow: 0 1px 2px rgba(17,24,39,.04), 0 6px 18px rgba(17,24,39,.05); border: 1px solid #ECEEF1; }}
.chip {{ font-size: .7rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; color: {PRIMARIO}; }}
.titulo {{ font-weight: 700; font-size: 1.18rem; line-height: 1.3; color: {TINTA}; margin: .3rem 0 .2rem 0;
          white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
.texto {{ color: {TINTA_2}; font-size: .88rem; line-height: 1.5; margin: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
.texto b {{ color: {TINTA}; font-weight: 600; }}
.limite {{ color: {TENUE}; font-size: .78rem; border-top: 1px solid {REJILLA}; padding-top: .55rem; margin: 0; }}
.limite b {{ color: {TINTA_2}; font-weight: 600; }}

/* Filtros */
.st-key-filtros {{ background: #fff; border-radius: 14px; padding: .9rem 1.4rem .5rem 1.4rem; border: 1px solid #ECEEF1;
                   box-shadow: 0 6px 18px rgba(17,24,39,.04); }}
[data-testid="stWidgetLabel"] p {{ font-size: .7rem !important; font-weight: 700 !important; letter-spacing: .1em;
                                   text-transform: uppercase; color: {TENUE} !important; }}
button[data-variant="segmented_control"] p, button[data-variant="pills"] p {{ font-family: {FUENTE}; font-size: .82rem; font-weight: 600; }}
button[data-variant="segmented_control"][data-selected="true"] {{ background: {PRIMARIO} !important; border-color: {PRIMARIO} !important; }}
button[data-variant="segmented_control"][data-selected="true"] p {{ color: #fff !important; }}
button[data-variant="pills"][data-selected="true"] {{ background: #E8EEF6 !important; border-color: {PRIMARIO} !important; }}
button[data-variant="pills"][data-selected="true"] p {{ color: {PRIMARIO} !important; }}
[data-testid="stSlider"] [role="slider"] {{ background: {PRIMARIO} !important; }}
.st-key-limpiar button {{ border-radius: 8px; border-color: {REJILLA}; }}
.st-key-limpiar button p {{ font-weight: 600; font-size: .82rem; color: {TINTA_2}; }}

/* Conclusiones */
.cierre {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16px; }}
.paso {{ background: #fff; border-radius: 14px; padding: 1rem 1.3rem; border: 1px solid #ECEEF1;
        border-top: 3px solid {PRIMARIO}; box-shadow: 0 6px 18px rgba(17,24,39,.04); }}
.paso .k {{ font-size: .7rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; color: {TENUE}; }}
.paso b {{ display: block; font-size: .98rem; margin: .25rem 0 .2rem 0; color: {TINTA}; }}
.paso span {{ color: {TINTA_2}; font-size: .86rem; }}
@media (max-width: 900px) {{ .cierre {{ grid-template-columns: 1fr; }} .titulo, .texto {{ white-space: normal; }} }}
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


def signo(x: float) -> str:
    return ("+" if x >= 0 else "−") + num(abs(x)) + " %"


def html(s: str) -> None:
    st.markdown(s, unsafe_allow_html=True)


def encabezado(chip: str, titulo: str, texto: str) -> None:
    html(f'<div class="chip">{chip}</div><div class="titulo" title="{titulo}">{titulo}</div><p class="texto">{texto}</p>')


def limite(t: str) -> None:
    html(f'<p class="limite"><b>Limitación:</b> {t}</p>')


def estilo(fig: go.Figure, leyenda: bool = False) -> go.Figure:
    """Plantilla común para todos los gráficos."""
    fig.update_layout(
        template="plotly_white", height=ALTO, margin=dict(l=4, r=12, t=30, b=4),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FUENTE, size=12.5, color=TINTA_2), showlegend=leyenda,
        hoverlabel=dict(bgcolor=TINTA, bordercolor=TINTA, font=dict(family=FUENTE, size=12.5, color="#fff")),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, title=None, font=dict(size=12)),
    )
    fig.update_xaxes(showgrid=False, linecolor=REJILLA, zeroline=False, tickfont=dict(color=TENUE),
                     title_font=dict(size=12, color=TENUE))
    fig.update_yaxes(gridcolor=REJILLA, zeroline=False, tickfont=dict(color=TENUE),
                     title_font=dict(size=12, color=TENUE))
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
# 4. Encabezado (se llena al final, cuando ya se conocen los filtros)
# ──────────────────────────────────────────────────────────────────────────────
banda = st.empty()
st.write("")

# ──────────────────────────────────────────────────────────────────────────────
# 5. Filtros
# ──────────────────────────────────────────────────────────────────────────────
PERIODOS = ["Todo", "2024", "2025"]
CATEGORIAS = sorted(productos.categoria.unique())
SEGMENTOS = ["Frecuente", "Regular", "Ocasional"]
MEDIOS = ["Moto", "Carro", "Bicicleta"]
PLURAL = {"Frecuente": "frecuentes", "Regular": "regulares", "Ocasional": "ocasionales"}
DEFAULTS = {"f_periodo": "Todo", "f_cat": CATEGORIAS, "f_seg": SEGMENTOS, "f_medio": MEDIOS, "plazo": 3.0}
for k, val in DEFAULTS.items():
    st.session_state.setdefault(k, val)


def restablecer() -> None:
    for k, val in DEFAULTS.items():
        st.session_state[k] = val


with st.container(key="filtros"):
    f1, f2, f3, f4, f5, f6 = st.columns([2.1, 2.7, 2.9, 2.3, 1.9, .5], gap="small", vertical_alignment="bottom")
    with f1:
        periodo = st.segmented_control("Periodo", PERIODOS, key="f_periodo") or "Todo"
    with f2:
        cats = st.pills("Categoría", CATEGORIAS, selection_mode="multi", key="f_cat")
    with f3:
        segs = st.pills("Segmento", SEGMENTOS, selection_mode="multi", key="f_seg")
    with f4:
        medios = st.pills("Medio de entrega", MEDIOS, selection_mode="multi", key="f_medio")
    with f5:
        plazo = st.slider("Plazo de entrega (h)", 1.0, 8.0, step=0.5, key="plazo")
    with f6:
        st.button(":material/restart_alt:", key="limpiar", on_click=restablecer, help="Restablecer filtros",
                  use_container_width=True)

# Una selección vacía equivale a "todos", para que el tablero nunca quede en blanco.
cats = [c for c in CATEGORIAS if c in (cats or CATEGORIAS)]
segs = [s for s in SEGMENTOS if s in (segs or SEGMENTOS)]
medios = [m for m in MEDIOS if m in (medios or MEDIOS)]
etiqueta_periodo = "2024 – 2025" if periodo == "Todo" else periodo

v = ventas if periodo == "Todo" else ventas[ventas.anio == int(periodo)]
v = v.assign(Ventas=v.ventas_millones / v.ventas_millones.iloc[0] * 100,            # índice rebasado al
             Publicidad=v.publicidad_millones / v.publicidad_millones.iloc[0] * 100)  # primer mes del periodo
prod = productos[productos.categoria.isin(cats)]
cli = clientes[clientes.segmento.isin(segs)]
ent = entregas[entregas.tipo.isin(medios)]

anual = ventas.groupby("anio")[["ventas_millones", "publicidad_millones"]].sum()
crec_v = anual.loc[2025, "ventas_millones"] / anual.loc[2024, "ventas_millones"] - 1
crec_p = anual.loc[2025, "publicidad_millones"] / anual.loc[2024, "publicidad_millones"] - 1
top_g = prod.loc[prod.ganancia.idxmax()]
mas_vendido = prod.loc[prod.unidades.idxmax()]
st.write("")

# ──────────────────────────────────────────────────────────────────────────────
# 6. Fila 1 · Ventas (líneas y área) · Rentabilidad (burbujas)
# ──────────────────────────────────────────────────────────────────────────────
c1, c2 = st.columns(2, gap="medium")

with c1, st.container(key="card_ventas"):
    ini, ult = v.iloc[0], v.iloc[-1]
    brecha = ult.Ventas - ult.Publicidad
    encabezado(
        "Ventas y publicidad",
        "Las ventas crecen más rápido que la publicidad" if brecha > 10 else "Ventas y publicidad avanzan a la par",
        f"Índice base {ini.mes} = 100 · ventas <b>{signo(ult.Ventas - 100)}</b> · publicidad "
        f"<b>{signo(ult.Publicidad - 100)}</b>",
    )
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=v.mes, y=v.Publicidad, name="Publicidad", mode="lines",
                             line=dict(color=TENUE, width=2.5), customdata=v.publicidad_millones,
                             hovertemplate="Publicidad %{y:.0f} · $%{customdata:.1f} M<extra></extra>"))
    fig.add_trace(go.Scatter(x=v.mes, y=v.Ventas, name="Ventas", mode="lines", fill="tonexty",
                             fillcolor=rgba(PRIMARIO, .10), line=dict(color=PRIMARIO, width=3),
                             customdata=v.ventas_millones,
                             hovertemplate="Ventas %{y:.0f} · $%{customdata:.0f} M<extra></extra>"))
    for serie, color in [("Ventas", PRIMARIO), ("Publicidad", TINTA_2)]:
        fig.add_trace(go.Scatter(x=[ult.mes], y=[ult[serie]], mode="markers", hoverinfo="skip", showlegend=False,
                                 marker=dict(size=9, color=color, line=dict(color="white", width=2))))
        fig.add_annotation(x=ult.mes, y=ult[serie], text=f"<b>{serie}  {num(ult[serie])}</b>", showarrow=False,
                           xanchor="left", xshift=10, font=dict(color=color, size=12.5))
    medio = v.iloc[len(v) // 2]
    fig.add_annotation(x=medio.mes, y=(medio.Ventas + medio.Publicidad) / 2, text="brecha", showarrow=False,
                       font=dict(size=12, color=PRIMARIO))
    estilo(fig)
    paso = 3 if len(v) > 12 else 2
    fig.update_layout(hovermode="x unified", margin=dict(r=120))
    fig.update_xaxes(tickvals=list(v.mes[::paso]), ticktext=[m.replace(" ", "<br>") for m in v.mes[::paso]])
    techo = max(v.Ventas.max(), v.Publicidad.max())
    fig.update_yaxes(range=[min(85, v[["Ventas", "Publicidad"]].min().min() - 5), techo * 1.07])
    mostrar(fig)
    limite("la correlación entre ambas series no implica causalidad.")

with c2, st.container(key="card_rentabilidad"):
    if mas_vendido.name != top_g.name:
        titulo = "El volumen no determina la ganancia"
        texto = (f"Área = ganancia estimada · <b>{mas_vendido.producto}</b> lidera en unidades; "
                 f"<b>{top_g.producto}</b>, en ganancia")
    else:
        titulo = f"{top_g.producto} lidera en volumen y en ganancia"
        texto = f"Área = ganancia estimada · {', '.join(cats)}"
    encabezado("Rentabilidad por producto", titulo, texto)
    fig = go.Figure()
    POS_ETIQUETA = {"Escritorio": "middle left", "Estante": "top center", "Silla": "bottom right",
                    "Marcadores": "middle left", "Agenda": "top center"}   # evita etiquetas encimadas
    escala = 2.0 * productos.ganancia.max() / 58 ** 2          # burbujas por área, escala fija entre filtros
    for cat in cats:
        g = prod[prod.categoria == cat]
        fig.add_trace(go.Scatter(
            x=g.unidades, y=g.margen_pct, mode="markers+text", name=cat, text=g.producto,
            textposition=[POS_ETIQUETA.get(p, "middle right") for p in g.producto],
            textfont=dict(size=11.5, color=TINTA_2),
            marker=dict(size=g.ganancia, sizemode="area", sizeref=escala, sizemin=4, color=rgba(CATEGORIA_COL[cat], .55),
                        line=dict(color=CATEGORIA_COL[cat], width=1.5)),
            customdata=np.stack([g.precio, g.ganancia], axis=1),
            hovertemplate="<b>%{text}</b><br>%{x:,.0f} unidades · margen %{y} %<br>Precio $%{customdata[0]:,.0f}"
                          "<br>Ganancia $%{customdata[1]:,.0f}<extra></extra>"))
    estilo(fig, leyenda=True)
    fig.update_xaxes(type="log", title="Unidades vendidas (escala log)", showgrid=True, gridcolor=REJILLA,
                     range=[np.log10(35), np.log10(12000)], tickvals=[100, 300, 1000, 3000, 10000])
    fig.update_yaxes(title="Margen (%)", range=[8, 70], ticksuffix=" %")
    mostrar(fig)
    limite("ganancia estimada como ingreso × margen, sin costos fijos.")

st.write("")

# ──────────────────────────────────────────────────────────────────────────────
# 7. Fila 2 · Clientes (radar) · Entregas (raincloud)
# ──────────────────────────────────────────────────────────────────────────────
c3, c4 = st.columns(2, gap="medium")

with c3, st.container(key="card_clientes"):
    variables = {"compras": "Compras", "gasto_medio": "Gasto por compra", "valor": "Valor por cliente", "edad": "Edad"}
    perfil = clientes.groupby("segmento")[list(variables)].median()
    indice = perfil / perfil.max() * 100                       # 100 = segmento con el valor más alto
    top_s = perfil.loc[segs, "valor"].idxmax()
    encabezado(
        "Perfil de clientes",
        "Cada segmento compra de forma distinta" if len(segs) > 1 else f"Perfil de los clientes {PLURAL[segs[0]]}",
        f"Mediana por segmento (100 = máximo) · mayor valor: <b>{PLURAL[top_s]}</b> "
        f"(${num(perfil.loc[top_s, 'valor'])} por cliente)",
    )
    fig = go.Figure()
    ejes = list(variables.values())
    for s in segs:
        r = list(indice.loc[s]) + [indice.loc[s].iloc[0]]
        reales = list(perfil.loc[s]) + [perfil.loc[s].iloc[0]]
        fig.add_trace(go.Scatterpolar(
            r=r, theta=ejes + [ejes[0]], name=s, fill="toself", fillcolor=rgba(SEGMENTO_COL[s], .14),
            line=dict(color=SEGMENTO_COL[s], width=2.5), marker=dict(size=6), customdata=reales,
            hovertemplate=f"<b>{s}</b><br>%{{theta}}: %{{customdata:,.0f}}<extra></extra>"))
    estilo(fig, leyenda=True)
    fig.update_layout(polar=dict(bgcolor="rgba(0,0,0,0)",
                                 radialaxis=dict(range=[0, 105], showticklabels=False, gridcolor=REJILLA, linecolor=REJILLA),
                                 angularaxis=dict(gridcolor=REJILLA, linecolor=REJILLA,
                                                  tickfont=dict(size=12.5, color=TINTA_2))),
                      legend=dict(orientation="v", x=0, y=1, yanchor="top", xanchor="left"),
                      margin=dict(l=40, r=40, t=36, b=20))
    mostrar(fig)
    limite("el archivo no documenta el criterio de segmentación.")

with c4, st.container(key="card_entregas"):
    cumple = ent.assign(ok=ent.tiempo_horas <= plazo).groupby("tipo")["ok"].mean()
    peor = cumple.idxmin()
    articulo = lambda m: ("el " if m == "Carro" else "la ") + m.lower()
    encabezado(
        "Servicio de entrega",
        f"{articulo(peor).capitalize()} concentra los retrasos" if len(medios) > 1
        else f"{medios[0]}: {pct(cumple[medios[0]])} de entregas a tiempo",
        f"A tiempo con plazo de {num(plazo, 1)} h: "
        + " · ".join(f"{m.lower()} <b>{pct(cumple[m])}</b>" for m in medios),
    )
    orden = [m for m in ["Bicicleta", "Carro", "Moto"] if m in medios]
    fig = go.Figure()
    for m in orden:
        g = ent[ent.tipo == m]
        fig.add_trace(go.Violin(
            x=g.tiempo_horas, y=[m] * len(g), name=m, orientation="h", side="positive", width=1.6,
            line=dict(color=MEDIO_COL[m], width=1.5), fillcolor=rgba(MEDIO_COL[m], .25),
            points="all", pointpos=-0.25, jitter=0.18,
            marker=dict(size=4, color=MEDIO_COL[m], opacity=0.45),
            meanline=dict(visible=False), box=dict(visible=False), spanmode="hard",
            hoveron="points", hovertemplate=f"{m}: %{{x:.1f}} h<extra></extra>"))
        fig.add_annotation(x=1, xref="paper", xshift=10, y=m, yshift=12, text=f"<b>{pct(cumple[m])}</b>",
                           showarrow=False, xanchor="left",
                           font=dict(size=13, color=RIESGO if m == peor and len(medios) > 1 else TINTA))
    fig.add_vline(x=plazo, line=dict(color=TINTA, width=1.5, dash="dash"))
    fig.add_annotation(x=plazo, y=1.0, yref="paper", yanchor="bottom", text=f"plazo {num(plazo, 1)} h",
                       showarrow=False, xanchor="left", xshift=6, font=dict(size=11.5, color=TINTA))
    fig.add_annotation(x=1, xref="paper", xshift=10, y=1.0, yref="paper", yanchor="bottom", text="a tiempo",
                       showarrow=False, xanchor="left", font=dict(size=11, color=TENUE))
    estilo(fig)
    fig.update_layout(margin=dict(r=70), violingap=0.15)
    fig.update_xaxes(title="Horas hasta la entrega", range=[0, 10], dtick=1, showgrid=True, gridcolor=REJILLA)
    fig.update_yaxes(gridcolor="rgba(0,0,0,0)", tickfont=dict(color=TINTA_2, size=13))
    mostrar(fig)
    d_bici = entregas[entregas.tipo == "Bicicleta"].distancia_km.median()
    d_moto = entregas[entregas.tipo == "Moto"].distancia_km.median()
    limite(f"la bicicleta cubre distancias mayores ({num(d_bici, 1)} km frente a {num(d_moto, 1)} km en moto).")

# ──────────────────────────────────────────────────────────────────────────────
# 8. Encabezado, ya con los filtros aplicados
# ──────────────────────────────────────────────────────────────────────────────
a_tiempo = (ent.tiempo_horas <= plazo).mean()
v_tot, p_tot = v.ventas_millones.sum(), v.publicidad_millones.sum()
r24 = anual.loc[2024, "ventas_millones"] / anual.loc[2024, "publicidad_millones"]
delta_v = "año base" if periodo == "2024" else f"▲ {pct(crec_v)} vs 2024"
delta_r = "año base" if periodo == "2024" else f"${num(r24, 1)} en 2024"
banda.markdown(
    f"""
<div class="hero">
  <div>
    <div class="tag">Desempeño comercial · {etiqueta_periodo}</div>
    <h1>Las ventas crecieron {pct(crec_v)} en 2025; la inversión publicitaria, {pct(crec_p)}</h1>
    <p>Ventas, rentabilidad, clientes y servicio de entrega.</p>
  </div>
  <div class="kpis">
    <div class="kpi"><div class="v">${num(v_tot)} M</div><div class="l">Ventas</div><div class="d">{delta_v}</div></div>
    <div class="kpi"><div class="v">${num(v_tot / p_tot, 1)}</div><div class="l">Ventas por $1 de publicidad</div>
      <div class="d">{delta_r}</div></div>
    <div class="kpi"><div class="v">{top_g.producto}</div><div class="l">Mayor ganancia</div>
      <div class="d">${num(top_g.ganancia)}</div></div>
    <div class="kpi"><div class="v">{pct(a_tiempo)}</div><div class="l">Entregas en {num(plazo, 1)} h o menos</div>
      <div class="d">{len(medios)} de 3 medios</div></div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────────────────────────────────────
# 9. Conclusiones (sobre el total de los datos)
# ──────────────────────────────────────────────────────────────────────────────
st.write("")
g_all = productos.loc[productos.ganancia.idxmax()]
bici_ok = (entregas[entregas.tipo == "Bicicleta"].tiempo_horas <= 3).mean()
seg_top = clientes.groupby("segmento").valor.median().idxmax()
html(
    f"""
<div class="cierre">
  <div class="paso"><div class="k">Portafolio</div><b>Gestionar por ganancia, no por volumen</b>
    <span>{g_all.producto} concentra la mayor ganancia estimada.</span></div>
  <div class="paso"><div class="k">Clientes</div><b>Diferenciar la estrategia por segmento</b>
    <span>Los clientes {PLURAL[seg_top]} generan el mayor valor.</span></div>
  <div class="paso"><div class="k">Operación</div><b>Fortalecer la capacidad de entrega</b>
    <span>Solo el {pct(bici_ok)} de las entregas en bicicleta llega en 3 h.</span></div>
</div>
"""
)
