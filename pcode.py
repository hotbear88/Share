import sys
import pandas as pd
from PySide6.QtCore import Qt, QCoreApplication, QMetaObject, QSize
from PySide6.QtWidgets import (QApplication, QMessageBox, QDialog, QHeaderView,
                                QGridLayout, QSpacerItem, QTableView, )
from common import *

tbname = "product"

class Ui_PCodeDialog(object):
    def setupUi(self, P_Dialog):

        P_Dialog.setObjectName("P_Dialog")
        P_Dialog.resize(387, 435)
        
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        P_Dialog.setSizePolicy(sizePolicy)

        self.gridLayout = QGridLayout()
        self.gridLayout_2 = QGridLayout(P_Dialog)
  
        self.label_2 = StyleSetup.create_label("code", P_Dialog)
        self.label_3 = StyleSetup.create_label("id", P_Dialog)
        self.label_4 = StyleSetup.create_label("name", P_Dialog)
        self.pb_show = StyleSetup.create_button("ShowAll", P_Dialog)
        self.pb_insert = StyleSetup.create_button("Insert", P_Dialog)
        self.pb_search = StyleSetup.create_button("Search", P_Dialog)
        self.pb_update = StyleSetup.create_button("Update", P_Dialog)
        self.pb_clear = StyleSetup.create_button("Clear", P_Dialog)
        self.pb_delete = StyleSetup.create_button("Delete", P_Dialog)
        self.pb_export = StyleSetup.create_button("Export", P_Dialog)
        self.pb_close = StyleSetup.create_button("Close", P_Dialog)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.lbl_id = StyleSetup.create_label("", P_Dialog)
        self.entry_pcode = StyleSetup.create_line_edit(P_Dialog)
        self.entry_pname = StyleSetup.create_line_edit(P_Dialog)
        self.tv_pcode = QTableView(P_Dialog)
        self.tv_pcode.setBaseSize(QSize(0, 1))

        self.arrange_layout()
        self.retranslateUi(P_Dialog)
        QMetaObject.connectSlotsByName(P_Dialog)
    
    def arrange_layout(self):
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.tv_pcode, 0, 0, 1, 5)

        # Apply the styles to the tableview object
        self.tv_pcode.setStyleSheet(StyleSetup.tableview_style)

        # Set the font family and size for the QTableView
        self.tv_pcode.setFont(StyleSetup.font_style)     

        self.gridLayout.addItem(self.horizontalSpacer, 6, 1, 1, 1)

        self.gridLayout.addWidget(self.label_3, 3, 0, 1, 1)
        self.gridLayout.addWidget(self.pb_update, 4, 4, 1, 1)
        self.gridLayout.addWidget(self.lbl_id, 3, 1, 1, 1)
        self.gridLayout.addWidget(self.pb_insert, 3, 4, 1, 1)
        self.gridLayout.addWidget(self.pb_export, 6, 3, 1, 1)
        self.gridLayout.addWidget(self.pb_close, 6, 4, 1, 1)
        self.gridLayout.addWidget(self.entry_pcode, 4, 1, 1, 1)
        self.gridLayout.addWidget(self.pb_search, 4, 3, 1, 1)
        self.gridLayout.addWidget(self.label_2, 4, 0, 1, 1)
        self.gridLayout.addWidget(self.entry_pname, 5, 1, 1, 1)
        self.gridLayout.addWidget(self.label_4, 5, 0, 1, 1)
        self.gridLayout.addWidget(self.pb_show, 3, 3, 1, 1)
        self.gridLayout.addWidget(self.pb_clear, 5, 3, 1, 1)
        self.gridLayout.addWidget(self.pb_delete, 5, 4, 1, 1)

    def retranslateUi(self, P_Dailog):
        P_Dailog.setWindowTitle(QCoreApplication.translate("P_Dialog", "Code Input", None))

class CodeMain(QDialog, Ui_PCodeDialog, BaseMD):
    def __init__(self):
        super().__init__()

        self.setupUi(self)
        self.conn, self.cursor = connectdb()

        set_flag(self)
        deletion_on_close(self)  
        
        create_model(self)                      # Initialize model

        self.resize(400, 450)

        self.set_df()                           # Initialize pandas dataFrame
        self.setup_tableview()                  # Set the tableview
        self.set_column_widths()                # Set the column widths

        self.conn_button_to_method()            # Set button action connect
        self.conn_signal_to_slot()        
        self.set_tab_order()                    # Set tab order
       
        self.entry_pcode.setFocus()

        # Apply the custom style
        AltRowColor = create_alt_row_color_style()
        self.tv_pcode.setStyle(AltRowColor)
        self.tv_pcode.setAlternatingRowColors(True)

    def set_df(self):
        self.df = self.load_data()   # Load data into a DataFrame

        if self.df.empty:
            print("DataFrame is empty!")
            return

        # Define column types
        self.column_type = ["numeric", "", ""]

        # Ensure column_type matches the number of columns in self.df
        if len(self.column_type) != len(self.df.columns):
            print("Mismatch between column_type length and number of columns in DataFrame.")
            return

        # Convert numeric columns to float
        for i, col_type in enumerate(self.column_type):
            if col_type == 'numeric':
                self.df.iloc[:, i] = pd.to_numeric(self.df.iloc[:, i], errors='coerce')

        # Define alignments
        halignments = [AL_C, AL_L, AL_L]

        # Create and set the model
        self.model = PandasModel(self.df, alignments=halignments)
        self.tv_pcode.setModel(self.model)

        # Set up the delegate for number formatting
        delegate = NumberFormatDelegate(self.column_type, self)
        self.tv_pcode.setItemDelegate(delegate)

        # Set the alignment of the line edit widgets
        line_edits = [self.entry_pcode, self.entry_pname]
        alignments = [AL_C, AL_C]
        for line_edit, alignment in zip(line_edits, alignments):
            set_lineEdit_alignment(line_edit, alignment)

    def setup_tableview(self):
        header = self.tv_pcode.horizontalHeader()
        num_columns = len(self.df.columns)

        for i in range(num_columns):  # 3 columns
            header.setSectionResizeMode(i, QHeaderView.Interactive)
        
        self.tv_pcode.verticalHeader().setVisible(False)
        self.tv_pcode.setSortingEnabled(True)                   # Enable sorting
        self.tv_pcode.sortByColumn(0, Qt.AscendingOrder)        # Sort by 'id' column ('id' is the first column)

        # Set delegate for column alignment and formatting
        delegate = NumberFormatDelegate(self.column_type, self.tv_pcode)
        self.tv_pcode.setItemDelegate(delegate)

    def set_column_widths(self):    # Set the column widths
        column_widths = [60, 100, 100]
        for i, width in enumerate(column_widths):
            self.tv_pcode.setColumnWidth(i, width)

    def conn_button_to_method(self):    # Connect the button to the method
        button_methods = {
            'pb_show': self.make_data,
            'pb_search': self.search_data,
            'pb_clear': self.clear_data,
            'pb_close': self.close_dialog,
            'pb_insert': self.tb_insert,
            'pb_update': self.tb_update,
            'pb_delete': self.tb_delete,
            'pb_export': self.export_table            
        }
        for button_name, method in button_methods.items():
            button = getattr(self, button_name)
            button.clicked.connect(method)

    def conn_signal_to_slot(self):
        self.tv_pcode.clicked.connect(self.show_selected_data)

    def set_tab_order(self):    # Tab order for sub window
        widgets = [self.pb_show, self.entry_pcode, self.entry_pname, 
            self.pb_search, self.pb_clear, self.pb_close, 
            self.pb_insert, self.pb_update, self.pb_delete]

        for i in range(len(widgets) - 1):
            self.setTabOrder(widgets[i], widgets[i + 1])

    def load_data(self):
        try:
            query = "SELECT * FROM product ORDER BY id"
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
        self.tv_pcode.setModel(self.model)
        vertical_scrollbar = self.tv_pcode.verticalScrollBar()
        vertical_scrollbar.setValue(vertical_scrollbar.maximum())

    def get_customer_input(self):   # Get the value of other variables
        pcode = str(self.entry_pcode.text())
        pname = str(self.entry_pname.text())
        return pcode, pname

    def tb_insert(self):    # insert new product data to MySQL table
        pass

    def tb_update(self):    # revise the values in the selected row
        pass

    def tb_delete(self):    # delete row according to id selected
        pass

    def search_data(self):  # Search data
        pname = self.entry_pname.text()
        if not pname:
            QMessageBox.about(self, "검색 조건 확인", "검색 조건이 비어 있습니다!")
            return
        
        filtered_df = self.df[self.df['pname'].str.contains(pname, case=False)]
        self.model = PandasModel(filtered_df)
        self.tv_pcode.setModel(self.model)
        QMessageBox.about(self, "검색 조건 확인", f"제품명: {pname} \n\n위 조건으로 검색을 수행합니다!")

    def clear_data(self):   # clear input field entry
        self.lbl_id.setText("")
        clear_widget_data(self)

    def show_selected_data(self, index):  # table widget cell click
        row = index.row()
        widgets = [self.lbl_id, self.entry_pcode, self.entry_pname]

        for i, wg in enumerate(widgets):
            value = self.model._data.iloc[row, i]
            if isinstance(wg, QComboBox):
                wg.setCurrentText(str(value))
            else:
                wg.setText(format_number(value))

    # Export data to Excel sheet                
    def export_table(self):
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = CodeMain()
    main_window.show()
    sys.exit(app.exec())    