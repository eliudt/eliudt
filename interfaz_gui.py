import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import motor_examen as motor
from tkinter import filedialog
import os
import subprocess
import sys
import bd_preguntas as bd


BASE = "evaluaciones"
archivo_odt = None
tipo_hoja = "carta"
preview_path = None
numero_actual = None
preview_window = None
archivo_visto_externamente = None


# =========================================================
# VENTANA PRINCIPAL
# =========================================================

root = tk.Tk()
root.title("Generador de Evaluaciones")
root.geometry("980x760")
root.configure(bg="#fff8f0")

numero_var = tk.StringVar()
con_procedimiento_var = tk.BooleanVar(value=True)

COLORES = {
    "fondo": "#fff8f0",
    "panel": "#fffdf8",
    "panel_sec": "#ffe9d6",
    "borde": "#f0c7a1",
    "texto": "#2f2a26",
    "texto_sec": "#7b6252",
    "acento": "#ff7a59",
    "acento_2": "#ffc15e",
    "exito": "#2a9d8f",
    "claro": "#fff3e6",
}

FUENTE_TITULO = ("Helvetica", 24, "bold")
FUENTE_SUBTITULO = ("Helvetica", 11)
FUENTE_LABEL = ("Helvetica", 11, "bold")
FUENTE_TEXTO = ("Helvetica", 11)
FUENTE_BOTON = ("Helvetica", 11, "bold")


def crear_boton(parent, texto, comando, bg, fg="white", width=16):
    return tk.Button(
        parent,
        text=texto,
        command=comando,
        width=width,
        bg=bg,
        fg=fg,
        activebackground=bg,
        activeforeground=fg,
        relief="flat",
        bd=0,
        padx=14,
        pady=10,
        cursor="hand2",
        font=FUENTE_BOTON
    )


def maximizar_ventana(ventana):

    try:
        ventana.state("zoomed")
        return
    except tk.TclError:
        pass

    try:
        ventana.attributes("-zoomed", True)
        return
    except tk.TclError:
        pass

    ancho = ventana.winfo_screenwidth()
    alto = ventana.winfo_screenheight()
    ventana.geometry(f"{ancho}x{alto}+0+0")


main = tk.Frame(root, bg=COLORES["fondo"], padx=28, pady=24)
main.pack(fill="both", expand=True)

header = tk.Frame(main, bg=COLORES["fondo"])
header.pack(fill="x", pady=(0, 18))

tk.Label(
    header,
    text="Generador de Evaluaciones",
    bg=COLORES["fondo"],
    fg=COLORES["texto"],
    font=FUENTE_TITULO
).pack(anchor="w")

tk.Label(
    header,
    text="Crea, previsualiza y organiza preguntas en un espacio mas limpio y agradable.",
    bg=COLORES["fondo"],
    fg=COLORES["texto_sec"],
    font=FUENTE_SUBTITULO
).pack(anchor="w", pady=(4, 0))

info_card = tk.Frame(
    main,
    bg=COLORES["panel_sec"],
    highlightbackground=COLORES["borde"],
    highlightthickness=1,
    padx=18,
    pady=16
)
info_card.pack(fill="x", pady=(0, 18))

tk.Label(
    info_card,
    text="Documento Activo",
    bg=COLORES["panel_sec"],
    fg=COLORES["texto"],
    font=("Helvetica", 14, "bold")
).pack(anchor="w")

label_ruta = tk.Label(
    info_card,
    text="Ruta: —",
    bg=COLORES["panel_sec"],
    fg=COLORES["texto_sec"],
    font=FUENTE_TEXTO
)
label_ruta.pack(anchor="w", pady=(10, 2))

label_archivo = tk.Label(
    info_card,
    text="Archivo: —",
    bg=COLORES["panel_sec"],
    fg=COLORES["texto_sec"],
    font=FUENTE_TEXTO
)
label_archivo.pack(anchor="w", pady=2)

stats_row = tk.Frame(info_card, bg=COLORES["panel_sec"])
stats_row.pack(fill="x", pady=(12, 0))

label_total = tk.Label(
    stats_row,
    text="Preguntas en el documento: 0",
    bg=COLORES["claro"],
    fg=COLORES["texto"],
    font=FUENTE_TEXTO,
    padx=12,
    pady=8
)
label_total.pack(side=tk.LEFT, padx=(0, 10))

label_sugerencia = tk.Label(
    stats_row,
    text="Sugerido: 1",
    bg=COLORES["claro"],
    fg=COLORES["acento"],
    font=FUENTE_TEXTO,
    padx=12,
    pady=8
)
label_sugerencia.pack(side=tk.LEFT)

editor_card = tk.Frame(
    main,
    bg=COLORES["panel"],
    highlightbackground=COLORES["borde"],
    highlightthickness=1,
    padx=20,
    pady=18
)
editor_card.pack(fill="both", expand=True)

top_controls = tk.Frame(editor_card, bg=COLORES["panel"])
top_controls.pack(fill="x", pady=(0, 14))

frame_numero = tk.Frame(top_controls, bg=COLORES["panel"])
frame_numero.pack(side=tk.LEFT)

tk.Label(
    frame_numero,
    text="Numero de pregunta",
    bg=COLORES["panel"],
    fg=COLORES["texto"],
    font=FUENTE_LABEL
).pack(anchor="w")

entry_numero = tk.Entry(
    frame_numero,
    textvariable=numero_var,
    width=12,
    relief="flat",
    highlightthickness=1,
    highlightbackground=COLORES["borde"],
    highlightcolor=COLORES["acento"],
    bg="#ffffff",
    fg=COLORES["texto"],
    font=FUENTE_TEXTO
)
entry_numero.pack(anchor="w", pady=(6, 0), ipady=6)

options_frame = tk.Frame(top_controls, bg=COLORES["panel"])
options_frame.pack(side=tk.RIGHT, padx=(20, 0))

tk.Label(
    options_frame,
    text="Formato",
    bg=COLORES["panel"],
    fg=COLORES["texto"],
    font=FUENTE_LABEL
).pack(anchor="w")

tk.Checkbutton(
    options_frame,
    text="Con procedimiento",
    variable=con_procedimiento_var,
    bg=COLORES["panel"],
    fg=COLORES["texto_sec"],
    activebackground=COLORES["panel"],
    activeforeground=COLORES["texto"],
    selectcolor=COLORES["claro"],
    font=FUENTE_TEXTO
).pack(anchor="w", pady=(6, 0))

tk.Label(
    editor_card,
    text="Pregunta en LaTeX",
    bg=COLORES["panel"],
    fg=COLORES["texto"],
    font=FUENTE_LABEL
).pack(anchor="w")

txt = tk.Text(
    editor_card,
    width=90,
    height=15,
    state="disabled",
    relief="flat",
    wrap="word",
    highlightthickness=1,
    highlightbackground=COLORES["borde"],
    highlightcolor=COLORES["acento"],
    bg="#fffaf5",
    fg=COLORES["texto"],
    insertbackground=COLORES["texto"],
    font=("Courier New", 11)
)
txt.pack(fill="both", expand=True, pady=(8, 14))

frame_btn = tk.Frame(editor_card, bg=COLORES["panel"])
frame_btn.pack(fill="x")

label_img = tk.Label(editor_card, bg=COLORES["panel"])
label_img.pack(pady=(12, 0))


# =========================================================
# FUNCIONES
# =========================================================

def habilitar_editor():
    txt.config(state="normal")


def activar_documento(ruta, limpiar_editor=True):

    global archivo_odt, numero_actual

    archivo_odt = os.path.abspath(ruta)
    numero_actual = None

    label_ruta.config(text=f"Ruta: {archivo_odt}")
    label_archivo.config(
        text=f"Archivo: {os.path.basename(archivo_odt)}"
    )

    habilitar_editor()
    actualizar_info_documento(actualizar_numero=True)

    if limpiar_editor:
        txt.delete("1.0", tk.END)
        label_img.config(image="")
        label_img.image = None


def actualizar_info_documento(actualizar_numero=False):

    if not archivo_odt:
        label_total.config(text="Preguntas en el documento: 0")
        label_sugerencia.config(text="Sugerido: 1")
        if actualizar_numero:
            numero_var.set("")
        return

    numeros = motor.obtener_numeros_pregunta(archivo_odt)
    sugerido = motor.obtener_numero_sugerido(archivo_odt)

    label_total.config(
        text=f"Preguntas en el documento: {len(numeros)}"
    )
    label_sugerencia.config(
        text=f"Sugerido: {sugerido}"
    )

    if actualizar_numero:
        numero_var.set(str(sugerido))


def obtener_numero_ingresado():

    texto = numero_var.get().strip()

    if not texto:
        messagebox.showwarning(
            "Error",
            "Ingrese el número de la pregunta."
        )
        return None

    if not texto.isdigit():
        messagebox.showwarning(
            "Error",
            "El número de la pregunta debe ser un entero positivo."
        )
        return None

    numero = int(texto)

    if numero <= 0:
        messagebox.showwarning(
            "Error",
            "El número de la pregunta debe ser mayor que cero."
        )
        return None

    return numero


def generar_preview_pregunta(latex, numero):

    if con_procedimiento_var.get():
        return motor.latex_a_png(latex, numero, tipo_hoja)

    return motor.latex_a_png_sin_recuadro(latex, numero, tipo_hoja)


# ---------------- Vista previa ----------------

def cerrar_preview():

    global preview_window

    if preview_window and preview_window.winfo_exists():
        preview_window.destroy()

    preview_window = None


def _actualizar_panel_preview(img_tk, numero, latex):

    if not preview_window or not preview_window.winfo_exists():
        return

    canvas = preview_window.preview_canvas
    canvas.delete("all")
    canvas.create_image(24, 24, anchor="nw", image=img_tk)
    canvas.image = img_tk
    canvas.config(scrollregion=canvas.bbox("all"))

    modo = "Con procedimiento" if con_procedimiento_var.get() else "Sin procedimiento"

    preview_window.label_preview_numero.config(
        text=f"Pregunta #{numero}"
    )
    preview_window.label_preview_formato.config(
        text=f"Hoja: {tipo_hoja.capitalize()}  |  Vista: {modo}"
    )
    preview_window.label_preview_detalle.config(
        text=f"Longitud del contenido: {len(latex)} caracteres"
    )


def _crear_ventana_preview():

    global preview_window

    preview_window = tk.Toplevel(root)
    preview_window.title("Vista previa")
    preview_window.geometry("1320x760")
    preview_window.minsize(980, 620)
    preview_window.configure(bg=COLORES["fondo"])
    preview_window.after(100, lambda: maximizar_ventana(preview_window))

    header = tk.Frame(
        preview_window,
        bg=COLORES["fondo"],
        padx=24,
        pady=20
    )
    header.pack(fill="x")

    tk.Label(
        header,
        text="Vista previa de la pregunta",
        bg=COLORES["fondo"],
        fg=COLORES["texto"],
        font=("Helvetica", 20, "bold")
    ).pack(anchor="w")

    tk.Label(
        header,
        text="Revisa la composición antes de insertarla y ajusta lo necesario desde la pantalla principal.",
        bg=COLORES["fondo"],
        fg=COLORES["texto_sec"],
        font=FUENTE_SUBTITULO
    ).pack(anchor="w", pady=(4, 0))

    body = tk.Frame(
        preview_window,
        bg=COLORES["fondo"],
        padx=24,
        pady=0
    )
    body.pack(fill="both", expand=True)

    side_panel = tk.Frame(
        body,
        bg=COLORES["panel_sec"],
        highlightbackground=COLORES["borde"],
        highlightthickness=1,
        padx=18,
        pady=18,
        width=360
    )
    side_panel.pack(side=tk.LEFT, fill="y", padx=(0, 18))
    side_panel.pack_propagate(False)

    tk.Label(
        side_panel,
        text="Resumen",
        bg=COLORES["panel_sec"],
        fg=COLORES["texto"],
        font=("Helvetica", 14, "bold")
    ).pack(anchor="w")

    preview_window.label_preview_numero = tk.Label(
        side_panel,
        text="Pregunta #1",
        bg=COLORES["claro"],
        fg=COLORES["texto"],
        font=("Helvetica", 12, "bold"),
        padx=12,
        pady=10
    )
    preview_window.label_preview_numero.pack(fill="x", pady=(14, 10))

    preview_window.label_preview_formato = tk.Label(
        side_panel,
        text="Hoja: Carta",
        bg=COLORES["claro"],
        fg=COLORES["texto_sec"],
        font=FUENTE_TEXTO,
        justify="left",
        anchor="w",
        wraplength=300,
        padx=12,
        pady=10
    )
    preview_window.label_preview_formato.pack(fill="x", pady=(0, 10))

    preview_window.label_preview_detalle = tk.Label(
        side_panel,
        text="Longitud del contenido: 0 caracteres",
        bg=COLORES["claro"],
        fg=COLORES["texto_sec"],
        font=FUENTE_TEXTO,
        justify="left",
        anchor="w",
        wraplength=300,
        padx=12,
        pady=10
    )
    preview_window.label_preview_detalle.pack(fill="x", pady=(0, 18))

    tk.Label(
        side_panel,
        text="Acciones",
        bg=COLORES["panel_sec"],
        fg=COLORES["texto"],
        font=("Helvetica", 13, "bold")
    ).pack(anchor="w", pady=(4, 10))

    crear_boton(
        side_panel,
        "Actualizar vista",
        vista_previa,
        COLORES["acento_2"],
        fg=COLORES["texto"],
        width=20
    ).pack(fill="x", pady=(0, 10))

    crear_boton(
        side_panel,
        "Agregar pregunta",
        lambda: (agregar(), cerrar_preview()),
        COLORES["exito"],
        width=20
    ).pack(fill="x", pady=(0, 10))

    crear_boton(
        side_panel,
        "Limpiar editor",
        limpiar,
        COLORES["acento"],
        width=20
    ).pack(fill="x", pady=(0, 10))

    crear_boton(
        side_panel,
        "Cerrar vista",
        cerrar_preview,
        COLORES["texto_sec"],
        width=20
    ).pack(fill="x")

    tk.Label(
        side_panel,
        text='Tip: edita el contenido en la ventana principal y luego usa "Actualizar vista" para comparar cambios.',
        bg=COLORES["panel_sec"],
        fg=COLORES["texto_sec"],
        font=("Helvetica", 10),
        justify="left",
        wraplength=300
    ).pack(anchor="w", pady=(18, 0))

    preview_card = tk.Frame(
        body,
        bg=COLORES["panel"],
        highlightbackground=COLORES["borde"],
        highlightthickness=1,
        padx=16,
        pady=16
    )
    preview_card.pack(side=tk.LEFT, fill="both", expand=True)

    preview_top = tk.Frame(preview_card, bg=COLORES["panel"])
    preview_top.pack(fill="x", pady=(0, 12))

    tk.Label(
        preview_top,
        text="Resultado renderizado",
        bg=COLORES["panel"],
        fg=COLORES["texto"],
        font=("Helvetica", 14, "bold")
    ).pack(side=tk.LEFT)

    tk.Label(
        preview_top,
        text="Usa la rueda del mouse para revisar toda la pregunta.",
        bg=COLORES["panel"],
        fg=COLORES["texto_sec"],
        font=("Helvetica", 10)
    ).pack(side=tk.RIGHT)

    canvas_wrap = tk.Frame(
        preview_card,
        bg=COLORES["claro"],
        highlightbackground=COLORES["borde"],
        highlightthickness=1
    )
    canvas_wrap.pack(fill="both", expand=True)

    v_scroll = tk.Scrollbar(canvas_wrap, orient=tk.VERTICAL)
    v_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    h_scroll = tk.Scrollbar(canvas_wrap, orient=tk.HORIZONTAL)
    h_scroll.pack(side=tk.BOTTOM, fill=tk.X)

    canvas = tk.Canvas(
        canvas_wrap,
        bg="#fffaf5",
        bd=0,
        highlightthickness=0,
        yscrollcommand=v_scroll.set,
        xscrollcommand=h_scroll.set
    )
    canvas.pack(side=tk.LEFT, fill="both", expand=True)

    v_scroll.config(command=canvas.yview)
    h_scroll.config(command=canvas.xview)

    def _on_config(_event):
        canvas.config(scrollregion=canvas.bbox("all"))

    def _on_mousewheel(event):
        paso = -1 if event.delta > 0 else 1
        if event.state & 0x0001:
            canvas.xview_scroll(paso, "units")
        else:
            canvas.yview_scroll(paso, "units")

    def _on_linux_scroll_up(_event):
        canvas.yview_scroll(-1, "units")

    def _on_linux_scroll_down(_event):
        canvas.yview_scroll(1, "units")

    def _on_linux_shift_scroll_up(_event):
        canvas.xview_scroll(-1, "units")

    def _on_linux_shift_scroll_down(_event):
        canvas.xview_scroll(1, "units")

    canvas.bind("<Configure>", _on_config)
    canvas.bind_all("<MouseWheel>", _on_mousewheel)
    canvas.bind_all("<Button-4>", _on_linux_scroll_up)
    canvas.bind_all("<Button-5>", _on_linux_scroll_down)
    canvas.bind_all("<Shift-Button-4>", _on_linux_shift_scroll_up)
    canvas.bind_all("<Shift-Button-5>", _on_linux_shift_scroll_down)

    def _al_cerrar():
        canvas.unbind_all("<MouseWheel>")
        canvas.unbind_all("<Button-4>")
        canvas.unbind_all("<Button-5>")
        canvas.unbind_all("<Shift-Button-4>")
        canvas.unbind_all("<Shift-Button-5>")
        cerrar_preview()

    preview_window.preview_canvas = canvas
    preview_window.protocol("WM_DELETE_WINDOW", _al_cerrar)

def vista_previa():

    global preview_path

    if not archivo_odt:
        messagebox.showwarning("Error", "Primero cree un documento.")
        return

    latex = txt.get("1.0", tk.END).strip()

    if not latex:
        messagebox.showwarning("Error", "Escriba una pregunta.")
        return

    numero = obtener_numero_ingresado()

    if numero is None:
        return

    preview_path = generar_preview_pregunta(latex, numero)

    # Abrir la imagen y preparar una vista amplia con scroll
    img = Image.open(preview_path)
    img.thumbnail((1800, 1800))

    img_tk = ImageTk.PhotoImage(img)

    global preview_window

    if preview_window and preview_window.winfo_exists():
        preview_window.lift()
        _actualizar_panel_preview(img_tk, numero, latex)
        return

    _crear_ventana_preview()
    _actualizar_panel_preview(img_tk, numero, latex)


# ---------------- Agregar pregunta ----------------

def agregar():

    global preview_path, numero_actual
    global preview_window

    if not archivo_odt:
        messagebox.showwarning("Error", "No hay documento activo.")
        return

    latex = txt.get("1.0", tk.END).strip()

    if not latex:
        messagebox.showwarning("Error", "Escriba una pregunta.")
        return

    numero = obtener_numero_ingresado()

    if numero is None:
        return

    if numero_actual is None and motor.pregunta_existe(archivo_odt, numero):
        reemplazar = messagebox.askyesno(
            "Número existente",
            f"La pregunta {numero} ya existe. ¿Desea reemplazarla?"
        )

        if not reemplazar:
            return

    if numero_actual is not None and numero != numero_actual:
        if motor.pregunta_existe(archivo_odt, numero):
            messagebox.showerror(
                "Error",
                f"Ya existe una pregunta con el número {numero}."
            )
            return

    # ⭐ Generar imagen
    preview_path = generar_preview_pregunta(latex, numero)

    if not os.path.exists(preview_path):
        messagebox.showerror("Error", "No se generó la imagen.")
        return

    if numero_actual is not None:
        updated = motor.actualizar_pregunta_en_odt(
            archivo_odt,
            numero_actual,
            preview_path,
            numero
        )

        if not updated:
            motor.insertar_pregunta(archivo_odt, preview_path, numero)

        bd.actualizar_pregunta(
            archivo_odt,
            numero_actual,
            numero,
            latex,
            preview_path
        )
    else:
        if motor.pregunta_existe(archivo_odt, numero):
            replaced = motor.reemplazar_pregunta(archivo_odt, preview_path, numero)

            if replaced:
                bd.actualizar_pregunta(
                    archivo_odt,
                    numero,
                    numero,
                    latex,
                    preview_path
                )
            else:
                motor.insertar_pregunta(archivo_odt, preview_path, numero)
                bd.guardar_pregunta(archivo_odt, numero, latex, preview_path)
        else:
            motor.insertar_pregunta(archivo_odt, preview_path, numero)
            bd.guardar_pregunta(archivo_odt, numero, latex, preview_path)

    refrescar_vista_externa()
    messagebox.showinfo("Listo", "Pregunta agregada.")

    # Cerrar ventana de vista previa si está abierta
    if preview_window and preview_window.winfo_exists():
        preview_window.destroy()
    preview_window = None

    # Limpiar editor y resetear estado de edición
    limpiar()
    numero_actual = None
    actualizar_info_documento(actualizar_numero=True)

# ---------------- Limpiar ----------------

def limpiar():

    global preview_path, numero_actual
    global preview_window

    txt.delete("1.0", tk.END)
    label_img.config(image="")
    label_img.image = None
    con_procedimiento_var.set(True)
    preview_path = None
    numero_actual = None
    actualizar_info_documento(actualizar_numero=True)
    # Cerrar ventana de vista previa si existe
    if preview_window and preview_window.winfo_exists():
        preview_window.destroy()
    preview_window = None


def obtener_directorio_evaluaciones():

    ruta_base = os.path.abspath(BASE)

    if not os.path.isdir(ruta_base):
        os.makedirs(ruta_base, exist_ok=True)

    return ruta_base


def abrir_en_visor_sistema(ruta):

    if sys.platform.startswith("linux"):
        subprocess.Popen(["xdg-open", ruta])
    elif sys.platform == "darwin":
        subprocess.Popen(["open", ruta])
    elif os.name == "nt":
        os.startfile(ruta)
    else:
        raise OSError("Sistema operativo no compatible")


def refrescar_vista_externa():

    if not archivo_odt or archivo_visto_externamente != archivo_odt:
        return

    try:
        abrir_en_visor_sistema(archivo_odt)
    except Exception:
        pass


def ver_evaluacion():

    global archivo_visto_externamente

    ruta = filedialog.askopenfilename(
        title="Ver evaluación",
        initialdir=obtener_directorio_evaluaciones(),
        filetypes=[("Documentos ODT", "*.odt")]
    )

    if not ruta:
        return

    try:
        archivo_visto_externamente = os.path.abspath(ruta)
        abrir_en_visor_sistema(archivo_visto_externamente)
    except Exception as exc:
        messagebox.showerror(
            "Error",
            f"No se pudo abrir la evaluación:\n{exc}"
        )


# =========================================================
# BOTONES PRINCIPALES
# =========================================================

crear_boton(
    frame_btn,
    "Vista previa",
    vista_previa,
    COLORES["acento_2"],
    fg=COLORES["texto"],
    width=15
).pack(side=tk.LEFT, padx=(0, 10))

crear_boton(
    frame_btn,
    "Agregar pregunta",
    agregar,
    COLORES["exito"],
    width=18
).pack(side=tk.LEFT, padx=10)

crear_boton(
    frame_btn,
    "Limpiar",
    limpiar,
    COLORES["acento"],
    width=12
).pack(side=tk.LEFT, padx=(10, 0))


# =========================================================
# NUEVO DOCUMENTO
# =========================================================

def nuevo_documento():

    ventana = tk.Toplevel(root)
    ventana.title("Crear nuevo documento")
    ventana.geometry("400x450")
    ventana.resizable(False, False)
    ventana.grab_set()

    cont = tk.Frame(ventana, padx=15, pady=10)
    cont.pack(fill="both", expand=True)

    tk.Label(cont, text="Curso:").pack(anchor="w")

    cursos = ["Septimo C", "Octavo A", "Noveno A", "Noveno B"]
    curso_var = tk.StringVar(value=cursos[0])

    tk.OptionMenu(cont, curso_var, *cursos).pack(fill="x", pady=5)

    tk.Label(cont, text="Tamaño de hoja:").pack(anchor="w", pady=(10,0))

    hoja_var = tk.StringVar(value="carta")

    tk.Radiobutton(cont, text="Carta",
                   variable=hoja_var, value="carta").pack(anchor="w")

    tk.Radiobutton(cont, text="Oficio",
                   variable=hoja_var, value="oficio").pack(anchor="w")

    tk.Label(cont, text="Año:").pack(anchor="w", pady=(10,0))
    entry_anio = tk.Entry(cont)
    entry_anio.insert(0, "2026")
    entry_anio.pack(fill="x")

    tk.Label(cont, text="Período:").pack(anchor="w", pady=(10,0))
    entry_periodo = tk.Entry(cont)
    entry_periodo.insert(0, "1")
    entry_periodo.pack(fill="x")


    # ---------- Crear documento ----------

    def crear_documento():

        global archivo_odt, tipo_hoja

        curso = curso_var.get()
        tipo_hoja = hoja_var.get()
        anio = entry_anio.get()
        periodo = entry_periodo.get()

        archivo_odt = motor.crear_evaluacion(
            BASE, curso, periodo, anio
        )

        label_ruta.config(text=f"Ruta: {archivo_odt}")
        label_archivo.config(
            text=f"Archivo: {archivo_odt.split('/')[-1]}"
        )

        habilitar_editor()
        actualizar_info_documento(actualizar_numero=True)

        messagebox.showinfo("Listo", "Documento creado.")
        ventana.destroy()


    botones = tk.Frame(cont)
    botones.pack(fill="x", pady=25)

    tk.Button(botones,
              text="Crear documento",
              command=crear_documento,
              bg="#4CAF50",
              fg="white",
              height=2).pack(side="left",
                             expand=True,
                             fill="x",
                             padx=5)

    tk.Button(botones,
              text="Cancelar",
              command=ventana.destroy,
              height=2).pack(side="left",
                             expand=True,
                             fill="x",
                             padx=5)

# =========================================================
# EDITAR EVALUACION
# =========================================================

def editar_evaluacion():

    ruta = filedialog.askopenfilename(
        title="Seleccionar evaluación",
        initialdir=obtener_directorio_evaluaciones(),
        filetypes=[("Documentos ODT", "*.odt")]
    )

    if not ruta:
        return

    activar_documento(ruta)

    messagebox.showinfo(
        "Evaluación cargada",
        "La evaluación quedó abierta para seguir agregando preguntas."
    )


# =========================================================
# MENÚ PRINCIPAL
# =========================================================

menu_bar = tk.Menu(root)

menu_archivo = tk.Menu(menu_bar, tearoff=0)
menu_archivo.add_command(
    label="Nuevo documento",
    command=nuevo_documento
)
menu_archivo.add_command(
    label="Editar evaluación",
    command=editar_evaluacion
)

menu_herramientas = tk.Menu(menu_bar, tearoff=0)
menu_herramientas.add_command(
    label="Ver evaluación",
    command=ver_evaluacion
)

menu_bar.add_cascade(label="Archivo",
                     menu=menu_archivo)
menu_bar.add_cascade(label="Herramientas",
                     menu=menu_herramientas)

root.config(menu=menu_bar)

root.after(100, lambda: maximizar_ventana(root))
root.mainloop()
