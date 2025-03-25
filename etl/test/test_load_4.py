import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from etl.load_4 import cruzar_facturacion, enviar_correo

class TestLoad(unittest.TestCase):
    
    @patch('etl.load_4.obtener_info_comercios')
    def test_cruzar_facturacion(self, mock_obtener_info):
        # Datos de prueba
        df_factura = pd.DataFrame({
            'commerce_id': [1, 2],
            'year_month': ['2025-03', '2025-03'],
            'total_llamados_exitosos': [10, 20],
            'total_llamados_no_exitosos': [5, 10],
            'total_facturado': [1000, 2000],
            'descuento_aplicado': [0.1, 0.2]
        })
        
        df_comercios = pd.DataFrame({
            'commerce_id': [1, 2],
            'commerce_name': ['Comercio A', 'Comercio B'],
            'commerce_nit': ['123', '456'],
            'commerce_email': ['a@email.com', 'b@email.com']
        })
        
        mock_obtener_info.return_value = df_comercios
        
        df_resultado = cruzar_facturacion(df_factura)
        
        # Verificaciones
        self.assertEqual(len(df_resultado), 2)
        self.assertIn('Fecha-Mes', df_resultado.columns)
        self.assertIn('Valor_a_pagar', df_resultado.columns)
        self.assertAlmostEqual(df_resultado['Valor_a_pagar'].iloc[0], 1000 * 0.9 * 1.19, places=2)
        self.assertAlmostEqual(df_resultado['Valor_a_pagar'].iloc[1], 2000 * 0.8 * 1.19, places=2)
    
    @patch('builtins.input', side_effect=["test@example.com;valid@mail.com"])
    @patch('win32com.client.Dispatch')
    @patch('os.getcwd', return_value="C:\\ruta\\falsa")
    def test_enviar_correo(self, mock_getcwd, mock_dispatch, mock_input):
        mock_outlook = MagicMock()
        mock_mail = MagicMock()
        mock_dispatch.return_value = mock_outlook
        mock_outlook.CreateItem.return_value = mock_mail

        enviar_correo()
        mock_dispatch.assert_called_with('Outlook.Application')
        mock_outlook.CreateItem.assert_called_with(0)
        mock_mail.To = "test@example.com;valid@mail.com"
        mock_mail.Attachments.Add.assert_called_with(r"C:\ruta\falsa\resultados\Factura_ordenada.xlsx")
        mock_mail.Send.assert_called_once()
        
if __name__ == '__main__':
    unittest.main()