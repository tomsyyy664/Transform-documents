import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image
import os
import sys

# --- LOGICA DEL CONVERSOR ---
def convert_image_file(input_path, target_format):
    target_format = target_format.lower().replace('.', '')
    with Image.open(input_path) as img:
        root_name, current_ext = os.path.splitext(input_path)
        if current_ext.lower().replace('.', '') == target_format:
            return False
        
        output_path = f"{root_name}.{target_format}"
        if target_format in ['jpg', 'jpeg'] and img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
            
        img.save(output_path, quality=95)
        return True

# --- INTERFAZ GRAFICA ---
class ImageConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Transform-documents (Img)")
        self.root.geometry("500x350")
        self.root.resizable(False, False)

        self.selected_files = []
        self.target_format = tk.StringVar(value="jpg")

        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Conversor de Imagenes", font=("Helvetica", 16, "bold")).pack(pady=(0, 20))

        ttk.Button(main_frame, text="Seleccionar Imagenes", command=self.select_images).pack(fill=tk.X, pady=5)
        self.files_label = ttk.Label(main_frame, text="Ningun archivo seleccionado", foreground="gray")
        self.files_label.pack(pady=(0, 20))

        fmt_frame = ttk.LabelFrame(main_frame, text="Formato de Salida", padding="10")
        fmt_frame.pack(fill=tk.X, pady=10)
        ttk.Radiobutton(fmt_frame, text="JPG", variable=self.target_format, value="jpg").pack(side=tk.LEFT, padx=20)
        ttk.Radiobutton(fmt_frame, text="PNG", variable=self.target_format, value="png").pack(side=tk.LEFT)

        self.convert_btn = ttk.Button(main_frame, text="CONVERTIR", command=self.start_conversion, state=tk.DISABLED)
        self.convert_btn.pack(fill=tk.X, pady=20)

        self.status_var = tk.StringVar(value="Listo")
        ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W).pack(side=tk.BOTTOM, fill=tk.X)

    def select_images(self):
        files = filedialog.askopenfilenames(filetypes=[('Imagenes', '*.png *.jpg *.jpeg')])
        if files:
            self.selected_files = files
            self.files_label.config(text=f"{len(files)} archivo(s) listos", foreground="black")
            self.convert_btn.config(state=tk.NORMAL)
            self.status_var.set("Archivos cargados.")

    def start_conversion(self):
        target = self.target_format.get()
        ok = 0
        errors = []
        self.status_var.set("Procesando...")
        self.root.update()
        for path in self.selected_files:
            try:
                if convert_image_file(path, target): ok += 1
            except Exception as e:
                errors.append(f"{os.path.basename(path)}: {e}")
        
        self.status_var.set("Finalizado")
        msg = f"Convertidos: {ok}"
        if errors: messagebox.showwarning("Resultados", msg + f"\nErrores: {len(errors)}")
        else: messagebox.showinfo("Exito", msg)
        self.selected_files = []
        self.files_label.config(text="Ningun archivo seleccionado", foreground="gray")
        self.convert_btn.config(state=tk.DISABLED)

if __name__ == "__main__":
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except: pass
    root = tk.Tk()
    app = ImageConverterApp(root)
    root.mainloop()