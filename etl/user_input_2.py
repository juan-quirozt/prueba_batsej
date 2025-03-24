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
    
    while True:
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
            while True:    
                seleccion = input("\nSeleccione el número de la empresa: ").strip()
                if seleccion not in [str(x) for x in list(range(len(comercios)))]:
                    print("Elige un número de empresa válido")
                    continue
                selected_commerce_ids = [comercios[int(seleccion)][0]]
                break  
        elif opcion == "3":
            comercios = obtener_todos_los_comercios()
            print("\nLista de empresas:")
            for idx, (commerce_id, name) in enumerate(comercios):
                print(f"{idx}. {name}")
            while True:
                indices = input("\nIngrese los números de las empresas separadas por espacio: ").strip()
                if not all(x in [str(x) for x in list(range(len(comercios)))] for x in indices.split(' ')):
                    print("Ingrese una cadena válida de empresas")
                    continue
                selected_commerce_ids = [comercios[int(i)][0] for i in indices.split(" ")]
                break
        else:
            print("Opción no válida. Intente de nuevo.")
            continue

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
        0. anio/Mes
        1. anio
        2. Todo el histórico
        Ingrese una opción (0-2): 0
        Ingrese el anio (YYYY): 2024
        Ingrese el mes (MM): 03
        >>> print(df.head())
               date_api_call        commerce_id   ask_status    is_related
            0  2024-03-31 14:19:50  empresa_B_id  Successful    0.0
            1  2024-03-29 14:18:35  empresa_B_id  Successful    0.0
            2  2024-03-12 08:20:16  empresa_A_id  Unsuccessful  1.0
    """
    print("\nSeleccione el rango de fecha:")
    print("0. anio/Mes")
    print("1. anio")
    print("2. Todo el histórico")

    while True:
        opcion = input("Ingrese una opción (0-2): ").strip()

        if opcion == "0":
            while True:
                anio = input("Ingrese el anio (YYYY): ").strip()
                mes = input("Ingrese el mes (MM): ").strip()
                if len(mes) == 1:
                    mes = '0' + mes
                try:
                    anio_aux = int(anio)
                    mes_aux = int(mes)
                    if anio_aux < 0 or mes_aux not in list(range(1, 13)):
                        raise Exception()
                except:
                    print("El año no es válido")
                    continue
                
                query = """
                    SELECT * FROM apicall
                    WHERE commerce_id IN ({})
                    AND strftime('%Y', date_api_call) = ?
                    AND strftime('%m', date_api_call) = ?
                """.format(",".join("?" * len(selected_commerce_ids)))
                params = selected_commerce_ids + [anio, mes]
                break
            break

        elif opcion == "1":
            while True:
                anio = input("Ingrese el anio (YYYY): ").strip()
                try:
                    anio_aux = int(anio)
                    if anio_aux < 0:
                        raise Exception()
                except:
                    print("El año no es válido")
                    continue

                query = """
                    SELECT * FROM apicall
                    WHERE commerce_id IN ({})
                    AND strftime('%Y', date_api_call) = ?
                """.format(",".join("?" * len(selected_commerce_ids)))
                params = selected_commerce_ids + [anio]
                break
            break

        elif opcion == "2":
            query = """
                SELECT * FROM apicall
                WHERE commerce_id IN ({})
            """.format(",".join("?" * len(selected_commerce_ids)))
            params = selected_commerce_ids
            break

        else:
            print("Opción no válida. Intente de nuevo.")
            continue


    conn = conectar_db()
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    
    return df