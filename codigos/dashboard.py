import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QDialog, QApplication, QMainWindow, QMessageBox, QWidget
from PyQt5.uic import loadUi

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import mysql.connector as mc

import imgs_rc

sender_email = "newtetcc2025@gmail.com"
app_password = "bboq pkqm nexm riyv"
receiver_email = "migmig.zimmer@gmail.com"

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

class TelaInicial(QMainWindow):
    def __init__(self):
        super(TelaInicial,self).__init__()
        loadUi("../design/NOVODASH.ui",self)

        self.stack = self.findChild(QWidget, "stackedwidget_btns_da_sidebar")
        #self.stackList = {"btn_home", "btn_chat","btn_config","btn_cadastro","btn_perfil"}

        #for i, botao in enumerate(self.stackList, start=0):
        #    print(i, botao)
        #    botao.clicked.connect(lambda: self.mudarTela(i))

        self.btn_home.clicked.connect(lambda: self.mudarTela(0))
        self.btn_chat.clicked.connect(lambda: self.mudarTela(1))
        self.btn_config.clicked.connect(lambda: self.mudarTela(2))
        self.btn_cadastro.clicked.connect(lambda: self.mudarTela(3))
        self.btn_perfil.clicked.connect(lambda: self.mudarTela(4))

        self.dashboardStack = self.findChild(QWidget, "stacked_widget_botoes_principais_do_dashboard")
        self.btn_rendimento_do_dash.clicked.connect(lambda : self.mudarDashboard(0))
        self.btn_func_do_dash.clicked.connect(lambda: self.mudarDashboard(1))
        self.btn_calendario_do_dash.clicked.connect(lambda: self.mudarDashboard(2))

    def mudarTela(self, index):
        self.stack.setCurrentIndex(index)

    def mudarDashboard(self, index):
        self.dashboardStack.setCurrentIndex(index)