import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QDialog, QApplication, QMainWindow, QMessageBox
from PyQt5.uic import loadUi

import dashboard
import mysql.connector as mc

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
        # try:
            email = self.usuario.text()
            senha = self.senha.text()

            if email == "" or senha == "":
                QMessageBox.warning(None, "oi", "Por favor, preencha todos os campos.")
                return

            self.logarAplicativo()


            # mydb = mc.connect(
                #    host="localhost",
                # user="root",
                # password="",
                # database="newte",
                # use_pure=True
            # )

            # mycursor = mydb.cursor()
            # query = "SELECT email, senha from usuario where email like '" + email + "' and senha like '" + senha + "'"
            # mycursor.execute(query)

            # result = mycursor.fetchone()

            #if result == None:
            #    QMessageBox.warning(None, "oi", "Usuário ou senha incorretos.")
            #else:
            #    QMessageBox.information(None, "oi", "Logado com sucesso!")

            #except mc.Error as e:
                #  (
            #    QMessageBox.warning(None, "oi", f'Erro ao conectar no banco de dados.'))

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
        #self.logar.clicked.connect()
        self.trocar.clicked.connect(self.trocartela)

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