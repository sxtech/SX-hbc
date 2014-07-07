# -*- coding: cp936 -*-
from hbccenter import HbcCenter
from PyQt4 import QtGui, QtCore
import sys,time,datetime,os
import MySQLdb
import cx_Oracle
import logging
import logging.handlers
from singleinstance import singleinstance
import gl

def getTime():
    return datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
            
def initLogging(logFilename):
    """Init for logging"""
    path = os.path.split(logFilename)
    if os.path.isdir(path[0]):
        pass
    else:
        os.makedirs(path[0])
    logging.basicConfig(
                    level    = logging.DEBUG,
                    format   = '%(asctime)s %(filename)s[line:%(lineno)d] [%(levelname)s] %(message)s',
                    datefmt  = '%Y-%m-%d %H:%M:%S',
                    filename = logFilename,
                    filemode = 'a');

def version():
    return 'SX-Hbc V0.1.6'

 
class MyThread(QtCore.QThread):
    trigger = QtCore.pyqtSignal(str,int)
 
    def __init__(self, parent=None):
        super(MyThread, self).__init__(parent)
 
    def run(self):
        m = hbcmain(self.trigger)
        m.mainloop()

class hbcmain:
    def __init__(self,trigger):
        self.style_red = 'size=4 face=arial color=red'
        self.style_blue = 'size=4 face=arial color=blue'
        self.style_green = 'size=4 face=arial color=green'
        self.trigger = trigger
        self.dc = HbcCenter(trigger)
        initLogging(r'log\hbcview.log')
        self.count = 0

        self.setupflag = False

        self.trigger.emit("<font %s>%s</font>"%(self.style_green,"Welcome to "+version()),1)


    def __del__(self):
        del self.dc

    def loginMYSQL(self):
        now = getTime()
        try:
            self.trigger.emit("<font %s>%s</font>"%(self.style_green,now+'Start to connect mysql server '),1)
            self.dc.loginMysql()
            self.trigger.emit("<font %s>%s</font>"%(self.style_green,now+'Connect mysql success! '),1)
        except MySQLdb.Error,e:
            self.trigger.emit("<font %s>%s</font>"%(self.style_red,now+str(e)),1)
            self.trigger.emit("<font %s>%s</font>"%(self.style_red,now+'Reconn after 15 seconds'),1)
            logging.exception(e)
            self.dc.loginmysqlflag = True
            self.dc.loginmysqlcount = 1
        except Exception,e:
            self.trigger.emit("<font %s>%s</font>"%(self.style_red,now+str(e)),1)
            logging.exception(e)
        else:
            self.dc.loginmysqlflag = False
            self.dc.loginmysqlcount = 0
            
    def loginHbcORC(self):
        now = getTime()
        try:
            self.trigger.emit("<font %s>%s</font>"%(self.style_green,now+'Start to connect HbcOracle server '),1)
            self.dc.loginHbcOrc()
            self.trigger.emit("<font %s>%s</font>"%(self.style_green,now+'Connect Oracle success! '),1)
        except Exception,e:
            self.trigger.emit("<font %s>%s</font>"%(self.style_red,now+str(e)),1)
            self.trigger.emit("<font %s>%s</font>"%(self.style_red,now+'Reconn after 15 seconds'),1)
            logging.exception(e)
            self.dc.loginhbcorcflag = True
            self.dc.loginhbccount = 1
        else:
            self.dc.loginhbcorcflag = False
            self.dc.loginhbccount = 0

    def loginKakouORC(self):
        now = getTime()
        #print '123'
        try:
            self.trigger.emit("<font %s>%s</font>"%(self.style_green,now+'Start to connect KakouOracle server '),1)
            self.dc.loginKakouOrc()
            self.trigger.emit("<font %s>%s</font>"%(self.style_green,now+'Connect Oracle success! '),1)
        except Exception,e:
            self.trigger.emit("<font %s>%s</font>"%(self.style_red,now+str(e)),1)
            self.trigger.emit("<font %s>%s</font>"%(self.style_red,now+'Reconn after 15 seconds'),1)
            logging.exception(e)
            self.dc.loginkakouorcflag = True
            self.dc.loginkakoucount = 1
        else:
            self.dc.loginkakouorcflag = False
            self.dc.loginkakoucount = 0
        
    def setup(self):
        #print 'setup'
        try:
            self.dc.getSiteID()
            self.dc.getWlcp()
            self.dc.getBkcp()
            self.dc.getIPState()
        except Exception,e:
            self.trigger.emit("<font %s>%s</font>"%(self.style_red,getTime()+str(e)),1)
            logging.exception(e)
            self.loginorcflag = True
            self.loginorccount = 1
        else:
            self.setupflag = True

    def mainloop(self):                    
        while True:
            if gl.qtflag == False:
                gl.dcflag = False
                break
            
            if self.dc.loginmysqlflag == True:
                if self.dc.loginmysqlcount==0:
                    self.loginMYSQL()
                elif self.dc.loginmysqlcount<=15:
                    self.dc.loginmysqlcount += 1
                    time.sleep(1)
                else:
                    self.dc.loginmysqlcount = 0
                    
            elif self.dc.loginhbcorcflag == True:
                if self.dc.loginhbccount==0:
                    self.loginHbcORC()
                elif self.dc.loginhbccount<=15:
                    self.dc.loginhbccount += 1
                    time.sleep(1)
                else:
                    self.dc.loginhbccount = 0
                    
            elif self.dc.loginkakouorcflag == True:
                if self.dc.loginkakoucount==0:
                    self.loginKakouORC()
                elif self.dc.loginkakoucount<=15:
                    self.dc.loginkakoucount += 1
                    time.sleep(1)
                else:
                    self.dc.loginkakoucount = 0

            else:
                if datetime.datetime.now()>(self.dc.timeflag+datetime.timedelta(minutes = 10)):
                    self.dc.setData()
                else:
                    time.sleep(1)
    
    
class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):  
        super(MainWindow, self).__init__(parent)
        self.resize(600, 400)
        self.setWindowTitle(version())

        self.count = 0
        
        self.text_area = QtGui.QTextBrowser()
        self.text_area.setMinimumWidth(600)
        self.text_area.setMinimumHeight(250)

        title1 = QtGui.QLabel(u'开始时间')
        title2 = QtGui.QLabel(u'结束时间')
        
        self.TimeEdit = QtGui.QTimeEdit()
        self.TimeEdit2 = QtGui.QTimeEdit() 
        self.TimeEdit.setDisplayFormat("hh:mm:ss")
        self.TimeEdit2.setDisplayFormat("hh:mm:ss") 
        self.time = QtCore.QTime()
        self.time2 = QtCore.QTime()
        gl.hour1 = 7
        gl.min1 = 30 
        gl.sec1 = 0
        gl.hour2 = 20
        gl.min2 = 30
        gl.sec2 = 0
        self.time.setHMS(gl.hour1, gl.min1, gl.sec1)
        self.time2.setHMS(gl.hour2, gl.min2, gl.sec2)
        self.TimeEdit.setTime(self.time)
        self.TimeEdit2.setTime(self.time2)
        
        #Hours ScrollBar
        self.HourScrollBar = QtGui.QScrollBar(QtCore.Qt.Horizontal)
        self.HourScrollBar.setMinimum(0)
        self.HourScrollBar.setMaximum(23)
        self.HourScrollBar.setFocusPolicy(QtCore.Qt.StrongFocus)

        #Minutes ScrollBar
        self.MinScrollBar = QtGui.QScrollBar(QtCore.Qt.Horizontal)
        self.MinScrollBar.setMinimum(0)
        self.MinScrollBar.setMaximum(59)
        self.MinScrollBar.setFocusPolicy(QtCore.Qt.StrongFocus)

        #Seconds ScrollBar
        self.SecScrollBar = QtGui.QScrollBar(QtCore.Qt.Horizontal)
        self.SecScrollBar.setMinimum(0)
        self.SecScrollBar.setMaximum(59)
        self.SecScrollBar.setFocusPolicy(QtCore.Qt.StrongFocus)

        #ScrollBar connections
        self.HourScrollBar.valueChanged.connect(self.HourChanged)
        self.MinScrollBar.valueChanged.connect(self.MinChanged)
        self.SecScrollBar.valueChanged.connect(self.SecChanged)

        #Hours ScrollBar
        self.HourScrollBar2 = QtGui.QScrollBar(QtCore.Qt.Horizontal)
        self.HourScrollBar2.setMinimum(0)
        self.HourScrollBar2.setMaximum(23)
        self.HourScrollBar2.setFocusPolicy(QtCore.Qt.StrongFocus)

        #Minutes ScrollBar
        self.MinScrollBar2 = QtGui.QScrollBar(QtCore.Qt.Horizontal)
        self.MinScrollBar2.setMinimum(0)
        self.MinScrollBar2.setMaximum(59)
        self.MinScrollBar2.setFocusPolicy(QtCore.Qt.StrongFocus)

        #Seconds ScrollBar
        self.SecScrollBar2 = QtGui.QScrollBar(QtCore.Qt.Horizontal)
        self.SecScrollBar2.setMinimum(0)
        self.SecScrollBar2.setMaximum(59)
        self.SecScrollBar2.setFocusPolicy(QtCore.Qt.StrongFocus)

        #ScrollBar connections
        self.HourScrollBar2.valueChanged.connect(self.HourChanged2)
        self.MinScrollBar2.valueChanged.connect(self.MinChanged2)
        self.SecScrollBar2.valueChanged.connect(self.SecChanged2)
        
        central_widget = QtGui.QWidget()
        leftLayout = QtGui.QGridLayout()
        rightLayout = QtGui.QVBoxLayout()
        bottomLayout = QtGui.QHBoxLayout()
        central_layout = QtGui.QGridLayout()
        #central_layout.addLayout(bottomLayout,5,1)
##        central_layout.addLayout(leftLayout)
##        central_layout.addLayout(rightLayout)
        
        central_layout.addWidget(title1,1,0)
        central_layout.addWidget(self.TimeEdit,1,1)
        central_layout.addWidget(self.HourScrollBar,2,1)
        central_layout.addWidget(self.MinScrollBar,3,1)
        central_layout.addWidget(self.SecScrollBar,4,1)
        central_layout.addWidget(title2,1,2)
        central_layout.addWidget(self.TimeEdit2,1,3)
        central_layout.addWidget(self.HourScrollBar2,2,3)
        central_layout.addWidget(self.MinScrollBar2,3,3)
        central_layout.addWidget(self.SecScrollBar2,4,3)
        central_layout.addWidget(self.text_area,5,0,5,4)
        central_widget.setLayout(central_layout)
        self.setCentralWidget(central_widget)

        exit = QtGui.QAction(QtGui.QIcon('icons/exit.png'), 'Exit', self)
        exit.setShortcut('Ctrl+Q')
        exit.setStatusTip('Exit application')
        self.connect(exit, QtCore.SIGNAL('triggered()'), QtCore.SLOT('close()'))

        self.statusBar()

        menubar = self.menuBar()
        file = menubar.addMenu('&File')
        file.addAction(exit)
        
        toolbar = self.addToolBar('Exit')
        toolbar.addAction(exit)
        
        self.setWindowIcon(QtGui.QIcon('icons/logo.png'))
        
        self.start_threads()
        
    def closeEvent(self, event):
        reply = QtGui.QMessageBox.question(self, 'Message',
            u"确定要退出吗?", QtGui.QMessageBox.Yes |
            QtGui.QMessageBox.No, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            gl.qtflag = False
            while gl.dcflag == True:
                #print 'gl.dcflag',gl.dcflag
                time.sleep(1)
            event.accept()
        else:
            event.ignore()
            
    def start_threads(self):
        self.threads = []              # this will keep a reference to threads
        thread = MyThread(self)    # create a thread
        thread.trigger.connect(self.update_text)  # connect to it's signal
        thread.start()             # start the thread
        self.threads.append(thread) # keep a reference
            
 
    def update_text(self, message,m_type):
        self.text_area.append(unicode(message, 'gbk'))
        self.count += 1
        if self.count > 1000:
            self.text_area.clear()
            self.count = 0

    def HourChanged(self): 
        gl.hour1 = self.HourScrollBar.value() 
        self.set_time() 

    def MinChanged(self): 
        gl.min1 = self.MinScrollBar.value() 
        self.set_time() 

    def SecChanged(self): 
        gl.sec1 = self.SecScrollBar.value() 
        self.set_time()

    def HourChanged2(self): 
        gl.hour2 = self.HourScrollBar2.value() 
        self.set_time2() 

    def MinChanged2(self): 
        gl.min2 = self.MinScrollBar2.value() 
        self.set_time2() 

    def SecChanged2(self): 
        gl.sec2 = self.SecScrollBar2.value() 
        self.set_time2() 

    def set_time(self): 
        self.time.setHMS(gl.hour1, gl.min1, gl.sec1) 
        self.TimeEdit.setTime(self.time)

    def set_time2(self): 
        self.time2.setHMS(gl.hour2, gl.min2, gl.sec2) 
        self.TimeEdit2.setTime(self.time2)
 
if __name__ == '__main__':
    myapp = singleinstance()
    if myapp.aleradyrunning():
        print version(),'已经启动!3秒后自动退出...'
        time.sleep(3)
        sys.exit(0)
    
    app = QtGui.QApplication(sys.argv)
 
    mainwindow = MainWindow()
    mainwindow.show()
 
    sys.exit(app.exec_())
