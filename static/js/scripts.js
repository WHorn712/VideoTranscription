// Declaração global para armazenar e-mails registrados
registeredEmails = [];

// Função genérica para selecionar um único elemento
function getElement(selector) {
    return document.querySelector(selector);
}

// Função genérica para selecionar múltiplos elementos
function getElements(selector) {
    return document.querySelectorAll(selector);
}

// Seleciona elementos de modal de forma genérica
var modal = getElement("#myModal");
var modalLogin = getElement("#myModalLogin");
var modalContato = getElement("#myModalContato");
var modalPrice = getElement("#myModalPrice");
var modalRecupere = getElement("#modalRecupere");

// Seleciona botões de forma genérica
var btnCadastrar = getElement("#cadastrarBtn");
var btnLogin = getElement("#loginBtn");
var btnEntrar = modalLogin ? modalLogin.querySelector('button[type="submit"]') : null;
var btnContato = getElement('.nav-links li:nth-child(3) a');
var btnTranscrever = getElement("#transcreverBtn");
var btnTranscrever_index = getElement("#transcreverBtnIndex");
var btnIndexar_index = getElement("#indexarBtnIndex");
var spanCloses = getElements('.close');
var form = modal ? modal.querySelector("form") : null;
var submitButton = form ? form.querySelector('button[type="submit"]') : null;
var btnComoUsar = getElement('#comoUsarLink');
var fileInput = getElement("#fileInput");
var indexarBtn = getElement("#indexarBtn");
var canvas = getElement("#canvas");
var context = canvas ? canvas.getContext("2d") : null;
var video = document.createElement("video");
var btnContatoRodape = getElement('.footer-links a:nth-child(3)');
var emailExistenteBD = false;



// Seleciona o botão de registrar do modal de recuperação
var btnRegistrarRecupere = modalRecupere ? modalRecupere.querySelector('button[type="submit"]') : null;

// Define o estado inicial dos botões
if (btnRegistrarRecupere) {
    btnRegistrarRecupere.style.backgroundColor = "#d3d3d3"; // Cinza por padrão
    btnRegistrarRecupere.style.color = "#000000";
}

// Eventos
if (btnContatoRodape) {
    btnContatoRodape.addEventListener('click', function(event) {
        event.preventDefault();
        abrirModalContato();
    });
}

if (fileInput) {
    fileInput.addEventListener("change", function(event) {
        if (event.target.files.length > 0) {
            var file = event.target.files[0];
            var fileURL = URL.createObjectURL(file);
            video.src = fileURL;

            video.addEventListener("loadeddata", function() {
                video.currentTime = 1;
            }, { once: true });

            video.addEventListener("seeked", function() {
                document.getElementById('video-info').innerHTML = '';

                if (canvas) {
                    canvas.width = video.videoWidth * 0.3;
                    canvas.height = video.videoHeight * 0.3;
                    context.drawImage(video, 0, 0, canvas.width, canvas.height);
                    URL.revokeObjectURL(fileURL);
                    canvas.style.display = "block";
                }
            }, { once: true });
        }
    });
}

// Função para verificar os campos do modal de login
function verificarCamposLogin() {
    if (!modalLogin) return; // Verifica se o modal existe
    const loginInputs = modalLogin.querySelectorAll('input[required]');
    let todosPreenchidosLogin = Array.from(loginInputs).every(input => input.value.trim());

    if (btnEntrar) {
        if (todosPreenchidosLogin) {
            btnEntrar.style.backgroundColor = "#FF0000";
            btnEntrar.style.color = "#ffffff";
        } else {
            btnEntrar.style.backgroundColor = "#d3d3d3";
            btnEntrar.style.color = "#000000";
        }
    }
}

// Evento para disparar a verificação de campos no modal de login
if (modalLogin) {
    modalLogin.addEventListener('input', verificarCamposLogin);
}

if (btnLogin) {
    btnLogin.addEventListener('click', function() {
        abrirModal(modalLogin);
        verificarCamposLogin(); // Verifica os campos ao abrir o modal
    });
}


if (getElement('#fetch-video')) {
    getElement('#fetch-video').addEventListener('click', function() {
        const url = getElement('#videoLink').value;
        const videoId = extractVideoId(url);
        if (videoId) {
            displayThumbnail(videoId);
        } else {
            getElement('#video-info').innerHTML = 'Link inválido. Por favor, insira um link válido do YouTube.';
        }
    });
}

if (getElement('#logoButton')) {
    getElement('#logoButton').addEventListener('click', function() {
        window.location.href = 'main_web.html';
    });
}

if (indexarBtn) {
    indexarBtn.addEventListener('click', function() {
        // Verifique o typeSignature antes de permitir a indexação
        fetch('/get_type_signature')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Não foi possível obter o typeSignature');
                }
                return response.json();
            })
            .then(data => {
                if (data.typeSignature === 1 || data.typeSignature === 2) {
                    // Permita a indexação apenas se o typeSignature for 1 ou 2
                    if (fileInput) fileInput.click();
                } else {
                    window.location.href = 'pagamento_tela';
                }
            })
            .catch(error => {
                console.error('Erro ao verificar o typeSignature:', error);
                alert('Erro ao verificar o plano. Tente novamente mais tarde.');
            });
    });
}

// Armazena o arquivo de vídeo selecionado
let selectedFile;
if (fileInput) {
    fileInput.addEventListener("change", function(event) {
        if (event.target.files.length > 0) {
            selectedFile = event.target.files[0];
            document.getElementById('video-info').innerHTML = `Vídeo selecionado: ${selectedFile.name}`;
        }
    });
}


// Altere o comportamento do botão TRANSCREVER para enviar o vídeo
// Altere o comportamento do botão TRANSCREVER para enviar o vídeo
if (btnTranscrever) {
    btnTranscrever.onclick = function() {
        if (!selectedFile) {
            alert('Por favor, selecione um arquivo de vídeo usando o botão INDEXAR VÍDEO.');
            return;
        }

        var progressContainer = getElement("#progress-container");
        var progressBar = getElement("#progress-bar");
        var progressLabel = getElement("#progress-label");
        progressContainer.style.display = "block";
        progressBar.style.width = "0%";
        progressLabel.textContent = "0%";

        // Verifique o typeSignature antes de enviar o vídeo
        fetch('/get_type_signature')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Não foi possível obter o typeSignature');
                }
                return response.json();
            })
            .then(data => {
                if (data.typeSignature === 1 || data.typeSignature === 2) {
                    // Envie o vídeo para transcrição apenas se o typeSignature for 1 ou 2
                    var formData = new FormData();
                    formData.append('file', selectedFile);
                    updateProgressBar(30);

                    fetch('/transcrever', {
                        method: 'POST',
                        body: formData
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.message === "Vídeo enviado para transcrição com sucesso.") {
                            alert('Vídeo enviado para transcrição com sucesso. Aguarde a notificação de download.');
                            updateProgressBar(60);
                            startPolling(data.video_id); // Inicia o loop de verificação
                        } else {
                            console.error('Erro ao enviar o vídeo:', data.error);
                            alert('Erro ao enviar o vídeo: ' + data.error);
                            resetProgressBar();
                        }
                    })
                    .catch(error => {
                         console.error('Erro ao transcrever o vídeo:', error);
                         alert('Erro ao transcrever o vídeo:', error);
                         resetProgressBar(); // Resetar a barra de progresso em caso de erro
                    });
                } else {
                    // Exiba uma mensagem de erro no console se o typeSignature for 0
                    window.location.href = 'pagamento_tela';
                }
            })
            .catch(error => {
                console.error('Erro ao verificar o typeSignature:', error);
                alert('Erro ao verificar o plano. Tente novamente mais tarde.');
                resetProgressBar();
            });
    };
}

var contagem_bar = 0
function startPolling(video_id) {
    console.log("video_id:", video_id)
    var intervalId = setInterval(function() {
        fetch('/transcription_status?video_id=' + video_id)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'completed') {
                clearInterval(intervalId); // Para o loop de verificação
                // Inicia o download usando window.location
                updateProgressBar(100);
                window.location.href = data.video_url;
                esconder_bar();
            } else if (data.status === 'error') {
                clearInterval(intervalId);
                alert('Erro na transcrição: ' + data.error);
                resetProgressBar();
            } else {
                if (contagem_bar === 5) {
                    // Sorteio de tempo e porcentagem
                    const tempoEspera = Math.floor(Math.random() * 7000) + 3000; // Tempo entre 3 e 10 segundos
                    const porcentagemAumento = Math.floor(Math.random() * 5) + 1; // Aumento entre 1 e 5%

                    // Atualiza a barra de progresso com o valor sorteado
                    var currentPercentage = parseInt(getElement("#progress-label").textContent);
                    var newPercentage = Math.min(currentPercentage + porcentagemAumento, 99); // Garante que não ultrapasse 99%
                    updateProgressBar(newPercentage);
                    contagem_bar = 0

                }
                else {
                    contagem_bar = contagem_bar + 1
                }
            }
        })
        .catch(error => {
            clearInterval(intervalId);
            console.error('Erro ao verificar o status da transcrição:', error);
            alert('Erro ao verificar o status da transcrição: ' + error);
            resetProgressBar();
        });
    }, 5000); // Verifica a cada 5 segundos
}

// Função para atualizar a barra de progresso
function updateProgressBar(percentage) {
    var progressBar = getElement("#progress-bar");
    var progressLabel = getElement("#progress-label");
    progressBar.style.width = percentage + "%";
    progressLabel.textContent = percentage + "%";
}

// Função para resetar a barra de progresso
function resetProgressBar() {
    var progressContainer = getElement("#progress-container");
    var progressBar = getElement("#progress-bar");
    var progressLabel = getElement("#progress-label");
    progressContainer.style.display = "none";
    progressBar.style.width = "0%";
    progressLabel.textContent = "0%";
}

function esconder_bar() {
    var progressContainer = getElement("#progress-container");
    var progressBar = getElement("#progress-bar");
    var progressLabel = getElement("#progress-label");
    progressContainer.style.display = "none";
    progressBar.style.display = "none";
    progressLabel.style.display = "none";
}

function extractVideoId(url) {
    const regex = /(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/.*(?:v=|shorts\/)|youtu\.be\/)([a-zA-Z0-9_-]{11})/;
    const match = url.match(regex);
    return match ? match[1] : null;
}

function displayThumbnail(videoId) {
    if (canvas) canvas.style.display = "none";
    const imgUrl = `https://img.youtube.com/vi/${videoId}/0.jpg`;
    getElement('#video-info').innerHTML = `
        <img src="${imgUrl}" alt="Thumbnail do vídeo" style="max-width: 100%; height: auto; border-radius: 10px;">
    `;
}

// Função para limpar inputs de um modal
function limparInputs(modal) {
    const inputs = modal.querySelectorAll('input');
    inputs.forEach(input => input.value = ""); // Limpa os valores dos inputs
}

// Funções para abrir modais
function abrirModal(modal) {
    console.log(modal)
    if (modal) {
        limparInputs(modal);  // Limpa os inputs ao abrir o modal
        modal.style.display = "block";
    }
    else{
        console.log("bnao encontrado");
    }
}

function abrirModalContato() {
    abrirModal(modalContato);
}

function abrirModalPrice() {
    abrirModal(modalPrice);
}

// Eventos de fechamento de modal
spanCloses.forEach(function(spanClose) {
    spanClose.onclick = function() {
        if (this.closest('.modal, .modalPrice')) {
            this.closest('.modal, .modalPrice').style.display = "none";
        }
    };
});

// Eventos de clique
if (btnCadastrar) btnCadastrar.onclick = function() { abrirModal(modal); };
if (btnTranscrever_index) btnTranscrever_index.onclick = function() { abrirModal(modal); };
if (btnIndexar_index) btnIndexar_index.onclick = function() { abrirModal(modal) };
if (btnLogin) btnLogin.onclick = function() {
     abrirModal(modalLogin);
     var recuperePassword = document.getElementById("recoverPasswordBtn");
     recuperePassword.style.display = "none"
};
if (btnContato) btnContato.addEventListener('click', function(event) {
    event.preventDefault();
    abrirModalContato();
});

var signButtons = getElements('.sign-button');
signButtons.forEach(function(button) {
    button.onclick = function() {
        if (modalPrice) modalPrice.style.display = "none";
        abrirModal(modal);
        verificarCampos();
        verificarStatusERedirecionar();
    };
});

function verificarStatusERedirecionar() {
    fetch('/get_type_signature')  // Substitua '/sua_nova_rota' pela rota real
        .then(response => {
            if (!response.ok) {
                throw new Error('Erro ao obter o status');
            }
            return response.json();
        })
        .then(data => {
            const status = data.status;  // Supondo que a resposta JSON contenha um campo 'status' com o número inteiro

            if (status === 0) {
                window.location.href = 'pagamento_tela';  // Redireciona para a tela de pagamento
            } else {
                window.location.href = 'perfil-logged';  // Redireciona para a tela de perfil
            }
        })
        .catch(error => {
            console.error('Erro ao verificar o status:', error);
            alert('Erro ao verificar o status. Tente novamente mais tarde.');
        });
}

// Verificação de campos
function verificarCampos() {
    if (!form) return;
    const inputs = form.querySelectorAll('input[required]');
    let todosPreenchidos = Array.from(inputs).every(input => input.value.trim());

    const senhasIguais = getElement('#password').value === getElement('#passwordrepeat').value;

    if (submitButton) {
        if (todosPreenchidos && !registeredEmails.includes(emailInput.value) && senhasIguais) {
            submitButton.style.backgroundColor = "#FF0000";
            submitButton.style.color = "#ffffff";
        } else {
            submitButton.style.backgroundColor = "#d3d3d3";
            submitButton.style.color = "#000000";
        }
    }
}

function abrirModalExit() {
    modalExit.style.display = "block";
}



if (form) {
    form.addEventListener('input', verificarCampos);
}

if (btnCadastrar) {
    btnCadastrar.addEventListener('click', verificarCampos);
}

function showMessageModal() {
    const modal = document.getElementById('messageModal');
    modal.style.display = 'block';

    // Fechar o modal após 3 segundos
    setTimeout(() => {
        modal.style.display = 'none';
    }, 3000);
    is_sucess_register = false;
}

function showMessageModalRecupere() {
    const modal = document.getElementById('messageModalRecupere');
    modal.style.display = 'block';

    // Fechar o modal após 3 segundos
    setTimeout(() => {
        modal.style.display = 'none';
    }, 3000);
    is_sucess_register = false;
}

function executeActionAndShowModal() {
    // Supondo que 'fetchAction' seja a ação que desejamos executar
    fetch('/')
        .then(response => {
            if (response.ok) {
                response.text().then(() => {
                    // Após a ação bem-sucedida, exibir o modal de mensagem
                    showMessageModal();

                    // Redirecionar para a página principal após o modal ser fechado
                    setTimeout(() => {
                        window.location.href = response.url;
                    }, 2000); // Adicionando um delay para respeitar o tempo do modal
                });
            } else {
                // Caso contrário, exibir uma mensagem de erro
                response.text().then(text => alert('Erro ao redirecionar: ' + text));
            }
        })
        .catch(error => console.error('Error:', error));
}

function toggleLoadingSpinner(show) {
    var loadingSpinner = getElement("#loading-spinner");
    if (loadingSpinner) {
        loadingSpinner.style.display = show ? "block" : "none";
    }
}



document.addEventListener('DOMContentLoaded', function() {
    // Duplicação desnecessária destas variáveis
    // Elas já foram definidas anteriormente no código
    // var modalLogin = document.querySelector("#myModalLogin");
    // var modalRecupere = document.querySelector("#modalRecupere");

    console.log("Modal Recupere encontrado:", !!modalRecupere);

    var btnRecoverPassword = document.querySelector("#recoverPasswordBtn");

    if (btnRecoverPassword) {
        btnRecoverPassword.addEventListener('click', function() {
            fetchRegisteredEmails();
            emailInputLoginRecupere = document.querySelector('#loginemail');
            if (registeredEmails.includes(emailInputLoginRecupere.value)) {
                if (modalLogin) {
                    modalLogin.style.display = "none";
                }
                if (modalRecupere) {
                    modalRecupere.style.display = "block";
                    limparInputs(modalRecupere);
                } else {
                    console.error("Modal de recuperação não encontrado.");
                }
            }
            else {
                modalLogin.style.display = "none";
                modalRecupere.style.display = "none";
            }});
    }

    // Evento para verificar senhas no modal de recuperação
    if (modalRecupere) {
        modalRecupere.addEventListener('input', verificarSenhasRecupere);
    }
});

function for_logged() {
    window.location.href = '/logged';
}

document.getElementById('registerForm').addEventListener('submit', function(event) {
  event.preventDefault();

  const formData = new FormData(this);

  fetch('/register', {
    method: 'POST',
    body: formData
  })
  .then(response => response.text())
  .then(result => {

  })
  .catch(error => console.error('Error:', error));
  executeActionAndShowModal();
});

document.getElementById('loginForm').addEventListener('submit', function(event) {
  event.preventDefault();
  verificarSenhasLogin();
  const formData = new FormData(this);

  toggleLoadingSpinner(true);

  fetch('/login', {
    method: 'POST',
    body: formData
  })
  .then(response => {
    if (response.ok) {
      // Se a resposta do servidor for 200 OK, redirecionar para logged.html
      setTimeout(for_logged, 3000);
      toggleLoadingSpinner(false);
    } else {
      // Caso contrário, exibir uma mensagem de erro
      getElement('#loginpassword').setCustomValidity("Senha inválida");
      toggleLoadingSpinner(false);
    }
  })
  .catch(error => {
        console.error('Error:', error);
        // Esconde a animação de carregamento em caso de erro
        toggleLoadingSpinner(false);
    });
});



// Função para buscar e-mails ao abrir o modal
function fetchRegisteredEmails() {
    fetch('/get_registered_emails')
        .then(response => response.json())
        .then(data => {
            registeredEmails = data;
        })
        .catch(error => console.error('Erro ao buscar e-mails registrados:', error));
}

// Adicione a chamada para `fetchRegisteredEmails` quando o modal for aberto
if (btnCadastrar) {
    btnCadastrar.onclick = function() {
        abrirModal(modal);
        fetchRegisteredEmails();
    };
}

var emailInput = document.querySelector('#email');
var errorMessage = document.querySelector('#error-message');

// Função para verificar se o e-mail está no banco de dados
function verificarEmail() {
    if (registeredEmails.includes(emailInput.value)) {
        emailInput.style.backgroundColor = "#d3d3d3"; // Mesma cor que campo vazio
        emailInput.style.color = "#000000";
        emailInput.setCustomValidity("E-mail já existente.");
    } else {
        emailInput.style.backgroundColor = "#e8e8e8"; // Cor normal do campo
        emailInput.style.color = "#000000";
        errorMessage.textContent = '';
        emailInput.setCustomValidity("");
    }
}

// Evento de input para disparar a verificação do email
emailInput.addEventListener('input', function () {
    verificarEmail();
});

if (form) {
    form.addEventListener('input', verificarCampos);
}

document.addEventListener('DOMContentLoaded', function() {
    // Faz uma solicitação para o servidor para obter a string
    fetch('/get-username')
        .then(response => response.json())
        .then(data => {
            // Insere a string no elemento desejado
            const messageElement = document.getElementById('usernameLogged');
            if (messageElement) {
                messageElement.textContent = data.message;
            }
        })
        .catch(error => console.error('Erro ao obter a mensagem do usuário:', error));
});

function verificarSenhasLogin() {
    const email = getElement('#loginemail').value;
    const senhaDigitada = getElement('#loginpassword').value;

    fetch('/verify_user_password', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email: email, password: senhaDigitada })
    })
    .then(response => response.json())
    .then(data => {
        if (data.valid) {
            getElement('#loginpassword').setCustomValidity("");
            getElement('#loginpassword').style.backgroundColor = "#e8e8e8"; // Cor normal do campo
            getElement('#loginpassword').style.color = "#000000";
        } else {
            getElement('#loginpassword').setCustomValidity(data.error);
            getElement('#loginpassword').style.backgroundColor = "#d3d3d3"; // Mesma cor que campo vazio
            getElement('#loginpassword').style.color = "#000000";
        }
    })
    .catch(error => console.error('Erro ao verificar a senha:', error));
}

// Adicione o evento para verificar senhas ao input de senha
senhaInputLogin = getElement('#loginpassword');
if (senhaInputLogin) {
    senhaInputLogin.addEventListener('input', verificarSenhasLogin);
}

// Adicionando eventos de input para disparar a verificação de senha
getElement('#password').addEventListener('input', verificarSenhas);
getElement('#passwordrepeat').addEventListener('input', verificarSenhas);

function verificarSenhas() {
    const senha = getElement('#password');
    const repetirSenha = getElement('#passwordrepeat');

    // Verifica se os campos de senha estão disponíveis e comparam os valores
    if (senha && repetirSenha) {
        if (senha.value !== repetirSenha.value) {
            repetirSenha.setCustomValidity("Por favor, repita a mesma senha.");
        } else {
            repetirSenha.setCustomValidity("");
        }
    }
}

function verificarSenhasRecupere() {
    const novaSenha = modalRecupere.querySelector('#loginemailrecupere');
    const repetirNovaSenha = modalRecupere.querySelector('#loginpasswordrecupere');

    if (btnRegistrarRecupere) {
        if (novaSenha.value === repetirNovaSenha.value) {
            btnRegistrarRecupere.style.backgroundColor = "#FF0000"; // Vermelho quando iguais
            btnRegistrarRecupere.style.color = "#ffffff";
        } else {
            btnRegistrarRecupere.style.backgroundColor = "#d3d3d3"; // Cinza quando diferentes
            btnRegistrarRecupere.style.color = "#000000";
        }
    }
}

var emailInputLogin = document.querySelector('#loginemail');verificarEmailLogin()
function verificarEmailLogin() {
    if (registeredEmails.includes(emailInputLogin.value)) {
        emailInputLogin.setCustomValidity("");
        var recuperePassword = document.getElementById("recoverPasswordBtn");
        recuperePassword.style.display = "block";
    } else {
        emailInputLogin.setCustomValidity("E-mail não cadastrado");
    }
}

loginemail = getElement('#loginemail');
if (loginemail) {
    fetchRegisteredEmails();
    loginemail.addEventListener('input', verificarEmailLogin);
    var recuperePassword = document.getElementById("recoverPasswordBtn");
    recuperePassword.style.display = "block";
}

// Adicionando eventos de input para disparar a verificação de senha
senhaInput = getElement('#password');
repetirSenhaInput = getElement('#passwordrepeat');

if (senhaInput) {
    senhaInput.addEventListener('input', verificarSenhas);
}

if (repetirSenhaInput) {
    repetirSenhaInput.addEventListener('input', verificarSenhas);
}

// Função para verificar senhas no modal de recuperação e alterar a cor do botão
function verificarSenhasRecupere() {
    const novaSenha = modalRecupere.querySelector('#loginemailrecupere');
    const repetirNovaSenha = modalRecupere.querySelector('#loginpasswordrecupere');

    if (novaSenha && repetirNovaSenha) {
        if (novaSenha.value !== repetirNovaSenha.value) {
            repetirNovaSenha.setCustomValidity("Por favor, repita a mesma senha.");
            btnRegistrarRecupere.style.backgroundColor = "#d3d3d3"; // Cinza quando diferentes
            btnRegistrarRecupere.style.color = "#000000";
        } else {
            repetirNovaSenha.setCustomValidity("");
            btnRegistrarRecupere.style.backgroundColor = "#FF0000"; // Vermelho quando iguais
            btnRegistrarRecupere.style.color = "#ffffff";
        }
    }
}

// Evento para disparar a verificação de senhas no modal de recuperação
if (modalRecupere) {
    modalRecupere.addEventListener('input', verificarSenhasRecupere);
}

// Verificação de senhas ao clicar no botão "Registrar"
if (btnRegistrarRecupere) {
    btnRegistrarRecupere.addEventListener('click', function(event) {
        event.preventDefault(); // Previne o envio do formulário se as senhas estiverem diferentes

        // Checa se os avisos de validação estão presentes
        const repetirNovaSenha = modalRecupere.querySelector('#loginpasswordrecupere');
        if (!repetirNovaSenha.checkValidity()) {
            // Exibe mensagem de erro se houver
            repetirNovaSenha.reportValidity();
        } else {
            // Senhas são iguais, prosseguir com a submissão do formulário
            const emailInputLogin = document.querySelector('#loginemail').value;
            const novaSenha = modalRecupere.querySelector('#loginemailrecupere').value;

            fetch('/update_password', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email: emailInputLogin, new_password: novaSenha })
            })
            .then(response => {
                if (response.ok) {
                    modalRecupere.style.display = "none";
                    showMessageModalRecupere()
                } else {
                    alert("Erro ao alterar senha.");
                    console.log(response.status);
                }
            })
            .catch(error => console.error('Erro:', error));
        }
    });
}









