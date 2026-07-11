from io import BytesIO
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)


class LibroPasillo:

    def __init__(
        self,
        titulo,
        df,
        resumen,
        kpis,
        p25,
        p50,
        p75,
        tipo="pasillo",
    ):

        self.titulo = titulo
        self.tipo = tipo

        self.df = df
        self.resumen = resumen
        self.kpis = kpis

        self.p25 = p25
        self.p50 = p50
        self.p75 = p75

        self.estilos = getSampleStyleSheet()

    def generar(self):

        buffer = BytesIO()

        doc = SimpleDocTemplate(
            buffer,
            rightMargin=20,
            leftMargin=20,
            topMargin=20,
            bottomMargin=20,
        )

        elementos = []

        self.portada(elementos)
        self.resumen_general(elementos)
        self.racks(elementos)

        doc.build(elementos)

        pdf = buffer.getvalue()

        buffer.close()

        return pdf

    # =====================================================
    # PORTADA
    # =====================================================

    def portada(self, elementos):

        estilo_titulo = self.estilos["Heading1"]
        estilo_titulo.alignment = TA_CENTER

        estilo_sub = self.estilos["Heading2"]
        estilo_sub.alignment = TA_CENTER

        elementos.append(
            Paragraph(
                "MAPA DE CALOR DEL ALMACÉN",
                estilo_titulo,
            )
        )

        elementos.append(Spacer(1, 20))

        if self.tipo == "pasillo":
            texto = "LIBRO DE PASILLO"
        else:
            texto = "LIBRO DE SECCIÓN"

        elementos.append(
            Paragraph(
                texto,
                estilo_sub,
            )
        )

        elementos.append(Spacer(1, 20))

        elementos.append(
            Paragraph(
                self.titulo,
                estilo_sub,
            )
        )

        elementos.append(Spacer(1, 20))

        elementos.append(
            Paragraph(
                datetime.now().strftime("%d/%m/%Y %H:%M"),
                self.estilos["Normal"],
            )
        )

        elementos.append(PageBreak())
    # =====================================================
    # RESUMEN GENERAL
    # =====================================================

    def resumen_general(self, elementos):

        if self.tipo == "pasillo":
            titulo = "RESUMEN DEL PASILLO"
        else:
            titulo = "RESUMEN DE LA SECCIÓN"

        elementos.append(
            Paragraph(
                titulo,
                self.estilos["Heading1"],
            )
        )

        elementos.append(Spacer(1, 15))

        datos = [
            ["Palets", self.kpis["palets"]],
            ["Edad media", f"{self.kpis['edad_media']} días"],
            ["Rack crítico", self.kpis["rack_critico"]],
            [">90 días", self.kpis["mas_90"]],
        ]

        tabla = Table(
            datos,
            colWidths=[180, 180],
        )

        tabla.setStyle(
            TableStyle(
                [
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
                    ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )

        elementos.append(tabla)

        elementos.append(Spacer(1, 20))

        elementos.append(
            Paragraph(
                "Resumen por rack",
                self.estilos["Heading2"],
            )
        )

        elementos.append(Spacer(1, 10))

        resumen = self.resumen.copy()

        resumen["rack_num"] = resumen["rack"].astype(int)
        resumen = resumen.sort_values("rack_num")

        tabla = [["Rack", "Palets", "Edad máx.", "Edad media"]]

        for _, fila in resumen.iterrows():

            tabla.append(
                [
                    str(fila["rack"]),
                    str(int(fila["palets"])),
                    f"{int(fila['dias_max'])} días",
                    f"{round(fila['dias_media'],1)} días",
                ]
            )

        t = Table(
            tabla,
            colWidths=[70, 70, 90, 90],
        )

        t.setStyle(
            TableStyle(
                [
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#D6EAF8")),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ]
            )
        )

        elementos.append(t)

        elementos.append(PageBreak())

    # =====================================================
    # RACKS
    # =====================================================

    def racks(self, elementos):

        resumen = self.resumen.copy()

        resumen["rack_num"] = resumen["rack"].astype(int)
        resumen = resumen.sort_values("rack_num")

        for _, rack_info in resumen.iterrows():

            rack = rack_info["rack"]

            elementos.append(
                Paragraph(
                    f"RACK {rack}",
                    self.estilos["Heading1"]
                )
            )

            elementos.append(Spacer(1, 10))

            tabla = Table(
                [
                    ["Palets", int(rack_info["palets"])],
                    ["Edad máxima", f"{int(rack_info['dias_max'])} días"],
                    ["Edad media", f"{round(rack_info['dias_media'],1)} días"],
                ],
                colWidths=[150, 150],
            )

            tabla.setStyle(
                TableStyle(
                    [
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                        ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
                        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ]
                )
            )

            elementos.append(tabla)

            elementos.append(Spacer(1, 15))

            datos = self.df[
                self.df["rack"] == rack
            ].copy()

            datos = datos.sort_values(
                ["altura", "posicion"]
            )

            if "address" not in datos.columns:
                elementos.append(PageBreak())
                continue

            alturas = sorted(
                datos["altura"].dropna().unique(),
                reverse=True
            )

            posiciones = sorted(
                datos["posicion"].dropna().unique()
            )

            for altura in alturas:

                for posicion in posiciones:

                    datos_ubicacion = datos[
                        (datos["altura"] == altura)
                        &
                        (datos["posicion"] == posicion)
                    ].copy()

                    if datos_ubicacion.empty:

                        elementos.append(
                            Paragraph(
                                f"<b>{rack}-{altura}-{posicion}</b>",
                                self.estilos["Heading2"]
                            )
                        )

                        elementos.append(
                            Paragraph(
                                "Sin palets",
                                self.estilos["Normal"]
                            )
                        )

                        elementos.append(Spacer(1, 10))

                        continue

                    ubicacion = datos_ubicacion.iloc[0]["address"]

                    elementos.append(
                        Paragraph(
                            f"<b>Ubicación:</b> {ubicacion}",
                            self.estilos["Heading2"]
                        )
                    )

                    if datos_ubicacion["sscc"].nunique() > 1:

                        elementos.append(
                            Paragraph(
                                "<font color='red'><b>⚠ DOBLE PALET</b></font>",
                                self.estilos["Normal"]
                            )
                        )

                        elementos.append(Spacer(1, 5))
                    for sscc, palet in datos_ubicacion.groupby("sscc"):

                        elementos.append(
                            Paragraph(
                                f"<b>SSCC:</b> {sscc}",
                                self.estilos["Normal"]
                            )
                        )

                        productos = [["Producto", "Cantidad"]]

                        for _, fila in palet.iterrows():

                            productos.append(
                                [
                                    str(fila["product_name"]),
                                    str(int(fila["qty"]))
                                ]
                            )

                        tabla_productos = Table(
                            productos,
                            colWidths=[320, 70]
                        )

                        tabla_productos.setStyle(
                            TableStyle(
                                [
                                    ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#D6EAF8")),
                                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                                ]
                            )
                        )

                        elementos.append(tabla_productos)

                        elementos.append(Spacer(1, 10))

                    elementos.append(Spacer(1, 15))

            elementos.append(PageBreak())