import sys
import os
import logging
from flask import Flask, render_template, jsonify, request, send_from_directory
import json
from ControleDeEstudos import ControleDeEstudos
from datetime import datetime
import requests
from requests.exceptions import HTTPError, ConnectionError

# Configuração de logging
logging.basicConfig(level=logging.DEBUG)

# Adicionar o diretório atual ao sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
logging.debug(f"Current directory added to sys.path: {current_dir}")

# Imprimir o sys.path para depuração
logging.debug(f"sys.path: {sys.path}")

# Imprimir o conteúdo do diretório atual
logging.debug(f"Conteúdo do diretório atual: {os.listdir(current_dir)}")

# Verificar se o arquivo TagProcessor.py existe no diretório atual
tagprocessor_path = os.path.join(current_dir, 'TagProcessor.py')
if not os.path.exists(tagprocessor_path):
    logging.error("Arquivo TagProcessor.py não encontrado no diretório atual.")
    sys.exit(1)
else:
    logging.debug(f"Arquivo TagProcessor.py encontrado: {tagprocessor_path}")

# Importar diretamente o módulo TagProcessor
try:
    import TagProcessor
    logging.debug("Módulo TagProcessor importado com sucesso.")
    importar_topicos_manuais = TagProcessor.importar_topicos_manuais
except Exception as e:
    logging.error(f"Erro ao importar o módulo TagProcessor: {e}")
    sys.exit(1)

app = Flask(__name__)

# Caminhos e inicializações
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
PESOS_FILE = os.path.join(DATA_DIR, 'pesos.json')
os.makedirs(DATA_DIR, exist_ok=True)

# Dados padrão
DADOS_PADRAO = {
    "estudo": {},
    "musica": {}
}

# Inicializar controle de estudos
controle = ControleDeEstudos()

# Garantir que o arquivo pesos.json existe
if not os.path.exists(PESOS_FILE):
    with open(PESOS_FILE, 'w', encoding='utf-8') as f:
        json.dump(DADOS_PADRAO, f, indent=4)

# Importar tópicos manuais
importar_topicos_manuais(PESOS_FILE, os.path.join(DATA_DIR, 'topicos_estudo.txt'), os.path.join(DATA_DIR, 'topicos_musica.txt'))

# Função para processar tags
def processar_tags():
    try:
        response = requests.get('http://127.0.0.1:8765/')
        response.raise_for_status()
        print('Processamento de tags bem-sucedido')
    except HTTPError as http_err:
        logging.error(f'HTTP error occurred: {http_err}')  # HTTP error
    except ConnectionError as conn_err:
        logging.error(f'Connection error occurred: {conn_err}')  # Connection error
    except Exception as err:
        logging.error(f'Other error occurred: {err}')  # Other errors

# Chamada da função
processar_tags()

@app.route('/test_requests')
def test_requests():
    try:
        response = requests.get('https://api.github.com')
        return jsonify({"status_code": response.status_code, "content": response.json()})
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def index():
    """Página inicial."""
    modo_estudo = getattr(controle, "modo_estudo", "randomizado")
    return render_template('index.html', modo_estudo=modo_estudo)

@app.route('/buscar_topicos/<tipo>', methods=['GET'])
def buscar_topicos(tipo):
    """Busca tópicos dos arquivos especificados."""
    file_map = {
        'estudo': 'topicos_estudo.txt',
        'musica': 'topicos_musica.txt'
    }
    file_path = os.path.join(DATA_DIR, file_map.get(tipo, ''))

    if not os.path.exists(file_path):
        return jsonify({"erro": "Arquivo não encontrado."}), 404

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            topicos = [linha.strip() for linha in file.readlines() if linha.strip()]
        
        # Adicionar indicação de que o tópico é manual
        manual_topicos = []
        for topico in topicos:
            if topico in controle.pesos.get(tipo, {}) and controle.pesos[tipo][topico].get('adicionado') == 'manual':
                manual_topicos.append(f"{topico} (manual)")
            else:
                manual_topicos.append(topico)
        
        return jsonify({"topicos": manual_topicos}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    
@app.route('/carregar_pesos', methods=['GET'])
def carregar_pesos():
    """Carrega os dados de pesos para estudo e música."""
    app.logger.debug('Rota /carregar_pesos foi chamada')
    try:
        pesos = controle.carregar_pesos()

        # Ordenar os tópicos de estudo e música pelo peso em ordem decrescente
        estudo_ordenado = {k: v for k, v in sorted(pesos.get("estudo", {}).items(), key=lambda item: item[1]["peso"], reverse=True)}
        musica_ordenado = {k: v for k, v in sorted(pesos.get("musica", {}).items(), key=lambda item: item[1]["peso"], reverse=True)}

        return jsonify({
            "estudo": estudo_ordenado,
            "musica": musica_ordenado
        })
    except Exception as e:
        app.logger.error(f"Erro ao carregar pesos: {e}")
        return jsonify({
            "sucesso": False,
            "erro": f"Erro ao carregar pesos: {str(e)}"
        }), 500

@app.route('/salvar_pesos', methods=['POST'])
def salvar_pesos():
    """Salva os pesos no arquivo JSON e atualiza os arquivos de tópicos."""
    try:
        dados = request.json
        print(f"Dados recebidos para salvar: {json.dumps(dados, indent=4)}")

        if os.path.exists(PESOS_FILE):
            with open(PESOS_FILE, 'r', encoding='utf-8') as f:
                pesos = json.load(f)
            print(f"Pesos carregados do arquivo: {json.dumps(pesos, indent=4)}")
        else:
            pesos = {"estudo": {}, "musica": {}}
            print("Arquivo pesos.json não encontrado. Usando pesos padrão.")

        def atualizar_pesos(dados, categoria, file_path):
            # Carregar tópicos existentes no arquivo de texto
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as file:
                    topicos_existentes = set(line.strip() for line in file)
            else:
                topicos_existentes = set()

            # Atualizar pesos e adicionar tópicos manuais ao arquivo de texto
            for item in dados:
                topico = item["topico"]
                peso = item["peso"]
                origem = "manual"
                if topico in controle.carregar_arquivo(
                    controle.arquivo_topicos_estudo if categoria == "estudo" else controle.arquivo_topicos_musica
                ):
                    origem = "lista"
                pesos[categoria][topico] = {"peso": peso, "adicionado": origem}
                print(f"Atualizando peso: {categoria} -> {topico} = {peso}")

                # Adicionar tópicos manuais ao arquivo de texto, evitando duplicatas
                if origem == "manual" and topico not in topicos_existentes:
                    topicos_existentes.add(topico)
                    with open(file_path, 'a', encoding='utf-8') as file:
                        file.write(f"{topico}\n")
                        print(f"Tópico manual '{topico}' adicionado ao arquivo '{file_path}'")

        atualizar_pesos(dados.get("estudo", []), "estudo", os.path.join(DATA_DIR, 'topicos_estudo.txt'))
        atualizar_pesos(dados.get("musica", []), "musica", os.path.join(DATA_DIR, 'topicos_musica.txt'))

        print(f"Pesos atualizados: {json.dumps(pesos, indent=4)}")

        # Atualizar os pesos no objeto de controle e salvar
        controle.pesos = pesos
        print("Chamando função salvar_pesos no controle...")
        controle.salvar_pesos()
        print(f"Pesos salvos no arquivo: {json.dumps(pesos, indent=4)}")

        return jsonify({"mensagem": "Pesos atualizados com sucesso!"}), 200
    except Exception as e:
        print(f"Erro ao salvar pesos: {str(e)}")
        return jsonify({"erro": str(e)}), 500

@app.route('/pesos')
def pesos():
    """Renderiza a página de controle de pesos."""
    try:
        with open(PESOS_FILE, 'r', encoding='utf-8') as f:
            pesos = json.load(f)
        return render_template('pesos.html', pesos=pesos)
    except FileNotFoundError:
        return jsonify({"erro": "Arquivo pesos.json não encontrado."}), 404
    except json.JSONDecodeError as e:
        return jsonify({"erro": f"Erro ao carregar JSON: {e}"}), 500

@app.route('/adicionar_topico', methods=['POST'])
def adicionar_topico():
    """Adiciona um novo tópico à categoria especificada, ou atualiza o peso se já existir."""
    data = request.json
    categoria = data.get('categoria')
    nome = data.get('nome')
    peso = data.get('peso')

    print(f"Recebido: categoria={categoria}, nome={nome}, peso={peso}")

    if not categoria or not nome or peso is None:
        print("Erro: Todos os campos são obrigatórios.")
        return jsonify({"sucesso": False, "erro": "Todos os campos são obrigatórios."}), 400

    if categoria not in ['estudo', 'musica']:
        print("Erro: Categoria inválida.")
        return jsonify({"sucesso": False, "erro": "Categoria inválida."}), 400

    # Carregar os dados atuais do JSON
    try:
        with open('data/pesos.json', 'r', encoding='utf-8') as file:
            dados = json.load(file)
        print(f"Dados carregados do JSON: {json.dumps(dados, indent=4)}")
    except FileNotFoundError:
        dados = {"estudo": {}, "musica": {}}
        print("Arquivo pesos.json não encontrado, iniciando com dados padrões.")

    topicos = dados[categoria]

    # Verificar se o tópico já existe no arquivo de texto correspondente
    arquivo_topicos = 'data/topicos_estudo.txt' if categoria == 'estudo' else 'data/topicos_musica.txt'
    try:
        with open(arquivo_topicos, 'r', encoding='utf-8') as file:
            topicos_lista = {linha.strip() for linha in file}
        print(f"Tópicos carregados do arquivo {arquivo_topicos}: {topicos_lista}")
    except FileNotFoundError:
        topicos_lista = set()
        print(f"Arquivo {arquivo_topicos} não encontrado, iniciando com lista vazia.")

    origem = "lista" if nome in topicos_lista else "manual"
    print(f"Tópico {nome} adicionado como {origem}.")

    if nome in topicos:
        print(f"Tópico {nome} já existe com peso {topicos[nome].get('peso')}. Atualizando peso para {peso}.")
        topicos[nome]['peso'] = peso
    else:
        print(f"Tópico {nome} não existe. Adicionando com peso {peso}.")
        topicos[nome] = {"peso": peso, "adicionado": origem}

        # Se o tópico for manual, adicionar ao arquivo .txt com uma nova linha se necessário
        if origem == "manual":
            with open(arquivo_topicos, 'a+', encoding='utf-8') as file:
                file.seek(0)
                conteudo = file.read()
                if not conteudo.endswith('\n'):
                    file.write('\n')
                file.write(f"{nome}\n")
            print(f"Tópico manual '{nome}' adicionado ao arquivo '{arquivo_topicos}'.")

    # Atualizar os dados
    dados[categoria] = topicos
    print(f"Dados modificados: {json.dumps(dados, indent=4)}")

    # Salvar os dados atualizados no JSON
    try:
        with open('data/pesos.json', 'w', encoding='utf-8') as file:
            json.dump(dados, file, ensure_ascii=False, indent=4)
        print(f"Dados salvos no JSON: {json.dumps(dados, indent=4)}")
    except Exception as e:
        print(f"Erro ao salvar os dados: {str(e)}")
        return jsonify({"sucesso": False, "erro": f"Erro ao salvar os dados: {str(e)}"}), 500

    print("Tópico adicionado ou atualizado com sucesso.")
    return jsonify({"sucesso": True, "mensagem": "Tópico adicionado ou atualizado com sucesso."})
 
@app.route('/remover_topico', methods=['POST'])
def remover_topico():
    """Remove um tópico do pesos.json."""
    try:
        dados = request.json
        categoria = dados.get('categoria')
        topico = dados.get('topico')

        if not categoria or not topico:
            return jsonify({"erro": "Categoria ou tópico não informado!"}), 400

        with open(PESOS_FILE, 'r', encoding='utf-8') as f:
            pesos = json.load(f)

        if categoria in pesos and topico in pesos[categoria]:
            origem = pesos[categoria][topico].get('adicionado')
            del pesos[categoria][topico]

            with open(PESOS_FILE, 'w', encoding='utf-8') as f:
                json.dump(pesos, f, ensure_ascii=False, indent=4)

            # Remover o tópico do arquivo de texto correspondente se for manual
            if origem == "manual":
                arquivo_topicos = 'data/topicos_estudo.txt' if categoria == 'estudo' else 'data/topicos_musica.txt'
                if os.path.exists(arquivo_topicos):
                    with open(arquivo_topicos, 'r', encoding='utf-8') as file:
                        linhas = file.readlines()
                    with open(arquivo_topicos, 'w', encoding='utf-8') as file:
                        for linha in linhas:
                            if linha.strip() != topico:
                                file.write(linha)
                    print(f"Tópico manual '{topico}' removido do arquivo '{arquivo_topicos}'")

            return jsonify({"sucesso": True, "mensagem": f"Tópico '{topico}' removido com sucesso!"}), 200
        else:
            return jsonify({"erro": "Tópico não encontrado ou categoria inválida!"}), 404

    except Exception as e:
        return jsonify({"erro": f"Erro ao remover o tópico: {str(e)}"}), 500

@app.route('/concluir_topico', methods=['POST'])
def concluir_topico():
    """Conclui o tópico atual ou verifica se todos foram concluídos."""
    try:
        # Obter o tópico atual e valor do progresso
        topico_atual = controle.topico_atual
        progresso_topico = controle.log["progresso_topicos"].get(topico_atual, 0)
        peso_topico = controle.pesos["estudo"].get(topico_atual, {}).get("peso", 1)

        # Verificar se o progresso alcançou o peso definido
        if progresso_topico < peso_topico:
            controle.log["progresso_topicos"][topico_atual] += 1  # Incrementar o progresso
            controle.salvar_log()  # Salvar o log atualizado
            return jsonify({
                "mensagem": "O tópico atual ainda não atingiu o peso necessário.",
                "proximo_topico": topico_atual,
                "reiniciar": False
            }), 200

        controle.concluir_topico()
        proximo_topico = controle.topico_atual
        return jsonify({
            "mensagem": "Tópico concluído com sucesso.",
            "proximo_topico": proximo_topico
        }), 200
    except Exception as e:
        return jsonify({
            "erro": f"Erro ao concluir o tópico: {str(e)}"
        }), 500
    
@app.route('/avancar_topico', methods=['POST'])
def avancar_topico():
    controle.avancar_topico()
    if controle.topico_atual:
        mensagem = f"Novo tópico selecionado: {controle.topico_atual}"
        return jsonify({"mensagem": mensagem, "proximo_topico": controle.topico_atual}), 200
    else:
        return jsonify({"mensagem": "Erro ao avançar o tópico. Tente novamente.", "proximo_topico": None}), 400

@app.route('/concluir_topico_musica', methods=['POST'])
def concluir_topico_musica():
    try:
        controle.concluir_topico_musica()
        mensagem = "Tópico musical concluído com sucesso!"
        if controle.topico_musica_atual:
            mensagem += f" Novo tópico musical selecionado: {controle.topico_musica_atual}"
        return jsonify({"mensagem": mensagem, "proximo_topico": controle.topico_musica_atual}), 200
    except ValueError as e:
        return jsonify({"mensagem": str(e)}), 400

@app.route('/avancar_topico_musica', methods=['POST'])
def avancar_topico_musica():
    controle.avancar_topico_musica()
    if controle.topico_musica_atual:
        mensagem = f"Novo tópico musical selecionado: {controle.topico_musica_atual}"
        return jsonify({"mensagem": mensagem, "proximo_topico": controle.topico_musica_atual}), 200
    else:
        return jsonify({"mensagem": "Erro ao avançar o tópico musical. Tente novamente.", "proximo_topico": None}), 400


@app.route('/configuracoes', methods=['GET', 'POST'])
def configuracoes():
    """Exibe e atualiza configurações."""
    if request.method == 'POST':
        novo_modo = request.json.get('modo_estudo')
        if novo_modo in ['sequencial', 'randomizado']:
            controle.atualizar_modo_estudo(novo_modo)
            return jsonify({"mensagem": f"Modo de estudo atualizado para {novo_modo}."}), 200
        return jsonify({"erro": "Modo de estudo inválido."}), 400

    modo_estudo_atual = getattr(controle, 'modo_estudo', 'randomizado')
    return render_template('configuracoes.html', modo_estudo=modo_estudo_atual)

@app.route('/topico_atual', methods=['GET'])
def topico_atual():
    """Retorna o tópico atual sem avançar."""
    try:
        topico_atual = controle.topico_atual
        return jsonify({
            "topico_atual": topico_atual
        }), 200
    except Exception as e:
        return jsonify({
            "erro": f"Erro ao carregar o tópico atual: {str(e)}"
        }), 500

@app.route('/topico_musica_atual')
def topico_musica_atual():
    """Retorna o tópico de música atual."""
    try:
        # Carrega os tópicos do arquivo
        with open(os.path.join(DATA_DIR, 'topicos_musica.txt'), 'r', encoding='utf-8') as f:
            topicos = f.readlines()

        print(f"Tópicos carregados: {topicos}")

        # Tenta ler o índice do último tópico visto
        try:
            with open(os.path.join(DATA_DIR, 'topico_musica_atual.txt'), 'r', encoding='utf-8') as f:
                ultimo_topico = f.read().strip()

            print(f"Último tópico lido: {ultimo_topico}")

            if ultimo_topico.isdigit():
                ultimo_topico_index = int(ultimo_topico)
                if 0 <= ultimo_topico_index < len(topicos):
                    topico_atual = topicos[ultimo_topico_index]
                else:
                    topico_atual = topicos[0]
            else:
                topico_atual = topicos[0]
        except FileNotFoundError:
            topico_atual = topicos[0]

        print(f"Tópico atual: {topico_atual.strip()}")

        # Alteração aqui: chave do JSON deve ser 'topico_musica_atual'
        return jsonify({"topico_musica_atual": topico_atual.strip()})

    except Exception as e:
        print(f"Erro: {str(e)}")
        return jsonify({"erro": f"Erro ao carregar tópico de música: {str(e)}"}), 500
    
@app.route('/topicos_musica')
def topicos_musica():
    """Renderiza a página de música."""
    try:
        with open(os.path.join(DATA_DIR, 'topicos_musica.txt'), 'r', encoding='utf-8') as f:
            topicos = f.readlines()
        return render_template('musica.html', topicos=topicos)
    except FileNotFoundError:
        return jsonify({"erro": "Arquivo de tópicos de música não encontrado."}), 404

@app.route('/topicos_estudo')
def topicos_estudo():
    """Renderiza a página de tópicos de estudo."""
    try:
        with open(os.path.join(DATA_DIR, 'topicos_estudo.txt'), 'r', encoding='utf-8') as f:
            topicos = f.readlines()
        return render_template('topicos.html', topicos=topicos)
    except FileNotFoundError:
        return jsonify({"erro": "Arquivo de tópicos de estudo não encontrado."}), 404
    except Exception as e:
        return jsonify({"erro": f"Erro ao carregar tópicos de estudo: {str(e)}"}), 500

@app.route('/projeto_web/static/js/<path:filename>')
def static_files(filename):
    """Serve arquivos estáticos."""
    return send_from_directory('projeto_web/static/js', filename)

@app.route('/verificar_progresso/<topico>', methods=['GET'])
def verificar_progresso(topico):
    limite = controle.pesos["estudo"].get(topico, {}).get("peso", 1)
    progresso_atual = controle.log["progresso_topicos"].get(topico, 0)
    return jsonify({'limite': limite, 'progresso_atual': progresso_atual})

if __name__ == '__main__':
    app.run(debug=True)


