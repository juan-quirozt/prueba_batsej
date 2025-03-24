"""
1_extract.py

Módulo encargado de la extracción y limpieza de datos desde la base de datos.

Funciones principales:
- `extraer_datos_facturacion()`: Obtiene los datos de facturación desde la base de datos.
- `extraer_datos_tarifas()`: Obtiene las tarifas aplicables por empresa.
- `extraer_datos_descuentos()`: Obtiene las reglas de descuentos para llamadas no exitosas.
- `limpiar_datos(df)`: Realiza una limpieza básica de los datos extraídos.

Este módulo forma parte de un sistema de procesamiento de facturación, 
siguiendo el enfoque ETL (Extract, Transform, Load).

Autor: Juan Esteban Quiroz Taborda
Fecha: 23 de marzo de 2025
"""

import sqlite3
import pandas as pd

DATABASE_PATH = r"data/database.sqlite"

def conectar_db():
    """Establece conexión con la base de datos SQLite."""
    return sqlite3.connect(DATABASE_PATH)

def obtener_comercios_por_estado(estado):
    """Obtiene los IDs de los comercios que están en el estado seleccionado (Active o Inactive)."""
    query = "SELECT commerce_id FROM commerce WHERE commerce_status = ?"
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute(query, (estado,))
    ids = [row[0] for row in cursor.fetchall()]
    conn.close()
    return ids

def obtener_todos_los_comercios():
    """Obtiene todos los IDs de los comercios registrados en la base de datos."""
    query = "SELECT commerce_id, commerce_name FROM commerce"
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute(query)
    comercios = cursor.fetchall()
    conn.close()
    return comercios

def obtener_contrato_exitoso():
    """Obtiene los contratos de los comercios de los llamados exitosos y los devuelve como un DataFrame"""
    query = "SELECT * FROM contract_success"
    conn = conectar_db()
    cursor = conn.cursor()
    # Ejecutar la consulta
    cursor.execute(query)
    # Obtener los nombres de las columnas
    column_names = [desc[0] for desc in cursor.description]
    # Obtener los datos
    contratos = cursor.fetchall()
    # Cerrar conexión
    conn.close()

    # Convertir a DataFrame
    df = pd.DataFrame(contratos, columns=column_names)

    return df

def obtener_contrato_no_exitoso():
    """Obtiene los contratos de los comercios de los llamados no exitosos y los devuelve como un DataFrame"""
    query = "SELECT * FROM contract_unsuccess"
    conn = conectar_db()
    cursor = conn.cursor()
    # Ejecutar la consulta
    cursor.execute(query)
    # Obtener los nombres de las columnas
    column_names = [desc[0] for desc in cursor.description]
    # Obtener los datos
    contratos = cursor.fetchall()
    # Cerrar conexión
    conn.close()
    # Convertir a DataFrame
    df = pd.DataFrame(contratos, columns=column_names)

    return df

def obtener_info_comercios():
    """Obtiene la informacion de todos los comercios de los llamados no exitosos y los devuelve como un DataFrame"""
    query = "SELECT * FROM commerce"
    conn = conectar_db()
    cursor = conn.cursor()
    # Ejecutar la consulta
    cursor.execute(query)
    # Obtener los nombres de las columnas
    column_names = [desc[0] for desc in cursor.description]
    # Obtener los datos
    comercios = cursor.fetchall()
    # Cerrar conexión
    conn.close()
    # Convertir a DataFrame
    df = pd.DataFrame(comercios, columns=column_names)

    return df