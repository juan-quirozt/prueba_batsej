import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from etl.extract_1 import (
    obtener_comercios_por_estado,
    obtener_todos_los_comercios,
    obtener_contrato_exitoso,
    obtener_contrato_no_exitoso,
    obtener_info_comercios,
    obtener_anios,
    obtener_meses
)

class TestExtract(unittest.TestCase):
    
    @patch('etl.extract_1.conectar_db')
    def test_obtener_comercios_por_estado(self, mock_conectar_db):
        mock_conn = MagicMock()
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchall.return_value = [(1,), (2,), (3,)]
        mock_conectar_db.return_value = mock_conn
        
        result = obtener_comercios_por_estado("Active")
        self.assertEqual(result, [1, 2, 3])
        
    @patch('etl.extract_1.conectar_db')
    def test_obtener_todos_los_comercios(self, mock_conectar_db):
        mock_conn = MagicMock()
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchall.return_value = [(1, 'Comercio A'), (2, 'Comercio B')]
        mock_conectar_db.return_value = mock_conn
        
        result = obtener_todos_los_comercios()
        self.assertEqual(result, [(1, 'Comercio A'), (2, 'Comercio B')])

    @patch('etl.extract_1.conectar_db')
    def test_obtener_contrato_exitoso(self, mock_conectar_db):
        mock_conn = MagicMock()
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.description = [('id',), ('name',)]
        mock_cursor.fetchall.return_value = [(1, 'Contract A'), (2, 'Contract B')]
        mock_conectar_db.return_value = mock_conn
        
        df = obtener_contrato_exitoso()
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(df.shape, (2, 2))
        self.assertListEqual(df.columns.tolist(), ['id', 'name'])

    @patch('etl.extract_1.conectar_db')
    def test_obtener_contrato_no_exitoso(self, mock_conectar_db):
        mock_conn = MagicMock()
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.description = [('id',), ('status',)]
        mock_cursor.fetchall.return_value = [(1, 'Failed'), (2, 'Failed')]
        mock_conectar_db.return_value = mock_conn
        
        df = obtener_contrato_no_exitoso()
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(df.shape, (2, 2))
        self.assertListEqual(df.columns.tolist(), ['id', 'status'])

    @patch('etl.extract_1.conectar_db')
    def test_obtener_info_comercios(self, mock_conectar_db):
        mock_conn = MagicMock()
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.description = [('id',), ('name',)]
        mock_cursor.fetchall.return_value = [(1, 'Store A'), (2, 'Store B')]
        mock_conectar_db.return_value = mock_conn
        
        df = obtener_info_comercios()
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(df.shape, (2, 2))
        self.assertListEqual(df.columns.tolist(), ['id', 'name'])

    @patch('etl.extract_1.conectar_db')
    def test_obtener_anios(self, mock_conectar_db):
        mock_conn = MagicMock()
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchall.return_value = [('2022',), ('2023',)]
        mock_conectar_db.return_value = mock_conn
        
        result = obtener_anios()
        self.assertEqual(result, ['2022', '2023'])
    
    @patch('etl.extract_1.conectar_db')
    def test_obtener_meses(self, mock_conectar_db):
        mock_conn = MagicMock()
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchall.return_value = [('01',), ('02',)]
        mock_conectar_db.return_value = mock_conn
        
        result = obtener_meses('2023')
        self.assertEqual(result, ['01', '02'])

if __name__ == "__main__":
    unittest.main()
