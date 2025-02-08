console.log('Carregando script.js do endereço:', window.location.href);

// Função genérica para enviar requisições e lidar com respostas
function enviarRequisicao(endpoint, callback) {
    console.log(`Enviando requisição para ${endpoint}`);
    fetch(endpoint, { method: "POST" })
        .then(response => {
            console.log(`Resposta do servidor para ${endpoint}:`, response);
            if (!response.ok) {
                throw new Error(`Erro na requisição: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            console.log(`Dados recebidos para ${endpoint}:`, data);
            callback(data);
        })
        .catch(error => {
            console.error(`Erro ao comunicar com o servidor em ${endpoint}:`, error);
            exibirMensagem(`Erro: ${error.message}`, "error");
        });
}

// Função para salvar novo tópico
function salvarNovoTopico() {
    const categoria = document.getElementById('categoria-topico').value;
    const nomeTopico = document.getElementById('novo-topico').value.trim();
    const peso = parseInt(document.getElementById('peso-topico').value, 10);

    if (!nomeTopico || isNaN(peso)) {
        exibirMensagem('Por favor, preencha todos os campos corretamente.', 'error');
        return;
    }

    fetch('/adicionar_topico', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            categoria: categoria,
            nome: nomeTopico,
            peso: peso
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data.sucesso) {
                const tabelaId = categoria === 'estudo' ? 'tabela-estudo' : 'tabela-musica';
                const tabela = document.getElementById(tabelaId).querySelector('tbody');
                const novaLinha = tabela.insertRow();

                novaLinha.innerHTML = `
                    <td>${nomeTopico}</td>
                    <td>${peso}</td>
                    <td><button class="button delete-button" onclick="removerLinha(this)">Excluir</button></td>
                `;

                exibirMensagem(data.mensagem, 'success');
                limparCamposModal(); // Limpar os campos ao adicionar um novo tópico com sucesso
                fecharModal(); // Fechar a modal após adicionar um novo tópico com sucesso
            } else if (data.erro === "Este tópico já está adicionado.") {
                exibirMensagem('Este tópico já está adicionado.', 'error');
            } else {
                exibirMensagem('Erro ao adicionar o tópico. Tente novamente.', 'error');
            }
        })
        .catch(error => {
            console.error('Erro ao adicionar tópico:', error);
            exibirMensagem('Erro ao adicionar o tópico. Tente novamente.', 'error');
        });
}


// Função para avançar tópico de música
function avancarTopicoMusica() {
    console.log('Função avancarTopicoMusica foi chamada');
    fetch("/avancar_topico_musica", { method: "POST" })
        .then(response => response.json())
        .then(data => {
            if (data.proximo_topico) {
                document.getElementById("topico-atual").innerHTML = `<span class="negrito">Próximo Tópico:</span> <span class="negrito verde">${data.proximo_topico}</span>`;
                const botaoConcluir = document.querySelector("button[onclick='concluirTopicoMusica()']");
                botaoConcluir.disabled = false;
                botaoConcluir.style.backgroundColor = 'green';
                botaoConcluir.style.cursor = 'pointer';
                exibirMensagem(data.mensagem, 'success');
            } else {
                exibirMensagem('Erro ao avançar o tópico musical. Tente novamente.', 'error');
            }
        })
        .catch(error => {
            console.error("Erro ao avançar o tópico musical:", error);
            exibirMensagem('Erro ao avançar o tópico musical. Tente novamente.', 'error');
        });
}

function exibirMensagem(mensagem, tipo) {
    const container = document.getElementById('mensagem-container') || criarContainerMensagem();
    const msgDiv = document.createElement('div');

    msgDiv.className = `mensagem ${tipo}`; // Define a classe baseada no tipo
    msgDiv.innerText = mensagem;

    container.appendChild(msgDiv);

    // Remove a mensagem após 2 segundos
    setTimeout(() => {
        container.removeChild(msgDiv);
    }, 2000);
}

function criarContainerMensagem() {
    const container = document.createElement('div');
    container.id = 'mensagem-container';
    container.style.position = 'fixed';
    container.style.top = '10px';
    container.style.right = '10px';
    container.style.zIndex = '1000';
    document.body.appendChild(container);
    return container;
}



// Função para avançar tópico de estudo
function avancarTopico() {
    console.log('Função avancarTopico foi chamada');
    fetch("/avancar_topico", { method: "POST" })
        .then(response => response.json())
        .then(data => {
            if (data.proximo_topico) {
                document.getElementById("topico-atual").innerHTML = `<span class="negrito">Próximo Tópico:</span> <span class="negrito verde">${data.proximo_topico}</span>`;
                const botaoConcluir = document.querySelector("button[onclick='concluirTopico()']");
                botaoConcluir.disabled = false;
                botaoConcluir.style.backgroundColor = 'green';
                botaoConcluir.style.cursor = 'pointer';
                exibirMensagem(data.mensagem, 'success');
            } else {
                exibirMensagem('Erro ao avançar o tópico. Tente novamente.', 'error');
            }
        })
        .catch(error => {
            console.error("Erro ao avançar o tópico:", error);
            exibirMensagem('Erro ao avançar o tópico. Tente novamente.', 'error');
        });
}

// Função para limpar os campos do modal
function limparCamposModal() {
    document.getElementById('novo-topico').value = '';
    document.getElementById('peso-topico').value = '';
}

// Função para abrir a modal e carregar os tópicos existentes
function abrirModal(categoria) {
    document.getElementById('modal-novo-topico').style.display = 'block';
    document.getElementById('modal-overlay').style.display = 'block';
    document.getElementById('categoria-topico').value = categoria;

    // Fetch tópicos disponíveis do backend
    fetch(`/buscar_topicos/${categoria}`)
        .then(response => response.json())
        .then(data => {
            const lista = document.getElementById('lista-topicos');
            lista.innerHTML = '';
            data.topicos.forEach(topico => {
                // Filtrar tópicos manuais
                if (!topico.includes(" (manual)")) {
                    const li = document.createElement('li');
                    li.textContent = topico;
                    li.onclick = () => {
                        document.getElementById('novo-topico').value = topico;
                    };
                    lista.appendChild(li);
                }
            });
        })
        .catch(error => console.error('Erro ao buscar tópicos:', error));
}

// Função para fechar a modal e limpar os campos
function fecharModal() {
    document.getElementById('modal-novo-topico').style.display = 'none';
    document.getElementById('modal-overlay').style.display = 'none';
    limparCamposModal(); // Limpar os campos ao fechar a modal
}

// Função para remover linha da tabela
function removerLinha(botao) {
    console.log('Função removerLinha foi chamada!');
    const linha = botao.parentElement.parentElement; // Captura a linha clicada
    const categoria = botao.closest('table').id.includes('estudo') ? 'estudo' : 'musica'; // Define a categoria com base no ID da tabela
    const topico = linha.cells[0].innerText.trim(); // Obtém o nome do tópico da primeira célula

    console.log(`Removendo: Categoria=${categoria}, Tópico=${topico}`); // Log para depuração

    // Envia requisição ao backend para remover o tópico
    fetch('/remover_topico', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ categoria, topico }),
    })
        .then(response => response.json())
        .then(data => {
            if (data.sucesso) {
                linha.remove(); // Remove a linha da tabela no frontend
                exibirMensagem(data.mensagem, 'success'); // Mensagem de sucesso
                console.log(data.mensagem); // Exibe mensagem de sucesso no console
            } else {
                console.error(data.erro); // Exibe mensagem de erro no console
                exibirMensagem(data.erro || 'Erro ao excluir o tópico.', 'error'); // Mensagem de erro
            }
        })
        .catch(error => {
            console.error('Erro ao excluir o tópico:', error);
            exibirMensagem('Erro ao excluir o tópico. Tente novamente.', 'error'); // Mensagem de erro
        });
}

document.addEventListener("DOMContentLoaded", () => {
    console.log("DOM completamente carregado e analisado.");

    fetch("/carregar_pesos")
        .then(response => {
            if (!response.ok) {
                throw new Error("Erro ao carregar os pesos. Código de status: " + response.status);
            }
            return response.json();
        })
        .then(dados => {
            console.log("Dados recebidos do servidor:", dados);

            const dadosEstudo = Object.entries(dados.estudo).map(([idx, item]) => ({ topico: idx, peso: item.peso }));
            const dadosMusica = Object.entries(dados.musica).map(([idx, item]) => ({ topico: idx, peso: item.peso }));

            console.log("Dados transformados para estudo:", dadosEstudo);
            console.log("Dados transformados para música:", dadosMusica);

            preencherTabela("tabela-estudo", dadosEstudo);
            preencherTabela("tabela-musica", dadosMusica);
        })
        .catch(error => {
            console.error("Erro no carregamento dos dados:", error);
        });

    const botaoConcluirTopico = document.getElementById('botaoConcluirTopico');
    const topicoAtualElemento = document.getElementById('topicoAtual');
    const topicoAtual = topicoAtualElemento ? topicoAtualElemento.textContent : null;

    function atualizarBotaoConcluir() {
        if (topicoAtual) {
            fetch(`/verificar_progresso/${topicoAtual}`)
                .then(response => response.json())
                .then(data => {
                    const { limite, progresso_atual } = data;
                    if (progresso_atual < limite) {
                        botaoConcluirTopico.disabled = false;
                    } else {
                        botaoConcluirTopico.disabled = true;
                    }
                })
                .catch(error => {
                    console.error("Erro ao verificar o progresso do tópico:", error);
                });
        }
    }

    if (botaoConcluirTopico) {
        botaoConcluirTopico.addEventListener('click', function() {
            // Lógica para concluir o tópico
            fetch("/concluir_topico", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ topico: topicoAtual })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === "success") {
                    atualizarBotaoConcluir();
                }
            })
            .catch(error => {
                console.error("Erro ao concluir o tópico:", error);
            });
        });
    }

    // Carregar o tópico atual sem avançar ao carregar a página
    if (window.location.pathname === '/topicos_estudo') {
        fetch("/topico_atual")
            .then(response => response.json())
            .then(data => {
                if (data.topico_atual) {
                    document.getElementById("topico-atual").innerHTML = `<span class="negrito">Próximo Tópico:</span> <span class="negrito verde">${data.topico_atual}</span>`;
                    atualizarBotaoConcluir();
                } else {
                    document.getElementById("topico-atual").innerHTML = `<span class="negrito">Próximo Tópico:</span> <span class="negrito verde">Nenhum tópico carregado.</span>`;
                }
            })
            .catch(error => {
                console.error("Erro ao carregar o tópico atual:", error);
            });
    } else if (window.location.pathname === '/topicos_musica') {
        fetch("/topico_musica_atual")
            .then(response => response.json())
            .then(data => {
                if (data.topico_musica_atual) {
                    document.getElementById("topico-atual").innerHTML = `<span class="negrito">Próximo Tópico:</span> <span class="negrito verde">${data.topico_musica_atual}</span>`;
                    atualizarBotaoConcluir();
                } else {
                    document.getElementById("topico-atual").innerHTML = `<span class="negrito">Próximo Tópico:</span> <span class="negrito verde">Nenhum tópico carregado.</span>`;
                }
            })
            .catch(error => {
                console.error("Erro ao carregar o tópico musical atual:", error);
            });
    }
});

// Função para redirecionar para a página de tópicos de estudo
function irParaTopicos() {
    window.location.href = "/topicos_estudo";
}

// Função para redirecionar para a página de tópicos de música
function irParaMusica() {
    window.location.href = "/topicos_musica";
}

// Função para redirecionar para a página de controle de pesos
function controlePesos() {
    window.location.href = "/pesos";
}

// Função para preencher tabela com ordenação decrescente
let tabelaEstudoPreenchida = false;
let tabelaMusicaPreenchida = false;

function preencherTabela(tabelaId, dados) {
    if ((tabelaId === 'tabela-estudo' && tabelaEstudoPreenchida) || 
        (tabelaId === 'tabela-musica' && tabelaMusicaPreenchida)) {
        console.log(`Tabela ${tabelaId} já foi preenchida. Ignorando.`);
        return;
    }

    if (tabelaId === 'tabela-estudo') tabelaEstudoPreenchida = true;
    if (tabelaId === 'tabela-musica') tabelaMusicaPreenchida = true;

    console.log(`Preenchendo tabela ${tabelaId} com os dados:`, dados);

    // Ordenar os dados por peso em ordem decrescente
    dados.sort((a, b) => b.peso - a.peso);

    const tabela = document.getElementById(tabelaId);
    const tbody = tabela.querySelector('tbody');
    tbody.innerHTML = '';

    dados.forEach(item => {
        console.log(`Adicionando linha para tópico: ${item.topico}, peso: ${item.peso}`);
        const linha = document.createElement('tr');
        linha.innerHTML = `
            <td>${item.topico}</td>
            <td>${item.peso}</td>
            <td><button class="button delete-button" onclick="removerLinha(this)">Excluir</button></td>
        `;
        tbody.appendChild(linha);
    });
}

// Função para concluir tópico de estudo
function concluirTopico() {
    console.log('Função concluirTopico foi chamada');
    fetch("/concluir_topico", { method: "POST" })
        .then(response => response.json())
        .then(data => {
            if (data.proximo_topico !== null) {
                document.getElementById("topico-atual").innerHTML = `<span class="negrito">Próximo Tópico:</span> <span class="negrito verde">${data.proximo_topico}</span>`;
            }
            if (data.todos_concluidos) {
                const botaoConcluir = document.querySelector("button[onclick='concluirTopico()']");
                botaoConcluir.disabled = true;
                botaoConcluir.style.backgroundColor = '#d3d3d3';
                botaoConcluir.style.cursor = 'not-allowed';
            }
            exibirMensagem(data.mensagem, 'success');
        })
        .catch(error => {
            console.error("Erro ao concluir o tópico:", error);
            exibirMensagem('Erro ao concluir o tópico. Tente novamente.', 'error');
        });
}

// Função para concluir tópico de música
function concluirTopicoMusica() {
    console.log('Função concluirTopicoMusica foi chamada');
    fetch("/concluir_topico_musica", { method: "POST" })
        .then(response => response.json())
        .then(data => {
            if (data.proximo_topico !== null) {
                document.getElementById("topico-atual").innerHTML = `<span class="negrito">Próximo Tópico:</span> <span class="negrito verde">${data.proximo_topico}</span>`;
            }
            if (data.todos_concluidos) {
                const botaoConcluir = document.querySelector("button[onclick='concluirTopicoMusica()']");
                botaoConcluir.disabled = true;
                botaoConcluir.style.backgroundColor = '#d3d3d3';
                botaoConcluir.style.cursor = 'not-allowed';
            }
            exibirMensagem(data.mensagem, 'success');
        })
        .catch(error => {
            console.error("Erro ao concluir o tópico musical:", error);
            exibirMensagem('Erro ao concluir o tópico musical. Tente novamente.', 'error');
        });
}






