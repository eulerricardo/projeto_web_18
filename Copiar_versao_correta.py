import os
import shutil

def get_next_version(target_dir, base_name):
    """
    Obtém o próximo número de versão com base nos diretórios existentes.

    :param target_dir: O diretório onde procurar pelas versões existentes.
    :param base_name: O nome base do diretório, ex: "Versao 20".
    :return: O próximo número de versão no formato "Versao 20.X - Web".
    """
    # Lista todos os subdiretórios no diretório de destino
    subdirs = [d for d in os.listdir(target_dir) if os.path.isdir(os.path.join(target_dir, d))]

    # Filtra os diretórios que começam com o nome base
    versions = [d for d in subdirs if d.startswith(base_name)]

    # Extrai os números das versões
    version_numbers = []
    for version in versions:
        try:
            # Obtém o número decimal da versão (depois do nome base)
            number_part = version.replace(base_name, "").split(" - ")[0].strip()
            version_numbers.append(float(number_part))
        except ValueError:
            continue

    # Calcula o próximo número de versão
    if version_numbers:
        next_number = max(version_numbers) + 0.1  # Incrementa 0.1
    else:
        next_number = 0.0

    # Formata o número para manter uma casa decimal
    next_version_str = f"{next_number:.1f}"
    return f"{base_name} {next_version_str} - Web"

def copy_directory_with_version(source_dir, target_dir, base_name):
    """
    Copia o diretório de origem para o diretório de destino com um número de versão incrementado.

    :param source_dir: O caminho do diretório de origem.
    :param target_dir: O caminho do diretório de destino.
    :param base_name: O nome base do diretório, ex: "Versao 20".
    """
    # Obtém o próximo nome de versão
    next_version = get_next_version(target_dir, base_name)

    # Caminho completo para o novo diretório
    new_dir_path = os.path.join(target_dir, next_version)

    # Realiza a cópia
    shutil.copytree(source_dir, new_dir_path)

    print(f"Diretório copiado com sucesso para: {new_dir_path}")

# Caminhos e base do nome da versão
source_directory = r"G:\Meu Drive\PYTHON\Programa\Controle_Estudo\bkp\Versao 18 - Web"
target_directory = r"G:\Meu Drive\PYTHON\Programa\Controle_Estudo\Bkps Web"
base_version_name = "Versao 20"

# Executa a cópia com versionamento
copy_directory_with_version(source_directory, target_directory, base_version_name)
