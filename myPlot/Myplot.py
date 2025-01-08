import os
import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QFileDialog, QVBoxLayout,QHBoxLayout, QWidget, QLabel, QSlider
)
from PySide6.QtGui import QKeyEvent
from PySide6.QtCore import Qt, QObject, QEvent
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar,
)
import matplotlib.pyplot as plt
import numpy as np

class KeyEventFilter(QObject):
    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress or event.type() == QEvent.KeyRelease:
            # 屏蔽键盘事件
            return True
        return super().eventFilter(obj, event)


class PlotWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 设置窗口标题和大小
        self.setWindowTitle("MYPlot")
        self.setGeometry(100, 100, 800, 600)
        # 设置主窗口的焦点策略
        # self.setFocusPolicy(Qt.StrongFocus)

        # 创建主控件
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)

        # 创建布局
        self.layout = QVBoxLayout(self.main_widget)

        # 添加选择目录按钮
        self.select_button = QPushButton("选择目录")
        self.select_button.clicked.connect(self.select_directory)
        self.layout.addWidget(self.select_button)
        self.select_button.setFocusPolicy(Qt.NoFocus)

        

        self.label1=QLabel("目录", self)
        self.label1.setMaximumHeight(30)
        self.layout.addWidget(self.label1)

        self.layout1 = QHBoxLayout(self.main_widget)
        self.label=QLabel("0 / 0", self)
        self.label.setMaximumHeight(30)
        self.layout1.addWidget(self.label,1)

        self.slider=QSlider(self)
        self.slider.setMaximumHeight(30)
        # self.slider.setMaximumWidth(450)
        self.slider.setOrientation(Qt.Horizontal)
        self.slider.valueChanged.connect(self.change_cnt)
        self.slider.setFocusPolicy(Qt.NoFocus)
        self.slider.setSingleStep(1)
        key_filter = KeyEventFilter()
        self.slider.installEventFilter(key_filter)

        self.layout1.addWidget(self.slider,1)

        self.layout.addLayout(self.layout1)

        # 添加 Matplotlib 画布
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(NavigationToolbar(self.canvas, self))
        self.layout.addWidget(self.canvas)
        self.ax = self.figure.gca()
        self.ax.grid(True)
        self.fileList=[]
        self.cnt=0
        self.directory=""

        self.key_press_flag=False

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        # self.label.setText(f"按下了键：{key}（{event.text()}）")
        # if(key==16777220 and self.cnt+1<len(self.fileList) ):
        if(event.key() == Qt.Key_Down and self.cnt+1<len(self.fileList) ):
            self.cnt+=1
            self.set_value()
        
        if(event.key() == Qt.Key_Up and self.cnt>0 ):
            self.cnt-=1
            self.set_value()

    def select_directory(self):
        # 打开文件选择对话框
        directory = QFileDialog.getExistingDirectory(self, "选择目录")
        if directory:
            # self.fileList=[f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
            self.fileList=self.list_files_sorted_by_time(directory)
            self.directory=directory
            self.label1.setText(f"目录：{directory}")
            self.cnt=0
            self.set_value()

    def set_value(self):
        length=len(self.fileList)
        val=(int) (self.cnt/length*100)
        self.key_press_flag=True
        self.slider.setValue(val)
        self.read_and_plot()
        
    
    def change_cnt(self,val):
        # 打开文件选择对话框
        length=len(self.fileList)
        if length <=0 :
            return
        if not self.key_press_flag:
            self.cnt=(int) (val*length/100)
            self.read_and_plot()
        self.key_press_flag=False
        
        # self.set_value()
    
    def list_files_sorted_by_time(self,directory):
        # 获取目录中的文件和文件夹列表
        items = os.listdir(directory)
    
        # 构造一个包含文件名和修改时间的列表，并按修改时间排序
        items_sorted = sorted(
        items,
        key=lambda item: os.path.getmtime(os.path.join(directory, item)))
        return items_sorted
        
        

    def read_and_plot(self):
        self.label.setText(f"{self.cnt} / {len(self.fileList)}")
        plt.cla()
        file=self.fileList[self.cnt]
        file_path = os.path.join(self.directory, file)
        data = self.read_file(file_path)
        data=data[:len(data)-35]
        x=self.getX(length=len(data))
        self.ax.plot(x,data)  # 绘制曲线
        self.ax.axvline(1305,linestyle="--",color='r')
        self.ax.grid(True)
        self.ax.set_title(file)
        self.canvas.draw()

    @staticmethod
    def read_file(file_path):
        # 示例读取文件数据，假设每行是一个数值
        with open(file_path, "r") as file:
            data = [float(line.strip()) for line in file]
        return np.array(data)
    
    @staticmethod
    def getX(starX=678.866, length=426,interval=1.9285):
        # 返回一组x下标
        x=[]
        for i in range(length):
            x.append(starX+i*interval)
        return np.array(x)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PlotWindow()
    window.show()
    sys.exit(app.exec())