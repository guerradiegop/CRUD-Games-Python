"""Interface gráfica simples para o CRUD de jogos em MySQL."""

import tkinter as tk
from tkinter import messagebox, ttk

from mysql.connector import Error
import database as db


class CadastroJogos:
    def __init__(self, janela, conexao):
        self.janela = janela
        self.conexao = conexao
        self.identificador = None
        janela.title('Cadastro de jogos — MySQL')
        janela.geometry('950x620')
        janela.minsize(760, 550)
        janela.protocol('WM_DELETE_WINDOW', self.fechar)

        painel = ttk.Frame(janela, padding=16)
        painel.pack(fill='both', expand=True)
        painel.columnconfigure(1, weight=1)
        painel.rowconfigure(8, weight=1)

        ttk.Label(painel, text='Meus jogos', font=('Arial', 18, 'bold')).grid(
            row=0, column=0, columnspan=2, sticky='w', pady=(0, 12))
        self.titulo = tk.StringVar()
        self.plataforma = tk.StringVar()
        self.status = tk.StringVar(value=db.STATUS[2])
        self.filtro = tk.StringVar(value='Todos')
        self.mensagem = tk.StringVar(value='Novo cadastro')

        for linha, (rotulo, variavel) in enumerate(
            [('Título', self.titulo), ('Plataforma', self.plataforma)], 1
        ):
            ttk.Label(painel, text=rotulo).grid(row=linha, column=0, sticky='w', padx=(0, 12))
            ttk.Entry(painel, textvariable=variavel).grid(row=linha, column=1, sticky='ew', pady=4)
        ttk.Label(painel, text='Status').grid(row=3, column=0, sticky='w')
        ttk.Combobox(painel, textvariable=self.status, values=db.STATUS, state='readonly').grid(
            row=3, column=1, sticky='ew', pady=4)
        ttk.Label(painel, text='Observações').grid(row=4, column=0, sticky='nw', pady=4)
        self.observacoes = tk.Text(painel, height=4, wrap='word')
        self.observacoes.grid(row=4, column=1, sticky='ew', pady=4)

        botoes = ttk.Frame(painel)
        botoes.grid(row=5, column=0, columnspan=2, sticky='w', pady=10)
        for rotulo, comando in [('Novo / Limpar', self.limpar), ('Salvar', self.salvar),
                                ('Excluir selecionado', self.excluir)]:
            ttk.Button(botoes, text=rotulo, command=comando).pack(side='left', padx=(0, 8))
        ttk.Label(painel, textvariable=self.mensagem).grid(row=6, column=0, columnspan=2, sticky='w')

        filtros = ttk.Frame(painel)
        filtros.grid(row=7, column=0, columnspan=2, sticky='ew', pady=10)
        ttk.Label(filtros, text='Filtrar por status:').pack(side='left', padx=(0, 8))
        seletor = ttk.Combobox(filtros, textvariable=self.filtro,
                              values=('Todos',) + db.STATUS, state='readonly', width=22)
        seletor.pack(side='left')
        seletor.bind('<<ComboboxSelected>>', self.recarregar)
        ttk.Button(filtros, text='Atualizar lista', command=self.recarregar).pack(side='left', padx=8)

        lista = ttk.Frame(painel)
        lista.grid(row=8, column=0, columnspan=2, sticky='nsew')
        lista.columnconfigure(0, weight=1)
        lista.rowconfigure(0, weight=1)
        colunas = ('id', 'titulo', 'plataforma', 'status')
        self.tabela = ttk.Treeview(lista, columns=colunas, show='headings', selectmode='browse')
        for coluna, rotulo, largura in [('id', 'ID', 60), ('titulo', 'Título', 350),
                                        ('plataforma', 'Plataforma', 140), ('status', 'Status', 180)]:
            self.tabela.heading(coluna, text=rotulo)
            self.tabela.column(coluna, width=largura, minwidth=50)
        self.tabela.grid(row=0, column=0, sticky='nsew')
        rolagem = ttk.Scrollbar(lista, orient='vertical', command=self.tabela.yview)
        rolagem.grid(row=0, column=1, sticky='ns')
        self.tabela.configure(yscrollcommand=rolagem.set)
        self.tabela.bind('<<TreeviewSelect>>', self.selecionar)
        self.recarregar()

    def limpar(self):
        self.identificador = None
        self.titulo.set('')
        self.plataforma.set('')
        self.status.set(db.STATUS[2])
        self.observacoes.delete('1.0', 'end')
        self.tabela.selection_remove(*self.tabela.selection())
        self.mensagem.set('Novo cadastro')

    def recarregar(self, evento=None):
        try:
            filtro = self.filtro.get()
            jogos = db.listar(self.conexao, None if filtro == 'Todos' else filtro)
        except (Error, ValueError) as erro:
            messagebox.showerror('Falha ao listar', str(erro), parent=self.janela)
            return
        self.tabela.delete(*self.tabela.get_children())
        self.limpar()
        for jogo in jogos:
            self.tabela.insert('', 'end', iid=str(jogo['id']),
                values=(jogo['id'], jogo['titulo'], jogo['plataforma'], jogo['status']))
        self.mensagem.set(f'{len(jogos)} jogo(s) na lista. Selecione um jogo para editar.')

    def selecionar(self, evento=None):
        selecao = self.tabela.selection()
        if not selecao:
            return
        try:
            jogo = db.obter(self.conexao, int(selecao[0]))
        except Error as erro:
            self.limpar()
            messagebox.showerror('Falha ao selecionar', str(erro), parent=self.janela)
            return
        if jogo is None:
            self.recarregar()
            return
        self.identificador = jogo['id']
        self.titulo.set(jogo['titulo'])
        self.plataforma.set(jogo['plataforma'])
        self.status.set(jogo['status'])
        self.observacoes.delete('1.0', 'end')
        self.observacoes.insert('1.0', jogo['observacoes'])
        self.mensagem.set(f"Editando jogo #{jogo['id']}")

    def salvar(self):
        valores = (self.titulo.get(), self.plataforma.get(), self.status.get(),
                   self.observacoes.get('1.0', 'end-1c'))
        try:
            if self.identificador is None:
                identificador = db.cadastrar(self.conexao, *valores)
            else:
                identificador = self.identificador
                if not db.atualizar(self.conexao, identificador, *valores):
                    messagebox.showwarning('Jogo não encontrado', 'O jogo foi removido. Atualize a lista.', parent=self.janela)
                    return
        except (Error, ValueError) as erro:
            messagebox.showerror('Não foi possível salvar', str(erro), parent=self.janela)
            return
        self.recarregar()
        self.mensagem.set(f'Jogo #{identificador} salvo.')

    def excluir(self):
        if self.identificador is None:
            messagebox.showwarning('Selecione um jogo', 'Selecione o jogo que deseja excluir.', parent=self.janela)
            return
        if not messagebox.askyesno('Confirmar exclusão',
            f'Excluir "{self.titulo.get()}"?', parent=self.janela):
            return
        try:
            removido = db.excluir(self.conexao, self.identificador)
        except Error as erro:
            messagebox.showerror('Não foi possível excluir', str(erro), parent=self.janela)
            return
        self.recarregar()
        self.mensagem.set('Jogo excluído.' if removido else 'O jogo já havia sido removido.')

    def fechar(self):
        try:
            self.conexao.close()
        finally:
            self.janela.destroy()


def main():
    janela = tk.Tk()
    janela.withdraw()
    try:
        conexao = db.conectar()
    except (Error, ValueError) as erro:
        messagebox.showerror('Falha de conexão com MySQL',
            f'{erro}\n\nConfira config.ini e execute schema.sql no servidor.', parent=janela)
        janela.destroy()
        return
    try:
        CadastroJogos(janela, conexao)
        janela.deiconify()
        janela.mainloop()
    finally:
        conexao.close()


if __name__ == '__main__':
    main()
