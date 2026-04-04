import streamlit as st
from neo4j import GraphDatabase
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
from pyvis.network import Network
import tempfile
import os

# ─────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────
NEO4J_URI      = "neo4j://127.0.0.1:7687"
NEO4J_USER     = "neo4j"
NEO4J_PASSWORD = "bigdata2025"

st.set_page_config(
    page_title="Caso Penal - Audiencia Legal Colombia",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# CONEXIÓN A NEO4J
# ─────────────────────────────────────────────
@st.cache_resource
def get_driver():
    return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def run_query(query):
    driver = get_driver()
    with driver.session() as session:
        result = session.run(query)
        return [dict(record) for record in result]

# ─────────────────────────────────────────────
# ESTILOS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .chapter-header {
        background: linear-gradient(90deg, #1a1a2e, #16213e);
        border-left: 5px solid #e94560;
        padding: 15px 20px;
        border-radius: 5px;
        margin: 20px 0;
    }
    .chapter-number {
        color: #e94560;
        font-size: 13px;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    .chapter-title {
        color: #ffffff;
        font-size: 26px;
        font-weight: bold;
        margin: 5px 0;
    }
    .chapter-subtitle {
        color: #a0a0b0;
        font-size: 14px;
    }
    .narrative-box {
        background-color: #16213e;
        border-radius: 8px;
        padding: 20px;
        margin: 15px 0;
        border: 1px solid #1f4068;
        color: #d0d0e0;
        font-size: 15px;
        line-height: 1.7;
    }
    .metric-card {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border: 1px solid #e94560;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
    }
    .metric-number {
        color: #e94560;
        font-size: 36px;
        font-weight: bold;
    }
    .metric-label {
        color: #a0a0b0;
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .highlight {
        color: #e94560;
        font-weight: bold;
    }
    .timeline-item {
        border-left: 3px solid #e94560;
        padding: 10px 20px;
        margin: 10px 0;
        background-color: #16213e;
        border-radius: 0 8px 8px 0;
    }
    .timeline-date {
        color: #e94560;
        font-size: 12px;
        font-weight: bold;
    }
    .timeline-text {
        color: #d0d0e0;
        font-size: 14px;
    }
    .verdict-box {
        background: linear-gradient(135deg, #1a0a0a, #2d1010);
        border: 2px solid #e94560;
        border-radius: 10px;
        padding: 25px;
        margin: 20px 0;
        text-align: center;
    }
    .verdict-title {
        color: #e94560;
        font-size: 22px;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 3px;
    }
    .verdict-text {
        color: #ffffff;
        font-size: 16px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚖️ Navegación")
    st.markdown("---")
    capitulo = st.radio("Ir al capítulo:", [
        "📋 Resumen del Caso",
        "👥 Capítulo 1 — Los Actores",
        "🔴 Capítulo 2 — Los Hechos",
        "🔍 Capítulo 3 — La Investigación",
        "🏛️ Capítulo 4 — El Proceso Judicial",
        "⚖️ Capítulo 5 — La Sentencia",
        "🕸️ Grafo Completo"
    ])
    st.markdown("---")
    st.markdown("### 📁 Datos del caso")
    st.markdown("**Radicado:** 110016721202000054")
    st.markdown("**Tribunal:** Superior de Bogotá")
    st.markdown("**Fecha audiencia:** 24 Oct 2025")

# ─────────────────────────────────────────────
# FUNCIONES DE GRAFO
# ─────────────────────────────────────────────
def build_pyvis_graph(nodes_data, rels_data, height="500px"):
    net = Network(height=height, width="100%", bgcolor="#0e1117", font_color="white")
    net.barnes_hut()

    color_map = {
        "Persona":       "#e94560",
        "Organización":  "#0f3460",
        "Lugar":         "#16a085",
        "Delito":        "#c0392b",
        "Norma":         "#8e44ad",
        "Jurisprudencia":"#2980b9",
        "Prueba":        "#f39c12",
        "Actuación":     "#27ae60",
        "Pena":          "#e74c3c",
    }

    added_nodes = set()
    for n in nodes_data:
        nid   = n.get("nodeId", str(n.get("nombre", "")))
        label = n.get("nombre", nid)[:25]
        tipo  = n.get("label", "Otro")
        color = color_map.get(tipo, "#888888")
        if nid not in added_nodes:
            net.add_node(nid, label=label, color=color, title=f"{tipo}: {n.get('nombre','')}")
            added_nodes.add(nid)

    for r in rels_data:
        src = r.get("src")
        dst = r.get("dst")
        rel = r.get("tipo", "RELACIONADO_CON")
        if src in added_nodes and dst in added_nodes:
            net.add_edge(src, dst, label=rel, color="#555555")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode="w", encoding="utf-8") as f:
        net.save_graph(f.name)
        return f.name

# ─────────────────────────────────────────────
# RESUMEN DEL CASO
# ─────────────────────────────────────────────
if capitulo == "📋 Resumen del Caso":
    st.markdown("""
    <div style='text-align:center; padding: 30px 0'>
        <div style='color:#e94560; font-size:13px; letter-spacing:3px; text-transform:uppercase'>Tribunal Superior de Distrito Judicial de Bogotá — Sala Penal</div>
        <div style='color:#ffffff; font-size:38px; font-weight:bold; margin:10px 0'>Caso de Acceso Carnal Violento Agravado</div>
        <div style='color:#a0a0b0; font-size:16px'>Audiencia del 24 de octubre de 2025 · Radicado 110016721202000054</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Métricas generales
    total_nodos = run_query("MATCH (n) RETURN count(n) AS total")[0]["total"]
    total_rels  = run_query("MATCH ()-[r]->() RETURN count(r) AS total")[0]["total"]
    total_personas = run_query("MATCH (n {label:'Persona'}) RETURN count(n) AS total")[0]["total"]
    total_pruebas  = run_query("MATCH (n {label:'Prueba'}) RETURN count(n) AS total")[0]["total"]

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class='metric-card'>
            <div class='metric-number'>{total_nodos}</div>
            <div class='metric-label'>Entidades identificadas</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class='metric-card'>
            <div class='metric-number'>{total_rels}</div>
            <div class='metric-label'>Relaciones extraídas</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class='metric-card'>
            <div class='metric-number'>{total_personas}</div>
            <div class='metric-label'>Personas involucradas</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class='metric-card'>
            <div class='metric-number'>{total_pruebas}</div>
            <div class='metric-label'>Pruebas del caso</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Distribución de nodos
    dist = run_query("MATCH (n) RETURN n.label AS tipo, count(n) AS cantidad ORDER BY cantidad DESC")
    df_dist = pd.DataFrame(dist)
    if not df_dist.empty:
        fig = px.bar(df_dist, x="tipo", y="cantidad",
                     color="cantidad",
                     color_continuous_scale=["#1a1a2e", "#e94560"],
                     title="Distribución de entidades por tipo",
                     template="plotly_dark")
        fig.update_layout(
            plot_bgcolor="#0e1117",
            paper_bgcolor="#0e1117",
            showlegend=False,
            coloraxis_showscale=False
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    <div class='narrative-box'>
    🎙️ <strong>¿De qué trata este caso?</strong><br><br>
    El <span class='highlight'>24 de octubre de 2025</span>, la Sala de Decisión Penal del Tribunal Superior de Bogotá 
    llevó a cabo la audiencia de lectura de la decisión de segunda instancia dentro del proceso penal seguido en contra de 
    <span class='highlight'>Yeison Andrés Chipantasín García</span>, patrullero de la Policía Nacional, 
    por el delito de <span class='highlight'>acceso carnal violento agravado</span> en perjuicio de 
    <span class='highlight'>Nicole Daniela Jiménez Garzón</span>.<br><br>
    Los hechos ocurrieron el <span class='highlight'>13 de enero de 2020</span> al interior del 
    <span class='highlight'>CAI Molinos</span> en Bogotá, cuando la víctima fue retenida y agredida sexualmente 
    por el procesado, quien se aprovechó de su condición de miembro de la fuerza pública y de la autoridad 
    que ejercía sobre sus compañeros y sobre la víctima.
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CAPÍTULO 1 — LOS ACTORES
# ─────────────────────────────────────────────
elif capitulo == "👥 Capítulo 1 — Los Actores":
    st.markdown("""
    <div class='chapter-header'>
        <div class='chapter-number'>Capítulo 1</div>
        <div class='chapter-title'>👥 Los Actores</div>
        <div class='chapter-subtitle'>¿Quiénes participaron en este caso?</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class='narrative-box'>
    En toda audiencia judicial participan distintos actores con roles muy definidos. 
    En este caso confluyen el <span class='highlight'>acusado</span>, la <span class='highlight'>víctima</span>, 
    los <span class='highlight'>operadores de justicia</span> y los <span class='highlight'>testigos</span> 
    que permitieron reconstruir la verdad de los hechos.
    </div>
    """, unsafe_allow_html=True)

    personas = run_query("""
        MATCH (n {label: 'Persona'})
        RETURN n.nodeId AS id, n.nombre AS nombre, n.rol AS rol, n.descripcion AS descripcion
        ORDER BY n.nodeId
    """)
    df_personas = pd.DataFrame(personas)

    if not df_personas.empty:
        # Categorizar
        acusado    = df_personas[df_personas["id"] == "P001"]
        victima    = df_personas[df_personas["id"] == "P002"]
        tribunal   = df_personas[df_personas["id"].isin(["P007","P008","P009"])]
        fiscalia   = df_personas[df_personas["id"].isin(["P003","P004","P005","P006"])]
        testigos   = df_personas[~df_personas["id"].isin(["P001","P002","P003","P004","P005","P006","P007","P008","P009"])]

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 🔴 Acusado")
            if not acusado.empty:
                r = acusado.iloc[0]
                st.markdown(f"""
                <div style='background:#2d1010;border:1px solid #e94560;border-radius:8px;padding:15px'>
                <b style='color:#e94560'>{r['nombre']}</b><br>
                <span style='color:#a0a0b0'>{r['rol']}</span><br>
                <span style='color:#d0d0e0;font-size:13px'>{r['descripcion']}</span>
                </div>""", unsafe_allow_html=True)

            st.markdown("### 🟡 Víctima")
            if not victima.empty:
                r = victima.iloc[0]
                st.markdown(f"""
                <div style='background:#1a2010;border:1px solid #f39c12;border-radius:8px;padding:15px'>
                <b style='color:#f39c12'>{r['nombre']}</b><br>
                <span style='color:#a0a0b0'>{r['rol']}</span><br>
                <span style='color:#d0d0e0;font-size:13px'>{r['descripcion']}</span>
                </div>""", unsafe_allow_html=True)

        with col2:
            st.markdown("### 🏛️ Tribunal")
            for _, r in tribunal.iterrows():
                st.markdown(f"""
                <div style='background:#0a1020;border:1px solid #2980b9;border-radius:8px;padding:12px;margin:5px 0'>
                <b style='color:#2980b9'>{r['nombre']}</b><br>
                <span style='color:#a0a0b0;font-size:13px'>{r['rol']}</span>
                </div>""", unsafe_allow_html=True)

            st.markdown("### ⚖️ Partes procesales")
            for _, r in fiscalia.iterrows():
                st.markdown(f"""
                <div style='background:#0a1020;border:1px solid #27ae60;border-radius:8px;padding:12px;margin:5px 0'>
                <b style='color:#27ae60'>{r['nombre']}</b><br>
                <span style='color:#a0a0b0;font-size:13px'>{r['rol']}</span>
                </div>""", unsafe_allow_html=True)

        st.markdown("### 👁️ Testigos y peritos")
        cols = st.columns(3)
        for i, (_, r) in enumerate(testigos.iterrows()):
            with cols[i % 3]:
                st.markdown(f"""
                <div style='background:#0e1117;border:1px solid #555;border-radius:8px;padding:12px;margin:5px 0'>
                <b style='color:#ffffff'>{r['nombre']}</b><br>
                <span style='color:#a0a0b0;font-size:12px'>{r['rol']}</span>
                </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CAPÍTULO 2 — LOS HECHOS
# ─────────────────────────────────────────────
elif capitulo == "🔴 Capítulo 2 — Los Hechos":
    st.markdown("""
    <div class='chapter-header'>
        <div class='chapter-number'>Capítulo 2</div>
        <div class='chapter-title'>🔴 Los Hechos</div>
        <div class='chapter-subtitle'>13 de enero de 2020 — CAI Molinos, Bogotá</div>
    </div>
    """, unsafe_allow_html=True)

    # Timeline
    st.markdown("### 🕐 Cronología de los hechos")

    timeline = [
        ("~1:30 PM",  "Nicole se encuentra en el Parque Molinos esperando reunirse con su novia Stephanie para asistir a una misa."),
        ("~1:30 PM",  "Un grupo de policías llega al parque y realiza requisas. Encuentran celulares en las maletas de otros presentes. Yeison ordena retener a todos por presunto hurto calificado."),
        ("~2:00 PM",  "Nicole y otras personas son trasladadas en una patrulla al CAI Molinos. Nicole no es registrada en el libro de población pese a que le solicitan su cédula."),
        ("~2:30 PM",  "Yeison, como auxiliar de información y comandante de turno, ordena a sus compañeros salir a patrullar. Queda solo con Nicole al interior del CAI."),
        ("~2:45 PM",  "Yeison lleva a Nicole a un cuarto interior del CAI. Saca un taser del locker, la amenaza, la somete físicamente y la agrede sexualmente."),
        ("~3:30 PM",  "Yeison le venda los ojos a Nicole y la traslada en una patrulla hasta dejarla cerca de la estación Transmilenio Molinos."),
        ("~3:45 PM",  "Nicole llega llorando a la casa de la familia de su novia. No quiere hablar ni comer. Su excuñado David la recogió en Transmilenio."),
        ("14 ene 2020","Al día siguiente, Nicole interpone la denuncia ante la Fiscalía (Formato Único de Noticia Criminal)."),
    ]

    for fecha, evento in timeline:
        st.markdown(f"""
        <div class='timeline-item'>
            <div class='timeline-date'>📅 {fecha}</div>
            <div class='timeline-text'>{evento}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Lugares
    st.markdown("### 📍 Lugares del caso")
    lugares = run_query("MATCH (n {label:'Lugar'}) RETURN n.nombre AS nombre, n.descripcion AS descripcion")
    df_lugares = pd.DataFrame(lugares)
    if not df_lugares.empty:
        for _, r in df_lugares.iterrows():
            st.markdown(f"""
            <div style='background:#16213e;border-left:3px solid #16a085;border-radius:0 8px 8px 0;padding:12px 20px;margin:8px 0'>
            <b style='color:#16a085'>📍 {r['nombre']}</b>
            <span style='color:#a0a0b0;font-size:13px'> — {r['descripcion']}</span>
            </div>""", unsafe_allow_html=True)

    # Delito
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class='narrative-box'>
    ⚠️ <strong>El delito cometido</strong><br><br>
    Yeison Andrés Chipantasín García, en su condición de <span class='highlight'>patrullero y auxiliar de información 
    de la Policía Nacional</span>, utilizó su posición de autoridad para retener a Nicole, 
    aislarla de sus compañeros, amenazarla con un <span class='highlight'>arma taser</span>, 
    someterla físicamente y accederla carnalmente vía vaginal sin su consentimiento.<br><br>
    Durante la agresión profirió expresiones discriminatorias contra la víctima por su 
    <span class='highlight'>orientación sexual</span>, señalando que "tenía que gustarle los hombres".
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CAPÍTULO 3 — LA INVESTIGACIÓN
# ─────────────────────────────────────────────
elif capitulo == "🔍 Capítulo 3 — La Investigación":
    st.markdown("""
    <div class='chapter-header'>
        <div class='chapter-number'>Capítulo 3</div>
        <div class='chapter-title'>🔍 La Investigación</div>
        <div class='chapter-subtitle'>Las pruebas y testimonios que reconstruyeron la verdad</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class='narrative-box'>
    La reconstrucción de los hechos fue posible gracias a una combinación de 
    <span class='highlight'>prueba testimonial</span>, <span class='highlight'>prueba pericial</span> 
    y <span class='highlight'>evidencia documental</span>. Aunque Yeison negó conocer a Nicole, 
    el conjunto probatorio demostró su responsabilidad más allá de toda duda razonable.
    </div>
    """, unsafe_allow_html=True)

    # Pruebas
    st.markdown("### 🗂️ Pruebas del caso")
    pruebas = run_query("MATCH (n {label:'Prueba'}) RETURN n.nombre AS nombre, n.descripcion AS descripcion, n.fecha AS fecha")
    df_pruebas = pd.DataFrame(pruebas)
    if not df_pruebas.empty:
        for _, r in df_pruebas.iterrows():
            st.markdown(f"""
            <div style='background:#16213e;border:1px solid #f39c12;border-radius:8px;padding:15px;margin:8px 0'>
            <b style='color:#f39c12'>📄 {r['nombre']}</b>
            {'<span style="color:#e94560;font-size:12px;margin-left:10px">📅 ' + str(r['fecha']) + '</span>' if r['fecha'] else ''}
            <br><span style='color:#d0d0e0;font-size:13px'>{r['descripcion']}</span>
            </div>""", unsafe_allow_html=True)

    # Testigos
    st.markdown("<br>")
    st.markdown("### 🗣️ Testigos y su aporte al caso")

    testigos_info = [
        ("Nicole Daniela Jiménez Garzón", "Víctima / Testigo principal", "Relató en detalle los hechos: la retención, el traslado al CAI, la agresión sexual y las expresiones discriminatorias del acusado. Su testimonio fue calificado como claro, espontáneo y consistente.", "#e94560"),
        ("Javier Rubio Medina", "Testigo de descargo / Patrullero", "Paradójicamente, su testimonio como testigo de la defensa corroboró que Yeison tenía autoridad sobre sus compañeros y que debía permanecer permanentemente en el CAI.", "#f39c12"),
        ("Andrés Leonardo Ávila Sánchez", "Teniente coronel / Comandante CAI", "Confirmó la descripción del interior del CAI que hizo la víctima, validando que solo alguien que estuvo allí podía conocer esos detalles.", "#27ae60"),
        ("Carlos Enrique Lozano Reyes", "Perito médico forense", "Su informe del 14 de enero de 2020 evidenció lesiones en muñecas y zona genital de Nicole, compatibles con su relato. El agresor usó preservativo y Nicole se bañó, lo que explica ausencia de semen.", "#2980b9"),
        ("Stephanie Geraldine Villarrubio", "Expareja de la víctima", "Testigo del estado emocional devastado de Nicole al llegar a su casa ese día. Confirmó las conversaciones de WhatsApp durante la retención.", "#8e44ad"),
        ("Diarnely Rubio Jiménez", "Madre de Stephanie", "Recibió a Nicole en su casa llorando y retraída. Describió el cambio abrupto en el comportamiento de la joven como prueba del trauma sufrido.", "#16a085"),
    ]

    for nombre, rol, aporte, color in testigos_info:
        st.markdown(f"""
        <div style='background:#0e1117;border-left:4px solid {color};border-radius:0 8px 8px 0;padding:15px 20px;margin:10px 0'>
        <b style='color:{color}'>{nombre}</b> <span style='color:#a0a0b0;font-size:12px'>— {rol}</span><br>
        <span style='color:#d0d0e0;font-size:13px;margin-top:5px;display:block'>{aporte}</span>
        </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CAPÍTULO 4 — EL PROCESO JUDICIAL
# ─────────────────────────────────────────────
elif capitulo == "🏛️ Capítulo 4 — El Proceso Judicial":
    st.markdown("""
    <div class='chapter-header'>
        <div class='chapter-number'>Capítulo 4</div>
        <div class='chapter-title'>🏛️ El Proceso Judicial</div>
        <div class='chapter-subtitle'>El camino desde la denuncia hasta la sentencia de segunda instancia</div>
    </div>
    """, unsafe_allow_html=True)

    # Timeline judicial
    st.markdown("### ⚖️ Línea de tiempo judicial")

    timeline_judicial = [
        ("14 Ene 2020",  "Denuncia",          "Nicole interpone la denuncia ante la Fiscalía. Se inicia la investigación penal."),
        ("13 Oct 2021",  "Reconocimiento",     "Nicole participa en diligencia de reconocimiento fotográfico e identifica a Yeison como su agresor."),
        ("2022-2023",    "Imputación y juicio","Formulación de imputación y acusación. Juicio oral con declaración de Nicole (24 de abril de 2024) y demás testigos."),
        ("6 Jun 2025",   "1ª instancia",       "El Juzgado 58 Penal del Circuito de Bogotá profiere sentencia ABSOLUTORIA. La Fiscalía y el representante de víctimas apelan."),
        ("21 Oct 2025",  "Deliberación",       "La Sala Penal del Tribunal Superior aprueba la decisión de segunda instancia mediante Acta 154."),
        ("24 Oct 2025",  "2ª instancia",       "Audiencia de lectura de la decisión. El Tribunal REVOCA la absolutoria y condena a Yeison a 198 meses de prisión."),
    ]

    for fecha, etapa, desc in timeline_judicial:
        color = "#e94560" if "instancia" in etapa or "instancia" in desc else "#2980b9"
        st.markdown(f"""
        <div style='display:flex;margin:10px 0'>
            <div style='min-width:120px;color:{color};font-weight:bold;font-size:13px;padding-top:3px'>{fecha}</div>
            <div style='width:3px;background:{color};margin:0 15px;border-radius:3px'></div>
            <div style='background:#16213e;border-radius:8px;padding:12px 20px;flex:1'>
                <b style='color:{color}'>{etapa}</b><br>
                <span style='color:#d0d0e0;font-size:13px'>{desc}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Instancias
    st.markdown("<br>")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div style='background:#1a2010;border:2px solid #27ae60;border-radius:10px;padding:20px;text-align:center'>
            <div style='color:#27ae60;font-size:13px;text-transform:uppercase;letter-spacing:2px'>Primera Instancia</div>
            <div style='color:#ffffff;font-size:18px;font-weight:bold;margin:10px 0'>Juzgado 58 Penal del Circuito</div>
            <div style='background:#c0392b;color:white;border-radius:5px;padding:8px;font-weight:bold'>SENTENCIA ABSOLUTORIA</div>
            <div style='color:#a0a0b0;font-size:12px;margin-top:10px'>6 de junio de 2025</div>
            <div style='color:#d0d0e0;font-size:13px;margin-top:10px'>El juez consideró que existían inconsistencias en el relato de la víctima y dudas sobre la responsabilidad del acusado.</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style='background:#2d1010;border:2px solid #e94560;border-radius:10px;padding:20px;text-align:center'>
            <div style='color:#e94560;font-size:13px;text-transform:uppercase;letter-spacing:2px'>Segunda Instancia</div>
            <div style='color:#ffffff;font-size:18px;font-weight:bold;margin:10px 0'>Tribunal Superior de Bogotá</div>
            <div style='background:#27ae60;color:white;border-radius:5px;padding:8px;font-weight:bold'>SENTENCIA CONDENATORIA</div>
            <div style='color:#a0a0b0;font-size:12px;margin-top:10px'>24 de octubre de 2025</div>
            <div style='color:#d0d0e0;font-size:13px;margin-top:10px'>El Tribunal revocó la absolutoria al considerar que la prueba sí era suficiente para condenar y que el juez valoró mal los testimonios.</div>
        </div>
        """, unsafe_allow_html=True)

    # Normas
    st.markdown("<br>")
    st.markdown("### 📜 Marco normativo aplicado")
    normas = run_query("MATCH (n {label:'Norma'}) RETURN n.nombre AS nombre, n.descripcion AS descripcion")
    df_normas = pd.DataFrame(normas)
    if not df_normas.empty:
        for _, r in df_normas.iterrows():
            st.markdown(f"""
            <div style='background:#16213e;border-left:3px solid #8e44ad;padding:10px 20px;margin:6px 0;border-radius:0 5px 5px 0'>
            <b style='color:#8e44ad'>{r['nombre']}</b>
            <span style='color:#d0d0e0;font-size:13px'> — {r['descripcion']}</span>
            </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CAPÍTULO 5 — LA SENTENCIA
# ─────────────────────────────────────────────
elif capitulo == "⚖️ Capítulo 5 — La Sentencia":
    st.markdown("""
    <div class='chapter-header'>
        <div class='chapter-number'>Capítulo 5</div>
        <div class='chapter-title'>⚖️ La Sentencia</div>
        <div class='chapter-subtitle'>La decisión final del Tribunal Superior de Bogotá</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class='verdict-box'>
        <div class='verdict-title'>🔨 Sentencia Condenatoria</div>
        <div class='verdict-text'>Yeison Andrés Chipantasín García</div>
        <div style='color:#a0a0b0;font-size:14px'>CC 80.774.139 — Bogotá</div>
        <div style='color:#e94560;font-size:20px;font-weight:bold;margin:15px 0'>CULPABLE</div>
        <div class='verdict-text'>Acceso carnal violento agravado</div>
        <div style='color:#a0a0b0;font-size:13px'>Arts. 205 y 211 num. 2 del Código Penal</div>
    </div>
    """, unsafe_allow_html=True)

    # Penas
    st.markdown("### 🔒 Penas impuestas")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class='metric-card'>
            <div class='metric-number'>198</div>
            <div style='color:#e94560;font-size:16px'>meses de prisión</div>
            <div class='metric-label'>≈ 16.5 años</div>
            <div style='color:#d0d0e0;font-size:13px;margin-top:10px'>Pena principal privativa de libertad</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class='metric-card'>
            <div class='metric-number'>198</div>
            <div style='color:#e94560;font-size:16px'>meses de inhabilitación</div>
            <div class='metric-label'>Derechos y funciones públicas</div>
            <div style='color:#d0d0e0;font-size:13px;margin-top:10px'>Pena accesoria — mismo término que la pena principal</div>
        </div>
        """, unsafe_allow_html=True)

    # Resolutiva
    st.markdown("<br>")
    st.markdown("### 📋 Parte resolutiva")
    resolutiva = [
        ("Primero",  "REVOCAR la sentencia absolutoria proferida el 6 de junio de 2025 por el Juzgado 58 Penal del Circuito de Bogotá."),
        ("Segundo",  "CONDENAR a Yeison Andrés Chipantasín García como autor responsable del delito de acceso carnal violento agravado (Arts. 205 y 211 num. 2 C.P.)."),
        ("Tercero",  "IMPONER pena de 198 meses de prisión e inhabilitación para el ejercicio de derechos y funciones públicas por el mismo término."),
        ("Cuarto",   "NEGAR la suspensión condicional de la pena y la prisión domiciliaria."),
        ("Quinto",   "Una vez en firme, librar ORDEN DE CAPTURA a través del Centro de Servicios Judiciales del Sistema Penal Acusatorio de Bogotá."),
        ("Sexto",    "El INPEC determinará el establecimiento carcelario donde se cumplirá la condena."),
        ("Séptimo",  "Compulsar copias para que la Fiscalía investigue si Yeison incurrió en el delito de privación ilegal de la libertad de la víctima."),
    ]
    for num, texto in resolutiva:
        st.markdown(f"""
        <div style='background:#16213e;border-radius:8px;padding:12px 20px;margin:8px 0;display:flex;gap:15px'>
            <span style='color:#e94560;font-weight:bold;min-width:70px'>{num}:</span>
            <span style='color:#d0d0e0;font-size:14px'>{texto}</span>
        </div>""", unsafe_allow_html=True)

    # Agravantes
    st.markdown("<br>")
    st.markdown("""
    <div class='narrative-box'>
    ⚠️ <strong>Circunstancias agravantes consideradas por el Tribunal</strong><br><br>
    1. <span class='highlight'>Condición de miembro de la Policía Nacional:</span> Yeison ostentaba una posición de autoridad que generó en la víctima un estado de sujeción y confianza, aprovechada para cometer el delito.<br><br>
    2. <span class='highlight'>Discriminación por orientación sexual:</span> El acusado usó la violencia como un "correctivo" ante la orientación sexual diversa de la víctima, lo que reviste el hecho de mayor gravedad.<br><br>
    3. <span class='highlight'>Abuso de poder institucional:</span> La CIDH ha señalado que la violación sexual de una mujer detenida por un agente del Estado es especialmente grave por la vulnerabilidad de la víctima.
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# GRAFO COMPLETO
# ─────────────────────────────────────────────
elif capitulo == "🕸️ Grafo Completo":
    st.markdown("""
    <div class='chapter-header'>
        <div class='chapter-number'>Visualización</div>
        <div class='chapter-title'>🕸️ Grafo Completo del Caso</div>
        <div class='chapter-subtitle'>Red completa de entidades y relaciones extraídas de la audiencia</div>
    </div>
    """, unsafe_allow_html=True)

    # Filtro
    tipos = ["Todos", "Persona", "Organización", "Lugar", "Delito", "Prueba", "Norma", "Actuación"]
    filtro = st.selectbox("Filtrar por tipo de entidad:", tipos)

    if filtro == "Todos":
        query_nodes = "MATCH (n) RETURN n.nodeId AS nodeId, n.nombre AS nombre, n.label AS label"
        query_rels  = "MATCH (a)-[r]->(b) RETURN a.nodeId AS src, b.nodeId AS dst, r.tipo AS tipo"
    else:
        query_nodes = f"MATCH (n {{label:'{filtro}'}}) RETURN n.nodeId AS nodeId, n.nombre AS nombre, n.label AS label"
        query_rels  = f"""
            MATCH (a)-[r]->(b)
            WHERE a.label = '{filtro}' OR b.label = '{filtro}'
            RETURN a.nodeId AS src, b.nodeId AS dst, r.tipo AS tipo
        """

    nodes_data = run_query(query_nodes)
    rels_data  = run_query(query_rels)

    if nodes_data:
        html_file = build_pyvis_graph(nodes_data, rels_data, height="600px")
        with open(html_file, "r", encoding="utf-8") as f:
            html_content = f.read()
        st.components.v1.html(html_content, height=620, scrolling=False)
        os.unlink(html_file)

    # Leyenda
    st.markdown("### 🎨 Leyenda de colores")
    leyenda = [
        ("#e94560", "Persona"),
        ("#0f3460", "Organización"),
        ("#16a085", "Lugar"),
        ("#c0392b", "Delito"),
        ("#8e44ad", "Norma"),
        ("#2980b9", "Jurisprudencia"),
        ("#f39c12", "Prueba"),
        ("#27ae60", "Actuación"),
    ]
    cols = st.columns(len(leyenda))
    for col, (color, nombre) in zip(cols, leyenda):
        with col:
            st.markdown(f"""
            <div style='text-align:center'>
                <div style='width:20px;height:20px;background:{color};border-radius:50%;margin:0 auto'></div>
                <div style='color:#a0a0b0;font-size:12px;margin-top:5px'>{nombre}</div>
            </div>""", unsafe_allow_html=True)