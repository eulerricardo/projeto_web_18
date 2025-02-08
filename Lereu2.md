####Métodos###
- concluir_topico = sgera as informações para o  arquivo progresso.json
    - chama o salvar_log
- salvar_log = salva a informação no progresso.json





#####DESABILITAR BOTAO######
    musica.html // <button class="button" onclick="concluirTopicoMusica()">Concluir Tópico</button>
    script.js //   function concluirTopicoMusica() 
                                fetch("/concluir_topico_musica", { method: "POST" })
    app.py  //  @app.route('/concluir_topico_musica', methods=['POST'])
    ControleDeEstudos.py //   def concluir_topico_musica(self):
                                            Atualiza progresso.json
                                                        self.topico_musica_atual = None (se completar tudo)
        script.js //  function concluirTopicoMusica()
                                data.proximo_topico = null (desabilita o botão)






###Validar peso de um tópico###
    Modificar a função concluir_topico para incrementar o progresso do tópico e verificar se ele atingiu o limite de conclusões definidos no pesos.json.
            Alterar a função que controla a habilitação/desabilitação do botão "Concluir Tópicos" na interface gráfica.
            Adicionar uma verificação do progresso atual do tópico em relação ao limite definido em pesos.json.
    Modificar a função avancar_topico para respeitar o limite de conclusões do tópico.
    Modificar a função carregar_log para garantir que o progresso dos tópicos seja inicializado corretamente.




- [x] Trocar a estrutura do progresso.json tem que ser números e não true
-