import mysql.connector as mc
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QWidget, QPushButton, QMessageBox
from PyQt5.uic import loadUi

class usuarioChat(QWidget):
    def __init__(self, username):#, callback):
        super().__init__()
        loadUi("../design/templates/contatos.ui", self)  # your .ui file with a QPushButton

        self.nome_salvo.setText(username)
        # Connect the button to shared callback with username
        # self.pushButton.clicked.connect(lambda: callback(username))

class bancoDados:
    def __init__(self):
        print("inicializado banco de dados")

    def conectar(self):

        try:
            mydb = mc.connect(
                host="localhost",
                user="root",
                password="",
                database="newte",
                use_pure=True
            )

            return mydb
        except mc.Error:
            QMessageBox.warning(None, "Erro", "Erro ao conectar no banco de dados.")

            return False