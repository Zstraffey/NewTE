import mysql.connector as mc
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox


def conectar():

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


class bancoDados:
    #def __init__(self):
    #    print("inicializado")

    pass