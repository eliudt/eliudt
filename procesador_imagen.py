from PIL import Image, ImageChops


# =========================================================
# RECORTAR BORDES BLANCOS REALES
# =========================================================

def recortar_bordes(imagen_path):

    img = Image.open(imagen_path).convert("RGB")

    fondo = Image.new("RGB", img.size, (255, 255, 255))

    diff = ImageChops.difference(img, fondo)

    bbox = diff.getbbox()

    if bbox:
        img = img.crop(bbox)

    img.save(imagen_path)
