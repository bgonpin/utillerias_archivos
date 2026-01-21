import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QComboBox,
    QFileDialog, QGroupBox, QFormLayout, QMessageBox
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont, QColor, QPalette
from .logic import MongoClonerLogic

class Worker(QThread):
    finished = Signal(int)
    log_signal = Signal(str)

    def __init__(self, mode, params):
        super().__init__()
        self.mode = mode
        self.params = params
        self.logic = MongoClonerLogic(self.log_signal.emit)

    def run(self):
        if self.mode == "Direct":
            result = self.logic.direct_clone(
                self.params['src_uri'], self.params['src_db'],
                self.params['dst_uri'], self.params['dst_db']
            )
        elif self.mode == "Dump":
            result = self.logic.dump_to_file(
                self.params['src_uri'], self.params['src_db'],
                self.params['path']
            )
        elif self.mode == "Restore":
            result = self.logic.restore_from_file(
                self.params['dst_uri'], self.params['dst_db'],
                self.params['path']
            )
        self.finished.emit(result)

class MongoClonerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MongoDB cloner - Professional Suite")
        self.setMinimumSize(800, 600)
        self.setup_ui()
        self.apply_dark_theme()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Title
        title_label = QLabel("MongoDB cloner")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        main_layout.addWidget(title_label)

        # Source Configuration
        source_group = QGroupBox("Source Server")
        source_form = QFormLayout()
        self.src_uri = QLineEdit("mongodb://localhost:27017")
        self.src_db = QLineEdit("source_db")
        source_form.addRow("Connection URI:", self.src_uri)
        source_form.addRow("Database Name:", self.src_db)
        source_group.setLayout(source_form)
        main_layout.addWidget(source_group)

        # Destination Configuration
        dest_group = QGroupBox("Destination Server")
        dest_form = QFormLayout()
        self.dst_uri = QLineEdit("mongodb://localhost:27017")
        self.dst_db = QLineEdit("dest_db")
        dest_form.addRow("Connection URI:", self.dst_uri)
        dest_form.addRow("Database Name:", self.dst_db)
        dest_group.setLayout(dest_form)
        main_layout.addWidget(dest_group)

        # Mode and Path
        options_layout = QHBoxLayout()
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Direct (Server to Server)", "Dump to File", "Restore from File"])
        self.mode_combo.currentIndexChanged.connect(self.on_mode_changed)
        options_layout.addWidget(QLabel("Operation Mode:"))
        options_layout.addWidget(self.mode_combo)

        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("Select folder for dump/restore...")
        self.path_edit.setEnabled(False)
        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.setEnabled(False)
        self.browse_btn.clicked.connect(self.browse_path)
        options_layout.addWidget(self.path_edit)
        options_layout.addWidget(self.browse_btn)
        main_layout.addLayout(options_layout)

        # Controls
        controls_layout = QHBoxLayout()
        self.run_btn = QPushButton("Start Operation")
        self.run_btn.setFixedHeight(40)
        self.run_btn.clicked.connect(self.start_operation)
        controls_layout.addWidget(self.run_btn)
        main_layout.addLayout(controls_layout)

        # Log Terminal
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setFont(QFont("Consolas", 10))
        main_layout.addWidget(self.log_output)

    def apply_dark_theme(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QLabel {
                color: #e0e0e0;
                font-family: 'Segoe UI', Arial;
            }
            QGroupBox {
                color: #3d9dfa;
                font-weight: bold;
                border: 1px solid #333;
                margin-top: 1.5em;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
            QLineEdit, QComboBox, QTextEdit {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                color: #ffffff;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton {
                background-color: #3d9dfa;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5aa9fb;
            }
            QPushButton:pressed {
                background-color: #2a7acc;
            }
            QPushButton:disabled {
                background-color: #444;
                color: #888;
            }
        """)

    def on_mode_changed(self, index):
        is_direct = index == 0
        self.path_edit.setEnabled(not is_direct)
        self.browse_btn.setEnabled(not is_direct)
        
        # Update destination fields based on mode
        is_dump = index == 1
        self.dst_uri.setEnabled(not is_dump)
        self.dst_db.setEnabled(not is_dump)
        
        is_restore = index == 2
        self.src_uri.setEnabled(not is_restore)
        self.src_db.setEnabled(not is_restore)

    def browse_path(self):
        path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if path:
            self.path_edit.setText(path)

    def start_operation(self):
        mode_text = self.mode_combo.currentText()
        params = {
            'src_uri': self.src_uri.text(),
            'src_db': self.src_db.text(),
            'dst_uri': self.dst_uri.text(),
            'dst_db': self.dst_db.text(),
            'path': self.path_edit.text()
        }

        # Validate inputs
        if "Direct" in mode_text:
            mode = "Direct"
        elif "Dump" in mode_text:
            mode = "Dump"
            if not params['path']:
                QMessageBox.warning(self, "Error", "Please select a path for the dump.")
                return
        else:
            mode = "Restore"
            if not params['path']:
                QMessageBox.warning(self, "Error", "Please select a path for the restore.")
                return

        self.log_output.clear()
        self.run_btn.setEnabled(False)
        self.log_output.append(f"Starting {mode} operation...")

        self.worker = Worker(mode, params)
        self.worker.log_signal.connect(self.log_output.append)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()

    def on_finished(self, return_code):
        self.run_btn.setEnabled(True)
        if return_code == 0:
            self.log_output.append("\nOperation completed successfully.")
            QMessageBox.information(self, "Success", "Operation finished successfully.")
        else:
            self.log_output.append(f"\nOperation failed with return code: {return_code}")
            QMessageBox.critical(self, "Error", f"Operation failed (Return code: {return_code})")

def main():
    app = QApplication(sys.argv)
    window = MongoClonerGUI()
    window.show()
    sys.exit(app.exec())
