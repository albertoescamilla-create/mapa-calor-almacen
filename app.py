import streamlit as st

from config import TITULO_APP
from data import cargar_csv
from metrics import (
    calcular_kpis,
    calcular_percentiles,
    resumen_racks,
    detectar_doble_palets
)
from heatmap import dibujar_heatmap
from pdf import LibroPasillo
from rack import mostrar_rack
from layout import LAYOUT


# ==========================================
# CONFIGURACIÓN
# ==========================================

st.set_page_config(
    page_title=TITULO_APP,
    page_icon="🔥",
    layout="wide"
)

st.title(TITULO_APP)

st.caption("Versión 1.0.0")

with st.sidebar:
    st.divider()
    st.caption("Mapa de Calor del Almacén")
    st.caption("v1.0.0")
    st.caption("© Julio 2026")
    st.caption("Desarrollado por Alberto Escamilla")

# ==========================================
# SESSION STATE
# ==========================================

if "rack_seleccionado" not in st.session_state:
    st.session_state["rack_seleccionado"] = None

# ==========================================
# SUBIR CSV
# ==========================================

archivo = st.file_uploader(
    "Selecciona el CSV exportado desde Power BI",
    type=["csv"]
)

if archivo is None:
    st.info("Sube un archivo CSV para comenzar.")
    st.stop()

# ==========================================
# LEER CSV
# ==========================================

try:
    df = cargar_csv(archivo)
    # Excluir altura de picking
    df = df[df["altura"] != "10"].copy()

except Exception as e:
    st.error(str(e))
    st.stop()

# ==========================================
# CALCULAR DATOS
# ==========================================

kpis = calcular_kpis(df)

p25, p50, p75 = calcular_percentiles(df)

resumen = resumen_racks(df)

dobles = detectar_doble_palets(df)

# ==========================================
# KPIs
# ==========================================

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric(
    "📦 Palets",
    kpis["palets"]
)

c2.metric(
    "⏳ Edad media",
    f'{kpis["edad_media"]} días'
)

c3.metric(
    "🚨 Rack crítico",
    kpis["rack_critico"]
)

c4.metric(
    "🔥 >90 días",
    kpis["mas_90"]
)

c5.metric(
    "⚠️ Dobles ubicaciones",
    len(dobles)
)

st.divider()

# ==========================================
# INCIDENCIAS
# ==========================================

if not dobles.empty:

    with st.expander(
        f"⚠️ Ver {len(dobles)} dobles ubicaciones"
    ):

        st.dataframe(
            dobles,
            hide_index=True,
            use_container_width=True
        )

# ==========================================
# LEYENDA
# ==========================================

st.subheader("Leyenda")

l1, l2, l3, l4 = st.columns(4)

l1.metric("🟢 Verde", f"≤ {int(p25)} días")
l2.metric("🟡 Amarillo", f"{int(p25)+1}-{int(p50)}")
l3.metric("🟠 Naranja", f"{int(p50)+1}-{int(p75)}")
l4.metric("🔴 Rojo", f"> {int(p75)} días")

st.divider()

# ==========================================
# PASILLO
# ==========================================

pasillos = sorted(df["pasillo_completo"].unique())

pasillo = st.selectbox(
    "Selecciona un pasillo",
    pasillos
)

resumen_pasillo = resumen[
    resumen["pasillo_completo"] == pasillo
].copy()

df_pasillo = df[
    df["pasillo_completo"] == pasillo
].copy()

rack_critico = resumen_pasillo.loc[
    resumen_pasillo["dias_max"].idxmax()
]

kpis_pasillo = {
    "palets": df_pasillo["sscc"].nunique(),
    "edad_media": round(df_pasillo["dias"].mean(), 1),
    "rack_critico": rack_critico["rack"],
    "mas_90": df_pasillo[df_pasillo["dias"] > 90]["sscc"].nunique()
}

libro = LibroPasillo(
    pasillo,
    df_pasillo,
    resumen_pasillo,
    kpis_pasillo,
    p25,
    p50,
    p75
)

pdf = libro.generar()

st.download_button(
    "📄 Descargar Libro de Pasillo",
    data=pdf,
    file_name=f"Libro_{pasillo}.pdf",
    mime="application/pdf"
)

# ==========================================
# DISEÑO PRINCIPAL
# ==========================================

col_mapa, col_detalle = st.columns([7, 3])

# ==========================================
# MAPA
# ==========================================

with col_mapa:

    st.subheader("Mapa de calor")

    rack = dibujar_heatmap(
        resumen,
        pasillo,
        p25,
        p50,
        p75
    )

# ==========================================
# DETALLE
# ==========================================

with col_detalle:

    st.subheader("Detalle")

    if rack is None:

        st.info("Selecciona un rack del mapa.")

    else:

        mostrar_rack(
            df,
            pasillo,
            rack
        )