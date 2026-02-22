from odf.opendocument import load
from odf.text import P
from odf.draw import Frame, Image
from odf.style import Style, GraphicProperties
from PIL import Image as PILImage
import matplotlib.pyplot as plt


# =========================================================
# FUNCIÓN: LaTeX → imagen SIN márgenes
# =========================================================

def pregunta_latex_a_imagen(texto, archivo, fontsize=18):

    fig = plt.figure(figsize=(0.01, 0.01))

    text = fig.text(0, 0, texto, fontsize=fontsize, wrap=True)

    fig.canvas.draw()

    bbox = text.get_window_extent()
    bbox = bbox.transformed(fig.dpi_scale_trans.inverted())

    fig.set_size_inches(bbox.width, bbox.height)

    text.set_position((0, 0))

    plt.axis('off')

    plt.savefig(
        archivo,
        dpi=300,
        transparent=True,
        bbox_inches='tight',
        pad_inches=0
    )

    plt.close(fig)


# =========================================================
# PREGUNTA EN LATEX
# =========================================================

pregunta = (
    r"En un laboratorio, la concentración de una sustancia radiactiva "
    r"sigue el modelo $C(t)=C_0 e^{-0.03t}$, donde $C(t)$ es la "
    r"concentración al tiempo $t$ (en días). Si después de 50 días "
    r"la concentración es de 40 mg/L y se sabe que $C_0=100$ mg/L, "
    r"¿cuánto tiempo debe pasar para que la concentración sea de 20 mg/L?"
    "\n\n"
    r"a) 23 días"
    "\n"
    r"b) 100 días"
    "\n"
    r"c) 115 días"
    "\n"
    r"d) 134 días"
)

pregunta_latex_a_imagen(pregunta, "pregunta1.png")


# =========================================================
# OBTENER TAMAÑO REAL DE LA IMAGEN
# =========================================================

img_pil = PILImage.open("pregunta1.png")
px_w, px_h = img_pil.size

dpi = 300
cm_w = (px_w / dpi) * 2.54
cm_h = (px_h / dpi) * 2.54

ancho = f"{cm_w:.2f}cm"
alto = f"{cm_h:.2f}cm"


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

for p in doc.getElementsByType(P):
    if "<<PREGUNTAS>>" in str(p):

        parent = p.parentNode
        parent.removeChild(p)

        href = doc.addPicture("pregunta1.png")

        frame = Frame(
            stylename=style,
            width=ancho,
            height=alto,
            anchortype="as-char"
        )

        image = Image(href=href)
        frame.addElement(image)

        p_img = P()
        p_img.addElement(frame)

        parent.addElement(p_img)

        break


# =========================================================
# GUARDAR DOCUMENTO
# =========================================================

doc.save("examen_generado.odt")

print("✔ Pregunta insertada SIN distorsión.")
