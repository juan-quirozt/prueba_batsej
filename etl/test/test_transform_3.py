import unittest
from unittest.mock import patch
import pandas as pd
from collections import namedtuple
from etl.transform_3 import agrupar_datos, calcular_facturacion, calcular_descuento, generar_facturacion

class TestTransform(unittest.TestCase):

    def setUp(self):
        self.data = {
            "date_api_call": ["2024-03-15", "2024-03-20", "2024-04-10", "2024-03-18", "2024-04-15"],
            "commerce_id": ["empresa_A", "empresa_A", "empresa_A", "empresa_B", "empresa_B"],
            "ask_status": ["Successful", "Unsuccessful", "Successful", "Successful", "Unsuccessful"]
        }
        self.df = pd.DataFrame(self.data)

    def test_agrupar_datos(self):
        df_grouped = agrupar_datos(self.df)
        expected_columns = ["year_month", "commerce_id", "Success_Count", "Unsuccess_Count"]
        self.assertListEqual(list(df_grouped.columns), expected_columns)
        self.assertEqual(df_grouped.loc[df_grouped["commerce_id"] == "empresa_A", "Success_Count"].sum(), 2)
        self.assertEqual(df_grouped.loc[df_grouped["commerce_id"] == "empresa_B", "Unsuccess_Count"].sum(), 1)

    def test_calcular_facturacion(self):
        Tarifa = namedtuple("Tarifa", ["valor", "limite"])
        tarifas = [Tarifa(valor=100, limite=10), Tarifa(valor=50, limite=5)]
        
        total = calcular_facturacion(15, tarifas)  # 5 llamadas a 100 + 5 llamadas a 50 = 750
        self.assertEqual(total, 750)

    def test_calcular_descuento(self):
        Descuento = namedtuple("Descuento", ["valor", "limite"])
        descuentos = [Descuento(valor=20, limite=5), Descuento(valor=10, limite=3)]
        
        descuento = calcular_descuento(6, descuentos)  # Debe aplicar el de 20
        self.assertEqual(descuento, 20)
        
        descuento = calcular_descuento(4, descuentos)  # Debe aplicar el de 10
        self.assertEqual(descuento, 10)
        
        descuento = calcular_descuento(2, descuentos)  # No aplica ninguno
        self.assertEqual(descuento, 0)

    @patch("etl.transform_3.obtener_contrato_exitoso")
    @patch("etl.transform_3.obtener_contrato_no_exitoso")
    def test_generar_facturacion(self, mock_obtener_contrato_no_exitoso, mock_obtener_contrato_exitoso):
        df_agrupado = agrupar_datos(self.df)

        # Configurar mocks
        mock_obtener_contrato_exitoso.return_value = pd.DataFrame({
            "commerce_id": ["empresa_A", "empresa_B"],
            "price_success": [100, 50],
            "min_limit_success": [10, 5]
        })
        
        mock_obtener_contrato_no_exitoso.return_value = pd.DataFrame({
            "commerce_id": ["empresa_A", "empresa_B"],
            "discount_unsuccess": [20, 10],
            "min_limit_unsuccess": [5, 3]
        })
        
        df_factura = generar_facturacion(df_agrupado)
        expected_columns = ["year_month", "commerce_id", "total_llamados_exitosos", "total_llamados_no_exitosos", "total_facturado", "descuento_aplicado"]
        self.assertListEqual(list(df_factura.columns), expected_columns)
        
        empresa_A_facturacion = df_factura[df_factura["commerce_id"] == "empresa_A"]["total_facturado"].sum()
        empresa_B_descuento = df_factura[df_factura["commerce_id"] == "empresa_B"]["descuento_aplicado"].sum()
        
        self.assertGreaterEqual(empresa_A_facturacion, 0)
        self.assertGreaterEqual(empresa_B_descuento, 0)

if __name__ == "__main__":
    unittest.main()
