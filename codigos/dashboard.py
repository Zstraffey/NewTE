import mysql
from PyQt5.QtWidgets import QMainWindow, QWidget, QPushButton, QVBoxLayout, QFormLayout, QMessageBox
from PyQt5.uic import loadUi
import classes
import mysql.connector as mc

import imgs_rc  # your resources
class TelaInicial(QMainWindow):
    def __init__(self, stacked_widget):
        super().__init__()
        loadUi("../design/NOVODASH.ui", self)
        self.widget = stacked_widget

        self.stack = self.findChild(QWidget, "stackedwidget_btns_da_sidebar")
        self.dashboardStack = self.findChild(QWidget, "stacked_widget_botoes_principais_do_dashboard")

        self.btn_sair.clicked.connect(self.logOut)

        self.stackList = [
            self.findChild(QPushButton, "btn_home"),
            self.findChild(QPushButton, "btn_chat"),
            self.findChild(QPushButton, "btn_config"),
            self.findChild(QPushButton, "btn_cadastro"),
            self.findChild(QPushButton, "btn_perfil"),
        ]

        self.dashboardList = [
            self.findChild(QPushButton, "btn_rendimento_do_dash"),
            self.findChild(QPushButton, "btn_func_do_dash"),
            self.findChild(QPushButton, "btn_calendario_do_dash"),
        ]

        # Use partial to bind index safely
        from functools import partial
        for i, botao in enumerate(self.stackList):
            botao.clicked.connect(partial(self.mudarTela, i))

        for i, botao in enumerate(self.dashboardList):
            botao.clicked.connect(partial(self.mudarDashboard, i))

        container = self.usuarios_chat.widget()
        self.usuarios_chat.setWidgetResizable(True)

        layout = container.layout()

        users = ["Alice", "Bob", "Charlie", "Dave",]

        for user in users:
            btn = classes.usuarioChat(user)
            layout.addWidget(btn)

        layout.addStretch()

        container.setMinimumHeight(70 * len(users))
        self.usuarios_chat.setFixedHeight(
            min(70 * len(users), 717)
        )
        self.usuarios_chat.setMaximumHeight(717)

        self.btn_confirmar.clicked.connect(self.cadastrarUsuario)

    def mudarTela(self, index):
        self.stack.setCurrentIndex(index)

    def mudarDashboard(self, index):
        self.dashboardStack.setCurrentIndex(index)

    def logOut(self):
        self.close()
        self.widget.setCurrentIndex(0)
        self.widget.show()

    def cadastrarUsuario(self):
        db = classes.bancoDados().conectar()
        if not db:
            return

        cursor = db.cursor()

        valuesDictionaries = {
            "nome": self.lineEdit_nome.text(),
            "email": self.lineEdit_email.text(),
            "telefone": ''.join([c for c in self.lineEdit_telefone.text() if c.isdigit()]),
            "cpf": ''.join([c for c in self.lineEdit_cpf.text() if c.isdigit()]),
            "rg": ''.join([c for c in self.lineEdit_rg.text() if c.isdigit()]),
            "departamento": self.comboBox_depto.currentText(),
            "cargo": self.comboBox_cargo.currentText(),
            "foto_perfil": "FOTO.jpg",
            "status": "ONLINE",
            "data_entrada": "2025-09-12",
            "sobre_mim": "Sobre mim...",
            "senha": 1234,
            "endereco": self.lineEdit_endereco.text(),
            "tipo_usuario": "admin",
            "experiencias": "Experiências..."
        }

        values = (
            valuesDictionaries["nome"],
            valuesDictionaries["email"],
            valuesDictionaries["telefone"],
            valuesDictionaries["cpf"],
            valuesDictionaries["rg"],
            valuesDictionaries["departamento"],
            valuesDictionaries["cargo"],
            valuesDictionaries["foto_perfil"],
            valuesDictionaries["status"],
            valuesDictionaries["data_entrada"],
            valuesDictionaries["sobre_mim"],
            valuesDictionaries["senha"],
            valuesDictionaries["endereco"],
            valuesDictionaries["tipo_usuario"],
            valuesDictionaries["experiencias"]
        )

        for i, value in enumerate(values):
            if value is None or value == "":
                print(f"Value at index {i} is empty or None: {value}")
                QMessageBox.warning(self, "Erro", "Preencha todos os campos!")
                break
        else:
            query = """
            INSERT INTO usuario 
            (nome, email, telefone, cpf, rg, departamento, cargo, foto_perfil, status, data_entrada, sobre_mim, senha, endereco, tipo_usuario, experiencias) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """

            try:
                cursor = db.cursor()
                cursor.execute(query, values)
                db.commit()
                print("User inserted successfully!")
                QMessageBox.information(self, "Sucesso", "Usuário cadastrado com sucesso!")
            except mc.Error as err:
                print("Error:", err)