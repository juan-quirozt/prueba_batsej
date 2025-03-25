import win32com.client as client
from etl.extract_1 import obtener_info_comercios
from datetime import datetime
import os
import re

## Merge para facturacion

def cruzar_facturacion(df_factura):
    """Cruza los datos de facturación con la información de los comercios para generar el reporte final.
 
    Combina los datos de facturación con la información de los comercios mediante el 'commerce_id',
    calcula valores como total con descuento, IVA y valor a pagar, y renombra las columnas para el reporte final.
 
    Args:
        df_factura (pd.DataFrame): DataFrame con los datos de facturación inicial. Debe contener las columnas:
            - 'commerce_id' (int): Identificador único del comercio
            - 'year_month' (str): Periodo en formato AAAA-MM
            - 'total_llamados_exitosos' (int): Cantidad de llamados exitosos
            - 'total_llamados_no_exitosos' (int): Cantidad de llamados no exitosos
            - 'total_facturado' (float): Valor bruto a facturar
            - 'descuento_aplicado' (float): Descuento aplicado (entre 0 y 1)
 
    Returns:
        pd.DataFrame: DataFrame procesado con las siguientes columnas renombradas:
            - Fecha-Mes: Periodo de facturación (AAAA-MM)
            - Nombre: Nombre del comercio
            - Nit: NIT del comercio
            - Correo: Email del comercio
            - Llamados_exitosos: Llamados exitosos
            - Llamados_no_exitosos: Llamados no exitosos
            - Valor_comision: Valor bruto de comisión
            - Descuento_aplicado_porc: Porcentaje de descuento aplicado
            - Valor_comision_con_descuentos: Valor neto después de descuentos
            - Valor_iva: IVA aplicado (19%)
            - Valor_a_pagar: Valor total a pagar
    """
    df_info_comercios = obtener_info_comercios()

    df_merged = df_factura.merge(df_info_comercios, how='left', on='commerce_id')

    df_factura_final = df_merged[['year_month', 'commerce_name', 'commerce_nit',
                                    'commerce_email', 'total_llamados_exitosos',
                                    'total_llamados_no_exitosos', 'total_facturado',
                                    'descuento_aplicado']].copy()
        
    df_factura_final['valor_total'] = df_factura_final['total_facturado'] * ( 1 - df_factura_final['descuento_aplicado'])
    df_factura_final['valor_iva'] = 0.19
    df_factura_final['valor_a_pagar'] = df_factura_final['valor_total'] * (1 + df_factura_final['valor_iva'])
    
    df_factura_final = df_factura_final.rename(columns={"year_month": "Fecha-Mes",
                                                        "commerce_name": "Nombre",
                                                        "commerce_nit": "Nit",
                                                        "commerce_email": "Correo",
                                                        "total_llamados_exitosos": "Llamados_exitosos",
                                                        "total_llamados_no_exitosos": "Llamados_no_exitosos",
                                                        "total_facturado": "Valor_comision",
                                                        "descuento_aplicado": "Descuento_aplicado_porc",
                                                        "valor_total": "Valor_comision_con_descuentos",
                                                        "valor_iva": "Valor_iva",
                                                        "valor_a_pagar": "Valor_a_pagar",
                                                        })
    return df_factura_final


## Correo
def enviar_correo():

    while True:
        correos = input('Ingrese los correos electronicos separados por punto y coma: ')
        correos_2 = correos.split(';')

        email_flag = None
        for correo in correos_2:
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', correo):
                email_flag = correo
                break

        if email_flag:
            print(f'El correo {email_flag} no es válido')
            continue
        break
    
    fecha = datetime.now()
    outlook = client.Dispatch('Outlook.Application')
    mail = outlook.CreateItem(0)

    mail.To = correos
    mail.Subject = f'Reporte de Ejecución Rutina de Facturación {fecha.date()}'
    mail.Body = 'Saludos, este es el resultado de la ejecución según tu preferencias.'
    mail._oleobj_.Invoke(*(64209, 0, 8, 0, outlook.Session.Accounts[0]))

    #mail.Save()
    #time.sleep(3)  # Espera 3 segundos antes de enviar

    mail.Attachments.Add(rf"{os.getcwd()}\resultados\Factura_ordenada.xlsx")
    mail.Send()