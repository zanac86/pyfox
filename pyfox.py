from PySide2 import QtCore, QtWidgets, QtGui
from PySide2.QtCore import QRect, QRectF, QSize, Qt, QTimer, QPoint
from PySide2.QtGui import QColor, QPainter, QPalette, QPen, QBrush, qRgb
from PySide2.QtWidgets import QApplication, QFrame, QVBoxLayout, QGridLayout
from PySide2.QtWidgets import QLabel, QSizePolicy, QWidget

import random


class Cell():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.Fox = False
        self.Found = False
        self.Radar = False
        self.Hint = False
        self.Count = 0


class Cells():
    def __init__(self, w, h, fox_max_count):
        self.w = w
        self.h = h
        self.field = [[Cell(x, y) for y in range(h)]for x in range(w)]
        self.foxes = []
        self.place_fox(fox_max_count)
        self.count_count()
        self.found_count = 0
        self.fox_max_count = fox_max_count

    def is_all_found(self):
        return self.fox_max_count == self.found_count

    def place_fox(self, fox_max_count):
        while len(self.foxes) < fox_max_count:
            while True:
                x, y = random.randrange(0, self.w), random.randrange(0, self.h)
                if not self.field[x][y].Fox:
                    self.field[x][y].Fox = True
                    self.foxes.append([x, y])
                    break
        print(self.foxes)

    def put_radar_at(self, x, y):
        if not self.is_valid_xy(x, y):
            return
        if self.field[x][y].Radar:
            return

        self.field[x][y].Radar = True
        if self.field[x][y].Fox:
            if not self.field[x][y].Found:
                self.found_count = self.found_count+1
            self.field[x][y].Found = True

        if self.field[x][y].Count == 0:
            self.mark_hint_from(x, y)

        self.update_hints()

    def is_view_fox_from(self, c, xy):
        found = (xy[0] == c.x) or (xy[1] == c.y)
        found = found or ((xy[1] - xy[0]) == (c.y-c.x))
        found = found or ((xy[1] + xy[0]) == (c.y+c.x))
        return found

    def is_valid_xy(self, x, y):
        if (x < 0 or x >= self.w) or (y < 0 or y >= self.h):
            return False
        return True

    def update_hints(self):
        for y in range(self.h):
            for x in range(self.w):
                if self.field[x][y].Radar:
                    count_found = self.count_found_from(x, y)
                    count = self.field[x][y].Count
                    if count > 0 and count_found == count:
                        self.mark_hint_from(x, y)

    def mark_hint_from(self, x, y):
        for i in range(self.w):
            self.field[i][y].Hint = True
        for i in range(self.h):
            self.field[x][i].Hint = True

        for i in range(self.w):
            xx = i
            yy = xx+(y-x)
            if self.is_valid_xy(xx, yy):
                self.field[xx][yy].Hint = True
            yy = -xx+(y+x)
            if self.is_valid_xy(xx, yy):
                self.field[xx][yy].Hint = True

    def count_found_from(self, x, y):
        count = 0
        for f in self.foxes:
            if self.is_view_fox_from(self.field[x][y], f) and self.field[f[0]][f[1]].Found:
                count = count+1
        return count

    def count_count(self):
        for y in range(self.h):
            for x in range(self.w):
                count = 0
                for f in self.foxes:
                    if self.is_view_fox_from(self.field[x][y], f):
                        count = count+1
                self.field[x][y].Count = count


class FieldWidget(QWidget):

    showClickStat = QtCore.Signal(str)

    def __init__(self, parent=None):
        super(FieldWidget, self).__init__(parent)
        self.ColorBackground = qRgb(0, 0, 0)
        self.ColorGrid = qRgb(0, 0, 160)
        self.ColorFox = qRgb(255, 0, 0)
        self.ColorRadar = qRgb(0, 160, 0)
        self.ColorHint = qRgb(250, 240, 0)
        # self.state = None
        self.board_size = (7, 7, 3)  # 7x7, 3 foxes
        self.board = None  # Cells(*self.board_size)
        self.setBackgroundRole(QPalette.Base)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.clickCount = 0

    def minimumSizeHint(self):
        return QSize(80, 80)

    def sizeHint(self):
        return QSize(240, 240)

    def paintNothing(self, painter):
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setPen(QPen(QColor(0, 0, 120, 255)))
        painter.drawRect(0, 0, self.width(), self.height())
        painter.setPen(QPen(Qt.red))
        # s = "Click on field to start"
        # painter.drawText(0, 0, self.width(), self.height(), Qt.AlignCenter, s)
        self.showClickStat.emit("Click on field to start")

    def paintField(self, painter):
        painter.setRenderHint(QPainter.Antialiasing, True)

        cw = int(self.width()/self.board.w)
        ch = int(self.height()/self.board.h)

        for y in range(self.board.h):
            for x in range(self.board.w):
                _x = x*cw
                _y = y*ch
                # QBrush(QColor("#a6ce39") )
                # painter.fillRect(event.rect(), QtGui.QBrush(QtCore.Qt.white))

                if self.board.is_all_found():
                    if self.board.field[x][y].Found:
                        c = self.ColorFox
                        painter.setPen(QPen(c))
                        painter.setBrush(QBrush(c, Qt.SolidPattern))
                        painter.drawEllipse(_x+2, _y+2, cw-4, ch-4)
                    painter.setPen(QPen(Qt.black))
                    s = "%d" % self.board.field[x][y].Count
                    painter.drawText(_x, _y, cw, ch, Qt.AlignCenter, s)
                    painter.setBrush(Qt.NoBrush)
                    painter.setPen(QPen(QColor(self.ColorGrid), 1))
                    painter.drawRect(_x, _y, cw, ch)
                    continue

                if self.board.field[x][y].Hint:
                    painter.setPen(QPen(QColor(self.ColorHint), 6))
                    painter.setBrush(Qt.NoBrush)
                    painter.drawEllipse(_x+2, _y+2, cw-4, ch-4)

                if self.board.field[x][y].Found:
                    # fox found
                    c = self.ColorFox
                    painter.setPen(QPen(c))
                    painter.setBrush(QBrush(c, Qt.SolidPattern))
                    painter.drawEllipse(_x+2, _y+2, cw-4, ch-4)
                elif self.board.field[x][y].Radar:
                    # radar here
                    c = self.ColorRadar
                    painter.setPen(QPen(QColor(c), 2))
                    painter.setBrush(QBrush(c, Qt.SolidPattern))
                    painter.setBrush(Qt.NoBrush)
                    painter.drawEllipse(_x+2, _y+2, cw-4, ch-4)

                painter.setBrush(Qt.NoBrush)
                painter.setPen(QPen(QColor(self.ColorGrid), 1))
                painter.drawRect(_x, _y, cw, ch)

                if self.board.field[x][y].Radar:
                    painter.setPen(QPen(Qt.black))
                    s = "%d" % self.board.field[x][y].Count
                    painter.drawText(_x, _y, cw, ch, Qt.AlignCenter, s)

        painter.setPen(QPen(QColor(0, 0, 120, 255)))
        painter.drawRect(0, 0, cw*self.board.w, ch*self.board.h)

    def paintEvent(self, event):
        painter = QPainter(self)
        if self.board is None:
            self.paintNothing(painter)
        else:
            self.paintField(painter)

    def getCellClicked(self, x, y):
        cw = int(self.width()/self.board.w)
        ch = int(self.height()/self.board.h)
        nx = int(int(x)/cw)
        ny = int(int(y)/ch)
        nx = -1 if nx >= self.board.w else nx
        ny = -1 if ny >= self.board.h else ny
        return nx, ny

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton or self.board is None:
            self.board = Cells(*self.board_size)
            self.clickCount = 0
            self.showClickStat.emit("Click on field to start")
            self.update()
            return

        if self.board.is_all_found():
            self.board = None
            self.update()
            return

        nx, ny = self.getCellClicked(event.pos().x(), event.pos().y())

        self.board.put_radar_at(nx, ny)
        print(nx, ny)

        self.clickCount = self.clickCount+1
        self.showClickStat.emit("Clicked {}, found {} from {}". format(
            self.clickCount, self.board.found_count, self.board.fox_max_count))

        self.update()

    def mouseMoveEvent(self, event):
        pass


class Window(QWidget):
    def __init__(self):
        super(Window, self).__init__()
        random.seed()

        layout = QVBoxLayout()
        self.field = FieldWidget()
        layout.addWidget(self.field)
        self.label = QLabel()
        layout.addWidget(self.label)

        self.setLayout(layout)
        self.setWindowTitle("fx")

        self.field.showClickStat.connect(self.printClickStat)

    @QtCore.Slot()
    def printClickStat(self, s):
        print(s)
        self.label.setText(s)


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
