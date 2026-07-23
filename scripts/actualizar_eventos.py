import requests
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import urljoin
from datetime import datetime

AGENDA_URL = (
    "https://sedeelectronica.pamplona.es/srv/Agenda/"
    "lista_p_agenda.aspx?"
    "Subject=pamplona&busq=agenda&idioma=1&subMnuActual=2&tr=TREGISI02"
)

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
            url = urljoin(r.url, enlace["href"])

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
                "url": url,
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
        "# Eventos en Pamplona",
        "",
        "Consulta algunos de los próximos eventos y actividades que puedes disfrutar durante tu estancia en Pamplona.",
        "",
        f"*Información actualizada el {fecha_actualizacion}.*",
        "",
    ]

    for evento in eventos:

        lineas.append(f"## {evento['titulo']}")
        lineas.append("")

        if evento["lugar"]:
            lineas.append(f"**Lugar:** {evento['lugar']}  ")

        if evento["fecha_fin"]:
            lineas.append(f"**Fecha de finalización:** {evento['fecha_fin']}  ")

        if evento["url"]:
            lineas.append(
                f"[Consultar información oficial del evento]({evento['url']})"
            )

        lineas.append("")

    return "\n".join(lineas)


def main():

    eventos = obtener_eventos()

    print()
    print(f"Eventos encontrados: {len(eventos)}")
    print()

    if not eventos:
        print("No se han encontrado eventos.")
        return

    markdown = generar_markdown(eventos)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    OUTPUT_FILE.write_text(markdown, encoding="utf-8")

    print(f"Archivo generado: {OUTPUT_FILE}")
    print()
    print("Primeros eventos encontrados:")

    for evento in eventos[:5]:
        print(f"- {evento['titulo']}")

    print()
    print("Proceso terminado correctamente.")


if __name__ == "__main__":
    main()
