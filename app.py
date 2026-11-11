"""
Tarea Streamlit · Herramientas de Visualización
================================================

Informe de desempeño comercial en formato de tablero (una sola pantalla),
construido con los datos de práctica del curso. Cuatro secciones, cada una
con un gráfico del catálogo de clase:

    Sección                       Archivo                    Gráfico del catálogo
    1. Ventas y publicidad ...... 01_ventas_mensuales.csv .. 2 · Línea
    2. Rentabilidad ............. 05_productos.csv ......... 3 · Barras ordenadas
    3. Perfil de clientes ....... 03_clientes.csv .......... 8 · Paneles (barras por segmento)
    4. Nivel de servicio ........ 04_entregas.csv .......... 5 · Boxplot

(02_clientes_por_ciudad_canal.csv no se usa: no aporta al mensaje del informe.)

Híbrido informe + tablero: la barra de filtros (periodo, categoría, segmento y
medio de entrega) recalcula indicadores, gráficos y títulos; los títulos se
reescriben para que la afirmación siga siendo cierta con la selección.

Reglas de cada gráfico (reto del PDF de la clase)
    - El título afirma un hallazgo verificable.
    - Cada sección cierra con una limitación: lo que los datos no permiten concluir.
    - Sin doble eje (índice base 100); ingreso = precio × unidades;
      misma escala entre grupos en paneles y boxplot.

Ejecutar:  python -m streamlit run app.py
"""

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

# ──────────────────────────────────────────────────────────────────────────────
# 1. Configuración, paleta y estilo
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Desempeño comercial 2024–2025", page_icon="📊", layout="wide",
                   initial_sidebar_state="collapsed")

DATA = Path(__file__).parent / "data"

# Paleta corporativa: azul marino para la marca, azul acero para el dato
# principal, rojo vino solo para señalar riesgos y grises para el contexto.
FONDO = "#F5F6F8"
TINTA = "#111827"
TINTA_2 = "#4B5563"
TENUE = "#9CA3AF"
REJILLA = "#E5E7EB"
CONTEXTO = "#CBD3DC"
MARINO = "#0B2545"
PRIMARIO = "#1D4E89"
VERDE = "#3E8E7E"
OCRE = "#C99A2E"
RIESGO = "#B23A48"
SEGMENTO_COL = {"Frecuente": PRIMARIO, "Regular": VERDE, "Ocasional": OCRE}
MEDIO_COL = {"Moto": PRIMARIO, "Carro": CONTEXTO, "Bicicleta": RIESGO}
FUENTE = "'Plus Jakarta Sans', 'Segoe UI', sans-serif"
PLOT_CONFIG = {"displayModeBar": False}

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
.hero {{ background: {MARINO}; border-radius: 16px; padding: 2rem 2.4rem; color: #fff;
        display: grid; grid-template-columns: minmax(0, 1.25fr) minmax(0, 1fr); gap: 2.4rem; align-items: center;
        border-bottom: 4px solid {OCRE}; }}
.hero .tag {{ font-size: .74rem; letter-spacing: .14em; text-transform: uppercase; color: #9FB3C8; font-weight: 600; }}
.hero h1 {{ font-family: {FUENTE}; font-weight: 700; font-size: clamp(1.55rem, 2.3vw, 2.25rem); line-height: 1.2;
           color: #fff !important; margin: .55rem 0 .8rem 0; padding: 0; letter-spacing: -.015em; }}
.hero p {{ color: #C9D6E3 !important; font-size: .98rem; line-height: 1.6; margin: 0; max-width: 42rem; }}
.kpis {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }}
.kpi {{ background: rgba(255,255,255,.06); border: 1px solid rgba(255,255,255,.12); border-radius: 12px; padding: 14px 16px; }}
.kpi .v {{ font-weight: 700; font-size: clamp(1.4rem, 2vw, 1.95rem); line-height: 1.05; color: #fff; white-space: nowrap; }}
.kpi .l {{ font-size: .8rem; color: #9FB3C8; margin-top: 5px; line-height: 1.35; }}
.kpi .d {{ display: inline-block; font-size: .74rem; font-weight: 600; margin-top: 8px; color: #E3C77A; }}
@media (max-width: 900px) {{ .hero {{ grid-template-columns: 1fr; }} }}

/* Tarjetas */
[class*="st-key-card"] {{ background: #fff; border-radius: 14px; padding: 1.3rem 1.5rem 1rem 1.5rem;
                          box-shadow: 0 1px 2px rgba(17,24,39,.04), 0 6px 18px rgba(17,24,39,.05);
                          border: 1px solid #ECEEF1; }}
.chip {{ font-size: .72rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; color: {PRIMARIO}; }}
.titulo {{ font-weight: 700; font-size: 1.22rem; line-height: 1.3; color: {TINTA}; margin: .4rem 0 .35rem 0; letter-spacing: -.01em; }}
.texto {{ color: {TINTA_2}; font-size: .92rem; line-height: 1.6; margin: 0 0 .2rem 0; }}
.texto b {{ color: {TINTA}; font-weight: 600; }}
.cap {{ color: {TENUE}; font-size: .78rem; margin: .4rem 0 -.6rem 0; }}
.limite {{ color: {TENUE}; font-size: .79rem; line-height: 1.5; border-top: 1px solid {REJILLA}; padding-top: .6rem; margin: 0; }}
.limite b {{ color: {TINTA_2}; font-weight: 600; }}

/* Filtros y controles */
.st-key-card_filtros {{ padding: 1rem 1.5rem .7rem 1.5rem !important; }}
[data-testid="stWidgetLabel"] p {{ font-size: .72rem !important; font-weight: 700 !important; letter-spacing: .1em;
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
.concl-t {{ font-size: .72rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; color: {PRIMARIO}; margin: .2rem 0 .7rem 0; }}
.cierre {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16px; }}
.paso {{ background: #fff; border-radius: 14px; padding: 1.1rem 1.3rem; border: 1px solid #ECEEF1;
        border-top: 3px solid {PRIMARIO}; box-shadow: 0 6px 18px rgba(17,24,39,.04); }}
.paso b {{ display: block; font-size: .97rem; margin-bottom: 4px; color: {TINTA}; }}
.paso span {{ color: {TINTA_2}; font-size: .88rem; line-height: 1.5; }}
@media (max-width: 900px) {{ .cierre {{ grid-template-columns: 1fr; }} }}
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
    return f"{num(x * 100, dec)} %"  # espacio que no se rompe entre número y %


def signo(x: float, dec: int = 0) -> str:
    return ("+" if x >= 0 else "−") + num(abs(x), dec)


def html(s: str) -> None:
    st.markdown(s, unsafe_allow_html=True)


def encabezado(chip: str, titulo: str, texto: str) -> None:
    html(f'<div class="chip">{chip}</div><div class="titulo">{titulo}</div><p class="texto">{texto}</p>')


def limite(t: str) -> None:
    html(f'<p class="limite"><b>Limitación:</b> {t}</p>')


def con_articulo(medio: str) -> str:
    return ("el " if medio == "Carro" else "la ") + medio.lower()


def estilo(fig: go.Figure, alto: int = 330, leyenda: bool = False) -> go.Figure:
    """Plantilla común para todos los gráficos."""
    fig.update_layout(
        template="plotly_white", height=alto, margin=dict(l=4, r=12, t=12, b=4),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FUENTE, size=12.5, color=TINTA_2), showlegend=leyenda,
        hoverlabel=dict(bgcolor=TINTA, bordercolor=TINTA, font=dict(family=FUENTE, size=12.5, color="#fff")),
        legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="left", x=0, title=None, font=dict(size=12)),
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
# 4. Encabezado (se reserva el espacio y se llena al final, con los filtros ya
#    aplicados, para que los indicadores respondan a ellos)
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
DEFAULTS = {"f_periodo": PERIODOS[0], "f_cat": CATEGORIAS, "f_seg": SEGMENTOS, "f_medio": MEDIOS,
            "promesa": 3.0}
for k, val in DEFAULTS.items():
    st.session_state.setdefault(k, val)


def limpiar_filtros() -> None:
    for k, v in DEFAULTS.items():
        st.session_state[k] = v


with st.container(key="card_filtros"):
    f1, f2, f3, f4, f5 = st.columns([1.5, 2, 2, 1.8, 1], gap="medium", vertical_alignment="bottom")
    with f1:
        periodo = st.segmented_control("Periodo", PERIODOS, key="f_periodo") or PERIODOS[0]
    with f2:
        cats = st.pills("Categoría de producto", CATEGORIAS, selection_mode="multi", key="f_cat")
    with f3:
        segs = st.pills("Segmento de cliente", SEGMENTOS, selection_mode="multi", key="f_seg")
    with f4:
        medios = st.pills("Medio de entrega", MEDIOS, selection_mode="multi", key="f_medio")
    with f5:
        st.button("Restablecer", icon=":material/restart_alt:", key="limpiar", on_click=limpiar_filtros,
                  use_container_width=True)

# Una selección vacía se interpreta como "todos", para que el tablero nunca quede en blanco.
cats = cats or CATEGORIAS
segs = [s for s in SEGMENTOS if s in (segs or SEGMENTOS)]
medios = [m for m in MEDIOS if m in (medios or MEDIOS)]
etiqueta_periodo = "2024 – 2025" if periodo == "Todo" else periodo

v = ventas if periodo == "Todo" else ventas[ventas.anio == int(periodo)]
v = v.assign(Ventas=v.ventas_millones / v.ventas_millones.iloc[0] * 100,           # índice rebasado al
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
# 6. Fila 1 · Ventas y publicidad (línea) · Rentabilidad (barras ordenadas)
# ──────────────────────────────────────────────────────────────────────────────
c1, c2 = st.columns([1.15, 1], gap="medium")

with c1, st.container(key="card_crecimiento"):
    ini, ult = v.iloc[0], v.iloc[-1]
    brecha = (ult.Ventas - 100) - (ult.Publicidad - 100)
    titulo = ("Las ventas crecieron a un ritmo superior al de la inversión publicitaria" if brecha > 10
              else "Las ventas y la inversión publicitaria evolucionaron a un ritmo similar")
    encabezado(
        "01 · Ventas y publicidad",
        titulo,
        f"Entre {ini.mes} y {ult.mes}, las ventas mensuales variaron <b>{signo(ult.Ventas - 100)}&nbsp;%</b> y la "
        f"inversión publicitaria <b>{signo(ult.Publicidad - 100)}&nbsp;%</b>. Ambas series se expresan como índice "
        f"(base {ini.mes} = 100) para comparar su evolución en una misma escala.",
    )
    largo = v.melt(id_vars=["mes"], value_vars=["Ventas", "Publicidad"], var_name="Serie", value_name="Índice")
    largo["M"] = np.r_[v.ventas_millones, v.publicidad_millones]  # mismo orden que melt
    fig = px.line(largo, x="mes", y="Índice", color="Serie", markers=len(v) <= 12, custom_data=["M"],
                  color_discrete_map={"Ventas": PRIMARIO, "Publicidad": TENUE})
    fig.update_traces(line=dict(width=2.75),
                      hovertemplate="%{y:.0f}  ($%{customdata[0]:.1f} M)<extra>%{fullData.name}</extra>")
    fig.update_traces(selector=dict(name="Ventas"), fill="tozeroy", fillcolor="rgba(29,78,137,.07)")
    fig.add_hline(y=100, line=dict(color=TENUE, width=1, dash="dot"))
    for serie, color in [("Ventas", PRIMARIO), ("Publicidad", TINTA_2)]:
        fig.add_annotation(x=ult.mes, y=ult[serie], text=f"<b>{serie} {num(ult[serie])}</b>", showarrow=False,
                           xanchor="left", xshift=8, font=dict(color=color, size=12.5))
    estilo(fig, 330)
    paso = 3 if len(v) > 12 else 2
    fig.update_layout(hovermode="x unified", margin=dict(r=110))
    fig.update_xaxes(title=None, tickvals=list(v.mes[::paso]), ticktext=[m.replace(" ", "<br>") for m in v.mes[::paso]])
    techo = max(v.Ventas.max(), v.Publicidad.max())
    piso = min(80, v[["Ventas", "Publicidad"]].min().min() - 5)
    fig.update_yaxes(title=f"Índice (base {ini.mes} = 100)", range=[piso, techo * 1.07])
    mostrar(fig)
    limite("la relación entre ambas series no demuestra causalidad; el análisis no controla cambios de precios "
           "ni otras acciones comerciales.")

with c2, st.container(key="card_ganancia"):
    n = len(prod)
    puesto = int(prod.ganancia.rank(ascending=False)[mas_vendido.name])
    if mas_vendido.name != top_g.name:
        titulo = "El producto de mayor volumen no es el de mayor ganancia"
        texto = (f"El <b>{mas_vendido.producto.lower()}</b> registra el mayor volumen ({num(mas_vendido.unidades)} "
                 f"unidades), pero ocupa el puesto {puesto} de {n} en ganancia. El <b>{top_g.producto.lower()}</b> "
                 f"genera la mayor ganancia estimada (${num(top_g.ganancia)}).")
    else:
        titulo = f"El {top_g.producto.lower()} lidera en volumen y en ganancia dentro de la selección"
        texto = (f"En {', '.join(cats).lower()}, el <b>{top_g.producto.lower()}</b> registra a la vez el mayor "
                 f"volumen y la mayor ganancia estimada (${num(top_g.ganancia)}).")
    encabezado("02 · Rentabilidad del portafolio", titulo, texto)
    metrica = st.segmented_control("Ordenar por", ["Ganancia", "Ingreso", "Unidades"], default="Ganancia",
                                   key="metrica", label_visibility="collapsed") or "Ganancia"
    col = {"Ganancia": "ganancia", "Ingreso": "ingreso", "Unidades": "unidades"}[metrica]
    d = prod.sort_values(col).copy()
    d["Rol"] = np.where(d.index == top_g.name, "Mayor ganancia",
                        np.where(d.index == mas_vendido.name, "Mayor volumen", "Resto"))
    pref = "" if col == "unidades" else "$"
    fig = px.bar(d, x=col, y="producto", orientation="h", color="Rol", text=[pref + num(x) for x in d[col]],
                 color_discrete_map={"Mayor ganancia": PRIMARIO, "Mayor volumen": OCRE, "Resto": CONTEXTO},
                 category_orders={"Rol": ["Mayor ganancia", "Mayor volumen", "Resto"]},
                 custom_data=["precio", "unidades", "margen_pct", "ganancia", "categoria"])
    fig.update_traces(textposition="outside", cliponaxis=False, textfont=dict(size=11.5, color=TINTA_2),
                      marker_cornerradius=3,
                      hovertemplate="<b>%{y}</b> · %{customdata[4]}<br>$%{customdata[0]:,.0f} × %{customdata[1]:,.0f} u × "
                                    "%{customdata[2]} %<br>Ganancia $%{customdata[3]:,.0f}<extra></extra>")
    estilo(fig, 318, leyenda=True)
    fig.update_layout(bargap=0.3)
    fig.update_yaxes(title=None, categoryorder="array", categoryarray=list(d.producto), gridcolor="rgba(0,0,0,0)",
                     tickfont=dict(color=TINTA_2))
    fig.update_xaxes(visible=False, range=[0, d[col].max() * 1.2])
    mostrar(fig)
    limite("la ganancia es una estimación (precio × unidades × margen) que no incluye costos fijos "
           "ni un periodo de referencia.")

st.write("")

# ──────────────────────────────────────────────────────────────────────────────
# 7. Fila 2 · Perfil de clientes (paneles de barras) · Nivel de servicio (boxplot)
# ──────────────────────────────────────────────────────────────────────────────
c3, c4 = st.columns([1.15, 1], gap="medium")

with c3, st.container(key="card_clientes"):
    res = (cli.groupby("segmento")
              .agg(compras=("compras", "median"), gasto=("gasto_medio", "median"), valor=("valor", "median"),
                   n=("cliente", "count"))
              .reindex(segs))
    top_s = res.valor.idxmax()
    plural = {"Frecuente": "frecuentes", "Regular": "regulares", "Ocasional": "ocasionales"}
    if len(segs) > 1:
        titulo = f"Los clientes {plural[top_s]} generan el mayor valor por cliente"
    else:
        titulo = f"Perfil de los clientes {plural[top_s]}"
    detalle = "; ".join(f"los {plural[s]} realizan {num(r.compras)} compras de ${num(r.gasto)}"
                        for s, r in res.iterrows())
    encabezado(
        "03 · Perfil de clientes",
        titulo,
        f"Frecuencia y gasto por compra varían de forma marcada entre segmentos: {detalle} (valores medianos). "
        f"El resultado es un valor mediano de <b>${num(res.loc[top_s, 'valor'])}</b> por cliente en el segmento "
        f"{top_s.lower()}.",
    )
    html('<p class="cap">Mediana por segmento · misma escala dentro de cada panel</p>')
    paneles = [("compras", "Compras por cliente", ""), ("gasto", "Gasto por compra", "$"),
               ("valor", "Valor por cliente", "$")]
    fig = make_subplots(rows=1, cols=3, subplot_titles=[t for _, t, _ in paneles], horizontal_spacing=0.06)
    for j, (col, nombre, pref) in enumerate(paneles, start=1):
        fig.add_trace(go.Bar(
            x=res.index, y=res[col], marker=dict(color=[SEGMENTO_COL[s] for s in res.index], cornerradius=3),
            text=[pref + num(x) for x in res[col]], textposition="outside", cliponaxis=False,
            textfont=dict(size=12.5, color=TINTA), width=0.62, customdata=res["n"],
            hovertemplate=f"<b>%{{x}}</b><br>{nombre}: {pref}%{{y:,.0f}}<br>%{{customdata}} clientes<extra></extra>"),
            1, j)
        fig.update_yaxes(range=[0, res[col].max() * 1.22], visible=False, row=1, col=j)
    estilo(fig, 300)
    fig.update_layout(margin=dict(t=34), bargap=0.25)
    fig.update_annotations(font=dict(size=12.5, color=TINTA_2))
    fig.update_xaxes(tickfont=dict(color=TINTA_2, size=12), linecolor=REJILLA)
    mostrar(fig)
    limite("se desconoce el criterio con el que el archivo asigna los segmentos, y el valor por cliente "
           "(compras × gasto medio) no descuenta costos.")

with c4, st.container(key="card_entrega"):
    promesa = st.session_state["promesa"]
    cumple = ent.assign(ok=ent.tiempo_horas <= promesa).groupby("tipo")["ok"].mean()
    med = ent.groupby("tipo")["tiempo_horas"].median()
    mejor, peor = cumple.idxmax(), cumple.idxmin()
    if len(medios) > 1:
        titulo = f"{con_articulo(peor).capitalize()} presenta el menor nivel de cumplimiento en las entregas"
        texto = (f"Con un plazo de <b>{num(promesa, 1)} h</b>, se cumple a tiempo el <b>{pct(cumple[mejor])}</b> de "
                 f"las entregas en {mejor.lower()}, frente al <b>{pct(cumple[peor])}</b> en {peor.lower()}, cuyo "
                 f"tiempo mediano es de {num(med[peor], 1)} h.")
    else:
        titulo = f"Entregas en {medios[0].lower()}: {pct(cumple[medios[0]])} dentro del plazo"
        texto = (f"Con un plazo de <b>{num(promesa, 1)} h</b>, el tiempo mediano de entrega es de "
                 f"{num(med[medios[0]], 1)} h.")
    encabezado("04 · Nivel de servicio en entregas", titulo, texto)
    st.slider("Plazo de entrega (horas)", 1.0, 8.0, step=0.5, key="promesa")
    orden = [m for m in ["Bicicleta", "Carro", "Moto"] if m in medios]
    fig = px.box(ent, x="tiempo_horas", y="tipo", color="tipo", color_discrete_map=MEDIO_COL,
                 category_orders={"tipo": orden}, points="all")
    fig.update_traces(marker=dict(size=4, opacity=0.35), jitter=0.35, pointpos=0, line=dict(width=2),
                      fillcolor="rgba(255,255,255,0)", hovertemplate="%{y}: %{x:.1f} h<extra></extra>")
    fig.add_vline(x=promesa, line=dict(color=TINTA, width=1.5, dash="dash"))
    fig.add_annotation(x=promesa, y=1.02, yref="paper", text=f"plazo {num(promesa, 1)} h", showarrow=False,
                       xanchor="left", xshift=6, font=dict(size=11.5, color=TINTA))
    for t in orden:
        fig.add_annotation(x=1, xref="paper", xshift=10, y=t, text=f"<b>{pct(cumple[t])}</b> a tiempo",
                           showarrow=False, xanchor="left",
                           font=dict(size=12, color=RIESGO if t == peor and len(medios) > 1 else TINTA_2))
    estilo(fig, 90 + 58 * len(orden))
    fig.update_layout(margin=dict(r=110, t=24))
    fig.update_xaxes(title="Horas hasta la entrega", range=[0, 10], dtick=1, showgrid=True, gridcolor=REJILLA)
    fig.update_yaxes(title=None, gridcolor="rgba(0,0,0,0)", tickfont=dict(color=TINTA_2, size=13))
    mostrar(fig)
    d_bici = entregas[entregas.tipo == "Bicicleta"].distancia_km.median()
    d_moto = entregas[entregas.tipo == "Moto"].distancia_km.median()
    limite(f"las diferencias no se pueden atribuir solo al medio de transporte: la bicicleta atiende recorridos "
           f"más largos ({num(d_bici, 1)} km de mediana frente a {num(d_moto, 1)} km en moto).")

# ──────────────────────────────────────────────────────────────────────────────
# 8. Encabezado, ya con los filtros aplicados
# ──────────────────────────────────────────────────────────────────────────────
a_tiempo = (ent.tiempo_horas <= promesa).mean()
v_tot, p_tot = v.ventas_millones.sum(), v.publicidad_millones.sum()
if periodo == "2024":
    delta_v, delta_r = "Año base de la serie", "Año base de la serie"
else:
    r24 = anual.loc[2024, "ventas_millones"] / anual.loc[2024, "publicidad_millones"]
    delta_v = f"▲ {pct(crec_v)} en 2025 frente a 2024"
    delta_r = f"${num(r24, 1)} en 2024"
banda.markdown(
    f"""
<div class="hero">
  <div>
    <div class="tag">Informe de desempeño comercial · {etiqueta_periodo}</div>
    <h1>Las ventas crecieron {pct(crec_v)} en 2025, frente a un aumento de {pct(crec_p)} en la inversión publicitaria</h1>
    <p>Este tablero resume la evolución de las ventas, la rentabilidad del portafolio, el perfil de los clientes
    y el nivel de servicio en las entregas. Los filtros permiten analizar cada dimensión por periodo,
    categoría, segmento y medio de entrega.</p>
  </div>
  <div class="kpis">
    <div class="kpi"><div class="v">${num(v_tot)} M</div>
      <div class="l">Ventas acumuladas · {etiqueta_periodo}</div><span class="d">{delta_v}</span></div>
    <div class="kpi"><div class="v">${num(v_tot / p_tot, 1)}</div>
      <div class="l">Ventas por cada $1 invertido en publicidad</div><span class="d">{delta_r}</span></div>
    <div class="kpi"><div class="v">{top_g.producto}</div>
      <div class="l">Producto con mayor ganancia estimada</div><span class="d">${num(top_g.ganancia)}</span></div>
    <div class="kpi"><div class="v">{pct(a_tiempo)}</div>
      <div class="l">Entregas dentro del plazo de {num(promesa, 1)} h</div><span class="d">{', '.join(medios)}</span></div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────────────────────────────────────
# 9. Conclusiones (sobre el total de los datos; no cambian con los filtros)
# ──────────────────────────────────────────────────────────────────────────────
st.write("")
g_all = productos.loc[productos.ganancia.idxmax()]
bici_ok = (entregas[entregas.tipo == "Bicicleta"].tiempo_horas <= 3).mean()
seg_top = clientes.groupby("segmento").valor.median().idxmax()
html(
    f"""
<div class="concl-t">Conclusiones</div>
<div class="cierre">
  <div class="paso"><b>Gestionar el portafolio por ganancia</b>
    <span>El volumen de unidades no refleja la contribución de cada producto; el {g_all.producto.lower()}
    concentra la mayor ganancia estimada.</span></div>
  <div class="paso"><b>Diferenciar la estrategia por segmento</b>
    <span>La frecuencia de compra y el gasto por compra difieren entre segmentos; los clientes
    {plural[seg_top]} generan el mayor valor por cliente.</span></div>
  <div class="paso"><b>Fortalecer la capacidad de entrega</b>
    <span>Solo el {pct(bici_ok)} de las entregas en bicicleta se cumple en 3 horas; es el principal riesgo
    operativo ante un mayor volumen de pedidos.</span></div>
</div>
"""
)
