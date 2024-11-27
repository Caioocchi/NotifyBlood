from flask import Flask, render_template, redirect, request, flash, jsonify
import smtplib
import email.message
from twilio.rest import Client
import mysql.connector
import google.generativeai as genai

#----- Gemini -----
genai.configure(api_key="AIzaSyBzr-8ES6ErKJySXloTtXio1U02crY3jAM")
model = genai.GenerativeModel("gemini-1.5-flash")

#----- Twilio - SMS/Whatsapp -----
sid = "sua sid"
token = "seu token"
client = Client(sid, token)

#----- Flask -----
app = Flask(__name__)
app.config['SECRET_KEY'] = 'NOTIFYBLOOD'

#----- conecta os arquivos css e imagens -----
app.static_url_path = '/static'
app.static_folder = 'static'

#----- VARIÁVEIS E FUNÇÕES GLOBAIS -----
logado = False

chat = model.start_chat(history=[])
chat.send_message("Você irá entrevistar um usuário com apenas perguntas de sim ou não, uma por vez, para saber se ele está apto para doar sangue. No fim, informe apenas APTO ou INAPTO. Aguarde o usuário digitar ok para começar.")


#----- Conexão banco de dados -----
connectBD = mysql.connector.connect(host='localhost', database='notifyblood_banco', user='root', password='')

#----- info email -----
msg = email.message.Message()
s = smtplib.SMTP('smtp.gmail.com: 587')
password = 'qsfwkxldnotyfgxc'
msg['From'] = 'notifyblood@gmail.com'

#----- notificacao pelo tipo sanguineo -----
def notificacao(tipo_sanguineo, local, sangue):
    if connectBD.is_connected():
        cursor = connectBD.cursor()
        cursor.execute('select * from usuario;')
        usuarios = cursor.fetchall()
    
    if tipo_sanguineo < "35":
            cont = 0
            for user in usuarios:
                cont += 1
                if str(user[5]) == sangue:

                    #envio de Whatsapp
                    # client.messages.create(from_='whatsapp:+14155238886', body=f"NotifyBlood: {str(user[1])}, estamos precisando da sua doação! Por favor, quando for possível se direcionar ao endereço: {local}", to="whatsapp:+55"+str(user[3]))

                    #envio de email
                    corpo_email = f"""
                    <p>Olá, {str(user[1])}!</p>
                    <p>Estamos precisando da sua doação!</p>
                    <p>Por favor, quando for possível se direcionar ao endereço: {local}</p>
                    <br>
                    <p>Qualquer dúvida entre em contato!</p>
                    <p>Telefone: (27) 9 9905-5593</p>
                    <p>Email: notifyblood@gmail.com</p>
                    """

                    msg['Subject'] = f"Precisamos da sua doação, {str(user[1])}!"
                    msg['To'] = str(user[2])
                    msg.add_header('Content-Type', 'text/html')
                    msg.set_payload(corpo_email)
                    
                    s.starttls()
                    s.login(msg['From'], password)
                    s.sendmail(msg['From'], [msg['To']], msg.as_string().encode('utf-8'))
                    
                if cont >= len(usuarios):
                    break
                
#----- HOME C/ CHAT -----
@app.route('/')
def home():
    global logado
    logado = False
    return render_template('FrontEnd_chat.html')

#----- HOME C/ CADASTRO -----
@app.route('/home_cadastro')
def home_cadastro():
    global logado
    logado = False
    return render_template('FrontEnd.html')

#----- CONTATOS -----
@app.route('/contatos', methods=['GET', 'POST'])
def contatos():
    if request.method == 'POST':
        nome_contato = request.form.get('name_contato')
        email_contato = request.form.get('email_contato')
        mensagem_contato = request.form.get('mensagem_contato')
        telefone_contato = request.form.get('telefone_contato')

#envio das informações de contato para email
        corpo_email = f"""
        <p>Nome: {nome_contato}</p>
        <p>Email: {email_contato}</p>
        <p>Telefone: {telefone_contato}</p>
        <p>Mensagem: {mensagem_contato}</p>
        """

        msg['Subject'] = f"Contato/dúvida de {nome_contato}"
        msg['To'] = 'notifyblood@gmail.com'
        msg.add_header('Content-Type', 'text/html')
        msg.set_payload(corpo_email)

        s.starttls()
        s.login(msg['From'], password)
        s.sendmail(msg['From'], [msg['To']], msg.as_string().encode('utf-8'))

#envio de informações para o banco de dados
        if connectBD.is_connected():
            cursor = connectBD.cursor()
            cursor.execute(f"insert into contato values (default, '{nome_contato}', '{email_contato}', '{mensagem_contato}', '{telefone_contato}');")
            
        if connectBD.is_connected():
            cursor.close()
            
        flash('Mensagem enviada com sucesso!')
        return redirect('/')

#----- CADASTRO -----
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    global logado
    if request.method == 'POST':
        email_cadastro = request.form.get('email')
        name = request.form.get('name')
        idade = request.form.get('idade')
        sangue = request.form.get('sangue')
        telefone = request.form.get('telefone')
        sexo = request.form.get('sexo')

#login de administrador
        if email_cadastro == 'admin@admin' and name == 'admin' and telefone == '99999999999':
            logado = True
            return render_template('admin.html')

#verifica se email ou telefone ja estao cadastrados
        if connectBD.is_connected():
            cursor = connectBD.cursor()
            cursor.execute('select * from usuario;')
            usuarios = cursor.fetchall()
            cont = 0
            for user in usuarios:
                cont += 1
                if str(user[2]) == email_cadastro:
                    flash("Email ja cadastrado")
                    return redirect('/')
                
                if str(user[3]) == telefone:
                    flash("Telefone ja cadastrado")
                    return redirect('/')

#cadastro do usuario no banco de dados
        if connectBD.is_connected():
            cursor = connectBD.cursor()
            cursor.execute(f"insert into usuario values (default, '{name}', '{email_cadastro}', '{telefone}', '{idade}', '{sangue}', '{sexo}');")

#envio das informações de contato para email
            corpo_email = f"""
            <p>Olá, {name}!</p>
            <p>Estamos muito felizes que você resolveu participar do nosso projeto!</p>
            <p>Fique atento às notificações que enviamos, através dela você saberá quando estivermos precisando de doação.</p>
            <br>
            <p>Qualquer dúvida entre em contato!</p>
            <p>Telefone: (27) 9 9905-5593</p>
            <p>Email: notifyblood@gmail.com</p>
            """

            msg['Subject'] = f"Bem-vindo ao NotifyBlood, {name}!"
            msg['To'] = email_cadastro
            msg.add_header('Content-Type', 'text/html')
            msg.set_payload(corpo_email)

            s.starttls()
            s.login(msg['From'], password)
            s.sendmail(msg['From'], [msg['To']], msg.as_string().encode('utf-8'))

        if connectBD.is_connected():
            cursor.close()
            
        flash(f"Cadastro realizado com sucesso! Seja bem-vindo(a), {name}")    
        return redirect('/')

#----- ADMIN -----
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    Ap = request.form.get('A+')
    An = request.form.get('A-')
    Bp = request.form.get('B+')
    Bn = request.form.get('B-')
    ABp = request.form.get('AB+')
    ABn = request.form.get('AB-')
    Op = request.form.get('O+')
    On = request.form.get('O-')
    local = request.form.get('local')

    if connectBD.is_connected():
        cursor = connectBD.cursor()
        cursor.execute('select * from usuario;')
        usuarios = cursor.fetchall()

#envio de notificação
    #A+    
    notificacao(Ap, local, "A+")

    #A-    
    notificacao(An, local, "A-")

    #B+    
    notificacao(Bp, local, "B+")

    #B-    
    notificacao(Bn, local, "B+")

    #AB+    
    notificacao(ABp, local, "AB+")

    #AB-    
    notificacao(ABn, local, "AB-")

    #O+    
    notificacao(Op, local, "O+")

    #O-    
    notificacao(On, local, "O-")

    flash("ATUALIZADO COM SUCESSO")
    return redirect('/')

#----- CHAT -----
@app.route('/send_message', methods=['GET', 'POST'])
def send_message():    
    # Obtém a mensagem do usuário enviada pelo frontend
    user_message = request.json.get('message')
    ai_message = chat.send_message(user_message).text
    print(ai_message)
    
    try:    
        if ai_message.strip().upper() == "INAPTO":
            flash('Você não está apto para doar sangue.')
            return jsonify({'redirect': '/'})
        
        if ai_message.strip().upper() == "APTO":
            flash('VOCÊ ESTÁ APTO PARA SALVAR VIDAS! CLIQUE EM CADASTRO E REALIZE O SEU.')
            return jsonify({'redirect': 'home_cadastro'})
    
        else:
            return jsonify({'message': ai_message})
    except Exception as e:
        # Retorna erro caso algo dê errado
        return jsonify({'error': str(e)}), 500

#----- HOST DO SITE -----    
if __name__ == '__main__':
    app.run(debug=True)
