"""
CONFIGURACIÓN DEL PROYECTO
Mapa de Calor del Almacén
"""

# =====================================
# INFORMACIÓN DEL ALMACÉN
# =====================================

RACKS_PASILLO = {
    "LS-A": 48,
    "LS-B": 49,
    "LS-C": 42,
    "LS-E": 10
}

ALTURAS = [
    "20",
    "30",
    "40"
]

POSICIONES = [
    "A",
    "B",
    "C"
]

# =====================================
# COLORES
# =====================================

COLORES = {
    "verde": "#2ecc71",
    "amarillo": "#f1c40f",
    "naranja": "#e67e22",
    "rojo": "#e74c3c",
    "gris": "#bdc3c7",
    "fondo": "#f8f9fa",
    "texto": "#2c3e50"
}

# =====================================
# DISTRIBUCIÓN DEL MAPA
# =====================================

RACKS_POR_FILA = 6

ANCHO_RACK = 120
ALTO_RACK = 90

# =====================================
# INFORMACIÓN DEL CSV
# =====================================

COLUMNAS_REQUERIDAS = [
    "address",
    "sscc",
    "sscc_creation_time",
    "product_name",
    "qty"
]

COLUMNAS_OPCIONALES = [
    "product_picture",
    "product_code",
    "ean_code",
    "note",
    "type"
]

# =====================================
# KPIs
# =====================================

DIAS_CRITICOS = [
    30,
    60,
    90,
    120,
    180
]

# =====================================
# STREAMLIT
# =====================================

TITULO_APP = "🔥 Mapa de Calor del Almacén"

ICONO_APP = "🔥"

LAYOUT = "wide"

# =====================================
# ORDEN DE PASILLOS
# =====================================

ORDEN_PASILLOS = [
    "LS-A",
    "LS-B",
    "LS-C",
    "LS-E"
]

# =====================================
# ORDEN ALTURAS
# =====================================

ORDEN_ALTURAS = [
    "40",
    "30",
    "20",
    "10"
]

# =====================================
# ORDEN POSICIONES
# =====================================

ORDEN_POSICIONES = [
    "A",
    "B",
    "C"
]