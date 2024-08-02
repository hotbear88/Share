import sys
import pandas as pd
from PySide6.QtCore import Qt, QCoreApplication, QMetaObject, QSize
from PySide6.QtWidgets import (QApplication, QMessageBox, QDialog, QHeaderView, 
                                QComboBox, QGridLayout, QTableView)
from common import *

class Ui_Product(object):
    def setupUi(self, ViewProd):
        ViewProd.setObjectName("ViewProd")
        ViewProd.resize(765, 448)
        
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        ViewProd.setSizePolicy(sizePolicy)
        
        self.gridLayout_2 = QGridLayout(ViewProd)
        self.gridLayout = QGridLayout()
        
        self.label = StyleSetup.create_label("id", ViewProd)
        self.label_2 = StyleSetup.create_label("name", ViewProd)
        self.label_3 = StyleSetup.create_label("Empty", ViewProd)
        self.label_4 = StyleSetup.create_label("Total", ViewProd)
        self.label_5 = StyleSetup.create_label("DiffVal", ViewProd)
        self.label_6 = StyleSetup.create_label("remark", ViewProd)
        self.label_7 = StyleSetup.create_label("code", ViewProd)
        
        self.show_button = StyleSetup.create_button("ShowAll", ViewProd)
        self.save_button = StyleSetup.create_button("Insert", ViewProd)
        self.search_button = StyleSetup.create_button("Search", ViewProd)
        self.update_button = StyleSetup.create_button("Update", ViewProd)
        self.delete_button = StyleSetup.create_button("Delete", ViewProd)
        self.clear_button = StyleSetup.create_button("Clear", ViewProd)
        self.export_button = StyleSetup.create_button("Export", ViewProd)
        self.close_button = StyleSetup.create_button("Close", ViewProd)
        
        self.lbl_id = StyleSetup.create_label("", ViewProd)
        self.entry_code = StyleSetup.create_line_edit(ViewProd)
        self.entry_qty1 = StyleSetup.create_line_edit(ViewProd)
        self.entry_qty2 = StyleSetup.create_line_edit(ViewProd)
        self.entry_qty3 = StyleSetup.create_line_edit(ViewProd)
        self.entry_remark = StyleSetup.create_line_edit(ViewProd)
        self.cb_iname = StyleSetup.create_combo_box(ViewProd)
        
        self.table_view_display = QTableView(ViewProd)
        self.table_view_display.setBaseSize(QSize(0, 1))

        self.arrange_layout()

        self.retranslateUi(ViewProd)
        QMetaObject.connectSlotsByName(ViewProd)
        
    def arrange_layout(self):
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.table_view_display, 0, 0, 1, 8)

        # Apply the styles to the tableview object
        self.table_view_display.setStyleSheet(StyleSetup.tableview_style)

        # Set the font family and size for the QTableView
        self.table_view_display.setFont(StyleSetup.font_style)   

        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.lbl_id, 1, 1, 1, 1)
        self.gridLayout.addWidget(self.label_7, 2, 0, 1, 1)
        self.gridLayout.addWidget(self.entry_code, 2, 1, 1, 1)
        self.gridLayout.addWidget(self.label_2, 2, 2, 1, 1)
        self.gridLayout.addWidget(self.cb_iname, 2, 3, 1, 1)
        self.gridLayout.addWidget(self.search_button, 2, 6, 1, 1)
        self.gridLayout.addWidget(self.update_button, 2, 7, 1, 1)
        
        self.gridLayout.addWidget(self.label_3, 3, 0, 1, 1)
        self.gridLayout.addWidget(self.entry_qty1, 3, 1, 1, 1)
        self.gridLayout.addWidget(self.label_4, 3, 2, 1, 1)
        self.gridLayout.addWidget(self.entry_qty2, 3, 3, 1, 1)
        self.gridLayout.addWidget(self.delete_button, 3, 7, 1, 1)
        
        self.gridLayout.addWidget(self.label_5, 4, 0, 1, 1)
        self.gridLayout.addWidget(self.entry_qty3, 4, 1, 1, 1)
        self.gridLayout.addWidget(self.label_6, 4, 4, 1, 1)
        self.gridLayout.addWidget(self.entry_remark, 4, 5, 1, 1)
        self.gridLayout.addWidget(self.export_button, 4, 6, 1, 1)
        self.gridLayout.addWidget(self.close_button, 4, 7, 1, 1)
        
        self.gridLayout.addWidget(self.show_button, 1, 6, 1, 1)
        self.gridLayout.addWidget(self.save_button, 1, 7, 1, 1)
        self.gridLayout.addWidget(self.clear_button, 3, 6, 1, 1)

    def retranslateUi(self, ViewProd):
        ViewProd.setWindowTitle(QCoreApplication.translate("ViewProd", "Input Transactions", None))
        
class Product(QDialog, Ui_Product, BaseMD):

    def __init__(self):
        super().__init__()    

        self.setupUi(self)                      # Load UI
        self.conn, self.cursor = connectdb()    # Connect to db

        set_flag(self)                          # Set min, max, close on title bar
        deletion_on_close(self)                 
        create_model(self)                      # Initialize model

        self.resize(800, 720) 

        self.set_df()                           # Initialize pandas dataFrame
        self.setup_tableview()                  # Set the tableview
        self.set_column_widths()                # Set the column widths

        self.get_combobox_contents()
        self.conn_button_to_method()
        self.conn_signal_to_slot()
        self.set_tab_order()

        self.entry_code.setFocus()

        # Apply the custom style
        AltRowColor = create_alt_row_color_style()
        self.table_view_display.setStyle(AltRowColor)
        self.table_view_display.setAlternatingRowColors(True)

    def set_df(self):
        self.df = self.load_data()   # Load data into a DataFrame       

        if self.df.empty:
            print("DataFrame is empty!")
            return
                
        # Define column types
        self.column_type = ["", "", "", "numeric", "numeric", "numeric", ""]

        # Ensure column_type matches the number of columns in self.df
        if len(self.column_type) != len(self.df.columns):
            print("Mismatch between column_type length and number of columns in DataFrame.")
            return
        
        # Convert numeric columns to float
        for i, col_type in enumerate(self.column_type):
            if col_type == 'numeric':
                self.df.iloc[:, i] = pd.to_numeric(self.df.iloc[:, i], errors='coerce')

        # Define alignments
        halignments = [AL_C, AL_L, AL_L, AL_R, AL_R, AL_R, AL_L]

        # Create and set the model
        self.model = PandasModel(self.df, alignments=halignments)
        self.table_view_display.setModel(self.model)
        vertical_scrollbar = self.table_view_display.verticalScrollBar()
        vertical_scrollbar.setValue(vertical_scrollbar.maximum())

        # Set up the delegate for number formatting
        delegate = NumberFormatDelegate(self.column_type, self)
        self.table_view_display.setItemDelegate(delegate)

        # Set the alignment of the line edit widgets
        line_edits = [self.entry_code, self.entry_qty1, self.entry_qty2, self.entry_qty3, self.entry_remark]
        alignments = [AL_C, AL_R, AL_R, AL_R, AL_L]
        for line_edit, alignment in zip(line_edits, alignments):
            set_lineEdit_alignment(line_edit, alignment)

    def setup_tableview(self):
        header = self.table_view_display.horizontalHeader()
        num_columns = len(self.df.columns)

        for i in range(num_columns):  # columns
            header.setSectionResizeMode(i, QHeaderView.Interactive)
        
        self.table_view_display.verticalHeader().setVisible(False)
        self.table_view_display.setSortingEnabled(True)                     # Enable sorting  
        self.table_view_display.sortByColumn(0, Qt.AscendingOrder)        # Sort by 'id' column (assuming 'id' is the first column)      

        # Set delegate for column alignment and formatting
        delegate = NumberFormatDelegate(self.column_type, self.table_view_display)
        self.table_view_display.setItemDelegate(delegate)

    def set_column_widths(self):    # Set the column widths
        column_widths = [80, 100, 100, 100, 100, 100, 150]
        for i, width in enumerate(column_widths):
            self.table_view_display.setColumnWidth(i, width)
        
    # Pass combobox info and sql to next method
    def get_combobox_contents(self):
        self.insert_combobox_initiate(self.cb_iname, "SELECT DISTINCT pname FROM product ORDER BY pname")

    def insert_combobox_initiate(self, combo_box, sql_query):
        self.combobox_initializing(combo_box, sql_query) 

    def conn_button_to_method(self):    # Connect the button to the method
        button_methods = {
            'show_button': self.make_data,
            'clear_button': self.clear_data,
            'close_button': self.close_dialog,
            'save_button': self.tb_insert,
            'update_button': self.tb_update,
            'delete_button': self.tb_delete,
            'search_button': self.search_data,
            'export_button': self.export_table
        }
        for button_name, method in button_methods.items():
            button = getattr(self, button_name)
            button.clicked.connect(method)

    # Connect signal to method    
    def conn_signal_to_slot(self):
        self.table_view_display.clicked.connect(self.show_selected_data)
        self.cb_iname.activated.connect(self.cb_iname_changed)
        self.entry_qty1.editingFinished.connect(self.calc_qty)
        self.entry_qty2.editingFinished.connect(self.calc_qty)

    # Tab order for sub window
    def set_tab_order(self):
        widgets = [self.lbl_id, self.entry_code, self.cb_iname, 
            self.entry_qty1, self.entry_qty2, self.entry_qty3, self.entry_remark, 
            self.show_button, self.clear_button, self.save_button, 
            self.update_button, self.delete_button, self.close_button]
        
        for i in range(len(widgets) - 1):
            self.setTabOrder(widgets[i], widgets[i + 1])

    def load_data(self):
        try:
            query = "SELECT * FROM vw_list ORDER BY id"           
            self.cursor.execute(query)
            columns = [column[0] for column in self.cursor.description]
            data = self.cursor.fetchall()
            data = [list(row) for row in data]  # convert tuples to lists
            return pd.DataFrame(data, columns=columns)
        except Exception as e:
            print(f"Error loading data: {e}")
            return pd.DataFrame()  # Return an empty DataFrame if there's an error
    
    def make_data(self):
        self.df = self.load_data()
        self.model = PandasModel(self.df)
        self.table_view_display.setModel(self.model)
        vertical_scrollbar = self.table_view_display.verticalScrollBar()
        vertical_scrollbar.setValue(vertical_scrollbar.maximum())

    def load_result(self, query):
        try:
            query = query
            self.cursor.execute(query)
            columns = [column[0] for column in self.cursor.description]
            data = self.cursor.fetchall()
            data = [list(row) for row in data]  # convert tuples to lists
            return pd.DataFrame(data, columns=columns)

        except Exception as e:
            print(f"Error loading data: {e}")
            return pd.DataFrame()  # Return an empty DataFrame if there's an error

    def make_result(self, query):
        self.df = self.load_result(query)
        self.model = PandasModel(self.df)
        self.table_view_display.setModel(self.model)
        vertical_scrollbar = self.table_view_display.verticalScrollBar()
        vertical_scrollbar.setValue(vertical_scrollbar.maximum())

    # Get the value of other variables
    def get_general_input(self):
        iname = str(self.cb_iname.currentText())
        qty1 = float(self.entry_qty1.text() or 0)
        qty2 = float(self.entry_qty2.text() or 0)
        qty3 = abs(qty2-qty1)
        remark = str(self.entry_remark.text())

        return iname, qty1, qty2, qty3, remark
    
    # Insert new data to the table
    def tb_insert(self):
        pass

    # Revise the values in the selected row
    def tb_update(self):
        pass

    # Delete selected row in the table
    def tb_delete(self):
        pass

    # Search data
    def search_data(self):
        iname = self.cb_iname.currentText()
        conditions = {
                    'v01': (iname, "iname like '%{}%'"),
                    }
        selected_conditions = []
        for key, (value, condition_format) in conditions.items():
            if len(value) > 0:
                selected_conditions.append(condition_format.format(value))

        if not selected_conditions:
            QMessageBox.about(self, "검색 조건 확인", "검색 조건이 비어 있습니다!")
            return

        # Join the selected conditions to form the SQL query
        search_query = f"SELECT * FROM vw_list WHERE {' AND '.join(selected_conditions)} ORDER BY id"

        QMessageBox.about(self, "검색 조건 확인", 
            f"Description: {iname}\n\n위 조건으로 검색을 수행합니다!")
                
        self.make_result(search_query)  

    def cb_iname_changed(self):
        self.entry_code.clear()
        tablename = "product"
        selected_item = self.cb_iname.currentText()

        if selected_item:
            query = f"SELECT DISTINCT pcode From {tablename} WHERE pname ='{selected_item}'"
            line_edit_widgets = [self.entry_code]
        
            # Check if any line edit widgets are provided
            if line_edit_widgets:
                self.lineEdit_contents(line_edit_widgets, query)
            else:
                pass

    def calc_qty(self):
        q1 = float(self.entry_qty1.text() or 0)
        q2 = float(self.entry_qty2.text() or 0)

        if q1 or q2:
            q3 = abs(q1-q2)
            self.entry_qty3.setText(str(q3))
        else:
            ValueError

    # table widget cell click
    def show_selected_data(self, index):
        row = index.row()
        widgets = [self.lbl_id, self.entry_code, self.cb_iname,
                self.entry_qty1, self.entry_qty2, self.entry_qty3,
                self.entry_remark]
        
        for i, wg in enumerate(widgets):
            value = self.model._data.iloc[row, i]
            if isinstance(wg, QComboBox):
                wg.setCurrentText(str(value))
            else:
                wg.setText(format_number(value))

    # clear input field entry
    def clear_data(self):
        self.lbl_id.setText("")
        clear_widget_data(self)

    # Export data to Excel sheet                
    def export_table(self):
        pass
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = Product()
    main_window.show()
    sys.exit(app.exec())    