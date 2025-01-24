from flask import Flask, render_template, jsonify, session, request, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import create_engine, text
import os
import stripe

app = Flask(__name__)

secret_key = os.urandom(24)
app.secret_key = os.environ.get('SECRET_KEY', secret_key)

stripe.api_key = 'sua_chave_secreta_do_stripe'

# Configurações do banco de dados
DATABASE_URL = os.environ.get('DATABASE_URL')
engine = create_engine(DATABASE_URL, echo=True)

# Função para conectar ao banco
def get_db_connection():
    return engine.connect()

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
            connection = get_db_connection()
            result = connection.execute(text('SELECT senha FROM users WHERE email = :email'), {'email': email})
            user = result.fetchone()
            connection.close()

            if user:
                error_message = 'E-MAIL EXISTENTE'
            else:
                hashed_senha = generate_password_hash(password, method='pbkdf2:sha256')
                connection = get_db_connection()
                connection.execute(text('INSERT INTO users (nome, email, senha, typeSignature) VALUES (:name, :email, :hashed_senha, :typeSignature)'),
                                   {'name': name, 'email': email, 'hashed_senha': hashed_senha, 'typeSignature': typeSignature})
                connection.close()
                return redirect(url_for('index'))

    return render_template('index.html', error_message=error_message)

@app.route('/get_registered_emails', methods=['GET'])
def get_registered_emails():
    connection = get_db_connection()
    result = connection.execute(text('SELECT email FROM users'))
    emails = result.fetchall()
    connection.close()

    email_list = [email[0] for email in emails]
    return jsonify(email_list)

@app.route('/verify_user_password', methods=['POST'])
def verify_user_password():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    connection = get_db_connection()
    result = connection.execute(text('SELECT senha FROM users WHERE email = :email'), {'email': email})
    user = result.fetchone()
    connection.close()

    if user and check_password_hash(user[0], password):
        return jsonify({"valid": True}), 200
    else:
        return jsonify({"valid": False, "error": "Senha inválida"}), 401

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        connection = get_db_connection()
        result = connection.execute(text('SELECT nome, senha FROM users WHERE email = :email'), {'email': email})
        user = result.fetchone()
        connection.close()

        if user and check_password_hash(user[1], password):
            session['username'] = user[0]
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
    try:
        data = request.json
        email = data.get('email')
        new_password = data.get('new_password')

        if not email or not new_password:
            return jsonify({"success": False, "error": "Dados incompletos"}), 400

        connection = get_db_connection()
        result = connection.execute(text('SELECT email FROM users WHERE email = :email'), {'email': email})
        user = result.fetchone()
        if not user:
            connection.close()
            return jsonify({"success": False, "error": "Usuário não encontrado"}), 404

        hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')
        connection.execute(text('UPDATE users SET senha = :hashed_password WHERE email = :email'),
                           {'hashed_password': hashed_password, 'email': email})
        connection.close()

        return jsonify({"success": True}), 200
    except Exception as e:
        app.logger.error(f"Error in update_password: {str(e)}")
        return jsonify({"success": False, "error": "Internal server error"}), 500

@app.route('/perfil-logged')
def perfil_logged():
    email = session.get('user_email')
    if not email:
        return redirect(url_for('login'))

    connection = get_db_connection()
    result = connection.execute(text('SELECT nome, email, senha, typeSignature FROM users WHERE email = :email'), {'email': email})
    user_data = result.fetchone()
    connection.close()

    if not user_data:
        return "Usuário não encontrado", 404

    assinatura_text = "SEM PLANO" if user_data[3] == 0 else "COM PLANO"
    user = {
        "nome": user_data[0],
        "email": user_data[1],
        "senha": user_data[2],
        "assinatura": assinatura_text
    }

    return render_template('tela_perfil.html', user=user)

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