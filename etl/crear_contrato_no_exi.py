import pandas as pd

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
    'min_limit_unsuccess': [6000, 2500, 4500]
}

def crear_no_exitosos():
    df_contract_unsuccess = pd.DataFrame(data_contract_unsuccess)
    return df_contract_unsuccess
