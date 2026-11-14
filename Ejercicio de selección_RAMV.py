"""
EJERCICIO 3 - METODO DE ORDENAMIENTO POR SELECCION

Problema: una tienda quiere mostrar sus productos ordenados por precio.

Como funciona: se busca el elemento mas pequeno de la parte no ordenada
y se intercambia con el primero de esa parte. Se repite hasta terminar
la lista.
"""

import re
import tkinter as tk
from tkinter import ttk

MAX_ELEMENTOS = 50          # cuantos precios se pueden escribir
PRECIO_MAXIMO = 1_000_000   # precio mas alto permitido
MAX_TEXTO = 600             # largo maximo de todo lo escrito
EJEMPLO = "249.90, 89.50, 150, 35, 499.99"

PROBLEMA = ("Una tienda tiene los precios de sus productos en desorden y "
            "quiere mostrarlos ordenados para que el cliente los compare "
            "fácilmente.")
EXPLICACION = ("Se usa el método por Selección: se busca el precio más bajo "
               "de los que faltan por ordenar y se coloca al inicio de esa "
               "parte. Se repite con el resto hasta terminar la lista.")
LIMITES = (f"Solo se permiten precios de $0 a ${PRECIO_MAXIMO:,} con máximo "
           f"2 decimales (hasta {MAX_ELEMENTOS} precios).")

SEPARADORES = re.compile(r"[,;\s]+")
PARCIAL = re.compile(r"\$?\d{0,7}(\.\d{0,2})?")     # mientras se escribe
NUMERO = re.compile(r"[+-]?(\d+(\.\d*)?|\.\d+)")    # numero ya completo


# ----------------------------------------------------------------------
# Algoritmo
# ----------------------------------------------------------------------
def seleccion(datos, descendente=False):
    """Ordena con el metodo de seleccion.

    No modifica la lista original. Regresa
    (lista_ordenada, pasos, comparaciones, intercambios), donde cada paso
    es (estado_de_la_lista, valor_elegido, hubo_intercambio).
    """
    lista = list(datos)
    pasos = []
    comparaciones = 0
    intercambios = 0
    n = len(lista)
    for i in range(n - 1):
        elegido = i
        # Busca el menor (o el mayor) de la parte que falta por ordenar
        for j in range(i + 1, n):
            comparaciones += 1
            if descendente:
                es_mejor = lista[j] > lista[elegido]
            else:
                es_mejor = lista[j] < lista[elegido]
            if es_mejor:
                elegido = j
        hubo_intercambio = elegido != i
        if hubo_intercambio:
            lista[i], lista[elegido] = lista[elegido], lista[i]
            intercambios += 1
        pasos.append((list(lista), lista[i], hubo_intercambio))
    return lista, pasos, comparaciones, intercambios


# ----------------------------------------------------------------------
# Validacion de la entrada
# ----------------------------------------------------------------------
def entrada_permitida(texto):
    """Revisa el texto mientras se escribe, para bloquear lo que no cabe.

    Permite precios a medio escribir (por ejemplo "89."), pero no letras,
    mas de 2 decimales ni valores mayores al precio maximo.
    """
    if len(texto) > MAX_TEXTO:
        return False
    partes = [p for p in SEPARADORES.split(texto) if p]
    if len(partes) > MAX_ELEMENTOS:
        return False
    for parte in partes:
        if not PARCIAL.fullmatch(parte):
            return False
        numero = parte.lstrip("$")
        if numero not in ("", ".") and float(numero) > PRECIO_MAXIMO:
            return False
    return True


def leer_precios(texto):
    """Convierte el texto en una lista de precios.

    Lanza ValueError con un mensaje claro si algun dato no es valido.
    """
    partes = [p for p in SEPARADORES.split(texto.strip()) if p]
    if not partes:
        raise ValueError("Escribe los precios separados por comas.")
    if len(partes) < 2:
        raise ValueError("Escribe al menos 2 precios para ordenar.")
    if len(partes) > MAX_ELEMENTOS:
        raise ValueError(f"Escribe como máximo {MAX_ELEMENTOS} precios.")

    precios = []
    for parte in partes:
        numero = parte[1:] if parte.startswith("$") else parte
        if not NUMERO.fullmatch(numero):
            raise ValueError(
                f'"{parte[:12]}" no es un precio válido. Usa punto para los '
                "decimales, por ejemplo 89.50")
        if "." in numero and len(numero.split(".")[1]) > 2:
            raise ValueError(f'"{parte[:12]}" tiene más de 2 decimales.')
        valor = float(numero)
        if valor < 0:
            raise ValueError(f'"{parte[:12]}" no es válido: el precio no '
                             "puede ser negativo.")
        if valor > PRECIO_MAXIMO:
            raise ValueError(f'"{parte[:12]}" pasa del máximo permitido '
                             f"(${PRECIO_MAXIMO:,}).")
        precios.append(valor)
    return precios


def pesos(valor):
    return f"${valor:,.2f}"


def formato(lista):
    return "  ".join(pesos(valor) for valor in lista)


# ----------------------------------------------------------------------
# Interfaz grafica
# ----------------------------------------------------------------------
class Aplicacion(ttk.Frame):
    def __init__(self, raiz):
        super().__init__(raiz, padding=12)
        raiz.title("Ejercicio 3 - Método por Selección")
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

        ttk.Label(self, text="Ordenar precios (Selección)",
                  font=("Segoe UI", 14, "bold")).grid(row=0, column=0, sticky="w")
        self.recuadro(1, "Problema", PROBLEMA)
        self.recuadro(2, "¿Qué hace el programa?", EXPLICACION)

        ttk.Label(self, text=f"Precios de $0 a ${PRECIO_MAXIMO:,} (máximo 2 "
                             "decimales, con punto), separados por comas:"
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
        ttk.Radiobutton(opciones, text="Barato a caro", value="asc",
                        variable=self.orden).pack(side="left")
        ttk.Radiobutton(opciones, text="Caro a barato", value="desc",
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
            precios = leer_precios(self.entrada.get())
        except ValueError as error:
            self.escribir("")
            self.avisar(str(error), es_error=True)
            self.caja.focus_set()
            return

        ordenada, pasos, comparaciones, intercambios = seleccion(
            precios, self.orden.get() == "desc")
        lineas = [f"Original:  {formato(precios)}", ""]
        for numero, (estado, elegido, hubo_intercambio) in enumerate(pasos, 1):
            nota = "se intercambia" if hubo_intercambio else "ya estaba en su lugar"
            lineas.append(f"Paso {numero} (elige {pesos(elegido)}, {nota}):")
            lineas.append(f"    {formato(estado)}")
        lineas += ["", f"Ordenada:  {formato(ordenada)}", "",
                   f"Comparaciones: {comparaciones}",
                   f"Intercambios:  {intercambios}"]
        self.escribir("\n".join(lineas))
        self.avisar(f"Lista ordenada en {len(pasos)} paso(s). "
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