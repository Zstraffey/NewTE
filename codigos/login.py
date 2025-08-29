import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.uic import loadUi
import mysql.connector as mc
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import dashboard
import imgs_rc  # your resources


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

        try:
            mydb = mc.connect(
                host="localhost",
                user="root",
                password="",
                database="newte",
                use_pure=True
            )
            mycursor = mydb.cursor()
            query = "SELECT email, senha FROM usuario WHERE email = %s AND senha = %s"
            mycursor.execute(query, (email, senha))
            result = mycursor.fetchone()

            if result is None:
                QMessageBox.warning(None, "Aviso", "Usuário ou senha incorretos.")
            else:
                QMessageBox.information(None, "Bem-Vindo!", "Logado com sucesso!")
                self.logarAplicativo()

        except mc.Error:
            QMessageBox.warning(None, "Erro", "Erro ao conectar no banco de dados.")

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
        self.enviar.clicked.connect(self.requisitarSenha)

    def requisitarSenha(self):
        def mudarTexto(text, color):
            return f'<html><head/><body><p align="center"><span style=" font-size:11pt; color:#{color};">{text}</span></p></body></html>'

        self.verificacao.setText(mudarTexto("Enviando Email...", "ffffff"))

        sender_email = "newtetcc2025@gmail.com"
        app_password = "bboq pkqm nexm riyv"
        receiver_email = self.usuario.text()

        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = "Test Email from Python"
        message.attach(MIMEText("Hello! This is a test email sent from Python.", "plain"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, app_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
            self.verificacao.setText(mudarTexto("Email enviado!", "9999ff"))

    def trocartela(self):
        login = Login(self.widget)
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
