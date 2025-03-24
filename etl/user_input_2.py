"""
user_input_2.py

Este módulo permite al usuario seleccionar empresas para facturación y filtrar 
la información según un rango de fechas determinado.

Funciones principales:
- `seleccionar_empresas()`: Permite al usuario seleccionar empresas activas, 
  inactivas o específicas para facturación.
- `filtrar_por_fecha(selected_commerce_ids)`: Filtra los registros de llamadas 
  según el rango de fechas definido por el usuario.

Dependencias:
- `pandas`: Para la manipulación de datos en DataFrames.
- `extract_1`: Se importan las funciones `conectar_db`, `obtener_comercios_por_estado` 
  y `obtener_todos_los_comercios` para la extracción de datos.

Uso:
Este módulo es parte del flujo ETL en el sistema de facturación y permite a los usuarios 
especificar qué datos desean procesar.

Autor: Juan Esteban Quiroz Taborda
Última modificación: 23 de marzo de 2025
"""


from etl.extract_1 import conectar_db, obtener_comercios_por_estado, obtener_todos_los_comercios
import pandas as pd

def seleccionar_empresas():
    """
    Permite al usuario seleccionar las empresas que desea facturar.

    Returns:
        List[str]: Una lista con los IDs de las empresas seleccionadas.

    Example:
        >>> empresas = seleccionar_empresas()
        Seleccione las empresas que desea facturar:
        0. Todas las empresas Activas
        1. Todas las empresas Inactivas
        2. Seleccionar una empresa
        3. Seleccionar varias empresas
        Ingrese una opción (0-3): 2
        Lista de empresas:
        0. Empresa A
        1. Empresa B
        2. Empresa C
        Seleccione el número de la empresa: 1
        >>> print(empresas)
        ['empresa_B_id']
    """    

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
    """
    Filtra la información según el rango de fecha elegido por el usuario.

    Params:
        selected_commerce_ids (List[str]): Lista de IDs de empresas seleccionadas.

    Return:
        pd.DataFrame: Un DataFrame con los registros filtrados por fecha.

    Example:
        >>> empresas = ["empresa_A_id", "empresa_B_id"]
        >>> df = filtrar_por_fecha(empresas)
        Seleccione el rango de fecha:
        0. Año/Mes
        1. Año
        2. Todo el histórico
        Ingrese una opción (0-2): 0
        Ingrese el año (YYYY): 2024
        Ingrese el mes (MM): 03
        >>> print(df.head())
               date_api_call        commerce_id   ask_status    is_related
            0  2024-03-31 14:19:50  empresa_B_id  Successful    0.0
            1  2024-03-29 14:18:35  empresa_B_id  Successful    0.0
            2  2024-03-12 08:20:16  empresa_A_id  Unsuccessful  1.0
    """
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