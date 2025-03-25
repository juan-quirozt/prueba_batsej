import win32com.client as client
from etl.extract_1 import obtener_info_comercios
from datetime import datetime

## Merge para facturacion

def cruzar_facturacion(df_factura):
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
    fecha = datetime.now()
    outlook = client.Dispatch('Outlook.Application')
    mail = outlook.CreateItem(0)

    # mail.display()

    mail.To = 'esteban-408@hotmail.com'
    mail.Subject = f'Reporte de Ejecución Rutina de Facturación {fecha.date()}'
    mail.Body = 'Saludos, este es el resultado de la ejecución según tu preferencias.'
    mail._oleobj_.Invoke(*(64209, 0, 8, 0, outlook.Session.Accounts[0]))

    #mail.Save()
    #time.sleep(3)  # Espera 3 segundos antes de enviar

    mail.Attachments.Add(r"D:/batsej_open_company/Factura_ordenada.xlsx")
    mail.Send()