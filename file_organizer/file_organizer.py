"""
Módulo principal para organizar archivos por extensión.
Permite mover o copiar archivos de una carpeta a otra según su extensión.
"""

import os
import shutil
import hashlib
from pathlib import Path
from typing import List, Tuple, Optional, Dict
import logging


class FileOrganizer:
    """
    Clase para organizar archivos por extensión.
    
    Permite mover o copiar archivos desde una carpeta origen a una carpeta destino
    basándose en las extensiones de archivo especificadas.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Inicializa el organizador de archivos.
        
        Args:
            logger: Logger opcional para registrar operaciones
        """
        self.logger = logger or logging.getLogger(__name__)
        self.files_processed = 0
        self.files_failed = 0
        self.operation_log = []
    
    def scan_files(
        self,
        source_dir: str,
        extensions: List[str],
        recursive: bool = False
    ) -> List[Path]:
        """
        Escanea archivos en el directorio origen que coincidan con las extensiones.
        
        Args:
            source_dir: Directorio de origen
            extensions: Lista de extensiones a buscar (ej: ['.pdf', '.jpg'])
            recursive: Si True, busca recursivamente en subdirectorios
            
        Returns:
            Lista de rutas de archivos encontrados
        """
        source_path = Path(source_dir)
        
        if not source_path.exists():
            raise ValueError(f"El directorio origen no existe: {source_dir}")
        
        if not source_path.is_dir():
            raise ValueError(f"La ruta origen no es un directorio: {source_dir}")
        
        # Normalizar extensiones (asegurar que empiecen con punto)
        normalized_extensions = [
            ext if ext.startswith('.') else f'.{ext}'
            for ext in extensions
        ]
        
        found_files = []
        
        if recursive:
            # Búsqueda recursiva
            for ext in normalized_extensions:
                found_files.extend(source_path.rglob(f'*{ext}'))
        else:
            # Búsqueda solo en el directorio actual
            for ext in normalized_extensions:
                found_files.extend(source_path.glob(f'*{ext}'))
        
        # Filtrar solo archivos (no directorios)
        found_files = [f for f in found_files if f.is_file()]
        
        self.logger.info(f"Encontrados {len(found_files)} archivos con extensiones {normalized_extensions}")
        return found_files
    
    def _calculate_sha512(self, file_path: Path) -> str:
        """
        Calcula el hash SHA-512 de un archivo.
        
        Args:
            file_path: Ruta del archivo
            
        Returns:
            Hash SHA-512 en formato hexadecimal
        """
        sha512_hash = hashlib.sha512()
        try:
            with open(file_path, "rb") as f:
                # Leer en bloques para no saturar la memoria
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha512_hash.update(byte_block)
            return sha512_hash.hexdigest()
        except Exception as e:
            self.logger.error(f"Error calculando hash para {file_path}: {e}")
            return ""

    def _get_unique_filename(self, dest_path: Path) -> Path:
        """
        Genera un nombre de archivo único si ya existe en el destino.
        
        Args:
            dest_path: Ruta de destino del archivo
            
        Returns:
            Ruta única para el archivo
        """
        if not dest_path.exists():
            return dest_path
        
        # Separar nombre y extensión
        stem = dest_path.stem
        suffix = dest_path.suffix
        parent = dest_path.parent
        
        counter = 1
        while True:
            new_name = f"{stem}_{counter}{suffix}"
            new_path = parent / new_name
            if not new_path.exists():
                return new_path
            counter += 1
    
    def organize_files(
        self,
        source_dir: str,
        dest_dir: str,
        extensions: List[str],
        copy_mode: bool = False,
        recursive: bool = False,
        create_dest: bool = True,
        check_hash: bool = False,
        progress_callback: Optional[callable] = None
    ) -> Tuple[int, int, List[str]]:
        """
        Organiza archivos moviéndolos o copiándolos al directorio destino.
        
        Args:
            source_dir: Directorio de origen
            dest_dir: Directorio de destino
            extensions: Lista de extensiones a procesar
            copy_mode: Si True, copia en lugar de mover
            recursive: Si True, busca recursivamente
            create_dest: Si True, crea el directorio destino si no existe
            check_hash: Si True, evita procesar archivos con el mismo hash SHA-512 que ya existan en el destino
            progress_callback: Función callback para reportar progreso (recibe: current, total, filename)
            
        Returns:
            Tupla (archivos_procesados, archivos_fallidos, log_operaciones)
        """
        # Resetear contadores
        self.files_processed = 0
        self.files_failed = 0
        self.operation_log = []
        
        # Validar directorio destino
        dest_path = Path(dest_dir)
        
        if not dest_path.exists():
            if create_dest:
                dest_path.mkdir(parents=True, exist_ok=True)
                self.logger.info(f"Directorio destino creado: {dest_dir}")
                self.operation_log.append(f"✓ Directorio destino creado: {dest_dir}")
            else:
                raise ValueError(f"El directorio destino no existe: {dest_dir}")
        
        # Escanear archivos
        files_to_process = self.scan_files(source_dir, extensions, recursive)
        total_files = len(files_to_process)
        
        # Mapeo de hashes en destino si está activado
        dest_hashes = set()
        if check_hash:
            self.logger.info("Escaneando hashes en el directorio destino...")
            self.operation_log.append("🔍 Escaneando hashes en el directorio destino...")
            for f in dest_path.rglob('*'):
                if f.is_file():
                    h = self._calculate_sha512(f)
                    if h:
                        dest_hashes.add(h)
        
        if total_files == 0:
            self.logger.warning("No se encontraron archivos para procesar")
            self.operation_log.append("⚠ No se encontraron archivos para procesar")
            return 0, 0, self.operation_log
        
        # Procesar cada archivo
        operation = "Copiando" if copy_mode else "Moviendo"
        
        for idx, file_path in enumerate(files_to_process, 1):
            try:
                # Comprobar hash si está activado
                if check_hash:
                    file_hash = self._calculate_sha512(file_path)
                    if file_hash in dest_hashes:
                        log_msg = f"⚠ Omitido: {file_path.name} (ya existe un archivo con el mismo contenido en el destino)"
                        self.logger.info(log_msg)
                        self.operation_log.append(log_msg)
                        if progress_callback:
                            progress_callback(idx, total_files, file_path.name)
                        continue
                    # Si no está en el conjunto, lo añadiremos después de procesarlo con éxito
                
                # Determinar ruta de destino
                dest_file = dest_path / file_path.name
                
                # Manejar conflictos de nombres
                if dest_file.exists():
                    dest_file = self._get_unique_filename(dest_file)
                    self.logger.info(f"Archivo renombrado para evitar conflicto: {dest_file.name}")
                
                # Copiar o mover
                if copy_mode:
                    shutil.copy2(file_path, dest_file)
                else:
                    shutil.move(str(file_path), str(dest_file))
                
                self.files_processed += 1
                log_msg = f"✓ {operation} {file_path.name} → {dest_file.name}"
                self.logger.info(log_msg)
                self.operation_log.append(log_msg)
                
                # Si el procesamiento fue exitoso y el check de hash está activo, añadirlo al set
                if check_hash and 'file_hash' in locals():
                    dest_hashes.add(file_hash)
                
                # Callback de progreso
                if progress_callback:
                    progress_callback(idx, total_files, file_path.name)
                    
            except Exception as e:
                self.files_failed += 1
                error_msg = f"✗ Error procesando {file_path.name}: {str(e)}"
                self.logger.error(error_msg)
                self.operation_log.append(error_msg)
        
        # Resumen final
        summary = f"\n{'='*50}\nResumen: {self.files_processed} exitosos, {self.files_failed} fallidos"
        self.logger.info(summary)
        self.operation_log.append(summary)
        
        return self.files_processed, self.files_failed, self.operation_log
    
    def preview_files(
        self,
        source_dir: str,
        extensions: List[str],
        recursive: bool = False
    ) -> List[Tuple[str, int]]:
        """
        Obtiene una vista previa de los archivos que serían procesados.
        
        Args:
            source_dir: Directorio de origen
            extensions: Lista de extensiones
            recursive: Si True, busca recursivamente
            
        Returns:
            Lista de tuplas (nombre_archivo, tamaño_bytes)
        """
        files = self.scan_files(source_dir, extensions, recursive)
        return [(f.name, f.stat().st_size) for f in files]
