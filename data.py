import pandas as pd


def cargar_csv(archivo):
    df = pd.read_csv(archivo)

    # Normalizar columnas
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("-", "_")
    )

    # Solo ubicaciones LS
    df = df[df["address"].astype(str).str.contains("LS", case=False, na=False)]
    df = df[~df["address"].astype(str).str.contains("XP1", case=False, na=False)]

    # Fecha
    df["sscc_creation_time"] = pd.to_datetime(
        df["sscc_creation_time"],
        errors="coerce",
        utc=True
    )

    hoy = pd.Timestamp.now(tz="UTC")

    df["dias"] = (hoy - df["sscc_creation_time"]).dt.days

    # Separar dirección
    partes = df["address"].str.split("-", expand=True)

    df["almacen"] = partes[0]
    df["zona"] = partes[1]
    df["pasillo"] = partes[2]
    df["rack"] = partes[3]
    df["altura"] = partes[4]
    df["posicion"] = partes[5]

    df["pasillo_completo"] = df["zona"] + "-" + df["pasillo"]

    return df