import random
import json
from datetime import datetime
import os
from pathlib import Path
import TagProcessor
import requests
from requests.exceptions import HTTPError, ConnectionError
import logging

# Configuração de logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Processa as tags antes de iniciar o programa
TagProcessor.processar_tags()

# Diretório base para localizar os arquivos
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# Caminhos dos arquivos
ARQUIVO_TOPICOS_ESTUDO = os.path.join(DATA_DIR, "topicos_estudo.txt")
ARQUIVO_TOPICOS_MUSICA = os.path.join(DATA_DIR, "topicos_musica.txt")
ARQUIVO_PESOS = os.path.join(DATA_DIR, "pesos.json")
ARQUIVO_LOG = os.path.join(DATA_DIR, "progresso.json")

class ControleDeEstudos:
    def __init__(self, interface=None):
        self.interface = interface

        # Caminhos definidos explicitamente
        self.arquivo_topicos_estudo = ARQUIVO_TOPICOS_ESTUDO
        self.arquivo_topicos_musica = ARQUIVO_TOPICOS_MUSICA
        self.arquivo_pesos = ARQUIVO_PESOS
        self.arquivo_log = ARQUIVO_LOG

        # Carregar dados
        self.topicos = self.carregar_arquivo(self.arquivo_topicos_estudo)
        self.topicos_musicais = self.carregar_arquivo(self.arquivo_topicos_musica)
        self.pesos = self.carregar_pesos()
        self.log = self.carregar_log()

        # Estado atual
        self.topico_atual = self.log.get("estado_atual", {}).get("topico_atual", None)
        self.topico_musica_atual = self.log.get("estado_atual", {}).get("topico_musica_atual", None)
        self.progresso_atual = self.log.get("estado_atual", {}).get("progressao_atual", None)
        self.modo_estudo = self.log.get("estado_atual", {}).get("modo_estudo", "sequencial")

        # Garantir que as chaves necessárias estejam no log
        if "progresso_topicos" not in self.log:
            self.log["progresso_topicos"] = {topico: 0 for topico in self.topicos}
        if "progresso_topicos_musica" not in self.log:
            self.log["progresso_topicos_musica"] = {topico: 0 for topico in self.topicos_musicais}

        # Verificar estado inicial e avançar o tópico se necessário
        if not self.topicos:
            print("Aviso: Nenhum tópico encontrado para avançar. Verifique o arquivo 'topicos_estudo.txt'.")
        elif not self.topico_atual:
            self.avancar_topico()

        if not self.topicos_musicais:
            print("Aviso: Nenhum tópico musical encontrado. Verifique o arquivo 'topicos_musica.txt'.")
        elif not self.topico_musica_atual:
            self.avancar_topico_musica()

        # Salvar o log atualizado
        self.salvar_log()

    def carregar_arquivo(self, caminho):
        """Carrega tópicos de um arquivo como lista."""
        try:
            with open(caminho, 'r', encoding='utf-8') as arquivo:
                return [linha.strip() for linha in arquivo if linha.strip()]
        except FileNotFoundError:
            print(f"Erro: Arquivo '{caminho}' não encontrado.")
            return []

    def carregar_pesos(self):
        """Carrega os pesos de tópicos de estudo e música a partir do arquivo JSON ou usa valores padrão."""
        try:
            with open(self.arquivo_pesos, "r", encoding="utf-8") as file:
                pesos = json.load(file)
                return pesos
        except (FileNotFoundError, json.JSONDecodeError):
            print("Arquivo de pesos não encontrado ou inválido. Usando valores padrão.")
            return {"estudo": {}, "musica": {}}

    def sincronizar_topicos(self, dados_pesos):
        """Sincroniza os tópicos dos dados_pesos com os arquivos .txt correspondentes."""
        try:
            def atualizar_arquivo(arquivo, novos_topicos):
                if os.path.exists(arquivo):
                    with open(arquivo, 'r', encoding='utf-8') as f:
                        topicos_existentes = {linha.strip() for linha in f.readlines()}
                else:
                    topicos_existentes = set()

                topicos_para_adicionar = set(novos_topicos.keys()) - topicos_existentes

                if topicos_para_adicionar:
                    with open(arquivo, 'a', encoding='utf-8') as f:
                        for topico in topicos_para_adicionar:
                            f.write(f"{topico}\n")

            atualizar_arquivo(self.arquivo_topicos_estudo, dados_pesos.get('estudo', {}))
            atualizar_arquivo(self.arquivo_topicos_musica, dados_pesos.get('musica', {}))
            print("Sincronização concluída.")
        except Exception as e:
            print(f"Erro ao sincronizar tópicos: {e}")


    def obter_topico_musica_atual(self):
        """Retorna o primeiro tópico musical pendente ou o último registrado."""
        if not self.topicos_musicais:
            return None
        return next((t for t, status in self.log["progresso_topicos_musica"].items() if not status), None) or self.topicos_musicais[-1]

    def atualizar_modo_estudo(self, novo_modo):
        if novo_modo not in ["sequencial", "randomizado"]:
            print(f"Modo de estudo inválido: {novo_modo}")
            return

        self.log["estado_atual"]["modo_estudo"] = novo_modo
        self.modo_estudo = novo_modo
        self.salvar_log()
        print(f"Modo de estudo atualizado para: {novo_modo}")

    def salvar_pesos(self):
        """Salva os pesos no arquivo JSON."""
        try:
            print("Iniciando o salvamento dos pesos...")
            with open(self.arquivo_pesos, "w", encoding="utf-8") as file:
                json.dump(self.pesos, file, indent=4, ensure_ascii=False)
            print(f"Pesos salvos com sucesso em: {self.arquivo_pesos}")
        except Exception as e:
            print(f"Erro ao salvar os pesos {self.arquivo_pesos}: {e}")

    @staticmethod
    def processar_tags():
        try:
            response = requests.get('http://127.0.0.1:8765/')
            response.raise_for_status()
            print('Processamento de tags bem-sucedido')
            return response.json()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')  # HTTP error
        except ConnectionError as conn_err:
            print(f'Connection error occurred: {conn_err}')  # Connection error
        except Exception as err:
            print(f'Other error occurred: {err}')  # Other errors
        return None


     # Função Alterada: concluir_topico

    def progresso_completo(self, topico):
            """Verifica se o progresso do tópico atingiu o valor necessário."""
            peso_necessario = self.pesos.get('estudo', {}).get(topico, {}).get('peso', 0)
            progresso_atual = self.log["progresso_topicos"].get(topico, 0)
            return progresso_atual >= peso_necessario


    def concluir_topico_musica(self):
        """Marca o tópico musical atual como concluído e avança para o próximo."""
        if not self.topico_musica_atual:
            print("Erro: Nenhum tópico musical atual para concluir.")
            return

        self.log["progresso_topicos_musica"][self.topico_musica_atual] = 0
        self.salvar_log()

        if all(value == 0 for value in self.log["progresso_topicos_musica"].values()):
            print("Todos os tópicos musicais foram concluídos! Reiniciando progresso...")
            for key in self.log["progresso_topicos_musica"].keys():
                self.log["progresso_topicos_musica"][key] = 0
            self.topico_musica_atual = None
        else:
            self.avancar_topico_musica()

    def avancar_topico_musica(self):
        """Avança para o próximo tópico musical disponível ou informa se todos foram concluídos."""
        logging.debug("Iniciando avancar_topico_musica()")

        topicos_pendentes = [t for t in self.topicos_musicais if self.log["progresso_topicos_musica"].get(t, 0) < self.pesos["musica"].get(t, {}).get("peso", 1)]
        logging.debug(f"Tópicos musicais pendentes: {topicos_pendentes}")

        if not topicos_pendentes:
            logging.warning("Nenhum tópico musical disponível para seleção. Todos os tópicos musicais foram concluídos.")
            self.topico_musica_atual = None
            self.salvar_log()  # Salvar o estado quando todos os tópicos musicais estão concluídos
            return

        if self.modo_estudo == "randomizado":
            self.topico_musica_atual = random.choice(topicos_pendentes)
        else:
            self.topico_musica_atual = topicos_pendentes[0]

        logging.info(f"Novo tópico musical selecionado: {self.topico_musica_atual}")
        self.salvar_log()  # Salvar o estado após selecionar um novo tópico musical

    def concluir_topico(self):
        """Marca o tópico atual como concluído e avança para o próximo tópico."""
        if not self.topico_atual:
            logging.error("Erro: Nenhum tópico atual para concluir.")
            return {"todos_concluidos": False, "progresso_atual": 0, "limite": 0}

        logging.debug(f"Concluindo tópico: {self.topico_atual}")

        # Incrementar o progresso do tópico atual
        if self.topico_atual in self.log["progresso_topicos"]:
            self.log["progresso_topicos"][self.topico_atual] += 1
        else:
            self.log["progresso_topicos"][self.topico_atual] = 1

        progresso_atual = self.log["progresso_topicos"][self.topico_atual]
        limite = self.pesos["estudo"].get(self.topico_atual, {}).get("peso", 1)

        # Verificar se o progresso atingiu o limite
        if progresso_atual >= limite:
            self.log["progresso_topicos"][self.topico_atual] = 0
            logging.info(f"Tópico {self.topico_atual} concluído definitivamente.")

        logging.info("Chamando avancar_topico()")
        self.avancar_topico()  # Chamar avancar_topico para selecionar o próximo tópico

        # Salvar o log
        self.salvar_log()

        # Adicionar logs para depuração
        todos_concluidos = all(value == 0 for value in self.log["progresso_topicos"].values())
        logging.debug(f"Todos concluídos: {todos_concluidos}")

        return {"todos_concluidos": todos_concluidos, "progresso_atual": progresso_atual, "limite": limite}


    def avancar_topico(self):
        """Avança para o próximo tópico disponível ou informa se todos foram concluídos."""
        logging.debug("Iniciando avancar_topico()")

        topicos_pendentes = [t for t in self.topicos if self.log["progresso_topicos"].get(t, 0) < self.pesos["estudo"].get(t, {}).get("peso", 1)]
        logging.debug(f"Tópicos pendentes: {topicos_pendentes}")

        if not topicos_pendentes:
            logging.warning("Nenhum tópico disponível para seleção. Todos os tópicos foram concluídos.")
            self.topico_atual = None
            self.salvar_log()  # Salvar o estado quando todos os tópicos estão concluídos
            return

        if self.modo_estudo == "randomizado":
            self.topico_atual = random.choice(topicos_pendentes)
        else:
            self.topico_atual = topicos_pendentes[0]

        logging.info(f"Novo tópico selecionado: {self.topico_atual}")
        self.salvar_log()  # Salvar o estado após selecionar um novo tópico


    def salvar_log(self):
        """Salva o log de progresso no arquivo JSON."""
        logging.debug(f"Conteúdo do log a ser salvo em salvar_log: {json.dumps(self.log, indent=4, ensure_ascii=False)}")
        with open(self.arquivo_log, "w", encoding="utf-8") as arquivo:
            json.dump(self.log, arquivo, ensure_ascii=False, indent=4)
        logging.info(f"Log salvo com sucesso em: {self.arquivo_log}")

    def carregar_log(self):
        """Carrega o log de progresso do arquivo JSON ou cria um log padrão."""
        log_padrao = {
            "estado_atual": {
                "modo_estudo": "randomizado",
            },
            "historico": [],
            "progresso_topicos": {
                topico: 0 for topico in self.topicos
            },
            "progresso_topicos_musica": {
                topico: 0 for topico in self.topicos_musicais
            },
        }

        if not os.path.exists(self.arquivo_log):
            with open(self.arquivo_log, "w", encoding="utf-8") as arquivo:
                json.dump(log_padrao, arquivo, ensure_ascii=False, indent=4)
            return log_padrao

        try:
            with open(self.arquivo_log, "r", encoding="utf-8") as arquivo:
                log = json.load(arquivo)

            if "progresso_topicos" not in log:
                log["progresso_topicos"] = {topico: 0 for topico in self.topicos}
            if "progresso_topicos_musica" not in log:
                log["progresso_topicos_musica"] = {topico: 0 for topico in self.topicos_musicais}
            if "estado_atual" not in log:
                log["estado_atual"] = {"modo_estudo": "randomizado"}

            return log

        except Exception as e:
            logging.error(f"Erro ao carregar o log: {e}")
            return log_padrao


if __name__ == "__main__":
    print("Iniciando Controle de Estudos...")
    controle = ControleDeEstudos()
    print("Pesos carregados:")
    print(json.dumps(controle.pesos, indent=4, ensure_ascii=False))
    
    # Teste a função concluir_topico diretamente
    controle.topico_atual = "Abacate"  # Defina um tópico atual para testar
    controle.concluir_topico()

