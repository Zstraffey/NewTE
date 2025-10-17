from PyQt5.QtCore import QTimer, Qt, QThread, pyqtSignal, QByteArray, QBuffer, QIODevice, QSize, QRect, QRectF
from PyQt5.QtWidgets import QMainWindow, QWidget, QPushButton, QMessageBox, QFileDialog, QTableWidgetItem, QHeaderView, \
    QSizePolicy, QGridLayout
from PyQt5.uic import loadUi
from PyQt5.QtGui import QPixmap, QIcon, QPainterPath, QRegion
import imgs_qrc
import mysql.connector as mc
import time
from functools import partial

from codigos.classes import Session, bancoDados, ChatBubble
class licao(QWidget):
    def __init__(self):#, callback):
        super().__init__()
        loadUi("../design/templates/aula_funcionario.ui", self)

class usuarioChat(QWidget):
    def __init__(self, user):#, callback):
        print(user)
        super().__init__()
        loadUi("../design/templates/contatos.ui", self)

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
        self.licao_ativa = None

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

        self.foto_func.setPixmap(Session.current_user["foto_perfil"])

        from functools import partial
        for i, botao in enumerate(self.stackList):
            botao.clicked.connect(partial(self.mudarTela, i))

        for i, botao in enumerate(self.dashboardList):
            botao.clicked.connect(partial(self.mudarDashboard, i))

        container = self.usuarios_chat.widget()
        self.usuarios_chat.setWidgetResizable(True)

        layout = container.layout()

        self.chat_timer = self.DBLoopUdpate()
        self.chat_timer.new_data.connect(self.updateChat)
        self.chat_timer.start()

        self.newte.setText(f'<html><head/><body><p><span style=" font-size:20pt;">Olá {Session.current_user["nome"]}!</span></p></body></html>')
        self.nome_func.setText(f'<html><head/><body><p align="center"><span style=" font-size:14pt;">{Session.current_user["nome"]}</span></p></body></html>')
        self.carg_func.setText(f'<html><head/><body><p align="center"><span style=" font-size:12pt;">{Session.current_user["cargo"]}</span></p></body></html>')

        def callback(user):
            Session.loaded_chat = user["id_user"]
            self.infos_contato.setText(user["nome"])
            Session.last_message_id = 0

            self.clearLayout(self.chat.widget().layout())
            self.chat_timer.query()

        self.ListUsers()

        layout.addStretch()

        self.btn_enviar.clicked.connect(self.sendMessage)
        self.btn_voltar.clicked.connect(partial(self.mudarDashboard, 2))
        self.btn_concluir.clicked.connect(self.concluirAtividade)
        self.atualizarLicoes()

    def mudarDashboard(self, index):
        if index == 2:
            self.licao_ativa = None
            self.atualizarLicoes()
        self.stacked_widget_botoes_principais_do_dashboard.setCurrentIndex(index)

    def quitProgram(self):
        if Session.current_user is None:
            return
        db = bancoDados().conectar()
        if not db:
            return

        cursor = db.cursor()

        query = f"""
                    UPDATE usuario SET status = 'OFFLINE' WHERE email = '{Session.current_user["email"]}';
               """
        cursor.execute(query)
        db.commit()

        cursor.close()
        db.close()

    def atualizarLicoes(self):
        container = self.scroll_licoes.widget()

        self.scroll_licoes.setWidgetResizable(True)
        layout = container.layout()

        self.clearLayout(layout)

        db = bancoDados().conectar()
        cursor = db.cursor()

        query = "SELECT id_licao FROM usuario_licao_realizada WHERE id_usuario = %s"
        cursor.execute(query, (Session.current_user["id_user"], ))
        list = cursor.fetchall()
        id_list = [row[0] for row in list]

        cursor.execute("SELECT * FROM licoes")
        rows = cursor.fetchall()

        i = 0
        print(id_list)
        for id_licao, id_user, titulo, desc, metas, criacao, validade in rows:
            print(id_licao)
            row = i // 4
            col = i % 4
            template = licao()
            layout.addWidget(template, row, col)
            template.lbl_titulo_curso.setText(titulo)
            template.lbl_desc_curso.setText(desc)
            template.btn_visualizar.clicked.connect(partial(self.visualizarLicao, id_licao))
            i = i + 1

            if id_licao in id_list:
                print("ta")
                template.template_cursos_substituir.setStyleSheet('QWidget{\nbackground-color: rgb(109, 109, 109);\n}\n#template_cursos_substituir{\n\n    border-radius: 6px;\n    border: 3px solid rgb(111, 230, 111);}')
                template.lbl_situacao_licao.setStyleSheet('background-color:rgb(111, 230, 111);\nborder-radius: 4px;')
                template.lbl_situacao_licao.setText(f'<html><head/><body><p align="center">{"Concluído"}</p></body></html>')

    def visualizarLicao(self, id_licao):
        self.mudarDashboard(3)

        db = bancoDados().conectar()
        if not db:
            return

        cursor = db.cursor()
        query = "SELECT titulo, conteudo, metas FROM licoes WHERE id_licao = %s"
        cursor.execute(query, (id_licao,))
        result = cursor.fetchone()

        self.licao_ativa = id_licao

        if not (result is None):
            titulo, conteudo, metas = result

            # self.titulo_cadastro_2.setText(f"Alterando {titulo} ({self.alterar})")

            self.lbl_titulo.setText(f'<html><head/><body><p><span style=" font-size:20pt;">{titulo}</span></p></body></html>')
            self.lbl_desc.setText(f'<html><head/><body><p><span style=" font-size:12pt;">{conteudo}</span></p></body></html>')
            self.lbl_metas.setText(f'<html><head/><body><p><span style=" font-size:10pt; font-weight:600; color:#d1d1d1;">{metas}</span></p></body></html>')

        cursor.close()
        db.close()

    def ListUsers(self):
        container = self.usuarios_chat.widget()
        self.usuarios_chat.setWidgetResizable(True)

        layout = container.layout()
        self.clearLayout(layout)

        users = self.updateUserList()

        def callback(user):
            Session.loaded_chat = user["id_user"]

            path = QPainterPath()
            path.addEllipse(QRectF(0, 0, 60, 60))
            region = QRegion(path.toFillPolygon().toPolygon())

            self.infos_contato.setText(user["nome"])

            #self.foto_func_contato.setPixmap(user["foto_perfil"])
            #self.foto_func_contato.setMask(region)

            #self.foto_func_contato_2.setPixmap(user["foto_perfil"])
            #self.foto_func_contato_2.setMask(region)

            self.nome_func_contato.setText(user["nome"])
            self.carg_func_contato.setText(user["cargo"])

            Session.last_message_id = 0

            self.clearLayout(self.chat.widget().layout())
            self.chat_timer.query()

        for user in users:
            btn = usuarioChat(user)
            btn.pushButton.clicked.connect(partial(callback, user))

            icon = user["foto_perfil"].scaled(btn.foto_cntt.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            btn.foto_cntt.setFixedSize(60, 60)
            btn.foto_cntt.setPixmap(icon)

            path = QPainterPath()
            path.addEllipse(QRectF(0, 0, 60, 60))  # usa QRectF
            region = QRegion(path.toFillPolygon().toPolygon())

            btn.foto_cntt.setMask(region)

            btn.online.setText(user["status"])

            if user["status"] == "OFFLINE":
                btn.online.setStyleSheet("""
                    QLabel {
                        color: red;
                    }
                """)
            else:
                btn.online.setStyleSheet("""
                    QLabel {
                        color: green;
                    }
                """)

            layout.addWidget(btn)

        layout.addStretch()

    def updateUserList(self):
        db = bancoDados().conectar()
        if not db:
            return []

        cursor = db.cursor()
        query = "SELECT id_user, nome, foto_perfil, cargo, status FROM usuario WHERE id_user != %s"
        cursor.execute(query, (Session.current_user["id_user"],))
        results = cursor.fetchall()
        cursor.close()
        db.close()

        users = []
        for id_user, nome, foto_perfil, cargo, status in results:
            pixmap = QPixmap()

            if foto_perfil:
                pixmap.loadFromData(foto_perfil)

            if pixmap.isNull():
                pixmap = QPixmap('../imagens/user.png')

            users.append({
                "id_user": id_user,
                "nome": nome,
                "foto_perfil": pixmap,
                "cargo" : cargo,
                "status" : status,
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
    def concluirAtividade(self):
        db = bancoDados().conectar()

        query = f"""
                  INSERT INTO usuario_licao_realizada
                  (id_usuario, id_licao) 
                  VALUES ({Session.current_user["id_user"]}, {self.licao_ativa});
                  """
        try:
            cursor = db.cursor()
            cursor.execute(query)
            db.commit()
            cursor.close()
            db.close()

            QMessageBox.information(self, "Sucesso", f"Parabéns! Você concluiu esta lição!")
        except mc.Error as err:
            print("Error:", err)

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
        self.chat_timer.stop()
        self.quitProgram()
        Session.current_user = None

        self.close()
        self.widget.setCurrentIndex(0)
        self.widget.show()