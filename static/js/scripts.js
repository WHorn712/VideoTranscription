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

// Seleciona botões de forma genérica
var btnCadastrar = getElement("#cadastrarBtn");
var btnLogin = getElement("#loginBtn");
var btnEntrar = modalLogin ? modalLogin.querySelector('button[type="submit"]') : null;
var btnContato = getElement('.nav-links li:nth-child(3) a');
var btnTranscrever = getElement("#transcreverBtn");
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
        if (fileInput) fileInput.click();
    });
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

// Funções para abrir modais
function abrirModal(modal) {
    if (modal) modal.style.display = "block";
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
if (btnLogin) btnLogin.onclick = function() { abrirModal(modalLogin); };
if (btnContato) btnContato.addEventListener('click', function(event) {
    event.preventDefault();
    abrirModalContato();
});
if (btnTranscrever) btnTranscrever.onclick = function() { abrirModalPrice(); };

var signButtons = getElements('.sign-button');
signButtons.forEach(function(button) {
    button.onclick = function() {
        if (modalPrice) modalPrice.style.display = "none";
        abrirModal(modal);
        verificarCampos();
    };
});

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
  verificarSenhasLogin()
  const formData = new FormData(this);

  toggleLoadingSpinner(true);

  fetch('/login', {
    method: 'POST',
    body: formData
  })
  .then(response => {
    if (response.ok) {
      // Se a resposta do servidor for 200 OK, redirecionar para logged.html
      window.location.href = '/logged';
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

let registeredEmails = [];

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
const senhaInputLogin = getElement('#loginpassword');
if (senhaInputLogin) {
    senhaInputLogin.addEventListener('input', verificarSenhasLogin);
}

getElement('#loginpassword').addEventListener('input', verificarSenhasLogin);

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

var emailInputLogin = document.querySelector('#loginemail');
function verificarEmailLogin() {
    if (registeredEmails.includes(emailInputLogin.value)) {
        emailInputLogin.setCustomValidity("");
    } else {
        emailInputLogin.setCustomValidity("E-mail não cadastrado");
    }
}
const loginemail = getElement('#loginemail');
if (loginemail) {
    fetchRegisteredEmails()
    loginemail.addEventListener('input', verificarEmailLogin);
}


// Adicionando eventos de input para disparar a verificação de senha
const senhaInput = getElement('#password');
const repetirSenhaInput = getElement('#passwordrepeat');

if (senhaInput) {
    senhaInput.addEventListener('input', verificarSenhas);
}

if (repetirSenhaInput) {
    repetirSenhaInput.addEventListener('input', verificarSenhas);
}

