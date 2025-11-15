import math
import os
from encodings import normalize_encoding

os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu --disable-software-rasterizer --no-sandbox"

import vlc

from PyQt5.QtCore import QTimer, Qt, QThread, pyqtSignal, QByteArray, QBuffer, QIODevice, QSize, QRect, QRectF, QDate
from PyQt5.QtWidgets import QMainWindow, QWidget, QPushButton, QMessageBox, QFileDialog, QTableWidgetItem, QHeaderView, \
    QSizePolicy, QGridLayout, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSlider
from PyQt5.uic import loadUi
from PyQt5.QtGui import QPixmap, QIcon, QPainterPath, QRegion, QTextCharFormat, QBrush, QColor
import imgs_qrc
import mysql.connector as mc
import time
from functools import partial

from codigos.classes import Session, bancoDados, ChatBubble, PopupSobreMim, PopupVisualizarCal

import re
import unicodedata
import difflib
import tempfile
import subprocess

leet_map = {
    'a': ['4', '@'],
    'e': ['3'],
    'i': ['1', '!', '|', 'l'],
    'o': ['0'],
    'u': ['v'],
    's': ['5', '$'],
    'g': ['9'],
    'b': ['8'],
    't': ['7'],
    'c': ['('],
}

palavras_bloqueadas = [
    "nigger", "nigga", "merda", "cu", "cus", "cuzao", "cuzão", "cv", "pcc",
    "foda", "fodo", "fodao", "fodão", "ass", "bundao", "bundão", "bunda", "bundinha",
    "viado", "bicha", "traveco", "tranny", "puto", "puta", "fdp", "filho da puta",
    "filha da puta", "urtiga", "desgraçado", "desgracado", "vai tomar no cu",
    "retardado", "mongol", "imbecil", "caralho", "krl", "putinho", "putinha",
    "nazista", "nazi", "arrombado", "arrombada", "crl"
]

def normalizar(texto):
    # Remove acentos e coloca tudo em minúsculo
    texto = unicodedata.normalize('NFD', texto)
    texto = texto.encode('ascii', 'ignore').decode('utf-8')
    return texto.lower()

def gerar_variacoes(palavra):
    # Cria regex com variações leet
    regex = ""
    for letra in palavra:
        letras_possiveis = [letra]
        if letra in leet_map:
            letras_possiveis += leet_map[letra]
        grupo = "[" + re.escape("".join(set(letras_possiveis))) + "]"
        regex += grupo
    return regex

def palavras_semelhantes(palavra, lista, limiar=0.8):
    # Retorna palavras da lista que são parecidas com a fornecida (acima de certo limiar)
    semelhantes = []
    for proibida in lista:
        ratio = difflib.SequenceMatcher(None, palavra, proibida).ratio()
        if ratio >= limiar:
            semelhantes.append(proibida)
    return semelhantes

def filtrar_texto(texto_original):
    texto_filtrado = texto_original
    texto_normalizado = normalizar(texto_original)

    # Divide o texto normalizado em palavras individuais para verificação de similaridade
    palavras_no_texto = re.findall(r'\b\w+\b', texto_normalizado)

    for palavra_texto in palavras_no_texto:
        similares = palavras_semelhantes(palavra_texto, palavras_bloqueadas)

        for proibida in similares:
            padrao_regex = gerar_variacoes(proibida)
            regex_compilado = re.compile(padrao_regex, re.IGNORECASE)

            # Substitui variações encontradas
            texto_filtrado = regex_compilado.sub(lambda m: m.group(0)[0] + "#" * (len(m.group(0)) - 1), texto_filtrado)

            # Também substitui se a palavra for parecida diretamente (ex: "desagraçado")
            texto_filtrado = re.sub(rf'\b{re.escape(palavra_texto)}\b',
                                    palavra_texto[0] + "#" * (len(palavra_texto) - 1),
                                    texto_filtrado, flags=re.IGNORECASE)

    return texto_filtrado

from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView  # Para PDF
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent  # Para vídeo
from PyQt5.QtMultimediaWidgets import QVideoWidget
#pip install PyQtWebEngine

class VisualizadorArquivo(QDialog):
    def __init__(self, caminho_arquivo, tipo, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Visualizador de Arquivo")
        self.resize(900, 600)

        layout = QVBoxLayout(self)
        self.setLayout(layout)

        self._player = None
        self._viewer = None
        self.timer = None

        try:
            if not os.path.exists(caminho_arquivo):
                raise FileNotFoundError("Arquivo não encontrado.")

            tipo = (tipo or "").lower()

            # -----------------------------
            # VISUALIZADOR DE PDF
            # -----------------------------
            if tipo == "pdf":
                self._viewer = QWebEngineView()
                layout.addWidget(self._viewer)

                self._viewer.settings().setAttribute(self._viewer.settings().PluginsEnabled, True)
                self._viewer.settings().setAttribute(self._viewer.settings().PdfViewerEnabled, True)

                file_url = QUrl.fromLocalFile(caminho_arquivo)
                self._viewer.load(file_url)

                QTimer.singleShot(300, lambda: self._viewer.setZoomFactor(1.0))

            # -----------------------------
            # VISUALIZADOR DE VÍDEO (VLC)
            # -----------------------------
            elif tipo in ["mp4", "avi", "mov", "mkv", "webm"]:
                video_widget = QVideoWidget()
                layout.addWidget(video_widget)

                # VLC
                self._vlc_instance = vlc.Instance()
                self._vlc_media = self._vlc_instance.media_new(caminho_arquivo)
                self._player = self._vlc_instance.media_player_new()
                self._player.set_media(self._vlc_media)

                # conectar vídeo ao widget
                winid = int(video_widget.winId())
                if os.name == "nt":
                    self._player.set_hwnd(winid)
                elif os.name == "posix":
                    self._player.set_xwindow(winid)

                self._player.play()

                # ==== CONTROLES ====
                controls_layout = QHBoxLayout()

                # Botão play/pause
                self.play_btn = QPushButton("⏸ Pausar")
                self.play_btn.clicked.connect(self.toggle_play_pause)
                controls_layout.addWidget(self.play_btn)

                # Tempo atual
                self.label_tempo_atual = QLabel("00:00")
                controls_layout.addWidget(self.label_tempo_atual)

                # Slider
                self.slider = QSlider(Qt.Horizontal)
                self.slider.setRange(0, 0)
                controls_layout.addWidget(self.slider)

                # Tempo total
                self.label_tempo_total = QLabel("00:00")
                controls_layout.addWidget(self.label_tempo_total)

                layout.addLayout(controls_layout)

                # Quando mover o slider
                self.slider.sliderMoved.connect(self._mudar_posicao)

                # Timer para atualizar UI
                self.timer = QTimer()
                self.timer.setInterval(200)
                self.timer.timeout.connect(self._update_vlc_ui)
                self.timer.start()

            else:
                QMessageBox.information(
                    self,
                    "Abrindo Externamente",
                    f"O formato '{tipo}' não é suportado internamente.\n"
                    f"O arquivo será aberto com o programa padrão."
                )
                self._abrir_externo_e_fechar(caminho_arquivo)
                return

        except Exception as e:
            QMessageBox.critical(self, "Erro ao abrir arquivo", str(e))
            try:
                self._abrir_externo_e_fechar(caminho_arquivo)
            except:
                pass
            self.close()

    # ----------------------------------------------
    # Métodos auxiliares
    # ----------------------------------------------

    def _abrir_externo_e_fechar(self, caminho):
        try:
            if os.name == 'nt':
                os.startfile(caminho)
            elif os.name == 'posix':
                subprocess.call(('xdg-open', caminho))
            else:
                QMessageBox.information(self, "Arquivo salvo", f"Arquivo em: {caminho}")
        finally:
            try:
                self.accept()
            except:
                self.close()

    # ---------- VLC UI UPDATE ----------
    def _update_vlc_ui(self):
        if self._player is None:
            return

        length = self._player.get_length()  # ms
        if length > 0 and self.slider.maximum() != length:
            self.slider.setRange(0, length)
            self.label_tempo_total.setText(self._formatar_tempo(length))

        pos = self._player.get_time()  # ms
        if not self.slider.isSliderDown():
            self.slider.setValue(pos)

        self.label_tempo_atual.setText(self._formatar_tempo(pos))

    # ---------- SLIDER / SEEK ----------
    def _mudar_posicao(self, position):
        if self._player:
            self._player.set_time(position)

    # ---------- FORMATAR TEMPO ----------
    def _formatar_tempo(self, ms):
        secs = ms // 1000
        mins = secs // 60
        secs = secs % 60
        return f"{mins:02d}:{secs:02d}"

    # ---------- PLAY / PAUSE ----------
    def toggle_play_pause(self):
        if self._player is None:
            return

        if self._player.is_playing():
            self._player.pause()
            self.play_btn.setText("▶ Reproduzir")
        else:
            self._player.play()
            self.play_btn.setText("⏸ Pausar")

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

class agendaListada(QWidget):
    def __init__(self, agenda):#, callback):
        print(agenda)
        super().__init__()
        loadUi("../design/templates/compromisso_marcado_agenda.ui", self)

        dias = [
            "Seg", "Ter", "Qua",
            "Qui", "Sex", "Sáb", "Dom"
        ]

        dia_semana = dias[agenda["data"].weekday()]

        self.lbl_nome_compromisso.setText(agenda["nome"])
        self.lbl_data.setText(agenda["data"].strftime("%d/%m"))
        self.lbl_dia_semanal.setText(dia_semana)

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
                query = f"""
                     UPDATE mensagens_chat
                     SET lida = 1
                     WHERE lida = 0 AND destinatario_id = {Session.current_user["id_user"]} AND remetente_id = {Session.loaded_chat}
                 """
                cursor.execute(query)
                db.commit()
                print(query)

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
                    query = f"""
                         UPDATE mensagens_chat
                         SET lida = 1
                         WHERE lida = 0 AND destinatario_id = {Session.current_user["id_user"]} AND remetente_id = {Session.loaded_chat}
                     """
                    cursor.execute(query)
                    db.commit()
                    print(query)

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
        self.atualizarPerfil(Session.current_user["id_user"])
        self.btn_editar_perfil.clicked.connect(self.abrirSobreMim)
        self.btn_visualizar_perfil.clicked.connect(lambda: self.atualizarPerfil(Session.loaded_chat))

        from functools import partial
        for i, botao in enumerate(self.stackList):
            botao.clicked.connect(partial(self.mudarTela, i))

        for i, botao in enumerate(self.dashboardList):
            botao.clicked.connect(partial(self.mudarDashboard, i))

        container = self.usuarios_chat.widget()
        self.usuarios_chat.setWidgetResizable(True)

        layout = container.layout()

        self.chat_timer = self.DBLoopUpdate()
        self.chat_timer.new_data.connect(self.updateChat)
        self.chat_timer.start()

        self.newte.setText(f'<html><head/><body><p><span style=" font-size:20pt;">Olá {Session.current_user["nome"]}!</span></p></body></html>')
        self.nome_func.setText(f'<html><head/><body><p align="center"><span style=" font-size:14pt;">{Session.current_user["nome"]}</span></p></body></html>')
        self.carg_func.setText(f'<html><head/><body><p align="center"><span style=" font-size:12pt;">{Session.current_user["cargo"]}</span></p></body></html>')

        self.widget_calendario.activated.connect(self.calendarioClique)
        self.atualizarCalendario()

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

        self.listarCalendario()
        self.atualizarProgresso()

        self.atualizarLicoes()

    def atualizarProgresso(self):
        db = bancoDados().conectar()

        if not db:
            return

        cursor = db.cursor()

        cursor.execute("SELECT COUNT(*) FROM licoes")
        total = cursor.fetchone()[0]
        cursor.execute(f"SELECT COUNT(*) FROM usuario_licao_realizada WHERE id_usuario = {Session.current_user['id_user']}")
        realizadas = cursor.fetchone()[0]

        self.lbl_progresso.setText(f"{realizadas}/{total}")
        self.barra_progresso.setValue(math.floor(realizadas/total)*100)

        self.lbl_novas_licoes.setText(f"{total-realizadas}")

        query = """
            SELECT id_licao, titulo
            FROM licoes
            WHERE id_licao NOT IN (
                SELECT id_licao
                FROM usuario_licao_realizada
                WHERE id_usuario = %s
            )
        """

        cursor.execute(query, (Session.current_user['id_user'],))
        resultados = cursor.fetchall()

        container = self.dash_licoes.widget()
        self.dash_licoes.setWidgetResizable(True)

        layout = container.layout()
        self.clearLayout(layout)

        for id_licao, titulo in resultados:
            label = QLabel(titulo)
            label.setStyleSheet("""
                 QLabel {
                     font-size: 14px;
                     color: white;
                     padding: 6px;
                 }
             """)
            layout.addWidget(label)

        cursor.execute(f"SELECT COUNT(*) FROM mensagens_chat WHERE destinatario_id = {Session.current_user['id_user']} AND lida = 0")
        contagem = cursor.fetchone()[0]
        self.lbl_novas_mensagens.setText(f"{contagem}")

        query = """
            SELECT DISTINCT u.id_user, u.nome
            FROM usuario u
            JOIN mensagens_chat m 
                ON m.remetente_id = u.id_user
            WHERE m.destinatario_id = %s
              AND m.lida = 0
        """

        cursor.execute(query, (Session.current_user['id_user'],))
        resultados = cursor.fetchall()

        container = self.dash_mensagens.widget()
        self.dash_mensagens.setWidgetResizable(True)

        layout = container.layout()
        self.clearLayout(layout)

        for id_user, nome in resultados:
            label = QLabel(nome)
            label.setStyleSheet("""
                 QLabel {
                     font-size: 14px;
                     color: white;
                     padding: 6px;
                 }
             """)
            layout.addWidget(label)

        cursor.close()
        db.close()

    def listarCalendario(self):
        container = self.scroll_agenda.widget()
        self.scroll_agenda.setWidgetResizable(True)

        layout = container.layout()
        self.clearLayout(layout)

        db = bancoDados().conectar()

        if not db:
            return

        cursor = db.cursor()
        cursor.execute("SELECT * FROM calendario")
        datas = cursor.fetchall()
        cursor.close()
        db.close()

        for id_calendario, titulo, descricao, data in datas:
            lista = {
                "nome" : titulo,
                "data" : data,
            }

            btn = agendaListada(lista)

            layout.addWidget(btn)

        layout.addStretch()



    def atualizarCalendario(self):
        db = bancoDados().conectar()

        if not db:
            return

        try:
            cursor = db.cursor()
            cursor.execute("SELECT data FROM calendario")
            datas = cursor.fetchall()
            cursor.close()
            db.close()

            formato_verde = QTextCharFormat()
            formato_verde.setBackground(QBrush(QColor("#90EE90")))  # Verde claro
            formato_verde.setForeground(QBrush(QColor("#000000")))

            self.widget_calendario.setDateTextFormat(QDate(), QTextCharFormat())

            # Marca as datas salvas
            for (data_mysql,) in datas:
                data_qt = QDate(data_mysql.year, data_mysql.month, data_mysql.day)
                self.widget_calendario.setDateTextFormat(data_qt, formato_verde)

        except mc.Error as e:
            QMessageBox.critical(self, "Erro", f"Erro ao buscar datas: {e}")

    def calendarioClique(self, date: QDate):
        data_str = date.toString("yyyy-MM-dd")
        db = bancoDados().conectar()
        if not db:
            return

        cursor = db.cursor()
        cursor.execute("SELECT * FROM calendario WHERE data = %s", (data_str,))
        resultado = cursor.fetchone()

        if resultado:
            id_evento, titulo, descricao, data = resultado

            popup = PopupVisualizarCal(self)
            popup.label_data.setText(date.toString("dd-MM-yyyy"))
            popup.lineEdit_titulo.setText(titulo)
            popup.textEdit_descricao.setPlainText(descricao)
            resultado_popup = popup.exec_()

        cursor.close()
        db.close()

    def atualizarPerfil(self, id):
        print(id)
        db = bancoDados().conectar()
        cursor = db.cursor()
        cursor.execute(f"SELECT id_user, nome, departamento, cargo, foto_perfil, sobre_mim, experiencias FROM usuario WHERE id_user = {id}")

        row = cursor.fetchone()

        if not (row is None):
            id_user, nome, departamento, cargo, foto_perfil, sobre_mim, experiencias = row

            self.btn_editar_perfil.setVisible(True if Session.current_user["id_user"] == id_user else False)

            self.nome_funcionario.setText(f'<html><head/><body><p><span style=" font-size:22pt;">{nome}</span></p></body></html>')
            self.cargo_func.setText(f'<html><head/><body><p><span style=" font-size:14pt;">{cargo}</span></p></body></html>')
            self.sobre_mim.setText(f'<html><head/><body><p><span style=" font-size:10pt;">{sobre_mim}</span></p></body></html>')
            self.experiencias.setText(f'<html><head/><body><p><span style=" font-size:9pt;">{experiencias}</span></p></body></html>')

            pixmap = QPixmap()
            pixmap.loadFromData(foto_perfil)  # converte bytes → QPixmap

            if pixmap.isNull():
                pixmap = QPixmap('../imagens/user.png')

            self.foto_funcionario.setPixmap(pixmap)

            if Session.loaded_chat:
                self.mudarTela(2, False)
                self.btn_perfil.setChecked(True)

            cursor.execute("SELECT foto_depto FROM departamento WHERE nome_depto = %s", (departamento,))
            row = cursor.fetchone()
            if row and row[0]:
                image_data = row[0]
                print(type(image_data), len(image_data))
                print(image_data[:20])
                pixmap = QPixmap()
                pixmap.loadFromData(image_data)  # converte bytes → QPixmap

                if pixmap.isNull():
                    pixmap = QPixmap('../imagens/logo new te.png')

                self.foto_aqui.setPixmap(pixmap)  # coloca na QLabel
                self.foto_aqui.setScaledContents(True)  # ajusta o tamanho automaticamente
                print("Imagem carregada com sucesso!")
            else:
                print("Nenhuma imagem encontrada para esse departamento.")
                pixmap = QPixmap('../imagens/logo new te.png')

                self.foto_aqui.setPixmap(pixmap)  # coloca na QLabel
                self.foto_aqui.setScaledContents(True)  # ajusta o tamanho automaticamente

    def abrirSobreMim(self):
        popup = PopupSobreMim(self)
        resultado = popup.exec_()  # Abre o popup de forma modal

        # Se o usuário confirmou (clicou em "Confirmar")
        if resultado == QDialog.Accepted:
            print("eba")
            valores = popup.valor_retornado
            db = bancoDados().conectar()

            if valores[0] == "" or valores[1] == "":
                QMessageBox.warning(self, "Aviso", "Preencha todos os campos!")
                return

            query = f"""
                              UPDATE usuario SET sobre_mim = '{valores[0]}', experiencias = '{valores[1]}' WHERE id_user = '{Session.current_user["id_user"]}';
                         """
            try:
                cursor = db.cursor()
                cursor.execute(query)
                db.commit()
                cursor.close()
                db.close()

                QMessageBox.information(self, "Sucesso", "Perfil atualizado!")
                self.atualizarPerfil(Session.current_user["id_user"])

            except mc.Error as err:
                print("Error:", err)
        else:
            print("Usuário cancelou o popup.")

    def mudarDashboard(self, index):
        if index == 0:
            self.listarCalendario()
            self.atualizarProgresso()
        if index == 2:
            self.licao_ativa = None
            self.atualizarLicoes()
        self.stacked_widget_botoes_principais_do_dashboard.setCurrentIndex(index)
        self.atualizarCalendario()

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
        Session.current_user = None

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
        for id_licao, id_user, titulo, desc, metas, criacao, validade, nomeArquivo, arquivo, tipo in rows:
            print(id_licao)
            row = i // 4
            col = i % 4
            template = licao()
            layout.addWidget(template, row, col)
            template.lbl_titulo_curso.setText(titulo)
            template.lbl_desc_curso.setText(desc)
            template.lbl_tipo_de_arquivo.setText("Nenhum" if (not nomeArquivo or not arquivo) else f"{nomeArquivo}")
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
        query = "SELECT titulo, conteudo, metas, nome_arquivo, arquivo, tipo FROM licoes WHERE id_licao = %s"
        cursor.execute(query, (id_licao,))
        result = cursor.fetchone()

        self.licao_ativa = id_licao

        if not (result is None):
            titulo, conteudo, metas, nomeArquivo, arquivo, tipo = result

            # self.titulo_cadastro_2.setText(f"Alterando {titulo} ({self.alterar})")

            self.lbl_titulo.setText(f'<html><head/><body><p><span style=" font-size:20pt;">{titulo}</span></p></body></html>')
            self.lbl_desc.setText(f'<html><head/><body><p><span style=" font-size:12pt;">{conteudo}</span></p></body></html>')
            self.lbl_metas.setText(f'<html><head/><body><p><span style=" font-size:10pt; font-weight:600; color:#d1d1d1;">{metas}</span></p></body></html>')
            self.label_anexo.setText(nomeArquivo)

            if arquivo:
                # nomeArquivo vem do banco (nome original). Para evitar problemas com caracteres,
                # você pode gerar um nome temporário seguro, mas aqui vamos usar o original.
                temp_path = os.path.join(tempfile.gettempdir(), nomeArquivo)

                # SALVA o arquivo antes de tentar medir / abrir
                try:
                    with open(temp_path, "wb") as f:
                        f.write(arquivo)
                except Exception as e:
                    QMessageBox.critical(self, "Erro ao salvar arquivo temporário", str(e))
                    cursor.close()
                    db.close()
                    return

                # Debug: confirmar que existe e qual tamanho
                try:
                    tamanho_bytes = os.path.getsize(temp_path)
                    print("Arquivo temporário salvo em:", temp_path)
                    print("Tamanho (bytes):", tamanho_bytes)
                except Exception as e:
                    print("Erro ao checar tamanho do temp file:", e)

                # Exibir dentro do app (VisualizadorArquivo fará fallback se necessário)
                viewer = VisualizadorArquivo(temp_path, tipo)
                viewer.exec_()

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

            btn.mensagens.setVisible(False)

            if user["mensagens"] > 0:
                btn.mensagens.setVisible(True)
                btn.mensagens.setText(f'{user["mensagens"]}')

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

        query = """
                 SELECT
                     u.id_user,
                     u.nome,
                     u.foto_perfil,
                     u.cargo,
                     u.status,
                     (
                         SELECT MAX(m.data_envio)
                         FROM mensagens_chat m
                         WHERE 
                             (m.remetente_id = u.id_user AND m.destinatario_id = %s)
                             OR
                             (m.destinatario_id = u.id_user AND m.remetente_id = %s)
                     ) AS data_envio
                 FROM usuario u
                 WHERE u.id_user != %s
                 ORDER BY data_envio DESC
             """
        current_id = Session.current_user["id_user"]

        cursor.execute(query, (current_id, current_id, current_id))
        results = cursor.fetchall()

        users = []
        for id_user, nome, foto_perfil, cargo, status, ultima_msg in results:
            pixmap = QPixmap()

            if foto_perfil:
                pixmap.loadFromData(foto_perfil)

            if pixmap.isNull():
                pixmap = QPixmap('../imagens/user.png')

            query = "SELECT COUNT(*) FROM mensagens_chat WHERE destinatario_id = %s AND lida = 0 AND remetente_id = %s"
            cursor.execute(query, (Session.current_user["id_user"], id_user))
            mensagens = cursor.fetchone()[0]

            users.append({
                "id_user": id_user,
                "nome": nome,
                "foto_perfil": pixmap,
                "cargo": cargo,
                "status": status,
                "mensagens": mensagens,
            })
            print(ultima_msg)

        cursor.close()
        db.close()

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
        text = filtrar_texto(self.lineEdit_mensagem.text())
        db = bancoDados().conectar()

        if text == "" or text is None:
            return

        self.lineEdit_mensagem.setText("")

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
        self.ListUsers()
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

    def mudarTela(self, index, update=True):
        if index == 2 and update:
            self.atualizarPerfil(Session.current_user["id_user"])
        if index == 1:
            self.ListUsers()
        if index == 0:
            self.atualizarProgresso()
        self.stack.setCurrentIndex(index)

    def logOut(self):
        self.chat_timer.stop()
        self.quitProgram()


        self.close()
        self.widget.setCurrentIndex(0)
        self.widget.show()