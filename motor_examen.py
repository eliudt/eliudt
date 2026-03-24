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
ANCHO_HOJA_CARTA_CM = 21.59
ALTO_HOJA_CARTA_CM = 27.94
ANCHO_HOJA_LEGAL_CM = 21.59
ALTO_HOJA_LEGAL_CM = 35.56
PROPORCION_ANCHO_PREGUNTA = 2 / 3
MARGEN_RENDER_LATEX_CM = 0.6


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


def obtener_numeros_pregunta(archivo_odt):

    doc = load(archivo_odt)
    numeros = []

    for frame in doc.getElementsByType(Frame):
        nombre = frame.getAttribute("name") or ""

        if not nombre.startswith("Pregunta_"):
            continue

        try:
            numeros.append(int(nombre.split("_", 1)[1]))
        except (IndexError, ValueError):
            continue

    return sorted(numeros)


def obtener_numero_sugerido(archivo_odt):

    numeros = obtener_numeros_pregunta(archivo_odt)

    if not numeros:
        return 1

    return max(numeros) + 1


def pregunta_existe(archivo_odt, numero):

    return numero in obtener_numeros_pregunta(archivo_odt)
# =========================================================
# LATEX -> PNG CON NUMERACION
# =========================================================

def _renderizar_latex_a_png(tex):

    tex_file = "temp.tex"
    pdf_file = "temp.pdf"
    png_file = "temp.png"

    with open(tex_file, "w", encoding="utf-8") as f:
        f.write(tex)

    subprocess.run(
        ["pdflatex", "-interaction=nonstopmode", tex_file],
        stdout=subprocess.DEVNULL
    )

    subprocess.run([
        "pdftoppm",
        "-png",
        "-r", "300",
        "-singlefile",
        pdf_file,
        "temp"
    ], stdout=subprocess.DEVNULL)

    if not os.path.exists(png_file):
        raise RuntimeError("No se pudo generar la imagen.")

    recortar_bordes(png_file)

    return png_file


def _obtener_dimensiones_papel_cm(tipo_hoja):

    if tipo_hoja == "legal":
        return ANCHO_HOJA_LEGAL_CM, ALTO_HOJA_LEGAL_CM

    return ANCHO_HOJA_CARTA_CM, ALTO_HOJA_CARTA_CM


def _encabezado_latex(numero, tipo_hoja):
    ancho_papel_cm, alto_papel_cm = _obtener_dimensiones_papel_cm(tipo_hoja)

    return fr"""
\documentclass[10pt]{{article}}

\usepackage[spanish]{{babel}}
\usepackage{{amsmath, amssymb}}
\usepackage{{enumitem}}
\usepackage{{graphicx}}
\usepackage{{grffile}}
\usepackage{{float}}
\usepackage{{wrapfig}}
\usepackage{{caption}}
\usepackage{{subcaption}}
\usepackage{{array}}
\usepackage{{multirow}}
\usepackage{{tabularx}}
\usepackage{{tikz}}
\usetikzlibrary{{babel}}
\usepackage{{pgfplots}}
\pgfplotsset{{compat=1.18}}
\usepackage[
paperwidth={ancho_papel_cm:.2f}cm,
paperheight={alto_papel_cm:.2f}cm,
margin={MARGEN_RENDER_LATEX_CM:.2f}cm
]{{geometry}}
\usepackage{{xcolor}}
\usepackage{{multicol}}
\usepackage[utf8]{{inputenc}}

\usepackage{{helvet}}
\renewcommand{{\familydefault}}{{\sfdefault}}
\AtBeginDocument{{\shorthandoff{{<>}}}}

\pagestyle{{empty}}
\setlength{{\parindent}}{{0pt}}
\setlength{{\parskip}}{{0pt}}

\begin{{document}}

\noindent
\textbf{{{numero}.}}

\vspace{{0.2cm}}
"""


def latex_a_png(latex, numero, tipo_hoja="carta"):
    tex = _encabezado_latex(numero, tipo_hoja) + fr"""
\noindent
\begin{{minipage}}[t]{{\dimexpr{PROPORCION_ANCHO_PREGUNTA:.6f}\textwidth-0.5em\relax}}
\vspace{{0pt}}
{latex}
\end{{minipage}}\hfill
\begin{{minipage}}[t]{{\dimexpr\textwidth-{PROPORCION_ANCHO_PREGUNTA:.6f}\textwidth-0.5em\relax}}
\vspace{{0pt}}
\setlength{{\fboxsep}}{{5mm}}
\setlength{{\fboxrule}}{{0.5pt}}
\fbox{{
\begin{{minipage}}[t][6cm][t]{{\dimexpr\linewidth-10mm-2\fboxrule-2\fboxsep\relax}}
\hspace{{0pt}}
\end{{minipage}}
}}
\end{{minipage}}

\end{{document}}
"""

    return _renderizar_latex_a_png(tex)


def latex_a_png_sin_recuadro(latex, numero, tipo_hoja="carta"):
    tex = _encabezado_latex(numero, tipo_hoja) + fr"""
\noindent
{latex}
\par

\end{{document}}
"""

    return _renderizar_latex_a_png(tex)


def _calcular_dimensiones_frame(ruta_imagen):

    img = Image.open(ruta_imagen)
    px_w, px_h = img.size

    dpi = 300
    cm_w = (px_w / dpi) * 2.54
    cm_h = (px_h / dpi) * 2.54

    ancho_final = max(cm_w, 1.0)
    alto_final = max(cm_h, 1.0)

    return ancho_final, alto_final

# =========================================================
# INSERTAR PREGUNTA EN DOCUMENTO
# =========================================================

def insertar_pregunta(archivo_odt, ruta_imagen, numero):

    if not os.path.exists(ruta_imagen):
        raise RuntimeError("La imagen no existe.")

    doc = load(archivo_odt)

    parent = doc.text

    ancho_final, alto_final = _calcular_dimensiones_frame(ruta_imagen)

    href = doc.addPicture(ruta_imagen)

    frame = Frame(
        width=f"{ancho_final:.2f}cm",
        height=f"{alto_final:.2f}cm",
        anchortype="as-char"
    )

    frame.setAttribute("name", f"Pregunta_{numero}")

    image = OdfImage(href=href)
    frame.addElement(image)

    # Reuse the template body paragraph style so the image starts as far
    # to the left as the document layout allows.
    p = P(stylename="P1")
    p.addElement(frame)

    parent.addElement(p)

    doc.save(archivo_odt)


def reemplazar_pregunta(archivo_odt, ruta_imagen, numero):

    doc = load(archivo_odt)

    for frame in doc.getElementsByType(Frame):

        nombre = frame.getAttribute("name")

        if nombre == f"Pregunta_{numero}":

            href = doc.addPicture(ruta_imagen)
            ancho_final, alto_final = _calcular_dimensiones_frame(ruta_imagen)

            # Eliminar imagen anterior
            for img in frame.getElementsByType(OdfImage):
                frame.removeChild(img)

            frame.setAttribute("width", f"{ancho_final:.2f}cm")
            frame.setAttribute("height", f"{alto_final:.2f}cm")

            # Insertar nueva
            nueva_img = OdfImage(href=href)
            frame.addElement(nueva_img)

            doc.save(archivo_odt)
            return True

    return False


def actualizar_pregunta_en_odt(archivo_odt, numero_original, ruta_imagen, numero_nuevo):

    doc = load(archivo_odt)

    for frame in doc.getElementsByType(Frame):

        nombre = frame.getAttribute("name")

        if nombre == f"Pregunta_{numero_original}":

            href = doc.addPicture(ruta_imagen)
            ancho_final, alto_final = _calcular_dimensiones_frame(ruta_imagen)

            for img in frame.getElementsByType(OdfImage):
                frame.removeChild(img)

            frame.setAttribute("name", f"Pregunta_{numero_nuevo}")
            frame.setAttribute("width", f"{ancho_final:.2f}cm")
            frame.setAttribute("height", f"{alto_final:.2f}cm")
            frame.addElement(OdfImage(href=href))

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
