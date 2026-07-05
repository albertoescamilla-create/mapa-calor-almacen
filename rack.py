import streamlit as st
import pandas as pd


def mostrar_rack(df, pasillo, rack):

    datos = df[
        (df["pasillo_completo"] == pasillo)
        &
        (df["rack"] == rack)
    ].copy()

    # Ocultar picking
    datos = datos[
        datos["altura"] != "10"
    ]

    if datos.empty:
        st.info("Sin información.")
        return

    # ==========================
    # TÍTULO
    # ==========================

    st.markdown(
        f"## 📍 Rack {rack}"
    )

    # ==========================
    # KPIs
    # ==========================

    st.metric(
    "Palets",
    datos["sscc"].nunique()
)

    st.metric(
        "Edad máxima",
        f"{int(datos['dias'].max())} días"
    )

    st.metric(
        "Edad media",
        f"{int(datos['dias'].mean())} días"
    )

    st.metric(
        "Unidades",
        int(datos["qty"].sum())
    )

    st.divider()

    # ==========================
    # UBICACIONES
    # ==========================

    st.caption("Ubicaciones")

    alturas = ["40", "30", "20"]
    posiciones = ["A", "B", "C"]

    tabla = []

    for altura in alturas:

        fila = {"Altura": altura}

        for posicion in posiciones:

            ub = datos[
                (datos["altura"] == altura)
                &
                (datos["posicion"] == posicion)
            ]

            if ub.empty:

                fila[posicion] = "—"

            else:

                fila[posicion] = str(
                    int(ub["dias"].max())
                )

        tabla.append(fila)

    st.table(
        pd.DataFrame(tabla)
    )

    st.divider()

    # ==========================
    # PALLETS
    # ==========================

    columnas = [
        "address",
        "product_name",
        "qty",
        "dias"
    ]

    columnas = [
        c for c in columnas
        if c in datos.columns
    ]

    st.dataframe(
        datos[columnas]
        .sort_values(
            "dias",
            ascending=False
        ),
        hide_index=True,
        use_container_width=True,
        height=300
    )

    # ==========================
    # FOTO
    # ==========================

    if "product_picture" in datos.columns:

        imagen = datos["product_picture"].dropna()

        if not imagen.empty:

            st.image(
                imagen.iloc[0],
                use_container_width=True
            )