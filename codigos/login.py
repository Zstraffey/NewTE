import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QDialog, QApplication, QMainWindow, QMessageBox
from PyQt5.uic import loadUi

import dashboard
import mysql.connector as mc

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import imgs_rc

class Login(QMainWindow):
    def __init__(self):
        super(Login,self).__init__()
        loadUi("../design/login.ui",self)
        self.logar.clicked.connect(self.loginfunction)
        self.senha.setEchoMode(QtWidgets.QLineEdit.Password)

        self.trocar.clicked.connect(self.mudartela)
        #self.createaccbutton.clicked.connect(self.gotocreate)

    def loginfunction(self):
        try:
            email = self.usuario.text()
            senha = self.senha.text()

            if email == "" or senha == "":
                QMessageBox.warning(None, "Aviso", "Por favor, preencha todos os campos.")
                return

            mydb = mc.connect(
                host="localhost",
                user="root",
                password="",
                database="newte",
                use_pure=True
            )

            mycursor = mydb.cursor()
            query = "SELECT email, senha from usuario where email like '" + email + "' and senha like '" + senha + "'"
            mycursor.execute(query)

            result = mycursor.fetchone()

            if result == None:
                QMessageBox.warning(None, "Aviso", "Usuário ou senha incorretos.")
            else:
                QMessageBox.information(None, "Bem-Vindo!", "Logado com sucesso!")
                self.logarAplicativo()


        except mc.Error as e:
            (
                QMessageBox.warning(None, "Erro", f'Erro ao conectar no banco de dados.'))

    def mudartela(self):
        createacc=EsqueciSenha()
        widget.addWidget(createacc)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def logarAplicativo(self):
        self.main = dashboard.TelaInicial()
        self.main.show()

        # Close this login window
        widget.close()

class EsqueciSenha(QMainWindow):
    def __init__(self):
        super(EsqueciSenha,self).__init__()
        loadUi("../design/senha.ui",self)
        self.trocar.clicked.connect(self.trocartela)
        self.enviar.clicked.connect(self.requisitarSenha)

    def requisitarSenha(self):
        def mudarTexto(text, color):
            return f'<html><head/><body><p align="center"><span style=" font-size:11pt; color:#{color};">{text}</span></p></body></html>'

        self.verificacao.setText(mudarTexto("Enviando Email...", "ffffff"))

        sender_email = "newtetcc2025@gmail.com"
        app_password = "bboq pkqm nexm riyv"
        receiver_email = self.usuario.text()

        # Create the email
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = "Test Email from Python"

        # Email body
        body = "Hello! This is a test email sent from Python."
        message.attach(MIMEText(body, "plain"))

        # Connect to Gmail SMTP server
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, app_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
            self.verificacao.setText(mudarTexto("Email enviado!", "9999ff"))

    def trocartela(self):
        login=Login()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainwindow = Login()
    widget = QtWidgets.QStackedWidget()
    widget.addWidget(mainwindow)
    widget.setFixedWidth(900)
    widget.setFixedHeight(540)
    widget.show()
    app.exec_()