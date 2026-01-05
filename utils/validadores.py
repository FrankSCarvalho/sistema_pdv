def normalizar_numero(texto):
    """
    Converte um número em formato brasileiro (com vírgula) 
    para o formato Python/banco de dados (com ponto).
    
    Exemplos:
        "10,50" -> 10.50
        "10.50" -> 10.50
        "1.250,99" -> 1250.99
        "" -> 0.0
    
    Args:
        texto (str): O texto digitado pelo usuário
        
    Returns:
        float: O número convertido
        
    Raises:
        ValueError: Se o texto não for um número válido
    """
    if not texto or texto.strip() == "":
        return 0.0
    
    # Remove espaços em branco
    texto = texto.strip()
    
    # Se tiver ponto E vírgula, assume formato brasileiro: 1.250,99
    # O ponto é separador de milhar e a vírgula é decimal
    if "." in texto and "," in texto:
        texto = texto.replace(".", "")  # Remove pontos (milhares)
        texto = texto.replace(",", ".")  # Troca vírgula por ponto
    # Se tiver apenas vírgula, troca por ponto
    elif "," in texto:
        texto = texto.replace(",", ".")
    # Se tiver apenas ponto, mantém como está
    
    # Converte para float
    try:
        return float(texto)
    except ValueError:
        raise ValueError(f"'{texto}' não é um número válido")
    
def formatar_moeda(valor):
    """
    Formata um número para o padrão brasileiro de moeda.
    
    Exemplos:
        1234.50 -> "R$ 1.234,50"
        10.5 -> "R$ 10,50"
        0 -> "R$ 0,00"
    
    Args:
        valor (float): O valor numérico a ser formatado
        
    Returns:
        str: O valor formatado como string no padrão brasileiro
    """
    if valor is None:
        valor = 0.0
    
    # Formata o número com 2 casas decimais e separador de milhares
    valor_formatado = f"{valor:,.2f}"
    
    # Troca ponto por vírgula (decimal) e vírgula por ponto (milhares)
    valor_formatado = valor_formatado.replace(",", "X")  # Temporário
    valor_formatado = valor_formatado.replace(".", ",")  # Ponto vira vírgula
    valor_formatado = valor_formatado.replace("X", ".")  # Vírgula vira ponto
    
    return f"R$ {valor_formatado}"