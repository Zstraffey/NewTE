import mysql
from PyQt5.QtWidgets import QMainWindow, QWidget, QPushButton, QVBoxLayout, QFormLayout, QMessageBox
from PyQt5.uic import loadUi
import mysql.connector as mc
from functools import partial

import imgs_rc  # your resources
from codigos.classes import Session, bancoDados, ChatBubble

class usuarioChat(QWidget):
    def __init__(self, user):#, callback):
        print(user)
        super().__init__()
        loadUi("../design/templates/contatos.ui", self)  # your .ui file with a QPushButton

        self.nome_salvo.setText(user["nome"])
        print("yooo")


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

        def callback(user):
            Session.loaded_chat = user["id_user"]
            self.infos_contato.setText(user["nome"])
            self.updateChat()

        for user in users:
            btn = usuarioChat(user)
            btn.pushButton.clicked.connect(partial(callback, user))
            layout.addWidget(btn)

        layout.addStretch()

        container.setMinimumHeight(70 * len(users))
        self.usuarios_chat.setFixedHeight(
            min(70 * len(users), 717)
        )
        self.usuarios_chat.setMaximumHeight(717)

        self.btn_confirmar.clicked.connect(self.cadastrarUsuario)
        self.btn_enviar.clicked.connect(self.sendMessage)

    def sendMessage(self):
        text = self.lineEdit_mensagem.text()
        db = bancoDados().conectar()

        query = f"""
        INSERT INTO mensagens_chat
        (remetente_id, destinatario_id, mensagem) 
        VALUES ({Session.current_user["id_user"]}, {Session.loaded_chat}, '{text}');
        """

        try:
            cursor = db.cursor()
            cursor.execute(query)
            db.commit()
            self.updateChat()
        except mc.Error as err:
            print("Error:", err)

    def updateUserList(self):
        db = bancoDados().conectar()
        if not db:
            return

        print("oi")

        cursor = db.cursor()
        print("eba")
        print(Session.current_user["id_user"])

        query = "SELECT id_user, nome FROM usuario WHERE id_user != %s"
        cursor.execute(query, (Session.current_user["id_user"],))
        results = cursor.fetchall()

        users = []

        #matheus@example.com

        for id_user, nome in results:
            users.append({
                "id_user": id_user,
                "nome": nome,
            })

        return users

    def updateChat(self):
        def clearLayout(layout):
            if layout is not None:
                while layout.count():
                    item = layout.takeAt(0)
                    widget = item.widget()
                    if widget is not None:
                        widget.deleteLater()  # safely deletes the widget
                    else:
                        clearLayout(item.layout())  # if it’s a nested layout

        db = bancoDados().conectar()
        if not db:
            return
        cursor = db.cursor()

        query = f"""
    SELECT * 
    FROM mensagens_chat
    WHERE 
        (remetente_id = {Session.current_user["id_user"]} 
         AND destinatario_id = {Session.loaded_chat})
    OR 
        (remetente_id = {Session.loaded_chat} 
         AND destinatario_id = {Session.current_user["id_user"]})
    ORDER BY data_envio ASC;
"""

        print(query)

        cursor.execute(query)
        results = cursor.fetchall()

        print(results)

        container = self.chat.widget()
        self.chat.setWidgetResizable(True)

        layout = container.layout()
        clearLayout(layout)

        defaultPos = 613
        self.chat.setGeometry(self.chat.x(), 613, self.chat.width(), self.chat.height())

        for row in results:
            bubble = ChatBubble(row[3], layout,sender="me" if row[1] == Session.current_user["id_user"] else "other")
            new_y = max(20, self.chat.y() - 30)
            self.chat.setGeometry(self.chat.x(), new_y, self.chat.width(), self.chat.height())

            layout.addWidget(bubble)

        print(len(results))

        container.setMinimumHeight(30 * len(results))
        self.chat.setFixedHeight(
            min(30 * len(results), 620)
        )
        self.chat.setMaximumHeight(620)

        layout.addStretch()
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
        db = bancoDados().conectar()
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