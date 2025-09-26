import mysql
from PyQt5.QtCore import QTimer, Qt, QThread, pyqtSignal, QByteArray, QBuffer, QIODevice, QSize
from PyQt5.QtWidgets import QMainWindow, QWidget, QPushButton, QVBoxLayout, QFormLayout, QMessageBox, QFileDialog
from PyQt5.uic import loadUi
from PyQt5.QtGui import QPixmap, QIcon

import mysql.connector as mc
import time
import sys
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
    class DBLoopUpdate(QThread):
        new_data = pyqtSignal(list)

        def __init__(self):
            super().__init__()
            self.running = True

        def query(self):
            if Session.current_user is None:
                self.stop()
                return

            db = bancoDados().conectar()
            if not db:
                return
            cursor = db.cursor()

            query = f"""
                 SELECT *
                 FROM mensagens_chat
                 WHERE id_mensagem > {Session.last_message_id} AND (
                     (remetente_id = {Session.current_user["id_user"]} AND destinatario_id = {Session.loaded_chat})
                     OR
                     (remetente_id = {Session.loaded_chat} AND destinatario_id = {Session.current_user["id_user"]})
                 )
                 ORDER BY data_envio ASC;
             """
            cursor.execute(query)
            results = cursor.fetchall()
            if results:
                self.new_data.emit(results)

        def run(self):
            while self.running:
                if Session.current_user is None:
                    self.stop()
                    return

                db = bancoDados().conectar()
                if not db:
                    return
                cursor = db.cursor()

                query = f"""
                     SELECT *
                     FROM mensagens_chat
                     WHERE id_mensagem > {Session.last_message_id} AND (
                         (remetente_id = {Session.current_user["id_user"]} AND destinatario_id = {Session.loaded_chat})
                         OR
                         (remetente_id = {Session.loaded_chat} AND destinatario_id = {Session.current_user["id_user"]})
                     )
                     ORDER BY data_envio ASC;
                 """
                cursor.execute(query)
                results = cursor.fetchall()

                if results:
                    self.new_data.emit(results)

                db.close()
                cursor.close()
                time.sleep(2)

        def stop(self):
            self.running = False

    def __init__(self, stacked_widget):
        super().__init__()
        loadUi("../design/NOVODASH.ui", self)
        self.widget = stacked_widget

        Session.last_message_id = 0

        self.stack = self.findChild(QWidget, "stackedwidget_btns_da_sidebar")
        self.dashboardStack = self.findChild(QWidget, "stacked_widget_botoes_principais_do_dashboard")

        self.btn_sair.clicked.connect(self.logOut)

        self.stackList = [
            self.findChild(QPushButton, "btn_home"),
            self.findChild(QPushButton, "btn_chat"),
            self.findChild(QPushButton, "btn_cadastro"),
            self.findChild(QPushButton, "btn_perfil"),
        ]

        self.dashboardList = [
            self.findChild(QPushButton, "btn_rendimento_do_dash"),
            self.findChild(QPushButton, "btn_licoes_do_dash"),
            self.findChild(QPushButton, "btn_func_do_dash"),
            self.findChild(QPushButton, "btn_calendario_do_dash"),
        ]

        from functools import partial
        for i, botao in enumerate(self.stackList):
            botao.clicked.connect(partial(self.mudarTela, i))

        for i, botao in enumerate(self.dashboardList):
            botao.clicked.connect(partial(self.mudarDashboard, i))

        self.ListUsers()

        self.chat_timer = self.DBLoopUpdate()
        self.chat_timer.new_data.connect(self.updateChat)
        self.chat_timer.start()

        self.btn_confirmar.clicked.connect(self.cadastrarUsuario)
        self.btn_enviar.clicked.connect(self.sendMessage)
        self.btn_selecionar_foto.clicked.connect(self.escolherFoto)

        self.foto_func.setIcon(QIcon(Session.current_user["foto_perfil"]))
        self.foto_func.setIconSize(QSize(80, 80))
        self.nome_func.setText(Session.current_user["nome"])
        self.carg_func.setText(Session.current_user["cargo"])

    def ListUsers(self):
        container = self.usuarios_chat.widget()
        self.usuarios_chat.setWidgetResizable(True)

        layout = container.layout()
        self.clearLayout(layout)

        users = self.updateUserList()

        def callback(user):
            Session.loaded_chat = user["id_user"]
            self.infos_contato.setText(user["nome"])
            self.infos_contato.setIcon(QIcon(user["foto_perfil"]))

            self.foto_func_contato.setIcon(QIcon(user["foto_perfil"]))
            self.nome_func_contato.setText(user["nome"])
            self.carg_func_contato.setText(user["cargo"])

            Session.last_message_id = 0

            self.clearLayout(self.chat.widget().layout())
            self.chat_timer.query()

        for user in users:
            btn = usuarioChat(user)
            btn.pushButton.clicked.connect(partial(callback, user))

            icon = user["foto_perfil"]
            btn.foto_cntt.setPixmap(icon)
            btn.foto_cntt.setScaledContents(True)

            layout.addWidget(btn)

        layout.addStretch()


    def escolherFoto(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "", "Images (*.png *.jpg *.jpeg *.bmp)"
        )

        if not file_path:
            return  # user cancelled

        pixmap = QPixmap(file_path)
        if pixmap.isNull():
            QMessageBox.warning(self, "Erro", "Não foi possível carregar a imagem!")
            return

        # Set button icon
        icon = QIcon(pixmap)
        self.foto_novo_func.setIcon(icon)
        self.foto_pixmap = pixmap

    def updateUserList(self):
        db = bancoDados().conectar()
        if not db:
            return []

        cursor = db.cursor()
        query = "SELECT id_user, nome, foto_perfil, cargo FROM usuario WHERE id_user != %s"
        cursor.execute(query, (Session.current_user["id_user"],))
        results = cursor.fetchall()
        cursor.close()
        db.close()

        users = []
        for id_user, nome, foto_perfil, cargo in results:
            pixmap = QPixmap()

            if foto_perfil:
                pixmap.loadFromData(foto_perfil)

            # If pixmap is invalid, use a default avatar
            if pixmap.isNull():
                pixmap = QPixmap('../imagens/user.png')

            users.append({
                "id_user": id_user,
                "nome": nome,
                "foto_perfil": pixmap,
                "cargo" : cargo
            })

        return users

    def clearLayout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()  # safely deletes the widget
                else:
                    self.clearLayout(item.layout())  # if it’s a nested layout

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
            cursor.close()
            db.close()

            self.chat_timer.query()
        except mc.Error as err:
            print("Error:", err)

    def updateChat(self, results):

        if results:
            Session.last_message_id = results[len(results)-1][0]

            self.chat.setWidgetResizable(True)
            container = self.chat.widget()
            layout = container.layout()
            layout.setAlignment(Qt.AlignTop)

            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(5)

            if layout.count() == 0:
                layout.addStretch()

            container.setMinimumHeight(self.chat.viewport().height())

            for row in results:
                bubble = ChatBubble(
                    row[3],
                    self.chat.viewport().width() / 2,
                    sender="me" if row[1] == Session.current_user["id_user"] else "other",
                )
                layout.insertWidget(layout.count() - 1, bubble)
                bubble.adjustSize()

            #container.setMinimumHeight(self.chat.viewport().height())

            self.resize(self.width() + 1, self.height())
            self.chat.setMaximumHeight(920)
            self.scrollToBottom()

    def scrollToBottom(self):
        # Delay slightly to ensure layout has fully recalculated
        QTimer.singleShot(50, self._scrollToBottomImmediate)

    def _scrollToBottomImmediate(self):
        sb = self.chat.verticalScrollBar()
        sb.setValue(sb.maximum())
        self.resize(self.width() - 1, self.height())

    def mudarTela(self, index):
        if index == 1:
            self.ListUsers()
        self.stack.setCurrentIndex(index)

    def mudarDashboard(self, index):
        self.dashboardStack.setCurrentIndex(index)

    def logOut(self):
        Session.current_user = None

        self.close()
        self.widget.setCurrentIndex(0)
        self.widget.show()

    def cadastrarUsuario(self):
        db = bancoDados().conectar()
        if not db:
            return

        cursor = db.cursor()

        # Convert pixmap to binary for DB
        if hasattr(self, "foto_pixmap") and self.foto_pixmap:
            ba = QByteArray()
            buffer = QBuffer(ba)
            buffer.open(QIODevice.WriteOnly)
            self.foto_pixmap.save(buffer, "PNG")
            buffer.close()
            img_data = ba.data()
        else:
            img_data = None  # No image selected

        valuesDictionaries = {
            "nome": self.lineEdit_nome.text(),
            "email": self.lineEdit_email.text(),
            "telefone": ''.join(c for c in self.lineEdit_telefone.text() if c.isdigit()),
            "cpf": ''.join(c for c in self.lineEdit_cpf.text() if c.isdigit()),
            "rg": ''.join(c for c in self.lineEdit_rg.text() if c.isdigit()),
            "departamento": self.comboBox_depto.currentText(),
            "cargo": self.comboBox_cargo.currentText(),
            "foto_perfil": img_data,
            "status": "ONLINE",
            "data_entrada": "2025-09-12",
            "sobre_mim": "Sobre mim...",
            "senha": 1234,
            "endereco": self.lineEdit_endereco.text(),
            "tipo_usuario": "admin",
            "experiencias": "Experiências..."
        }

        # Simple validation: all required fields filled
        for key, value in valuesDictionaries.items():
            if value is None or value == "":
                QMessageBox.warning(self, "Erro", f"Preencha o campo: {key}")
                return

        # Prepare query
        query = """
        INSERT INTO usuario
        (nome, email, telefone, cpf, rg, departamento, cargo, foto_perfil, status, data_entrada, sobre_mim, senha, endereco, tipo_usuario, experiencias)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        values = tuple(valuesDictionaries.values())

        try:
            cursor.execute(query, values)
            db.commit()
            QMessageBox.information(self, "Sucesso", "Usuário cadastrado com sucesso!")
        except mc.Error as err:
            QMessageBox.critical(self, "Erro", f"Falha ao salvar usuário: {err}")
        finally:
            cursor.close()
            db.close()