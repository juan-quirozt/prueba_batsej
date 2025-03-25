import pandas as pd
from collections import namedtuple
from etl.extract_1 import obtener_contrato_exitoso, obtener_contrato_no_exitoso

def agrupar_datos(df):
    """
    Agrupa el DataFrame por Año-Mes y Empresa, contando los estados 'Successful' y 'Unsuccessful'.

    Esta función agrega una columna 'year_month' que representa el año y mes de cada registro, 
    luego agrupa los datos por 'year_month' y 'commerce_id', contando la cantidad de veces que 
    aparecen los valores 'Successful' y 'Unsuccessful' en la columna 'ask_status'. Finalmente, 
    ordena los resultados por 'commerce_id' y 'year_month' en orden ascendente.

    Params:
        df (pd.DataFrame): DataFrame con las siguientes columnas necesarias:
            - 'date_api_call' (datetime): Fecha de la llamada API.
            - 'commerce_id' (str): Identificador de la empresa.
            - 'ask_status' (str): Estado de la llamada, puede ser 'Successful' o 'Unsuccessful'.

    Returns:
        pd.DataFrame: DataFrame con las siguientes columnas:
            - 'year_month' (str): Año y mes en formato 'YYYY-MM'.
            - 'commerce_id' (str): Identificador de la empresa.
            - 'Success_Count' (int): Cantidad de llamadas exitosas ('Successful').
            - 'Unsuccess_Count' (int): Cantidad de llamadas fallidas ('Unsuccessful').

    Example:
        >>> import pandas as pd
        >>> data = {
        ...     "date_api_call": ["2024-03-15", "2024-03-20", "2024-04-10", "2024-03-18", "2024-04-15"],
        ...     "commerce_id": ["empresa_A", "empresa_A", "empresa_A", "empresa_B", "empresa_B"],
        ...     "ask_status": ["Successful", "Unsuccessful", "Successful", "Successful", "Unsuccessful"]
        ... }
        >>> df = pd.DataFrame(data)
        >>> df_grouped = agrupar_datos(df)
        >>> print(df_grouped)
           year_month commerce_id  Success_Count  Unsuccess_Count
        0    2024-03  empresa_A              1                1
        1    2024-04  empresa_A              1                0
        2    2024-03  empresa_B              1                0
        3    2024-04  empresa_B              0                1
    """
    
    # Agregar columna de Año-Mes
    df["year_month"] = pd.to_datetime(df["date_api_call"]).dt.strftime("%Y-%m")

    # Agrupar por Año-Mes y Empresa, contando los estados
    df_grouped = df.groupby(["year_month", "commerce_id"])["ask_status"].value_counts().unstack(fill_value=0)

    # Renombrar columnas para mayor claridad
    df_grouped = df_grouped.rename(columns={"Successful": "Success_Count", "Unsuccessful": "Unsuccess_Count"}).reset_index()

    return df_grouped.sort_values(by=['commerce_id', 'year_month'], ascending=[True, True])

def calcular_facturacion(llamados_exitosos, tarifas):
    suma = 0

    for tarifa in tarifas:
        total_llamados_paso = max(llamados_exitosos - tarifa.limite, 0)
        suma += tarifa.valor * total_llamados_paso
        llamados_exitosos -= total_llamados_paso

    return suma

# Estructuras de datos descuentos
Tarifa = namedtuple("Tarifa", ["valor", "limite"])
Descuento = namedtuple("Descuento", ["valor", "limite"])

def obtener_tarifas_por_empresa(df):
    tarifas_por_empresa = {}

    for commerce_id, group in df.groupby("commerce_id"):
        # Ordenar por min_limit_success en orden descendente
        tarifas_ordenadas = sorted(
            group[["price_success", "min_limit_success"]].to_records(index=False),
            key=lambda x: x[1],    # Ordenamos por min_limit_success
            reverse=True
        )

        # Convertimos la lista en una tupla de namedtuples
        tarifas_por_empresa[commerce_id] = [Tarifa(valor=row[0], limite=row[1]) for row in tarifas_ordenadas]

    return tarifas_por_empresa


def obtener_descuentos_por_empresa(df):
    descuentos_por_empresa = {}

    for commerce_id, group in df.groupby("commerce_id"):
        descuentos_ordenados = sorted(
            group[["discount_unsuccess", "min_limit_unsuccess"]].to_records(index=False),
            key=lambda x: x[1],  
            reverse=True
        )
        descuentos_por_empresa[commerce_id] = [Descuento(valor=row[0], limite=row[1]) for row in descuentos_ordenados]

    return descuentos_por_empresa

def calcular_descuento(llamados_no_exitosos, descuentos):
    for descuento in descuentos:
        if llamados_no_exitosos >= descuento.limite:
            return descuento.valor
    return 0  # Si no hay descuento aplicable


## Facturacion
def generar_facturacion(df_agrupado):
    """Genera el DataFrame de facturación basado en las tarifas de cada empresa."""
    
    df_contract_success = obtener_contrato_exitoso()
    df_contract_unsuccess = obtener_contrato_no_exitoso()

    # Obtener tarifas por empresa
    descuentos = obtener_descuentos_por_empresa(df_contract_unsuccess)
    tarifas_por_empresa = obtener_tarifas_por_empresa(df_contract_success)

    # Lista para almacenar los resultados
    facturas = []

    for _, row in df_agrupado.iterrows():
        year_month = row['year_month']
        commerce_id = row["commerce_id"]
        total_exitosos = row["Success_Count"]
        total_no_exitosos = row["Unsuccess_Count"]

        # Obtener tarifas de la empresa (si no existen, usar tarifa 0)
        tarifas = tarifas_por_empresa.get(commerce_id, [Tarifa(0, 0)])
        descuento = descuentos.get(commerce_id, [Descuento(valor=0, limite=0)])  # Si no hay descuento, usar 0

        # Calcular facturación
        total_facturado = calcular_facturacion(total_exitosos, tarifas)
        descuento_aplicado = calcular_descuento(total_no_exitosos, descuento)

        # Agregar datos al resultado
        facturas.append({
            "year_month": year_month,
            "commerce_id": commerce_id,
            "total_llamados_exitosos": total_exitosos,
            "total_llamados_no_exitosos": total_no_exitosos,
            "total_facturado": total_facturado,
            "descuento_aplicado": descuento_aplicado
        })

    # Convertir la lista en DataFrame
    df_factura = pd.DataFrame(facturas)
    
    return df_factura