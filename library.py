#в списки занесены элементы которые пренадлежат комбобоксам в классе paramwindow и играют роль параметров которые можно настраивать
list1 = [
            'param1',
            'param2',
            'param3',
            'param4',
        ]
list2 = [
            'param1',
            'param2',
            'param3',
            'param4',
        ]
list3 = [
            'param1',
            'param2',
            'param3',
            'param4',
        ]
list4 = [
            'param1',
            'param2',
            'param3',
            'param4',
        ]
#максимальное количество параметров для каждого элемента
param_max_value = 10
#StyleSheet
css = '''
QWidget{
    background-color: #23272a;
    background: #23272a;
    font-size: 22px;
    color: #dfe8ed;
    font: italic bold serif;
}
QScrollArea{
    background-color: #23272a;
    font-size: 22px;
    color: #dfe8ed;
    font: italic bold serif;
}
QTreeWidget{
    background-color: #23272a;
    font-size: 22px;
    color: #dfe8ed;
    font: italic bold serif;
    border-radius: 20;
}
QDockWidget{
    background-color: #394045;
    font-size: 22px;
    color: #dfe8ed;
    font: italic bold serif;
    border-radius: 20;
}
QVBoxLayout{
    background-color: #394045;
    font-size: 22px;
    color: #dfe8ed;
    font: italic bold serif;
    border-radius: 20;
}
QHBoxLayout{
    background-color: #394045;
    font-size: 22px;
    color: #dfe8ed;
    font: italic bold serif;
    border-radius: 20;
}
QGroupBox{
    background-color: #394045;
    font-size: 22px;
    color: #dfe8ed;
    font: italic bold serif;
}
QFormLayout{
    background-color: #394045;
    font-size: 22px;
    color: #dfe8ed;
    font: italic bold serif;
    border-radius: 20;
}
QPlainTextEdit{
    background-color: #394045;
    font-size: 22px;
    color: #dfe8ed;
    font: italic bold serif;
}
QGraphicsView{
    background-color: #394045;
    color: #394045;
    border-radius: 20;
}
QGraphicsScene{
    background-color: #36281d;
    color: #36281d;
    border-radius: 20;
}
QPainter{
    background-color: #394045;
    color: #394045;
    border-radius: 20;
}
QTabWidget{
    background-color: #394045;
    font-size: 22px;
    color: #dfe8ed;
    font: italic bold serif;
    border-radius: 20;
}
QLayout{
    background-color: #394045;
    font-size: 22px;
    color: #dfe8ed;
    font: italic bold serif;
    border-radius: 20;
}
QTabBar{
    background-color: #394045;
    font-size: 22px;
    color: #dfe8ed;
    font: italic bold serif;
    border-radius: 20;
}
QWidget:tab1{
    background-color: #394045;
    color: #dfe8ed;
}
QMainWindow{
    background-color: #394045;
    color: #dfe8ed;

    border-radius: 10px;
}
'''