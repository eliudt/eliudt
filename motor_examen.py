import subprocess
import os
import shutil
from PIL import Image
from odf.opendocument import load
from odf.text import P
from odf.draw import Frame, Image as OdfImage
from odf.style import Style, GraphicProperties
from odf import teletype

from procesador_imagen import recortar_bordes

from datetime import datetime



PLANTILLA = "plantilla_examen.odt"


# =========================================================
# CREAR EVALUACIÓN DESDE PLANTILLA
# =========================================================

def crear_evaluacion(base, curso, periodo, anio):

    # ---------- Carpeta destino ----------
    ruta = os.path.join(base, str(anio), curso, f"Periodo_{periodo}")
    os.makedirs(ruta, exist_ok=True)

    # ---------- Fecha ----------
    timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M")

    curso_limpio = curso.replace(" ", "")

    nombre_archivo = (
        f"Evaluacion_{curso_limpio}_P{periodo}_{timestamp}.odt"
    )

    archivo_odt = os.path.join(ruta, nombre_archivo)

    # ---------- Copiar plantilla ----------
    shutil.copy(PLANTILLA, archivo_odt)

    # ⭐ Obtener grado
    grado = obtener_grado(curso)

    # ⭐ Rellenar plantilla
    llenar_grado_en_odt(archivo_odt, grado)

    return archivo_odt

# =========================================================
# OBTENER NÚMERO DE PREGUNTA
# =========================================================

def obtener_numero(archivo_odt):

    doc = load(archivo_odt)

    contador = 0

    for frame in doc.getElementsByType(Frame):
        imgs = frame.getElementsByType(OdfImage)
        if imgs:
            contador += 1

    return contador
# =========================================================
# LATEX → PNG CON NUMERACIÓN
# =========================================================

def latex_a_png(latex, numero, tipo_hoja="carta"):

    paper = "letterpaper" if tipo_hoja == "carta" else "legalpaper"

    tex = fr"""
\documentclass[12pt]{{article}}

\usepackage[spanish]{{babel}}
\usepackage{{amsmath, amssymb}}
\usepackage{{enumitem}}
\usepackage{{multicol}}
\usepackage[{paper},margin=1.5cm]{{geometry}}
\usepackage{{xcolor}}
\usepackage[utf8]{{inputenc}}

% Fuente tipo Arial (Helvetica)
\usepackage{{helvet}}
\renewcommand{{\familydefault}}{{\sfdefault}}

% Gráficos matemáticos
\usepackage{{tikz}}
\usepackage{{pgfplots}}
\pgfplotsset{{compat=1.18}}
\usetikzlibrary{{arrows.meta,calc,patterns}}

\pagestyle{{empty}}
\setlength{{\parindent}}{{0pt}}
\color{{black}}

\begin{{document}}

\noindent
\textbf{{{numero}. }}{latex}

\end{{document}}
"""

    tex_file = "temp.tex"
    pdf_file = "temp.pdf"
    crop_file = "temp_crop.pdf"
    png_file = "temp.png"

    # Guardar TEX
    with open(tex_file, "w") as f:
        f.write(tex)

    # Compilar
    subprocess.run(
        ["pdflatex", "-interaction=nonstopmode", tex_file],
        stdout=subprocess.DEVNULL
    )

    # Recortar PDF
    subprocess.run(
        ["pdfcrop", pdf_file, crop_file],
        stdout=subprocess.DEVNULL
    )

    # Convertir a PNG
    subprocess.run([
        "pdftoppm",
        "-png",
        "-r", "300",
        "-singlefile",
        crop_file,
        "temp"
    ], stdout=subprocess.DEVNULL)

    if not os.path.exists(png_file):
        raise RuntimeError("No se pudo generar la imagen.")

    recortar_bordes(png_file)

    return png_file

# =========================================================
# INSERTAR PREGUNTA EN DOCUMENTO
# =========================================================

def insertar_pregunta(archivo_odt, ruta_imagen, numero):

    if not os.path.exists(ruta_imagen):
        raise RuntimeError("La imagen no existe.")

    doc = load(archivo_odt)

    parent = doc.text

    img = Image.open(ruta_imagen)
    px_w, px_h = img.size

    dpi = 300
    cm_w = (px_w / dpi) * 2.54
    cm_h = (px_h / dpi) * 2.54

    href = doc.addPicture(ruta_imagen)

    frame = Frame(
        width=f"{cm_w:.2f}cm",
        height=f"{cm_h:.2f}cm",
        anchortype="as-char"
    )

    frame.setAttribute("name", f"Pregunta_{numero}")

    image = OdfImage(href=href)
    frame.addElement(image)

    p = P()
    p.addElement(frame)

    parent.addElement(p)

    doc.save(archivo_odt)


def reemplazar_pregunta(archivo_odt, ruta_imagen, numero):

    doc = load(archivo_odt)

    for frame in doc.getElementsByType(Frame):

        nombre = frame.getAttribute("name")

        if nombre == f"Pregunta_{numero}":

            href = doc.addPicture(ruta_imagen)

            # Eliminar imagen anterior
            for img in frame.getElementsByType(OdfImage):
                frame.removeChild(img)

            # Insertar nueva
            nueva_img = OdfImage(href=href)
            frame.addElement(nueva_img)

            doc.save(archivo_odt)
            return True

    return False
def eliminar_pregunta(archivo_odt, numero):

    doc = load(archivo_odt)

    for frame in doc.getElementsByType(Frame):

        nombre = frame.getAttribute("name")

        if nombre == f"Pregunta_{numero}":

            parent = frame.parentNode
            parent.removeChild(frame)

            doc.save(archivo_odt)
            return True

    return False

#========================================================
# FUNCIÓN PARA EXTAER GRADO
#========================================================

def obtener_grado(curso):

    curso = curso.lower()

    if "septimo" in curso:
        return "SÉPTIMO"

    if "octavo" in curso:
        return "OCTAVO"

    if "noveno" in curso:
        return "NOVENO"

    return curso

# =========================================================
# LLENAR GRADO EN ODT
# =========================================================

def llenar_grado_en_odt(archivo_odt, grado):

    doc = load(archivo_odt)

    def reemplazar_texto_recursivo(nodo, buscar, reemplazar):
        """Busca y reemplaza texto en nodos recursivamente, preservando estilos"""
        for hijo in nodo.childNodes:
            if hasattr(hijo, 'data'):
                # Es un nodo de texto
                if buscar in hijo.data:
                    hijo.data = hijo.data.replace(buscar, reemplazar)
            else:
                # Es un nodo elemento, buscar recursivamente
                reemplazar_texto_recursivo(hijo, buscar, reemplazar)

    for p in doc.getElementsByType(P):

        texto = teletype.extractText(p)

        if "<<GRADO>>" in texto:

            # Reemplazar preservando estilos
            reemplazar_texto_recursivo(p, "<<GRADO>>", grado)

    doc.save(archivo_odt)
