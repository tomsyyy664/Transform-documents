from PIL import Image
import os

def convert_image_file(input_path, target_format):
    """
    Función principal que usa tanto la terminal como la interfaz.
    Retorna True si se convirtió, False si ya estaba en ese formato.
    Lanza excepciones si hay error.
    """
    target_format = target_format.lower().replace('.', '')
    
    with Image.open(input_path) as img:
        root, current_ext = os.path.splitext(input_path)
        
        # Si ya está en el formato deseado, no hacemos nada
        if current_ext.lower().replace('.', '') == target_format:
            return False

        output_path = f"{root}.{target_format}"

        # Convertir transparencia si pasamos a JPG
        if target_format in ['jpg', 'jpeg'] and img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')

        img.save(output_path, quality=95)
        return True

# --- SOLO SE EJECUTA SI USAS ESTE ARCHIVO DIRECTAMENTE ---
if __name__ == "__main__":
    print("--- MODO TERMINAL ---")
    path = input("Ruta de la imagen: ").strip('"').strip("'")
    if os.path.exists(path):
        fmt = input("Formato (jpg/png): ")
        try:
            if convert_image_file(path, fmt):
                print(f"[OK] Convertido correctamente.")
            else:
                print("[INFO] La imagen ya estaba en ese formato.")
        except Exception as e:
            print(f"[ERROR] {e}")
    else:
        input("Archivo no encontrado. Presiona Enter para salir.")