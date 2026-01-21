"""
Interfaz gráfica para el organizador de archivos.
Permite seleccionar carpetas, configurar opciones y organizar archivos por extensión.
"""

import sys
from pathlib import Path
from typing import List
import logging

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QCheckBox, QTextEdit, QTableWidget,
    QTableWidgetItem, QFileDialog, QMessageBox, QProgressBar, QGroupBox,
    QHeaderView
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont, QColor

from file_organizer import FileOrganizer


class WorkerThread(QThread):
    """Thread worker para ejecutar operaciones de archivo sin bloquear la GUI."""
    
    progress = Signal(int, int, str)  # current, total, filename
    finished = Signal(int, int, list)  # processed, failed, log
    error = Signal(str)
    
    def __init__(self, organizer, source, dest, extensions, copy_mode, recursive, create_dest, check_hash):
        super().__init__()
        self.organizer = organizer
        self.source = source
        self.dest = dest
        self.extensions = extensions
        self.copy_mode = copy_mode
        self.recursive = recursive
        self.create_dest = create_dest
        self.check_hash = check_hash
    
    def run(self):
        """Ejecuta la operación de organización de archivos."""
        try:
            processed, failed, log = self.organizer.organize_files(
                self.source,
                self.dest,
                self.extensions,
                self.copy_mode,
                self.recursive,
                self.create_dest,
                check_hash=self.check_hash,
                progress_callback=lambda c, t, f: self.progress.emit(c, t, f)
            )
            self.finished.emit(processed, failed, log)
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    """Ventana principal de la aplicación."""
    
    def __init__(self):
        super().__init__()
        self.organizer = FileOrganizer()
        self.worker = None
        self.init_ui()
        self.setup_logging()
    
    def setup_logging(self):
        """Configura el sistema de logging."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    def init_ui(self):
        """Inicializa la interfaz de usuario."""
        self.setWindowTitle("Organizador de Archivos por Extensión")
        self.setMinimumSize(900, 700)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Título
        title = QLabel("📁 Organizador de Archivos")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # Grupo de selección de carpetas
        folder_group = QGroupBox("Configuración de Carpetas")
        folder_layout = QVBoxLayout()
        
        # Carpeta origen
        source_layout = QHBoxLayout()
        source_layout.addWidget(QLabel("Carpeta Origen:"))
        self.source_input = QLineEdit()
        self.source_input.setPlaceholderText("Selecciona la carpeta de origen...")
        source_layout.addWidget(self.source_input)
        self.source_btn = QPushButton("📂 Explorar")
        self.source_btn.clicked.connect(self.select_source_folder)
        source_layout.addWidget(self.source_btn)
        folder_layout.addLayout(source_layout)
        
        # Carpeta destino
        dest_layout = QHBoxLayout()
        dest_layout.addWidget(QLabel("Carpeta Destino:"))
        self.dest_input = QLineEdit()
        self.dest_input.setPlaceholderText("Selecciona la carpeta de destino...")
        dest_layout.addWidget(self.dest_input)
        self.dest_btn = QPushButton("📂 Explorar")
        self.dest_btn.clicked.connect(self.select_dest_folder)
        dest_layout.addWidget(self.dest_btn)
        folder_layout.addLayout(dest_layout)
        
        folder_group.setLayout(folder_layout)
        main_layout.addWidget(folder_group)
        
        # Grupo de extensiones
        ext_group = QGroupBox("Extensiones de Archivo")
        ext_layout = QVBoxLayout()
        
        ext_input_layout = QHBoxLayout()
        ext_input_layout.addWidget(QLabel("Extensiones:"))
        self.ext_input = QLineEdit()
        self.ext_input.setPlaceholderText("Ej: .pdf, .jpg, .png, .txt (separadas por comas)")
        ext_input_layout.addWidget(self.ext_input)
        ext_layout.addLayout(ext_input_layout)
        
        ext_group.setLayout(ext_layout)
        main_layout.addWidget(ext_group)
        
        # Grupo de opciones
        options_group = QGroupBox("Opciones")
        options_layout = QHBoxLayout()
        
        self.copy_checkbox = QCheckBox("Copiar (en lugar de mover)")
        self.recursive_checkbox = QCheckBox("Buscar en subdirectorios (recursivo)")
        self.create_dest_checkbox = QCheckBox("Crear carpeta destino si no existe")
        self.create_dest_checkbox.setChecked(True)
        self.hash_checkbox = QCheckBox("Evitar duplicados (SHA-512)")
        
        options_layout.addWidget(self.copy_checkbox)
        options_layout.addWidget(self.recursive_checkbox)
        options_layout.addWidget(self.create_dest_checkbox)
        options_layout.addWidget(self.hash_checkbox)
        options_layout.addStretch()
        
        options_group.setLayout(options_layout)
        main_layout.addWidget(options_group)
        
        # Botones de acción
        action_layout = QHBoxLayout()
        
        self.preview_btn = QPushButton("👁 Vista Previa")
        self.preview_btn.clicked.connect(self.show_preview)
        self.preview_btn.setStyleSheet("""
            QPushButton {
                background-color: #0d7377;
                color: #e8e8e8;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                border: 1px solid #14a085;
            }
            QPushButton:hover {
                background-color: #14a085;
            }
        """)
        
        self.execute_btn = QPushButton("▶ Ejecutar")
        self.execute_btn.clicked.connect(self.execute_operation)
        self.execute_btn.setStyleSheet("""
            QPushButton {
                background-color: #2e7d32;
                color: #e8e8e8;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                border: 1px solid #388e3c;
            }
            QPushButton:hover {
                background-color: #388e3c;
            }
        """)
        
        self.clear_btn = QPushButton("🗑 Limpiar")
        self.clear_btn.clicked.connect(self.clear_all)
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #c62828;
                color: #e8e8e8;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                border: 1px solid #d32f2f;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        
        action_layout.addWidget(self.preview_btn)
        action_layout.addWidget(self.execute_btn)
        action_layout.addWidget(self.clear_btn)
        action_layout.addStretch()
        
        main_layout.addLayout(action_layout)
        
        # Tabla de vista previa
        preview_label = QLabel("Vista Previa de Archivos:")
        preview_label.setFont(QFont("", 10, QFont.Bold))
        main_layout.addWidget(preview_label)
        
        self.preview_table = QTableWidget()
        self.preview_table.setColumnCount(2)
        self.preview_table.setHorizontalHeaderLabels(["Nombre del Archivo", "Tamaño"])
        self.preview_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.preview_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.preview_table.setAlternatingRowColors(True)
        main_layout.addWidget(self.preview_table)
        
        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # Panel de logs
        log_label = QLabel("Registro de Operaciones:")
        log_label.setFont(QFont("", 10, QFont.Bold))
        main_layout.addWidget(log_label)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #3e3e42;
                border-radius: 5px;
                font-family: 'Courier New', monospace;
                font-size: 9pt;
            }
        """)
        main_layout.addWidget(self.log_text)
        
        # Aplicar estilo general
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2d2d30;
            }
            QWidget {
                background-color: #2d2d30;
                color: #e8e8e8;
            }
            QLabel {
                color: #e8e8e8;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3e3e42;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: #252526;
                color: #e8e8e8;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #e8e8e8;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #3e3e42;
                border-radius: 4px;
                background-color: #1e1e1e;
                color: #e8e8e8;
            }
            QLineEdit:focus {
                border: 2px solid #0d7377;
            }
            QCheckBox {
                color: #e8e8e8;
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 3px;
                border: 1px solid #3e3e42;
                background-color: #1e1e1e;
            }
            QCheckBox::indicator:checked {
                background-color: #0d7377;
                border: 1px solid #14a085;
            }
            QTableWidget {
                background-color: #1e1e1e;
                alternate-background-color: #252526;
                color: #e8e8e8;
                gridline-color: #3e3e42;
                border: 1px solid #3e3e42;
                border-radius: 5px;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #0d7377;
            }
            QHeaderView::section {
                background-color: #252526;
                color: #e8e8e8;
                padding: 8px;
                border: 1px solid #3e3e42;
                font-weight: bold;
            }
            QProgressBar {
                border: 1px solid #3e3e42;
                border-radius: 5px;
                text-align: center;
                background-color: #1e1e1e;
                color: #e8e8e8;
            }
            QProgressBar::chunk {
                background-color: #0d7377;
                border-radius: 4px;
            }
            QPushButton {
                background-color: #3e3e42;
                color: #e8e8e8;
                border: 1px solid #555555;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #505050;
            }
            QPushButton:pressed {
                background-color: #2d2d30;
            }
        """)
    
    def select_source_folder(self):
        """Abre diálogo para seleccionar carpeta origen."""
        folder = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta Origen")
        if folder:
            self.source_input.setText(folder)
    
    def select_dest_folder(self):
        """Abre diálogo para seleccionar carpeta destino."""
        folder = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta Destino")
        if folder:
            self.dest_input.setText(folder)
    
    def get_extensions(self) -> List[str]:
        """Obtiene y procesa las extensiones del campo de texto."""
        ext_text = self.ext_input.text().strip()
        if not ext_text:
            return []
        
        # Separar por comas y limpiar espacios
        extensions = [ext.strip() for ext in ext_text.split(',')]
        return [ext for ext in extensions if ext]
    
    def validate_inputs(self) -> bool:
        """Valida que todos los campos requeridos estén completos."""
        if not self.source_input.text().strip():
            QMessageBox.warning(self, "Error", "Por favor selecciona una carpeta origen.")
            return False
        
        if not self.dest_input.text().strip():
            QMessageBox.warning(self, "Error", "Por favor selecciona una carpeta destino.")
            return False
        
        if not self.get_extensions():
            QMessageBox.warning(self, "Error", "Por favor especifica al menos una extensión.")
            return False
        
        return True
    
    def show_preview(self):
        """Muestra vista previa de los archivos que serán procesados."""
        if not self.validate_inputs():
            return
        
        try:
            source = self.source_input.text()
            extensions = self.get_extensions()
            recursive = self.recursive_checkbox.isChecked()
            
            # Obtener vista previa
            files = self.organizer.preview_files(source, extensions, recursive)
            
            # Actualizar tabla
            self.preview_table.setRowCount(len(files))
            
            for row, (filename, size) in enumerate(files):
                # Nombre del archivo
                name_item = QTableWidgetItem(filename)
                self.preview_table.setItem(row, 0, name_item)
                
                # Tamaño formateado
                size_str = self.format_size(size)
                size_item = QTableWidgetItem(size_str)
                size_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.preview_table.setItem(row, 1, size_item)
            
            # Log
            self.log_text.append(f"✓ Vista previa: {len(files)} archivos encontrados")
            
            if len(files) == 0:
                QMessageBox.information(
                    self,
                    "Vista Previa",
                    "No se encontraron archivos con las extensiones especificadas."
                )
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al generar vista previa:\n{str(e)}")
            self.log_text.append(f"✗ Error en vista previa: {str(e)}")
    
    def format_size(self, size_bytes: int) -> str:
        """Formatea el tamaño de archivo en unidades legibles."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def execute_operation(self):
        """Ejecuta la operación de organización de archivos."""
        if not self.validate_inputs():
            return
        
        # Confirmación
        operation = "copiar" if self.copy_checkbox.isChecked() else "mover"
        reply = QMessageBox.question(
            self,
            "Confirmar Operación",
            f"¿Estás seguro de que deseas {operation} los archivos?\n\n"
            f"Esta operación puede modificar tus archivos.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.No:
            return
        
        # Deshabilitar botones durante la operación
        self.set_buttons_enabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Crear y configurar worker thread
        self.worker = WorkerThread(
            self.organizer,
            self.source_input.text(),
            self.dest_input.text(),
            self.get_extensions(),
            self.copy_checkbox.isChecked(),
            self.recursive_checkbox.isChecked(),
            self.create_dest_checkbox.isChecked(),
            self.hash_checkbox.isChecked()
        )
        
        # Conectar señales
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.operation_finished)
        self.worker.error.connect(self.operation_error)
        
        # Iniciar operación
        self.log_text.append(f"\n{'='*50}")
        self.log_text.append(f"Iniciando operación de {operation}...")
        self.worker.start()
    
    def update_progress(self, current: int, total: int, filename: str):
        """Actualiza la barra de progreso."""
        progress = int((current / total) * 100)
        self.progress_bar.setValue(progress)
        self.log_text.append(f"[{current}/{total}] Procesando: {filename}")
    
    def operation_finished(self, processed: int, failed: int, log: List[str]):
        """Maneja la finalización de la operación."""
        self.progress_bar.setVisible(False)
        self.set_buttons_enabled(True)
        
        # Mostrar logs
        for entry in log:
            self.log_text.append(entry)
        
        # Mensaje de resumen
        if failed == 0:
            QMessageBox.information(
                self,
                "Operación Completada",
                f"✓ Operación completada exitosamente!\n\n"
                f"Archivos procesados: {processed}"
            )
        else:
            QMessageBox.warning(
                self,
                "Operación Completada con Errores",
                f"Operación completada con algunos errores.\n\n"
                f"Exitosos: {processed}\n"
                f"Fallidos: {failed}\n\n"
                f"Revisa el registro para más detalles."
            )
    
    def operation_error(self, error_msg: str):
        """Maneja errores durante la operación."""
        self.progress_bar.setVisible(False)
        self.set_buttons_enabled(True)
        
        QMessageBox.critical(self, "Error", f"Error durante la operación:\n{error_msg}")
        self.log_text.append(f"✗ ERROR: {error_msg}")
    
    def set_buttons_enabled(self, enabled: bool):
        """Habilita o deshabilita los botones de acción."""
        self.preview_btn.setEnabled(enabled)
        self.execute_btn.setEnabled(enabled)
        self.source_btn.setEnabled(enabled)
        self.dest_btn.setEnabled(enabled)
    
    def clear_all(self):
        """Limpia todos los campos y la vista previa."""
        self.source_input.clear()
        self.dest_input.clear()
        self.ext_input.clear()
        self.preview_table.setRowCount(0)
        self.log_text.clear()
        self.copy_checkbox.setChecked(False)
        self.recursive_checkbox.setChecked(False)
        self.create_dest_checkbox.setChecked(True)
        self.hash_checkbox.setChecked(False)
        self.log_text.append("✓ Interfaz limpiada")


def main():
    """Función principal para ejecutar la aplicación."""
    app = QApplication(sys.argv)
    
    # Configurar estilo de la aplicación
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
