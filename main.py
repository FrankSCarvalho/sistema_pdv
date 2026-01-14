from telas.tela_login import TelaLogin
from telas.tela_principal import TelaPrincipal

if __name__ == "__main__":
    # Abre a tela de login
    tela_login = TelaLogin()
    tela_login.mainloop()
    
    # Se o login foi bem-sucedido, abre a tela principal
    usuario_autenticado = tela_login.get_usuario_autenticado()
    
    if usuario_autenticado:
        app = TelaPrincipal(usuario_logado=usuario_autenticado)
        app.mainloop()
