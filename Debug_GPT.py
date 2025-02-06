import os

# Caminhos dos arquivos
arquivos = {
    "pesos.json": r"G:\Meu Drive\PYTHON\Programa\Controle_Estudo\bkp\Versao 18 - Web\projeto_web\data\pesos.json",
    "modelo_pagina_pesos.html": r"G:\Meu Drive\PYTHON\Programa\Controle_Estudo\bkp\Versao 18 - Web\projeto_web\templates\modelo_pagina_pesos.html",
    "pesos_modelo.json": r"G:\Meu Drive\PYTHON\Programa\Controle_Estudo\bkp\Versao 18 - Web\projeto_web\data\pesos_modelo.json",
    "log.txt": r"G:\Meu Drive\PYTHON\Programa\Controle_Estudo\bkp\Versao 18 - Web\projeto_web\log.txt",
    "pesos.html": r"G:\Meu Drive\PYTHON\Programa\Controle_Estudo\bkp\Versao 18 - Web\projeto_web\templates\pesos.html",
    "app.py": r"G:\Meu Drive\PYTHON\Programa\Controle_Estudo\bkp\Versao 18 - Web\projeto_web\app.py",
    "ControleDeEstudos.py": r"G:\Meu Drive\PYTHON\Programa\Controle_Estudo\bkp\Versao 18 - Web\projeto_web\ControleDeEstudos.py",
    "script.js": r"G:\Meu Drive\PYTHON\Programa\Controle_Estudo\bkp\Versao 18 - Web\projeto_web\static\js\script.js"
}

# Função para ler o conteúdo de um arquivo
def ler_arquivo(caminho, encoding='utf-8'):
    try:
        with open(caminho, 'r', encoding=encoding) as file:
            return file.read()
    except Exception as e:
        return f"Erro ao ler o arquivo {caminho}: {e}"

# Função para combinar os conteúdos
def combinar_conteudos(arquivos, ordem_arquivos):
    conteudo_final = ""
    for nome, prefixo in ordem_arquivos:
        caminho = arquivos[nome]
        conteudo = ler_arquivo(caminho)
        conteudo_final += f"### {prefixo} ###\n{conteudo}\n\n"
    return conteudo_final

# Definir a ordem e os prefixos para cada arquivo combinado
ordens = [
    [
        ("pesos.json", "Veja o que você gerou no pesos.json:"),
        ("modelo_pagina_pesos.html", "Veja o que eu esperava no pesos.html:"),
        ("pesos_modelo.json", "Veja o que eu esperava no pesos.json:")
    ],
    [
        ("log.txt", "log.txt"),
        ("pesos.html", "pesos.html")
    ],
    [
        ("app.py", "app.py"),
        ("ControleDeEstudos.py", "ControleDeEstudos.py")
    ],
    [
        ("script.js", "script.js")
    ]
]

# Caminhos dos arquivos combinados
caminhos_arquivos_combinados = [
    r"G:\Meu Drive\PYTHON\Programa\Controle_Estudo\bkp\Versao 18 - Web\projeto_web\arquivo_debug_controle_estudo_1.txt",
    r"G:\Meu Drive\PYTHON\Programa\Controle_Estudo\bkp\Versao 18 - Web\projeto_web\arquivo_debug_controle_estudo_2.txt",
    r"G:\Meu Drive\PYTHON\Programa\Controle_Estudo\bkp\Versao 18 - Web\projeto_web\arquivo_debug_controle_estudo_3.txt",
    r"G:\Meu Drive\PYTHON\Programa\Controle_Estudo\bkp\Versao 18 - Web\projeto_web\arquivo_debug_controle_estudo_4.txt"
]

# Combinar e escrever os conteúdos em arquivos distintos
for i in range(4):
    conteudo_combinado = combinar_conteudos(arquivos, ordens[i])
    caminho_arquivo_combinado = caminhos_arquivos_combinados[i]
    with open(caminho_arquivo_combinado, 'w', encoding='utf-8') as file:
        file.write(conteudo_combinado)
    print(f"Conteúdo combinado foi salvo em {caminho_arquivo_combinado}")

# Abre os arquivos combinados no editor de texto padrão
for caminho in caminhos_arquivos_combinados:
    os.system(f'notepad "{caminho}"')