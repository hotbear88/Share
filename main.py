import sys
import traceback
import logging
from datetime import datetime
from PySide6.QtWidgets import QApplication, QMainWindow, QMdiArea, QMdiSubWindow
from PySide6.QtGui import QAction
from common import *
from pcode import *
from inputlist import *

logging.basicConfig(filename='output.txt', level=logging.INFO, 
                    format='%(asctime)s - %(message)s', 
                    datefmt='%Y-%m-%d %H:%M:%S')

def log(message):
    logging.info(message)

class BasicInfo(CodeMain):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        log(f"BasicInfo Created: {id(self)}")

    def closeEvent(self, event):
        log(f"BasicInfo closeEvent Called: {id(self)}")
        self.main_window.handle_sub_window_close(self)
        log(f"{self.__class__.__name__} Closed")
        event.accept()

class ProductInfo(Product):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        log(f"ProductInfo Created: {id(self)}")

    def closeEvent(self, event):
        log(f"ProductInfo closeEvent Called: {id(self)}")
        self.main_window.handle_sub_window_close(self)
        log(f"{self.__class__.__name__} Closed")
        event.accept()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.mdi = QMdiArea()
        self.setCentralWidget(self.mdi)

        self.open_windows = {1: None, 2: None}
        self.sub_window_objects = []
        self.cnt = 0

        bar = self.menuBar()

        file_menu = bar.addMenu("File")
        file_menu.addAction("Infos")

        input_menu = bar.addMenu("Input")
        input_menu.addAction("Inputs")

        window_menu = bar.addMenu("Window")
        window_menu.addAction("Cascaded")
        window_menu.addAction("Tiled")

        bar.triggered[QAction].connect(self.window_action)

        self.setWindowTitle("MDI Application")

    def open_dialog(self, dialog_num, dialog_class, title):
        log(f"open_dialog start: dialog_num={dialog_num}, dialog_class={dialog_class.__name__}")
        try:
            if self.open_windows[dialog_num] is None or not self.open_windows[dialog_num].isVisible():
                log(f"Start new window creation: {dialog_class.__name__}")
                dialog = dialog_class(self)
                log(f"dialog object created: id={id(dialog)}")
                sub = QMdiSubWindow()
                log(f"QMdiSubWindow created: id={id(sub)}")
                sub.setWidget(dialog)
                sub.setWindowTitle(title)
                self.mdi.addSubWindow(sub)
                sub.show()
                
                self.open_windows[dialog_num] = sub
                self.sub_window_objects.append(dialog)
                log(f"added to sub_window_objects: {dialog_class.__name__}(id={id(dialog)})")

                log("After open_dialog function, sub window objects remained in memory:")
                self.print_sub_window_objects()
                            
            else:
                log(f"Activated previously opened sub window: dialog_num={dialog_num}")
                self.open_windows[dialog_num].showNormal()
                self.open_windows[dialog_num].activateWindow()
        except Exception as e:
            log(f"Exception happened in open_dialog function: {e}")
            log(traceback.format_exc())
        finally:
            log("open_dialog closed")
            self.print_remaining_windows()

    def window_action(self, q):
        log(f"window_action called: action={q.text()}")
        try:
            if q.text() == "Infos":
                self.open_dialog(1, BasicInfo, "Input Master Infos")
            elif q.text() == "Inputs":
                self.open_dialog(2, ProductInfo, "Input Transaction List")
            elif q.text() == "Cascaded":
                self.mdi.cascadeSubWindows()
            elif q.text() == "Tiled":
                self.mdi.tileSubWindows()
        except Exception as e:
            log(f"Exception happened in window_action function: {e}")
            log(traceback.format_exc())

    def handle_sub_window_close(self, dialog):
        log(f"handle_sub_window_close called: dialog={type(dialog).__name__}, id={id(dialog)}")
        if dialog in self.sub_window_objects:
            self.sub_window_objects.remove(dialog)
            log("After execution of the handle_sub_window_close, remained sub window objects in memory:")
            self.print_sub_window_objects()
            for key, value in self.open_windows.items():
                if value and value.widget() == dialog:
                    log(f"cleared from open_windows function: key={key}")
                    self.open_windows[key] = None
                    break
        else:
            log(f"Warning: {type(dialog).__name__}(id={id(dialog)}) is not in sub_window_objects.")

        # Check the open_windows dictionary whether it is empty or not.
        if not any(self.open_windows.values()):
            self.open_windows = {1: None, 2: None}        
        
        self.print_remaining_windows()

    def closeEvent(self, event):
        log("MainWindow closeEvent called")
        for sub in self.mdi.subWindowList():
            sub.close()
        super().closeEvent(event)

    def print_sub_window_objects(self):
        log([f"{type(obj).__name__}(id={id(obj)})" for obj in self.sub_window_objects])
        self.cnt += 1
        log(str(self.cnt))

    def print_remaining_windows(self):
        log("currently opened sub windows:")
        for key, value in self.open_windows.items():
            if value and value.isVisible():
                log(f"  Window {key}: {type(value.widget()).__name__}(id={id(value.widget())})")
        log(f"sub_window_objects: {[type(obj).__name__ for obj in self.sub_window_objects]}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec())