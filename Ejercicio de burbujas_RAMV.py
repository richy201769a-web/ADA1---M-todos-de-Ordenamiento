"""
EJERCICIO 1 - METODO DE ORDENAMIENTO BURBUJA

Problema: un profesor quiere ordenar las calificaciones de su grupo.

Como funciona: se comparan elementos vecinos y se intercambian si estan
en el orden incorrecto. En cada pasada el valor mas grande "sube" hasta
el final de la lista, como una burbuja.
"""

import re
import tkinter as tk
from tkinter import ttk

MAX_ELEMENTOS = 50      # cuantas calificaciones se pueden escribir
MAX_TEXTO = 400         # largo maximo de todo lo escrito
EJEMPLO = "85, 70, 95.5, 60, 100, 75"

PROBLEMA = ("Un profesor tiene las calificaciones de su grupo en desorden y "
            "necesita verlas ordenadas para ubicar rápido la más baja y la "
            "más alta.")
EXPLICACION = ("Se usa el método Burbuja: se compara cada calificación con la "
               "de al lado y se intercambian si están en el orden incorrecto. "
               "En cada pasada la mayor queda al final; se repite hasta que "
               "ya no hay intercambios.")
LIMITES = ("Solo se permiten números de 0 a 100 con máximo 2 decimales "
           f"(hasta {MAX_ELEMENTOS} calificaciones).")

SEPARADORES = re.compile(r"[,;\s]+")
PARCIAL = re.compile(r"\d{0,3}(\.\d{0,2})?")        # mientras se escribe
NUMERO = re.compile(r"[+-]?(\d+(\.\d*)?|\.\d+)")    # numero ya completo


# ----------------------------------------------------------------------
# Algoritmo
# ----------------------------------------------------------------------
def burbuja(datos, descendente=False):
    """Ordena con el metodo burbuja.

    No modifica la lista original. Regresa
    (lista_ordenada, pasadas, comparaciones, intercambios), donde pasadas
    es el estado de la lista al final de cada pasada.
    """
    lista = list(datos)
    pasadas = []
    comparaciones = 0
    intercambios = 0
    n = len(lista)
    for i in range(n - 1):
        hubo_intercambio = False
        # Los ultimos i elementos ya quedaron en su lugar
        for j in range(n - 1 - i):
            comparaciones += 1
            if descendente:
                desordenados = lista[j] < lista[j + 1]
            else:
                desordenados = lista[j] > lista[j + 1]
            if desordenados:
                lista[j], lista[j + 1] = lista[j + 1], lista[j]
                intercambios += 1
                hubo_intercambio = True
        pasadas.append(list(lista))
        # Si no hubo intercambios la lista ya esta ordenada
        if not hubo_intercambio:
            break
    return lista, pasadas, comparaciones, intercambios


# ----------------------------------------------------------------------
# Validacion de la entrada
# ----------------------------------------------------------------------
def entrada_permitida(texto):
    """Revisa el texto mientras se escribe, para bloquear lo que no cabe.

    Permite numeros a medio escribir (por ejemplo "85."), pero no letras,
    mas de 2 decimales ni valores mayores a 100.
    """
    if len(texto) > MAX_TEXTO:
        return False
    partes = [p for p in SEPARADORES.split(texto) if p]
    if len(partes) > MAX_ELEMENTOS:
        return False
    for parte in partes:
        if not PARCIAL.fullmatch(parte):
            return False
        if parte != "." and float(parte) > 100:
            return False
    return True


def leer_calificaciones(texto):
    """Convierte el texto en una lista de calificaciones (0 a 100).

    Lanza ValueError con un mensaje claro si algun dato no es valido.
    """
    partes = [p for p in SEPARADORES.split(texto.strip()) if p]
    if not partes:
        raise ValueError("Escribe las calificaciones separadas por comas.")
    if len(partes) < 2:
        raise ValueError("Escribe al menos 2 calificaciones para ordenar.")
    if len(partes) > MAX_ELEMENTOS:
        raise ValueError(f"Escribe como máximo {MAX_ELEMENTOS} calificaciones.")

    calificaciones = []
    for parte in partes:
        if not NUMERO.fullmatch(parte):
            raise ValueError(f'"{parte}" no es un número válido.')
        if "." in parte and len(parte.split(".")[1]) > 2:
            raise ValueError(f'"{parte[:12]}" tiene más de 2 decimales.')
        valor = float(parte)
        if not 0 <= valor <= 100:
            raise ValueError(f'"{parte[:12]}" está fuera del rango de 0 a 100.')
        calificaciones.append(valor)
    return calificaciones


def formato(lista):
    """Muestra 85.0 como 85 y 85.5 como 85.5."""
    return "[" + ", ".join(f"{valor:g}" for valor in lista) + "]"


# ----------------------------------------------------------------------
# Interfaz grafica
# ----------------------------------------------------------------------
class Aplicacion(ttk.Frame):
    def __init__(self, raiz):
        super().__init__(raiz, padding=12)
        raiz.title("Ejercicio 1 - Método Burbuja")
        raiz.minsize(560, 540)
        raiz.columnconfigure(0, weight=1)
        raiz.rowconfigure(0, weight=1)
        self.grid(sticky="nsew")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(7, weight=1)

        self.entrada = tk.StringVar()
        self.orden = tk.StringVar(value="asc")
        self.mensaje = tk.StringVar()
        self.textos = []    # etiquetas largas que se ajustan al ancho

        ttk.Label(self, text="Ordenar calificaciones (Burbuja)",
                  font=("Segoe UI", 14, "bold")).grid(row=0, column=0, sticky="w")
        self.recuadro(1, "Problema", PROBLEMA)
        self.recuadro(2, "¿Qué hace el programa?", EXPLICACION)

        ttk.Label(self, text="Calificaciones de 0 a 100 (máximo 2 decimales), "
                             "separadas por comas:"
                  ).grid(row=3, column=0, sticky="w", pady=(10, 2))

        # validate="key" revisa cada tecla y bloquea lo que no se permite
        revisar = (self.register(self.revisar_tecla), "%P")
        self.caja = ttk.Entry(self, textvariable=self.entrada,
                              validate="key", validatecommand=revisar)
        self.caja.grid(row=4, column=0, sticky="ew")
        self.caja.bind("<Return>", lambda evento: self.ordenar())
        self.caja.focus_set()

        opciones = ttk.Frame(self)
        opciones.grid(row=5, column=0, sticky="ew", pady=8)
        ttk.Radiobutton(opciones, text="Menor a mayor", value="asc",
                        variable=self.orden).pack(side="left")
        ttk.Radiobutton(opciones, text="Mayor a menor", value="desc",
                        variable=self.orden).pack(side="left", padx=(8, 0))
        ttk.Button(opciones, text="Limpiar", command=self.limpiar).pack(side="right")
        ttk.Button(opciones, text="Ejemplo", command=self.ejemplo
                   ).pack(side="right", padx=4)
        ttk.Button(opciones, text="Ordenar", command=self.ordenar).pack(side="right")

        self.etiqueta = ttk.Label(self, textvariable=self.mensaje, wraplength=520)
        self.etiqueta.grid(row=6, column=0, sticky="w")
        self.textos.append(self.etiqueta)

        marco = ttk.Frame(self)
        marco.grid(row=7, column=0, sticky="nsew", pady=(6, 0))
        marco.columnconfigure(0, weight=1)
        marco.rowconfigure(0, weight=1)
        self.salida = tk.Text(marco, height=10, wrap="word", state="disabled",
                              font=("Consolas", 10))
        barra = ttk.Scrollbar(marco, command=self.salida.yview)
        self.salida.configure(yscrollcommand=barra.set)
        self.salida.grid(row=0, column=0, sticky="nsew")
        barra.grid(row=0, column=1, sticky="ns")

        self.bind("<Configure>", self.ajustar_textos)

    def recuadro(self, fila, titulo, texto):
        caja = ttk.LabelFrame(self, text=titulo, padding=(8, 4))
        caja.grid(row=fila, column=0, sticky="ew", pady=(8, 0))
        etiqueta = ttk.Label(caja, text=texto, wraplength=500, justify="left")
        etiqueta.pack(anchor="w")
        self.textos.append(etiqueta)

    def ajustar_textos(self, evento):
        ancho = max(evento.width - 50, 200)
        for etiqueta in self.textos:
            etiqueta.configure(wraplength=ancho)

    def revisar_tecla(self, texto_nuevo):
        if entrada_permitida(texto_nuevo):
            if self.mensaje.get() == LIMITES:
                self.avisar("")
            return True
        self.avisar(LIMITES, es_error=True)
        return False

    def escribir(self, texto):
        self.salida.configure(state="normal")
        self.salida.delete("1.0", "end")
        self.salida.insert("1.0", texto)
        self.salida.configure(state="disabled")

    def avisar(self, texto, es_error=False):
        self.etiqueta.configure(foreground="#b00020" if es_error else "#1b5e20")
        self.mensaje.set(texto)

    def ordenar(self):
        try:
            calificaciones = leer_calificaciones(self.entrada.get())
        except ValueError as error:
            self.escribir("")
            self.avisar(str(error), es_error=True)
            self.caja.focus_set()
            return

        ordenada, pasadas, comparaciones, intercambios = burbuja(
            calificaciones, self.orden.get() == "desc")
        lineas = [f"Original:  {formato(calificaciones)}", ""]
        for numero, estado in enumerate(pasadas, start=1):
            lineas.append(f"Pasada {numero}:  {formato(estado)}")
        lineas += ["", f"Ordenada:  {formato(ordenada)}", "",
                   f"Comparaciones: {comparaciones}",
                   f"Intercambios:  {intercambios}"]
        self.escribir("\n".join(lineas))
        self.avisar(f"Lista ordenada en {len(pasadas)} pasada(s). "
                    f"Comparaciones: {comparaciones}. "
                    f"Intercambios: {intercambios}.")

    def ejemplo(self):
        self.entrada.set(EJEMPLO)
        self.ordenar()

    def limpiar(self):
        self.entrada.set("")
        self.escribir("")
        self.avisar("")
        self.caja.focus_set()


def main():
    try:  # Evita que la ventana se vea borrosa en Windows
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
    raiz = tk.Tk()
    Aplicacion(raiz)
    raiz.mainloop()


if __name__ == "__main__":
    main()