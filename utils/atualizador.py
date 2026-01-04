import requests
import webbrowser
from tkinter import messagebox

from versao import VERSAO_APP

URL_RELEASE = "https://api.github.com/repos/FrankSCarvalho/sistema_pdv/releases/latest"


def comparar_versoes(v1, v2):
    def normalizar(v):
        partes = v.strip().split(".")
        partes = [int(p) for p in partes]
        while len(partes) < 3:
            partes.append(0)
        return partes

    return normalizar(v1) > normalizar(v2)


def verificar_atualizacao(janela=None):
    try:
        resposta = requests.get(URL_RELEASE, timeout=5)

        if resposta.status_code != 200:
            return

        dados = resposta.json()
        versao_remota = dados.get("tag_name", "").replace("v", "")

        if not versao_remota:
            return

        # 🔑 AQUI ESTAVA FALTANDO
        if comparar_versoes(versao_remota, VERSAO_APP):
            if messagebox.askyesno(
                "Atualização disponível",
                f"Uma nova versão ({versao_remota}) está disponível.\n\n"
                "Deseja baixar agora?",
                parent=janela
            ):
                webbrowser.open(dados["html_url"])

    except Exception:
        pass  # silencioso
