import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem, QHBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt


class MplCanvas(FigureCanvas):
    def __init__(self, parent=None):
        fig, self.ax = plt.subplots(figsize=(6, 4))
        super().__init__(fig)


class Dashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dashboard de Tarefas")
        self.setGeometry(200, 200, 900, 500)

        # Layout principal
        main_layout = QHBoxLayout()

        # ----------- Tabela de Colaboradores -----------
        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Colaborador", "Quantidade", "Rendimento"])
        colaboradores = [
            ("Helena", 19, "+84%"),
            ("Oscar", 4, "+2%"),
            ("Daniel", 13, "-8%"),
            ("Daniel J. Park", 9, "+33%"),
            ("Mark Rojas", 17, "+30%")
        ]
        table.setRowCount(len(colaboradores))
        for i, (nome, qtd, rend) in enumerate(colaboradores):
            table.setItem(i, 0, QTableWidgetItem(nome))
            table.setItem(i, 1, QTableWidgetItem(str(qtd)))
            table.setItem(i, 2, QTableWidgetItem(rend))
        table.resizeColumnsToContents()

        # ----------- Gráfico -----------
        sc = MplCanvas(self)
        months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        values = [30,40,30,28,42,65,45,52,38,32,27,9]
        colors = ["red","green","red","red","green","green","red","green","red","red","red","green"]

        sc.ax.bar(months, values, color=colors)
        sc.ax.set_title("Realização de Tarefas no Ano")
        sc.ax.set_ylabel("Quantidade")

        chart_widget = QWidget()
        chart_layout = QVBoxLayout()
        chart_layout.addWidget(sc)
        chart_widget.setLayout(chart_layout)

        # Adiciona tabela + gráfico
        main_layout.addWidget(table, 40)
        main_layout.addWidget(chart_widget, 60)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Dashboard()
    window.show()
    sys.exit(app.exec_())
