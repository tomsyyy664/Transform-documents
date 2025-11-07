import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
# AQUI ESTA LA CLAVE: Importamos la función de tu otro archivo
try:
    from converter import convert_image_file
except ImportError:
    # Fallback por si ejecutan interfaz.py sin tener converter.py al lado
    messagebox.showerror("Error", "No se encontró 'converter.py' en la misma carpeta.")
    exit()

class ImageConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Conversor de Imagenes")
        self.root.geometry("500x350")
        self.root.resizable(False, False)

        self.selected_files = []
        self.target_format = tk.StringVar(value="jpg")

        # --- LAYOUT ---
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Conversor PNG - JPG", font=("Helvetica", 16, "bold")).pack(pady=(0, 20))

        ttk.Button(main_frame, text="1. Seleccionar Imagenes", command=self.select_images).pack(fill=tk.X, pady=5)
        self.files_label = ttk.Label(main_frame, text="Ningun archivo seleccionado", foreground="gray")
        self.files_label.pack(pady=(0, 20))

        fmt_frame = ttk.LabelFrame(main_frame, text="2. Formato Destino", padding="10")
        fmt_frame.pack(fill=tk.X, pady=10)
        ttk.Radiobutton(fmt_frame, text="JPG", variable=self.target_format, value="jpg").pack(side=tk.LEFT, padx=20)
        ttk.Radiobutton(fmt_frame, text="PNG", variable=self.target_format, value="png").pack(side=tk.LEFT)

        self.convert_btn = ttk.Button(main_frame, text="3. CONVERTIR AHORA", command=self.start_conversion, state=tk.DISABLED)
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
        ok_count = 0
        errors = []

        self.status_var.set("Procesando...")
        self.root.update() # Forzar actualizacion visual

        for path in self.selected_files:
            try:
                # LLAMADA A TU OTRO ARCHIVO
                if convert_image_file(path, target):
                    ok_count += 1
            except Exception as e:
                errors.append(f"{os.path.basename(path)}: {e}")

        self.status_var.set("Finalizado")
        
        msg = f"Proceso terminado.\nConvertidos: {ok_count}"
        if errors:
            msg += f"\n\nErrores ({len(errors)}):\n" + "\n".join(errors[:5])
            if len(errors) > 5: msg += "\n..."
            messagebox.showwarning("Resultado", msg)
        else:
            messagebox.showinfo("Exito", msg)
            
        self.selected_files = []
        self.files_label.config(text="Ningun archivo seleccionado", foreground="gray")
        self.convert_btn.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageConverterApp(root)
    root.mainloop()