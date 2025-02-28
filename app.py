from flask import Flask, request, jsonify, render_template, session, redirect, url_for
import os
import stripe
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import requests
from werkzeug.utils import secure_filename
import uuid
import threading

app = Flask(__name__)

# Configurar a variável de ambiente
TRANSCRIPTION_API_URL = os.getenv('TRANSCRIPTION_API_URL')

# Configurar a chave secreta do Flask a partir da variável de ambiente
app.secret_key = os.environ.get('SECRET_KEY')

# Configurar a chave de API do Stripe a partir da variável de ambiente
stripe.api_key = os.environ.get('STRIPE_API_KEY')

# Configurações do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Chave secreta para webhook
WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET')

app.config['SERVER_NAME'] = os.environ.get('SERVER_NAME')

# Armazenar a URL do vídeo transcrito
transcription_results = {}

# Rota para receber o vídeo e iniciar a transcrição
@app.route('/transcrever', methods=['POST'])
def transcrever():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400

        video_file = request.files['file']
        video_filename = secure_filename(video_file.filename)
        video_path = os.path.join('/tmp', video_filename)
        video_file.save(video_path)

        # Gere um ID único para o vídeo
        video_id = str(uuid.uuid4())

        # Envie o vídeo para o serviço de transcrição em uma thread separada
        threading.Thread(target=send_video_for_transcription, args=(video_filename, video_path, video_id)).start()

        return jsonify({"message": "Vídeo enviado para transcrição com sucesso.", "video_id": video_id}), 200

    except Exception as e:
        print(f"Erro no processamento da transcrição: {e}")
        return jsonify({"error": "Erro interno no servidor."}), 500

def send_video_for_transcription(video_filename, video_path, video_id):
    try:
        # Envie o vídeo para o serviço de transcrição
        transcription_url = f"{TRANSCRIPTION_API_URL}/transcribe"
        print(f"URL de transcrição: {transcription_url}")

        with open(video_path, 'rb') as video_file:
            files = {'file': (video_filename, video_file, 'multipart/form-data')}
            with app.app_context():
                webhook_url = url_for('transcription_webhook', _external=True)
            data = {'video_id': video_id, 'webhook_url': webhook_url}
            response = requests.post(transcription_url, files=files, data=data)

        if response.status_code != 200:
            print(f"Erro ao enviar o vídeo para transcrição: {response.status_code}")
            # Lide com o erro aqui (por exemplo, tente novamente mais tarde)

    except Exception as e:
        print(f"Erro ao enviar o vídeo para transcrição: {e}")

# Rota para receber a notificação do webhook
@app.route('/transcription_webhook', methods=['POST'])
def transcription_webhook():
    # Verifique a autenticidade da requisição
    webhook_token = request.headers.get('X-Webhook-Token')
    if webhook_token != WEBHOOK_SECRET:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

    data = request.get_json()
    video_id = data.get('video_id')
    video_url = data.get('video_url')

    # Armazena a URL do vídeo transcrito
    transcription_results[video_id] = {'status': 'completed', 'video_url': video_url}

    return jsonify({'status': 'success', 'video_url': video_url}), 200

# Rota para verificar o status da transcrição
@app.route('/transcription_status', methods=['GET'])
def transcription_status():
    print("transcription_status")
    video_id = request.args.get('video_id')
    print("transcription_status_videoID: ", video_id)
    if video_id in transcription_results:
        return jsonify(transcription_results[video_id]), 200
    else:
        print("pending")
        return jsonify({'status': 'pending'}), 200

# Definição do modelo de usuário
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    typeSignature = db.Column(db.Integer)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get-username')
def get_username():
    return jsonify(message=session.get('username', ''))

@app.route('/register', methods=['GET', 'POST'])
def register():
    error_message = None

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        repeatpassword = request.form['passwordrepeat']
        typeSignature = 0

        if password != repeatpassword:
            error_message = "POR FAVOR, REPITA SENHA CORRETAMENTE"
        else:
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                error_message = 'E-MAIL EXISTENTE'
            else:
                hashed_senha = generate_password_hash(password, method='pbkdf2:sha256')
                new_user = User(nome=name, email=email, senha=hashed_senha, typeSignature=typeSignature)
                db.session.add(new_user)
                db.session.commit()
                return redirect(url_for('index'))

    return render_template('index.html', error_message=error_message)

@app.route('/get_registered_emails', methods=['GET'])
def get_registered_emails():
    users = User.query.with_entities(User.email).all()
    email_list = [user.email for user in users]
    return jsonify(email_list)

@app.route('/verify_user_password', methods=['POST'])
def verify_user_password():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.senha, password):
        return jsonify({"valid": True}), 200
    else:
        return jsonify({"valid": False, "error": "Senha inválida"}), 401

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.senha, password):
            session['username'] = user.nome
            session['user_email'] = email
            return '', 200
        else:
            return 'Invalid credentials', 401
    return render_template('index.html')

@app.route('/logged')
def logged():
    username = session.get('username')
    if username:
        return render_template('logged.html', username=username)
    return redirect(url_for('login'))

@app.route('/update_password', methods=['POST'])
def update_password():
    data = request.json
    email = data.get('email')
    new_password = data.get('new_password')

    if not email or not new_password:
        return jsonify({"success": False, "error": "Dados incompletos"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"success": False, "error": "Usuário não encontrado"}), 404

    hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')
    user.senha = hashed_password
    db.session.commit()

    return jsonify({"success": True}), 200

@app.route('/perfil-logged')
def perfil_logged():
    email = session.get('user_email')
    if not email:
        return redirect(url_for('login'))

    user = User.query.filter_by(email=email).first()

    if not user:
        return "Usuário não encontrado", 404

    assinatura_text = "SEM PLANO" if user.typeSignature == 0 else "COM PLANO"
    user_data = {
        "nome": user.nome,
        "email": user.email,
        "senha": user.senha,
        "assinatura": assinatura_text
    }

    return render_template('tela_perfil.html', user=user_data)

@app.route('/como-usar-logged')
def como_usar_logged():
    return render_template('tela_como_usar_logged.html')

@app.route('/como-usar')
def como_usar():
    return render_template('tela_como_usar.html')

@app.route('/termos-de-servico-logged')
def termos_de_servico_logged():
    return render_template('tela_termos_de_servico_logged.html')

@app.route('/termos-de-servico')
def termos_de_servico():
    return render_template('tela_termos_de_servico.html')

@app.route('/politica-de-privacidade-logged')
def politica_de_privacidade_logged():
    return render_template('tela_politica_de_privacidade_logged.html')

@app.route('/politica-de-privacidade')
def politica_de_privacidade():
    return render_template('tela_politica_de_privacidade.html')

@app.route('/sobre-nos-logged')
def sobre_nos_logged():
    return render_template('tela_sobre_nos_logged.html')

@app.route('/sobre-nos')
def sobre_nos():
    return render_template('tela_sobre_nos.html')

@app.route('/pagamento')
def pagamento():
    return render_template('pagamento.html')

if __name__ == '__main__':
    app.run(debug=True)