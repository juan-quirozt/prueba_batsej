import sqlite3
import pandas as pd

DATABASE_PATH = r"D:/batsej_open_company/data/database.sqlite"

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

def seleccionar_empresas():
    """Permite al usuario seleccionar las empresas que desea facturar."""
    print("\nSeleccione las empresas que desea facturar:")
    print("0. Todas las empresas Activas")
    print("1. Todas las empresas Inactivas")
    print("2. Seleccionar una empresa")
    print("3. Seleccionar varias empresas")

    opcion = input("Ingrese una opción (0-3): ").strip()

    if opcion == "0":
        selected_commerce_ids = obtener_comercios_por_estado("Active")
    elif opcion == "1":
        selected_commerce_ids = obtener_comercios_por_estado("Inactive")
    elif opcion == "2":
        comercios = obtener_todos_los_comercios()
        print("\nLista de empresas:")
        for idx, (commerce_id, name) in enumerate(comercios):
            print(f"{idx}. {name}")
        seleccion = int(input("\nSeleccione el número de la empresa: ").strip())
        selected_commerce_ids = [comercios[seleccion][0]]
    elif opcion == "3":
        comercios = obtener_todos_los_comercios()
        print("\nLista de empresas:")
        for idx, (commerce_id, name) in enumerate(comercios):
            print(f"{idx}. {name}")
        indices = input("\nIngrese los números de las empresas separadas por comas: ").strip()
        selected_commerce_ids = [comercios[int(i)][0] for i in indices.split(",")]
    else:
        print("❌ Opción no válida. Intente de nuevo.")
        return seleccionar_empresas()

    return selected_commerce_ids


def filtrar_por_fecha(selected_commerce_ids):
    """Filtra la información según el rango de fecha elegido por el usuario."""
    print("\nSeleccione el rango de fecha:")
    print("0. Año/Mes")
    print("1. Año")
    print("2. Todo el histórico")

    opcion = input("Ingrese una opción (0-2): ").strip()

    if opcion == "0":
        año = input("Ingrese el año (YYYY): ").strip()
        mes = input("Ingrese el mes (MM): ").strip()
        query = """
            SELECT * FROM apicall
            WHERE commerce_id IN ({})
            AND strftime('%Y', date_api_call) = ?
            AND strftime('%m', date_api_call) = ?
        """.format(",".join("?" * len(selected_commerce_ids)))
        params = selected_commerce_ids + [año, mes]

    elif opcion == "1":
        año = input("Ingrese el año (YYYY): ").strip()
        query = """
            SELECT * FROM apicall
            WHERE commerce_id IN ({})
            AND strftime('%Y', date_api_call) = ?
        """.format(",".join("?" * len(selected_commerce_ids)))
        params = selected_commerce_ids + [año]

    elif opcion == "2":
        query = """
            SELECT * FROM apicall
            WHERE commerce_id IN ({})
        """.format(",".join("?" * len(selected_commerce_ids)))
        params = selected_commerce_ids

    else:
        print("❌ Opción no válida. Intente de nuevo.")
        return filtrar_por_fecha(selected_commerce_ids)

    conn = conectar_db()
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    
    return df

########### AGRUPACION DE DATOS


def agrupar_datos(df):
    """Agrupa el DataFrame por Año-Mes y Empresa, contando los 'Successful' y 'Unsuccessful'."""
    
    # Agregar columna de Año-Mes
    df["year_month"] = pd.to_datetime(df["date_api_call"]).dt.strftime("%Y-%m")

    # Agrupar por Año-Mes y Empresa, contando los estados
    df_grouped = df.groupby(["year_month", "commerce_id"])["ask_status"].value_counts().unstack(fill_value=0)

    # Renombrar columnas para mayor claridad
    df_grouped = df_grouped.rename(columns={"Successful": "Success_Count", "Unsuccessful": "Unsuccess_Count"}).reset_index()

    return df_grouped


############### FACTURACION

from collections import namedtuple

# Definimos la estructura de los valores de tarifa
Tarifa = namedtuple("Tarifa", ["valor", "limite"])

def obtener_tarifas_por_empresa(df):
    tarifas_por_empresa = {}

    for commerce_id, group in df.groupby("commerce_id"):
        # Ordenar por min_limit_success en orden descendente
        tarifas_ordenadas = sorted(
            group[["price_success", "min_limit_success"]].to_records(index=False),
            key=lambda x: x[1],  # Ordenamos por min_limit_success
            reverse=True
        )

        # Convertimos la lista en una tupla de namedtuples
        tarifas_por_empresa[commerce_id] = [Tarifa(valor=row[0], limite=row[1]) for row in tarifas_ordenadas]

    return tarifas_por_empresa

def calcular_facturacion(llamados_exitosos, tarifas):
    suma = 0

    for tarifa in tarifas:
        total_llamados_paso = max(llamados_exitosos - tarifa.limite, 0)
        suma += tarifa.valor * total_llamados_paso
        llamados_exitosos -= total_llamados_paso

    return suma

def generar_facturacion(df_agrupado, df_contract_success):
    """Genera el DataFrame de facturación basado en las tarifas de cada empresa."""
    
    # Obtener tarifas por empresa
    tarifas_por_empresa = obtener_tarifas_por_empresa(df_contract_success)

    # Lista para almacenar los resultados
    facturas = []

    for _, row in df_agrupado.iterrows():
        commerce_id = row["commerce_id"]
        total_exitosos = row["Success_Count"]
        total_no_exitosos = row["Unsuccess_Count"]

        # Obtener tarifas de la empresa (si no existen, usar tarifa 0)
        tarifas = tarifas_por_empresa.get(commerce_id, [Tarifa(0, 0)])

        # Calcular facturación
        total_facturado = calcular_facturacion(total_exitosos, tarifas)

        # Agregar datos al resultado
        facturas.append({
            "commerce_id": commerce_id,
            "total_llamados_exitosos": total_exitosos,
            "total_llamados_no_exitosos": total_no_exitosos,
            "total_facturado": total_facturado
        })

    # Convertir la lista en DataFrame
    df_factura = pd.DataFrame(facturas)
    
    return df_factura



#####
data_contract_success = {
    'commerce_id': ['KaSn-4LHo-m6vC-I4PU',
                        'Rh2k-J1o7-zndZ-cOo8',
                        'Vj9W-c4Pm-ja0X-fC1C',
                        'Vj9W-c4Pm-ja0X-fC1C',
                        'Vj9W-c4Pm-ja0X-fC1C',
                        '3VYd-4lzT-mTC3-DQN5',
                        '3VYd-4lzT-mTC3-DQN5',
                        'GdEQ-MGb7-LXHa-y6cd'],

    'commerce_name': ['Innovexa Solutions',
                        'QuantumLeap Inc',
                        'NexaTech Industries',
                        'NexaTech Industries',
                        'NexaTech Industries',
                        'Zenith Corp',
                        'Zenith Corp',
                        'FusionWave Enterprises'],

    'price_success': [300, 600, 250, 200, 170, 250, 130, 300],
    'min_limit_success': [0, 0, 0, 10000, 20000, 0, 22000, 0],
    }

df_contract_success = pd.DataFrame(data_contract_success)



####################### 🚀 EJECUCIÓN


# 🚀 EJECUCIÓN PRINCIPAL
selected_commerce_ids = seleccionar_empresas()
print("\n📌 Empresas seleccionadas:", selected_commerce_ids)

df_filtrado = filtrar_por_fecha(selected_commerce_ids)

print(df_filtrado[df_filtrado['ask_status'] == 'Successful'])

print("\n📌 DataFrame resultante:")
print(df_filtrado)

df_agrupado = agrupar_datos(df_filtrado)

print("\n📌 DataFrame Agrupado:")
print(df_agrupado.sort_values(by=['commerce_id', 'year_month'], ascending=[True, False]))


df_factura = generar_facturacion(df_agrupado, df_contract_success)

print("\n📌 DataFrame de Facturación:")
print(df_factura)