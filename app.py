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


# =====================================================
# DEPARTAMENTOS
# =====================================================

DPTS = {
    "01": "01 Materiales",
    "02": "02 Madera",
    "03": "03 Electricidad",
    "04": "04 Herramientas",
    "05": "05 Renovables",
    "06": "06 Cerámica",
    "07": "07 Sanitario",
    "08": "08 Cocina y Armarios",
    "09": "09 Jardín",
    "10": "10 Ferretería",
    "11": "11 Pintura",
    "12": "12 Decoración",
    "13": "13 Iluminación",
}


# =====================================================
# CONFIGURACIÓN
# =====================================================

st.set_page_config(
    page_title=TITULO_APP,
    page_icon="🔥",
    layout="wide"
)

st.title(TITULO_APP)
st.caption("Versión 1.2.0")


with st.sidebar:

    st.divider()
    st.caption("Mapa de Calor del Almacén LS")
    st.caption("v1.2.0")
    st.caption("© Julio 2026")
    st.caption("Desarrollado por Alberto Escamilla")


# =====================================================
# SESSION
# =====================================================

if "rack_seleccionado" not in st.session_state:
    st.session_state["rack_seleccionado"] = {
        "pasillo": None,
        "rack": None
    }


# =====================================================
# CSV
# =====================================================

archivo = st.file_uploader(
    "Selecciona el CSV exportado desde Power BI",
    type="csv"
)

if archivo is None:
    st.info("Sube un CSV para comenzar.")
    st.stop()


# =====================================================
# CARGA
# =====================================================

try:

    df = cargar_csv(archivo)

    # Ocultar picking
    df = df[df["altura"] != "10"].copy()

    # Normalizar departamento
    df["dpt"] = (
        df["dpt"]
        .fillna(0)
        .astype(int)
        .astype(str)
        .str.zfill(2)
    )

except Exception as e:

    st.error(e)
    st.stop()


# =====================================================
# MÉTRICAS
# =====================================================

kpis = calcular_kpis(df)

p25, p50, p75 = calcular_percentiles(df)

resumen = resumen_racks(df)

dobles = detectar_doble_palets(df)

# =====================================================
# KPIs GENERALES
# =====================================================

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("📦 Palets", kpis["palets"])
c2.metric("⏳ Edad media", f'{kpis["edad_media"]} días')
c3.metric("🚨 Rack crítico", kpis["rack_critico"])
c4.metric("🔥 >90 días", kpis["mas_90"])
c5.metric("⚠️ Dobles", len(dobles))

st.divider()

# =====================================================
# INCIDENCIAS
# =====================================================

if not dobles.empty:

    with st.expander(f"⚠️ Ver {len(dobles)} dobles ubicaciones"):

        st.dataframe(
            dobles,
            hide_index=True,
            use_container_width=True
        )

# =====================================================
# LEYENDA
# =====================================================

st.subheader("Leyenda")

l1, l2, l3, l4 = st.columns(4)

l1.metric("🟢 Verde", f"≤ {int(p25)} días")
l2.metric("🟡 Amarillo", f"{int(p25)+1}-{int(p50)}")
l3.metric("🟠 Naranja", f"{int(p50)+1}-{int(p75)}")
l4.metric("🔴 Rojo", f"> {int(p75)} días")

st.divider()

# =====================================================
# SELECTOR
# =====================================================

opciones = []

# Secciones

for codigo in sorted(df["dpt"].unique()):

    if codigo not in DPTS:
        continue

    opciones.append(
        f"📂 {DPTS[codigo]}"
    ) 

# Pasillos

for p in sorted(df["pasillo_completo"].unique()):

    opciones.append(
        f"📦 {p}"
    )

vista = st.selectbox(
    "Selecciona una vista",
    opciones
)

# =====================================================
# MODO PASILLO / SECCIÓN
# =====================================================

es_pasillo = vista.startswith("📦")

if es_pasillo:

    pasillo = vista.replace("📦 ", "")

    df_vista = df[
        df["pasillo_completo"] == pasillo
    ].copy()

    resumen_vista = resumen_racks(df_vista)
   

else:

    codigo = vista.replace("📂 ", "")[:2]

    df_vista = df[
         df["dpt"] == codigo
    ].copy()

    resumen_vista = resumen_racks(df_vista)

# =====================================================
# PDF (solo pasillos)
# =====================================================

if es_pasillo:

    rack_critico = resumen_vista.loc[
        resumen_vista["dias_max"].idxmax()
    ]

    kpis_pasillo = {

        "palets": df_vista["sscc"].nunique(),

        "edad_media": round(
            df_vista["dias"].mean(),
            1
        ),

        "rack_critico": rack_critico["rack"],

        "mas_90": df_vista[
            df_vista["dias"] > 90
        ]["sscc"].nunique()

    }

    libro = LibroPasillo(

        pasillo,

        df_vista,

        resumen_vista,

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
# =====================================================
# PDF (solo secciones)
# =====================================================

if not es_pasillo:

    rack_critico = resumen_vista.loc[
        resumen_vista["dias_max"].idxmax()
    ]

    kpis_seccion = {

        "palets": df_vista["sscc"].nunique(),

        "edad_media": round(
            df_vista["dias"].mean(),
            1
        ),

        "rack_critico": rack_critico["rack"],

        "mas_90": df_vista[
            df_vista["dias"] > 90
        ]["sscc"].nunique()

    }

    libro = LibroPasillo(

        DPTS[codigo],

        df_vista,

        resumen_vista,

        kpis_seccion,

        p25,

        p50,

        p75,

        tipo="seccion"

    )

    pdf = libro.generar()

    st.download_button(

        "📄 Descargar Libro de Sección",

        data=pdf,

        file_name=f"Libro_Seccion_{codigo}.pdf",

        mime="application/pdf"

    )

# =====================================================
# DISEÑO PRINCIPAL
# =====================================================

col_mapa, col_detalle = st.columns([7, 3])

# =====================================================
# MAPA
# =====================================================

with col_mapa:

    if es_pasillo:

        st.subheader(f"Mapa de calor · {pasillo}")

        rack = dibujar_heatmap(
            resumen_vista,
            pasillo,
            p25,
            p50,
            p75
        )

    else:

        st.subheader(f"Sección {DPTS[codigo]}")

        rack = None
        pasillo_rack = None

        pasillos_seccion = sorted(
            df_vista["pasillo_completo"].unique()
        )

        for pasillo_actual in pasillos_seccion:

            st.markdown("---")

            st.markdown(f"## 📦 {pasillo_actual}")

            rack_tmp = dibujar_heatmap(
                resumen_vista,
                pasillo_actual,
                p25,
                p50,
                p75
            )

            if rack_tmp is not None:

                rack = rack_tmp
                pasillo_rack = pasillo_actual


# =====================================================
# DETALLE
# =====================================================

with col_detalle:

    st.subheader("Detalle")

    if es_pasillo:

        if rack is None:

            st.info("Selecciona un rack.")

        else:

            mostrar_rack(
                df,
                pasillo,
                rack
            )

    else:

        if rack is None:

            st.info("Selecciona un rack de cualquier pasillo.")

        else:

            mostrar_rack(
                df,
                pasillo_rack,
                rack
            )
