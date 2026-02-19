import customtkinter as ctk
import sqlite3
from datetime import datetime
from PIL import Image
import decimal
from tkinter import messagebox

# Configuración de apariencia
ctk.set_appearance_mode("dark")

class GestorGastos(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Finanzas Neko Arc - Versión Final")
        self.geometry("550x800")
        self.resizable(False, False)
        
        self.total_acumulado = decimal.Decimal("0.00")
        self.ruta_imagen = r"C:\Users\APRENDIZ.SOPORTEPQ\Pictures\nekoarc-jydx.png"

        self.init_db()
        self.setup_ui()
        self.cargar_datos()

    def init_db(self):
        conn = sqlite3.connect("finanzas.db")
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS movimientos 
                          (id INTEGER PRIMARY KEY AUTOINCREMENT, tipo TEXT, monto TEXT, fecha TEXT)''')
        conn.commit()
        conn.close()

    def setup_ui(self):
        # --- FONDO ---
        try:
            img_fondo = Image.open(self.ruta_imagen)
            self.bg_image = ctk.CTkImage(light_image=img_fondo, dark_image=img_fondo, size=(550, 800))
            self.lbl_bg = ctk.CTkLabel(self, image=self.bg_image, text="")
            self.lbl_bg.place(x=0, y=0, relwidth=1, relheight=1)
        except: pass

        # --- PANEL DE CONTROL ---
        self.lbl_titulo = ctk.CTkLabel(self, text="BALANCE DISPONIBLE", font=("Arial", 18, "bold"), text_color="white", fg_color="#1a1a1a")
        self.lbl_titulo.pack(pady=(30, 5))

        self.lbl_balance = ctk.CTkLabel(self, text="Bs. 0,00", font=("Arial", 30, "bold"), text_color="#2ecc71", fg_color="#1a1a1a")
        self.lbl_balance.pack(pady=(0, 20))

        # Entrada de texto reforzada
        self.entry_monto = ctk.CTkEntry(self, placeholder_text="Ingrese monto sin puntos de mil", width=320, height=45, font=("Arial", 16))
        self.entry_monto.pack(pady=10)

        # Botones Principales
        self.btn_ganancia = ctk.CTkButton(self, text="✚ REGISTRAR INGRESO", fg_color="#2ecc71", hover_color="#27ae60", width=250, height=45, font=("Arial", 13, "bold"), command=lambda: self.registrar("Ingreso"))
        self.btn_ganancia.pack(pady=5)

        self.btn_gasto = ctk.CTkButton(self, text="▬ REGISTRAR GASTO", fg_color="#e74c3c", hover_color="#c0392b", width=250, height=45, font=("Arial", 13, "bold"), command=lambda: self.registrar("Gasto"))
        self.btn_gasto.pack(pady=5)

        # Botón de Borrado Total
        self.btn_borrar = ctk.CTkButton(self, text="🗑️ BORRAR TODO EL HISTORIAL", fg_color="#555555", hover_color="#333333", width=250, height=35, font=("Arial", 11, "bold"), command=self.confirmar_borrado)
        self.btn_borrar.pack(pady=20)

        self.txt_historial = ctk.CTkTextbox(self, width=500, height=220, font=("Courier New", 11), fg_color="#121212", text_color="#ecf0f1", border_width=1)
        self.txt_historial.pack(pady=10, padx=20)

    def formato_moneda(self, valor):
        """Convierte números a formato Bs. 1.234.567,89"""
        try:
            v = decimal.Decimal(str(valor)).quantize(decimal.Decimal("0.00"))
            f = "{:,.2f}".format(v)
            m, d = f.rsplit('.', 1)
            return "Bs. " + m.replace(',', '.') + ',' + d
        except: return "Bs. 0,00"

    def registrar(self, tipo):
        try:
            # LIMPIEZA TOTAL: Quitamos puntos y espacios, cambiamos coma por punto
            raw_text = self.entry_monto.get().strip().replace(".", "").replace(",", ".")
            if not raw_text: return
            
            monto_dec = decimal.Decimal(raw_text).quantize(decimal.Decimal("0.00"))

            # Verificación de saldo sin errores de redondeo
            if tipo == "Gasto" and monto_dec > self.total_acumulado:
                messagebox.showwarning("Saldo Insuficiente", f"No puedes gastar {self.formato_moneda(monto_dec)}.\nTu saldo es {self.formato_moneda(self.total_acumulado)}")
                return

            fecha = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            
            conn = sqlite3.connect("finanzas.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO movimientos (tipo, monto, fecha) VALUES (?, ?, ?)", (tipo, str(monto_dec), fecha))
            conn.commit()
            conn.close()

            self.entry_monto.delete(0, 'end')
            self.cargar_datos()
            
        except Exception as e:
            messagebox.showerror("Error", "Ingresa un número válido (ej: 1500.50)")

    def cargar_datos(self):
        try:
            conn = sqlite3.connect("finanzas.db")
            cursor = conn.cursor()
            cursor.execute("SELECT tipo, monto, fecha FROM movimientos ORDER BY id DESC LIMIT 100")
            registros = cursor.fetchall()
            cursor.execute("SELECT tipo, monto FROM movimientos")
            todos = cursor.fetchall()
            conn.close()

            total = decimal.Decimal("0.00")
            for r in todos:
                m = decimal.Decimal(str(r[1]))
                total = (total + m) if r[0] == "Ingreso" else (total - m)
            
            self.total_acumulado = total
            self.lbl_balance.configure(text=self.formato_moneda(total))
            
            self.txt_historial.configure(state="normal")
            self.txt_historial.delete("1.0", "end")
            for t, m, f in registros:
                sim = "+" if t == "Ingreso" else "-"
                self.txt_historial.insert("end", f"[{f}] {t}: {sim}{self.formato_moneda(m)}\n")
            self.txt_historial.configure(state="disabled")
        except: pass

    def confirmar_borrado(self):
        respuesta = messagebox.askyesno("Confirmar Borrado", "¿Estás seguro de que deseas eliminar TODOS los datos?\nEsta acción no se puede deshacer.")
        if respuesta:
            conn = sqlite3.connect("finanzas.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM movimientos")
            conn.commit()
            conn.close()
            self.cargar_datos()
            messagebox.showinfo("Éxito", "Todos los datos han sido borrados.")

if __name__ == "__main__":
    app = GestorGastos()
    app.mainloop()