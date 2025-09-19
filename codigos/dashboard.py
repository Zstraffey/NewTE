import mysql
from PyQt5.QtWidgets import QMainWindow, QWidget, QPushButton, QVBoxLayout, QFormLayout, QMessageBox
from PyQt5.uic import loadUi
import classes
import mysql.connector as mc

import imgs_rc  # your resources
from codigos.classes import Session, bancoDados

class usuarioChat(QWidget):
    def __init__(self, user):#, callback):
        print(user)
        super().__init__()
        loadUi("../design/templates/contatos.ui", self)  # your .ui file with a QPushButton

        self.nome_salvo.setText(user["nome"])
        print("yooo")
        # Connect the button to shared callback with username
        self.pushButton.clicked.connect(lambda: self.callback(user["id_user"]))

    def callback(self, id):
        Session.loaded_chat = id

class TelaInicial(QMainWindow):
    def __init__(self, stacked_widget):
        super().__init__()
        loadUi("../design/NOVODASH.ui", self)
        self.widget = stacked_widget

        print(Session.current_user)

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

        users = self.updateUserList()

        for user in users:
            btn = usuarioChat(user)
            layout.addWidget(btn)

        layout.addStretch()

        container.setMinimumHeight(70 * len(users))
        self.usuarios_chat.setFixedHeight(
            min(70 * len(users), 717)
        )
        self.usuarios_chat.setMaximumHeight(717)

        self.btn_confirmar.clicked.connect(self.cadastrarUsuario)

    def updateUserList(self):
        db = bancoDados().conectar()
        if not db:
            return

        print("oi")

        cursor = db.cursor()
        print("eba")
        print(Session.current_user["id_user"])

        query = "SELECT id_user, nome, email FROM usuario WHERE id_user != %s"
        cursor.execute(query, (Session.current_user["id_user"],))
        results = cursor.fetchall()

        users = []

        #matheus@example.com

        for id_user ,nome, email in results:
            users.append({
                "id_user": id_user,
                "nome": nome,
                "email": email
            })

        return users


    def updateChat(self):
        db = classes.bancoDados().conectar()
        if not db:
            return
        cursor = db.cursor()

        cursor.execute("SELECT sender, message FROM messages ORDER BY id ASC")
        results = cursor.fetchall()

        for sender, msg in results:
            bubble = classes.ChatBubble(msg, self.chat,sender="me" if sender == "Alice" else "other")
            self.vbox.addWidget(bubble)

        self.vbox.addStretch()
        cursor.close()
        db.close()

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