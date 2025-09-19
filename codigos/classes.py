import mysql.connector as mc
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QWidget, QPushButton, QMessageBox, QLabel, QSizePolicy, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.uic import loadUi

class Session:
    current_user = None
    loaded_chat = 0

class ChatBubble(QWidget):
    def __init__(self, text, sender="me", max_width=300):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        label = QLabel(text)
        label.setWordWrap(True)
        label.setMaximumWidth(max_width)
        label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        # Styling
        if sender == "me":
            label.setStyleSheet("""
                QLabel { background-color: lightgreen; padding: 8px; border-radius: 10px; color: black; }
            """)
            layout.addWidget(label, alignment=Qt.AlignRight)
        else:
            label.setStyleSheet("""
                QLabel { background-color: lightblue; padding: 8px; border-radius: 10px; color: black; }
            """)
            layout.addWidget(label, alignment=Qt.AlignLeft)

        # This is the crucial part:
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumHeight(1)  # allow vertical growth
        label.adjustSize()        # make label compute proper height
        self.adjustSize()
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