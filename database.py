"""Conexão e CRUD compartilhados pelas interfaces do projeto."""

import configparser
import os
from pathlib import Path

import mysql.connector
from mysql.connector.constants import ClientFlag

STATUS = ('Zerados', 'Platinados', 'Jogando', 'Um dia eu jogo')
PASTA = Path(__file__).resolve().parent


def carregar_config(caminho=None):
    config = configparser.ConfigParser(interpolation=None)
    config.read(caminho or PASTA / 'config.ini', encoding='utf-8')
    secao = config['mysql'] if config.has_section('mysql') else {}
    valores = {}
    for chave, padrao in [('host', 'localhost'), ('port', '3306'),
                          ('user', 'crud_games'), ('password', ''),
                          ('database', 'crud_games')]:
        valores[chave] = os.environ.get('DB_' + chave.upper(), secao.get(chave, padrao))
    try:
        valores['port'] = int(valores['port'])
        if not 1 <= valores['port'] <= 65535:
            raise ValueError
    except ValueError as erro:
        raise ValueError('A porta do MySQL deve ser um número entre 1 e 65535.') from erro
    return valores


def conectar():
    # FOUND_ROWS faz UPDATE retornar linhas encontradas mesmo sem alterar valores.
    return mysql.connector.connect(
        **carregar_config(), charset='utf8mb4', autocommit=True,
        connection_timeout=5, client_flags=[ClientFlag.FOUND_ROWS],
    )


def validar(titulo, plataforma, status, observacoes):
    titulo, plataforma, observacoes = titulo.strip(), plataforma.strip(), observacoes.strip()
    if not titulo or not plataforma:
        raise ValueError('Título e plataforma são obrigatórios.')
    if len(titulo) > 150 or len(plataforma) > 80:
        raise ValueError('Limites: 150 caracteres no título e 80 na plataforma.')
    if len(observacoes) > 5000:
        raise ValueError('As observações podem ter até 5000 caracteres.')
    if status not in STATUS:
        raise ValueError('Status inválido.')
    return titulo, plataforma, status, observacoes


def consultar(conexao, sql, parametros=(), unico=False):
    cursor = conexao.cursor(dictionary=True)
    try:
        cursor.execute(sql, parametros)
        return cursor.fetchone() if unico else cursor.fetchall()
    finally:
        cursor.close()


def gravar(conexao, sql, parametros, retornar_id=False):
    conexao.start_transaction()
    cursor = None
    try:
        cursor = conexao.cursor()
        cursor.execute(sql, parametros)
        resultado = cursor.lastrowid if retornar_id else cursor.rowcount > 0
        conexao.commit()
        return resultado
    except mysql.connector.Error:
        conexao.rollback()
        raise
    finally:
        if cursor is not None:
            cursor.close()


def cadastrar(conexao, titulo, plataforma, status, observacoes=''):
    valores = validar(titulo, plataforma, status, observacoes)
    return gravar(conexao,
        'INSERT INTO jogos (titulo, plataforma, status, observacoes) VALUES (%s, %s, %s, %s)',
        valores, retornar_id=True)


def listar(conexao, status=None):
    if status is not None:
        if status not in STATUS:
            raise ValueError('Status inválido.')
        return consultar(conexao, 'SELECT * FROM jogos WHERE status = %s ORDER BY titulo, id', (status,))
    return consultar(conexao, 'SELECT * FROM jogos ORDER BY titulo, id')


def obter(conexao, identificador):
    return consultar(conexao, 'SELECT * FROM jogos WHERE id = %s', (identificador,), unico=True)


def atualizar(conexao, identificador, titulo, plataforma, status, observacoes):
    valores = validar(titulo, plataforma, status, observacoes)
    return gravar(conexao,
        'UPDATE jogos SET titulo = %s, plataforma = %s, status = %s, observacoes = %s WHERE id = %s',
        valores + (identificador,))


def excluir(conexao, identificador):
    return gravar(conexao, 'DELETE FROM jogos WHERE id = %s', (identificador,))
