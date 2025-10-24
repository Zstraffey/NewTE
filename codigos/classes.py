import mysql.connector as mc
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMainWindow, QWidget, QPushButton, QMessageBox, QLabel, QSizePolicy, QVBoxLayout, QDialog
from PyQt5.QtCore import Qt, QSize
from PyQt5.uic import loadUi
import imgs_qrc

class Session:
    current_user = None
    loaded_chat = 0
    last_message_id = 0

class ChatBubble(QWidget):
    def __init__(self, text,max_width ,sender="me"):
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

    def resizeEvent(self, event):
        super().resizeEvent(event)
        needed = self.label.sizeHint().height()
        if self.height() != needed:
            self.setMinimumHeight(needed)
            self.resize(self.width(), needed)

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
                use_pure=True,
                ssl_disabled = False
            )

            return mydb
        except mc.Error as err:
            print(f"Erro do MySQL: {err}")
            QMessageBox.warning(None, "Erro", "Erro ao conectar no banco de dados.")

            return False

class PopupSobreMim(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("../design/templates/sobre_mim.ui", self)
        self.valor_retornado = None

        self.btn_confirmar_sobremim.clicked.connect(self.onConfirmar)

    def onConfirmar(self):
        self.valor_retornado = [self.lineEdit_sobremim.text(), self.lineEdit_experiencias.text()]
        self.accept()

class PopupCargo(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("../design/templates/cargo.ui", self)
        self.valor_retornado = None

        self.btn_adicionar_cargo.clicked.connect(self.onConfirmar)

    def onConfirmar(self):
        self.valor_retornado = [self.lineEdit_funcao.text(), self.comboBox_permissoes.currentText()]
        self.accept()