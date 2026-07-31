from pathlib import Path
import hashlib


def leer_archivo(ruta):
    ruta = Path(ruta)
    if not ruta.exists():
        return ""
    return ruta.read_text(encoding="utf-8")


def escribir_archivo(ruta, contenido):
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(contenido, encoding="utf-8")


import re


def normalizar_para_comparar(texto):
    """
    Elimina las líneas que cambian en cada ejecución pero que no implican
    un cambio real del contenido.
    """

    texto = re.sub(
        r"\*Información actualizada el .*?\.\*",
        "",
        texto,
        flags=re.MULTILINE,
    )

    return texto.strip()


def hash_texto(texto):
    texto = normalizar_para_comparar(texto)
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def guardar_si_cambia(ruta, contenido):
    """
    Guarda únicamente si el contenido realmente ha cambiado.
    Devuelve True si se ha modificado el archivo.
    """
    anterior = leer_archivo(ruta)

    if hash_texto(anterior) == hash_texto(contenido):
        print(f"✓ Sin cambios: {ruta}")
        return False

    escribir_archivo(ruta, contenido)
    print(f"✓ Actualizado: {ruta}")
    return True


def resumen(nombre, encontrados, nuevos=None, eliminados=None):
    print()
    print("=" * 50)
    print(nombre)
    print("=" * 50)
    print(f"Encontrados : {encontrados}")

    if nuevos is not None:
        print(f"Nuevos      : {nuevos}")

    if eliminados is not None:
        print(f"Eliminados  : {eliminados}")

    print("=" * 50)
