import os
from docx2pdf import convert
import sys

def convertir_un_archivo(ruta_docx, ruta_pdf=None):
    """
    Convierte un solo archivo .docx a .pdf
    """
    try:
        if not os.path.exists(ruta_docx):
            print(f"❌ Error: El archivo {ruta_docx} no existe.")
            return

        print(f"🔄 Convirtiendo '{ruta_docx}' a PDF...")
        # Si no se especifica ruta de salida, se guarda en el mismo lugar con extensión .pdf
        convert(ruta_docx, ruta_pdf)
        print(f"✅ ¡Listo! Archivo convertido exitosamente.")

    except Exception as e:
        print(f"❌ Ocurrió un error al convertir {ruta_docx}: {e}")

def convertir_carpeta(ruta_carpeta):
    """
    Busca todos los archivos .docx en una carpeta y los convierte a PDF
    """
    try:
        if not os.path.isdir(ruta_carpeta):
            print(f"❌ Error: La carpeta {ruta_carpeta} no existe.")
            return

        print(f"📂 Procesando carpeta: {ruta_carpeta}...")
        # La librería docx2pdf puede convertir una carpeta entera automáticamente
        convert(ruta_carpeta)
        print("✅ ¡Conversión por lotes terminada!")

    except Exception as e:
        print(f"❌ Ocurrió un error procesando la carpeta: {e}")

if __name__ == "__main__":
    # --- EJEMPLOS DE USO ---
    # Puedes descomentar las líneas de abajo para probarlo,
    # o adaptar las rutas a tus necesidades.

    # Opción 1: Convertir un archivo específico
    # ruta_doc = "C:\\Usuarios\\TuUsuario\\Documentos\\mi_contrato.docx"
    # convertir_un_archivo(ruta_doc)

    # Opción 2: Convertir una carpeta entera
    # ruta_dir = "C:\\Usuarios\\TuUsuario\\Documentos\\Reportes"
    # convertir_carpeta(ruta_dir)

    print("ℹ️ Para usar el script, edita las rutas en la sección 'if __name__ == \"__main__\":' al final del archivo.")