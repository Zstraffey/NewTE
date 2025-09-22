import mysql.connector as mc
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QWidget, QPushButton, QMessageBox, QLabel, QSizePolicy, QVBoxLayout
from PyQt5.QtCore import Qt, QSize
from PyQt5.uic import loadUi

class Session:
    current_user = None
    loaded_chat = 0

class ChatBubble(QWidget):
    def __init__(self, text, sender="me", max_width=300):
        super().__init__()

        self.max_width = max_width

        self.label = QLabel(text, self)
        self.label.setWordWrap(True)
        self.label.setMaximumWidth(self.max_width)
        self.label.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        # Styling
        if sender == "me":
            self.label.setStyleSheet("""
                QLabel {
                    background-color: lightgreen;
                    padding: 6px;
                    border-radius: 10px;
                    color: black;
                }
            """)
            alignment = Qt.AlignRight | Qt.AlignTop
        else:
            self.label.setStyleSheet("""
                QLabel {
                    background-color: lightblue;
                    padding: 6px;
                    border-radius: 10px;
                    color: black;
                }
            """)
            alignment = Qt.AlignLeft | Qt.AlignTop

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.label, alignment=alignment)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

    def sizeHint(self):
        hint = self.label.sizeHint()
        return QSize(hint.width(), hint.height())

    #def resizeEvent(self, event):
    #    super().resizeEvent(event)
    #    needed = self.label.sizeHint().height()
    #    if self.height() != needed:
    #        self.setMinimumHeight(needed)
    #        self.resize(self.width(), needed)

class bancoDados:
    def __init__(self):
        print("inicializado banco de dados")

    def conectar(self):

        try:
            #mydb = mc.connect(
            #    host="srv1897.hstgr.io",
            #    user="u416468954_NEWTE",
            #    password="Newte2025",
            #    database="u416468954_newtebd",
            #    use_pure=True
            #)

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