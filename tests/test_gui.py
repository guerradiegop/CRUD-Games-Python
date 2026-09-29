"""Testes dos callbacks, sem criar janela ou conectar a servidor."""
import importlib
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
# Isola widgets para testar callbacks mesmo em ambientes sem Tcl/Tk.
with patch.dict(sys.modules, {'tkinter': MagicMock()}):
    gui = importlib.import_module('gui')


class GuiTests(unittest.TestCase):
    def setUp(self):
        self.app = gui.CadastroJogos.__new__(gui.CadastroJogos)
        self.app.janela = MagicMock()
        self.app.conexao = MagicMock()
        self.app.identificador = None
        for nome in ('titulo', 'plataforma', 'status', 'observacoes', 'mensagem', 'tabela', 'filtro'):
            setattr(self.app, nome, MagicMock())
        self.app.titulo.get.return_value = 'Hollow Knight'
        self.app.plataforma.get.return_value = 'PC'
        self.app.status.get.return_value = 'Jogando'
        self.app.observacoes.get.return_value = ''
        self.app.recarregar = MagicMock()

    @patch.object(gui.db, 'cadastrar', return_value=12)
    def test_new_game_calls_insert(self, cadastrar):
        self.app.salvar()
        cadastrar.assert_called_once_with(self.app.conexao, 'Hollow Knight', 'PC', 'Jogando', '')
        self.app.recarregar.assert_called_once()

    @patch.object(gui.db, 'atualizar', return_value=True)
    @patch.object(gui.db, 'cadastrar')
    def test_selected_game_calls_update(self, cadastrar, atualizar):
        self.app.identificador = 3
        self.app.salvar()
        atualizar.assert_called_once_with(self.app.conexao, 3, 'Hollow Knight', 'PC', 'Jogando', '')
        cadastrar.assert_not_called()

    @patch.object(gui.messagebox, 'showerror')
    @patch.object(gui.db, 'cadastrar', side_effect=ValueError('Título obrigatório'))
    def test_invalid_form_is_preserved(self, cadastrar, mostrar):
        self.app.salvar()
        mostrar.assert_called_once()
        self.app.recarregar.assert_not_called()

    @patch.object(gui.messagebox, 'askyesno', return_value=False)
    @patch.object(gui.db, 'excluir')
    def test_cancel_delete_never_writes(self, excluir, confirmar):
        self.app.identificador = 3
        self.app.excluir()
        confirmar.assert_called_once()
        excluir.assert_not_called()

    @patch.object(gui.messagebox, 'askyesno', return_value=True)
    @patch.object(gui.db, 'excluir', return_value=True)
    def test_confirm_delete_uses_selected_id(self, excluir, confirmar):
        self.app.identificador = 3
        self.app.excluir()
        excluir.assert_called_once_with(self.app.conexao, 3)
        self.app.recarregar.assert_called_once()


if __name__ == '__main__':
    unittest.main()
