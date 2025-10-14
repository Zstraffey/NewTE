from functools import partial

from PyQt5.QtCore import QTimer, Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QWidget, QPushButton
from PyQt5.uic import loadUi
import mysql.connector as mc
import time
import imgs_qrc

from codigos.classes import Session, bancoDados, ChatBubble

class licao(QWidget):
    def __init__(self):#, callback):
        super().__init__()
        loadUi("../design/templates/aula_funcionario.ui", self)

class usuarioChat(QWidget):
    def __init__(self, user):#, callback):
        print(user)
        super().__init__()
        loadUi("../design/templates/contatos.ui", self)  # your .ui file with a QPushButton

        self.nome_salvo.setText(user["nome"])
        print("yooo")


class TelaInicial(QMainWindow):
    class DBLoopUdpate(QThread):
        new_data = pyqtSignal(list)

        def __init__(self):
            super().__init__()
            self.running = True

        def query(self):
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
        print("oi")
        loadUi("../design/dashboard_funcionario.ui", self)
        self.widget = stacked_widget

        Session.last_message_id = 0

        self.stack = self.findChild(QWidget, "stackedwidget_btns_da_sidebar")
        self.btn_sair.clicked.connect(self.logOut)

        self.stackList = [
            self.findChild(QPushButton, "btn_home"),
            self.findChild(QPushButton, "btn_chat"),
            self.findChild(QPushButton, "btn_perfil"),
        ]

        self.dashboardList = [
            self.findChild(QPushButton, "btn_rendimento_do_dash"),
            self.findChild(QPushButton, "btn_calendario_do_dash"),
            self.findChild(QPushButton, "btn_licoes_do_dash"),
        ]

        from functools import partial
        for i, botao in enumerate(self.stackList):
            botao.clicked.connect(partial(self.mudarTela, i))

        for i, botao in enumerate(self.dashboardList):
            botao.clicked.connect(partial(self.mudarDashboard, i))

        container = self.usuarios_chat.widget()
        self.usuarios_chat.setWidgetResizable(True)

        layout = container.layout()

        users = self.updateUserList()

        self.chat_timer = self.DBLoopUdpate()
        self.chat_timer.new_data.connect(self.updateChat)
        self.chat_timer.start()

        def callback(user):
            Session.loaded_chat = user["id_user"]
            self.infos_contato.setText(user["nome"])
            Session.last_message_id = 0

            self.clearLayout(self.chat.widget().layout())
            self.chat_timer.query()

        for user in users:
            btn = usuarioChat(user)
            btn.pushButton.clicked.connect(partial(callback, user))
            layout.addWidget(btn)

        layout.addStretch()

        self.btn_enviar.clicked.connect(self.sendMessage)
        self.atualizarLicoes()

    def mudarDashboard(self, index):
        self.stacked_widget_botoes_principais_do_dashboard.setCurrentIndex(index)

    def atualizarLicoes(self):
        container = self.scroll_licoes.widget()

        self.scroll_licoes.setWidgetResizable(True)
        layout = container.layout()

        self.clearLayout(layout)

        db = bancoDados().conectar()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM licoes")

        rows = cursor.fetchall()

        i = 0

        for id_licao, id_user, titulo, desc, metas, criacao, validade in rows:
            row = i // 4
            col = i % 4
            template = licao()
            layout.addWidget(template, row, col)
            template.lbl_titulo_curso.setText(titulo)
            template.lbl_desc_curso.setText(desc)
            template.btn_visualizar.clicked.connect(partial(self.alterarLicao, id_licao))
            i = i + 1

        row = i // 4
        col = i % 4

    def updateUserList(self):
        db = bancoDados().conectar()
        if not db:
            return

        cursor = db.cursor()

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
        self.stack.setCurrentIndex(index)

    def logOut(self):
        Session.current_user = None

        self.close()
        self.widget.setCurrentIndex(0)
        self.widget.show()