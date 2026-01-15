# 📁 Organizador de Archivos por Extensión

Aplicación de escritorio con interfaz gráfica para organizar archivos según su extensión, permitiendo mover o copiar archivos de una carpeta a otra de forma rápida y segura.

## ✨ Características

- **Interfaz Gráfica Moderna**: Diseño intuitivo y fácil de usar con PySide6
- **Vista Previa**: Visualiza los archivos que serán procesados antes de ejecutar la operación
- **Múltiples Extensiones**: Procesa múltiples tipos de archivo simultáneamente
- **Modo Recursivo**: Opción para buscar archivos en subdirectorios
- **Copiar o Mover**: Elige entre copiar o mover los archivos
- **Resolución de Conflictos**: Renombra automáticamente archivos duplicados
- **Barra de Progreso**: Seguimiento en tiempo real de la operación
- **Registro Detallado**: Panel de logs mostrando cada operación realizada
- **Seguridad**: Confirmación antes de ejecutar operaciones

## 📋 Requisitos

- Python 3.8 o superior
- PySide6

## 🚀 Instalación

### Opción 1: Con Conda (Recomendado)

Si tienes Anaconda o Miniconda instalado, simplemente ejecuta:

```bash
./run.sh
```

El script automáticamente:
- Verifica si existe el entorno conda `file_organizer`
- Lo crea si no existe (con Python 3.10)
- Instala las dependencias desde `requirements.txt`
- Activa el entorno
- Ejecuta la aplicación

### Opción 2: Instalación Manual

1. **Clonar o descargar el proyecto**

2. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

   O instalar PySide6 directamente:
   ```bash
   pip install PySide6
   ```

## 💻 Uso

### Ejecutar la Aplicación

```bash
python main.py
```

O hacerlo ejecutable (Linux/Mac):
```bash
chmod +x main.py
./main.py
```

### Guía de Uso

1. **Seleccionar Carpeta Origen**: Haz clic en "📂 Explorar" junto a "Carpeta Origen" y selecciona la carpeta que contiene los archivos a organizar.

2. **Seleccionar Carpeta Destino**: Haz clic en "📂 Explorar" junto a "Carpeta Destino" y selecciona donde quieres mover/copiar los archivos.

3. **Especificar Extensiones**: En el campo "Extensiones", escribe las extensiones de archivo separadas por comas.
   - Ejemplo: `.pdf, .jpg, .png, .txt`
   - También funciona sin el punto: `pdf, jpg, png`

4. **Configurar Opciones**:
   - ✅ **Copiar**: Copia los archivos en lugar de moverlos
   - ✅ **Buscar en subdirectorios**: Busca archivos recursivamente
   - ✅ **Crear carpeta destino**: Crea la carpeta destino si no existe

5. **Vista Previa**: Haz clic en "👁 Vista Previa" para ver qué archivos serán procesados.

6. **Ejecutar**: Haz clic en "▶ Ejecutar" para iniciar la operación.

7. **Limpiar**: Usa "🗑 Limpiar" para resetear todos los campos.

## 📝 Ejemplos de Uso

### Ejemplo 1: Organizar Fotos
- **Origen**: `/home/usuario/Descargas`
- **Destino**: `/home/usuario/Imágenes`
- **Extensiones**: `.jpg, .jpeg, .png, .gif`
- **Opciones**: Copiar ✓, Recursivo ✓

### Ejemplo 2: Mover Documentos PDF
- **Origen**: `/home/usuario/Documentos/temp`
- **Destino**: `/home/usuario/Documentos/PDFs`
- **Extensiones**: `.pdf`
- **Opciones**: Mover (sin marcar "Copiar")

### Ejemplo 3: Organizar Múltiples Tipos
- **Origen**: `/home/usuario/Descargas`
- **Destino**: `/home/usuario/Archivos`
- **Extensiones**: `.pdf, .docx, .xlsx, .txt`
- **Opciones**: Mover, Recursivo ✓

## 🏗️ Estructura del Proyecto

```
utillerias_archivos/
├── file_organizer/          # Módulo principal
│   ├── __init__.py         # Inicialización del paquete
│   └── file_organizer.py   # Lógica de organización de archivos
├── gui.py                   # Interfaz gráfica PySide6
├── main.py                  # Script de entrada
├── requirements.txt         # Dependencias
└── README.md               # Este archivo
```

## 🔧 Características Técnicas

### Módulo `FileOrganizer`

El módulo principal proporciona:

- **`scan_files()`**: Escanea archivos por extensión
- **`organize_files()`**: Mueve o copia archivos con callback de progreso
- **`preview_files()`**: Obtiene lista de archivos sin procesarlos
- **Manejo de conflictos**: Renombrado automático de archivos duplicados
- **Logging**: Registro detallado de todas las operaciones

### Interfaz Gráfica

- **Threading**: Operaciones de archivo en thread separado para no bloquear la UI
- **Validación**: Validación de entradas antes de ejecutar
- **Feedback visual**: Barra de progreso y logs en tiempo real
- **Diseño responsive**: Interfaz adaptable y moderna

## ⚠️ Notas Importantes

1. **Permisos**: Asegúrate de tener permisos de lectura en la carpeta origen y de escritura en la carpeta destino.

2. **Archivos Duplicados**: Si un archivo con el mismo nombre ya existe en el destino, se renombrará automáticamente añadiendo un número (ej: `archivo_1.pdf`).

3. **Operaciones Irreversibles**: El modo "Mover" elimina los archivos del origen. Usa "Copiar" si quieres mantener los originales.

4. **Vista Previa**: Siempre usa la vista previa antes de ejecutar para verificar qué archivos serán procesados.

## 🐛 Solución de Problemas

### Error: "El directorio origen no existe"
- Verifica que la ruta de la carpeta origen sea correcta y exista.

### Error: "No se encontraron archivos"
- Verifica que las extensiones estén escritas correctamente.
- Si usas modo no recursivo, asegúrate de que los archivos estén en la carpeta raíz.

### Error de permisos
- Verifica que tengas permisos de lectura/escritura en las carpetas.
- En Linux/Mac, puede que necesites ejecutar con permisos elevados.

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.

## 👤 Autor

Creado por **Nito**

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Si encuentras algún bug o tienes sugerencias de mejora, no dudes en abrir un *issue* o enviar un *pull request*.

---

**¡Disfruta organizando tus archivos! 📂✨**
