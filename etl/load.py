import sqlite3
import pandas as pd

DATABASE_PATH = r"D:/batsej_open_company/data/database.sqlite"

def conectar_db():
    """Establece conexión con la base de datos SQLite."""
    return sqlite3.connect(DATABASE_PATH)

def cargar_sql(ruta_sql):
    """Carga una consulta SQL desde un archivo."""
    with open(ruta_sql, "r", encoding="utf-8") as file:
        return file.read()

def ejecutar_query(query, params=()):
    """Ejecuta una consulta SQL con parámetros y devuelve un DataFrame."""
    conn = conectar_db()
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def obtener_apicalls_por_mes_anio(anio, mes, commerce_ids):
    """Obtiene registros de API Calls por mes y año específicos para múltiples comercios."""
    query = cargar_sql("sql/get_apicalls_by_month_year.sql")
    
    # Si hay varios commerce_ids, construimos una consulta con IN (...)
    placeholders = ",".join("?" * len(commerce_ids))
    query = query.replace("commerce_id = ?", f"commerce_id IN ({placeholders})")

    params = [f"{anio}-{mes:02d}%"] + list(commerce_ids)
    return ejecutar_query(query, params=params)

def obtener_apicalls_por_anio(anio, commerce_ids):
    """Obtiene registros de API Calls por año específico para múltiples comercios."""
    query = cargar_sql("sql/get_apicalls_by_year.sql")
    
    placeholders = ",".join("?" * len(commerce_ids))
    query = query.replace("commerce_id = ?", f"commerce_id IN ({placeholders})")

    params = [f"{anio}%"] + list(commerce_ids)
    return ejecutar_query(query, params=params)

def obtener_apicalls_historico(commerce_ids):
    """Obtiene todos los registros de API Calls para múltiples comercios."""
    query = cargar_sql("sql/get_apicalls_historical.sql")

    placeholders = ",".join("?" * len(commerce_ids))
    query = query.replace("commerce_id = ?", f"commerce_id IN ({placeholders})")

    return ejecutar_query(query, params=list(commerce_ids))

def obtener_comercios():
    """Obtiene la lista de comercios disponibles."""
    query = cargar_sql("sql/get_all_commerces.sql")
    return ejecutar_query(query)
