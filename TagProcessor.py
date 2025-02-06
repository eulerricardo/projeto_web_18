import json
import os
import re
import requests

# Define o diretório base como o diretório do script atual
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
output_dir = os.path.join(BASE_DIR, "data")

# Define os caminhos dos arquivos com base no diretório dinâmico
estudo_path = os.path.join(output_dir, "topicos_estudo.txt")
musica_path = os.path.join(output_dir, "topicos_musica.txt")
pesos_path = os.path.join(output_dir, "pesos.json")

# Garante que o diretório de saída exista
os.makedirs(output_dir, exist_ok=True)

def criar_arquivos_padrao(estudo_path, musica_path):
    """Gera arquivos padrão somente se houver sucesso na comunicação com o Anki."""
    with open(estudo_path, 'w', encoding='utf-8') as file:
        file.write("Exemplo de Tópico de Estudo 1\nExemplo de Tópico de Estudo 2\n")
    with open(musica_path, 'w', encoding='utf-8') as file:
        file.write("Exemplo de Tópico de Música 1\nExemplo de Tópico de Música 2\n")

def validar_e_corrigir_arquivo(file_path, output_path):
    """Verifica e corrige caracteres inválidos em um arquivo."""
    if not os.path.exists(file_path):
        return False

    try:
        with open(file_path, 'rb') as file:
            content = file.read()

        # Decodificar com substituição de caracteres inválidos
        cleaned_content = content.decode('utf-8', errors='replace')

        # Salvar o arquivo corrigido
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(cleaned_content)

        return True
    except Exception:
        return False

def importar_topicos_manuais(pesos_path, estudo_path, musica_path):
    """Importa tópicos manuais dos pesos.json para os arquivos de tópicos correspondentes."""
    if not os.path.exists(pesos_path):
        print(f"Erro: Arquivo '{pesos_path}' não encontrado.")
        return

    try:
        with open(pesos_path, 'r', encoding='utf-8') as file:
            pesos = json.load(file)

        topicos_manuais_estudo = [topico for topico, dados in pesos.get('estudo', {}).items() if dados.get('adicionado') == 'manual']
        topicos_manuais_musica = [topico for topico, dados in pesos.get('musica', {}).items() if dados.get('adicionado') == 'manual']

        # Ler os tópicos já existentes para evitar duplicatas
        if os.path.exists(estudo_path):
            with open(estudo_path, 'r', encoding='utf-8') as file:
                topicos_estudo_existentes = set(line.strip() for line in file)
        else:
            topicos_estudo_existentes = set()

        if os.path.exists(musica_path):
            with open(musica_path, 'r', encoding='utf-8') as file:
                topicos_musica_existentes = set(line.strip() for line in file)
        else:
            topicos_musica_existentes = set()

        # Adicionar tópicos manuais aos arquivos correspondentes, evitando duplicatas
        with open(estudo_path, 'a', encoding='utf-8') as file:
            for topico in topicos_manuais_estudo:
                if topico not in topicos_estudo_existentes:
                    file.write(f"\n{topico}")
                    topicos_estudo_existentes.add(topico)
            print(f"Tópicos de estudo manuais importados: {topicos_manuais_estudo}")

        with open(musica_path, 'a', encoding='utf-8') as file:
            for topico in topicos_manuais_musica:
                if topico not in topicos_musica_existentes:
                    file.write(f"\n{topico}")
                    topicos_musica_existentes.add(topico)
            print(f"Tópicos de música manuais importados: {topicos_manuais_musica}")

    except Exception as e:
        print(f"Erro ao importar tópicos manuais: {e}")

def processar_tags():
    """Processa tags e valida os arquivos antes do processamento."""
    ANKICONNECT_URL = "http://127.0.0.1:8765"
    ignored_topics = [
        "1.Espiritual", "2.Basicas", "3.Especificas", "4.Musica", "5.Valores",
        "6.Desenvolvimento_Pessoal", "7.Trabalho", "Euler", "leech", "marked",
        "Obsidian_to_Anki", "Estudar", "euler"
    ]
    default_hierarchy = "4.4.Intervalo_Referencia"

    try:
        # Comunicação com o Anki
        payload = {"action": "getTags", "version": 6}
        response = requests.post(ANKICONNECT_URL, json=payload)

        if response.status_code == 200:
            tags = response.json().get("result", [])
            if not tags:
                print("Nenhuma tag encontrada no Anki.")
                return

            filtered_tags = [tag for tag in tags if tag not in ignored_topics]
            if not filtered_tags:
                print("Nenhuma tag restante após filtragem.")
                return

            processed_tags = []
            processed_music_tags = []

            for tag in filtered_tags:
                if "::" in tag:
                    parts = tag.split("::")
                    for i in range(len(parts) - 1, -1, -1):
                        if re.match(r"^\d+\.", parts[i]):
                            processed_tag = "::".join(parts[i:])
                            if processed_tag.startswith("8."):
                                processed_tags.append(processed_tag)
                            elif not processed_tag.startswith("4."):
                                processed_tags.append(processed_tag)
                            if tag.startswith("4."):
                                processed_music_tags.append("::".join(parts[i:]))
                            break
                else:
                    if tag.startswith("8."):
                        processed_tags.append(tag)
                    elif not tag.startswith("4."):
                        processed_tags.append(f"{default_hierarchy}::{tag}")
                    if tag.startswith("4."):
                        processed_music_tags.append(f"{default_hierarchy}::{tag}")

            # Salvar tags processadas
            with open(estudo_path, "w", encoding="utf-8") as file:
                file.write("\n".join(sorted(set(processed_tags))))
                print("Tags de estudo salvas com sucesso.")

            with open(musica_path, "w", encoding="utf-8") as file:
                file.write("\n".join(sorted(set(processed_music_tags))))
                print("Tags de música salvas com sucesso.")

        else:
            print("Erro ao se comunicar com Anki. Verifique se o Anki está rodando e acessível.")

    except Exception as e:
        print(f"Erro durante o processamento de tags: {e}")

if __name__ == "__main__":
    try:
        processar_tags()
        importar_topicos_manuais(pesos_path, estudo_path, musica_path)
    except Exception as e:
        print("Erro fatal ao executar o script.")