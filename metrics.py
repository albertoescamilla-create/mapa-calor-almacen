import pandas as pd


# =====================================================
# PERCENTILES
# =====================================================

def calcular_percentiles(df):

    p25 = df["dias"].quantile(0.25)
    p50 = df["dias"].quantile(0.50)
    p75 = df["dias"].quantile(0.75)

    return p25, p50, p75


# =====================================================
# RESUMEN POR RACK
# =====================================================

def resumen_racks(df):

    resumen = (
        df.groupby(["pasillo_completo", "rack"])
        .agg(
            dias_max=("dias", "max"),
            dias_media=("dias", "mean"),
            palets=("sscc", "nunique"),   # <-- CAMBIO
            unidades=("qty", "sum")
        )
        .reset_index()
    )

    resumen["dias_media"] = resumen["dias_media"].round(1)

    return resumen


# =====================================================
# KPIs GENERALES
# =====================================================

def calcular_kpis(df):

    resumen = resumen_racks(df)

    rack_critico = resumen.loc[
        resumen["dias_max"].idxmax()
    ]

    return {

        "palets": df["sscc"].nunique(),   # <-- CAMBIO

        "referencias": df["product_name"].nunique(),

        "productos": len(df),

        "unidades": int(df["qty"].sum()),

        "racks_ocupados": resumen.shape[0],

        "rack_critico": f"{rack_critico['pasillo_completo']}-{rack_critico['rack']}",

        "rack_mas_antiguo": int(rack_critico["dias_max"]),

        "edad_media": round(df["dias"].mean(), 1),

        "edad_mediana": round(df["dias"].median(), 1),

        "edad_maxima": int(df["dias"].max()),

        "edad_minima": int(df["dias"].min()),

        "mas_30": df[df["dias"] > 30]["sscc"].nunique(),

        "mas_60": df[df["dias"] > 60]["sscc"].nunique(),

        "mas_90": df[df["dias"] > 90]["sscc"].nunique(),

        "mas_120": df[df["dias"] > 120]["sscc"].nunique(),

        "mas_180": df[df["dias"] > 180]["sscc"].nunique(),

    }


# =====================================================
# KPIs POR PASILLO
# =====================================================

def resumen_pasillos(df):

    return (
        df.groupby("pasillo_completo")
        .agg(
            palets=("sscc", "nunique"),   # <-- CAMBIO
            unidades=("qty", "sum"),
            edad_media=("dias", "mean"),
            edad_maxima=("dias", "max")
        )
        .round(1)
        .reset_index()
    )


# =====================================================
# TOP RACKS
# =====================================================

def top_racks(df, n=10):

    resumen = resumen_racks(df)

    return resumen.sort_values(
        "dias_max",
        ascending=False
    ).head(n)


# =====================================================
# TOP PRODUCTOS
# =====================================================

def top_productos(df, n=10):

    return (
        df.groupby("product_name")
        .agg(
            dias=("dias", "max"),
            palets=("sscc", "nunique")   # <-- CAMBIO
        )
        .sort_values(
            "dias",
            ascending=False
        )
        .head(n)
        .reset_index()
    )


# =====================================================
# HISTOGRAMA
# =====================================================

def distribucion_edades(df):

    return df["dias"]


# =====================================================
# PALLETS CRÍTICOS
# =====================================================

def palets_criticos(df, dias=90):

    return df[df["dias"] >= dias].sort_values(
        "dias",
        ascending=False
    )


# =====================================================
# RESUMEN RACK
# =====================================================

def resumen_rack(df, pasillo, rack):

    return df[
        (df["pasillo_completo"] == pasillo)
        &
        (df["rack"] == rack)
    ].sort_values(
        "dias",
        ascending=False
    )


# =====================================================
# DOBLES UBICACIONES
# =====================================================

def detectar_doble_palets(df):

    dobles = (
        df.groupby(
            [
                "pasillo_completo",
                "rack",
                "address"
            ]
        )
        .agg(
            palets=("sscc", "nunique")   # <-- CAMBIO
        )
        .reset_index()
    )

    dobles = dobles[
        dobles["palets"] > 1
    ].sort_values(
        "palets",
        ascending=False
    )

    return dobles