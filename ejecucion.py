from etl.extract_1 import obtener_todos_los_comercios, obtener_info_comercios
from etl.user_input_2 import seleccionar_empresas, filtrar_por_fecha
from etl.transform_3 import agrupar_datos, generar_facturacion
from collections import namedtuple
import pandas as pd

Tarifa = namedtuple("Tarifa", ["valor", "limite"])
Descuento = namedtuple("Descuento", ["valor", "limite"])

# EJECUCIÓN PRINCIPAL
def main():
    selected_commerce_ids = seleccionar_empresas()
    print("\n📌 Empresas seleccionadas:", selected_commerce_ids)

    df_filtrado = filtrar_por_fecha(selected_commerce_ids)
    print("\n📌 DataFrame resultante:", df_filtrado)

    df_agrupado = agrupar_datos(df_filtrado)
    print("\n📌 DataFrame Agrupado:")
    print(df_agrupado)

    df_factura = generar_facturacion(df_agrupado)
    print("\n📌 DataFrame de Facturación:", df_factura)

    df_factura.to_excel('factura.xlsx', index=False)

    df_info_comercios = obtener_info_comercios()

    df_factura_final = df_factura.merge(df_info_comercios, how='left', on='commerce_id')
    print(df_factura_final)

    df_factura_final_2 = df_factura_final[['year_month', 'commerce_name', 'commerce_nit', 'commerce_email',
                                           'total_llamados_exitosos', 'total_llamados_no_exitosos',
                                           'total_facturado', 'descuento_aplicado']].copy()
    
    df_factura_final_2['valor_total'] = df_factura_final_2['total_facturado'] * ( 1 - df_factura_final_2['descuento_aplicado'])
    df_factura_final_2['valor_iva'] = 0.19
    df_factura_final_2['valor_a_pagar'] = df_factura_final_2['valor_total'] * (1 + df_factura_final_2['valor_iva'])
    
    df_factura_final_2.to_excel('factura_2.xlsx', index=False)
    print(df_factura_final_2)

if __name__ == "__main__":
    main()