import tkinter as tk
from tkinter import ttk, messagebox

from dao.usuario_dao import autenticar_usuario, criar_usuario_admin_padrao


class TelaLogin(tk.Tk):
    """
    Tela de login do sistema.
    
    Permite que o usuário faça login com seu nome de usuário e senha.
    Se não existir nenhum usuário no sistema, cria automaticamente
    um usuário administrador padrão (login: admin, senha: admin123).
    """
    
    def __init__(self):
        super().__init__()
        self.title("Sistema PDV - Login")
        self.geometry("400x350")
        self.resizable(False, False)
        
        # Usuário autenticado (será preenchido após login bem-sucedido)
        self.usuario_autenticado = None
        
        # Cria usuário admin padrão se não existir nenhum usuário
        if criar_usuario_admin_padrao():
            messagebox.showinfo(
                "Primeiro Acesso",
                "Usuário administrador criado!\n\n"
                "Login: admin\n"
                "Senha: admin123\n\n"
                "Por favor, altere a senha após o primeiro login.",
                parent=self
            )
        
        self._criar_widgets()
        self._centralizar_janela()
        
        # Foca no campo de login
        self.entry_login.focus()
    
    def _criar_widgets(self):
        """Cria os elementos da interface."""
        
        # Frame principal
        frame_principal = tk.Frame(self, padx=40, pady=30)
        frame_principal.pack(expand=True, fill="both")
        
        # Logo/Título
        tk.Label(
            frame_principal,
            text="🛒 Sistema PDV",
            font=("Arial", 20, "bold"),
            fg="#2196F3"
        ).pack(pady=(0, 10))
        
        tk.Label(
            frame_principal,
            text="Controle de Estoque",
            font=("Arial", 12),
            fg="gray"
        ).pack(pady=(0, 30))
        
        # Frame do formulário
        frame_form = tk.Frame(frame_principal)
        frame_form.pack(fill="x")
        
        # Campo Login
        tk.Label(
            frame_form,
            text="Usuário:",
            font=("Arial", 10, "bold")
        ).pack(anchor="w", pady=(0, 5))
        
        self.entry_login = tk.Entry(
            frame_form,
            font=("Arial", 11),
            width=30
        )
        self.entry_login.pack(fill="x", pady=(0, 15))
        self.entry_login.bind("<Return>", lambda e: self.entry_senha.focus())
        
        # Campo Senha
        tk.Label(
            frame_form,
            text="Senha:",
            font=("Arial", 10, "bold")
        ).pack(anchor="w", pady=(0, 5))
        
        self.entry_senha = tk.Entry(
            frame_form,
            font=("Arial", 11),
            width=30,
            show="●"
        )
        self.entry_senha.pack(fill="x", pady=(0, 25))
        self.entry_senha.bind("<Return>", lambda e: self._fazer_login())
        
        # Botão Entrar
        self.btn_entrar = tk.Button(
            frame_form,
            text="ENTRAR",
            command=self._fazer_login,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 11, "bold"),
            height=2,
            cursor="hand2",
            relief="flat"
        )
        self.btn_entrar.pack(fill="x")
        
        # Efeito hover no botão
        self.btn_entrar.bind("<Enter>", lambda e: self.btn_entrar.config(bg="#45a049"))
        self.btn_entrar.bind("<Leave>", lambda e: self.btn_entrar.config(bg="#4CAF50"))
        
        # Rodapé
        tk.Label(
            frame_principal,
            text="Versão 2.0.0 - Sistema com Login",
            font=("Arial", 8),
            fg="gray"
        ).pack(side="bottom", pady=(20, 0))
    
    def _centralizar_janela(self):
        """Centraliza a janela na tela."""
        self.update_idletasks()
        
        # Dimensões da janela
        largura = self.winfo_width()
        altura = self.winfo_height()
        
        # Dimensões da tela
        largura_tela = self.winfo_screenwidth()
        altura_tela = self.winfo_screenheight()
        
        # Calcula posição
        x = (largura_tela // 2) - (largura // 2)
        y = (altura_tela // 2) - (altura // 2)
        
        self.geometry(f"{largura}x{altura}+{x}+{y}")
    
    def _fazer_login(self):
        """Realiza o processo de autenticação."""
        login = self.entry_login.get().strip()
        senha = self.entry_senha.get()
        
        # Validações básicas
        if not login:
            messagebox.showwarning(
                "Atenção",
                "Por favor, digite seu usuário.",
                parent=self
            )
            self.entry_login.focus()
            return
        
        if not senha:
            messagebox.showwarning(
                "Atenção",
                "Por favor, digite sua senha.",
                parent=self
            )
            self.entry_senha.focus()
            return
        
        # Desabilita botão durante autenticação
        self.btn_entrar.config(state="disabled", text="Autenticando...")
        self.update()
        
        try:
            # Tenta autenticar
            usuario = autenticar_usuario(login, senha)
            
            if usuario:
                # Login bem-sucedido
                self.usuario_autenticado = usuario
                
                messagebox.showinfo(
                    "Login Realizado",
                    f"Bem-vindo(a), {usuario.nome}!\n\n"
                    f"Nível de acesso: {usuario.get_nivel_nome()}",
                    parent=self
                )
                
                # Fecha a tela de login (o main.py abrirá a tela principal)
                self.destroy()
            else:
                # Login falhou
                messagebox.showerror(
                    "Erro de Autenticação",
                    "Usuário ou senha incorretos.\n\n"
                    "Por favor, verifique suas credenciais e tente novamente.",
                    parent=self
                )
                
                # Limpa senha e foca no campo de login
                self.entry_senha.delete(0, tk.END)
                self.entry_login.focus()
                self.entry_login.select_range(0, tk.END)
                self.btn_entrar.config(state="normal", text="ENTRAR")
        
        except Exception as e:
            messagebox.showerror(
                "Erro",
                f"Erro ao tentar fazer login:\n\n{str(e)}",
                parent=self
            )
        
        finally:
            # Reabilita botão
            #self.btn_entrar.config(state="normal", text="ENTRAR")
            pass
    
    def get_usuario_autenticado(self):
        """
        Retorna o usuário autenticado.
        
        Returns:
            Usuario ou None: Objeto Usuario se login foi bem-sucedido
        """
        return self.usuario_autenticado


if __name__ == "__main__":
    # Teste da tela de login
    app = TelaLogin()
    app.mainloop()
    
    if app.usuario_autenticado:
        print(f"Login bem-sucedido: {app.usuario_autenticado}")
    else:
        print("Login cancelado ou falhou")
