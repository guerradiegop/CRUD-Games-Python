# CRUD de jogos — Python e MySQL

Cadastro de jogos digitais com título, plataforma, observações e um dos status: **Zerados**, **Platinados**, **Jogando** ou **Um dia eu jogo**.

A branch `main` contém a interface de terminal. A branch `tkinter` acrescenta uma interface gráfica e mantém o terminal disponível. Ambas usam a mesma tabela e o mesmo módulo `database.py`.

## 1. Criar o banco físico

Requisitos: Python 3.10+ e um **MySQL Server 8.0.16+** em execução. O MySQL Workbench é o cliente de administração; instalar apenas o Workbench não instala necessariamente o servidor.

1. No Workbench, abra a conexão com seu servidor MySQL.
2. Abra `schema.sql` em **File > Open SQL Script** e execute o script completo.
3. Atualize a lista de schemas: o banco `crud_games` terá a tabela `jogos`.
4. Configure um usuário com acesso ao banco. Há um exemplo comentado no final do script para criar um usuário com permissões de leitura e escrita; escolha sua própria senha antes de executá-lo.

Também é possível executar o script com o cliente de linha de comando:

```bash
mysql -u root -p < schema.sql
```

O programa conecta a esse banco no servidor e não cria um arquivo SQLite nem executa DDL automaticamente. A implementação é para MySQL; PostgreSQL e SQL Server exigem outros drivers e adaptações no SQL. Dados do arquivo SQLite da versão anterior não são importados automaticamente.

## 2. Instalar e configurar

```bash
git clone https://github.com/guerradiegop/CRUD-Games-Python.git
cd CRUD-Games-Python
python -m venv .venv
```

Ative o ambiente no Windows PowerShell com `.venv\Scripts\Activate.ps1`; no Linux/macOS, use `source .venv/bin/activate`. Depois:

```bash
python -m pip install -r requirements.txt
```

Copie `config.example.ini` para `config.ini` e preencha host, porta, usuário, senha e banco. A configuração é lida da pasta do projeto, independentemente da pasta de execução. `config.ini` está no `.gitignore`; não publique credenciais.

Opcionalmente, use as variáveis de ambiente `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD` e `DB_DATABASE`. Elas têm prioridade sobre o arquivo. Senhas com `%` são aceitas no INI.

## 3. Executar

```bash
python app.py
```

No Linux/macOS, use `python3` se necessário; no Windows, também é possível usar `py`.

O menu permite cadastrar, listar, filtrar por status, editar e excluir pelo ID, com confirmação antes da exclusão. Na edição, Enter mantém o campo e `/limpar` apaga as observações.

Título e plataforma são obrigatórios. Limites: título de 150 caracteres, plataforma de 80 e observações de 5000. As consultas utilizam parâmetros e as gravações são confirmadas com `commit`; em erros de gravação ocorre `rollback`.

## Estrutura e verificações

- `app.py`: menu de terminal.
- `database.py`: configuração, conexão, validações e CRUD.
- `schema.sql`: criação do banco e da tabela.
- `config.example.ini`: modelo de conexão sem credenciais reais.
- `tests/`: testes de configuração, consultas e transações.

Execute os testes sem precisar de servidor:

```bash
python -m unittest discover -s tests -v
```

Os testes unitários usam conexões simuladas; não substituem uma validação no servidor MySQL. O teste de integração é opcional, usa a configuração local e remove somente o registro de teste ao finalizar:

```bash
python tests/integration_mysql.py
```

Se houver falha de conexão, verifique se o servidor está ativo, a porta (normalmente 3306), as credenciais e o acesso do usuário ao schema. Se a tabela não existir, execute `schema.sql`. Para usar um servidor em outra máquina, ajuste `host` e as permissões do usuário no MySQL.

## Interface gráfica (branch tkinter)

Após configurar o mesmo servidor e `config.ini` descritos acima:

```bash
git switch tkinter
python gui.py
```

A tela contém formulário de título, plataforma, status e observações, uma lista de jogos e filtro por status. Para cadastrar, clique em **Novo / Limpar**, preencha o formulário e clique em **Salvar**. Para editar, selecione uma linha, altere os campos e clique em **Salvar**. Para excluir, selecione uma linha e use **Excluir selecionado**, confirmando a ação. Para apagar as observações, esvazie o campo antes de salvar.

Tkinter costuma acompanhar o instalador oficial do Python no Windows/macOS. No Ubuntu/Debian, instale `python3-tk` se estiver ausente. Verifique a instalação com `python -m tkinter`. É necessário um ambiente desktop com suporte gráfico; o aplicativo não abre em um terminal sem display.

O terminal continua disponível com `python app.py`. As duas interfaces compartilham `database.py` e operam nos mesmos dados MySQL.
