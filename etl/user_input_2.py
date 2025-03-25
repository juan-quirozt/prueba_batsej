"""
user_input_2.py

Este módulo permite al usuario seleccionar empresas para facturación y filtrar 
la información según un rango de fechas determinado.

Funciones principales:
- `seleccionar_empresas()`: Permite al usuario seleccionar empresas activas, 
  inactivas o específicas para facturación.
- `filtrar_por_fecha(selected_commerce_ids)`: Filtra los registros de llamadas 
  según el rango de fechas definido por el usuario. Se pueden filtrar por año/mes, 
  solo por año o consultar todo el histórico.

Dependencias:
- `pandas`: Para la manipulación de datos en DataFrames.
- `extract_1`: Se importan las funciones `conectar_db`, `obtener_comercios_por_estado`, 
  `obtener_todos_los_comercios`, `obtener_anios` y `obtener_meses` para la extracción de datos.

Uso:
Este módulo es parte del flujo ETL en el sistema de facturación y permite a los usuarios 
especificar qué datos desean procesar.

Autor: Juan Esteban Quiroz Taborda
Última modificación: 24 de marzo de 2025
"""


from etl.extract_1 import conectar_db, obtener_comercios_por_estado, obtener_todos_los_comercios, obtener_anios, obtener_meses
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
        # Obtiene los comercios que están activos
        if opcion == "0":
            selected_commerce_ids = obtener_comercios_por_estado("Active")
        # Obtiene los comercios que están inactivos
        elif opcion == "1":
            selected_commerce_ids = obtener_comercios_por_estado("Inactive")
        elif opcion == "2":
            # Obtiene la lista de todos los comercios
            comercios = obtener_todos_los_comercios()
            print("\nLista de empresas:")

            # Muestra la lista de comercios con su índice
            for idx, (commerce_id, name) in enumerate(comercios):
                print(f"{idx}. {name}")
            while True:
                # Solicita al usuario seleccionar un comercio por su índice    
                seleccion = input("\nSeleccione el número de la empresa: ").strip()

                # Verifica que la selección sea un número válido dentro del rango de índices
                if seleccion not in [str(x) for x in list(range(len(comercios)))]:
                    print("Elige un número de empresa válido")
                    continue

                # Almacena el ID del comercio seleccionado
                selected_commerce_ids = [comercios[int(seleccion)][0]]
                break

        elif opcion == "3":
            # Obtiene la lista de todos los comercios
            comercios = obtener_todos_los_comercios()
            print("\nLista de empresas:")

            # Muestra la lista de comercios con su índice
            for idx, (commerce_id, name) in enumerate(comercios):
                print(f"{idx}. {name}")
            while True:
                # Solicita al usuario ingresar múltiples índices separados por espacio
                indices = input("\nIngrese los números de las empresas separadas por espacio: ").strip()

                # Verifica que todos los índices ingresados sean válidos
                if not all(x in [str(x) for x in list(range(len(comercios)))] for x in indices.split(' ')):
                    print("Ingrese una cadena válida de empresas")
                    continue

                # Almacena los IDs de los comercios seleccionados
                selected_commerce_ids = [comercios[int(i)][0] for i in indices.split(" ")]
                break
        else:
            print("Opción no válida. Intente de nuevo.")
            continue
        
        # Retorna los comercios seleccionados
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
            # Obtiene la lista de años disponibles
            anios = obtener_anios()
            
            while True:
                anio = input("Ingrese el anio (YYYY): ").strip()
                mes = input("Ingrese el mes (MM): ").strip()

                # Si el mes es de un solo dígito, se le agrega un '0' al inicio
                if len(mes) == 1:
                    mes = '0' + mes
                try:
                    # Verifica si el año ingresado está en la lista de años disponibles
                    # y si el mes ingresado pertenece a los meses válidos de ese año
                    if anio not in anios or mes not in obtener_meses(anio):
                        raise Exception()
                except:
                    print("El año o el mes no es válido")
                    continue # Vuelve a solicitar los datos
                
                # Consulta SQL para obtener datos filtrados por comercio, año y mes
                query = """
                    SELECT * FROM apicall
                    WHERE commerce_id IN ({})
                    AND strftime('%Y', date_api_call) = ?
                    AND strftime('%m', date_api_call) = ?
                """.format(",".join("?" * len(selected_commerce_ids)))

                # Parámetros para la consulta SQL
                params = selected_commerce_ids + [anio, mes]
                break
            break

        elif opcion == "1":
            anios = obtener_anios()
            while True:
                anio = input("Ingrese el anio (YYYY): ").strip()
                try:
                    # Verifica si el año ingresado está en la lista de años disponibles
                    if anio not in anios:
                        raise Exception()
                except:
                    print("El año no es válido")
                    continue # Vuelve a solicitar los datos

                # Consulta SQL para obtener datos filtrados por comercio y año      
                query = """
                    SELECT * FROM apicall
                    WHERE commerce_id IN ({})
                    AND strftime('%Y', date_api_call) = ?
                """.format(",".join("?" * len(selected_commerce_ids)))
                
                # Parámetros para la consulta SQL
                params = selected_commerce_ids + [anio]
                break
            break

        elif opcion == "2":
            # Consulta SQL para obtener todos los datos de los comercios
            # seleccionados sin filtros adicionales
            query = """
                SELECT * FROM apicall
                WHERE commerce_id IN ({})
            """.format(",".join("?" * len(selected_commerce_ids)))

            # Parámetros para la consulta SQL
            params = selected_commerce_ids
            break

        else:
            print("Opción no válida. Intente de nuevo.")
            continue


    conn = conectar_db()

    # Ejecuta la consulta SQL y almacena los resultados en un DataFrame de pandas
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    
    return df