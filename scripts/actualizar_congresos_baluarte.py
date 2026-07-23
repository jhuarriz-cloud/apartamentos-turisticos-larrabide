import requests
from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime
from urllib.parse import urljoin
import re


URL = "https://baluarte.com/es/agenda"

BASE_URL = "https://baluarte.com"

OUTPUT = Path(
    "content/pamplona/congresos/_index.md"
)


def limpiar_texto(texto):
    return re.sub(
        r"\s+",
        " ",
        texto
    ).strip()


def extraer_congresos():

    print(
        "Consultando agenda oficial de Baluarte..."
    )

    respuesta = requests.get(
        URL,
        timeout=30,
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    )

    respuesta.raise_for_status()

    soup = BeautifulSoup(
        respuesta.text,
        "html.parser"
    )

    congresos = []

    for enlace in soup.find_all(
        "a",
        href=True
    ):

        href = enlace["href"]

        titulo = limpiar_texto(
            enlace.get_text(
                " ",
                strip=True
            )
        )

        if not href.startswith(
            "/es/agenda/evento/"
        ):
            continue

        if not titulo:
            continue

        # Solo consideramos eventos cuyo
        # título contiene claramente
        # términos relacionados con congresos.
        titulo_lower = titulo.lower()

        palabras_congreso = [
            "congreso",
            "congresos",
            "simposio",
            "jornadas",
        ]

        if not any(
            palabra in titulo_lower
            for palabra in palabras_congreso
        ):
            continue

        url_evento = urljoin(
            BASE_URL,
            href
        )

        congresos.append(
            {
                "titulo": titulo,
                "url": url_evento,
            }
        )

    # Eliminar duplicados
    unicos = {}

    for congreso in congresos:

        unicos[
            congreso["url"]
        ] = congreso

    return list(
        unicos.values()
    )


def generar_markdown(
    congresos
):

    fecha_actualizacion = (
        datetime.now()
        .strftime(
            "%d/%m/%Y %H:%M"
        )
    )

    lineas = [

        "---",

        'title: "Congresos en Baluarte, Pamplona"',

        'description: "Próximos congresos, simposios y jornadas profesionales en Baluarte, Palacio de Congresos y Auditorio de Navarra. Encuentra alojamiento en Pamplona para tu congreso o viaje de trabajo."',

        "draft: false",

        "---",

        "",

        "# Congresos en Baluarte, Pamplona",

        "",

        "Si vas a asistir a un congreso, simposio o jornada profesional en Baluarte, Palacio de Congresos y Auditorio de Navarra, encontrar alojamiento cercano puede hacer tu estancia en Pamplona más cómoda.",

        "",

        "En esta página recopilamos automáticamente los próximos congresos y eventos profesionales publicados en la agenda oficial de Baluarte.",

        "",

        f"*Información actualizada el {fecha_actualizacion}.*",

        "",
    ]


    if not congresos:

        lineas.extend(
            [
                "Actualmente no se han encontrado próximos congresos publicados en la agenda oficial.",

                "",
            ]
        )


    else:

        for congreso in congresos:

            lineas.extend(
                [

                    f"## {congreso['titulo']}",

                    "",

                    f"[Ver información oficial del evento]({congreso['url']})",

                    "",

                ]
            )


    lineas.extend(
        [

            "## Alojamiento para congresos en Pamplona",

            "",

            "Si necesitas alojamiento durante un congreso en Baluarte, Apartamentos Turísticos Larrabide ofrece apartamentos completos en Pamplona para estancias profesionales y de varios días.",

            "",

            "Consulta nuestros apartamentos y encuentra la opción que mejor se adapte a tu estancia.",

            "",

            "[Ver apartamentos](/apartamentos/)",

            "",

            "[Consultar opciones de reserva](/reservar/)",

            "",

        ]
    )


    return "\n".join(
        lineas
    )


def main():

    congresos = (
        extraer_congresos()
    )

    print()

    print(
        "Congresos encontrados:",
        len(congresos)
    )

    print()

    for congreso in congresos:

        print(
            "-",
            congreso[
                "titulo"
            ]
        )


    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True
    )


    contenido = (
        generar_markdown(
            congresos
        )
    )


    OUTPUT.write_text(
        contenido,
        encoding="utf-8"
    )


    print()

    print(
        "Archivo generado:",
        OUTPUT
    )

    print()

    print(
        "Proceso terminado correctamente."
    )


if __name__ == "__main__":

    main()
