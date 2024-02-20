from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os
import pandas as pd

app = Flask(__name__)

# Tipos de arquivo que dá pra salvar
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'xlsx'}

# Adicionar usuarios
users = {
    'F8089947': '10092001Ale.',
    'F8084120': '@Amova071212',
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    if username in users and users[username] == password:
        return redirect(url_for('formulario'))
    else:
        return render_template('login.html', error='Nome de usuário ou senha incorretos.')

@app.route('/formulario')
def formulario():
    return render_template('formulario.html')

def get_next_filename(folder, base_name, extension):
    i = 1
    while True:
        filename = f"{base_name}{i}.{extension}"
        filepath = os.path.join(folder, filename)
        if not os.path.exists(filepath):
            return filename
        i += 1

@app.route('/processar_formulario', methods=['POST'])
def processar_formulario():
    meses = request.form.getlist('meses')
    consumo_energia = float(request.form['consumo_energia_mercado_livre'])
    producao_energia = float(request.form['producao_energia_gd'])
    total_kwh = float(request.form['total_kwh_2022'])

    # Criar um DataFrame com os dados do formulário
    dados_formulario = {
        'Meses': meses,
        'Consumo de Energia Mercado Livre': [consumo_energia],
        'Produção de Energia GD': [producao_energia],
        'Total KWh 2022': [total_kwh]
    }
    df_formulario = pd.DataFrame(dados_formulario)

    # Verificar se um arquivo é anexado e salvar
    if 'arquivo' in request.files:
        arquivo = request.files['arquivo']
        if arquivo.filename != '' and allowed_file(arquivo.filename):
            filename = secure_filename(arquivo.filename)
            arquivo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            arquivo.save(arquivo_path)
            print(f'Arquivo salvo em: {arquivo_path}')

    # Obter o próximo nome de arquivo de sequencia para o arquivo Excel
    base_name = 'Dados'
    extension = 'xlsx'
    next_filename = get_next_filename(app.config['UPLOAD_FOLDER'], base_name, extension)
    excel_path = os.path.join(app.config['UPLOAD_FOLDER'], next_filename)
    df_formulario.to_excel(excel_path, index=False)
    print(f'Dados salvos em: {excel_path}')

    return 'Processo Concluído!'

if __name__ == '__main__':
    app.run(debug=True)