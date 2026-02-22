import subprocess
from odf.opendocument import load
from odf.text import P
from odf.draw import Frame, Image
from odf.style import Style, GraphicProperties
from PIL import Image as PILImage


# =========================================================
# FUNCIÓN: LATEX → PNG NEGRO PURO
# =========================================================

def pregunta_a_imagen(latex_pregunta, nombre):

    tex = fr"""
\documentclass[12pt]{{article}}
\usepackage[spanish]{{babel}}
\usepackage{{amsmath, amssymb}}
\usepackage{{enumitem}}
\usepackage{{tikz}}
\usepackage{{pgfplots}}
\pgfplotsset{{compat=1.18}}
\usepackage[margin=1.5cm]{{geometry}}
\usepackage{{xcolor}}

\pagestyle{{empty}}
\setlength{{\parindent}}{{0pt}}
\color{{black}}

\begin{{document}}

{latex_pregunta}

\end{{document}}
"""

    with open(f"{nombre}.tex", "w") as f:
        f.write(tex)

    subprocess.run(["pdflatex", "-interaction=nonstopmode", f"{nombre}.tex"])
    subprocess.run(["pdfcrop", f"{nombre}.pdf", f"{nombre}_crop.pdf"])

    # Fondo blanco + negro sólido
    subprocess.run([
        "pdftoppm",
        "-png",
        "-r", "300",
        "-white",
        f"{nombre}_crop.pdf",
        nombre
    ])


# =========================================================
# PREGUNTA DE EJEMPLO
# =========================================================

preguntas = [

r"""
Una empresa de telecomunicaciones estudia la intensidad de la señal de un
transmisor según la distancia. El modelo es

\[
I(d) = 80 - 10 \log_{10}(d),
\]

donde \(d\) es la distancia en kilómetros.

\begin{center}
\begin{tikzpicture}
\begin{axis}[
    width=12cm,
    height=6cm,
    xmin=1, xmax=100,
    ymin=40, ymax=80,
    xlabel={Distancia (km)},
    ylabel={Intensidad (dB)},
    grid=both
]
\addplot[domain=1:100, samples=100] {80 - 10*log10(x)};
\end{axis}
\end{tikzpicture}
\end{center}

¿A qué distancia la intensidad será aproximadamente 60 dB?

\begin{enumerate}[label=\alph*)]
\item 10 km
\item 50 km
\item 100 km
\item 1000 km
\end{enumerate}
"""

]


# =========================================================
# GENERAR IMÁGENES
# =========================================================

imagenes = []

for i, p in enumerate(preguntas, start=1):
    nombre = f"pregunta{i}"
    pregunta_a_imagen(p, nombre)
    imagenes.append(f"{nombre}-1.png")


# =========================================================
# CARGAR PLANTILLA
# =========================================================

doc = load("plantilla_examen.odt")

style = Style(name="ImagenPregunta", family="graphic")
style.addElement(GraphicProperties())
doc.styles.addElement(style)


# =========================================================
# INSERTAR EN <<PREGUNTAS>>
# =========================================================

contador = 1

for p in doc.getElementsByType(P):
    if "<<PREGUNTAS>>" in str(p):

        parent = p.parentNode
        parent.removeChild(p)

        for img_path in imagenes:

            parent.addElement(P(text=f"{contador}."))

            img = PILImage.open(img_path)
            px_w, px_h = img.size

            dpi = 300
            cm_w = (px_w / dpi) * 2.54
            cm_h = (px_h / dpi) * 2.54

            href = doc.addPicture(img_path)

            frame = Frame(
                stylename=style,
                width=f"{cm_w:.2f}cm",
                height=f"{cm_h:.2f}cm",
                anchortype="as-char"
            )

            image = Image(href=href)
            frame.addElement(image)

            p_img = P()
            p_img.addElement(frame)

            parent.addElement(p_img)

            contador += 1

        break


# =========================================================
# GUARDAR
# =========================================================

doc.save("examen_generado.odt")

print("✔ Imagen con texto negro puro generada.")
