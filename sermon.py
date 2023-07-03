import sys, os, time, platform, datetime
import serial, serial.tools.list_ports
import PyQt5, PyQt5.Qt, PyQt5.QtWidgets

from serial import (
  SerialException        ,
  SerialTimeoutException
)

from datetime import (
  datetime
)

from PyQt5.Qt import (
  QTimer
)

from PyQt5.QtWidgets import (
  QApplication   ,
  QMainWindow    ,
  QStyle         ,
  QMessageBox    ,
  QLabel         ,
  QLineEdit      ,
  QTextEdit      ,
  QPlainTextEdit ,
  QVBoxLayout    ,
  QHBoxLayout    ,
  QGridLayout    ,
  QComboBox      ,
  QPushButton    ,
  QCheckBox      ,
  QFileDialog    ,
  QScrollBar     ,
  QWidget
)

# ----------------------------------------------------------------
# List the available ports

def populateSerialPorts():
  return [ tuple(p) for p in list(serial.tools.list_ports.comports()) ]

# ----------------------------------------------------------------
# Serial Monitor

class SerialMonitor(QMainWindow):
  def __init__(self):
    super().__init__()

    self.sercon = None

    self.timer_0 = QTimer()
    self.timer_0_interval = 1000
    self.timer_1 = QTimer()
    self.timer_1_interval = 1000

    self.timer_0.setInterval(self.timer_0_interval)
    self.timer_0.timeout.connect(self.onTimeoutTimer_0)
    self.timer_1.setInterval(self.timer_1_interval)
    self.timer_1.timeout.connect(self.onTimeoutTimer_1)

    self.initUI()

    self.timer_0.start()
    self.timer_1.start()

  def initUI(self):
    self.setWindowTitle('Serial Monitor')
    name = getattr(QStyle, 'SP_ComputerIcon')
    icon = self.style().standardIcon(name)
    self.setWindowIcon(icon)

    self.layout   = QHBoxLayout()
    self.layout_0 = QVBoxLayout()
    self.layout_1 = QVBoxLayout()
    self.layout_2 = QGridLayout()
    self.layout_3 = QVBoxLayout()
    self.layout_4 = QGridLayout()

    combobox_0_items = [ p[0] for p in populateSerialPorts() ]
    combobox_1_items = [
      '0'      ,
      '75'     ,
      '110'    ,
      '134'    ,
      '150'    ,
      '200'    ,
      '300'    ,
      '600'    ,
      '1200'   ,
      '1800'   ,
      '2400'   ,
      '4800'   ,
      '9600'   ,
      '19200'  ,
      '38400'  ,
      '57600'  ,
      '115200'
    ]

    self.combobox_0 = QComboBox()
    self.combobox_0.addItems(combobox_0_items)
    self.combobox_1 = QComboBox()
    self.combobox_1.addItems(combobox_1_items)
    self.combobox_1.setCurrentText('9600')

    self.button_0 = QPushButton('Connect')
    self.button_0.clicked.connect(self.connect)
    self.button_1 = QPushButton('Enter')
    self.button_1.clicked.connect(self.send)
    self.button_2 = QPushButton('Clear')
    self.button_2.clicked.connect(self.clear)
    self.button_3 = QPushButton('Extract')
    self.button_3.clicked.connect(self.extract)
    self.button_4 = QPushButton('Save')
    self.button_4.clicked.connect(self.save)

    self.checkbox_0 = QCheckBox('Timestamp')

    self.line_0 = QLineEdit()
    self.line_0.returnPressed.connect(self.send)

    self.text_0 = QPlainTextEdit()
    self.text_0.setReadOnly(True)
    self.text_0.setLineWrapMode(QPlainTextEdit.NoWrap)
    self.text_1 = QPlainTextEdit()
    self.text_1.setLineWrapMode(QPlainTextEdit.NoWrap)

    self.layout_2.addWidget(self.combobox_0, 0, 0, 1, 1)
    self.layout_2.addWidget(self.button_0, 0, 1, 1, 1)
    self.layout_2.addWidget(self.line_0, 1, 0, 1, 1)
    self.layout_2.addWidget(self.button_1, 1, 1, 1, 1)
    self.layout_4.addWidget(self.checkbox_0, 0, 0, 1, 1)
    self.layout_4.addWidget(self.combobox_1, 0, 1, 1, 1)
    self.layout_4.addWidget(self.button_2, 0, 2, 1, 1)
    self.layout_4.addWidget(self.button_3, 0, 3, 1, 1)
    self.layout_4.addWidget(self.button_4, 0, 4, 1, 1)
    self.layout_3.addWidget(self.text_0)
    self.layout_3.addLayout(self.layout_4)
    self.layout_0.addLayout(self.layout_2)
    self.layout_0.addLayout(self.layout_3)
    self.layout_1.addWidget(self.text_1)
    self.layout.addLayout(self.layout_0)
    self.layout.addLayout(self.layout_1)

    widget = QWidget(self)
    widget.setLayout(self.layout)
    self.setCentralWidget(widget)

  def onTimeoutTimer_0(self):
    port  = self.combobox_0.currentText()
    ports = populateSerialPorts()
    combobox_0_items = [ p[0] for p in ports ]
    self.combobox_0.clear()
    self.combobox_0.addItems(combobox_0_items)
    self.combobox_0.setCurrentText(port)

  def onTimeoutTimer_1(self):
    if self.sercon != None and self.sercon.isOpen():
      self.recv()

  def getTimestamp(self):
    return datetime.now().strftime('%d-%m-%Y %H:%M:%S')

  def log(self, text, end_of_line = True):
    s = ''
    if self.checkbox_0.isChecked() is True:
      s = self.getTimestamp() + ' - '
    s += text
    if end_of_line == True:
      s += '\n'
    self.text_0.setPlainText(self.text_0.toPlainText() + s)
    self.text_0.verticalScrollBar().setValue(self.text_0.verticalScrollBar().maximum())

  def error(self, text):
    box = QMessageBox(self)
    box.setIcon(QMessageBox.Critical)
    box.setWindowTitle('Error')
    box.setText(text)
    box.exec()

  def connect(self):
    if self.combobox_0.count() > 0:
      if self.sercon != None:
        self.disconnect()
      port = self.combobox_0.currentText()
      baud = int(self.combobox_1.currentText())
      self.log('>>> Try to connect `{}`'.format(port))
      try:
        self.sercon = serial.Serial(port, baud, timeout = 1)
        self.button_0.setText('Disconnect')
        self.button_0.clicked.connect(self.disconnect)
        self.setWindowTitle('Serial Monitor - ' + port)
      except SerialException:
        self.error('Cannot open the port')
    else:
      self.error('No ports to connect')

  def disconnect(self):
    if self.sercon != None and self.sercon.isOpen():
      self.sercon.close()
      self.sercon = None
      self.button_0.setText('Connect')
      self.button_0.clicked.connect(self.connect)
      self.setWindowTitle('Serial Monitor')
    else:
      self.error('No ports to disconnect')

  def send(self):
    if self.sercon != None and self.sercon.isOpen():
      if self.line_0.text() != '':
        s = str(self.line_0.text()) + '\n'
        b = s.encode()
        try:
          self.sercon.write(b)
          self.log(s, False)
        except SerialException:
          self.error('Cannot send `{}` to the port'.format(s[:-2]))
    else:
      self.error('No ports available for writing')

  def recv(self):
    if self.sercon != None and self.sercon.isOpen():
      try:
        b = b''
        while self.serial.inWaiting() > 0:
          b += self.serial.read(1000)
        self.log(b.decode(), False)
      except SerialException:
        self.error('Cannot recive data from port')
    else:
      self.error('No ports available for reading')

  def clear(self):
    self.text_0.setPlainText('')

  def extract(self):
    s = str(self.text_0.toPlainText())
    i = s.rfind('$0$')
    if i != -1:
      s = s[i + 3:]
      i = s.find('\n')
      if i == -1:
        self.error('Bad encoding')
      else:
        s = s[:i].replace(';', '\n')
        self.text_1.setPlainText(s)
        self.text_1.verticalScrollBar().setValue(self.text_1.verticalScrollBar().minimum())
    else:
      self.error('Nothing to extract')

  def save(self):
    options = QFileDialog.Options() | QFileDialog.DontUseNativeDialog
    filename, _ = QFileDialog.getSaveFileName(self, 'Save File', '', 'All Files(*);;Text Files(*.txt)', options = options)
    if filename:
      with open(filename, 'w') as f:
        f.write(self.text_1.toPlainText())

# ----------------------------------------------------------------
# Application

def run():
  app = QApplication(sys.argv)
  mon = SerialMonitor()
  mon.show()
  sys.exit(app.exec()) # use `exec_` in Python < 3

run() # entry point
