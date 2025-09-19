import mysql.connector as mc
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QWidget, QPushButton, QMessageBox, QLabel
from PyQt5.QtCore import Qt
from PyQt5.uic import loadUi

class Session:
    current_user = None
    loaded_chat = 0

class ChatBubble(QWidget):
    def __init__(self, text, layout, sender="me"):
        super().__init__()

        label = QLabel(text)
        label.setWordWrap(True)
        label.setStyleSheet("""
            QLabel {
                border-radius: 10px;
                padding: 8px;
                font-size: 14px;
            }
        """)

        if sender == "me":
            # Align right
            layout.addStretch()
            label.setStyleSheet(label.styleSheet() +
                                "background-color: lightgreen;")
            layout.addWidget(label, alignment=Qt.AlignRight)
        else:
            # Align left
            label.setStyleSheet(label.styleSheet() +
                                "background-color: lightblue;")
            layout.addWidget(label, alignment=Qt.AlignLeft)
            layout.addStretch()

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