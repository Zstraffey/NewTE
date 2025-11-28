import mysql.connector as mc
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMainWindow, QWidget, QPushButton, QMessageBox, QLabel, QSizePolicy, QVBoxLayout, QDialog, QFileDialog
from PyQt5.QtCore import Qt, QSize
from PyQt5.uic import loadUi
import imgs_qrc
from PyQt5.QtGui import QPixmap

import re
import random
import string

import sys, os

def resource_path(relative):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative)
    return os.path.abspath(relative)

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
        #self.label.setMaximumWidth(self.max_width)
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
            mydb = mc.connect(
                host="srv1897.hstgr.io",
                user="u416468954_NEWTE",
                password="Newte2025",
                database="u416468954_newtebd",
                use_pure=True,
                ssl_disabled=True,
            )

            #mydb = mc.connect(
            #    host="localhost",
            #    user="root",
            #    password="",
            #    database="newte",
            #    use_pure=True,
            #    ssl_disabled = False,
            #    connection_timeout = 600,  # até 10 minutos
            #)

            return mydb
        except mc.Error as err:
            print(f"Erro do MySQL: {err}")
            QMessageBox.warning(None, "Erro", "Erro ao conectar no banco de dados.")

            return False

class PopupSobreMim(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(resource_path("design/sobre_mim.ui"), self)
        self.valor_retornado = None

        self.btn_confirmar_sobremim.clicked.connect(self.onConfirmar)

    def onConfirmar(self):
        self.valor_retornado = [self.lineEdit_sobremim.text(), self.lineEdit_experiencias.text()]
        self.accept()

class PopupCargo(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(resource_path("design/cargo.ui"), self)
        self.valor_retornado = None

        self.btn_adicionar_cargo.clicked.connect(self.onConfirmar)

    def onConfirmar(self):
        self.valor_retornado = [self.lineEdit_funcao.text(), self.comboBox_permissoes.currentText()]
        self.accept()

class PopupCalendario(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(resource_path("design/calendario_adicionar.ui"), self)
        self.valor_retornado = None

        self.btn_adicionar_evento.clicked.connect(self.onConfirmar)

    def onConfirmar(self):
        self.valor_retornado = [self.lineEdit_titulo.text(), self.textEdit_descricao.toPlainText()]
        self.accept()

class PopupVisualizarCal(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(resource_path("design/calendario_visualizar.ui"), self)

class PopupDepto(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(resource_path("design/departamento.ui"), self)
        self.valor_retornado = None
        self.foto_pixmap = None  # Para guardar a imagem carregada

        # Conecta os botões
        self.btn_confirmar_depto.clicked.connect(self.onConfirmar)
        self.btn_selecionar_foto.clicked.connect(self.escolherFoto)

    def escolherFoto(self):
        # Abre o seletor de arquivos
        caminho_foto, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar foto",
            "",
            "Imagens (*.png *.jpg *.jpeg *.bmp *.gif *.jfif)"
        )

        if caminho_foto:
            # Cria um QPixmap a partir do arquivo
            pixmap = QPixmap(caminho_foto)

            if not pixmap.isNull():
                # Redimensiona o pixmap para caber na label (opcional)
                pixmap_redimensionado = pixmap.scaled(
                    self.label_foto.width(),
                    self.label_foto.height(),
                    #aspectRatioMode=1  # Mantém proporção
                )

                # Mostra na QLabel
                self.label_foto.setPixmap(pixmap_redimensionado)

                # Salva o pixmap original para retornar depois
                self.foto_pixmap = pixmap

    def onConfirmar(self):
        # Exemplo: retorna função, permissão e o pixmap da foto
        self.valor_retornado = [
            self.lineEdit_nome.text(),
            self.foto_pixmap if self.foto_pixmap is not None else ""
        ]
        self.accept()

class ValidadorCPF:
    def __init__(self, cpf: str):
        self.cpf = re.sub(r'\D', '', cpf)

    def validar(self):
        # CPF precisa ter 11 dígitos
        if len(self.cpf) != 11 or self.cpf == self.cpf[0] * 11:
            return False

        for i in range(9, 11):
            soma = sum(int(self.cpf[num]) * ((i + 1) - num) for num in range(i))
            digito = (soma * 10) % 11
            digito = 0 if digito == 10 else digito
            if digito != int(self.cpf[i]):
                return False

        return self.cpf

class ValidadorRG:
    def __init__(self, rg: str):
        self.rg = re.sub(r'\D', '', rg)

    def validar(self):
        if not (7 <= len(self.rg) <= 9):
            return False

        if self.rg == self.rg[0] * len(self.rg):
            return False

        return self.rg

class ValidadorSenha:
    def __init__(self, senha: str):
        self.senha = senha

    def validar(self):
        if len(self.senha) < 8:
            return False

        if not re.search(r'[a-z]', self.senha):
            return False

        if not re.search(r'[A-Z]', self.senha):
            return False

        if not re.search(r'[^a-zA-Z0-9]', self.senha):
            return False

        return self.senha

class ValidadorEmail:
    def __init__(self, email: str):
        self.email = email.strip()

    def validar(self):
        padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        if re.match(padrao, self.email):
            return self.email
        else:
            return False

class GeradorSenha:
    def __init__(self, tamanho=15):
        self.tamanho = tamanho

    def gerar(self):

        letras_minusculas = string.ascii_lowercase
        letras_maiusculas = string.ascii_uppercase
        numeros = string.digits
        especiais = "!@#$%^&*()-_=+[]{};:,.<>?/|\\"

        senha = [
            random.choice(letras_minusculas),
            random.choice(letras_maiusculas),
            random.choice(numeros),
            random.choice(especiais),
        ]

        todos = letras_minusculas + letras_maiusculas + numeros + especiais
        senha += random.choices(todos, k=self.tamanho - 4)

        random.shuffle(senha)

        return ''.join(senha)