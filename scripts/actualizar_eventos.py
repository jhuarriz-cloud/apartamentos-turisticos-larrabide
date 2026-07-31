import requests
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import urljoin
from datetime import datetime

from lib_agendas import guardar_si_cambia, resumen

AGENDA_URL = (
    "https://sedeelectronica.pamplona.es/srv/Agenda/"
    "lista_p_agenda.aspx?"
    "Subject=pamplona&busq=agenda&idioma=1&subMnuActual=2&tr=TREGISI02"
)

AGENDA_OFICIAL_URL = "https://www.pamplona.es/actualidad/eventos"

OUTPUT_FILE = Path("content/pamplona/eventos/_index.md")


def obtener_eventos():
    print("Consultando agenda oficial de Pamplona...")

    r = requests.get(AGENDA_URL, timeout=30)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    eventos = []

    for dl in soup.find_all("dl"):

        if len(dl.find_all("dt")) < 3:
            continue

        for dt in dl.find_all("dt"):

            enlace = dt.find("a", href=True)

            if not enlace:
                continue

            titulo = enlace.get_text(" ", strip=True)

            dd = dt.find_next_sibling("dd")

            lugar = ""
            fecha_fin = ""

            if dd:
                for p in dd.find_all("p"):

                    texto = p.get_text(" ", strip=True)

                    if texto.lower().startswith("lugar:"):
                        lugar = texto.split(":", 1)[1].strip()

                    elif texto.lower().startswith("fecha de finalización:"):
                        fecha_fin = texto.split(":", 1)[1].strip()

            eventos.append({
                "titulo": titulo,
                "lugar": lugar,
                "fecha_fin": fecha_fin,
            })

        break

    return eventos


def generar_markdown(eventos):

    fecha_actualizacion = datetime.now().strftime("%d/%m/%Y %H:%M")

    lineas = [
        "---",
        'title: "Eventos en Pamplona"',
        'description: "Eventos, exposiciones, actividades y propuestas culturales en Pamplona."',
        "draft: false",
        "---",
        "",
        "Consulta algunos de los próximos eventos y actividades que puedes disfrutar durante tu estancia en Pamplona.",
        "",
        f"*Información actualizada el {fecha_actualizacion}.*",
        "",
        '<div class="eventos-lista">',
        "",
    ]

    for evento in eventos:

        lineas.append('<article class="evento-card">')
        lineas.append("")

        lineas.append(f"## {evento['titulo']}")
        lineas.append("")

        if evento["lugar"]:
            lineas.append(
                f'<p class="evento-lugar"><strong>Lugar:</strong> {evento["lugar"]}</p>'
            )
            lineas.append("")

        if evento["fecha_fin"]:
            lineas.append(
                f'<p class="evento-fecha"><strong>Fecha de finalización:</strong> {evento["fecha_fin"]}</p>'
            )
            lineas.append("")

        lineas.append(
            f'<a class="evento-boton" href="{AGENDA_OFICIAL_URL}" target="_blank" rel="noopener">'
        )
        lineas.append("Consultar agenda oficial")
        lineas.append("</a>")
        lineas.append("")
        lineas.append("</article>")
        lineas.append("")

    lineas.append("</div>")
    lineas.append("")

    return "\n".join(lineas)


def main():

    eventos = obtener_eventos()

    if not eventos:
        print("No se han encontrado eventos.")
        return

    markdown = generar_markdown(eventos)

    actualizado = guardar_si_cambia(OUTPUT_FILE, markdown)

    resumen(
        "EVENTOS",
        encontrados=len(eventos)
    )

    if actualizado:
        print("Se ha actualizado el fichero de eventos.")
    else:
        print("No había cambios que guardar.")

    print()
    print("Primeros eventos encontrados:")

    for evento in eventos[:5]:
        print(f"- {evento['titulo']}")

    print()
    print("Proceso terminado correctamente.")


if __name__ == "__main__":
    main()
