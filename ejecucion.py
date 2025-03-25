from etl.extract_1 import obtener_todos_los_comercios, obtener_info_comercios
from etl.user_input_2 import seleccionar_empresas, filtrar_por_fecha
from etl.transform_3 import agrupar_datos, generar_facturacion
from etl.load_4 import cruzar_facturacion, enviar_correo
from collections import namedtuple
import pandas as pd
import os

Tarifa = namedtuple("Tarifa", ["valor", "limite"])
Descuento = namedtuple("Descuento", ["valor", "limite"])

# EJECUCIÓN PRINCIPAL
def main():
    selected_commerce_ids = seleccionar_empresas()

    df_filtrado = filtrar_por_fecha(selected_commerce_ids)

    df_agrupado = agrupar_datos(df_filtrado)

    df_factura = generar_facturacion(df_agrupado)

    df_factura.to_excel('factura.xlsx', index=False)

    df_factura_ordenada = cruzar_facturacion(df_factura)

    # Exportar la factura a xlsx
    df_factura_ordenada.to_excel(rf'{os.getcwd()}\resultados\Factura_ordenada.xlsx', index=False)

    # Enviar correo
    enviar_correo()

if __name__ == "__main__":
    main()