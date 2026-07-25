#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pathlib import Path
from datetime import datetime
import re
import unicodedata


URL_AGENDA = "https://baluarte.com/es/agenda"
BASE_URL = "https://baluarte.com"

OUTPUT = Path(
    "content/pamplona/conciertos/_index.md"
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/120 Safari/537.36"
    )
}


# =========================================================
# FUNCIONES AUXILIARES
# =========================================================

def limpiar(texto):

    if not texto:
        return ""

    return re.sub(
        r"\s+",
        " ",
        texto
    ).strip()


def escapar_html(texto):

    """
    Escapa caracteres especiales para evitar
    problemas al generar HTML desde Markdown.
    """

    if not texto:
        return ""

    return (
        texto
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def normalizar(texto):

    texto = texto.lower()

    texto = unicodedata.normalize(
        "NFD",
        texto
    )

    texto = "".join(
        caracter
        for caracter in texto
        if unicodedata.category(caracter) != "Mn"
    )

    return texto


def texto_relevante(lineas):

    """
    Intenta eliminar las zonas de navegación y pie
    de página para reducir falsos positivos.
    """

    ignorar = [
        "agenda",
        "entradas",
        "accesibilidad",
        "ver agenda",
        "organizar evento",
        "suscríbete a la newsletter",
        "histórico",
        "espacios",
        "tour virtual",
        "servicios",
        "testimonios",
        "últimos eventos",
        "qué es baluarte",
        "taquilla",
        "cómo llegar",
        "contacto",
        "visitas guiadas",
        "política de privacidad",
        "aviso legal",
        "cookies",
        "accesibilidad web",
        "redes profesionales",
    ]

    ignorar_normalizado = [
        normalizar(x)
        for x in ignorar
    ]

    resultado = []

    for linea in lineas:

        linea_normalizada = normalizar(
            linea
        )

        if linea_normalizada in ignorar_normalizado:

            continue

        resultado.append(
            linea
        )

    return " ".join(
        resultado
    )


# =========================================================
# EXTRAER INFORMACIÓN DE LA FICHA
# =========================================================

def extraer_ficha(url):

    try:

        respuesta = requests.get(
            url,
            headers=HEADERS,
            timeout=30
        )

        respuesta.raise_for_status()

        soup = BeautifulSoup(
            respuesta.text,
            "html.parser"
        )

        # -------------------------------------------------
        # TEXTO
        # -------------------------------------------------

        texto = soup.get_text(
            "\n",
            strip=True
        )

        lineas = [
            limpiar(linea)
            for linea in texto.splitlines()
        ]

        lineas = [
            linea
            for linea in lineas
            if linea
        ]

        # -------------------------------------------------
        # TÍTULO
        # -------------------------------------------------

        titulo = ""

        if soup.title:

            titulo = limpiar(
                soup.title.get_text(
                    " ",
                    strip=True
                )
            )

        titulo = re.sub(
            r"\s*\|\s*Baluarte.*$",
            "",
            titulo,
            flags=re.IGNORECASE
        )

        titulo = re.sub(
            r"\s*-\s*Baluarte.*$",
            "",
            titulo,
            flags=re.IGNORECASE
        )

        titulo = limpiar(
            titulo
        )

        titulo_normalizado = normalizar(
            titulo
        )

        # -------------------------------------------------
        # FECHA
        # -------------------------------------------------

        fecha = ""

        patron_fecha = re.compile(
            r"^\d{1,2} de "
            r"(enero|febrero|marzo|abril|mayo|junio|"
            r"julio|agosto|septiembre|octubre|noviembre|diciembre)"
            r" de \d{4}$",
            re.IGNORECASE
        )

        # Fecha única

        for linea in lineas:

            if patron_fecha.match(
                linea
            ):

                fecha = linea

                break

        # -------------------------------------------------
        # FECHA CON RANGO
        # -------------------------------------------------

        if not fecha:

            patron_rango = re.compile(
                r"^\d{1,2}"
                r"\s*(?:y|-|–|—)"
                r"\s*\d{1,2}"
                r"\s+de\s+"
                r"(enero|febrero|marzo|abril|mayo|junio|"
                r"julio|agosto|septiembre|octubre|noviembre|diciembre)"
                r"\s+de\s+\d{4}$",
                re.IGNORECASE
            )

            for linea in lineas:

                if patron_rango.match(
                    linea
                ):

                    fecha = linea

                    break

        # -------------------------------------------------
        # HORA
        # -------------------------------------------------

        hora = ""

        patron_hora = re.compile(
            r"^\d{1,2}:\d{2}$"
        )

        if fecha:

            try:

                indice_fecha = lineas.index(
                    fecha
                )

                for linea in lineas[
                    indice_fecha + 1:
                    indice_fecha + 8
                ]:

                    if patron_hora.match(
                        linea
                    ):

                        hora = linea

                        break

            except ValueError:

                pass

        # -------------------------------------------------
        # SALA
        # -------------------------------------------------

        sala = ""

        salas_conocidas = [

            "Sala Principal",

            "Sala de Cámara",

            "Sala de Exposiciones"

        ]

        if fecha:

            try:

                indice_fecha = lineas.index(
                    fecha
                )

                for linea in lineas[
                    indice_fecha + 1:
                    indice_fecha + 10
                ]:

                    if linea in salas_conocidas:

                        sala = linea

                        break

            except ValueError:

                pass

        # =================================================
        # TEXTO RELEVANTE
        # =================================================

        texto_relevante_evento = texto_relevante(
            lineas
        )

        texto_relevante_normalizado = normalizar(
            texto_relevante_evento
        )

        # =================================================
        # EXCLUSIONES
        # =================================================

        exclusiones_titulo = [

            # Humor y comedia

            "show patetico",
            "ignatius",
            "miguel lago",
            "yunez chaib",
            "matrimonio sin filtros",
            "piensa en wilbur",
            "corta el cable rojo",
            "ultrashow",
            "bien",
            "mentes peligrosas",
            "america forever",
            "poderio",
            "angel martin",
            "comandante lara",
            "sinvergonza",
            "javi sancho",
            "dani martinez",
            "no me toques el cuento",

            # Cine

            "zinema beach",
            "wall-e",
            "los cazafantasmas",

            # Congresos

            "congreso",
            "simposio",
            "jornada",
            "curso de actualizacion",
            "salon del estudiante",
            "travel market",

            # Eventos empresariales

            "zabala innovation",
            "smart green mobility",

        ]

        motivo_exclusion = None

        for palabra in exclusiones_titulo:

            if palabra in titulo_normalizado:

                motivo_exclusion = palabra

                break

        if motivo_exclusion:

            print(
                "  Excluido:",
                titulo,
                f"(motivo: {motivo_exclusion})"
            )

            return None

        # =================================================
        # VALIDACIÓN
        # =================================================

        if not fecha:

            print(
                "  Excluido sin fecha:",
                titulo
            )

            return None

        if not hora:

            print(
                "  Excluido sin hora:",
                titulo
            )

            return None

        if not sala:

            print(
                "  Excluido sin sala:",
                titulo
            )

            return None

        # =================================================
        # IDENTIFICACIÓN MUSICAL
        # =================================================

        indicadores_musicales = [

            "concierto",
            "musica",
            "flamenco",
            "opera",
            "recital",
            "musical",
            "gala lirica",
            "zarzuela",

            "orquesta",
            "orquesta sinfonica",
            "euskadiko orkestra",
            "sinfónica",
            "sinfonica",
            "sinfonia",
            "mozart",
            "beethoven",
            "bach",
            "brahms",
            "schumann",
            "stravinsky",
            "prokofiev",

            "piano",
            "violin",
            "guitarra",
            "coro",
            "cantores",
            "stabat mater",

            "ballet",
            "danza",
            "danza flamenca",

            "gira",
            "tour",
            "nuevo album",
            "presentacion nuevo album",

            "flamenco on fire",

            "gospel",

            "jose merce",
            "manuel linan",
            "yerai cortes",
            "zucchero",
            "victor manuel",
            "obk",
            "anastacia",
            "eliades ochoa",
            "chambao",
            "miguel rios",
            "rafa sanchez",
            "revolver",
            "malu",
            "mocedades",
            "los panchos",
            "fito",
            "sara baras",
            "rodrigo cuevas",
            "nadine sierra",
            "yuja wang",
            "janus lester",
            "izaro",
            "dire straits",
            "jakub jozef orlinski",

        ]

        es_musical = any(

            indicador in texto_relevante_normalizado

            for indicador
            in indicadores_musicales

        )

        if not es_musical:

            print(
                "  Excluido: no identificado como musical:",
                titulo
            )

            return None

        # =================================================
        # EVENTO VÁLIDO
        # =================================================

        print(
            "  ✓",
            titulo
        )

        print(
            "   ",
            fecha,
            "|",
            hora,
            "|",
            sala
        )

        return {

            "titulo": titulo,

            "fecha": fecha,

            "hora": hora,

            "sala": sala,

            "url": url

        }

    except Exception as e:

        print(
            "  ERROR leyendo ficha:",
            url
        )

        print(
            "  ",
            e
        )

        return None


# =========================================================
# FECHA PARA ORDENACIÓN
# =========================================================

def obtener_fecha_orden(evento):

    fecha = evento["fecha"]

    meses = {

        "enero": 1,
        "febrero": 2,
        "marzo": 3,
        "abril": 4,
        "mayo": 5,
        "junio": 6,
        "julio": 7,
        "agosto": 8,
        "septiembre": 9,
        "octubre": 10,
        "noviembre": 11,
        "diciembre": 12

    }

    patron = re.search(

        r"(\d{1,2})"
        r"(?:\s*(?:y|-|–|—)\s*\d{1,2})?"
        r"\s+de\s+"
        r"([a-záéíóú]+)"
        r"\s+de\s+"
        r"(\d{4})",

        fecha.lower()

    )

    if not patron:

        return datetime.max

    dia = int(
        patron.group(1)
    )

    mes = meses.get(

        normalizar(
            patron.group(2)
        ),

        1

    )

    año = int(
        patron.group(3)
    )

    return datetime(

        año,
        mes,
        dia

    )


# =========================================================
# OBTENER ENLACES DE LA AGENDA
# =========================================================

def obtener_enlaces_agenda():

    print(
        "Consultando agenda de Baluarte..."
    )

    print(
        URL_AGENDA
    )

    respuesta = requests.get(

        URL_AGENDA,

        headers=HEADERS,

        timeout=30

    )

    respuesta.raise_for_status()

    soup = BeautifulSoup(

        respuesta.text,

        "html.parser"

    )

    enlaces = []

    vistos = set()

    for enlace in soup.find_all(

        "a",

        href=True

    ):

        href = enlace.get(
            "href"
        )

        if "/es/agenda/evento/" not in href:

            continue

        url = urljoin(

            BASE_URL,

            href

        )

        if url in vistos:

            continue

        vistos.add(
            url
        )

        enlaces.append(
            url
        )

    return enlaces


# =========================================================
# GENERAR MARKDOWN
# =========================================================

def generar_markdown(eventos):

    ahora = datetime.now()

    fecha_actualizacion = ahora.strftime(
        "%d/%m/%Y %H:%M"
    )

    eventos.sort(
        key=obtener_fecha_orden
    )

    contenido = f"""---
title: "Conciertos y eventos musicales en Pamplona | Agenda 2026-2027"
description: "Agenda actualizada de conciertos, música clásica, ópera, flamenco, musicales y espectáculos musicales en Baluarte, Pamplona."
lastmod: "{ahora.isoformat()}"
---

<div class="page-section">

<div class="container">

<h1>Conciertos y eventos musicales en Pamplona</h1>

<p class="intro">
Consulta los próximos conciertos y eventos musicales programados en
<strong>Baluarte, Palacio de Congresos y Auditorio de Navarra</strong>.
</p>

<p class="intro">
Esta agenda incluye conciertos, música clásica, ópera, flamenco,
musicales, coros y otros espectáculos musicales.
</p>

<p class="actualizacion">
Última actualización: {fecha_actualizacion}
</p>

"""

    if not eventos:

        contenido += """
<div class="sin-eventos">

<p>
Actualmente no se han encontrado eventos musicales en la agenda de Baluarte.
</p>

</div>
"""

    else:

        contenido += """
<div class="eventos-lista">
"""

        for evento in eventos:

            titulo = escapar_html(
                evento["titulo"]
            )

            fecha = escapar_html(
                evento["fecha"]
            )

            hora = escapar_html(
                evento["hora"]
            )

            sala = escapar_html(
                evento["sala"]
            )

            url = evento["url"]

            contenido += f"""
<article class="evento-card">

<div class="evento-card-content">

<h2>{titulo}</h2>

<div class="evento-datos">

<span class="evento-fecha">
{fecha}
</span>

<span class="evento-separador">·</span>

<span class="evento-hora">
{hora}
</span>

<span class="evento-separador">·</span>

<span class="evento-sala">
{sala}
</span>

</div>

<a
class="evento-boton"
href="{url}"
target="_blank"
rel="noopener noreferrer"
>
Ver información y entradas
</a>

</div>

</article>
"""

        contenido += """
</div>
"""

    contenido += """

<section class="conciertos-cta">

<h2>¿Vienes a un concierto a Pamplona?</h2>

<p>
Si vas a asistir a un concierto o evento musical en Baluarte,
puedes alojarte en nuestros apartamentos turísticos en Pamplona.
</p>

<p>
Nuestros apartamentos están situados en Pamplona y son una opción
cómoda para quienes visitan la ciudad por motivos culturales,
musicales o de ocio.
</p>

<a
class="evento-boton"
href="/apartamentos/"
>
Ver nuestros apartamentos
</a>

</section>

</div>

</div>
"""

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    OUTPUT.write_text(
        contenido,
        encoding="utf-8"
    )

    print()

    print(
        "Archivo generado:"
    )

    print(
        OUTPUT
    )

    print()

    print(
        "Eventos musicales encontrados:",
        len(eventos)
    )


# =========================================================
# PROGRAMA PRINCIPAL
# =========================================================

def main():

    try:

        enlaces = obtener_enlaces_agenda()

        print(
            "Eventos de agenda encontrados:",
            len(enlaces)
        )

        eventos = []

        for url in enlaces:

            print()

            print(
                "Analizando ficha:",
                url
            )

            evento = extraer_ficha(
                url
            )

            if evento:

                eventos.append(
                    evento
                )

        # -------------------------------------------------
        # ELIMINAR DUPLICADOS
        # -------------------------------------------------

        eventos_unicos = {}

        for evento in eventos:

            eventos_unicos[
                evento["url"]
            ] = evento

        eventos = list(
            eventos_unicos.values()
        )

        generar_markdown(
            eventos
        )

    except Exception as e:

        print()

        print(
            "ERROR:",
            e
        )


if __name__ == "__main__":

    main()
