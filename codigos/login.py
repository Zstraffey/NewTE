import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.uic import loadUi
import mysql.connector as mc
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import os

import random

import dashboard
import imgs_rc  # your resources
from codigos.classes import bancoDados

class EmailSender(QThread):
    finished = pyqtSignal(str)

    def __init__(self, receiver_email):
        super().__init__()
        self.receiver_email = receiver_email

    def run(self):
        try:
            passCode = random.randint(100000, 999999)

            sender_email = "newtetcc2025@gmail.com"
            app_password = "bboq pkqm nexm riyv"

            message = MIMEMultipart("related")
            message["From"] = sender_email
            message["To"] = self.receiver_email
            message["Subject"] = "New TE - Recuperação de Senha"

            html_content = f"""
            <html>
            <head>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                    }}
                    .header {{
                        background-color: #6a1b9a;  /* Cor de fundo roxa */
                        color: white;
                        padding: 20px;
                        text-align: center;
                        font-size: 24px;
                        font-weight: bold;
                    }}
                    .sub-header {{
                        font-size: 16px;
                        color: #333;
                        text-align: center;
                        margin-top: 10px;
                    }}
                    .code {{
                        font-size: 20px;
                        font-weight: bold;
                        color: #333;
                        background-color: #f0f0f0;
                        padding: 10px;
                        border-radius: 5px;
                    }}
                    .centered-img {{
                        display: block;
                        margin-left: auto;
                        margin-right: auto;
                        width: 5%; /* Ajuste a largura da imagem conforme necessário */
                    }}
                </style>
            </head>
            <body>
                <!-- Cabeçalho -->
                
               <img src="cid:logo_image" alt="Logo da Empresa" class="centered-img" />
               
                <div class="header">
                    New TE - Onboarding Digital
                </div>

                <!-- Subcabeçalho -->
                <div class="sub-header">
                    Requisição de Recuperação de Senha
                </div>

                <p>Este e-mail é automaticamente gerado, não responda. Se você não solicitou esta recuperação, por favor, ignore este e-mail</p>
                <p>O seu código de segurança é: <span class="code">{str(passCode)}</span></p>
            </body>
            </html>
            """

            message.attach(MIMEText(html_content, "html"))
            image_path = "../imagens/logo_new_te.png"
            if os.path.exists(image_path):
                with open(image_path, 'rb') as img_file:
                    img = MIMEImage(img_file.read())
                    img.add_header('Content-ID', '<logo_image>')
                    img.add_header('Content-Disposition', 'inline',filename="image.jpg")
                    message.attach(img)

            # Connect and send
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(sender_email, app_password)
                server.sendmail(sender_email, self.receiver_email, message.as_string())

            self.finished.emit("Email enviado! Aguarde...")

            print("oi")

            db = bancoDados().conectar()
            if not db:
                return

            cursor = db.cursor()

            query = f"""
                DELETE FROM recuperacao_senha WHERE email_usuario = '{self.receiver_email}';
            """
            cursor.execute(query)

            print("ola")

            query = f"""
                INSERT INTO recuperacao_senha
                (email_usuario, codigo) 
                VALUES ('{self.receiver_email}', '{passCode}');
            """
            cursor.execute(query)

            print("eba")

            db.commit()
            cursor.close()
            db.close()

        except Exception as e:
            self.finished.emit(f"Erro ao enviar: {str(e)}")
            print(f"Erro ao enviar: {str(e)}")

class Codigo(QMainWindow):
    def __init__(self, stacked_widget):
        super().__init__()
        loadUi("../design/inserir_codigo.ui", self)
        self.widget = stacked_widget

        self.trocar.clicked.connect(self.mudartela)

    def mudartela(self):
        createacc = EsqueciSenha(self.widget)
        self.widget.addWidget(createacc)
        self.widget.setCurrentIndex(self.widget.currentIndex() - 1)

class Login(QMainWindow):
    def __init__(self, stacked_widget):
        super().__init__()
        loadUi("../design/login.ui", self)
        self.widget = stacked_widget

        self.logar.clicked.connect(self.loginfunction)
        self.senha.setEchoMode(QtWidgets.QLineEdit.Password)
        self.trocar.clicked.connect(self.mudartela)

    def loginfunction(self):
        email = self.usuario.text()
        senha = self.senha.text()

        self.logarAplicativo()

        if not email or not senha:
            QMessageBox.warning(None, "Aviso", "Por favor, preencha todos os campos.")
            return

        db = bancoDados().conectar()
        if not db:
            return

        cursor = db.cursor()

        query = "SELECT email, senha FROM usuario WHERE email = %s AND senha = %s"
        cursor.execute(query, (email, senha))
        result = cursor.fetchone()

        if result is None:
            QMessageBox.warning(None, "Aviso", "Usuário ou senha incorretos.")
        else:
            QMessageBox.information(None, "Bem-Vindo!", "Logado com sucesso!")
            self.logarAplicativo()

        cursor.close()
        db.close()

    def mudartela(self):
        createacc = EsqueciSenha(self.widget)
        self.widget.addWidget(createacc)
        self.widget.setCurrentIndex(self.widget.currentIndex() + 1)

    def logarAplicativo(self):
        self.main = dashboard.TelaInicial(self.widget)
        self.main.show()
        self.widget.hide()

class EsqueciSenha(QMainWindow):
    def __init__(self, stacked_widget):
        super().__init__()
        loadUi("../design/senha.ui", self)
        self.widget = stacked_widget

        self.trocar.clicked.connect(self.trocartela)
        self.codigo.clicked.connect(self.telacodigo)
        self.enviar.clicked.connect(self.requisitarSenha)

    def requisitarSenha(self):
        def mudarTexto(text, color):
            return f'<html><head/><body><p align="center"><span style=" font-size:11pt; color:#{color};">{text}</span></p></body></html>'

        receiverEmail = self.usuario.text()
        if not receiverEmail:
            self.verificacao.setText(mudarTexto("Digite um email válido!", "ff0000"))
            return

        db = bancoDados().conectar()
        if not db:
            return

        cursor = db.cursor()
        query = f"SELECT email FROM usuario WHERE email = '{receiverEmail}'"
        cursor.execute(query)
        result = cursor.fetchone()

        if result is None:
            self.verificacao.setText(mudarTexto("Esse email não está cadastrado!", "ff0000"))
            return
        cursor.close()
        db.close()

        self.verificacao.setText(mudarTexto("Enviando Email...", "ffffff"))

        self.email_thread = EmailSender(receiverEmail)
        self.email_thread.finished.connect(lambda msg: self.verificacao.setText(mudarTexto(msg, "9999ff")))
        self.email_thread.start()

    def trocartela(self):
        login = Login(self.widget)
        self.widget.addWidget(login)
        self.widget.setCurrentIndex(self.widget.currentIndex() - 1)

    def telacodigo(self):
        login = Codigo(self.widget)
        self.widget.addWidget(login)
        self.widget.setCurrentIndex(self.widget.currentIndex() + 1)


def main():
    app = QApplication(sys.argv)

    stacked_widget = QtWidgets.QStackedWidget()
    stacked_widget.setFixedSize(900, 540)

    login_screen = Login(stacked_widget)
    stacked_widget.addWidget(login_screen)
    stacked_widget.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
