import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QDialog, QApplication, QMainWindow, QMessageBox, QWidget
from PyQt5.uic import loadUi

import mysql.connector as mc

import imgs_rc

class TelaInicial(QMainWindow):
    def __init__(self):
        super(TelaInicial,self).__init__()
        loadUi("../design/NOVODASH.ui",self)

        self.stack = self.findChild(QWidget, "stackedwidget_btns_da_sidebar")
        #self.stackList = {"btn_home", "btn_chat","btn_config","btn_cadastro","btn_perfil"}

        #for i, botao in enumerate(self.stackList, start=0):
        #    print(i, botao)
        #    botao.clicked.connect(lambda: self.mudarTela(i))

        self.btn_home.clicked.connect(lambda: self.mudarTela(0))
        self.btn_chat.clicked.connect(lambda: self.mudarTela(1))
        self.btn_config.clicked.connect(lambda: self.mudarTela(2))
        self.btn_cadastro.clicked.connect(lambda: self.mudarTela(3))
        self.btn_perfil.clicked.connect(lambda: self.mudarTela(4))

        self.dashboardStack = self.findChild(QWidget, "stacked_widget_botoes_principais_do_dashboard")
        self.btn_rendimento_do_dash.clicked.connect(lambda : self.mudarDashboard(0))
        self.btn_func_do_dash.clicked.connect(lambda: self.mudarDashboard(1))
        self.btn_calendario_do_dash.clicked.connect(lambda: self.mudarDashboard(2))

    def mudarTela(self, index):
        self.stack.setCurrentIndex(index)

    def mudarDashboard(self, index):
        self.dashboardStack.setCurrentIndex(index)