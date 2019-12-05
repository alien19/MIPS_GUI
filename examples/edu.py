import os
import subprocess
import sys
import time
import PIL

from PIL import Image
from subprocess import*
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import*
from PyQt5.QtGui import*
from PyQt5.QtCore import*

import sys, random
import numpy as np
import math

import QtQuick

Rectangle {
    id: panel

    property bool open: false                     // The open or close state of the drawer
    property int position: Qt.LeftEdge            // Which side of the screen the drawer is on, can be Qt.LeftEdge or Qt.RightEdge
    property Item visualParent: parent            // The item the drawer should cover, by default the parent of the Drawer

    // The fraction showing how open the drawer is
    readonly property real panelProgress:  (panel.x - _minimumX) / (_maximumX - _minimumX)

    function show() { open = true; }
    function hide() { open = false; }

    function toggle() {
        if (open) open = false;
        else open = true;
    }

    // Internal

    default property alias data: contentItem.data
    readonly property real expandedFraction: 0.78  // How big fraction of the screen realesatate that is covered by an open menu
    readonly property real _scaleFactor: _rootItem.width / 320 // Note, this should really be application global
    readonly property int _pullThreshold: panel.width/2
    readonly property int _slideDuration: 260
    readonly property int _collapsedX: _rightEdge ? _rootItem.width :  - panel.width
    readonly property int _expandedWidth: expandedFraction * _rootItem.width
    readonly property int _expandedX: _rightEdge ? _rootItem.width - width : 0
    readonly property bool _rightEdge: position === Qt.RightEdge
    readonly property int _minimumX:  _rightEdge ?  _rootItem.width - panel.width : -panel.width
    readonly property int _maximumX: _rightEdge ? _rootItem.width : 0
    readonly property int _openMarginSize: 20 * _scaleFactor

    property real _velocity: 0
    property real _oldMouseX: -1

    function _findRootItem() {
        var p = panel;
        while (p.parent != null)
            p = p.parent;
        return p;
    }

    property Item _rootItem: _findRootItem()
    height: parent.height
    on_RightEdgeChanged: _setupAnchors()
    onOpenChanged: completeSlideDirection()
    width: _expandedWidth
    x: _collapsedX
    z: 10

    function _setupAnchors() {     // Note that we can't reliably apply anchors using bindings
        _rootItem = _findRootItem();

        shadow.anchors.right = undefined;
        shadow.anchors.left = undefined;

        mouse.anchors.left = undefined;
        mouse.anchors.right = undefined;

        if (_rightEdge) {
            mouse.anchors.right = mouse.parent.right;
            shadow.anchors.right = panel.left;
        } else {
            mouse.anchors.left = mouse.parent.left;
            shadow.anchors.left = panel.right;
        }

        slideAnimation.enabled = false;
        panel.x =_rightEdge ? _rootItem.width :  - panel.width;
        slideAnimation.enabled = true;
    }

    function completeSlideDirection() {
        if (open) {
            panel.x = _expandedX;
        } else {
            panel.x = _collapsedX;
            Qt.inputMethod.hide();
        }
    }

    function handleRelease() {
        var velocityThreshold = 5 * _scaleFactor;
        if ((_rightEdge && _velocity > velocityThreshold) ||
                (!_rightEdge && _velocity < -velocityThreshold)) {
            panel.open = false;
            completeSlideDirection()
        } else if ((_rightEdge && _velocity < -velocityThreshold) ||
                   (!_rightEdge && _velocity > velocityThreshold)) {
            panel.open = true;
            completeSlideDirection()
        } else if ((_rightEdge && panel.x < _expandedX + _pullThreshold) ||
                   (!_rightEdge && panel.x > _expandedX - _pullThreshold) ) {
            panel.open = true;
            panel.x = _expandedX;
        } else {
            panel.open = false;
            panel.x = _collapsedX;
        }
    }

    function handleClick(mouse) {
        if ((_rightEdge && mouse.x < panel.x ) || mouse.x > panel.width) {
            open = false;
        }
    }

    onPositionChanged: {
        if (! (position === Qt.RightEdge || position === Qt.LeftEdge ) ) {
            console.warn("SlidePanel: Unsupported position.")
        }
    }

    Behavior on x {
        id: slideAnimation
        enabled: !mouse.drag.active
        NumberAnimation {
            duration: _slideDuration
            easing.type: Easing.OutCubic
        }
    }

    Connections {
        target: _rootItem
        onWidthChanged: {
            slideAnimation.enabled = false
            panel.completeSlideDirection()
            slideAnimation.enabled = true
        }
    }

    NumberAnimation on x {
        id: holdAnimation
        to: _collapsedX + (_openMarginSize * (_rightEdge ? -1 : 1))
        running : false
        easing.type: Easing.OutCubic
        duration: 200
    }

    MouseArea {
        id: mouse
        parent: _rootItem

        y: visualParent.y
        width: open ? _rootItem.width : _openMarginSize
        height: visualParent.height
        onPressed:  if (!open) holdAnimation.restart();
        onClicked: handleClick(mouse)
        drag.target: panel
        drag.minimumX: _minimumX
        drag.maximumX: _maximumX
        drag.axis: Qt.Horizontal
        drag.onActiveChanged: if (active) holdAnimation.stop()
        onReleased: handleRelease()
        z: open ? 1 : 0
        onMouseXChanged: {
            _velocity = (mouse.x - _oldMouseX);
            _oldMouseX = mouse.x;
        }
    }

    Rectangle {
        id: backgroundDimmer
        parent: visualParent
        anchors.fill: parent
        opacity: 0.5 * Math.min(1, Math.abs(panel.x - _collapsedX) / _rootItem.width/2)
        color: "black"
    }

    Item {
        id: contentItem
        parent: _rootItem
        width: panel.width
        height: panel.height
        x: panel.x
        y: panel.y
        z: open ? 5 : 0
        clip: true
    }

    Item {
        id: shadow
        anchors.left: panel.right
        anchors.leftMargin: _rightEdge ? 0 : 4 * _scaleFactor
        height: parent.height
        Rectangle {
            height: 4 * _scaleFactor
            width: panel.height
            rotation: 90
            opacity: Math.min(1, Math.abs(panel.x - _collapsedX)/_openMarginSize)
            transformOrigin: Item.TopLeft
            gradient: Gradient{
                GradientStop { position: _rightEdge ? 1 : 0 ; color: "#00000000"}
                GradientStop { position: _rightEdge ? 0 : 1 ; color: "#2c000000"}
            }
        }
    }
}
#
# class Start_Edu(QMainWindow):
#
#     def __init__(self):
#         super(Start_Edu, self).__init__()
#         self.left = 20 #position from left of screen
#         self.top = 20 #position from top of screen
#         self.title = 'Educational Pipelined MIPS'
#         self.width = 1270 #width of window
#         self.height = 750 #height of window
#         self.initUI()
#
#     def initUI(self):
#         palette = QtGui.QPalette()
#         palette.setColor(QtGui.QPalette.Background, QtCore.Qt.white)
#         self.setPalette(palette)
#         self.tboard = Edu(self)
#         self.setCentralWidget(self.tboard)
#         self.setGeometry(self.top, self.left, self.width, self.height)
#         self.setWindowTitle('Educational Pipelined MIPS')
#         self.setStyleSheet('background-image: url( MIPS_Architecture_(Pipelined).svg.png);')
#         self.show()
#
#
# xmove=100
# ymove=650
# class Edu(QFrame):
#     Speed = 1000
#
#     def __init__(self, parent):
#         super(Edu, self).__init__(parent)
#         #self.setAutoFillBackground(True)
#         self.setMouseTracking(True)
#         self.setWindowIcon(QIcon('blackpearl'))
#         self.setFocusPolicy(QtCore.Qt.StrongFocus)
#
#
#         # self.layout = QHBoxLayout()
#         # self.label = QLabel('hello')
#         # self.label.setPixmap(QPixmap('MIPS_Architecture_(Pipelined).svg.png'))
#         # self.label.setScaledContents(True)
#         # self.label.adjustSize()
#         # self.layout.addWidget(self.label)
#         # self.setLayout(self.layout)
#
#         self.timer_draw = QtCore.QTimer(self)
#         self.timer_draw.timeout.connect(self.drawR)
#         self.timer_draw.start(self.Speed)
#
#         self.rec_color = QtCore.Qt.black
#         self.draw_r = False
#         self.drawR()
#
#         self.dial = QDial(self)
#         self.dial.move(xmove-50,ymove-50)
#         self.dial.setValue(30)
#         self.dial.resize(100,100)
#         self.dial.setWrapping(True)
#         self.dial.setMinimum(0)
#         self.dial.setMaximum(360)
#
#     def mouseMoveEvent(self, event):
#         x=event.x()
#         y=event.y()
#         if x<xmove and y<ymove :q=1
#         elif x>xmove and y<ymove :q=2
#         elif x>xmove and y>ymove :q=3
#         elif x<xmove and y>ymove :q=4
#         # edu_pip.label.setText('Mouse coords: ( %d : %d )' % (x,y))
#         if y != ymove and x != xmove:
#             a = math.degrees(math.atan((ymove-event.y())/(xmove - event.x())))
#             if q == 1: a=a
#             elif q == 2: a=180+a
#             elif q == 3: a=180+a
#             elif q == 4: a=a
#         else :
#             if x<xmove and y==ymove:a=0
#             elif x==xmove and y<ymove:a=90
#             elif x>xmove and y==ymove:a=180
#             elif x==xmove and y>ymove:a=270
#
#         self.dial.setValue(int(a)+90)
#
#     def paintEvent(self, event):
#         painter = QtGui.QPainter(self)
#         pen = QtGui.QPen()
#         pen.setWidth(3)
#         print ("Paint Event?")
#         if self.draw_r == True:
#             print ("Draw")
#             self.rec_color = QtCore.Qt.yellow
#             pen.setColor(self.rec_color)
#         else:
#             print ("Do not draw")
#             self.rec_color = QtCore.Qt.cyan
#             pen.setColor(self.rec_color)
#         painter.setPen(pen)
#         painter.drawRect(QRect(125,375 , 117, 150))
#
#         points_addr = [
#             QPoint(150,150),
#             QPoint(195,170),
#             QPoint(195,230),
#             QPoint(150,255),
#             QPoint(148,209),
#             QPoint(166,200),
#             QPoint(150,195)
#             ]
#         poly = QPolygon(points_addr)
#         painter.drawPolygon(poly)
#
#     def drawR(self):
#         self.draw_r = not self.draw_r
#         self.update()
#
#     def data_changed(self):
#         for i in range(0,len(regfile)):
#             assembler.content_pc +=  pc[i]+"\r\n"
#             assembler.content_rg = assembler.content_rg + regfile[i]+"\r\n"
#             assembler.content_dmem = assembler.content_dmem + dmem[i]+"\r\n"
#
#         assembler.lbl_pc.setText('The Final PC is:\r\n'+assembler.content_pc)
#         assembler.lbl_rg.setText('The contents of the register file are:\r\n'+assembler.content_rg)
#         assembler.lbl_dmem.setText('The contents of data memory are:\r\n'+assembler.content_dmem)
#
#
# def main():
#
#    app = QApplication([])
#    game = Start_Edu()
#    sys.exit(app.exec_())
#
# if __name__ == '__main__':
#    main()
