# This Python file uses the following encoding: utf-8
import os
from pathlib import Path
import sys

from PySide6.QtWidgets import (QApplication, QWidget, QTableWidgetItem, QMainWindow,
                               QPushButton, QLineEdit, QTableWidget, QHeaderView,
                               QStatusBar, QPlainTextEdit)
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QColor
import PySide6

from rule import load_rules, save_rules, Rule
from utils import is_regex_valid, test_regex, single_space
from cli import do_cli

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__()
        self.load_ui()
        # Own code here
        # We load and display the table
        self.table_widget_rules = self.findChild(QTableWidget, "tableWidgetRules")
        for r in load_rules():
            self.add_rule_to_table(r)

        # We get the interesting widgets
        self.test_string_field = self.findChild(QPlainTextEdit, "plainTextEditTestString")
        self.output_field = self.findChild(QLineEdit, "lineEditOutput")
        self.regex_field = self.findChild(QLineEdit, "lineEditRegex")
        self.tags_field = self.findChild(QLineEdit, "lineEditTags")
        self.notes_field = self.findChild(QLineEdit, "lineEditNotes")
        self.button_add_rule = self.findChild(QPushButton, "pushButtonAddRule")

        # We register the slots
        self.button_add_rule.clicked.connect(self.add_rule_from_form)
        self.findChild(QPushButton, "pushButtonSave").clicked.connect(self.save_rules_to_file)
        self.regex_field.textChanged.connect(self.check_regex_field)
        self.tags_field.editingFinished.connect(self.format_tags_field)
        self.test_string_field.textChanged.connect(self.apply_test_string)
        self.table_widget_rules.cellChanged.connect(self.on_cell_changed)

        # We put the table column width
        table_header = self.table_widget_rules.horizontalHeader()
        table_header.setSectionResizeMode(QHeaderView.Stretch)
        table_header.setSectionResizeMode(3, QHeaderView.ResizeToContents)

        # Some setup
        self.check_regex_field()

    def load_ui(self):
        loader = QUiLoader()
        path = os.fspath(Path(__file__).resolve().parent / "form.ui")
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)

        self.window = loader.load(ui_file, None)
        # Otherwise the window is super squished for some reason
        self.resize(self.window.width(), self.window.height())
        self.setCentralWidget(self.window)

        ui_file.close()


    def add_rule_to_table(self, r: Rule):
        # We make a new row
        rowPosition = self.table_widget_rules.rowCount()
        self.table_widget_rules.insertRow(rowPosition)
        # The we fill that row
        self.table_widget_rules.setItem(rowPosition, 0, QTableWidgetItem(r.regex))
        self.table_widget_rules.setItem(rowPosition, 1, QTableWidgetItem(r.tags))
        self.table_widget_rules.setItem(rowPosition, 2, QTableWidgetItem(r.notes))
        # And finally we add the delete button
        delete_button = QPushButton("delete")
        #delete_button.setStyleSheet("color: red")
        delete_button.clicked.connect(self.delete_row)
        self.table_widget_rules.setCellWidget(rowPosition, 3, delete_button)

    def add_rule_from_form(self):
        print("adding new rule")
        new_rule = Rule(regex=self.regex_field.text(),
                        tags=self.tags_field.text(),
                        notes=self.notes_field.text())
        self.add_rule_to_table(new_rule)
        self.find_output()

    def save_rules_to_file(self):
        rules_to_save = []
        # For each rule
        for row_id in range(self.table_widget_rules.rowCount()):
            regex = self.table_widget_rules.item(row_id, 0).text()
            tags = self.table_widget_rules.item(row_id, 1).text()
            notes = self.table_widget_rules.item(row_id, 2).text()
            rules_to_save.append(Rule(
                regex=regex, tags=tags, notes=notes
            ))
        save_rules(rules_to_save)

    def check_regex_field(self):
        reg = self.regex_field.text().strip()
        test_string = self.test_string_field.toPlainText()

        if is_regex_valid(reg):
            # If we didn't even put a test string
            if not test_string:
                self.regex_field.setStyleSheet("")
            elif test_regex(reg, test_string):
                self.regex_field.setStyleSheet("color: green;")
            else:
                self.regex_field.setStyleSheet("color: red")

            # We enable the button if there's text, else we don't
            self.button_add_rule.setEnabled( bool(reg) )
        else:
            self.regex_field.setStyleSheet("background-color: red;")
            self.button_add_rule.setEnabled(False)

    def format_tags_field(self):
        self.tags_field.setText( single_space(self.tags_field.text().strip()) )

    def on_cell_changed(self, row: int, column: int):
        print(self.sender())
        # if the regex was edited
        if column == 0:
            self.apply_test_sring_to_row(row) #  causes recursion error
            self.find_output()
        # if the tags were edited
        elif column == 1:
            item = self.table_widget_rules.item(row, column)
            item.setText( item.text().replace('  ', ' ') )

    def apply_test_sring_to_row(self, row_index: int):
        test_string = self.test_string_field.toPlainText()
        regex_item = self.table_widget_rules.item(row_index, 0)
        regex = regex_item.text()

        self.table_widget_rules.blockSignals(True) #  we block the signal so it doesn't cause infinite recursion

        # We remove existing special colors
        regex_item.setData(PySide6.QtCore.Qt.ItemDataRole.ForegroundRole, None)
        regex_item.setData(PySide6.QtCore.Qt.ItemDataRole.BackgroundRole, None)

        # If there's no text string, we don't put any special colors
        if test_string.strip():
            if is_regex_valid(regex):
                if test_regex(regex, test_string):
                    regex_item.setForeground(QColor("green"))
                else:
                    regex_item.setForeground(QColor("red"))
            else:
                regex_item.setBackground(QColor("red"))

        self.table_widget_rules.blockSignals(False)

    def apply_test_string(self):
        # test_string = self.test_string_field.text()

        # First we update the form regex's color
        self.check_regex_field()

        # Then we test the ones in the table
        for row_id in range(self.table_widget_rules.rowCount()):
            self.apply_test_sring_to_row(row_id)

        # Then finally we get the output
        self.find_output()

    def delete_row(self):
        button = self.sender()
        if button:
            row = self.table_widget_rules.indexAt(button.pos()).row()
            print(f"Removing row {row}")
            self.table_widget_rules.removeRow(row)

    def find_output(self):
        tags = ""
        for row_id in range(self.table_widget_rules.rowCount()):
            # If the regex is green
            if self.table_widget_rules.item(row_id, 0).foreground().color() == QColor("green"):
                # We add the tags
                tags += self.table_widget_rules.item(row_id, 1).text() + ' '
        self.output_field.setText(single_space(' '.join( set(tags.split(' '))) ))

if __name__ == "__main__":
    # Getting input for CLI Mode
    input_string = None
    #if not sys.stdin.isatty():
        # If we got piped stuff
        #input_string = sys.stdin.read()
    if len(sys.argv) != 1:
        # We got passed some args, so CLI mode
        if len(sys.argv) != 2:
            sys.exit('Too many arguments, please pass only one! (make sure to put "quotes" around the input')
        input_string = sys.argv[1]

    # CLI Mode
    if input_string is not None:
        do_cli(input_string.rstrip())

    # GUI Mode
    else:
        app = QApplication([])
        widget = MainWindow()
        widget.setWindowTitle("Tags from text")
        widget.show()
        #sys.exit(app.exec_())
        sys.exit( app.exec() )
