"""Interface de terminal para o cadastro de jogos em MySQL."""

from mysql.connector import Error
from database import STATUS, conectar, cadastrar, listar, obter, atualizar, excluir


def ler_texto(rotulo, atual=None):
    while True:
        dica = f' [{atual}]' if atual is not None else ''
        valor = input(f'{rotulo}{dica}: ').strip()
        if not valor and atual is not None:
            return atual
        if valor:
            return valor
        print('Este campo é obrigatório.')


def ler_status(atual=None):
    for numero, nome in enumerate(STATUS, 1):
        print(f'{numero} - {nome}')
    while True:
        dica = f' (Enter mantém {atual})' if atual else ''
        valor = input(f'Status{dica}: ').strip()
        if not valor and atual:
            return atual
        if valor in ('1', '2', '3', '4'):
            return STATUS[int(valor) - 1]
        print('Escolha um número de 1 a 4.')


def ler_id():
    while True:
        try:
            identificador = int(input('ID do jogo: '))
            if identificador > 0:
                return identificador
        except ValueError:
            pass
        print('Informe um número inteiro positivo.')


def mostrar(jogos):
    if not jogos:
        print('Nenhum jogo encontrado.')
        return
    for jogo in jogos:
        print(f"\nID: {jogo['id']} | {jogo['titulo']} | {jogo['plataforma']} | {jogo['status']}")
        print(f"Observações: {jogo['observacoes'] or '-'}")


def executar_menu(conexao):
    while True:
        print('\n=== CADASTRO DE JOGOS ===\n1 - Cadastrar\n2 - Listar todos\n3 - Filtrar por status\n4 - Editar\n5 - Excluir\n0 - Sair')
        opcao = input('Opção: ').strip()
        try:
            if opcao == '0':
                return
            if opcao == '1':
                titulo = ler_texto('Título')
                plataforma = ler_texto('Plataforma')
                status = ler_status()
                observacoes = input('Observações (opcional): ')
                identificador = cadastrar(conexao, titulo, plataforma, status, observacoes)
                print(f'Jogo cadastrado com ID {identificador}.')
            elif opcao == '2':
                mostrar(listar(conexao))
            elif opcao == '3':
                mostrar(listar(conexao, ler_status()))
            elif opcao in ('4', '5'):
                identificador = ler_id()
                jogo = obter(conexao, identificador)
                if jogo is None:
                    print('Jogo não encontrado.')
                    continue
                mostrar([jogo])
                if opcao == '4':
                    print('Pressione Enter para manter um campo.')
                    titulo = ler_texto('Título', jogo['titulo'])
                    plataforma = ler_texto('Plataforma', jogo['plataforma'])
                    status = ler_status(jogo['status'])
                    observacoes = input(f"Observações [{jogo['observacoes']}] (digite /limpar para apagar): ").strip()
                    if observacoes == '/limpar':
                        observacoes = ''
                    elif not observacoes:
                        observacoes = jogo['observacoes']
                    if atualizar(conexao, identificador, titulo, plataforma, status, observacoes):
                        print('Jogo atualizado.')
                    else:
                        print('O jogo não existe mais.')
                elif input('Confirmar exclusão? (s/n): ').strip().lower() == 's':
                    if excluir(conexao, identificador):
                        print('Jogo excluído.')
                    else:
                        print('O jogo já havia sido removido.')
                else:
                    print('Exclusão cancelada.')
            else:
                print('Opção inválida.')
        except (Error, ValueError) as erro:
            print(f'Não foi possível concluir a operação: {erro}')


def main():
    conexao = None
    try:
        conexao = conectar()
        executar_menu(conexao)
    except (EOFError, KeyboardInterrupt):
        print('\nPrograma encerrado.')
    except (Error, ValueError) as erro:
        print(f'Não foi possível abrir o banco de dados: {erro}')
    finally:
        if conexao is not None:
            conexao.close()


if __name__ == '__main__':
    main()
