import csv
import math
import sys
from datetime import datetime

import numpy as np
import pandas as pd
import pyqtgraph as pg
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QListWidget, QListWidgetItem


class WeightTracker(QMainWindow):
    def __init__(self):
        super().__init__()

        # 针对CSV文件提取绘图所需内容
        df = pd.read_csv('weight_data.csv', names=['date', 'weight'])
        row_count = df.shape[0]
        mean_weight = df['weight'].mean()
        coeff = mean_weight / (mean_weight + math.log(mean_weight))

        # 设置窗口标题和尺寸
        self.setWindowTitle("体重记录器")
        self.setGeometry(100, 100, 1000, 600)
        # 创建标签、输入框、按钮和列表部件
        self.weight_label = QLabel("当前体重 (kg):", self)
        self.weight_label.move(20, 20)
        self.weight_label.resize(120, 30)
        self.weight_input = QLineEdit(self)
        self.weight_input.move(160, 20)
        self.weight_input.resize(120, 30)
        # 创建列表并隐藏
        self.weight_list = QListWidget(self)
        self.weight_list.move(20, 60)
        self.weight_list.resize(260, 520)
        # 编辑列表项
        self.edit_button = QPushButton("删除所选记录", self)
        self.edit_button.move(300, 20)
        self.edit_button.resize(120, 30)
        self.edit_button.clicked.connect(self.edit_item)
        # 创建清除数据按钮
        self.clear_data_button = QPushButton("清除所有历史", self)
        self.clear_data_button.move(430, 20)
        self.clear_data_button.resize(120, 30)
        self.clear_data_button.clicked.connect(self.clear_data)
        self.clear_data_button.clicked.connect(self.weight_list.clear)
        self.clear_data_button.clicked.connect(self.update_plot)
        # 将按下回车连接到保存函数和刷新图表函数
        self.weight_input.returnPressed.connect(self.save_weight)
        self.weight_input.returnPressed.connect(self.update_plot)
        # 创建条形图画布
        self.plotWidget = pg.PlotWidget(self)
        self.plotWidget.move(300, 60)
        self.plotWidget.resize(680, 520)
        self.plotWidget.setBackground('w')
        self.plotWidget.showGrid(x=True, y=True)
        self.plotWidget.setLabel('left', '体重', units='kg', color='k')
        if row_count == 0:
            self.plotWidget.setYRange(0, 100)
            self.plotWidget.setXRange(0, 10)
        else:
            self.plotWidget.setYRange(mean_weight*coeff, mean_weight/coeff)
            self.plotWidget.setXRange(1, row_count)
        # 检测鼠标点击
        self.plotWidget.scene().sigMouseClicked.connect(self.mouse_clicked)
        # 读取CSV文件中的数据，并添加到列表部件中
        x = np.arange(1, row_count + 1, 1)
        y = []
        with open('weight_data.csv', mode='r') as file:
            reader = csv.reader(file)
            for row in reader:
                y.append(float(row[1]))
                item = QListWidgetItem(row[0] + " | " + row[1] + "kg", self.weight_list)
                self.weight_list.addItem(item)
        # 绘制折线图
        self.plotWidget.plot(x, y, pen='black', symbol='x', pensize=10, symbolPen='black', symbolBrush=0.2, symbolSize=10)

    def edit_item(self):
        # 获取当前选中的列表项
        item = self.weight_list.currentItem()
        self.weight_list.takeItem(self.weight_list.row(item))
        # 将剩下的数据保存到CSV文件中
        self.clear_data()
        for i in range(self.weight_list.count()):
            item = self.weight_list.item(i)
            text = item.text()
            text = text.split(" | ")
            with open('weight_data.csv', mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([text[0], text[1][:-2]])
        # 更新图表
        self.update_plot()

    # 清空CSV文件数据
    def clear_data(self):
        with open('weight_data.csv', mode='w') as file:
            file.truncate()

    def save_weight(self):
        # 获取当前日期和时间
        now = datetime.now()
        dt_string = now.strftime("%Y/%m/%d %H:%M")

        # 保存体重和日期/时间到CSV文件
        weight = self.weight_input.text()
        # 保留一位有效数字
        weight = "{:.1f}".format(float(weight))
        with open('weight_data.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([dt_string, weight])

        # 将新数据添加到列表部件中
        item = QListWidgetItem(dt_string + " | " + weight + "kg", self.weight_list)
        self.weight_list.addItem(item)
        # 清空输入框
        self.weight_input.clear()

    def update_plot(self):
        # 针对CSV文件提取绘图所需内容
        df = pd.read_csv('weight_data.csv',names=['date', 'weight'])
        row_count = df.shape[0]
        mean_weight = df['weight'].mean()
        coeff = mean_weight / (mean_weight + math.log(mean_weight))
        x = np.arange(1, row_count + 1, 1)
        y = []
        with open('weight_data.csv', mode='r') as file:
            reader = csv.reader(file)
            for row in reader:
                y.append(float(row[1]))
        self.plotWidget.clear()
        if row_count == 0:
            self.plotWidget.setYRange(0, 100)
            self.plotWidget.setXRange(0, 10)
        else:
            self.plotWidget.setYRange(mean_weight*coeff, mean_weight/coeff)
            self.plotWidget.setXRange(1, row_count)
        self.plotWidget.plot(x, y, pen='black', symbol='x', pensize=10, symbolPen='black', symbolBrush=0.2, symbolSize=10)

    # 子功能函数
    def clickmouse(self):
        self.plotWidget.scene().sigMouseClicked.connect(self.mouse_clicked)

    # 鼠标点击事件
    def mouse_clicked(self, event):
        if self.plotWidget is None:
            return

        pos = event.scenePos()
        point = self.plotWidget.plotItem.vb.mapSceneToView(pos)
        x = point.x()
        y = point.y()
        index = round(x)
        if abs(x - index) > 0.1:
            return
        else:
            data = self.plotWidget.getPlotItem().listDataItems()[0].yData[index - 1]
            if abs(y - data) > 0.1:
                return
            else:
                # 显示信息标签
                x1 = []
                y1 = []
                with open('weight_data.csv', mode='r') as file:
                    reader = csv.reader(file)
                    for row in reader:
                        x1.append(row[0])
                        y1.append(float(row[1]))
                    datetime = x1[index-1]
                    weight = y1[index-1]
                self.info_label = QLabel(self)
                self.info_label.setStyleSheet("QLabel {background-color:rgba(180,178,164,64);border:1px solid rgba(0,0,0,64);}")
                self.info_label.setText(f"记录时间：{datetime} \n体重：{weight}kg")
                self.info_label.setGeometry(int(pos.x()),
                                    int(pos.y()), 200, 60)
                self.info_label.adjustSize()
                self.timer = QTimer()
                self.info_label.show()
                self.timer.start(2000)
                self.timer.timeout.connect(self.info_label.hide)
                # 如果计时器正在计时，则禁用鼠标点击事件，等到计时器停止后再启用
                if self.timer.isActive():
                    self.plotWidget.scene().sigMouseClicked.disconnect(self.mouse_clicked)
                    self.timer.timeout.connect(self.clickmouse)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    tracker = WeightTracker()
    tracker.show()
    sys.exit(app.exec_())

