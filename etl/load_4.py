import win32com.client as client
import time

outlook = client.Dispatch('Outlook.Application')
mail = outlook.CreateItem(0)

# mail.display()

mail.To = 'esteban-408@hotmail.com'

mail.Subject = 'Reporte'

mail.Body = 'Saludos, esto es una prueba'

mail._oleobj_.Invoke(*(64209, 0, 8, 0, outlook.Session.Accounts[0]))

#mail.Save()
#time.sleep(3)  # Espera 3 segundos antes de enviar

mail.Attachments.Add(r"D:/batsej_open_company/factura_2.xlsx")

mail.Send()