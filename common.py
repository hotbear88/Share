import os
import sqlite3
import pandas as pd
from datetime import datetime
from PySide6 import QtWidgets, QtGui, QtCore
from PySide6.QtCore import Qt, QSortFilterProxyModel, QAbstractTableModel
from PySide6.QtGui import QStandardItemModel, QColor, QFont,QFontMetrics
from PySide6.QtWidgets import (QMdiSubWindow, QMessageBox, QStyledItemDelegate, 
                        QComboBox, QProxyStyle, QStyle, QStyleOptionViewItem,
                        QLabel, QLineEdit, QPushButton, QSizePolicy)

# Set global column alignments
AL_R = Qt.AlignRight | Qt.AlignVCenter
AL_C = Qt.AlignCenter
AL_L = Qt.AlignLeft | Qt.AlignVCenter

############################################################
class BaseMD:
    def make_dialog(self, dialog_class):            # populate the dialong as sub window of the main window
        dialog = dialog_class                       # Instantiate the specific dialog
        sub_window = QMdiSubWindow(self.mdi_area)   # Get the size hint from the dialog
        sub_window.setWidget(dialog)                # Set the widget and size of the sub window
        
        self.mdi_area.addSubWindow(sub_window)      # Add the sub window to the MDI area
        sub_window.show()

        self.open_sub_windows.append(sub_window)    # added to avoid duplication of sub window
    
    def max_row_id(self, tbname):                   # Check maximum id number to create new row number
        self.cursor.execute(f"SELECT MAX(id) FROM {tbname}")
        row = self.cursor.fetchone()
        max_id = row[0]
        
        if max_id is None: # Check if the table is empty
            idx = 1
        else:
            idx = max_id + 1 # Increment the maximum ID to get the next available ID
        return idx        

    def center(self):
        qr = self.frameGeometry()  # MainWindow의 기본 위치와 크기를 가져옴
        cp = QtGui.QGuiApplication.primaryScreen().availableGeometry().center()  # 화면의 중심 좌표를 가져옴
        qr.moveCenter(cp)  # MainWindow의 중심 좌표를 화면의 중심 좌표로 이동
        self.move(qr.topLeft())  # MainWindow를 새로운 위치로 이동

    # Combobox initializing
    def combobox_initializing(self, combo_box, sql_query, params=None):
        combo_box.clear()
        combo_box.addItem("")  # Add a blank item as the first option
        if params:
            self.cursor.execute(sql_query, params)
        else:
            self.cursor.execute(sql_query)
        for row in self.cursor.fetchall():
            combo_box.addItem(str(row[0]))

    # Set combobox item index as zero
    def clear_combobox_selections(self, combo_box):
        for combo_box in self.findChildren(QtWidgets.QComboBox):
            if combo_box.currentIndex() == 0 and combo_box.currentText() != "":
                combo_box.insertItem(0, "")  # Add an empty string at the beginning
            combo_box.setCurrentIndex(0)

    # For Multiple QLineEdit contents display
    def lineEdit_contents(self, line_edit_widgets, sql_query):
        num_widgets = len(line_edit_widgets)

        for index, line_edit in enumerate(line_edit_widgets):
            #line_edit.clear()
            self.cursor.execute(sql_query)
            result = self.cursor.fetchone()

            if result:
                if num_widgets == 1:
                    item01 = str(result[0])
                    line_edit.setText(item01)
                elif num_widgets == 2:
                    item01 = str(result[0])
                    item02 = str(result[1])
                    if index == 0:
                        line_edit.setText(item01)
                    elif index == 1:
                        line_edit.setText(item02)
                elif num_widgets == 3:
                    item01 = str(result[0])
                    item02 = str(result[1])
                    item03 = str(result[2])
                    if index == 0:
                        line_edit.setText(item01)
                    elif index == 1:
                        line_edit.setText(item02)
                    elif index == 2:
                        line_edit.setText(item03)
                elif num_widgets == 4:
                    item01 = str(result[0])
                    item02 = str(result[1])
                    item03 = str(result[2])
                    item04 = str(result[3])
                    if index == 0:
                        line_edit.setText(item01)
                    elif index == 1:
                        line_edit.setText(item02)
                    elif index == 2:
                        line_edit.setText(item03)
                    elif index == 3:
                        line_edit.setText(item04)
            else:
                line_edit.setText("")

    # For Multiple combo box contents display
    def insert_combobox_contents_changed(self, combobox_widgets, sql_query):
        num_widgets = len(combobox_widgets)
        for index, combo_box in enumerate(combobox_widgets):
            
            combo_box.clear() # Clear existing items
            combo_box.addItem("")  # Add a blank item as the first option

            self.cursor.execute(sql_query)
            items = self.cursor.fetchall()

            if items:
                if num_widgets == 1:
                    combo_box.addItems([str(item[0]) for item in items]) 
                    combo_box.setCurrentText(str(items[0][0]))
                elif num_widgets == 2:
                    if index == 0:
                        combo_box.addItems([str(item[0]) for item in items])
                        combo_box.setCurrentText(str(items[0][0]))
                    elif index == 1:
                        combo_box.addItems([str(item[1]) for item in items])
                        combo_box.setCurrentText(str(items[0][1]))
            else:
                print(num_widgets)  

    def close_dialog(self): # to inform the close of the dialong to user
        confirm_dialog = QMessageBox.question(
            self, "Confirm Close", "Are you sure you want to close this operation?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if confirm_dialog == QMessageBox.Yes:
            parent = self.parentWidget()
            if parent is not None:
                parent.close()
            else:
                self.close()    # Handle the case where the parent widget is None (e.g., no parent)
        else:
            pass

############################################################
class PandasModel(QAbstractTableModel):
    def __init__(self, data, alignments=None):
        super().__init__()
        self._data = data
        if alignments is None:
            self.alignments = [Qt.AlignCenter] * data.shape[1]
        else:
            self.alignments = [Qt.AlignVCenter | alignment for alignment in alignments]      

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if index.isValid():
            if role == Qt.ItemDataRole.DisplayRole:
                value = self._data.iloc[index.row(), index.column()]
                if isinstance(value, (float, int)):
                    return value    # 숫자 값을 그대로 반환
                elif pd.isna(value) or value is None:
                    return ""  # Return empty string instead of None
                return str(value)
            elif role == Qt.TextAlignmentRole:
                return self.alignments[index.column()]
        return None

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return str(self._data.columns[section])
        elif orientation == Qt.Vertical and role == Qt.ItemDataRole.DisplayRole:
            return str(self._data.index[section])
        return None

    def sort(self, column, order):
        self.layoutAboutToBeChanged.emit()
        self._data = self._data.sort_values(by=self._data.columns[column], ascending=(order == Qt.AscendingOrder))
        self.layoutChanged.emit()

    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled

    def update_data(self, new_data):
        self.layoutAboutToBeChanged.emit()
        self._data = new_data
        self.layoutChanged.emit()


############################################################
def connectdb():
    script_folder = os.path.dirname(os.path.abspath(__file__))  # Set the working directory to the folder where your script is located
    os.chdir(script_folder)
    relative_dbs_folder = '' # Relative path to the 'dbs' folder in case

    filename = 'testdb.db'
    db_path = os.path.join(script_folder, filename)

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        return conn, cursor
    except sqlite3.Error as e:
        print(f"데이터베이스 연결 중 오류 발생: {e}")
        return None, None

############################################################
def Today():
    now = datetime.now()
    curr_date = now.strftime("%Y-%m-%d")
    ddt = f"{curr_date}" 

    return ddt

############################################################
def format_number(value, format_type='auto', custom_format=None):
    if value is None:
        return ""
    
    if format_type == 'auto':
        # Automatically detect the type
        if isinstance(value, (int, float)):
            format_type = 'numeric'
        elif isinstance(value, str):
            try:
                datetime.strptime(value, '%Y-%m-%d')
                format_type = 'date'
            except ValueError:
                format_type = 'string'
        elif isinstance(value, datetime):
            format_type = 'date'
    
    if format_type in ['numeric', 'inumeric', 'snumeric', 'dnumeric', 'tnumeric']:
        if isinstance(value, (int, float)):
            if format_type == 'inumeric' and isinstance(value, int):
                return f"{value}"  # No comma for integers
            elif format_type == 'numeric':
                return f"{value:,}"  # Add comma for all numbers
            elif format_type == 'snumeric':
                return f"{value:,.1f}"  # 1 decimal place
            elif format_type == 'dnumeric':
                return f"{value:,.2f}"  # 2 decimal places
            elif format_type == 'tnumeric':
                return f"{value:,.3f}"  # 3 decimal places
            else:
                return f"{value:,}"  # Default to adding comma
        else:
            return str(value)
    
    elif format_type == 'date':
        if isinstance(value, str):
            try:
                date_obj = datetime.strptime(value, '%Y-%m-%d')
            except ValueError:
                return value
        elif isinstance(value, datetime):
            date_obj = value
        else:
            return str(value)
        
        if custom_format:
            return date_obj.strftime(custom_format)
        else:
            return date_obj.strftime('%Y-%m-%d')
    
    elif format_type == 'string':
        return str(value)
    
    else:
        return str(value)

# Clear the contents of each Widget
def clear_widget_data(widget):
    if isinstance(widget, QtWidgets.QLineEdit):
        widget.clear()
    elif isinstance(widget, QtWidgets.QComboBox):
        widget.setCurrentIndex(0)
    elif isinstance(widget, QtWidgets.QWidget):
        for child in widget.findChildren(QtWidgets.QWidget):
            clear_widget_data(child)

class NumberFormatDelegate(QStyledItemDelegate):
    def __init__(self, column_type, parent=None):
        super().__init__(parent)
        self.column_type = column_type

    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        column = index.column()
        value = index.data(Qt.ItemDataRole.DisplayRole)
        
        format_string = self.column_type[column]

        if format_string in ["numeric", "snumeric", "dnumeric", "tnumeric"]:
            option.text = format_number(value, format_string)

    def setEditorData(self, editor, index):
        column = index.column()
        value = index.data(Qt.EditRole)
        format_string = self.column_type[column]

        try:
            if format_string in ["numeric", "snumeric", "dnumeric", "tnumeric"]:
                editor.setText(format_number(value, format_string))
            else:
                editor.setText(str(value))
        
        except AttributeError:
            print("AttributeError: 'QSpinBox' object has no attribute 'setText'")

    def setModelData(self, editor, model, index):
        column = index.column()
        value = editor.text().replace(",", "")
        format_string = self.column_type[column]
        
        if format_string in ["numeric", "snumeric", "dnumeric", "tnumeric"]:
            value = float(value) if value else None
        else:
            value = str(value)

        model.setData(index, value, Qt.EditRole)

class NumericStringSortModel(QSortFilterProxyModel):    # NumericStringSortModel class for custom sorting
    def lessThan(self, left, right):
        left_data = left.data().strip()
        right_data = right.data().strip()
    
        try:    # Compare numeric and string values
            left_data_numeric = float(left_data)
            right_data_numeric = float(right_data)
            return left_data_numeric < right_data_numeric
        except ValueError:  # If conversion to float fails, compare as strings
            return left_data < right_data

def create_model(self):    # Create table_view and QSortFilterProxyModel
    self.model = QStandardItemModel()
    self.proxy_model = NumericStringSortModel(self.model)
    self.proxy_model.setSourceModel(self.model)

def create_alt_row_color_style():
    class AltRowColor(QProxyStyle):
        def drawPrimitive(self, element, option, painter, widget=None):
            if element == QStyle.PE_PanelItemViewRow:
                if option.features & QStyleOptionViewItem.Alternate:
                    painter.fillRect(option.rect, QColor(243, 243, 243))  # Light Gray
                else:
                    painter.fillRect(option.rect, QColor(255, 255, 255))  # White
            else:
                super().drawPrimitive(element, option, painter, widget)
    return AltRowColor()

############################################################
def set_flag(self):
    self.setWindowFlags(self.windowFlags() | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)  

# Deletion on close for sub windows
def deletion_on_close(self):
    self.setAttribute(QtCore.Qt.WA_DeleteOnClose)  

def clear_widget_data(widget):  # Clear the contents of each Widget
    if isinstance(widget, QtWidgets.QLineEdit):
        widget.clear()
    elif isinstance(widget, QtWidgets.QComboBox):
        widget.setCurrentIndex(0)
    elif isinstance(widget, QtWidgets.QWidget):
        for child in widget.findChildren(QtWidgets.QWidget):
            clear_widget_data(child)

# Set the alignment of the combobox
def set_cbbox_alignment(cbbox):
    cbbox.setCurrentIndex(0)                        # Set the index at the top
    cbbox.setEditable(True)                         # Make combobox editable
    line_edit = cbbox.lineEdit()                    # Get the line edit of combo box
    line_edit.setAlignment(QtCore.Qt.AlignCenter)   # Set the line_edit alignment to the center

# Set the alignment of the LineEdit
def set_lineEdit_alignment(lineEdit, alignment):
    lineEdit.setAlignment(alignment)

# Set the alignment of the QLabel
def set_lblTxt_alignment(lbltxt, alignment):
    lbltxt.setAlignment(alignment)

############################################################
class StyleSetup:
    # QLabel Style
    lbl_style  = """
        QLabel {
            font-family: 맑은 고딕;
            font-size: 11px;    
            height: 20px;    
        }
    """

    lbl_border_style = """
        QLabel {
            border: none;        
            border-bottom: 0.5px solid gray;        
        }
    """        

    # QLineEdit Style
    line_style  = """
        QLineEdit {
            font-family: 맑은 고딕;
            font-size: 11px;    
            height: 20px;        
        }
    """

    # QPushbutton Style
    button_style = """

    QPushButton{
        /*color: white;*/
        background-color: rgb(220, 220, 220);
        border-radius: 1px;
        padding: 2px 4px;
        margin: 1px;
    }
    QPushButton:hover{
        background-color: rgb(200, 200, 200);
    }

    QPushButton:selected, QPushButton:pressed{
        background-color: rgb(180, 180, 180);
    }

    """

    # QComboBox Style
    combo_style  = """
        QComboBox {
            font-family: 맑은 고딕;
            font-size: 11px;    
            height: 20px;
            line-height: 20px;
            border-bottom: 0.1px solid gray; /* 밑부분 테두리선 설정 */
        }
    """

    # 테이블 뷰에서 선택된 아이템의 스타일: 흰색 텍스트, 회색 배경
    tableview_style = """
    QTableView::item:selected {
        color: white;
        background-color: #a6a6a6;
    }
    """

    # Main Ui Style
    main_style = """       
        /* 공통 스타일 */
        QMenuBar, QMenu {
            font-family: 맑은 고딕;
            font-size: 9pt;
        }

        /* 메뉴바 스타일 */
        QMenuBar {
            background-color: rgb(240, 240, 240);
            border: none;
        }

        QMenuBar::item {
            background-color: transparent;
            color: black;
            border-radius: 1px;
            padding: 2px 10px;
            margin: 0;
        }

        QMenuBar::item:hover,
        QMenuBar::item:selected,
        QMenuBar::item:pressed {
            padding: 2px 4px 2px 12px;
        }

        QMenuBar::item:hover {
            background-color: rgba(0, 0, 155, 0.05);
        }

        QMenuBar::item:selected {
            background-color: rgba(0, 0, 155, 0.1);
        }

        QMenuBar::item:pressed {
            background-color: rgba(0, 0, 255, 0.5);
        }

        /* 툴바 스타일 */
        QToolBar {
            background-color: black;
            color: white;
        }

        /* 메뉴 및 서브메뉴 공통 스타일 */
        QMenu, QMenu QMenu {
            background-color: white;
            color: black;
            /*border: 1px solid black;*/
            margin: 2px;
        }

        QMenu::item, QMenu QMenu::item {
            background-color: transparent;
            padding: 2px 20px;
        }

        QMenu::item:selected,
        QMenu::item:hover,
        QMenu QMenu::item:selected,
        QMenu QMenu::item:hover {
            background-color: rgb(51, 51, 153);
            color: white;
            padding: 2px 12px 2px 22px;
        }

        /* 서브메뉴 특정 스타일 (필요한 경우 추가) */
        QMenu QMenu {
            /* 서브메뉴에만 적용할 특별한 스타일이 있다면 여기에 추가 */
        }

    """

    # 테이블 뷰의 cell font family and size
    font_style = QFont("맑은 고딕", 8)

    # 테이블 뷰의 header style
    @staticmethod
    def set_header_style(header):
        header.setStyleSheet("""
            QHeaderView::section { 
                background-color: rgb(220, 220, 220); 
                font-family: 맑은 고딕;
                font-size: 11px;
                font-weight: bold;
            }
        """)

    class FixedSizeButton(QPushButton):
        def __init__(self, text, parent=None):
            super().__init__(text, parent)
            self.setFixedSize(100, 23)  # Set your desired button size here
            self.setStyleSheet(StyleSetup.button_style)

        def resizeEvent(self, event):
            super().resizeEvent(event)
            self.adjustFontSize()

        def adjustFontSize(self):
            font = self.font()
            metrics = QFontMetrics(font)
            elided_text = metrics.elidedText(self.text(), Qt.ElideRight, self.width() - 10)

            if elided_text != self.text():
                font_size = font.pointSize()
                while metrics.horizontalAdvance(elided_text) > self.width() - 10 and font_size > 0:
                    font_size -= 1
                    font.setPointSize(font_size)
                    metrics = QFontMetrics(font)
                    elided_text = metrics.elidedText(self.text(), Qt.ElideRight, self.width() - 10)

            # Shrink the font size if the text is longer than 8 characters
            if len(self.text()) > 8:
                font_size = font.pointSize()
                while metrics.horizontalAdvance(self.text()) > self.width() - 10 and font_size > 0:
                    font_size -= 1
                    font.setPointSize(font_size)
                    metrics = QFontMetrics(font)
                    
            self.setFont(font)

    @staticmethod
    def create_button(text, parent):
        button = StyleSetup.FixedSizeButton(text, parent)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        button.setSizePolicy(sizePolicy)
        return button

    @staticmethod
    def create_label(text, parent):
        label = QLabel(text, parent)
        label.setAlignment(Qt.AlignCenter)
        label.setFixedHeight(23)
        label.setStyleSheet(StyleSetup.lbl_style)
        return label

    @staticmethod
    def create_line_edit(parent):
        line_edit = QLineEdit(parent)
        line_edit.setFixedHeight(23)
        line_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        line_edit.setStyleSheet(StyleSetup.line_style)
        return line_edit    

    @staticmethod
    def create_combo_box(parent):
        combo_box = QComboBox(parent)       
        combo_box.setFixedHeight(25)
        combo_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        combo_box.setStyleSheet(StyleSetup.combo_style)
        return combo_box