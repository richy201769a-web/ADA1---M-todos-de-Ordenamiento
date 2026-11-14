"""
EJERCICIO 2 - METODO DE ORDENAMIENTO POR INSERCION

Problema: una biblioteca recibe nombres de alumnos y necesita ordenarlos
alfabeticamente para su registro.

Como funciona: se toma un elemento a la vez y se inserta en la posicion
correcta dentro de la parte izquierda de la lista, que ya esta ordenada
(igual que al acomodar cartas en la mano).
"""

import re
import tkinter as tk
import unicodedata
from tkinter import ttk

MAX_ELEMENTOS = 50      # cuantos nombres se pueden escribir
MAX_LETRAS = 25         # largo maximo de cada nombre
MAX_TEXTO = 1500        # largo maximo de todo lo escrito
EJEMPLO = "Mario, Ana, Luis, Carla, Beto"

PROBLEMA = ("Una biblioteca recibe los nombres de los alumnos conforme van "
            "llegando y necesita tenerlos en orden alfabético para su "
            "registro.")
EXPLICACION = ("Se usa el método por Inserción: se toma un nombre a la vez y "
               "se coloca en el lugar que le corresponde entre los que ya "
               "están ordenados, igual que al acomodar cartas en la mano.")
LIMITES = (f"Solo se permiten letras y cada nombre puede tener máximo "
           f"{MAX_LETRAS} caracteres (hasta {MAX_ELEMENTOS} nombres).")

SEPARADORES = re.compile(r"[,;\n]+")
SIGNOS = " .'-"         # signos que puede llevar un nombre ademas de letras


# ----------------------------------------------------------------------
# Algoritmo
# ----------------------------------------------------------------------
def insercion(datos, descendente=False, clave=lambda elemento: elemento):
    """Ordena con el metodo de insercion.

    No modifica la lista original. "clave" es la funcion con la que se
    comparan los elementos. Regresa
    (lista_ordenada, pasos, comparaciones, desplazamientos), donde pasos
    es el estado de la lista despues de insertar cada elemento.

    Este metodo no intercambia: recorre elementos un lugar a la derecha
    para abrir espacio, por eso se cuentan "desplazamientos".
    """
    lista = list(datos)
    pasos = []
    comparaciones = 0
    desplazamientos = 0
    for i in range(1, len(lista)):
        actual = lista[i]
        clave_actual = clave(actual)
        j = i - 1
        # Recorre a la derecha los elementos que deben ir despues de "actual"
        while j >= 0:
            comparaciones += 1
            if descendente:
                va_despues = clave(lista[j]) < clave_actual
            else:
                va_despues = clave(lista[j]) > clave_actual
            if not va_despues:
                break
            lista[j + 1] = lista[j]
            desplazamientos += 1
            j -= 1
        lista[j + 1] = actual
        pasos.append(list(lista))
    return lista, pasos, comparaciones, desplazamientos


def clave_alfabetica(nombre):
    """Clave para ordenar en espanol.

    Ignora mayusculas y acentos (asi "ana", "Ángel" y "Beto" quedan en el
    orden esperado) y coloca la "ñ" despues de la "n".
    """
    texto = unicodedata.normalize("NFC", nombre).casefold()
    texto = texto.replace("ñ", "\x00")  # se protege para no perder la tilde
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return texto.replace("\x00", "n\U0010ffff")


# ----------------------------------------------------------------------
# Validacion de la entrada
# ----------------------------------------------------------------------
def separar(texto):
    """Parte el texto en nombres y quita espacios de mas."""
    partes = [" ".join(p.split()) for p in SEPARADORES.split(texto)]
    return [unicodedata.normalize("NFC", p) for p in partes if p]


def entrada_permitida(texto):
    """Revisa el texto mientras se escribe, para bloquear lo que no cabe.

    No deja escribir numeros o simbolos ni nombres mas largos de lo
    permitido.
    """
    if len(texto) > MAX_TEXTO:
        return False
    nombres = separar(texto)
    if len(nombres) > MAX_ELEMENTOS:
        return False
    for nombre in nombres:
        if len(nombre) > MAX_LETRAS:
            return False
        if not all(c.isalpha() or c in SIGNOS for c in nombre):
            return False
    return True


def leer_nombres(texto):
    """Convierte el texto en una lista de nombres.

    Lanza ValueError con un mensaje claro si algun dato no es valido.
    """
    partes = separar(texto)
    if not partes:
        raise ValueError("Escribe los nombres separados por comas.")
    if len(partes) < 2:
        raise ValueError("Escribe al menos 2 nombres para ordenar.")
    if len(partes) > MAX_ELEMENTOS:
        raise ValueError(f"Escribe como máximo {MAX_ELEMENTOS} nombres.")

    for nombre in partes:
        if len(nombre) > MAX_LETRAS:
            raise ValueError(f'"{nombre[:15]}..." es demasiado largo '
                             f"(máximo {MAX_LETRAS} caracteres).")
        if not any(c.isalpha() for c in nombre):
            raise ValueError(f'"{nombre}" no es un nombre válido.')
        if not all(c.isalpha() or c in SIGNOS for c in nombre):
            raise ValueError(
                f'"{nombre}" no es un nombre válido: usa solo letras.')
    return partes


def formato(lista):
    return ", ".join(lista)


# ----------------------------------------------------------------------
# Interfaz grafica
# ----------------------------------------------------------------------
class Aplicacion(ttk.Frame):
    def __init__(self, raiz):
        super().__init__(raiz, padding=12)
        raiz.title("Ejercicio 2 - Método por Inserción")
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

        ttk.Label(self, text="Ordenar nombres (Inserción)",
                  font=("Segoe UI", 14, "bold")).grid(row=0, column=0, sticky="w")
        self.recuadro(1, "Problema", PROBLEMA)
        self.recuadro(2, "¿Qué hace el programa?", EXPLICACION)

        ttk.Label(self, text=f"Nombres de máximo {MAX_LETRAS} caracteres, "
                             "separados por comas:"
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
        ttk.Radiobutton(opciones, text="A → Z", value="asc",
                        variable=self.orden).pack(side="left")
        ttk.Radiobutton(opciones, text="Z → A", value="desc",
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
            nombres = leer_nombres(self.entrada.get())
        except ValueError as error:
            self.escribir("")
            self.avisar(str(error), es_error=True)
            self.caja.focus_set()
            return

        ordenada, pasos, comparaciones, desplazamientos = insercion(
            nombres, self.orden.get() == "desc", clave=clave_alfabetica)
        lineas = [f"Original:  {formato(nombres)}", ""]
        for numero, estado in enumerate(pasos, start=1):
            lineas.append(f"Paso {numero} (se inserta {nombres[numero]}):")
            lineas.append(f"    {formato(estado)}")
        lineas += ["", f"Ordenada:  {formato(ordenada)}", "",
                   f"Comparaciones:   {comparaciones}",
                   f"Desplazamientos: {desplazamientos}"]
        self.escribir("\n".join(lineas))
        self.avisar(f"Lista ordenada en {len(pasos)} paso(s). "
                    f"Comparaciones: {comparaciones}. "
                    f"Desplazamientos: {desplazamientos}.")

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