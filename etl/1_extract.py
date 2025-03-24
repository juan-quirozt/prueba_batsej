import pandas as pd
import sqlite3

# Abrimos la conexion con la DB
connection = sqlite3.connect(r'D:/batsej_open_company/data/database.sqlite')

def leer_db(connection):
    # Leer la tabla que contiene los llamados a la API
    table_name_apicall = 'apicall'
    query_apicall = f'SELECT * FROM {table_name_apicall}'
    df_apicall =  pd.read_sql(query_apicall, connection)

    # Leer la tabla que contiene los comercios
    table_name_commerce = 'commerce'
    query_commerce = f'SELECT * FROM {table_name_commerce}'
    df_commerce = pd.read_sql(query_commerce, connection)

    # Eliminar esta parte cuando se cree la DB
    # ----------------------------------------
    # ----------------------------------------
    # Agregar columnas que me permiten saber si debo o no aplicar descuento
    df_commerce['contract_type_code'] = [0, 1, 0, 1, 0]
    df_commerce['contract_type'] = ['fijo', 'variable', 'fijo', 'variable', 'fijo']
    df_commerce['has_discount_success'] = [0, 1, 0, 1, 0]
    df_commerce['has_discount_unsuccess'] = [0, 0, 0, 1, 1]

    return df_apicall, df_commerce




# Crear tablas temporales para calcular los descuentos

# Tabla contract_success
# Crear un DataFrame con las condiciones de los contratos de las empresas
def crear_contrato_success():
    """
    Esta tabla contiene la información de los contratos con precios
    variables cuando se realizan llamados EXITOSOS a la API para cada
    una de las empresas. Esto se debe crear en la BD más adelante.

    Contiene
    commerce_id [VARCHAR19]: Hace referencia al indicador único de una empresa
    commerce_name [VARCHAR]: Hace referencia al nombre de la empresa

    price_success [INTEGER]: Hace referencia al valor que se debe cobrar cuando la cantidad de llamados exitosos a la API se encuentra en este rango. (NULL es no tiene descuento)
    min_limit_success [INTEGER]: Hace referencia al límite inferior del intervalo para el cual se aplica el descuento (NULL es no tiene descuento)
    max_limit_success [INTEGER]: Hace referencia al límite superior del intervalo para el cual se aplica el descuento (NULL es no tiene descuento) (-1 es inf)
    """

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

    return pd.DataFrame(data_contract_success)




# Tabla para los descuentos por llamados no exitosos

def crear_contrato_unsuccess():
    """
    Esta tabla que contiene la información de los descuentos que se deben hacer
    cuando se realizan llamados NO EXITOSOS a la API para cada
    una de las empresas. Esto se debe crear en la BD más adelante.

    Contiene
    commerce_id [VARCHAR19]: Hace referencia al indicador único de una empresa
    commerce_name [VARCHAR]: Hace referencia al nombre de la empresa

    discount_unsuccess [INTEGER]: Hace referencia al valor que se debe cobrar cuando la cantidad de llamados exitosos a la API se encuentra en este rango. (NULL es no tiene descuento)
    min_limit_success [INTEGER]: Hace referencia al límite inferior del intervalo para el cual se aplica el descuento (NULL es no tiene descuento)
    max_limit_unsuccess [INTEGER]: Hace referencia al límite superior del intervalo para el cual se aplica el descuento (NULL es no tiene descuento) (-1 es inf)
    """

    data_contract_unsuccess = {
        'commerce_id': ['3VYd-4lzT-mTC3-DQN5',
                        'GdEQ-MGb7-LXHa-y6cd',
                        'GdEQ-MGb7-LXHa-y6cd'],

        'commerce_name': ['Zenith Corp',
                        'FusionWave Enterprises',
                        'FusionWave Enterprises'],

        'discount_unsuccess': [0.05, 0.05, 0.08],
        'min_limit_unsuccess': [6000, 2500, 4500],
    }

    return pd.DataFrame(data_contract_unsuccess)

# ----------------------------------------
# ----------------------------------------

def convertir_fechas(df):
    # Cerramos la conexion con la DB
    print('Antes de convertir:', df.dtypes)

    # Convertir las fechas
    df['date_api_call'] = pd.to_datetime(df['date_api_call'])
    print('Despues de convertir:', df.dtypes)

    # Generar nueva columna con el mes/año
    df["year_month"] = df["date_api_call"].dt.to_period("M")
    
    return df


print('\nInicializando...\n')
df_apicall, df_commerce = leer_db(connection)
print('-'*50)
print('-'*50)
print('Bienvenido, te invito a generar tu factura!')
print('-'*50)
print('-'*50)

print('\nPor favor seleccione el periodo que desea facturar\n')
print('-'*50)

month_interes = int(input('Por favor ingrese el mes que desea facturar: '))
year_interes = int(input('Por favor ingrese el año que desea facturar: '))


print('\nSeleccione la empresa para la cual desea facturar\n')
print(df_commerce['commerce_name'].to_string(), '\n')

indice_empresa = int(input('Escriba el número de índice de la empresa de interés: '))
empresa = df_commerce.iloc[indice_empresa]['commerce_id']
print('La empresa seleccionada fue: ', indice_empresa, empresa)
connection.close()

def filtrar_apicalls_por_fecha(df):
    # Agrupar para saber cuantos tiene cada categoria Success o Unsuccess
    # Filtrar para obtener únicamente el mes que me interesa
    df_filtrado = df[ (df["date_api_call"].dt.year == year_interes) &
                        (df["date_api_call"].dt.month == month_interes) &
                        (df["commerce_id"] == empresa) ]
    
    return df_filtrado

# Leer array con las condiciones de los contratos
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


df_contract_success = crear_contrato_success()
df_contract_unsuccess = crear_contrato_unsuccess()

# Obtener la estructura de tarifas por empresa
tarifas_por_empresa = obtener_tarifas_por_empresa(df_contract_success)

# Seleccionar una empresa específica (ejemplo: "Vj9W-c4Pm-ja0X-fC1C")
commerce_id = "Vj9W-c4Pm-ja0X-fC1C"


# Por esto da lo mismoooooooooo
llamados_exitosos = 20440

# Calcular la facturación
if commerce_id in tarifas_por_empresa:
    monto_facturado = calcular_facturacion(llamados_exitosos, tarifas_por_empresa[commerce_id])
    print(f"Facturación para {commerce_id}: {monto_facturado}")
else:
    print("Empresa no encontrada")



# Calcular con tarifa base

# Generar descuentos si es que aplica

# Generar factura


"""
df_commerce.to_csv("commerce.csv", index=False)

print("df_commerce:\n", df_commerce.head(), '\n')
print("df_apicall:\n",df_apicall.head(), '\n')
print("df_contract_success:\n", df_contract_success, '\n')
print("df_contract_unsuccess:\n", df_contract_unsuccess, '\n')
print("df_apicall_filtrado:\n", df_apicall_filtrado.head())
"""