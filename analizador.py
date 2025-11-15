
import sys
from collections import defaultdict


def leer_gramatica(nombre_archivo):
    gramatica = defaultdict(list)
    simbolo_inicial = None
    with open(nombre_archivo, "r", encoding="utf-8") as f:
        for linea in f:
            if not linea.strip():
                continue
            izquierda, derecha = linea.split("->")
            izquierda = izquierda.strip()
            if simbolo_inicial is None:
                simbolo_inicial = izquierda
            alternativas = derecha.split("|")
            for alt in alternativas:
                gramatica[izquierda].append(alt.strip().split())
    return gramatica, simbolo_inicial

def calcular_primeros(gramatica):
    primeros = defaultdict(set)

    # Inicialización: los terminales producen a sí mismos
    for nt in gramatica:
        for prod in gramatica[nt]:
            for simbolo in prod:
                if simbolo not in gramatica and simbolo != "ε":
                    primeros[simbolo].add(simbolo)

    cambiado = True
    while cambiado:
        cambiado = False
        for nt in gramatica:
            for prod in gramatica[nt]:
                puede_vacio = True
                for simbolo in prod:
                    if simbolo not in gramatica:
                        antes = len(primeros[nt])
                        primeros[nt].add(simbolo)
                        if len(primeros[nt]) > antes:
                            cambiado = True
                        puede_vacio = False
                        break
                    else:
                        antes = len(primeros[nt])
                        primeros[nt] |= (primeros[simbolo] - {"ε"})
                        if len(primeros[nt]) > antes:
                            cambiado = True
                        if "ε" not in primeros[simbolo]:
                            puede_vacio = False
                            break
                if puede_vacio:
                    if "ε" not in primeros[nt]:
                        primeros[nt].add("ε")
                        cambiado = True
    return primeros

def calcular_siguientes(gramatica, inicial, primeros):
    siguientes = defaultdict(set)
    siguientes[inicial].add("$") 

    cambiado = True
    while cambiado:
        cambiado = False
        for nt in gramatica:
            for prod in gramatica[nt]:
                for i, simbolo in enumerate(prod):
                    if simbolo in gramatica:  
                        beta = prod[i+1:]
                        if beta:
                        
                            primeros_beta = set()
                            vacio = True
                            for b in beta:
                                primeros_beta |= (primeros[b] if b in primeros else {b})
                                if "ε" not in primeros[b]:
                                    vacio = False
                                    break
                            if vacio:
                                antes = len(siguientes[simbolo])
                                siguientes[simbolo] |= siguientes[nt]
                                if len(siguientes[simbolo]) > antes:
                                    cambiado = True
                            antes = len(siguientes[simbolo])
                            siguientes[simbolo] |= (primeros_beta - {"ε"})
                            if len(siguientes[simbolo]) > antes:
                                cambiado = True
                        else:
                            antes = len(siguientes[simbolo])
                            siguientes[simbolo] |= siguientes[nt]
                            if len(siguientes[simbolo]) > antes:
                                cambiado = True
    return siguientes

def calcular_prediccion(gramatica, primeros, siguientes):
    pred = {}
    for nt in gramatica:
        for prod in gramatica[nt]:
            conjunto = set()
            vacio = True
            for s in prod:
                conjunto |= (primeros[s] if s in primeros else {s})
                if "ε" not in (primeros[s] if s in primeros else {s}):
                    vacio = False
                    break
            if vacio:
                conjunto |= siguientes[nt]
            conjunto.discard("ε")
            pred[(nt, tuple(prod))] = conjunto
    return pred

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python analizador.py gramatica.txt")
        sys.exit(1)

    archivo = sys.argv[1]
    gramatica, inicial = leer_gramatica(archivo)

    print("Gramática cargada de:", archivo)
    for nt in gramatica:
        print(nt, "->", [" ".join(p) for p in gramatica[nt]])

    primeros = calcular_primeros(gramatica)
    siguientes = calcular_siguientes(gramatica, inicial, primeros)
    pred = calcular_prediccion(gramatica, primeros, siguientes)

    print("\n--- PRIMEROS ---")
    for nt in primeros:
        print(f"PRIMEROS({nt}) = {primeros[nt]}")

    print("\n--- SIGUIENTES ---")
    for nt in siguientes:
        print(f"SIGUIENTES({nt}) = {siguientes[nt]}")

    print("\n--- PREDICCIÓN ---")
    for (nt, prod), conj in pred.items():
        print(f"PRED({nt} -> {' '.join(prod)}) = {conj}")

