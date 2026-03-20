import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import motor_examen as motor
from tkinter import simpledialog
from tkinter import filedialog
import os
import bd_preguntas as bd


BASE = "evaluaciones"
archivo_odt = None
tipo_hoja = "carta"
preview_path = None
numero_actual = None
preview_window = None


# =========================================================
# VENTANA PRINCIPAL
# =========================================================

root = tk.Tk()
root.title("Generador de Evaluaciones")
root.geometry("750x650")


label_ruta = tk.Label(root, text="Ruta: —", fg="blue")
label_ruta.pack(pady=5)

label_archivo = tk.Label(root, text="Archivo: —", fg="blue")
label_archivo.pack(pady=5)


tk.Label(root, text="Pregunta en LaTeX:").pack()

txt = tk.Text(root, width=90, height=12, state="disabled")
txt.pack()


label_img = tk.Label(root)
label_img.pack(pady=10)


# =========================================================
# FUNCIONES
# =========================================================

def habilitar_editor():
    txt.config(state="normal")


# ---------------- Vista previa ----------------

def vista_previa():

    global preview_path, numero_actual

    if not archivo_odt:
        messagebox.showwarning("Error", "Primero cree un documento.")
        return

    latex = txt.get("1.0", tk.END).strip()

    if not latex:
        messagebox.showwarning("Error", "Escriba una pregunta.")
        return

    # ⭐ Obtener número REAL (si no estamos editando una pregunta)
    if numero_actual is None:
        numero_actual = motor.obtener_numero(archivo_odt)

    preview_path = motor.latex_a_png(
        latex,
        numero_actual,
        tipo_hoja
)

    
    # Abrir la imagen y preparar thumbnail razonable para mostrar
    img = Image.open(preview_path)
    # No limitar demasiado; la ventana tendrá scroll
    img.thumbnail((1200, 1200))

    img_tk = ImageTk.PhotoImage(img)

    # Crear ventana hija de vista previa
    global preview_window

    if preview_window and preview_window.winfo_exists():
        preview_window.lift()
        # actualizar imagen en la ventana existente
        try:
            canvas = preview_window.nametowidget("preview_canvas")
            canvas.delete("all")
            canvas.create_image(0, 0, anchor="nw", image=img_tk)
            canvas.image = img_tk
            canvas.config(scrollregion=canvas.bbox("all"))
        except Exception:
            pass
        return

    preview_window = tk.Toplevel(root)
    preview_window.title("Vista previa")
    preview_window.geometry("700x700")
    preview_window.transient(root)

    # Botones en la parte superior
    top_frame = tk.Frame(preview_window)
    top_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

    def cerrar_preview():
        global preview_window
        if preview_window and preview_window.winfo_exists():
            preview_window.destroy()
        preview_window = None

    tk.Button(top_frame, text="Agregar pregunta", command=lambda: (agregar(), cerrar_preview()), width=15).pack(side=tk.LEFT, padx=5)
    tk.Button(top_frame, text="Cerrar", command=cerrar_preview, width=12).pack(side=tk.LEFT, padx=5)

    # Contenedor con canvas y scrollbar vertical
    container = tk.Frame(preview_window)
    container.pack(fill="both", expand=True)

    v_scroll = tk.Scrollbar(container, orient=tk.VERTICAL)
    v_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    canvas = tk.Canvas(container, yscrollcommand=v_scroll.set, name="preview_canvas")
    canvas.pack(side=tk.LEFT, fill="both", expand=True)
    v_scroll.config(command=canvas.yview)

    # Insertar imagen en canvas
    canvas.create_image(0, 0, anchor="nw", image=img_tk)
    canvas.image = img_tk
    canvas.config(scrollregion=canvas.bbox("all"))

    # Soporte para redimensionar y actualizar scrollregion
    def _on_config(event):
        canvas.config(scrollregion=canvas.bbox("all"))

    canvas.bind("<Configure>", _on_config)


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

    # Si estamos editando una pregunta existente, usar ese número
    if numero_actual:
        numero = numero_actual
    else:
        # Nuevo: asignar siguiente número
        numero = motor.obtener_numero(archivo_odt) + 1

    # ⭐ Generar imagen
    preview_path = motor.latex_a_png(
        latex,
        numero,
        tipo_hoja
    )

    if not os.path.exists(preview_path):
        messagebox.showerror("Error", "No se generó la imagen.")
        return

    if numero_actual:
        # Reemplazar imagen en la posición existente
        replaced = motor.reemplazar_pregunta(archivo_odt, preview_path, numero)
        if not replaced:
            # Si no encontró la pregunta, insertar al final
            motor.insertar_pregunta(archivo_odt, preview_path, numero)
        # Actualizar BD
        bd.actualizar_pregunta(archivo_odt, numero, latex, preview_path)
    else:
        # Insertar nueva pregunta
        motor.insertar_pregunta(archivo_odt, preview_path, numero)
        bd.guardar_pregunta(archivo_odt, numero, latex, preview_path)

    messagebox.showinfo("Listo", "Pregunta agregada.")

    # Cerrar ventana de vista previa si está abierta
    if preview_window and preview_window.winfo_exists():
        preview_window.destroy()
    preview_window = None

    # Limpiar editor y resetear estado de edición
    limpiar()
    numero_actual = None

# ---------------- Limpiar ----------------

def limpiar():

    global preview_path, numero_actual
    global preview_window

    txt.delete("1.0", tk.END)
    label_img.config(image="")
    label_img.image = None
    preview_path = None
    numero_actual = None
    # Cerrar ventana de vista previa si existe
    if preview_window and preview_window.winfo_exists():
        preview_window.destroy()
    preview_window = None


# =========================================================
# BOTONES PRINCIPALES
# =========================================================

frame_btn = tk.Frame(root)
frame_btn.pack(pady=10)

tk.Button(frame_btn, text="Vista previa",
          command=vista_previa, width=15).pack(side=tk.LEFT, padx=5)

tk.Button(frame_btn, text="Agregar pregunta",
          command=agregar, width=18).pack(side=tk.LEFT, padx=5)

tk.Button(frame_btn, text="Limpiar",
          command=limpiar, width=12).pack(side=tk.LEFT, padx=5)


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
# EDITAR PREGUNTA
# =========================================================

def editar_pregunta():

    global archivo_odt, numero_actual

    ruta = filedialog.askopenfilename(
        title="Seleccionar evaluación",
        filetypes=[("Documentos ODT", "*.odt")]
    )

    if not ruta:
        return

    # ⭐ AQUÍ VA LA CONVERSIÓN
    archivo_odt = os.path.abspath(ruta)

    label_ruta.config(text=f"Ruta: {archivo_odt}")
    label_archivo.config(
        text=f"Archivo: {os.path.basename(archivo_odt)}"
    )

    numero = simpledialog.askinteger(
        "Editar pregunta",
        "Número de pregunta:"
    )

    if not numero:
        return

    fila = bd.obtener_pregunta(archivo_odt, numero)

    if not fila:
        messagebox.showerror(
            "Error",
            "No se encontró esa pregunta."
        )
        return

    latex, ruta_img, ruta_tex = fila

    txt.config(state="normal")
    txt.delete("1.0", tk.END)
    txt.insert("1.0", latex)

    numero_actual = numero

    messagebox.showinfo(
        "Editar",
        f"Editando pregunta {numero}"
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
    label="Editar pregunta",
    command=editar_pregunta
)


menu_bar.add_cascade(label="Archivo",
                     menu=menu_archivo)

root.config(menu=menu_bar)

root.mainloop()


