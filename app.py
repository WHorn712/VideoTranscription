from flask import Flask, render_template
import pymysql
from flask import request, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

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
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']  # Certifique-se de hash a senha aqui
        repeatpassword = request.form['passwordrepeat']
        typeSignature = 0

        if password != repeatpassword:
            return "POR FAVOR, REPITA A MESMA SENHA"

        connection = get_db_connection()
        with connection.cursor() as cursor:
            # Busca o usuário pelo email
            cursor.execute('SELECT senha FROM users WHERE email = %s', (email,))
            user = cursor.fetchone()
        connection.close()

        if user:
            return 'E-MAIL EXISTENTE'

        hashed_senha = generate_password_hash(password, method='pbkdf2:sha256')

        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute('INSERT INTO users (nome, email, senha, typeSignature) VALUES (%s, %s, %s, %s)',
                           (name, email, hashed_senha, typeSignature))
            connection.commit()
        connection.close()
        return redirect(url_for('index'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        connection = get_db_connection()
        with connection.cursor() as cursor:
            # Busca o usuário pelo email
            cursor.execute('SELECT senha FROM users WHERE email = %s', (email,))
            user = cursor.fetchone()
        connection.close()

        if user and check_password_hash(user[0], password):
            # Lógica de sucesso no login
            return 'Logged in successfully'
        else:
            # Lógica de falha no login
            return 'Invalid credentials'
    return render_template('login.html')


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