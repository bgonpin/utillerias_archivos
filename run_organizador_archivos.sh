#!/bin/bash

# Script para ejecutar el Organizador de Archivos con entorno conda
# Comprueba si existe el entorno, lo crea si es necesario, e instala dependencias

ENV_NAME="file_organizer"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🔍 Verificando entorno conda '$ENV_NAME'..."

# Verificar si conda está instalado
if ! command -v conda &> /dev/null; then
    echo "❌ Error: conda no está instalado o no está en el PATH"
    echo "Por favor instala Anaconda o Miniconda primero"
    exit 1
fi

# Inicializar conda para el script
eval "$(conda shell.bash hook)"

# Verificar si el entorno existe
if conda env list | grep -q "^${ENV_NAME} "; then
    echo "✅ Entorno '$ENV_NAME' encontrado"
else
    echo "📦 Creando entorno conda '$ENV_NAME'..."
    conda create -n "$ENV_NAME" python=3.10 -y
    
    if [ $? -ne 0 ]; then
        echo "❌ Error al crear el entorno conda"
        exit 1
    fi
    
    echo "✅ Entorno creado exitosamente"
fi

# Activar el entorno
echo "🔄 Activando entorno '$ENV_NAME'..."
conda activate "$ENV_NAME"

if [ $? -ne 0 ]; then
    echo "❌ Error al activar el entorno"
    exit 1
fi

# Verificar si las dependencias están instaladas
echo "📋 Verificando dependencias..."

if ! python -c "import PySide6" &> /dev/null; then
    echo "📥 Instalando dependencias desde requirements.txt..."
    pip install -r "$SCRIPT_DIR/requirements.txt"
    
    if [ $? -ne 0 ]; then
        echo "❌ Error al instalar dependencias"
        exit 1
    fi
    
    echo "✅ Dependencias instaladas correctamente"
else
    echo "✅ Dependencias ya instaladas"
fi

# Ejecutar la aplicación
echo ""
echo "🚀 Ejecutando Organizador de Archivos..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cd "$SCRIPT_DIR"
python main_organizador_archivos.py

# Capturar el código de salida
EXIT_CODE=$?

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Aplicación finalizada correctamente"
else
    echo "⚠️  Aplicación finalizada con código: $EXIT_CODE"
fi

exit $EXIT_CODE
