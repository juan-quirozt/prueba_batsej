from etl.extract_1 import obtener_todos_los_comercios
from etl.user_input_2 import seleccionar_empresas, filtrar_por_fecha
from etl.transform_3 import agrupar_datos, generar_facturacion
from collections import namedtuple
import pandas as pd

from etl.crear_contrato_exi import crear_exitosos
from etl.crear_contrato_no_exi import crear_no_exitosos

df_contract_success = crear_exitosos()
df_contract_unsuccess = crear_no_exitosos()

Tarifa = namedtuple("Tarifa", ["valor", "limite"])
Descuento = namedtuple("Descuento", ["valor", "limite"])

# EJECUCIÓN PRINCIPAL
selected_commerce_ids = seleccionar_empresas()
print("\n📌 Empresas seleccionadas:", selected_commerce_ids)

df_filtrado = filtrar_por_fecha(selected_commerce_ids)
print("\n📌 DataFrame resultante:", df_filtrado)

df_agrupado = agrupar_datos(df_filtrado)
print("\n📌 DataFrame Agrupado:")
print(df_agrupado.sort_values(by=['commerce_id', 'year_month'], ascending=[True, False]))

df_factura = generar_facturacion(df_agrupado, df_contract_success, df_contract_unsuccess)
print("\n📌 DataFrame de Facturación:", df_factura)

df_factura.to_excel('factura.xlsx', index=False)

comercios = obtener_todos_los_comercios()
print(comercios)
df_commerce = pd.DataFrame(comercios, columns=['commerce_id', 'commerce_name'])
print(df_commerce)


df_factura_final = df_factura.merge(df_commerce, how='left', on='commerce_id')
print(df_factura_final)