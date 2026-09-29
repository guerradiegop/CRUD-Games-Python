import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import database as db
from mysql.connector import Error


class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.connection = MagicMock()
        self.cursor = self.connection.cursor.return_value

    def test_config_environment_and_percent_password(self):
        with tempfile.TemporaryDirectory() as pasta:
            arquivo = Path(pasta) / 'config.ini'
            arquivo.write_text('[mysql]\npassword = abc%123\nport = 3307\n', encoding='utf-8')
            with patch.dict(os.environ, {}, clear=True):
                config = db.carregar_config(arquivo)
                self.assertEqual(config['password'], 'abc%123')
                self.assertEqual(config['port'], 3307)
            with patch.dict(os.environ, {'DB_HOST': 'servidor', 'DB_PORT': '3308'}, clear=True):
                config = db.carregar_config(arquivo)
                self.assertEqual(config['host'], 'servidor')
                self.assertEqual(config['port'], 3308)
            with patch.dict(os.environ, {'DB_PORT': 'abc'}, clear=True):
                with self.assertRaises(ValueError):
                    db.carregar_config(arquivo)

    def test_insert_parameterizes_user_input_and_commits(self):
        self.cursor.lastrowid = 42
        titulo = "Jogo'); DROP TABLE jogos; --"
        self.assertEqual(db.cadastrar(self.connection, titulo, ' PC ', 'Jogando'), 42)
        sql, params = self.cursor.execute.call_args.args
        self.assertNotIn(titulo, sql)
        self.assertEqual(params, (titulo, 'PC', 'Jogando', ''))
        self.connection.start_transaction.assert_called_once()
        self.connection.commit.assert_called_once()
        self.cursor.close.assert_called_once()

    def test_failed_write_rolls_back_and_closes_cursor(self):
        self.cursor.execute.side_effect = Error('Falha simulada')
        with self.assertRaises(Error):
            db.excluir(self.connection, 1)
        self.connection.rollback.assert_called_once()
        self.connection.commit.assert_not_called()
        self.cursor.close.assert_called_once()

    def test_filter_and_get_use_parameters(self):
        self.cursor.fetchall.return_value = [{'id': 1}]
        self.assertEqual(db.listar(self.connection, 'Platinados'), [{'id': 1}])
        self.assertEqual(self.cursor.execute.call_args.args[1], ('Platinados',))
        self.cursor.fetchone.return_value = None
        self.assertIsNone(db.obter(self.connection, 999))
        self.assertEqual(self.cursor.execute.call_args.args[1], (999,))

    def test_update_and_delete_report_missing_rows(self):
        self.cursor.rowcount = 0
        self.assertFalse(db.atualizar(self.connection, 99, 'A', 'PC', 'Jogando', ''))
        self.assertFalse(db.excluir(self.connection, 99))
        self.cursor.rowcount = 1
        self.assertTrue(db.atualizar(self.connection, 1, 'A', 'PC', 'Jogando', ''))

    def test_validation_prevents_database_write(self):
        for titulo, plataforma, status, obs in [
            (' ', 'PC', 'Jogando', ''), ('A', '', 'Jogando', ''),
            ('A', 'PC', 'Inválido', ''), ('A' * 151, 'PC', 'Jogando', ''),
            ('A', 'P' * 81, 'Jogando', ''), ('A', 'PC', 'Jogando', 'x' * 5001),
        ]:
            with self.assertRaises(ValueError):
                db.cadastrar(self.connection, titulo, plataforma, status, obs)
        self.connection.cursor.assert_not_called()


if __name__ == '__main__':
    unittest.main()
