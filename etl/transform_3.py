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
    """
    Calcula el costo total de facturación basado en la cantidad de llamados exitosos y una lista de tarifas escalonadas.

    La función evalúa cuántos llamados exitosos superan cada límite definido en las tarifas y aplica el costo correspondiente.
    Se utiliza un esquema de tarifas escalonadas donde cada nivel tiene un límite máximo y un valor asociado por llamado.

    Params:
        llamados_exitosos (int): Número total de llamados exitosos a facturar.
        tarifas (list): Lista de objetos de tarifas, cada uno con:
            - limite (int): Límite de llamados para aplicar la tarifa.
            - valor (float): Costo por cada llamado adicional que supere el límite.

    Returns:
        float: Costo total calculado en base a los llamados exitosos y las tarifas aplicadas.

    Example:
        >>> class Tarifa:
        ...     def __init__(self, limite, valor):
        ...         self.limite = limite
        ...         self.valor = valor
        ...
        >>> tarifas = [Tarifa(100, 0.5), Tarifa(200, 0.3), Tarifa(500, 0.2)]
        >>> calcular_facturacion(250, tarifas)
        40.0
    """
    # Variable de control para almacenar el total de la facturación
    suma = 0

    for tarifa in tarifas:
        # Calcular cuántos llamados superan el límite actual de la tarifa
        total_llamados_paso = max(llamados_exitosos - tarifa.limite, 0)

        # Sumar al total el costo de los llamados que superan el límite
        suma += tarifa.valor * total_llamados_paso

        # Reducir los llamados exitosos para la siguiente iteración
        llamados_exitosos -= total_llamados_paso

    return suma

# Estructuras de datos descuentos
Tarifa = namedtuple("Tarifa", ["valor", "limite"])
Descuento = namedtuple("Descuento", ["valor", "limite"])

def obtener_tarifas_por_empresa(df):
    """
    Genera un diccionario con las tarifas organizadas por empresa, ordenadas en orden descendente
    según el límite mínimo de éxito (`min_limit_success`).

    La función agrupa los datos por `commerce_id` y extrae las tarifas (`price_success`) junto con
    su respectivo límite mínimo de éxito. Luego, ordena estos valores de mayor a menor y los almacena
    en una lista de namedtuples `Tarifa` dentro del diccionario resultante.

    Params:
        df (pd.DataFrame): DataFrame con las columnas:
            - commerce_id (str): Identificador de la empresa.
            - price_success (float): Precio de cada éxito en la tarifa.
            - min_limit_success (int): Límite mínimo de éxitos para aplicar la tarifa.

    Returns:
        dict: Un diccionario donde:
            - Claves: `commerce_id` (str), identificador de la empresa.
            - Valores: Lista de objetos `Tarifa`, cada uno con:
                - `valor` (float): Precio de éxito.
                - `limite` (int): Límite mínimo para aplicar la tarifa.

    Example:
        >>> import pandas as pd
        >>> from collections import namedtuple
        >>> Tarifa = namedtuple("Tarifa", ["valor", "limite"])
        >>> data = {
        ...     "commerce_id": ['Empresa-A', 'Empresa-A', 'Empresa-B', 'Empresa-B', 'Empresa-B'],
        ...     "price_success": [50, 30, 40, 20, 10],
        ...     "min_limit_success": [100, 200, 50, 150, 300]
        ... }
        >>> df = pd.DataFrame(data)
        >>> obtener_tarifas_por_empresa(df)
        {'Empresa-A': [Tarifa(valor=30, limite=200), Tarifa(valor=50, limite=100)],
         'Empresa-B': [Tarifa(valor=10, limite=300), Tarifa(valor=20, limite=150), Tarifa(valor=40, limite=50)]}
    """
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
    """
    Agrupa y organiza los descuentos por empresa según el límite mínimo de llamadas no exitosas.

    Parameters:
        df (pd.DataFrame): DataFrame con las columnas:
            - "commerce_id" (str): Identificador de la empresa.
            - "discount_unsuccess" (float): Porcentaje de eescuento aplicable a llamadas no exitosas.
            - "min_limit_unsuccess" (int): Límite mínimo de llamadas no exitosas para aplicar el descuento.

    Returns:
        dict: Un diccionario donde las claves son los `commerce_id` y los valores son listas de namedtuples `Descuento`
              ordenadas en orden descendente por `min_limit_unsuccess`.

    Example:
        >>> import pandas as pd
        >>> from collections import namedtuple
        >>> Descuento = namedtuple("Descuento", ["valor", "limite"])
        >>> data = {
        ...     "commerce_id": ["Empresa-A", "Empresa-A", "Empresa-B", "Empresa-B"],
        ...     "discount_unsuccess": [0.1, 0.2, 0.15, 0.05],
        ...     "min_limit_unsuccess": [50, 100, 30, 80]
        ... }
        >>> df = pd.DataFrame(data)
        >>> obtener_descuentos_por_empresa(df)
        {'Empresa-A': [Descuento(valor=0.2, limite=100), Descuento(valor=0.1, limite=50)],
         'Empresa-B': [Descuento(valor=0.05, limite=80), Descuento(valor=0.15, limite=30)]}
    """
    descuentos_por_empresa = {}

    for commerce_id, group in df.groupby("commerce_id"):
        # Ordenar descuentos en orden descendente según min_limit_unsuccess
        descuentos_ordenados = sorted(
            group[["discount_unsuccess", "min_limit_unsuccess"]].to_records(index=False),
            key=lambda x: x[1],  
            reverse=True
        )

        # Convertir la lista en una lista de namedtuples Descuento
        descuentos_por_empresa[commerce_id] = [Descuento(valor=row[0], limite=row[1]) for row in descuentos_ordenados]

    return descuentos_por_empresa

def calcular_descuento(llamados_no_exitosos, descuentos):
    """
    Calcula el descuento aplicable basado en la cantidad de llamadas no exitosas.

    Parameters:
        llamados_no_exitosos (int): Número de llamadas no exitosas realizadas.
        descuentos (list of Descuento): Lista de namedtuples `Descuento`, ordenados de mayor a menor por `limite`.

    Returns:
        float: El valor del descuento aplicable o 0 si no hay descuento disponible.

    Example:
        >>> from collections import namedtuple
        >>> Descuento = namedtuple("Descuento", ["valor", "limite"])
        >>> descuentos = [Descuento(valor=0.2, limite=100), Descuento(valor=0.1, limite=50)]
        >>> calcular_descuento(120, descuentos)
        0.2
        >>> calcular_descuento(70, descuentos)
        0.1
        >>> calcular_descuento(30, descuentos)
        0
    """
    for descuento in descuentos:
        if llamados_no_exitosos >= descuento.limite:
            return descuento.valor
    return 0  # Si no hay descuento aplicable


## Facturacion
def generar_facturacion(df_agrupado):
    """
    Genera un DataFrame de facturación basado en las tarifas y descuentos aplicables a cada empresa.

    Esta función toma un DataFrame agrupado con el número de llamadas exitosas y no exitosas por empresa 
    y mes, y calcula el total facturado y el descuento aplicado según los contratos vigentes.

    Parameters:
        df_agrupado (pd.DataFrame): DataFrame con las siguientes columnas:
            - "year_month" (str): Año y mes en formato 'YYYY-MM'.
            - "commerce_id" (str): Identificador de la empresa.
            - "Success_Count" (int): Número de llamadas exitosas realizadas en el mes.
            - "Unsuccess_Count" (int): Número de llamadas no exitosas en el mes.

    Returns:
        pd.DataFrame: DataFrame con la facturación calculada, que contiene las siguientes columnas:
            - "year_month" (str): Año y mes del registro.
            - "commerce_id" (str): Identificador de la empresa.
            - "total_llamados_exitosos" (int): Total de llamadas exitosas en el mes.
            - "total_llamados_no_exitosos" (int): Total de llamadas no exitosas en el mes.
            - "total_facturado" (float): Monto total facturado a la empresa por llamadas exitosas.
            - "descuento_aplicado" (float): Monto del descuento aplicado por llamadas no exitosas.

    Example:
        >>> import pandas as pd
        >>> df_agrupado = pd.DataFrame([
        ...     {"year_month": "2024-02", "commerce_id": "Empresa-A", "Success_Count": 150, "Unsuccess_Count": 50},
        ...     {"year_month": "2024-02", "commerce_id": "Empresa-B", "Success_Count": 80, "Unsuccess_Count": 30}
        ... ])
        >>> generar_facturacion(df_agrupado)
           year_month commerce_id  total_llamados_exitosos  total_llamados_no_exitosos  total_facturado  descuento_aplicado
        0   2024-02   Empresa-A                       150                           50              X.X                  Y.Y
        1   2024-02   Empresa-B                        80                           30              X.X                  Y.Y
    """
    
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