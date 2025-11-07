import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from docx2pdf import convert
import threading
import sv_ttk
import win32com.client
import pythoncom

class ConvertidorPro(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Convertidor PRO Word a PDF")
        self.geometry("600x480")
        self.resizable(False, False)
        sv_ttk.set_theme("dark")
        
        self.ruta_seleccionada = tk.StringVar()
        self.tipo_seleccion = tk.StringVar(value="archivo")
        self.word_app = None # Variable para controlar el motor de Word

        self._crear_interfaz()
        # --- AUTO-ARRANQUE ---
        # Iniciamos Word nada más abrir el programa para ganar tiempo
        threading.Thread(target=self._precargar_word, daemon=True).start()

    def _crear_interfaz(self):
        main_frame = ttk.Frame(self, padding="30")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="📄 Word a PDF Rápido", font=("Segoe UI", 24, "bold")).pack(pady=(0, 20))

        sel_frame = ttk.LabelFrame(main_frame, text="Opciones", padding="15")
        sel_frame.pack(fill=tk.X, pady=10)

        radio_frame = ttk.Frame(sel_frame)
        radio_frame.pack(fill=tk.X, pady=(0, 15))
        ttk.Radiobutton(radio_frame, text="Un solo archivo", variable=self.tipo_seleccion, value="archivo", command=self._limpiar_ruta).pack(side=tk.LEFT, padx=(0, 20))
        ttk.Radiobutton(radio_frame, text="Carpeta completa", variable=self.tipo_seleccion, value="carpeta", command=self._limpiar_ruta).pack(side=tk.LEFT)

        ruta_frame = ttk.Frame(sel_frame)
        ruta_frame.pack(fill=tk.X)
        self.entry_ruta = ttk.Entry(ruta_frame, textvariable=self.ruta_seleccionada, state="readonly")
        self.entry_ruta.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        ttk.Button(ruta_frame, text="Examinar...", command=self._buscar_ruta, style="Accent.TButton").pack(side=tk.RIGHT)

        self.btn_convertir = ttk.Button(main_frame, text="🚀 CONVERTIR AHORA", command=self._iniciar_conversion_hilo, style="Accent.TButton")
        self.btn_convertir.pack(pady=30, ipadx=30, ipady=15)

        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.lbl_estado = ttk.Label(main_frame, text="Esperando selección...", font=("Segoe UI", 10), foreground="gray")
        self.lbl_estado.pack(side=tk.BOTTOM, pady=(0, 5))
        
        # Etiqueta extra para mostrar el estado del "motor"
        self.lbl_motor = ttk.Label(main_frame, text="⚙️ Iniciando motor Word...", font=("Segoe UI", 8), foreground="#e3a008")
        self.lbl_motor.pack(side=tk.BOTTOM, pady=(0, 10))

    def _precargar_word(self):
        """Abre Word silenciosamente al iniciar la app para que esté listo."""
        try:
            pythoncom.CoInitialize() # Necesario para hilos en Windows
            self.word_app = win32com.client.Dispatch("Word.Application")
            self.word_app.Visible = False
            self.lbl_motor.config(text="✅ Motor listo para conversión rápida", foreground="#28a745")
        except Exception:
            # Si falla la precarga, no pasa nada, funcionará el método lento normal
            self.lbl_motor.config(text="⚠️ Motor en espera (conversión normal)", foreground="gray")

    def _limpiar_ruta(self):
        self.ruta_seleccionada.set("")
        self.lbl_estado.config(text="Esperando selección...", foreground="gray")

    def _buscar_ruta(self):
        if self.tipo_seleccion.get() == "archivo":
            ruta = filedialog.askopenfilename(filetypes=[("Word", "*.docx"), ("Todos", "*.*")])
        else:
            ruta = filedialog.askdirectory()
        if ruta:
            self.ruta_seleccionada.set(ruta)
            self.lbl_estado.config(text="Listo para disparar.", foreground="white")

    def _iniciar_conversion_hilo(self):
        if not self.ruta_seleccionada.get():
            messagebox.showwarning("Ojo", "Selecciona primero un archivo o carpeta.")
            return
        threading.Thread(target=self._proceso_conversion, args=(self.ruta_seleccionada.get(),), daemon=True).start()

    def _proceso_conversion(self, ruta):
        self.btn_convertir.config(state="disabled")
        self.progress.pack(fill=tk.X, padx=30, pady=(0,20))
        self.progress.start()
        self.lbl_estado.config(text="⏳ Trabajando... (esto será rápido si el motor está listo)", foreground="#007acc")

        try:
            pythoncom.CoInitialize()
            convert(ruta)
            self.lbl_estado.config(text="✨ ¡Terminado con éxito!", foreground="#28a745")
            messagebox.showinfo("Genial", "Conversión completada.")
        except Exception as e:
            self.lbl_estado.config(text="❌ Error en la conversión.", foreground="#dc3545")
            messagebox.showerror("Error", str(e))
        finally:
            self.progress.stop()
            self.progress.pack_forget()
            self.btn_convertir.config(state="normal")

    def on_closing(self):
        # Intenta cerrar Word si lo abrimos nosotros y no hay documentos abiertos
        try:
            if self.word_app and self.word_app.Documents.Count == 0:
                self.word_app.Quit()
        except:
            pass
        self.destroy()

if __name__ == "__main__":
    app = ConvertidorPro()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()