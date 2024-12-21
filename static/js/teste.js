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
var emailExistenteBD = false

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
    };
});

// Verificação de campos
function verificarCampos() {
    if (!form) return;
    const inputs = form.querySelectorAll('input[required]');
    let todosPreenchidos = Array.from(inputs).every(input => input.value.trim());

    if (submitButton) {
        if (todosPreenchidos && !registeredEmails.includes(emailInput.value)) {
            submitButton.disabled = false;
            submitButton.style.backgroundColor = "#FF0000";
            submitButton.style.color = "#ffffff";
        } else {
            submitButton.disabled = true;
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

document.getElementById('registerForm').addEventListener('submit', function(event) {
  event.preventDefault();

  const formData = new FormData(this);

  fetch('/register', {
    method: 'POST',
    body: formData
  })
  .then(response => response.text())
  .then(result => {
    alert(result);
  })
  .catch(error => console.error('Error:', error));
});

document.getElementById('loginForm').addEventListener('submit', function(event) {
  event.preventDefault();

  const formData = new FormData(this);

  fetch('/login', {
    method: 'POST',
    body: formData
  })
  .then(response => response.text())
  .then(result => {
    alert(result);
  })
  .catch(error => console.error('Error:', error));
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
        emailInput.style.backgroundColor = "#d3d3d3";
        emailInput.style.color = "#000000";
        errorMessage.textContent = 'E-mail já existe.';
        errorMessage.style.display = 'block';

        if (submitButton) {
            submitButton.disabled = true; // Desativa o botão
            submitButton.style.backgroundColor = "#d3d3d3";
            submitButton.style.color = "#000000";
        }

        console.log("aqui")
    } else {
        emailInput.style.backgroundColor = "#e8e8e8";
        emailInput.style.color = "#000000";
        errorMessage.textContent = '';
        errorMessage.style.display = 'none';

        verificarCampos(); // Reavalie se deve ativar o botão
    }
}

// Evento de input para disparar a verificação do email
emailInput.addEventListener('input', function () {
    verificarEmail();
});

