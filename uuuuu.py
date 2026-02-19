import customtkinter as ctk
import sqlite3
from datetime import datetime
from PIL import Image
import decimal
from tkinter import messagebox

ctk.set_appearance_mode("dark")

class GestorGastos(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Finanzas Neko Arc - Versión Final")
        self.geometry("550x850")
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
        try:
            img_fondo = Image.open(self.ruta_imagen)
            self.bg_image = ctk.CTkImage(light_image=img_fondo, dark_image=img_fondo, size=(550, 850))
            self.lbl_bg = ctk.CTkLabel(self, image=self.bg_image, text="")
            self.lbl_bg.place(x=0, y=0, relwidth=1, relheight=1)
        except: pass

        self.lbl_titulo = ctk.CTkLabel(self, text="BALANCE DISPONIBLE", font=("Arial", 18, "bold"), text_color="white", fg_color="#1a1a1a")
        self.lbl_titulo.pack(pady=(30, 5))

        self.lbl_balance = ctk.CTkLabel(self, text="Bs. 0,00", font=("Arial", 35, "bold"), text_color="#2ecc71", fg_color="#1a1a1a")
        self.lbl_balance.pack(pady=(0, 20))

        self.entry_monto = ctk.CTkEntry(self, placeholder_text="Monto (ej: 1500.50)", width=320, height=45, font=("Arial", 16))
        self.entry_monto.pack(pady=10)

        self.btn_ganancia = ctk.CTkButton(self, text="✚ REGISTRAR INGRESO", fg_color="#2ecc71", hover_color="#27ae60", width=250, height=45, font=("Arial", 13, "bold"), command=lambda: self.registrar("Ingreso"))
        self.btn_ganancia.pack(pady=5)

        self.btn_gasto = ctk.CTkButton(self, text="▬ REGISTRAR GASTO", fg_color="#e74c3c", hover_color="#c0392b", width=250, height=45, font=("Arial", 13, "bold"), command=lambda: self.registrar("Gasto"))
        self.btn_gasto.pack(pady=5)

        self.lbl_hist_titulo = ctk.CTkLabel(self, text="DETALLE DE MOVIMIENTOS", font=("Arial", 12, "bold"), text_color="#aaaaaa")
        self.lbl_hist_titulo.pack(pady=(20, 5))

        self.frame_historial = ctk.CTkScrollableFrame(self, width=480, height=300, fg_color="#121212", border_width=1, border_color="#333333")
        self.frame_historial.pack(pady=5, padx=20)

        self.btn_borrar_todo = ctk.CTkButton(self, text="LIMPIAR TODO EL HISTORIAL", fg_color="#555555", hover_color="#333333", width=200, height=30, font=("Arial", 10, "bold"), command=self.confirmar_borrado_total)
        self.btn_borrar_todo.pack(pady=20)

    def formato_moneda(self, valor):
        try:
            v = decimal.Decimal(str(valor)).quantize(decimal.Decimal("0.00"))
            f = "{:,.2f}".format(v)
            m, d = f.rsplit('.', 1)
            return "Bs. " + m.replace(',', '.') + ',' + d
        except: return "Bs. 0,00"

    def registrar(self, tipo):
        try:
            raw_text = self.entry_monto.get().strip().replace(".", "").replace(",", ".")
            if not raw_text: return
            monto_dec = decimal.Decimal(raw_text).quantize(decimal.Decimal("0.00"))

            if tipo == "Gasto" and monto_dec > self.total_acumulado:
                messagebox.showwarning("Saldo Insuficiente", f"No puedes gastar más de lo que tienes.\nSaldo actual: {self.formato_moneda(self.total_acumulado)}")
                return

            fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
            conn = sqlite3.connect("finanzas.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO movimientos (tipo, monto, fecha) VALUES (?, ?, ?)", (tipo, str(monto_dec), fecha))
            conn.commit()
            conn.close()
            self.entry_monto.delete(0, 'end')
            self.cargar_datos()
        except:
            messagebox.showerror("Error", "Ingresa un monto válido")

    def cargar_datos(self):
        for widget in self.frame_historial.winfo_children():
            widget.destroy()

        conn = sqlite3.connect("finanzas.db")
        cursor = conn.cursor()
        cursor.execute("SELECT tipo, monto FROM movimientos")
        todos = cursor.fetchall()
        
        total = decimal.Decimal("0.00")
        for r in todos:
            m = decimal.Decimal(str(r[1]))
            total = (total + m) if r[0] == "Ingreso" else (total - m)
        
        self.total_acumulado = total
        self.lbl_balance.configure(text=self.formato_moneda(total))

        cursor.execute("SELECT id, tipo, monto, fecha FROM movimientos ORDER BY id DESC LIMIT 50")
        registros = cursor.fetchall()
        conn.close()

        for id_reg, tipo, monto, fecha in registros:
            color_texto = "#2ecc71" if tipo == "Ingreso" else "#e74c3c"
            etiqueta = " [GANANCIA] " if tipo == "Ingreso" else " [GASTO]    "
            simbolo = "+" if tipo == "Ingreso" else "-"
            
            fila = ctk.CTkFrame(self.frame_historial, fg_color="transparent")
            fila.pack(fill="x", pady=2)

            texto = f"{fecha} |{etiqueta}| {simbolo}{self.formato_moneda(monto)}"
            lbl = ctk.CTkLabel(fila, text=texto, font=("Courier New", 12, "bold"), text_color=color_texto)
            lbl.pack(side="left", padx=5)

            btn_del = ctk.CTkButton(fila, text="🗑", width=30, height=25, fg_color="#2b2b2b", hover_color="#c0392b", 
                                    command=lambda i=id_reg, t=tipo, m=monto: self.eliminar_registro(i, t, m))
            btn_del.pack(side="right", padx=5)

    def eliminar_registro(self, id_registro, tipo, monto):
        monto_dec = decimal.Decimal(monto)

        # Lógica de seguridad para ingresos
        if tipo == "Ingreso":
            # Simulamos el nuevo saldo si borramos esta ganancia
            if (self.total_acumulado - monto_dec) < 0:
                messagebox.showerror("Acción Bloqueada", 
                    f"No puedes eliminar esta ganancia.\n\n"
                    f"Si la quitas, el saldo sería negativo ({self.formato_moneda(self.total_acumulado - monto_dec)}), "
                    "lo cual significa que tus gastos superarían a tus ingresos actuales.")
                return

        if messagebox.askyesno("Confirmar", "¿Eliminar este registro?"):
            conn = sqlite3.connect("finanzas.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM movimientos WHERE id = ?", (id_registro,))
            conn.commit()
            conn.close()
            self.cargar_datos()

    def confirmar_borrado_total(self):
        if messagebox.askyesno("Atención", "¿Borrar TODO el historial?"):
            conn = sqlite3.connect("finanzas.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM movimientos")
            conn.commit()
            conn.close()
            self.cargar_datos()

if __name__ == "__main__":
    app = GestorGastos()
    app.mainloop()