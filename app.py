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
import datetime
import pytz

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
    check_daily_plan_internal()
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
    check_daily_plan_internal()
    # Verifique a autenticidade da requisição
    webhook_token = request.headers.get('X-Webhook-Token')
    print("error rota")
    if webhook_token != WEBHOOK_SECRET:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

    data = request.get_json()
    video_id = data.get('video_id')
    teste_url = "https://videos.legendasoficial.com/output_video_11.mp4"
    video_url = data.get('video_url')
    video_url = teste_url
    print("video_url ",video_url)

    # Armazena a URL do vídeo transcrito
    transcription_results[video_id] = {'status': 'completed', 'video_url': video_url}

    return jsonify({'status': 'success', 'video_url': video_url}), 200

# Rota para verificar o status da transcrição
@app.route('/transcription_status', methods=['GET'])
def transcription_status():
    check_daily_plan_internal()
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
    subscription_id = db.Column(db.String(255), nullable=True)
    daily_plan_expiration = db.Column(db.DateTime, nullable=True)

### Rotas para gerenciar typeSignature ###
@app.route('/get_type_signature', methods=['GET'])
def get_type_signature():
    check_daily_plan_internal()
    email = session.get('user_email')
    if not email:
        return jsonify({"error": "Usuário não autenticado"}), 401

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404

    return jsonify({"typeSignature": user.typeSignature}), 200

@app.route('/update_type_signature', methods=['POST'])
def update_type_signature():
    check_daily_plan_internal()
    email = session.get('user_email')
    if not email:
        return jsonify({"error": "Usuário não autenticado"}), 401

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404

    data = request.get_json()
    new_type_signature = data.get('typeSignature')

    if new_type_signature is None or not isinstance(new_type_signature, int):
        return jsonify({"error": "Valor de typeSignature inválido"}), 400

    user.typeSignature = new_type_signature
    db.session.commit()

    return jsonify({"message": "typeSignature atualizado com sucesso"}), 200
### Fim das rotas para gerenciar typeSignature ###

@app.route('/')
def index():
    check_daily_plan_internal()
    return render_template('index.html')

@app.route('/get-username')
def get_username():
    check_daily_plan_internal()
    return jsonify(message=session.get('username', ''))

@app.route('/register', methods=['GET', 'POST'])
def register():
    check_daily_plan_internal()
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
    check_daily_plan_internal()
    users = User.query.with_entities(User.email).all()
    email_list = [user.email for user in users]
    return jsonify(email_list)

@app.route('/verify_user_password', methods=['POST'])
def verify_user_password():
    check_daily_plan_internal()
    data = request.get_json()
    if not data:
        return jsonify({"error": "Nenhum dado JSON recebido"}), 400

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Dados incompletos"}), 400

    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.senha, password):
        return jsonify({"valid": True}), 200
    else:
        return jsonify({"valid": False, "error": "Senha inválida"}), 401

@app.route('/login', methods=['GET', 'POST'])
def login():
    check_daily_plan_internal()
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
    check_daily_plan_internal()
    username = session.get('username')
    user = User.query.filter_by(email=session.get('user_email')).first()
    user.typeSignature = 0
    user.subscription_id = None
    user.daily_plan_expiration = None
    db.session.commit()

    if username:
        return render_template('logged.html', username=username)
    return redirect(url_for('login'))

@app.route('/update_password', methods=['POST'])
def update_password():
    check_daily_plan_internal()
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
    check_daily_plan_internal()
    email = session.get('user_email')
    if not email:
        return redirect(url_for('login'))

    user = User.query.filter_by(email=email).first()

    if not user:
        return "Usuário não encontrado", 404

    assinatura_text = "SEM PLANO" if user.typeSignature == 0 else "PLANO MENSAL" if user.typeSignature == 1 else "VÁLIDO POR 1 DIA"
    user_data = {
        "nome": user.nome,
        "email": user.email,
        "senha": user.senha,
        "assinatura": assinatura_text
    }

    return render_template('tela_perfil.html', user=user_data)

@app.route('/como-usar-logged')
def como_usar_logged():
    check_daily_plan_internal()
    return render_template('tela_como_usar_logged.html')

@app.route('/como-usar')
def como_usar():
    check_daily_plan_internal()
    return render_template('tela_como_usar.html')

@app.route('/termos-de-servico-logged')
def termos_de_servico_logged():
    check_daily_plan_internal()
    return render_template('tela_termos_de_servico_logged.html')

@app.route('/termos-de-servico')
def termos_de_servico():
    check_daily_plan_internal()
    return render_template('tela_termos_de_servico.html')

@app.route('/politica-de-privacidade-logged')
def politica_de_privacidade_logged():
    check_daily_plan_internal()
    return render_template('tela_politica_de_privacidade_logged.html')

@app.route('/politica-de-privacidade')
def politica_de_privacidade():
    check_daily_plan_internal()
    return render_template('tela_politica_de_privacidade.html')

@app.route('/sobre-nos-logged')
def sobre_nos_logged():
    check_daily_plan_internal()
    return render_template('tela_sobre_nos_logged.html')

@app.route('/sobre-nos')
def sobre_nos():
    check_daily_plan_internal()
    return render_template('tela_sobre_nos.html')

@app.route('/pagamento_tela')
def pagamento_tela():
    check_daily_plan_internal()
    return render_template('pagamento.html')

@app.route('/pagamento', methods=['POST'])
def pagamento():
    check_daily_plan_internal()
    brasilia_tz = pytz.timezone('America/Sao_Paulo')
    now_utc = datetime.datetime.utcnow()
    now_brasilia = now_utc.replace(tzinfo=pytz.utc).astimezone(brasilia_tz)
    print("Rota /pagamento acessada!")
    if request.method == 'POST':
        print("Requisição POST recebida para /pagamento")
        try:
            # Obtenha os dados do JSON
            data = request.get_json()
            if not data:
                print("Erro: Nenhum dado JSON recebido")
                return jsonify({'error': 'Nenhum dado JSON recebido'}), 400
            token = data.get('stripeToken')
            plan = data.get('plan')
            name = data.get('name')
            email_form = data.get('email')  # Usando email_form para evitar conflito com email da sessão

            print(f"Token do Stripe recebido: {token}")
            print(f"Plano recebido: {plan}")
            print(f"Nome recebido: {name}")
            print(f"Email do formulário recebido: {email_form}")

            email = session.get('user_email')  # Obtém o email da sessão
            if not email:
                print("Erro: Email não encontrado na sessão")
                return jsonify({'error': 'Email não encontrado na sessão'}), 400

            user = User.query.filter_by(email=email).first()
            if not user:
                print("Erro: Usuário não encontrado no banco de dados")
                return jsonify({'error': 'Usuário não encontrado no banco de dados'}), 404

            if plan == 'basic':
                plan_typeSignature = 2
                price_id = 'price_1Qz1P0LTkDndcSCYcAFWMpZu'  # Substitua pelo seu price ID mensal real
            elif plan == 'standard':
                plan_typeSignature = 1
                price_id = 'price_1Qz1NrLTkDndcSCYd1kGyUAZ'  # Substitua pelo seu price ID diário real
            else:
                print("Plano inválido selecionado")
                return jsonify({'error': 'Plano inválido'}), 400
            print(f"ID do preço do Stripe: {price_id}")

            # Crie um cliente no Stripe
            customer = stripe.Customer.create(
                email=email_form,  # Usando o email do formulário
                source=token,
                name=name,
            )
            print(f"Cliente do Stripe criado: {customer.id}")

            # Para pagamentos únicos (plano diário), utilize stripe.charges.create
            if plan == 'basic':
                charge = stripe.Charge.create(
                    amount=390,  # R$3,90 em centavos
                    currency='brl',
                    customer=customer.id,
                    description='Pagamento único para plano diário'
                )
                user.typeSignature = plan_typeSignature
                user.subscription_id = charge.id  # Armazene o ID da cobrança para referência
                user.daily_plan_expiration = now_brasilia + datetime.timedelta(hours=24)


            # Para assinaturas (plano mensal), utilize stripe.Subscription.create
            elif plan == 'standard':
                subscription = stripe.Subscription.create(
                    customer=customer.id,
                    items=[{
                        "price": price_id,
                    }],
                )
                user.typeSignature = plan_typeSignature
                user.subscription_id = subscription.id
                user.daily_plan_expiration = None

            db.session.commit()
            print("Dados do usuário atualizados no banco de dados")

            print("Pagamento bem-sucedido!")
            return jsonify({'success': True, 'redirect': '/pagamento_sucesso'})
        except stripe.error.CardError as e:
            # Ocorreu um erro com o cartão
            print(f"Erro no cartão: {str(e)}")
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            # Outro erro ocorreu
            print(f"Erro inesperado: {str(e)}")
            return jsonify({'error': str(e)}), 500
    else:
        print("Requisição GET recebida para /pagamento - Não permitida")
        return jsonify({'error': 'Método não permitido'}), 405

@app.route('/cancelar_plano', methods=['POST'])
def cancelar_plano():
    check_daily_plan_internal()
    email = session.get('user_email')
    if not email:
        return jsonify({"error": "Usuário não autenticado"}), 401

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404

    try:
        # Cancela a assinatura no Stripe usando o subscription_id do usuário
        if user.subscription_id:
            stripe.Subscription.delete(user.subscription_id)  # Cancela a assinatura

            # Atualizar o typeSignature do usuário no banco de dados para 0 (SEM PLANO) e limpar o subscription_id
            user.typeSignature = 0
            user.subscription_id = None
            db.session.commit()

            return jsonify({"success": True, "message": "Plano cancelado com sucesso"}), 200
        else:
            return jsonify({"error": "Nenhuma assinatura ativa encontrada para este usuário"}), 404

    except Exception as e:
        print(f"Erro ao cancelar o plano: {str(e)}")
        return jsonify({"error": "Erro ao cancelar o plano"}), 500

@app.route('/pagamento_sucesso')
def pagamento_sucesso():
    check_daily_plan_internal()
    return render_template('pagamento_sucesso.html')

# Função para verificar e atualizar o plano diário internamente
def check_daily_plan_internal():
    try:
        with app.app_context():
            brasilia_tz = pytz.timezone('America/Sao_Paulo')
            now_utc = datetime.datetime.utcnow()
            now_brasilia = now_utc.replace(tzinfo=pytz.utc).astimezone(brasilia_tz)
            now = datetime.datetime.utcnow()
            users = User.query.filter(User.typeSignature == 2, User.daily_plan_expiration != None).all()

            for user in users:
                if user.daily_plan_expiration is not None:
                    if user.daily_plan_expiration <= now_brasilia:
                        # O plano expirou, cancelar
                        user.typeSignature = 0
                        user.daily_plan_expiration = None
                        db.session.commit()
                        print(f"Plano diário expirado para o usuário: {user.email}")

    except Exception as e:
        print(f"Erro ao verificar o plano diário: {str(e)}")

if __name__ == '__main__':
    app.run(debug=True)