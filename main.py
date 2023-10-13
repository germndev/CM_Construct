import sys, os, shutil, sqlite3, time, winreg, winshell

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.Qt import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from win32com.client import Dispatch
from random import randint
from library import *

class Connection(QGraphicsLineItem):
    def __init__(self, start, p2):
        super().__init__()

        self.start = start
        self.end = None
        self.line = QtCore.QLineF(start.scenePos(), p2)
        self.setLine(self.line)

        pen = QPen(QColor(153, 21, 214))
        pen.setWidth(7)
        self.setZValue(5)
        self.setPen(pen)

    def setEnd(self, end):
        self.end = end
        self.updateLine(end)
    def updateLine(self, source):
        if source == self.start: self.line.setP1(source.scenePos())
        else: self.line.setP2(source.scenePos())
        self.setLine(self.line)
class ControlPoint(QGraphicsEllipseItem):
    def __init__(self, parent):
        super().__init__(-5, -5, 10, 10, parent)
        self.lines = []
        self.setFlags(self.ItemSendsScenePositionChanges)
    def addLine(self, lineItem):
        self.lines.append(lineItem)
        return True
    def removeLine(self, lineItem):
        self.scene().removeItem(existing)
        self.lines.remove(existing)
    #обработчик для items(у которых уже есть line) для обновления line
    def itemChange(self, change, value):
        for line in self.lines: line.updateLine(self)
        return super().itemChange(change, value)
class CustomItem(QGraphicsItem):
    def __init__(self, x, y, Onleft, name, child, eventValue, DBpath, DBname, view):
        super().__init__()
        self.DBpath = DBpath
        self.DBname = DBname
        self.view = view

        if eventValue == 1: self.brush = QtGui.QBrush(QtGui.QColor(100, 76, 124))
        if eventValue == 2: self.brush = QtGui.QBrush(QtGui.QColor(83, 76, 125))
        if eventValue == 3: self.brush = QtGui.QBrush(QtGui.QColor(76, 105, 125))

        self.pen = QtGui.QPen(QtCore.Qt.black, 2)
        self.controlBrush = QtGui.QBrush(QtGui.QColor(214, 13, 36))
        self.rect = QtCore.QRectF(0, 0, 100, 100)

        self.setPos(x, y)
        self.setFlags(self.ItemIsMovable)
        self.controls = []

        control = ControlPoint(self)
        self.controls.append(control)
        control.setPen(self.pen)
        control.setBrush(self.controlBrush)

        if child:
            control2 = ControlPoint(self)
            self.controls.append(control2)
            control2.setPen(self.pen)
            control2.setBrush(self.controlBrush)

            control2.setX(90)
            control2.setY(10)

        textitem = QGraphicsTextItem(name[:8], self)
        font = QFont('Courier New', pointSize=8, weight=100)
        textitem.setFont(font)
        textitem.setDefaultTextColor(QColor(255, 255, 255))
        textitem.setX(15)
        textitem.setY(0)
        # textitem.setTextWidth(85)

        if Onleft: control.setX(90)
        else: control.setX(10)
        control.setY(10)

        self.setZValue(5)
        self.setAcceptHoverEvents(True)

    def boundingRect(self):
        adjust = self.pen.width() / 2
        return self.rect.adjusted(-adjust, -adjust, adjust, adjust)
    def paint(self, painter, option, widget=None):
        painter.save()
        painter.setPen(self.pen)
        painter.setBrush(self.brush)
        painter.drawRoundedRect(self.rect, 4, 4)
        painter.restore()

    def hoverEnterEvent(self, event):
        app.instance().setOverrideCursor(Qt.OpenHandCursor)
    def hoverLeaveEvent(self, event):
        app.instance().restoreOverrideCursor()
    def mousePressEvent(self, event):
        # self.selecteditem = SelectedItem(self.scenePos())
        # self.view.scene.addItem(self.selecteditem)
        try:
            print(self.view.scene.items())
            for i in self.view.scene.items():
                if 'SelectedItem' in str(i): self.selecteditem = i
            if int(self.selecteditem.scenePos().x()) == int(self.scenePos().x()) \
            and int(self.selecteditem.scenePos().y()) + 10 == int(self.scenePos().y()): self.selecteditem_move = True
            else: self.selecteditem_move = False
        except: self.selecteditem_move = False
    def mouseMoveEvent(self, event):
        orig_cursor_pos = event.lastScenePos()
        update_cursor_pos = event.scenePos()

        orig_pos = self.scenePos()

        update_cursor_x = update_cursor_pos.x() - orig_cursor_pos.x() + orig_pos.x()
        update_cursor_y = update_cursor_pos.y() - orig_cursor_pos.y() + orig_pos.y()

        self.setPos(QPointF(update_cursor_x, update_cursor_y))
        if self.selecteditem_move: self.selecteditem.setPos(QPointF(update_cursor_x, update_cursor_y - 10))
        else: print('nope')
        # self.selecteditem.setPos(QPointF(update_cursor_x, update_cursor_y - 10))
        # self.selecteditem.setZValue(6)
        self.setZValue(6)
    def mouseReleaseEvent(self, event):
        self.item = str(self)
        self.posx = int(self.scenePos().x())
        self.posy = int(self.scenePos().y())

        self.connect = sqlite3.connect(self.DBpath)
        self.cursor = self.connect.cursor()
        query = 'UPDATE "{table}" SET GIposx = ? WHERE graphicitem = ?'
        self.cursor.execute(query.format(table=self.DBname), (self.posx, self.item,))
        self.connect.commit()

        self.connect = sqlite3.connect(self.DBpath)
        self.cursor = self.connect.cursor()
        query = 'UPDATE "{table}" SET GIposy = ? WHERE graphicitem = ?'
        self.cursor.execute(query.format(table=self.DBname), (self.posy, self.item,))
        self.connect.commit()

        # self.view.scene.removeItem(self.selecteditem)
        self.setZValue(5)
class SelectedItem(QGraphicsItem):
    def __init__(self, x, y):
        super().__init__()
        self.pen = QtGui.QPen(QtCore.Qt.black, 2)
        self.brush = QtGui.QBrush(QtGui.QColor(219, 132, 0))
        self.controlBrush = QtGui.QBrush(QtGui.QColor(214, 13, 36))
        self.rect = QtCore.QRectF(25, 0, 50, 7)
        self.setPos(x, y-10)

        self.setFlags(self.ItemIsMovable)
        self.setAcceptHoverEvents(True)
    def boundingRect(self):
        adjust = self.pen.width() / 2
        return self.rect.adjusted(-adjust, -adjust, adjust, adjust)
    def paint(self, painter, option, widget=None):
        painter.save()
        painter.setPen(self.pen)
        painter.setBrush(self.brush)
        painter.drawRoundedRect(self.rect, 4, 4)
        painter.restore()

class Scene(QGraphicsScene):
    startItem = newConnection = None
    def lineConnect(self, item1, item2):
        self.newConnection = Connection(item1, item1.scenePos())
        self.addItem(self.newConnection)
        item1.addLine(self.newConnection)
        self.newConnection.setEnd(item2)
        item2.addLine(self.newConnection)
class EventPlaceFilter(QObject):
    MiddleMouseButton_pressed = pyqtSignal(float, float, QEvent)
    def __init__(self, widget):
        super().__init__(widget)
        self._widget = widget
        self.widget.installEventFilter(self)
        self.button_pressed = False
    @property
    def widget(self):
        return self._widget
    def eventFilter(self, source, event):
        if (event.type() == 156 and event.button() == Qt.MiddleButton):
            self.button_pressed = True
            self.old_x = event.scenePos().x()
            self.old_y = event.scenePos().y()
        if (event.type() == 157 and event.button() == Qt.MiddleButton):
            self.button_pressed = False
        if (event.type() == 155 and self.button_pressed):
            update_x = event.scenePos().x()
            update_y = event.scenePos().y()

            delta_x = update_x - self.old_x
            delta_y = update_y - self.old_y

            self.MiddleMouseButton_pressed.emit(delta_x, delta_y, event)
        return super(EventPlaceFilter, self).eventFilter(source, event)
class GraphicView(QGraphicsView):
    def __init__(self):
        super().__init__()

        self.x = 0
        self.y = 0
        self.d1 = 100
        self.d2 = 100
        self.scalling1 = 0
        self.scalling2 = 0
        self.wheel = True

        self.scene = Scene()
        self.setScene(self.scene)
        self.setSceneRect(self.x, self.y, self.d1, self.d2)

        self.setRenderHints(QtGui.QPainter.Antialiasing)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(30, 30, 30)))
        self.setFrameShape(QtWidgets.QFrame.NoFrame)

        self.eventFilter = EventPlaceFilter(self.scene)
        self.eventFilter.MiddleMouseButton_pressed.connect(self.trigger)
    def trigger(self, delta_x, delta_y, event):
        self.x -= delta_x
        self.y -= delta_y

        self.setSceneRect(self.x, self.y, self.d1, self.d2)
    def wheelEvent(self, event):
        zoomInFactor = 1.25
        zoomOutFactor = 1 / zoomInFactor

        oldPos = self.mapToScene(event.pos())

        if event.angleDelta().y() > 0:
            zoomFactor = zoomInFactor
            if self.scalling1 > 8.75: self.scalling1 = 8.75
            if self.scalling2 < -5.6: self.scalling2 = -5.6

            self.scalling1 += zoomFactor
            self.scalling2 -= zoomOutFactor
        else:
            zoomFactor = zoomOutFactor
            if self.scalling2 > 5.6: self.scalling2 = 5.6
            if self.scalling1 < -8.75: self.scalling1 = -8.75

            self.scalling2 += zoomOutFactor
            self.scalling1 -= zoomInFactor

        if (self.scalling1 <= 8.75 and self.scalling1 >= -8.75) and (self.scalling2 <= 5.6 and self.scalling2 >= -5.6):
            self.scale(zoomFactor, zoomFactor)

        newPos = self.mapToScene(event.pos())
        delta = newPos - oldPos

        self.translate(delta.x(), delta.y())

class paramWindow(QWidget):
    def __init__(self, tree, eventValue, parent, child, DBname, DBpath, child2, view):
        super(paramWindow, self).__init__()
        self.setWindowIcon(QtGui.QIcon('icon.jpg'))
        self.setWindowTitle('Настройка параметров')
        self.setFixedSize(420, 400)

        self.initUI()

        self.paramlist = []
        self.eventValue = eventValue

        self.tree = tree
        self.child = child
        self.parent = parent
        self.DBname = DBname
        self.DBpath = DBpath
        self.child2 = child2

        self.view = view
    def initUI(self):
        #container
        #width, height = 420, 380
        #
        # container = QWidget(self)
        # container.setFixedSize(width, height)
        # container.move(x_pos, y_pos)
        # container.setStyleSheet("background-color:salmon;")
        #accept button
        self.button = QPushButton('Show', self)
        self.button.resize(400, 23)
        self.button.move(10, 370)
        self.button.clicked.connect(self.btnClose)
        #name qline
        self.qle = QLineEdit(self, placeholderText='Name...', clearButtonEnabled=True)
        self.qle.resize(200, 23)
        self.qle.move(10, 10)
        #param text box(programming language)
        self.plainText = QPlainTextEdit(self)
        self.plainText.resize(400, 300)
        self.plainText.move(10, 60)
        self.plainText.setPlaceholderText("This is some text for our plaintextedit")
        #self.plainText.appendPlainText('params')
        self.plainText.setUndoRedoEnabled(True)
        #comboboxes
        self.box1 = QComboBox(self)
        self.box1.setFixedSize(100, 20)
        self.box1.move(10, 37)
        self.box1.addItems(list1)
        self.box1.currentTextChanged.connect(self.trigger)

        self.box2 = QComboBox(self)
        self.box2.setFixedSize(100, 20)
        self.box2.move(110, 37)
        self.box2.addItems(list2)
        self.box2.currentTextChanged.connect(self.trigger)

        self.box3 = QComboBox(self)
        self.box3.setFixedSize(100, 20)
        self.box3.move(210, 37)
        self.box3.addItems(list3)
        self.box3.currentTextChanged.connect(self.trigger)

        self.box4 = QComboBox(self)
        self.box4.setFixedSize(100, 20)
        self.box4.move(310, 37)
        self.box4.addItems(list4)
        self.box4.currentTextChanged.connect(self.trigger)
        #contain
        # self.vbox = QVBoxLayout(container)
        #
        # self.vbox.addWidget(self.qle)
        # self.vbox.addWidget(self.plainText)
        # self.vbox.addWidget(self.button)
        # self.setLayout(self.vbox)

        self.qle.setFocus()
        self.show()
    def trigger(self, value):
        self.plainText.appendPlainText('{' + value + '};')
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return:
            text = self.qle.text()
            if len(text) != 0: self.btnClose()
    def btnClose(self):
        global child2_index
        if len(self.qle.text()) != 0:
            self.text = self.qle.text()

            self.connect = sqlite3.connect(self.DBpath)
            self.cursor = self.connect.cursor()

            if self.eventValue == 1:
                query = 'SELECT n FROM "{table}" WHERE type = ? AND name = ?'
                self.cursor.execute(query.format(table=self.DBname), (self.eventValue, self.text,))
                self.child = 0
                child2_index = 0
            if self.eventValue == 2:
                query = 'SELECT n FROM "{table}" WHERE type = ? AND name = ? AND parent = ?'
                self.cursor.execute(query.format(table=self.DBname), (self.eventValue, self.text, self.parent,))
                child2_index = 0
            if self.eventValue == 3:
                query = 'SELECT n FROM "{table}" WHERE type = ? AND name = ? AND parent = ? AND child = ?'
                self.cursor.execute(query.format(table=self.DBname), (self.eventValue, self.text, self.parent, self.child,))
                child2_index = self.child2

            data = self.cursor.fetchone()
            if data is None:
                self.item = QTreeWidgetItem(self.tree)
                self.item.setText(0, self.text)
                self.ADDitem()

                query = 'SELECT n FROM "{table}"'
                self.cursor.execute(query.format(table=self.DBname))
                data = self.cursor.fetchall()

                self.N = len(data)
                hostparam = self.plainText.toPlainText()
                list = (self.N, self.eventValue, self.text, self.parent, self.child, child2_index, hostparam, 1, str(self.item), self.posx, self.posy)

                query = 'INSERT INTO "{table}"(n, type, name, parent, child, child2,' \
                        ' hostparam, dynamic, graphicitem, GIposx, GIposy) VALUES(?,?,?,?,?,?,?,?,?,?,?);'
                self.cursor.executemany(query.format(table=self.DBname), (list,))
                self.connect.commit()

                self.close()
            else: pass
    def ADDitem(self):
        self.connect = sqlite3.connect(self.DBpath)
        self.cursor = self.connect.cursor()

        scene = self.view.scene

        if self.eventValue == 1:
            self.posx = 0
            self.posy = 0
            self.item = CustomItem(self.posx, self.posy, True, self.text, False, self.eventValue, self.DBpath, self.DBname, self.view)
            scene.addItem(self.item)
        if self.eventValue == 2:
            query = 'SELECT graphicitem FROM "{table}" WHERE type = ? AND parent = ?'
            self.cursor.execute(query.format(table=self.DBname), (1, self.parent,))

            data = self.cursor.fetchone()
            self.mainItem = data[0]

            for i in (scene.items()):
                if str(i) == self.mainItem: self.mainItem = i

            self.posx = self.mainItem.pos().x() + 100
            self.posy = self.mainItem.pos().y()

            self.item = CustomItem(self.posx, self.posy, False, self.text, True, self.eventValue, self.DBpath, self.DBname, self.view)
            scene.addItem(self.item)
            scene.lineConnect(self.mainItem.childItems()[0], self.item.childItems()[0])
        if self.eventValue == 3:
            query = 'SELECT graphicitem FROM "{table}" WHERE type = ? AND parent = ? AND child = ?'
            self.cursor.execute(query.format(table=self.DBname), (2, self.parent, self.child))

            data = self.cursor.fetchone()
            self.mainItem = data[0]
            for i in (scene.items()):
                if str(i) == self.mainItem: self.mainItem = i

            self.posx = self.mainItem.pos().x() + 100
            self.posy = self.mainItem.pos().y()
            self.item = CustomItem(self.posx, self.posy, False, self.text, False, self.eventValue, self.DBpath, self.DBname, self.view)
            scene.addItem(self.item)
            scene.lineConnect(self.mainItem.childItems()[1], self.item.childItems()[0])
class EventFilter(QObject):
    mouseButton_pressed = pyqtSignal()
    def __init__(self, widget):
        super().__init__(widget)
        self._widget = widget
        self.widget.viewport().installEventFilter(self)
    @property
    def widget(self):
        return self._widget
    def eventFilter(self, source, event):
        if (event.type() == QtCore.QEvent.MouseButtonPress and source is self.widget.viewport()):
            self.mouseButton_pressed.emit()
        return super(EventFilter, self).eventFilter(source, event)
    # def eventFilter(self, object: QObject, event: QEvent):
    #     if object is self.widget and event.type() == QEvent.MouseButtonPress:
    #         print('OK!')
    #         self.mouseButton_pressed.emit()
    #     return super().eventFilter(object, event)
class MainWindow(QMainWindow):
    def __init__(self, DBname, DBpath, fileIsNew):
        super().__init__()
        self.DBname = DBname
        self.DBpath = DBpath

        self.setWindowTitle('CMconstruct: ' + self.DBpath)
        self.setWindowIcon(QtGui.QIcon('icon.jpg'))
        self.statusBar().showMessage('...')

        # self.screen = app.primaryScreen()
        # self.size = self.screen.size()
        # self.resize(self.size)
        self.resize(1280, 720)
        # self.setFixedSize(1280, 720)

        self.child = 0
        self.parent = 0
        self.child2 = 0
        self.counter = 0
        self.index_list = []

        self.setMouseTracking(True)
        self.childEnabled = False
        self.parentEnabled = False
        self.filesaved = not fileIsNew
        self.fileIsNew = fileIsNew

        self.initUI()

    def initUI(self):
        self.createMenuBar()
        self.createTables()
        self.DBLoader()
        self.HKsetting()
        # eventFilter - вызов класса EventFilter, которому мы передаем наши 3 виджета
        # TreeWidget для обработки событий именно в этих объектах
        eventFilter = EventFilter(self.treeView1)
        eventFilter.mouseButton_pressed.connect(self.handle_tree1)
        eventFilter = EventFilter(self.treeView2)
        eventFilter.mouseButton_pressed.connect(self.handle_tree2)
        eventFilter = EventFilter(self.treeView3)
        eventFilter.mouseButton_pressed.connect(self.handle_tree3)
    def loadUI(self):
        self.treeView1.clear()
        self.treeView2.clear()
        self.treeView3.clear()
        self.plain6.scene.clear()

        self.connect = sqlite3.connect(self.DBpath)
        self.cursor = self.connect.cursor()

        query = 'SELECT name FROM "{table}" WHERE type = ?'
        self.cursor.execute(query.format(table=self.DBname), (1,))
        data = self.cursor.fetchall()
        for i in data:
            self.item = QTreeWidgetItem(self.treeView1)
            self.item.setText(0, str(i[0]))

        query = 'SELECT name FROM "{table}" WHERE type = ?'
        self.cursor.execute(query.format(table=self.DBname), (2,))
        data = self.cursor.fetchall()
        for i in data:
            self.item = QTreeWidgetItem(self.treeView2)
            self.item.setText(0, str(i[0]))

        query = 'SELECT name FROM "{table}" WHERE type = ?'
        self.cursor.execute(query.format(table=self.DBname), (3,))
        data = self.cursor.fetchall()
        for i in data:
            self.item = QTreeWidgetItem(self.treeView3)
            self.item.setText(0, str(i[0]))

        query = 'SELECT * FROM "{table}"'
        self.cursor.execute(query.format(table=self.DBname))
        data = self.cursor.fetchall()
        for i in range(len(data)):
            self.connect = sqlite3.connect(self.DBpath)
            self.cursor = self.connect.cursor()

            posx = data[i][9]
            posy = data[i][10]
            type = data[i][1]
            name = data[i][2]
            parent = data[i][3]
            child = data[i][4]
            olditem = data[i][8]

            if type == 1:
                newitem = CustomItem(posx, posy, True, name, False, 1, self.DBpath, self.DBname, self.plain6)
                self.plain6.scene.addItem(newitem)
            if type == 2:
                newitem = CustomItem(posx, posy, False, name, True, 2, self.DBpath, self.DBname, self.plain6)
                self.plain6.scene.addItem(newitem)
            if type == 3:
                newitem = CustomItem(posx, posy, False, name, False, 3, self.DBpath, self.DBname, self.plain6)
                self.plain6.scene.addItem(newitem)

            query = 'UPDATE "{table}" SET graphicitem = ? WHERE graphicitem = ?'
            self.cursor.execute(query.format(table=self.DBname), (str(newitem), olditem))
            self.connect.commit()

            self.connect = sqlite3.connect(self.DBpath)
            self.cursor = self.connect.cursor()

            if type == 2:
                query = 'SELECT graphicitem FROM "{table}" WHERE type = ? AND parent = ?'
                self.cursor.execute(query.format(table=self.DBname), (1, parent,))

                data1 = self.cursor.fetchone()
                mainItem = data1[0]

                for i in (self.plain6.scene.items()):
                    if str(i) == mainItem: mainItem = i

                self.plain6.scene.lineConnect(mainItem.childItems()[0], newitem.childItems()[0])
            if type == 3:
                query = 'SELECT graphicitem FROM "{table}" WHERE type = ? AND child = ?'
                self.cursor.execute(query.format(table=self.DBname), (2, child,))

                data1 = self.cursor.fetchone()
                mainItem = data1[0]
                for i in (self.plain6.scene.items()):
                    if str(i) == mainItem: mainItem = i

                self.plain6.scene.lineConnect(mainItem.childItems()[1], newitem.childItems()[0])

        self.connect = sqlite3.connect(self.DBpath)
        self.cursor = self.connect.cursor()

        query = 'SELECT parent FROM "{table}"'
        self.cursor.execute(query.format(table=self.DBname))
        data = self.cursor.fetchall()
        self.parentIndex = max(data)[0]
        self.parent = self.parentIndex + 1

        query = 'SELECT child FROM "{table}"'
        self.cursor.execute(query.format(table=self.DBname))
        data = self.cursor.fetchall()
        self.childIndex = max(data)[0]
        self.child = self.childIndex + 1

        query = 'SELECT child2 FROM "{table}"'
        self.cursor.execute(query.format(table=self.DBname))
        data = self.cursor.fetchall()
        self.child2 = max(data)[0] + 1

    # Создание рабочих пространств
    def createTables(self):
            # x_pos, y_pos = 5, 50
            # width, height = 840, 668
            #
            # container = QWidget(self)
            # container.setContentsMargins(0, 0, 0, 0)
            # container.setFixedSize(width, height)
            # container.move(x_pos, y_pos)
            # container.setStyleSheet("background-color:salmon;")
            # tree1
            self.treeView1 = QTreeWidget(self)
            self.item1 = QTreeWidgetItem()
            self.treeView1.setHeaderHidden(True)
            self.treeView1.itemClicked.connect(self.onItemClicked)

            self.scroll_bar = QScrollBar(self)
            self.scroll_bar.setStyleSheet("background : white;")
            self.treeView1.setVerticalScrollBar(self.scroll_bar)

            self.treeView1.resize(300, 440)
            self.treeView1.move(160, 120)

            self.treeView1.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            self.treeView1.customContextMenuRequested.connect(self.context)
            # tree2
            self.treeView2 = QTreeWidget(self)
            self.item2 = QTreeWidgetItem()
            self.treeView2.setHeaderHidden(True)
            self.treeView2.itemClicked.connect(self.onItemClicked)

            self.scroll_bar = QScrollBar(self)
            self.scroll_bar.setStyleSheet("background : white;")
            self.treeView2.setVerticalScrollBar(self.scroll_bar)

            self.treeView2.resize(300, 440)
            self.treeView2.move(470, 120)

            self.treeView2.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            self.treeView2.customContextMenuRequested.connect(self.context)
            # tree3
            self.treeView3 = QTreeWidget(self)
            self.item3 = QTreeWidgetItem()
            self.treeView3.setHeaderHidden(True)
            self.treeView3.itemClicked.connect(self.onItemClicked)

            self.scroll_bar = QScrollBar(self)
            self.scroll_bar.setStyleSheet("background : white;")
            self.treeView3.setVerticalScrollBar(self.scroll_bar)

            self.treeView3.resize(300, 440)
            self.treeView3.move(780, 120)

            self.treeView3.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            self.treeView3.customContextMenuRequested.connect(self.context)
            # contain trees
            self.groupBox = QGroupBox()

            self.hbox = QHBoxLayout()

            self.hbox.addWidget(self.treeView1)
            self.hbox.addWidget(self.treeView2)
            self.hbox.addWidget(self.treeView3)

            self.groupBox.setLayout(self.hbox)

            self.dockWidget0 = QDockWidget()
            self.dockWidget0.setWidget(self.groupBox)
            self.dockWidget0.setFloating(False)
            self.addDockWidget(Qt.LeftDockWidgetArea, self.dockWidget0)

            # self.dockWidget0.setMinimumSize(240, 668)
            # create tabs

            x_pos, y_pos = 850, 50
            width, height = 425, 325
            #
            # container = QWidget(self)
            # container.setContentsMargins(0, 0, 0, 0)
            # container.setFixedSize(width, height)
            # container.move(x_pos, y_pos)
            # container.setStyleSheet("background-color:salmon;")

            self.hbox = QHBoxLayout()
            self.hbox.setContentsMargins(0, 0, 0, 0)

            self.tabs = QTabWidget()
            self.tab1 = QWidget()
            self.tab2 = QGroupBox()
            self.tab3 = QWidget()
            self.tab4 = QWidget()

            self.scroll = QScrollArea()
            self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
            self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

            self.tabs.addTab(self.tab1, "INFO")
            self.tabs.addTab(self.scroll, "PARAMS")
            self.tabs.addTab(self.tab3, "LIBRARY")
            self.tabs.addTab(self.tab4, "LOGGER")

            self.tab1_layout = QVBoxLayout(self.tab1)
            self.tab2_layout = QFormLayout(self.tab2)
            self.tab3_layout = QVBoxLayout(self.tab3)
            self.tab4_layout = QVBoxLayout(self.tab4)

            self.plain1 = QPlainTextEdit(self)
            self.plain1.setPlaceholderText("This is some text for our plaintextedit")
            self.plain1.setUndoRedoEnabled(True)

            # self.plain2 = QLineEdit(self)
            # self.plain2.setFixedSize(150, 25)
            # self.plain2.setPlaceholderText("Name...")
            #
            # self.button_minus = QPushButton("-")
            # self.button_minus.setFixedSize(25, 25)
            # self.button_minus.clicked.connect(self.DELparam)

            # self.checkbox = QCheckBox()
            # self.checkBoxA.stateChanged.connect(self.CBtrigger)

            # self.combobox = QComboBox(self)
            # self.combobox.setFixedSize(150, 25)
            # self.combobox.addItems(list1)

            self.button_plus = QPushButton("+")
            self.button_plus.setFixedSize(25, 25)
            self.button_plus.clicked.connect(self.ADDparam)

            self.plain3 = QPlainTextEdit(self)
            self.plain3.setPlaceholderText("This is some text for our plaintextedit")
            self.plain3.setUndoRedoEnabled(True)

            self.plain4 = QPlainTextEdit(self)
            self.plain4.setPlaceholderText("This is some text for our plaintextedit")
            self.plain4.setUndoRedoEnabled(True)

            # self.tab2_layout_form = QHBoxLayout()
            # self.tab2_layout_form.addWidget(self.plain2)
            # self.tab2_layout_form.addWidget(self.combobox)
            # self.tab2_layout_form.addWidget(self.checkbox)
            # self.tab2_layout_form.addWidget(self.button_minus)

            self.tab1_layout.addWidget(self.plain1)
            # self.tab2_layout.addRow(self.tab2_layout_form)
            self.tab2_layout.addRow(self.button_plus)
            self.tab3_layout.addWidget(self.plain3)
            self.tab4_layout.addWidget(self.plain4)

            self.tab1.setLayout(self.tab1_layout)
            self.tab2.setLayout(self.tab2_layout)
            self.tab3.setLayout(self.tab3_layout)
            self.tab4.setLayout(self.tab4_layout)

            # self.tab2.layout.setSpacing(2)
            # self.tab2.layout.setContentsMargins(10, 5, 0, 0)
            # self.tab2.layout.setAlignment(Qt.AlignTop)

            self.scroll.setWidget(self.tab2)
            self.scroll.setWidgetResizable(True)
            self.scroll.resize(width, height)

            self.hbox.addWidget(self.tabs)
            self.setLayout(self.hbox)

            # x_pos, y_pos = 850, 50
            # width, height = 425, 325
            #
            # container = QWidget(self)
            # container.setContentsMargins(0, 0, 0, 0)
            # container.setFixedSize(width, height)
            # container.move(x_pos, y_pos)
            # #container.setStyleSheet("background-color:salmon;")
            # self.hbox = QHBoxLayout(container)
            # self.hbox.setContentsMargins(0, 0, 0, 0)

            self.dockWidget = QDockWidget()
            self.dockWidget.setWidget(self.tabs)
            self.dockWidget.setFloating(False)
            self.addDockWidget(Qt.RightDockWidgetArea, self.dockWidget)
            self.dockWidget.setMaximumSize(800, 700)

            # create tabs2
            # x_pos, y_pos = 850, 375
            # width, height = 425, 325
            #
            # container = QWidget(self)
            # container.setContentsMargins(0, 0, 0, 0)
            # container.setFixedSize(width, height)
            # container.move(x_pos, y_pos)
            # container.setStyleSheet("background-color:salmon;")
            self.hbox2 = QHBoxLayout()
            self.hbox2.setContentsMargins(0, 0, 0, 0)

            self.tabs2 = QTabWidget()

            self.tab5 = QWidget()
            self.tab6 = QWidget()

            self.tabs2.addTab(self.tab5, "TAB1")
            self.tabs2.addTab(self.tab6, "TAB2")

            self.tab5_layout = QVBoxLayout(self)
            self.tab6_layout = QHBoxLayout(self)

            self.plain5 = QPlainTextEdit(self)
            self.plain5.appendPlainText('1')
            self.plain5.setUndoRedoEnabled(True)

            self.plain6 = GraphicView()
            # self.toolbar_widget = QWidget()
            # self.toolbar_layout = QVBoxLayout()

            # self.act = QAction(QIcon("icon.jpg"), 'act', self)
            # self.act2 = QAction(QIcon("act.jpg"), 'act', self)
            # self.toolbar.addWidget(QSlider())
            # self.toolbar.addAction(self.act)
            # self.toolbar.addAction(self.act2)

            # self.toolbutton = QPushButton()
            # self.toolbutton.setIcon(QIcon('icon.jpg'))

            # self.toolbar_layout.addWidget(QSlider())
            # self.toolbar_layout.addWidget(self.toolbutton)
            # self.toolbar_widget.setLayout(self.toolbar_layout)

            self.tab5_layout.addWidget(self.plain5)
            self.tab6_layout.addWidget(self.plain6)
            # self.tab6_layout.addWidget(self.toolbar_widget)

            self.tab5.setLayout(self.tab5_layout)
            self.tab6.setLayout(self.tab6_layout)
            # self.toolbar_widget.setLayout(self.toolbar_layout)

            self.hbox2.addWidget(self.tabs2)
            self.setLayout(self.hbox2)

            self.dockWidget2 = QDockWidget()
            self.dockWidget2.setWidget(self.tabs2)
            self.dockWidget2.setFloating(False)
            self.addDockWidget(Qt.RightDockWidgetArea, self.dockWidget2)
            # self.dockWidget2.setMaximumSize(800, 700)

            #create stylesheet
            # self.setStyleSheet("QTreeWidget {background-color: green}"
            #                    "QDockWidget {background-color: green}"
            #                    "QTabWidget {background-color: green}"
            #                    "QWidget {background-color: green}"
            #                    "QHBoxLayout {background-color: green}")
    # Создание верхнего контекстного меню
    def createMenuBar(self):
            menuBar = self.menuBar()

            fileMenu = QMenu("File", self)
            menuBar.addMenu(fileMenu)

            newAction = QtWidgets.QAction('New', fileMenu)
            newAction.triggered.connect(lambda: self.newFile())
            openAction = QtWidgets.QAction('Open', fileMenu)
            openAction.triggered.connect(lambda: self.openFile())
            saveAction = QtWidgets.QAction('Save', fileMenu)
            saveAction.triggered.connect(lambda: self.saveFile())
            saveAsAction = QtWidgets.QAction('Save as', fileMenu)
            saveAsAction.triggered.connect(lambda: self.saveAsFile())

            fileMenu.addAction(newAction)
            fileMenu.addAction(openAction)
            fileMenu.addAction(saveAction)
            fileMenu.addAction(saveAsAction)

            newAction.setShortcut("Ctrl+N")
            openAction.setShortcut("Ctrl+O")
            saveAction.setShortcut("Ctrl+S")
            saveAsAction.setShortcut("Ctrl+Shift+S")

            editMenu = QMenu("Edit", self)
            menuBar.addMenu(editMenu)
            dockWidgetmenu = QMenu("DockWodgets", self)
            editMenu.addMenu(dockWidgetmenu)

            dockWidget_trees = QtWidgets.QAction('DW-Trees', fileMenu)
            dockWidget_trees.triggered.connect(lambda: self.dockWidget0.setVisible(True))
            dockWidget_top = QtWidgets.QAction('DW-Top', fileMenu)
            dockWidget_top.triggered.connect(lambda: self.dockWidget.setVisible(True))
            dockWidget_down = QtWidgets.QAction('DW-Down', fileMenu)
            dockWidget_down.triggered.connect(lambda: self.dockWidget2.setVisible(True))

            dockWidgetmenu.addAction(dockWidget_trees)
            dockWidgetmenu.addAction(dockWidget_top)
            dockWidgetmenu.addAction(dockWidget_down)

            helpMenu = menuBar.addMenu("Help")
    # Контекстное меню по ПКМ
    def context(self, event):
            menu = QtWidgets.QMenu()

            eventlist = [1, 2, 3]

            if self.eventValue == 1: self.tree = self.treeView1
            if self.eventValue == 2: self.tree = self.treeView2
            if self.eventValue == 3: self.tree = self.treeView3

            try:
                self.name = self.tree.itemAt(event).text(0)
                self.isClicked = True
                # print(self.name, self.isClicked)
            except:
                pass

            if self.eventValue in eventlist:
                newAction = QtWidgets.QAction('New', menu)
                newAction.triggered.connect(lambda: self.DBinsert(self.eventValue))

                editAction = QtWidgets.QAction('Edit', menu)

                copyAction = QtWidgets.QAction('Copy', menu)

                pastAction = QtWidgets.QAction('Past', menu)

                deleteAction = QtWidgets.QAction('Delete', menu)
                deleteAction.triggered.connect(lambda: self.DBdelete())

                menu.addAction(newAction)
                menu.addAction(editAction)
                menu.addAction(copyAction)
                menu.addAction(pastAction)
                menu.addAction(deleteAction)

                menu.exec(self.tree.mapToGlobal(event))

    #HK
    def DBhk1(self):
        self.DBinsert(1)
    def DBhk2(self):
        self.DBinsert(2)
    def DBhk3(self):
        self.DBinsert(3)
    def HKsetting(self):
        # keyboard.add_hotkey("ctrl+a+1", lambda: self.DBinsert(1))
        # keyboard.add_hotkey("ctrl+a+2", lambda: self.DBinsert(2))
        # keyboard.add_hotkey("ctrl+a+3", lambda: self.DBinsert(3))
        # keyboard.wait()
        self.shortcut1 = QShortcut(QKeySequence("Ctrl+q"), self)
        self.shortcut1.activated.connect(self.DBhk1)
        self.shortcut2 = QShortcut(QKeySequence("Ctrl+w"), self)
        self.shortcut2.activated.connect(self.DBhk2)
        self.shortcut3 = QShortcut(QKeySequence("Ctrl+e"), self)
        self.shortcut3.activated.connect(self.DBhk3)
        self.shortcut3 = QShortcut(QKeySequence("Ctrl+x"), self)
        self.shortcut3.activated.connect(self.DBdelete)
    # Обработчики для выполнения eventFilter
    def handle_tree1(self):
            self.isClicked = False
            self.eventValue = 1
    def handle_tree2(self):
            self.isClicked = False
            self.eventValue = 2
    def handle_tree3(self):
            self.isClicked = False
            self.eventValue = 3

    #Создание DB
    def DBLoader(self):
        self.connect = sqlite3.connect(self.DBpath)
        self.cursor = self.connect.cursor()

        if self.fileIsNew:
            query = 'DROP TABLE IF EXISTS "{table}"'
            self.cursor.execute(query.format(table=self.DBname))
            query = """CREATE TABLE "{table}"(
                        n INTEGER,
                        type INTEGER,
                        name TEXT,
                        parent INTEGER,
                        child INTEGER,
                        child2 INTEGER,
                        hostparam TEXT,
                        dynamic INTEGER,
                        graphicitem TEXT,
                        GIposx INTEGER,
                        GIposy INTEGER)
                    """
            self.cursor.execute(query.format(table=self.DBname))
        else:
            try:
                query = 'SELECT * FROM "{table}"'
                self.cursor.execute(query.format(table=self.DBname))
                data = self.cursor.fetchall()

                if len(data) != 0: self.loadUI()
                else: pass
            except:
                print("\nError! Please, check your file :(")
                sys.exit()
    #Сохранение скрипта
    def saveScript(self):
        desktop = winshell.desktop()
        print(self.BATpath)
        path = os.path.join(self.BATpath.removesuffix(self.DBname + ".bat"),  self.DBname + ".lnk")
        myBat = open("D:/PROGRAMMING/Projects/CM_CONSTRUCT_PROJ/Temp/" + self.DBname + ".bat", 'w+')
        myBat.write('python main.py ' + self.DBname + '\npause')
        myBat.close()

        target = "D:/PROGRAMMING/Projects/CM_CONSTRUCT_PROJ/Temp/" + self.DBname + ".bat"
        wDir = "D:/PROGRAMMING/Projects/CM_CONSTRUCT_PROJ"
        icon = "D:/PROGRAMMING/Projects/CM_CONSTRUCT_PROJ/evv3.ico"

        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = target
        shortcut.WorkingDirectory = wDir
        shortcut.IconLocation = icon
        shortcut.save()

    #Удаление данных об items из БД
    def DBdelete(self):
            # QTreeWidget.invisibleRootItem(self.treeView1)
            # self.treeView1.currentIndex().row()
            # item = QTreeWidget.invisibleRootItem(self.treeView1).takeChild(self.treeView1.currentIndex().row())
            global tree
            if self.eventValue == 1: tree = self.treeView1
            if self.eventValue == 2: tree = self.treeView2
            if self.eventValue == 3: tree = self.treeView3
            try:
                self.cursor = self.connect.cursor()
                query = 'SELECT * FROM "{table}" WHERE name = ? AND type = ?'
                self.cursor.execute(query.format(table=self.DBname), (self.name, self.eventValue,))
                data = self.cursor.fetchone()

                if data is not None and self.isClicked:
                    query = 'DELETE FROM "{table}" WHERE name = ? AND type = ?'
                    self.cursor.execute(query.format(table=self.DBname), (self.name, self.eventValue,))
                    self.connect.commit()
                    self.cursor.close()

                    QTreeWidget.invisibleRootItem(tree).takeChild(tree.currentIndex().row())

                    self.isClicked = False
                else:
                    pass
            except:
                self.statusBar().showMessage('Error, please report')
    def DBinsert(self, eventValue):
            self.filesaved = False
            if eventValue == 1:
                self.parent += 1
                tree = self.treeView1

                self.window = paramWindow(tree, eventValue, self.parent, self.child,
                                          self.DBname, self.DBpath, self.child2, self.plain6)
                self.window.show()
            if eventValue == 2:
                if self.parent != 0 and self.parentEnabled:
                    self.child += 1
                    tree = self.treeView2

                    self.window = paramWindow(tree, eventValue, self.parentIndex, self.child,
                                              self.DBname, self.DBpath, self.child2, self.plain6)
                    self.window.show()
            if eventValue == 3:
                if self.parent != 0 and self.child != 0 and self.childEnabled:
                    self.child2 += 1
                    tree = self.treeView3

                    self.window = paramWindow(tree, eventValue, self.parentIndex, self.childIndex,
                                              self.DBname, self.DBpath, self.child2, self.plain6)
                    self.window.show()

    #Функция при нажатии на items
    @QtCore.pyqtSlot(QtWidgets.QTreeWidgetItem, int)
    def onItemClicked(self, item, column):
        # print(item, column, item.text(column))
        self.isClicked = True
        self.name = item.text(column)

        query = 'SELECT hostparam FROM "{table}" WHERE type = ? AND name = ?'
        self.cursor.execute(query.format(table=self.DBname), (self.eventValue, item.text(column),))
        data = self.cursor.fetchone()

        try: self.plain1.setPlainText(data[0])
        except: self.plain1.setPlainText('Empty')

        if self.eventValue == 1:
            self.parentEnabled = True

            self.cursor = self.connect.cursor()
            query = 'SELECT parent FROM "{table}" WHERE type = ? AND name = ?'
            self.cursor.execute(query.format(table=self.DBname), (1, item.text(column),))
            data = self.cursor.fetchall()
            self.parentIndex = data[0][0]

            self.treeView2.clear()
            self.treeView3.clear()

            self.cursor = self.connect.cursor()
            query = 'SELECT name FROM "{table}" WHERE type = ? AND parent = ?'
            self.cursor.execute(query.format(table=self.DBname), (2, self.parentIndex,))
            data = self.cursor.fetchall()
            for i in data:
                self.item = QTreeWidgetItem(self.treeView2)
                self.item.setText(0, str(i[0]))

            query = 'SELECT name FROM "{table}" WHERE type = ? AND parent = ?'
            self.cursor.execute(query.format(table=self.DBname), (3, self.parentIndex,))
            data = self.cursor.fetchall()
            for i in data:
                self.item = QTreeWidgetItem(self.treeView3)
                self.item.setText(0, str(i[0]))

            query = 'SELECT GIposx FROM "{table}" WHERE type = ? AND name = ? AND parent = ?'
            self.cursor.execute(query.format(table=self.DBname), (self.eventValue, item.text(column), self.parentIndex,))
            data1 = self.cursor.fetchone()

            query = 'SELECT GIposy FROM "{table}" WHERE type = ? AND name = ? AND parent = ?'
            self.cursor.execute(query.format(table=self.DBname), (self.eventValue, item.text(column), self.parentIndex,))
            data2 = self.cursor.fetchone()

            query = 'SELECT graphicitem FROM "{table}" WHERE type = ? AND name = ? AND parent = ?'
            self.cursor.execute(query.format(table=self.DBname), (self.eventValue, item.text(column), self.parentIndex,))
            data = self.cursor.fetchone()

            for i in self.plain6.scene.items():
                if str(i) == data[0]: self.mainitem = data[0]

            try: self.plain6.scene.removeItem(self.selecteditem)
            except: pass
            self.selecteditem = SelectedItem(data1[0], data2[0])
            self.plain6.scene.addItem(self.selecteditem)
        if self.eventValue == 2:
            self.childEnabled = True

            self.connect = sqlite3.connect(self.DBpath)
            self.cursor = self.connect.cursor()
            query = 'SELECT child FROM "{table}" WHERE type = ? AND name = ? AND parent = ?'
            self.cursor.execute(query.format(table=self.DBname), (2, item.text(column), self.parentIndex,))
            data = self.cursor.fetchall()

            self.childIndex = data[0][0]

            self.treeView3.clear()
            query = 'SELECT name FROM "{table}" WHERE type = ? AND parent = ? AND child = ?'
            self.cursor.execute(query.format(table=self.DBname), (3, self.parentIndex, self.childIndex))
            data = self.cursor.fetchall()

            for i in data:
                self.item = QTreeWidgetItem(self.treeView3)
                self.item.setText(0, str(i[0]))

            query = 'SELECT GIposx FROM "{table}" WHERE type = ? AND name = ? AND parent = ? AND child = ?'
            self.cursor.execute(query.format(table=self.DBname), (self.eventValue, item.text(column), self.parentIndex, self.childIndex,))
            data1 = self.cursor.fetchone()

            query = 'SELECT GIposy FROM "{table}" WHERE type = ? AND name = ? AND parent = ? AND child = ?'
            self.cursor.execute(query.format(table=self.DBname), (self.eventValue, item.text(column), self.parentIndex, self.childIndex,))
            data2 = self.cursor.fetchone()

            query = 'SELECT graphicitem FROM "{table}" WHERE type = ? AND name = ? AND parent = ? AND child = ?'
            self.cursor.execute(query.format(table=self.DBname), (self.eventValue, item.text(column), self.parentIndex, self.childIndex,))
            data = self.cursor.fetchone()

            for i in self.plain6.scene.items():
                if str(i) == data[0]: self.mainitem = data[0]

            try: self.plain6.scene.removeItem(self.selecteditem)
            except: pass
            self.selecteditem = SelectedItem(data1[0], data2[0])
            self.plain6.scene.addItem(self.selecteditem)
        if self.eventValue == 3:
            self.connect = sqlite3.connect(self.DBpath)
            self.cursor = self.connect.cursor()
            query = 'SELECT child2 FROM "{table}" WHERE type = ? AND name = ? AND parent = ? AND child = ?'
            self.cursor.execute(query.format(table=self.DBname), (3, item.text(column), self.parentIndex, self.childIndex))
            data = self.cursor.fetchall()

            self.childIndex2 = data[0][0]

            query = 'SELECT GIposx FROM "{table}" WHERE type = ? AND name = ? AND parent = ? AND child = ? AND child2 = ?'
            self.cursor.execute(query.format(table=self.DBname), (self.eventValue, item.text(column), self.parentIndex, self.childIndex, self.childIndex2,))
            data1 = self.cursor.fetchone()

            query = 'SELECT GIposy FROM "{table}" WHERE type = ? AND name = ? AND parent = ? AND child = ? AND child2 = ?'
            self.cursor.execute(query.format(table=self.DBname), (self.eventValue, item.text(column), self.parentIndex, self.childIndex, self.childIndex2,))
            data2 = self.cursor.fetchone()

            query = 'SELECT graphicitem FROM "{table}" WHERE type = ? AND name = ? AND parent = ? AND child = ? AND child2 = ?'
            self.cursor.execute(query.format(table=self.DBname), (self.eventValue, item.text(column), self.parentIndex, self.childIndex, self.childIndex2,))
            data = self.cursor.fetchone()

            for i in self.plain6.scene.items():
                if str(i) == data[0]: self.mainitem = data[0]

            try: self.plain6.scene.removeItem(self.selecteditem)
            except: pass
            self.selecteditem = SelectedItem(data1[0], data2[0])
            self.plain6.scene.addItem(self.selecteditem)
    #Функция для проверки места вызова contextMenu
    def eventChecker(self, event):
        if (event.x() >= 20 and event.y() >= 30) and (event.x() <= 320 and event.y() <= 440):
            return 1
        elif (event.x() >= 330 and event.y() >= 30) and (event.x() <= 630 and event.y() <= 440):
            return 2
        elif (event.x() >= 640 and event.y() >= 30) and (event.x() <= 940 and event.y() <= 440):
            return 3
        else:
            return 0
    # Обработка событий при выходе из приложения
    def closeEvent(self, event):
            # Переопределить closeEvent
            self.connect = sqlite3.connect(self.DBpath)
            self.cursor = self.connect.cursor()
            query = 'SELECT * FROM "{table}"'
            self.cursor.execute(query.format(table=self.DBname))
            data = self.cursor.fetchall()
            if len(data) == 0 or self.filesaved:
                if self.fileIsNew or self.filesaved:
                    event.accept()
                else:
                    reply = QtWidgets.QMessageBox.question(
                        self, 'Информация',
                        "Сохранить изменения перед выходом?",
                        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Cancel)
                    if reply == QtWidgets.QMessageBox.Yes:
                        self.saveFile()
                        event.ignore()
                        sys.exit()
                    if reply == QtWidgets.QMessageBox.No:
                        self.dropFile()
                        event.ignore()
                        sys.exit()
                    if reply == QtWidgets.QMessageBox.Cancel:
                        event.ignore()
            else:
                reply = QtWidgets.QMessageBox.question(
                    self, 'Информация',
                    "Сохранить изменения перед выходом?",
                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Cancel)
                if reply == QtWidgets.QMessageBox.Yes:
                    self.saveFile()
                    event.accept()
                    sys.exit()
                if reply == QtWidgets.QMessageBox.No:
                    self.dropFile()
                    event.accept()
                    sys.exit()
                if reply == QtWidgets.QMessageBox.Cancel:
                    event.ignore()

    #Операции с файлом
    def saveFile(self):
        if self.fileIsNew: self.saveAsFile()
        else:
            try:
                self.connect = sqlite3.connect(self.DBpath)
                self.cursor = self.connect.cursor()

                query = 'UPDATE "{table}" SET dynamic = ? WHERE dynamic = ?'
                self.cursor.execute(query.format(table=self.DBname), (0, 1,))

                self.connect.commit()
                self.filesaved = True
            except: self.statusBar().showMessage('Error, please report')
    def newFile(self):
        #Переопределить closeEvent
        self.connect = sqlite3.connect(self.DBpath)
        self.cursor = self.connect.cursor()
        query = 'SELECT * FROM "{table}"'
        self.cursor.execute(query.format(table=self.DBname))
        data = self.cursor.fetchall()
        if len(data) == 0:
            if self.fileIsNew or self.filesaved: pass
            else:
                reply = QtWidgets.QMessageBox.question(
                self, 'Информация',
                "Сохранить изменения перед выходом?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Cancel)
                if reply == QtWidgets.QMessageBox.Yes:
                    self.saveFile()
                    event.accept()
                if reply == QtWidgets.QMessageBox.No:
                    self.dropFile()
                if reply == QtWidgets.QMessageBox.Cancel:
                    pass
        else:
            reply = QtWidgets.QMessageBox.question(
                self, 'Информация',
                "Сохранить изменения перед выходом?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Cancel)
            if self.fileIsNew:
                if reply == QtWidgets.QMessageBox.Yes:
                    self.saveFile()
                    self.dropFile()

                    self.DBname = "CMconstruct"
                    self.DBpath = "D:/PROGRAMMING/Projects/CM_CONSTRUCT_PROJ/" + self.DBname + ".db"
                    self.DBLoader()
                if reply == QtWidgets.QMessageBox.No:
                    self.dropFile()

                    self.DBname = "CMconstruct"
                    self.DBpath = "D:/PROGRAMMING/Projects/CM_CONSTRUCT_PROJ/" + self.DBname + ".db"
                    self.DBLoader()
                if reply == QtWidgets.QMessageBox.Cancel:
                    pass
            else:
                if reply == QtWidgets.QMessageBox.Yes:
                    self.saveFile()
                    event.accept()
                if reply == QtWidgets.QMessageBox.No:
                    self.dropFile()
                    event.accept()
                if reply == QtWidgets.QMessageBox.Cancel:
                    pass
        self.dropFile()
    def dropFile(self):
        self.connect = sqlite3.connect(self.DBpath)
        self.cursor = self.connect.cursor()
        query = 'DELETE FROM "{table}" WHERE dynamic = ?'
        self.cursor.execute(query.format(table=self.DBname), (1,))
        self.connect.commit()

        self.DBLoader()

        self.treeView1.clear()
        self.treeView2.clear()
        self.treeView3.clear()

        self.plain6.scene.clear()

        self.childEnabled = False
        self.parentEnabled = False
        self.filesaved = False
        self.fileIsNew = True
    def saveAsFile(self):
        fileFilter = 'CMfile (*.bat)'
        name = QFileDialog.getSaveFileName(
            parent=self,
            caption='Save File As',
            # directory=os.getcwd(),
            filter=fileFilter,
            initialFilter=fileFilter)

        try:
            DBname, DBname_reverse = '', ''

            for i in reversed(range(len(name[0]))):
                if name[0][i] != '/': DBname_reverse += name[0][i]
                else: break
            for i in reversed(DBname_reverse): DBname += i

            self.connect = sqlite3.connect(self.DBpath)
            self.cursor = self.connect.cursor()
            query = 'SELECT * FROM "{table}"'
            self.cursor.execute(query.format(table=self.DBname))
            data = self.cursor.fetchall()
            self.connect.commit()

            self.DBname = DBname[:-4]
            self.DBpath = "D:/PROGRAMMING/Projects/CM_CONSTRUCT_PROJ/Data/" + DBname[:-4] + ".db"
            self.BATpath = name[0]

            self.connect = sqlite3.connect(self.DBpath)
            self.cursor = self.connect.cursor()
            query = 'DROP TABLE IF EXISTS "{table}"'
            self.cursor.execute(query.format(table=self.DBname))
            query = """
            CREATE TABLE "{table}" (
            n INTEGER,
            type INTEGER,
            name TEXT,
            parent INTEGER,
            child INTEGER,
            child2 INTEGER,
            hostparam TEXT,
            dynamic INTEGER,
            graphicitem TEXT,
            GIposx INTEGER,
            GIposy INTEGER)
            """
            self.cursor.execute(query.format(table=self.DBname))

            for i in range(len(data)):
                list = []
                for j in range(len(data[i])):
                    if j == 5: list.append(0)
                    else: list.append(data[i][j])

                query = 'INSERT INTO "{table}"(n, type, name, parent, child, ' \
                        'child2, hostparam, dynamic, graphicitem, GIposx, GIposy)' \
                        ' VALUES(?,?,?,?,?,?,?,?,?,?,?);'
                self.cursor.executemany(query.format(table=self.DBname), (list,))
            self.connect.commit()
            self.setWindowTitle(DBpath)
            self.saveScript()

            self.fileIsNew = False
            self.filesaved = True
        except: self.statusBar().showMessage('Error, please report')
    def openFile(self):
        fileFilter = 'DBFile (*.db)'
        name = QFileDialog.getOpenFileName(
            parent=self,
            caption='Open File',
            filter=fileFilter
            # directory=os.getcwd(),
            # initialFilter=fileFilter
        )
        try:
            DBname, DBname_reverse = '', ''

            for i in reversed(range(len(name[0]))):
                if name[0][i] != '/': DBname_reverse += name[0][i]
                else: break
            for i in reversed(DBname_reverse): DBname += i

            self.setWindowTitle('CMconstruct: ' + name[0])

            self.DBpath = name[0]
            self.DBname = DBname
            self.filesaved = True
            self.fileIsNew = False

            self.loadUI()
        except:
            self.statusBar().showMessage('Error, please report')

    #Триггер для создания виджетов параметров
    def ADDparam(self):
        self.tab2_layout.removeWidget(self.button_plus)

        self.plain2 = QLineEdit(self)
        self.plain2.setFixedSize(150, 25)
        self.plain2.setPlaceholderText("Name...")

        self.button_minus = QPushButton("-")
        self.button_minus.setFixedSize(25, 25)
        self.button_minus.clicked.connect(self.DELparam)

        self.combobox = QComboBox(self)
        self.combobox.setFixedSize(150, 25)
        self.combobox.addItems(list1)

        self.button_plus = QPushButton("+")
        self.button_plus.setFixedSize(25, 25)
        self.button_plus.clicked.connect(self.ADDparam)

        self.checkbox = QCheckBox()
        # self.checkBoxA.stateChanged.connect(self.CBtrigger)

        self.tab2_layout_form = QHBoxLayout()

        # index's: form; plain2; checkbox; combobox; button_minus;
        list = [self.tab2_layout_form, self.plain2, self.combobox, self.checkbox, self.button_minus]
        self.index_list.append(list)
        # for i in range(0, len(list)):
        #         print(self.index_list[self.counter][i])
        self.counter += 1

        self.tab2_layout_form.addWidget(self.plain2)
        self.tab2_layout_form.addWidget(self.combobox)
        self.tab2_layout_form.addWidget(self.checkbox)
        self.tab2_layout_form.addWidget(self.button_minus)

        self.tab2_layout.addRow(self.tab2_layout_form)
        self.tab2_layout.addRow(self.button_plus)
    def DELparam(self):
        button = self.sender()

        for i in range(self.counter):
            if button in self.index_list[i]:
                self.tab2_layout_form = self.index_list[i][0]
                self.plain2 = self.index_list[i][1]
                self.combobox = self.index_list[i][2]
                self.checkbox = self.index_list[i][3]
                self.button_minus = self.index_list[i][4]

                self.index_list.pop(i)
                break

        self.tab2_layout_form.setParent(None)
        self.plain2.setParent(None)
        self.checkbox.setParent(None)
        self.combobox.setParent(None)
        self.button_minus.setParent(None)

        self.counter -= 1

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(css)

    #Настройка параметров сценария зауска из bat файла
    try:
        #Взять расположение указанной при установке корневой дерективы для файлов с базами данных
        DBname = str(sys.argv[1])
        DBpath = "D:/PROGRAMMING/Projects/CM_CONSTRUCT_PROJ/Data/" + DBname + ".db"
        fileIsNew = False
    except:
        DBname = "CMconstruct"
        DBpath = "D:/PROGRAMMING/Projects/CM_CONSTRUCT_PROJ/" + DBname + ".db"
        fileIsNew = True

    window = MainWindow(DBname, DBpath, fileIsNew)
    window.showMaximized()
    app.exec()

#Строки которые указывают путь к дерикториям хранения файлов
#Путь к дерективе сохранения базы данных на строках: #1360
#Путь к дерективе сохранения проектов на строках: #1006 #1002
#Путь к дерективе где расположен корневой проект: #1497 #1501 #1296 #1302 #1007 #1008

#Грядущие Updates:
#1)Окно преднастроек под свои настройки (wizard downloader be like)
#2)Стилизация программы
#3)Добавление параметризации в DB
#4)...

#GOLOVINOV RUSLAN, PRUDNICHENKO GERMAN, SUZDALCEV VLADIMIR, #SMTU(KARABELKA) PROD 2023