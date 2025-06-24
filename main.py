import tkinter as tk
from tkinter import ttk
import random
import copy
import math

# ==================================================
# CONFIGURACIÓN INICIAL
# ==================================================
TABLERO_EJEMPLO = [
    [0, 6, 0, 1, 0, 4, 0, 5, 0],
    [0, 0, 8, 3, 0, 5, 6, 0, 0],
    [2, 0, 0, 0, 0, 0, 0, 0, 1],
    [8, 0, 0, 4, 0, 7, 0, 0, 6],
    [0, 0, 6, 0, 0, 0, 3, 0, 0],
    [7, 0, 0, 9, 0, 1, 0, 0, 4],
    [5, 0, 0, 0, 0, 0, 0, 0, 2],
    [0, 0, 7, 2, 0, 6, 9, 0, 0],
    [0, 4, 0, 5, 0, 8, 0, 7, 0]
]

# ==================================================
# FUNCIONES BASE
# ==================================================
def obtener_casillas_fijas(tablero_inicial):
    """Retorna matriz booleana para indicar casillas fijas."""
    return [[celda != 0 for celda in fila] for fila in tablero_inicial]

def inicializar_individuo(tablero_inicial):
    """Rellena casillas vacías en cada fila con números del 1 al 9."""
    individuo = copy.deepcopy(tablero_inicial)
    for i in range(9):
        usados = set(individuo[i]) - {0}
        disponibles = list(set(range(1, 10)) - usados)
        random.shuffle(disponibles)
        k = 0
        for j in range(9):
            if individuo[i][j] == 0:
                individuo[i][j] = disponibles[k]
                k += 1
    return individuo

def crear_poblacion(tamano, tablero_inicial):
    """Crea población inicial basada en el tablero inicial."""
    return [inicializar_individuo(tablero_inicial) for _ in range(tamano)]

def evaluar_adaptabilidad_simple(individuo):
    """Calcula adaptabilidad basada en faltas en COLUMNAS y SUBCUADRÍCULAS."""
    faltas = 0
    for col in range(9):
        nums = [individuo[fila][col] for fila in range(9)]
        faltas += (9 - len(set(nums)))
    for i in range(0, 9, 3):
        for j in range(0, 9, 3):
            nums = [individuo[x][y] for x in range(i, i + 3) for y in range(j, j + 3)]
            faltas += (9 - len(set(nums)))
    return faltas

def evaluar_adaptabilidad(individuo):
    """Calcula F(x) según el documento:
    F(x) = 5 * RS + 1 * sqrt(RP_diff) + 20 * REA
    """
    FACTORIAL_9 = math.factorial(9)
    adaptabilidad = 0

    # Por COLUMNAS
    for col in range(9):
        nums = [individuo[fila][col] for fila in range(9)]
        RS = abs(45 - sum(nums))
        RP = math.sqrt(abs(FACTORIAL_9 - math.prod(nums)))
        REA = 9 - len(set(nums))
        adaptabilidad += (5 * RS) + RP + (20 * REA)

    # Por SUBCUADRÍCULAS
    for i in range(0, 9, 3):
        for j in range(0, 9, 3):
            nums = [individuo[x][y] for x in range(i, i + 3) for y in range(j, j + 3)]
            RS = abs(45 - sum(nums))
            RP = math.sqrt(abs(FACTORIAL_9 - math.prod(nums)))
            REA = 9 - len(set(nums))
            adaptabilidad += (5 * RS) + RP + (20 * REA)

    return adaptabilidad


def torneo(poblacion,evaluar, k=3):
    """Selección por torneo."""
    return min(random.sample(poblacion, k), key=evaluar)

def cruce_por_filas(p1, p2, prob_cruce):
    """Cruce por posición de fila completa para mantener la validez interna."""
    hijo = []
    for i in range(9):
        if random.random() < prob_cruce:
            hijo.append(copy.deepcopy(p1[i]))
        else:
            hijo.append(copy.deepcopy(p2[i]))
    return hijo

def cruce_alternado(p1, p2):
    """Alterna las filas para crear un hijo."""
    hijo = []
    for i in range(9):
        hijo.append(copy.deepcopy(p1[i]) if i % 2 == 0 else copy.deepcopy(p2[i]))
    return hijo

def cruce_pmx_fila(fila1, fila2):
    """Cruce PMX para una sola fila."""
    size = len(fila1)
    hijo = [-1] * size
    p1, p2 = fila1, fila2
    punto1, punto2 = sorted(random.sample(range(size), 2))
    hijo[punto1:punto2] = p1[punto1:punto2]

    for elem in p2[punto1:punto2]:
        if elem not in hijo:
            pos = p2.index(elem)
            while hijo[pos] != -1:
                pos = p2.index(p1[pos])
            hijo[pos] = elem

    for i in range(size):
        if hijo[i] == -1:
            hijo[i] = p2[i]

    return hijo


def cruce_pmx(p1, p2, prob_cruce):
    """Aplica PMX por fila para crear un hijo."""
    hijo = []
    for i in range(9):
        if random.random() < prob_cruce:
            hijo.append(cruce_pmx_fila(p1[i], p2[i]))
        else:
            hijo.append(copy.deepcopy(p1[i]))
    return hijo

def cruce_ox_fila(fila1, fila2):
    """Cruce OX para una sola fila."""
    size = len(fila1)
    hijo = [-1] * size
    punto1, punto2 = sorted(random.sample(range(size), 2))
    hijo[punto1:punto2] = fila1[punto1:punto2]

    pos = punto2
    for elem in fila2:
        if elem not in hijo:
            if pos >= size:
                pos = 0
            hijo[pos] = elem
            pos += 1
    return hijo


def cruce_ox(p1, p2, prob_cruce):
    """Aplica OX por fila para crear un hijo."""
    hijo = []
    for i in range(9):
        if random.random() < prob_cruce:
            hijo.append(cruce_ox_fila(p1[i], p2[i]))
        else:
            hijo.append(copy.deepcopy(p1[i]))
    return hijo

def seleccionar_cruce(tipo_cruce, p1, p2, prob_cruce):
    """Devuelve el hijo según el método de cruce seleccionado."""
    if tipo_cruce == "Filas":
        return cruce_por_filas(p1, p2, prob_cruce)
    elif tipo_cruce == "Alternado":
        return cruce_alternado(p1, p2)
    elif tipo_cruce == "PMX":
        return cruce_pmx(p1, p2, prob_cruce)
    elif tipo_cruce == "OX":
        return cruce_ox(p1, p2, prob_cruce)
    else:
        # Por defecto usa cruce por filas
        return cruce_por_filas(p1, p2, prob_cruce)

def mutacion_intercambio(ind, fijos, prob_mut):
    """Intercambio en la misma fila para mantener validez interna."""
    hijo = copy.deepcopy(ind)
    for i in range(9):
        if random.random() < prob_mut:
            indices_libres = [k for k in range(9) if not fijos[i][k]]
            if len(indices_libres) >= 2:
                a, b = random.sample(indices_libres, 2)
                hijo[i][a], hijo[i][b] = hijo[i][b], hijo[i][a]
    return hijo

def mutacion_rotacion(ind, fijos, prob_mut):
    """Rota los elementos no fijos en cada fila para crear variación."""
    hijo = copy.deepcopy(ind)
    for i in range(9):  # Por cada fila
        if random.random() < prob_mut:
            indices_libres = [k for k in range(9) if not fijos[i][k]]
            if len(indices_libres) > 1:
                elementos = [hijo[i][k] for k in indices_libres]
                elementos = elementos[-1:] + elementos[:-1]  # Rotación a la derecha
                for k, elem in zip(indices_libres, elementos):
                    hijo[i][k] = elem
    return hijo

def mutacion_regeneracion(ind, fijos, prob_mut):
    """Regenera toda la fila para elementos no fijos, respetando elementos fijos."""
    hijo = copy.deepcopy(ind)
    for i in range(9):  # Por cada fila
        if random.random() < prob_mut:
            usados = {hijo[i][k] for k in range(9) if fijos[i][k]}
            disponibles = list(set(range(1, 10)) - usados)
            random.shuffle(disponibles)

            k = 0
            for j in range(9):  # Por cada posición en la fila
                if not fijos[i][j]:
                    hijo[i][j] = disponibles[k]
                    k += 1
    return hijo


def seleccionar_mutacion(tipo_mutacion, hijo, fijos, prob_mut):
    """Devuelve un hijo mutado según la estrategia seleccionada."""
    if tipo_mutacion == "Intercambio":
        return mutacion_intercambio(hijo, fijos, prob_mut)
    elif tipo_mutacion == "Rotación":
        return mutacion_rotacion(hijo, fijos, prob_mut)
    elif tipo_mutacion == "Regeneración":
        return mutacion_regeneracion(hijo, fijos, prob_mut)
    else:
        # Por defecto
        return mutacion_intercambio(hijo, fijos, prob_mut)


def algoritmo_genetico(tablero_inicial, tam_poblacion, generaciones, prob_cruce, prob_mut, elitismo, tipo_cruce, evaluar, tipo_mutacion):
    """Ejecución del AG para obtener la solución al sudoku."""
    fijos = obtener_casillas_fijas(tablero_inicial)
    poblacion = crear_poblacion(tam_poblacion, tablero_inicial)

    for gen in range(generaciones):
        poblacion = sorted(poblacion, key=evaluar)

        if evaluar(poblacion[0]) == 0:
            return poblacion[0]

        num_elites = max(1, int(elitismo * tam_poblacion))
        nueva_gen = poblacion[:num_elites]

        while len(nueva_gen) < tam_poblacion:
            p1 = torneo(poblacion, evaluar)
            p2 = torneo(poblacion, evaluar)

            hijo = seleccionar_cruce(tipo_cruce, p1, p2, prob_cruce)
            hijo = seleccionar_mutacion(tipo_mutacion, hijo, fijos, prob_mut)


            nueva_gen.append(hijo)

        poblacion = nueva_gen

    return sorted(poblacion, key=evaluar)[0]

def validar_tablero(tablero):
    """Retorna matriz de booleanos para indicar error en posición."""
    errores = [[False] * 9 for _ in range(9)]
    for i in range(9):  # Verificación de fila
        nums = [n for n in tablero[i]]
        for j, valor in enumerate(tablero[i]):
            if nums.count(valor) > 1:
                errores[i][j] = True
    for j in range(9):  # Verificación de columna
        col = [tablero[i][j] for i in range(9)]
        for i in range(9):
            if col.count(tablero[i][j]) > 1:
                errores[i][j] = True
    return errores

# ==================================================
# INTERFAZ GRÁFICA
# ==================================================
def crear_interfaz():
    root = tk.Tk()
    root.title("Resolución de Sudoku - AG Mejorado")
    entries_tablero = []
    matriz_inicial = copy.deepcopy(TABLERO_EJEMPLO)

    # --------------------------------------------------
    # CONFIGURACIÓN DE ENTRADAS DE PARÁMETROS
    # --------------------------------------------------
    frame_param = tk.Frame(root, padx=10, pady=10)
    frame_param.grid(row=0, column=0, sticky="nw")

    labels = [
        ("Tamaño población:", "300"),
        ("Máximo de generaciones:", "1000"),
        ("Prob. de cruce:", "0.9"),
        ("Prob. de mutación:", "0.3"),
        ("Elitismo:", "0.1"),
    ]
    entries_param = []
    for i, (text, value) in enumerate(labels):
        lbl = tk.Label(frame_param, text=text)
        lbl.grid(row=i, column=0, sticky="e")
        entry = tk.Entry(frame_param, width=10)
        entry.insert(0, value)
        entry.grid(row=i, column=1, sticky="w")
        entries_param.append(entry)

    opciones = {
        "Método Selección:": ["Torneo", "Ruleta", "Ranking"],
        "Método Mutación:": ["Intercambio", "Rotación", "Regeneración"],
        "Método Cruce:": ["Filas", "PMX", "OX", "Alternado"],
        "Función de Adaptabilidad:": ["Simple", "Ponderada"]
    }

    comboboxes = []
    for i, (text, values) in enumerate(opciones.items()):
        lbl = tk.Label(frame_param, text=text)
        lbl.grid(row=len(labels) + i, column=0, sticky="e")  # Ahora sigue el nuevo orden
        cb = ttk.Combobox(frame_param, values=values, state="readonly")
        cb.current(0)
        cb.grid(row=len(labels) + i, column=1, sticky="w")
        comboboxes.append(cb)

    # --------------------------------------------------
    # TABLERO DE SUDOKU
    # --------------------------------------------------
    frame_tablero = tk.Frame(root, padx=10, pady=10)
    frame_tablero.grid(row=1, column=0)

    for i in range(9):
        fila_entries = []
        for j in range(9):
            entry = tk.Entry(frame_tablero, width=3, justify="center", font=("Arial", 12))
            entry.grid(row=i, column=j, padx=1, pady=1)
            entry.insert(0, str(TABLERO_EJEMPLO[i][j]))
            entry.config(state="readonly")  # Inicialmente solo lectura
            fila_entries.append(entry)
        entries_tablero.append(fila_entries)

    # --------------------------------------------------
    # BOTÓN DE EJECUTAR
    # --------------------------------------------------
    def on_ejecutar():
        """Se ejecuta al hacer clic en Ejecutar"""
        tam_poblacion = int(entries_param[0].get())
        max_gen = int(entries_param[1].get())
        prob_cruce = float(entries_param[2].get())
        prob_mut = float(entries_param[3].get())
        elitismo = float(entries_param[4].get())

        tipo_seleccion = comboboxes[0].get()
        tipo_mutacion = comboboxes[1].get()
        tipo_cruce = comboboxes[2].get()
        funcion_adaptabilidad = comboboxes[3].get()

        if funcion_adaptabilidad == "Simple":
            evaluar = evaluar_adaptabilidad_simple
        else:
            evaluar = evaluar_adaptabilidad

        resultado = algoritmo_genetico(TABLERO_EJEMPLO, tam_poblacion, max_gen, prob_cruce, prob_mut, elitismo,
                                       tipo_cruce, evaluar,tipo_mutacion)

        errores = validar_tablero(resultado)

        for i in range(9):
            for j in range(9):
                entries_tablero[i][j].config(state="normal")  # Habilita para cambiar
                entries_tablero[i][j].delete(0, "end")
                entries_tablero[i][j].insert(0, str(resultado[i][j]))
                if errores[i][j]:
                    entries_tablero[i][j].config(fg="red")  # Error
                else:
                    entries_tablero[i][j].config(fg="black")  # Correcto
                entries_tablero[i][j].config(state="readonly")  # Dejarlo solo lectura

    btn_ejecutar = tk.Button(root, text="Ejecutar", font=("Arial", 12, "bold"), command=on_ejecutar)
    btn_ejecutar.grid(row=2, column=0, pady=10)

    root.mainloop()

if __name__ == '__main__':
    crear_interfaz()
