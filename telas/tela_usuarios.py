import tkinter as tk
from tkinter import ttk, messagebox

from modelos.usuario import Usuario
from dao.usuarios_dao import (
    inserir_usuario,
    atualizar_usuario,
    listar_usuarios,
    buscar_usuario_por_id,
    desativar_usuario,
    reativar_usuario,
    alterar_senha
)


class TelaUsuarios(tk.Toplevel):
    """
    Tela de gerenciamento de usuários do sistema.
    Apenas administradores podem acessar esta tela.
    """
    
    def __init__(self, master=None, usuario_logado=None):
        super().__init__(master)
        self.title("Gerenciamento de Usuários")
        self.geometry("900x600")
        
        self.usuario_logado = usuario_logado
        self.usuario_selecionado_id = None
        self.usuario_selecionado_ativo = True
        
        # Verifica permissão
        if not usuario_logado or not usuario_logado.pode_gerenciar_usuarios():
            messagebox.showerror(
                "Acesso Negado",
                "Apenas administradores podem gerenciar usuários.",
                parent=self
            )
            self.destroy()
            return
        
        self._criar_widgets()
        self._carregar_usuarios()
    
    def _criar_widgets(self):
        """Cria os elementos da interface."""
        
        # Frame de cadastro
        frame_form = tk.LabelFrame(self, text="Cadastro de Usuário", padx=10, pady=10)
        frame_form.pack(fill="x", padx=10, pady=(10, 5))
        
        # Campos
        tk.Label(frame_form, text="Nome Completo:*").grid(row=0, column=0, sticky="w", pady=5)
        tk.Label(frame_form, text="Login:*").grid(row=0, column=2, sticky="w", pady=5)
        tk.Label(frame_form, text="Senha:*").grid(row=1, column=0, sticky="w", pady=5)
        tk.Label(frame_form, text="Nível de Acesso:*").grid(row=1, column=2, sticky="w", pady=5)
        
        self.entry_nome = tk.Entry(frame_form, width=30)
        self.entry_login = tk.Entry(frame_form, width=25)
        self.entry_senha = tk.Entry(frame_form, width=25, show="●")
        
        self.combo_nivel = ttk.Combobox(
            frame_form,
            values=["1 - Administrador", "2 - Gerente", "3 - Vendedor"],
            state="readonly",
            width=22
        )
        self.combo_nivel.current(2)  # Padrão: Vendedor
        
        self.entry_nome.grid(row=0, column=1, padx=5, pady=5, sticky="we")
        self.entry_login.grid(row=0, column=3, padx=5, pady=5, sticky="we")
        self.entry_senha.grid(row=1, column=1, padx=5, pady=5, sticky="we")
        self.combo_nivel.grid(row=1, column=3, padx=5, pady=5, sticky="we")
        
        frame_form.columnconfigure(1, weight=1)
        frame_form.columnconfigure(3, weight=1)
        
        # Botões de ação
        frame_botoes = tk.Frame(self)
        frame_botoes.pack(fill="x", padx=10, pady=5)
        
        self.btn_salvar = tk.Button(
            frame_botoes,
            text="💾 Salvar Novo",
            command=self._salvar,
            bg="#4CAF50",
            fg="white",
            cursor="hand2"
        )
        self.btn_salvar.pack(side="left", padx=2)
        
        self.btn_atualizar = tk.Button(
            frame_botoes,
            text="✏️ Atualizar",
            command=self._atualizar,
            cursor="hand2"
        )
        self.btn_atualizar.pack(side="left", padx=2)
        
        self.btn_alterar_senha = tk.Button(
            frame_botoes,
            text="🔑 Alterar Senha",
            command=self._alterar_senha,
            cursor="hand2"
        )
        self.btn_alterar_senha.pack(side="left", padx=2)
        
        tk.Button(
            frame_botoes,
            text="🗑️ Limpar",
            command=self._limpar,
            cursor="hand2"
        ).pack(side="left", padx=2)
        
        self.btn_desativar = tk.Button(
            frame_botoes,
            text="❌ Desativar",
            command=self._desativar,
            bg="#ffcccc",
            cursor="hand2"
        )
        self.btn_desativar.pack(side="left", padx=2)
        
        self.btn_reativar = tk.Button(
            frame_botoes,
            text="✅ Reativar",
            command=self._reativar,
            bg="#ccffcc",
            cursor="hand2"
        )
        self.btn_reativar.pack(side="left", padx=2)
        
        # Checkbox para mostrar inativos
        frame_filtro = tk.Frame(self)
        frame_filtro.pack(fill="x", padx=10, pady=5)
        
        self.var_mostrar_inativos = tk.BooleanVar(value=False)
        tk.Checkbutton(
            frame_filtro,
            text="Mostrar usuários inativos",
            variable=self.var_mostrar_inativos,
            command=self._carregar_usuarios
        ).pack(side="left")
        
        # Tabela de usuários
        frame_lista = tk.Frame(self)
        frame_lista.pack(fill="both", expand=True, padx=10, pady=5)
        
        colunas = ("id", "status", "nome", "login", "nivel", "data_criacao", "ultimo_acesso")
        
        self.tree = ttk.Treeview(frame_lista, columns=colunas, show="headings")
        
        self.tree.heading("id", text="ID")
        self.tree.heading("status", text="Status")
        self.tree.heading("nome", text="Nome")
        self.tree.heading("login", text="Login")
        self.tree.heading("nivel", text="Nível de Acesso")
        self.tree.heading("data_criacao", text="Data de Criação")
        self.tree.heading("ultimo_acesso", text="Último Acesso")
        
        self.tree.column("id", width=40, anchor="center")
        self.tree.column("status", width=70, anchor="center")
        self.tree.column("nome", width=200)
        self.tree.column("login", width=120)
        self.tree.column("nivel", width=120, anchor="center")
        self.tree.column("data_criacao", width=140, anchor="center")
        self.tree.column("ultimo_acesso", width=140, anchor="center")
        
        scrollbar = ttk.Scrollbar(frame_lista, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.tree.bind("<<TreeviewSelect>>", self._selecionar_usuario)
        
        self._atualizar_visibilidade_botoes()
    
    def _carregar_usuarios(self):
        """Carrega a lista de usuários."""
        # Limpa a árvore
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Busca usuários
        mostrar_inativos = self.var_mostrar_inativos.get()
        usuarios = listar_usuarios(ativos_apenas=not mostrar_inativos)
        
        # Adiciona na árvore
        for usuario in usuarios:
            status = "ATIVO" if usuario.ativo == 1 else "INATIVO"
            
            self.tree.insert("", tk.END, values=(
                usuario.id,
                status,
                usuario.nome,
                usuario.login,
                usuario.get_nivel_nome(),
                usuario.data_criacao[:16] if usuario.data_criacao else "",
                usuario.ultimo_acesso[:16] if usuario.ultimo_acesso else "Nunca"
            ), tags=("inativo",) if usuario.ativo == 0 else ())
        
        self.tree.tag_configure("inativo", background="#ffcccc")
    
    def _salvar(self):
        """Salva um novo usuário."""
        try:
            nome = self.entry_nome.get().strip()
            login = self.entry_login.get().strip()
            senha = self.entry_senha.get()
            nivel_texto = self.combo_nivel.get()
            
            if not nome or not login or not senha:
                messagebox.showwarning(
                    "Atenção",
                    "Preencha todos os campos obrigatórios.",
                    parent=self
                )
                return
            
            if len(senha) < 6:
                messagebox.showwarning(
                    "Atenção",
                    "A senha deve ter no mínimo 6 caracteres.",
                    parent=self
                )
                return
            
            # Extrai o nível de acesso
            nivel_acesso = int(nivel_texto.split(" - ")[0])
            
            # Cria o usuário
            usuario = Usuario(
                nome=nome,
                login=login,
                senha_hash=Usuario.gerar_hash_senha(senha),
                nivel_acesso=nivel_acesso,
                ativo=1
            )
            
            inserir_usuario(usuario)
            self._carregar_usuarios()
            self._limpar()
            
            messagebox.showinfo(
                "Sucesso",
                f"Usuário '{nome}' cadastrado com sucesso!",
                parent=self
            )
        
        except ValueError as e:
            messagebox.showerror("Erro", str(e), parent=self)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar usuário:\n{str(e)}", parent=self)
    
    def _atualizar(self):
        """Atualiza os dados de um usuário existente."""
        if not self.usuario_selecionado_id:
            messagebox.showwarning("Atenção", "Selecione um usuário.", parent=self)
            return
        
        try:
            nome = self.entry_nome.get().strip()
            login = self.entry_login.get().strip()
            nivel_texto = self.combo_nivel.get()
            
            if not nome or not login:
                messagebox.showwarning(
                    "Atenção",
                    "Preencha todos os campos obrigatórios.",
                    parent=self
                )
                return
            
            nivel_acesso = int(nivel_texto.split(" - ")[0])
            
            # Busca o usuário atual
            usuario = buscar_usuario_por_id(self.usuario_selecionado_id)
            
            # Atualiza os dados (mantém a senha atual)
            usuario.nome = nome
            usuario.login = login
            usuario.nivel_acesso = nivel_acesso
            
            atualizar_usuario(usuario)
            self._carregar_usuarios()
            self._limpar()
            
            messagebox.showinfo("Sucesso", "Usuário atualizado!", parent=self)
        
        except ValueError as e:
            messagebox.showerror("Erro", str(e), parent=self)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar usuário:\n{str(e)}", parent=self)
    
    def _alterar_senha(self):
        """Abre janela para alterar a senha de um usuário."""
        if not self.usuario_selecionado_id:
            messagebox.showwarning("Atenção", "Selecione um usuário.", parent=self)
            return
        
        # Janela de alteração de senha
        janela = tk.Toplevel(self)
        janela.title("Alterar Senha")
        janela.geometry("350x200")
        janela.transient(self)
        janela.grab_set()
        
        frame = tk.Frame(janela, padx=20, pady=20)
        frame.pack(fill="both", expand=True)
        
        tk.Label(frame, text="Nova Senha:*", font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))
        entry_nova_senha = tk.Entry(frame, width=30, show="●", font=("Arial", 10))
        entry_nova_senha.pack(fill="x", pady=(0, 10))
        entry_nova_senha.focus()
        
        tk.Label(frame, text="Confirmar Senha:*", font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))
        entry_confirmar = tk.Entry(frame, width=30, show="●", font=("Arial", 10))
        entry_confirmar.pack(fill="x", pady=(0, 20))
        
        def salvar_nova_senha():
            senha1 = entry_nova_senha.get()
            senha2 = entry_confirmar.get()
            
            if not senha1 or not senha2:
                messagebox.showwarning("Atenção", "Preencha ambos os campos.", parent=janela)
                return
            
            if len(senha1) < 6:
                messagebox.showwarning(
                    "Atenção",
                    "A senha deve ter no mínimo 6 caracteres.",
                    parent=janela
                )
                return
            
            if senha1 != senha2:
                messagebox.showerror("Erro", "As senhas não coincidem.", parent=janela)
                return
            
            try:
                alterar_senha(self.usuario_selecionado_id, senha1)
                messagebox.showinfo("Sucesso", "Senha alterada com sucesso!", parent=janela)
                janela.destroy()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao alterar senha:\n{str(e)}", parent=janela)
        
        frame_botoes = tk.Frame(frame)
        frame_botoes.pack(fill="x")
        
        tk.Button(
            frame_botoes,
            text="✅ Salvar",
            command=salvar_nova_senha,
            bg="#4CAF50",
            fg="white",
            cursor="hand2"
        ).pack(side="left", expand=True, fill="x", padx=(0, 5))
        
        tk.Button(
            frame_botoes,
            text="❌ Cancelar",
            command=janela.destroy,
            cursor="hand2"
        ).pack(side="left", expand=True, fill="x", padx=(5, 0))
    
    def _desativar(self):
        """Desativa um usuário."""
        if not self.usuario_selecionado_id:
            messagebox.showwarning("Atenção", "Selecione um usuário.", parent=self)
            return
        
        if self.usuario_selecionado_id == self.usuario_logado.id:
            messagebox.showwarning(
                "Atenção",
                "Você não pode desativar seu próprio usuário.",
                parent=self
            )
            return
        
        if messagebox.askyesno("Confirmar", "Deseja desativar este usuário?", parent=self):
            desativar_usuario(self.usuario_selecionado_id)
            self._carregar_usuarios()
            self._limpar()
            messagebox.showinfo("Sucesso", "Usuário desativado!", parent=self)
    
    def _reativar(self):
        """Reativa um usuário."""
        if not self.usuario_selecionado_id:
            messagebox.showwarning("Atenção", "Selecione um usuário.", parent=self)
            return
        
        if messagebox.askyesno("Confirmar", "Deseja reativar este usuário?", parent=self):
            reativar_usuario(self.usuario_selecionado_id)
            self._carregar_usuarios()
            self._limpar()
            messagebox.showinfo("Sucesso", "Usuário reativado!", parent=self)
    
    def _limpar(self):
        """Limpa os campos do formulário."""
        self.usuario_selecionado_id = None
        self.usuario_selecionado_ativo = True
        
        self.entry_nome.delete(0, tk.END)
        self.entry_login.delete(0, tk.END)
        self.entry_senha.delete(0, tk.END)
        self.combo_nivel.current(2)
        
        self.btn_salvar.config(state="normal")
        self._atualizar_visibilidade_botoes()
    
    def _selecionar_usuario(self, event):
        """Preenche o formulário com os dados do usuário selecionado."""
        item = self.tree.selection()
        if not item:
            return
        
        valores = self.tree.item(item)["values"]
        usuario_id = valores[0]
        
        usuario = buscar_usuario_por_id(usuario_id)
        if not usuario:
            return
        
        self.usuario_selecionado_id = usuario.id
        self.usuario_selecionado_ativo = (usuario.ativo == 1)
        
        self.btn_salvar.config(state="disabled")
        self._atualizar_visibilidade_botoes()
        
        # Preenche os campos
        self.entry_nome.delete(0, tk.END)
        self.entry_nome.insert(0, usuario.nome)
        
        self.entry_login.delete(0, tk.END)
        self.entry_login.insert(0, usuario.login)
        
        self.entry_senha.delete(0, tk.END)
        self.entry_senha.insert(0, "******")  # Não mostra a senha real
        
        # Seleciona o nível de acesso
        nivel_map = {1: 0, 2: 1, 3: 2}
        self.combo_nivel.current(nivel_map.get(usuario.nivel_acesso, 2))
    
    def _atualizar_visibilidade_botoes(self):
        """Atualiza a visibilidade dos botões de acordo com o estado."""
        if self.usuario_selecionado_id is None:
            self.btn_desativar.pack_forget()
            self.btn_reativar.pack_forget()
        elif self.usuario_selecionado_ativo:
            self.btn_desativar.pack(side="left", padx=2)
            self.btn_reativar.pack_forget()
        else:
            self.btn_desativar.pack_forget()
            self.btn_reativar.pack(side="left", padx=2)


if __name__ == "__main__":
    # Teste da tela
    root = tk.Tk()
    root.withdraw()
    
    # Simula um usuário admin logado
    from modelos.usuario import Usuario
    usuario_teste = Usuario(id=1, nome="Admin", nivel_acesso=1)
    
    app = TelaUsuarios(root, usuario_logado=usuario_teste)
    app.mainloop()
