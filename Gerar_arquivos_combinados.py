import os

# Diretórios dos arquivos
arquivos = {
    "projeto_web": [
        r"G:\Meu Drive\PYTHON\Programa\Controle_Estudo\bkp\Versao 18 - Web\projeto_web\app.py",
        r"G:\Meu Drive\PYTHON\Programa\Controle_Estudo\bkp\Versao 18 - Web\projeto_web\ControleDeEstudos.py",
        r"G:\Meu Drive\PYTHON\Programa\Controle_Estudo\bkp\Versao 18 - Web\projeto_web\TagProcessor.py"
    ],
    "data": [
        r"G:\Meu Drive\PYTHON\Programa\Controle_Estudo\bkp\Versao 18 - Web\projeto_web\data\pesos.json",
        r"G:\Meu Drive\PYTHON\Programa\Controle_Estudo\bkp\Versao 18 - Web\projeto_web\data\progresso.json",
        r"G:\Meu Drive\PYTHON\Programa\Controle_Estudo\bkp\Versao 18 - Web\projeto_web\data\topicos_estudo.txt",
        r"G:\Meu Drive\PYTHON\Programa\Controle_Estudo\bkp\Versao 18 - Web\projeto_web\data\topicos_musica.txt"
    ],
    "static": [
        r"G:\Meu Drive\PYTHON\Programa\Controle_Estudo\bkp\Versao 18 - Web\projeto_web\static\js\script.js",
        r"G:\Meu Drive\PYTHON\Programa\Controle_Estudo\bkp\Versao 18 - Web\projeto_web\static\css\style.css"
    ],
    "templates": [
        r"G:\Meu Drive\PYTHON\Programa\Controle_Estudo\bkp\Versao 18 - Web\projeto_web\templates\configuracoes.html",
        r"G:\Meu Drive\PYTHON\Programa\Controle_Estudo\bkp\Versao 18 - Web\projeto_web\templates\index.html",
        r"G:\Meu Drive\PYTHON\Programa\Controle_Estudo\bkp\Versao 18 - Web\projeto_web\templates\musica.html",
        r"G:\Meu Drive\PYTHON\Programa\Controle_Estudo\bkp\Versao 18 - Web\projeto_web\templates\pesos.html",
        r"G:\Meu Drive\PYTHON\Programa\Controle_Estudo\bkp\Versao 18 - Web\projeto_web\templates\topicos.html"
    ]
}

# Caminhos para os arquivos de saída
arquivos_saida = {
    "projeto_web": r"G:\Meu Drive\PYTHON\Programa\Controle_Estudo\bkp\Versao 18 - Web\projeto_web\arquivo_debug_controle_estudo_1.txt",
    "data": r"G:\Meu Drive\PYTHON\Programa\Controle_Estudo\bkp\Versao 18 - Web\projeto_web\arquivo_debug_controle_estudo_2.txt",
    "static": r"G:\Meu Drive\PYTHON\Programa\Controle_Estudo\bkp\Versao 18 - Web\projeto_web\arquivo_debug_controle_estudo_3.txt",
    "templates": r"G:\Meu Drive\PYTHON\Programa\Controle_Estudo\bkp\Versao 18 - Web\projeto_web\arquivo_debug_controle_estudo_4.txt"
}

def criar_arquivos_separados(arquivos, arquivos_saida):
    for categoria, lista_arquivos in arquivos.items():
        caminho_saida = arquivos_saida[categoria]
        print(f"Criando arquivo de saída para a categoria: {categoria} -> {caminho_saida}")
        with open(caminho_saida, 'w', encoding='utf-8') as arquivo_final:
            for caminho in lista_arquivos:
                if os.path.exists(caminho):
                    print(f"Lendo arquivo: {caminho}")
                    with open(caminho, 'r', encoding='utf-8') as arquivo:
                        conteudo = arquivo.read()
                    arquivo_final.write(f"--- {os.path.basename(caminho)} ---\n")
                    arquivo_final.write(conteudo + "\n\n")
                else:
                    print(f"Arquivo não encontrado: {caminho}")
                    arquivo_final.write(f"--- {os.path.basename(caminho)} ---\n")
                    arquivo_final.write("Arquivo não encontrado.\n\n")

# Chamar a função para criar os arquivos separados
criar_arquivos_separados(arquivos, arquivos_saida)

print("Arquivos de saída criados com sucesso.")
