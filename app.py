from flask import Flask, render_template, jsonify, session
import pymysql
from flask import request, redirect, url_for
from jupyter_events.cli import console
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)

secret_key = os.urandom(24)
app.secret_key = os.environ.get('SECRET_KEY', secret_key)


# Configurações do banco de dados
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'rootsun5219'
app.config['MYSQL_DB'] = 'project_transcription_web'

# Função para conectar ao banco
def get_db_connection():
    return pymysql.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        db=app.config['MYSQL_DB']
    )

@app.route('/')
def index():
    return render_template('index.html')

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
            with connection.cursor() as cursor:
                cursor.execute('SELECT senha FROM users WHERE email = %s', (email,))
                user = cursor.fetchone()
            connection.close()

            if user:
                error_message = 'E-MAIL EXISTENTE'
            else:
                hashed_senha = generate_password_hash(password, method='pbkdf2:sha256')
                connection = get_db_connection()
                with connection.cursor() as cursor:
                    cursor.execute('INSERT INTO users (nome, email, senha, typeSignature) VALUES (%s, %s, %s, %s)',
                                   (name, email, hashed_senha, typeSignature))
                    connection.commit()
                connection.close()
                return redirect(url_for('index'))

    return render_template('index.html', error_message=error_message)

@app.route('/get_registered_emails', methods=['GET'])
def get_registered_emails():
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute('SELECT email FROM users')
        emails = cursor.fetchall()
    connection.close()

    # Converte a lista de tuplas para uma lista simples de strings
    email_list = [email[0] for email in emails]
    return jsonify(email_list)

@app.route('/verify_user_password', methods=['POST'])
def verify_user_password():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute('SELECT senha FROM users WHERE email = %s', (email,))
        user = cursor.fetchone()
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
        with connection.cursor() as cursor:
            cursor.execute('SELECT nome, senha FROM users WHERE email = %s', (email,))
            user = cursor.fetchone()
        connection.close()

        if user and check_password_hash(user[1], password):
            session['username'] = user[0]
            return '', 200  # Retorna código 200 para sucesso
        else:
            return 'Invalid credentials', 401  # Retorna código 401 para falha
    return render_template('index.html')

@app.route('/logged')
def logged():
    username = session.get('username')
    if username:
        return render_template('logged.html', username=username)
    return redirect(url_for('login'))

#@app.route('/get_password', methods=['GET'])
#def update_password():


@app.route('/update_password', methods=['POST'])
def update_password():
    try:
        data = request.json
        email = data.get('email')
        new_password = data.get('new_password')

        if not email or not new_password:
            return jsonify({"success": False, "error": "Dados incompletos"}), 400

        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute('SELECT email FROM users WHERE email = %s', (email,))
            user = cursor.fetchone()
            if not user:
                connection.close()
                return jsonify({"success": False, "error": "Usuário não encontrado"}), 404

            hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')
            cursor.execute('UPDATE users SET senha = %s WHERE email = %s', (hashed_password, email))
            connection.commit()
        connection.close()

        return jsonify({"success": True}), 200
    except Exception as e:
        app.logger.error(f"Error in update_password: {str(e)}")
        return jsonify({"success": False, "error": "Internal server error"}), 500


@app.route('/como-usar')
def como_usar():
    return render_template('tela_como_usar.html')

@app.route('/termos-de-servico')
def termos_de_servico():
    return render_template('tela_termos_de_servico.html')

@app.route('/politica-de-privacidade')
def politica_de_privacidade():
    return render_template('tela_politica_de_privacidade.html')

@app.route('/sobre-nos')
def sobre_nos():
    return render_template('tela_sobre_nos.html')

if __name__ == '__main__':
    app.run(debug=True)