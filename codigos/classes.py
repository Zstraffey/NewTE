import mysql.connector as mc
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QWidget, QPushButton, QMessageBox, QLabel, QSizePolicy, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.uic import loadUi

class Session:
    current_user = None
    loaded_chat = 0

class ChatBubble(QWidget):
    def __init__(self, text, layout, sender="me", max_width=400):
        super().__init__()
        label = QLabel(text)
        label.setWordWrap(True)
        label.setMaximumWidth(max_width)  # wrap text at this width
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        if sender == "me":
            label.setStyleSheet("background-color: lightgreen; padding: 8px; border-radius: 10px; color: black;")
            layout.addStretch()  # pushes bubble up
            layout.addWidget(label, alignment=Qt.AlignRight)
        else:
            label.setStyleSheet("background-color: lightblue; padding: 8px; border-radius: 10px; color: black;")
            layout.addWidget(label, alignment=Qt.AlignLeft)
            layout.addStretch()  # pushes bubble down if needed

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