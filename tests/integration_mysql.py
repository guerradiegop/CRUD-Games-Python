"""Teste opcional em servidor configurado, com limpeza do próprio registro."""
import sys
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import database as db


def main():
    conexao = db.conectar()
    identificador = None
    titulo = 'Teste CRUD ' + uuid4().hex
    try:
        identificador = db.cadastrar(conexao, titulo, 'PC', 'Um dia eu jogo')
        assert db.obter(conexao, identificador)['titulo'] == titulo
        for status in db.STATUS:
            assert db.atualizar(conexao, identificador, titulo, 'PC', status, 'Teste')
            assert any(j['id'] == identificador for j in db.listar(conexao, status))
        # UPDATE com os mesmos valores deve reconhecer que o registro existe.
        assert db.atualizar(conexao, identificador, titulo, 'PC', db.STATUS[-1], 'Teste')
        conexao.close()
        conexao = db.conectar()
        assert db.obter(conexao, identificador)['observacoes'] == 'Teste'
        assert db.excluir(conexao, identificador)
        assert db.obter(conexao, identificador) is None
        assert not db.excluir(conexao, identificador)
        print('CRUD, quatro status e persistência verificados no servidor MySQL.')
    finally:
        try:
            if identificador is not None:
                if not conexao.is_connected():
                    conexao = db.conectar()
                db.excluir(conexao, identificador)
        finally:
            conexao.close()


if __name__ == '__main__':
    main()
