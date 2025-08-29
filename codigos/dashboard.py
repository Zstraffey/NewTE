import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QDialog, QApplication, QMainWindow, QMessageBox, QWidget, QPushButton
from PyQt5.uic import loadUi

import mysql.connector as mc

import imgs_rc

class TelaInicial(QMainWindow):
    def __init__(self):
        super(TelaInicial,self).__init__()
        loadUi("../design/NOVODASH.ui",self)

        self.stack = self.findChild(QWidget, "stackedwidget_btns_da_sidebar")
        self.dashboardStack = self.findChild(QWidget, "stacked_widget_botoes_principais_do_dashboard")

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

        for i, botao in enumerate(self.stackList, start=0):
            botao.clicked.connect(lambda _, idx=i: self.mudarTela(idx))

        for i, botao in enumerate(self.dashboardList, start=0):
            botao.clicked.connect(lambda _, idx=i: self.mudarDashboard(idx))

    def mudarTela(self, index):
        self.stack.setCurrentIndex(index)

    def mudarDashboard(self, index):
        self.dashboardStack.setCurrentIndex(index)