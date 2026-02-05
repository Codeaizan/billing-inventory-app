from PyQt5.QtCore import QObject, pyqtSignal

class AppSignals(QObject):
    inventory_updated = pyqtSignal()

app_signals = AppSignals()
