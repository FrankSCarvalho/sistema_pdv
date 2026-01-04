import requests
import webbrowser
from tkinter import messagebox

from versao import VERSAO_APP

URL_RELEASE = "https://api.github.com/repos/frankcarvalho/estoque_loja/releases/latest"


def verificar_atualizacao(janela):
    try:
        resposta = requests.get(URL_RELEASE, timeout=5)
        resposta.raise_for_status()

        dados = resposta.json()
        versao_remota = dados["tag_name"].replace("v", "")

        if versao_remota > VERSAO_APP:
            if messagebox.askyesno(
                "Atualização disponível",
                f"Uma nova versão ({versao_remota}) está disponível.\n\n"
                f"Sua versão: {VERSAO_APP}\n\n"
                "Deseja baixar agora?",
                parent=janela
            ):
                webbrowser.open(dados["html_url"])

    except Exception:
        pass  # silencioso para não atrapalhar o uso
