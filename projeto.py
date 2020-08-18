#para a base de dados
import psycopg2
#para o servidor
import socket
import time

#-------------------------------def do servidor----------------------------

def ask(frase,client):
    message = ""
    client.send(bytes(frase, "utf-8"))
    while True:
        resp = client.recv(20)
        x = resp.decode("utf-8")
        if(x == "\r\n"):
            return message
        message = message + x

def manda(frase,client):
    client.send(bytes(frase+"\r\n","utf-8"))

#-------------------------------def da Base de dados----------------------------

def validacao(item):
    if item == ' ':
        return False
    try:
        item = int(item)
    except:
        return False
    return True

def login(client):
    cur = conn.cursor()
    manda('\r\n\r\n--- LOGIN ---\r\n', client)
    user = ask("Escreva o seu email: ",client)
    password = ask("\r\nDigite sua senha: ",client)
    print(user)
    print (password)

    cur.execute("select ncliente from cliente where utilizador_email= %s and utilizador_password = %s", (user, password))
    resultado = cur.fetchone()

    if (resultado != None):
        id_cliente = resultado
        cur.close()
        menu_cliente(id_cliente,client)

    cur.execute("select nadministrador from administrador where utilizador_email= %s and utilizador_password = %s", (user, password))
    resultado = cur.fetchone()

    if (resultado != None):
        id_adm = resultado
        cur.close()
        menu_adm(id_adm,client)

    manda("\r\n\r\nlogin invalido! Tente novamente",client)
    cur.close()
    login(client)

#-------------------------------def do admin----------------------------

def menu_adm(id_adm,client):
    cur = conn.cursor()
    manda("\r\n--- MENU DO ADMINISTRADOR --- \r\n",client)
    manda('''[1] Adicionar utilizador \r\n[2] Remover utilizador\r\n[3] Logout\r\n''',client)

    opcao = ask('>>>> Qual e sua opcao? ',client)
    if (validacao(opcao) == True):
        print(opcao)
        opcao = int(opcao)
        print(opcao)
        if opcao == 1:
            cur.close
            registro(id_adm,client)
        elif opcao == 2:
            cur.close()
            remover_utilizador(id_adm,client)
        elif opcao == 3:
            cur.close()
            login(client)
        else:
            manda("\r\nOOOOOPS!! Opcao invalida. Tente Novamente",client)
            cur.close()
            menu_adm(id_adm,client)
    else:
        manda("\r\nOOOOOPS!! Opcao invalida. Tente Novamente",client)
        cur.close()
        menu_adm(id_adm,client)

def remover_utilizador(id_adm,client):
    cur = conn.cursor()
    manda("--- REGISTRO ---",client)
    email = ask('''Escreva o endereco de email a ser desassociado: \r\nSe quiser voltar ao menu, digite '*'  ''',client)

    if (email == '*'):
        cur.close()
        menu_adm(id_adm,client)

    cur.execute("SELECT ncliente FROM cliente WHERE utilizador_email = %s", (email,))
    ncliente = cur.fetchone()
    if (ncliente == None):
        manda("Endereco de email nao existe. Insira um email valido",client)
        cur.close()
        remover_utilizador(id_adm,client)
    else:
        cur.execute("DELETE FROM cliente WHERE ncliente = %s ", (ncliente))
        conn.commit()
        cur.close()
        manda("O utilizador foi removido",client)
        c = ask("Carregue qualquer tecla voltar ao menu do administrador",client)
        menu_adm(id_adm,client)

def registro(id_adm,client):
    cur = conn.cursor()
    manda("--- REGISTRO ---\r\n", client)
    email = ask('''Escreva o endereco de email a ser associado: \r\nSe quiser voltar ao menu, digite '*'  ''',client)

    if(email=='*'):
        cur.close()
        login(client)
    while len(email) < 8:
        manda("Escreva um endereco de email valido deve conter 8 ou mais caracteres", client)
        email = ask("Escreva o endereco de email a ser associado:",client)
    cur.execute("SELECT utilizador_email FROM cliente WHERE utilizador_email = %s", (email,))
    conferencia = cur.fetchone()
    if (conferencia != None):
        manda("Endereco de email ja cadastrado. Insira um email valido",client)
        cur.close()
        registro(client)
    else:
        senha = ask("Insira uma senha com ao menos 5 caracteres",client)
        while len(senha) < 4 :
            manda("Escreva uma senha valida",client)
            senha = str(ask("Insira uma senha com ao menos 5 caracteres"))
        cur.execute("INSERT INTO cliente(utilizador_email, utilizador_password) " "VALUES (%s, %s)", (email, senha))
        conn.commit()
        cur.close()
        manda("Cliente registrado",client)
        menu_adm(id_adm,client)

#-------------------------------def do cliente----------------------------

def menu_cliente(id_cliente,client):
    cur = conn.cursor()
    manda('\r\n\r\n--- MENU CLIENTE ---\r\n',client)
    manda('''[1] Consultar Mensagem\r\n[2] Enviar Mensagem\r\n[3] Logout\r\n''',client)
    opcao = ask('>>>> Qual e sua opcao? ',client)
    if (validacao(opcao) == True):
        opcao = int(opcao)
        if opcao == 1:
            cur.close()
            consultar_mensagem(id_cliente,client)
        elif opcao == 2:
            cur.close()
            enviar_mensagem(id_cliente,client)
        elif opcao == 3:
            cur.close()
            login(client)
        else:
            manda("OOOOOPS!! Opcao invalida. Tente Novamente",client)
            cur.close()
            menu_cliente(id_cliente,client)
    elif (validacao(opcao) == False):
        manda("OOOOOPS!! Opcao invalida. Tente Novamente",client)
        cur.close()
        menu_cliente(id_cliente,client)

def enviar_mensagem(id_cliente,client):

    manda('\r\n\r\n--- ENVIAR MENSAGEM ---\n\r', client)
    conteudo = ask("Escreva a Mensagem a ser enviada:\r\n\r\n",client)
    qnt=ask("Para quantos destinatarios deseja enviar?", client)
    qnt=int(qnt)

    for i in range(0, qnt):
        cur = conn.cursor()
        email_destino = ask("\r\n\r\nQuem devera receber esta mensagem?",client)
        cur.execute("select ncliente from cliente where utilizador_email = %s",(email_destino,))
        ncliente_destino = cur.fetchone()
        if(ncliente_destino == None):
            manda("Este email nao existe. Digite um que seja valido",client)
            cur.close()
            enviar_mensagem(id_cliente,client)

        ncliente_destino = ncliente_destino[0]
        cur.execute("INSERT INTO mensagem(text_msg, lido, remetente, destinatario) "
                    "VALUES (%s, %s, %s, %s)", (conteudo, False, id_cliente, ncliente_destino))
        conn.commit()

    manda("\r\n\r\nMENSAGEM ENVIADA",client)
    cur.close()
    menu_cliente(id_cliente,client)

def consultar_mensagem(id_cliente,client):
    cur = conn.cursor()
    manda('\r\n\r\n--- CONSULTA DE MENSAGEM ---\r\n', client)
    manda('''[1] Lidas\r\n[2] Nao lidas\r\n[3] Apagar mensagem lida\r\n[4] Voltar\r\n''',client)
    opcao = ask('Qual e sua opcao: ',client)
    if (validacao(opcao) == True):
        opcao = int(opcao)
        if opcao == 1:
            cur.close()
            ler_msglidas(id_cliente,client)
        elif opcao == 2:
            cur.close()
            ler_mensagens_naolidas(id_cliente,client)
        elif opcao == 3:
            cur.close()
            apagar_msg_lidas(id_cliente,client)
        elif opcao == 4:
            cur.close()
            menu_cliente(id_cliente,client)
        else:
            manda("Escolha uma Opcao Valida!",client)
            cur.close()
            consultar_mensagem(id_cliente,client)
    elif (validacao(opcao) == False):
        manda("OOOOOPS!! Opcao invalida. Tente Novamente",client)
        cur.close()
        consultar_mensagem(id_cliente,client)

def ler_msglidas (id_cliente,client):
    cur = conn.cursor()
    manda("\r\n\r\n--- MENSAGENS LIDAS ---\r\n",client)
    cur.execute("select mensagem.id from mensagem where lido = %s and destinatario = %s", (True, id_cliente,))
    numero_mensagens = cur.fetchone()
    if numero_mensagens == None:
        manda("Nao ha mensagens ja lidas",client)
        b = ask("\r\nPressione qualquer tecla para voltar a Consultar Mensagens!",client)
        cur.close()
        consultar_mensagem(id_cliente,client)

    cur.execute("select mensagem.id from mensagem where lido = %s and destinatario = %s ", (True, id_cliente,))
    for linha in cur.fetchall():
        x = str( linha[0] )
        manda(x,client)
    n_mensagem = ask("\r\nQual mensagem voce deseja ler?",client)

    while ((validacao(n_mensagem) == False)):
        manda("Insira uma opcao valida!!",client)
        n_mensagem = ask("Qual mensagem desejas ler?",client)

    cur.execute("select remetente from mensagem where id = %s ", (n_mensagem,))
    n_remetente = cur.fetchone()

    if n_remetente == None:
        manda("Tal mensagem nao existe!!",client)
        cur.close()
        ler_msglidas(id_cliente,client)


    cur.execute("select utilizador_email from cliente where ncliente = %s ", (n_remetente,))
    email_remetente = cur.fetchone()
    manda("O remetente da mensagem e: \r\n",client)
    manda(email_remetente[0],client)

    cur.execute("select text_msg from mensagem where id = %s", (n_mensagem,))
    texto = cur.fetchone()
    manda("\r\nO corpo do texto e:", client)
    manda(texto[0],client)

    cur.close()
    b = ask("\r\nPressione qualquer tecla para voltar a Consultar Mensagens!",client)
    cur.close()
    consultar_mensagem(id_cliente,client)

def ler_mensagens_naolidas(id_cliente,client):
    manda("\r\n\r\n--- MENSAGENS NAO LIDAS ---\r\n",client)
    cur = conn.cursor()

    cur.execute("select mensagem.id from mensagem where lido = %s and destinatario = %s", (False, id_cliente,))
    numero_mensagens = cur.fetchone()
    if numero_mensagens == None:
        manda("Nao ha mensagens nao lidas",client)
        b = ask("Pressione qualquer tecla para voltar a Consultar Mensagens!",client)
        cur.close()
        consultar_mensagem(id_cliente,client)

    cur.execute("select mensagem.id from mensagem where lido = %s and destinatario = %s ", (False, id_cliente,))
    for linha in cur.fetchall():
        x = str( linha[0] )
        manda(x,client)

    n_mensagem = ask("Qual mensagem voce deseja ler?",client)

    while ((validacao(n_mensagem) == False)):
        manda("Insira uma opcao valida!!",client)
        n_mensagem = ask("Qual mensagem desejas ler?",client)

    cur.execute("select remetente from mensagem where id = %s ", (n_mensagem,))
    n_remetente = cur.fetchone()

    if n_remetente == None:
        manda("Tal mensagem nao existe!!",client)
        cur.close()
        ler_mensagens_naolidas(id_cliente,client)

    cur.execute("select utilizador_email from cliente where ncliente = %s ", (n_remetente,))
    email_remetente = cur.fetchone()
    manda("\r\n\r\nO remetente da mensagem e: ",client)
    manda( email_remetente[0],client)

    cur.execute("select text_msg from mensagem where id = %s", (n_mensagem,))
    texto = cur.fetchone()
    manda("\n\rO corpo do texto e:\r\n",client)
    manda( texto[0],client)
    cur.execute("UPDATE mensagem SET lido = True WHERE id = %s ", (n_mensagem,))
    cur.close()
    b = ask("\r\nPressione qualquer tecla para voltar a Consultar Mensagens!\r\n",client)
    consultar_mensagem(id_cliente,client)

def apagar_msg_lidas (id_cliente,client):
    cur = conn.cursor()
    manda("\r\n\r\n--- APAGAR MENSAGENS LIDAS ---\r\n",client)
    cur.execute("select mensagem.id from mensagem where lido = %s and destinatario = %s", (True, id_cliente,))
    numero_mensagens = cur.fetchone()
    if numero_mensagens == None:
        manda("Nao ha mensagens ja lidas",client)
        b = ask("\r\nPressione qualquer tecla para voltar a Consultar Mensagens!",client)
        cur.close()
        consultar_mensagem(id_cliente,client)

    cur.execute("select mensagem.id from mensagem where lido = %s and destinatario = %s ", (True, id_cliente,))
    for linha in cur.fetchall():
        x = str( linha[0] )
        manda(x,client)
    n_mensagem = ask("\r\nQual mensagem voce deseja apagar?",client)

    while ((validacao(n_mensagem) == False)):
        manda("Insira uma opcao valida!!",client)
        n_mensagem = ask("Qual mensagem desejas apagar?",client)

    cur.execute("select remetente from mensagem where id = %s ", (n_mensagem,))
    n_remetente = cur.fetchone()

    if n_remetente == None:
        manda("Tal mensagem nao existe!!",client)
        cur.close()
        ler_msglidas(id_cliente,client)


    cur.execute("select utilizador_email from cliente where ncliente = %s ", (n_remetente,))
    email_remetente = cur.fetchone()
    manda("O remetente da mensagem e: \r\n",client)
    manda(email_remetente[0],client)

    cur.execute("select text_msg from mensagem where id = %s", (n_mensagem,))
    texto = cur.fetchone()
    manda("\r\nO corpo do texto e:", client)
    manda(texto[0],client)



    b = ask("\r\nPressione qualquer tecla para apagar a mensagem",client)
    cur.execute("DELETE FROM mensagem WHERE id = %s ", (n_mensagem,))
    manda("\r\nMENSAGEM APAGADA", client)
    cur.close()
    consultar_mensagem(id_cliente,client)

#comunicação com a base de dados

conn = psycopg2.connect("host=localhost dbname=RC user=postgres password=postgres")

#liga o servidor

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("127.0.0.1", 1234))
s.listen()
print("on-line \r\n")

#executa o programa

while True:

    clientsocket, address = s.accept()
    print (f"Connection from {address} has been established.")

    manda("Welcome to the server! \r\n", clientsocket)

    while True:
        login(clientsocket)


