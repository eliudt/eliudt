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

    # ⭐ Obtener número REAL
    numero_actual = motor.obtener_numero(archivo_odt)

    preview_path = motor.latex_a_png(
        latex,
        numero_actual,
        tipo_hoja
)

    
    img = Image.open(preview_path)
    img.thumbnail((650, 650))

    img_tk = ImageTk.PhotoImage(img)

    label_img.config(image=img_tk)
    label_img.image = img_tk


# ---------------- Agregar pregunta ----------------

def agregar():

    global preview_path, numero_actual

    if not archivo_odt:
        messagebox.showwarning("Error", "No hay documento activo.")
        return

    latex = txt.get("1.0", tk.END).strip()

    if not latex:
        messagebox.showwarning("Error", "Escriba una pregunta.")
        return

    # ⭐ Recalcular número SIEMPRE
    numero_actual = motor.obtener_numero(archivo_odt)

    # ⭐ Generar imagen nuevamente
    preview_path = motor.latex_a_png(
        latex,
        numero_actual,
        tipo_hoja
    )

    if not os.path.exists(preview_path):
        messagebox.showerror("Error", "No se generó la imagen.")
        return

    # ⭐ Insertar en ODT
    motor.insertar_pregunta(
        archivo_odt,
        preview_path,
        numero_actual
    )

    # ⭐ Guardar en BD
    bd.guardar_pregunta(
        archivo_odt,
        numero_actual,
        latex,
        preview_path
    )

    messagebox.showinfo("Listo", "Pregunta agregada.")

    limpiar()

# ---------------- Limpiar ----------------

def limpiar():

    global preview_path, numero_actual

    txt.delete("1.0", tk.END)
    label_img.config(image="")
    label_img.image = None
    preview_path = None
    numero_actual = None


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


