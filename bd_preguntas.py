import sqlite3
import os
from datetime import datetime


DB = "preguntas.db"
CARPETA_TEX = "res/preguntas_latex"


# =========================================================
# INICIALIZAR BASE DE DATOS
# =========================================================

def inicializar_bd():

    os.makedirs(CARPETA_TEX, exist_ok=True)

    con = sqlite3.connect(DB)
    cur = con.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS preguntas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        archivo_odt TEXT,
        numero INTEGER,
        latex TEXT,
        ruta_imagen TEXT,
        ruta_tex TEXT,
        fecha TEXT
    )
    """)

    con.commit()
    con.close()


# =========================================================
# GUARDAR NUEVA PREGUNTA
# =========================================================

def guardar_pregunta(archivo_odt, numero, latex, ruta_imagen):

    inicializar_bd()

    archivo_odt = os.path.abspath(archivo_odt)

    # Nombre único del TEX
    base = os.path.basename(archivo_odt).replace(".odt", "")
    nombre_tex = f"{base}_p{numero}.tex"

    ruta_tex = os.path.join(CARPETA_TEX, nombre_tex)

    with open(ruta_tex, "w", encoding="utf-8") as f:
        f.write(latex)

    con = sqlite3.connect(DB)
    cur = con.cursor()

    cur.execute("""
        INSERT INTO preguntas
        (archivo_odt, numero, latex, ruta_imagen, ruta_tex, fecha)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        archivo_odt,
        numero,
        latex,
        ruta_imagen,
        ruta_tex,
        datetime.now().isoformat()
    ))

    con.commit()
    con.close()


# =========================================================
# OBTENER PREGUNTA
# =========================================================

def obtener_pregunta(archivo_odt, numero):

    archivo_odt = os.path.abspath(archivo_odt)

    con = sqlite3.connect(DB)
    cur = con.cursor()

    cur.execute("""
        SELECT latex, ruta_imagen, ruta_tex
        FROM preguntas
        WHERE archivo_odt=? AND numero=?
        ORDER BY id DESC
        LIMIT 1
    """, (archivo_odt, numero))

    fila = cur.fetchone()
    con.close()

    return fila


# =========================================================
# ACTUALIZAR PREGUNTA EXISTENTE
# =========================================================

def actualizar_pregunta(archivo_odt, numero_original, numero_nuevo, latex, ruta_imagen):

    archivo_odt = os.path.abspath(archivo_odt)

    base = os.path.basename(archivo_odt).replace(".odt", "")
    nombre_tex = f"{base}_p{numero_nuevo}.tex"
    ruta_tex = os.path.join(CARPETA_TEX, nombre_tex)

    os.makedirs(CARPETA_TEX, exist_ok=True)

    with open(ruta_tex, "w", encoding="utf-8") as f:
        f.write(latex)

    con = sqlite3.connect(DB)
    cur = con.cursor()

    cur.execute("""
        UPDATE preguntas
        SET numero=?, latex=?, ruta_imagen=?, ruta_tex=?, fecha=?
        WHERE archivo_odt=? AND numero=?
    """, (
        numero_nuevo,
        latex,
        ruta_imagen,
        ruta_tex,
        datetime.now().isoformat(),
        archivo_odt,
        numero_original
    ))

    con.commit()
    con.close()
