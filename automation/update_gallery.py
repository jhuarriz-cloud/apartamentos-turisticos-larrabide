from pathlib import Path

BASE = Path(__file__).resolve().parent.parent

IMAGE_ROOT = BASE / "static" / "images" / "apartamentos"
CONTENT_ROOT = BASE / "content" / "apartamentos"

for apartment in IMAGE_ROOT.iterdir():

    if not apartment.is_dir():
        continue

    md_file = CONTENT_ROOT / f"{apartment.name}.md"

    if not md_file.exists():
        print(f"No existe {md_file}")
        continue

    images = sorted(apartment.glob("*.jpg"))

    gallery = []

    for image in images:

        if image.name == "portada.jpg":
            continue

        gallery.append(
            f'  - "/images/apartamentos/{apartment.name}/{image.name}"'
        )

    text = md_file.read_text(encoding="utf-8")

    start = text.find("gallery:")
    end = text.find("\n\n---")

    if start == -1 or end == -1:
        print(f"No encuentro gallery en {md_file.name}")
        continue

    new_gallery = "gallery:\n" + "\n".join(gallery)

    text = text[:start] + new_gallery + text[end:]

    md_file.write_text(text, encoding="utf-8")

    print(f"Actualizado {md_file.name}")
