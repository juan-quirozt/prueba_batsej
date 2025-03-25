import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from etl.user_input_2 import seleccionar_empresas, filtrar_por_fecha

class TestUserInput(unittest.TestCase):
    
    @patch('builtins.input', side_effect=['0'])
    @patch('etl.user_input_2.obtener_comercios_por_estado', return_value=['empresa_1', 'empresa_2'])
    def test_seleccionar_empresas_activas(self, mock_obtener_comercios, mock_input):
        result = seleccionar_empresas()
        self.assertEqual(result, ['empresa_1', 'empresa_2'])
    
    @patch('builtins.input', side_effect=['1'])
    @patch('etl.user_input_2.obtener_comercios_por_estado', return_value=['empresa_3'])
    def test_seleccionar_empresas_inactivas(self, mock_obtener_comercios, mock_input):
        result = seleccionar_empresas()
        self.assertEqual(result, ['empresa_3'])
    
    @patch('builtins.input', side_effect=['2', '0'])
    @patch('etl.user_input_2.obtener_todos_los_comercios', return_value=[('empresa_1', 'Empresa A'), ('empresa_2', 'Empresa B')])
    def test_seleccionar_empresa_individual(self, mock_obtener_comercios, mock_input):
        result = seleccionar_empresas()
        self.assertEqual(result, ['empresa_1'])
    
    @patch('builtins.input', side_effect=['3', '0 1'])
    @patch('etl.user_input_2.obtener_todos_los_comercios', return_value=[('empresa_1', 'Empresa A'), ('empresa_2', 'Empresa B')])
    def test_seleccionar_varias_empresas(self, mock_obtener_comercios, mock_input):
        result = seleccionar_empresas()
        self.assertEqual(result, ['empresa_1', 'empresa_2'])

    @patch('builtins.input', side_effect=['0', '2024', '03'])
    @patch('etl.user_input_2.obtener_anios', return_value=['2023', '2024'])
    @patch('etl.user_input_2.obtener_meses', return_value=['01', '02', '03'])
    @patch('etl.user_input_2.conectar_db')
    def test_filtrar_por_fecha_anio_mes(self, mock_conectar_db, mock_obtener_meses, mock_obtener_anios, mock_input):
        mock_conn = MagicMock()
        mock_conectar_db.return_value = mock_conn
        mock_conn.cursor().execute().fetchall.return_value = [('2024-03-31 14:19:50', 'empresa_B_id', 'Successful', 0.0)]
        df = filtrar_por_fecha(['empresa_B_id'])
        self.assertIsInstance(df, pd.DataFrame)

    @patch('builtins.input', side_effect=['1', '2024'])
    @patch('etl.user_input_2.obtener_anios', return_value=['2023', '2024'])
    @patch('etl.user_input_2.conectar_db')
    def test_filtrar_por_fecha_anio(self, mock_conectar_db, mock_obtener_anios, mock_input):
        mock_conn = MagicMock()
        mock_conectar_db.return_value = mock_conn
        mock_conn.cursor().execute().fetchall.return_value = [('2024-03-29 14:18:35', 'empresa_B_id', 'Successful', 0.0)]
        df = filtrar_por_fecha(['empresa_B_id'])
        self.assertIsInstance(df, pd.DataFrame)

    @patch('builtins.input', side_effect=['2'])
    @patch('etl.user_input_2.conectar_db')
    def test_filtrar_por_fecha_historico(self, mock_conectar_db, mock_input):
        mock_conn = MagicMock()
        mock_conectar_db.return_value = mock_conn
        mock_conn.cursor().execute().fetchall.return_value = [('2023-01-10 10:10:10', 'empresa_A_id', 'Successful', 1.0)]
        df = filtrar_por_fecha(['empresa_A_id'])
        self.assertIsInstance(df, pd.DataFrame)

if __name__ == '__main__':
    unittest.main()