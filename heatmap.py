import math
import streamlit as st
from config import COLORES


def obtener_color(dias, p25, p50, p75):

    if dias <= p25:
        return "🟢"
    elif dias <= p50:
        return "🟡"
    elif dias <= p75:
        return "🟠"

    return "🔴"


def dibujar_heatmap(resumen, pasillo, p25, p50, p75):

    if "rack_seleccionado" not in st.session_state:
        st.session_state["rack_seleccionado"] = {
            "pasillo": None,
            "rack": None
        }

    datos = resumen[
        resumen["pasillo_completo"] == pasillo
    ].copy()

    if datos.empty:
        st.warning("No hay racks.")
        return None

    datos["rack_num"] = datos["rack"].astype(int)
    datos = datos.sort_values("rack_num")

    racks = datos.to_dict("records")

    columnas = 6
    filas = math.ceil(len(racks) / columnas)

    indice = 0

    for _ in range(filas):

        cols = st.columns(columnas)

        for col in cols:

            if indice >= len(racks):
                break

            info = racks[indice]
            indice += 1

            rack = info["rack"]

            icono = obtener_color(
                info["dias_max"],
                p25,
                p50,
                p75
            )

            with col:

                seleccionado = (
                    st.session_state["rack_seleccionado"]["pasillo"] == pasillo
                    and
                    st.session_state["rack_seleccionado"]["rack"] == rack
                )

                titulo = f"{icono} Rack {rack}"

                if seleccionado:
                    titulo = "📍 " + titulo

                with st.container(border=True):

                    st.markdown(f"### {titulo}")

                    st.write(f"🔥 **{int(info['dias_max'])} días**")
                    st.write(f"📦 **{int(info['palets'])} palets**")

                    if st.button(
                        "Seleccionar",
                        key=f"{pasillo}_{rack}",
                        use_container_width=True
                    ):

                        st.session_state["rack_seleccionado"] = {
                            "pasillo": pasillo,
                            "rack": rack
                        }

                        st.rerun()

    seleccion = st.session_state["rack_seleccionado"]

    if seleccion["pasillo"] == pasillo:
        return seleccion["rack"]

    return None