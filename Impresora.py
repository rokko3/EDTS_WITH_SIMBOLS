class Nodo:
    def __init__(self, valor, hijos=None):
        self.valor = valor
        self.hijos = hijos if hijos is not None else []
        self.traduccion = None  # Atributo semántico para traducción


def mostrar_arbol(nodo):
    if nodo is None:
        return [""], 0, 0 

    caja = cuadrado_con_semantica(nodo)
    ancho = len(caja[0])

    if not nodo.hijos:  # nodo sin hijos
        return caja, ancho // 2, ancho

    # Dibujar hijos recursivamente
    hijos_lineas = []
    posiciones = []
    anchos = []

    for hijo in nodo.hijos:
        lineas, pos, an = mostrar_arbol(hijo)
        hijos_lineas.append(lineas)
        posiciones.append(pos)
        anchos.append(an)

    # igualar alturas de cada nodo, compara la altura de cada nodo con todos los demas 
    # añade espacios en blanco 

    altura = max(len(h) for h in hijos_lineas)
    for i, h in enumerate(hijos_lineas):
        hijos_lineas[i] = h + [" " * anchos[i]] * (altura - len(h)) # Rellena con espacios en blanco
    
    # ancho total de los hijos
    total_ancho = sum(anchos) + len(anchos) - 1

    # centrar padre respecto a los hijos
    pos_padre = total_ancho // 2 - ancho // 2
    arriba = " " * pos_padre + caja[0] + " " * (total_ancho - pos_padre - ancho)
    medio = " " * pos_padre + caja[1] + " " * (total_ancho - pos_padre - ancho)
    abajo = " " * pos_padre + caja[2] + " " * (total_ancho - pos_padre - ancho)

    # Dibujar ramas diagonales
    rama_linea = [" "] * total_ancho
    inicio = 0
    # recorremos los anchos de los hijos
    for i, an in enumerate(anchos):
        centro_hijo = inicio + posiciones[i]
        centro_padre = pos_padre + ancho // 2
        if centro_hijo < centro_padre: # Si esta a la izquierda del nodo padre
            rama_linea[centro_hijo] = "/" 
        elif centro_hijo > centro_padre: # si esta a la derecha del nodo padre
            rama_linea[centro_hijo] = "\\"
        else:
            rama_linea[centro_hijo] = "|" # si esta abajo del nodo padre
        inicio += an + 1
    rama_linea = "".join(rama_linea) # Concatenamos todos los / y \

    resultado = [arriba, medio, abajo, rama_linea]

    # el metodo zip agrupa los elementos de igual indice en una lista, concatena todo en una linea
    # Usamos * para recorrer cada lista dentro de la lista de hijos_lineas
    for fila in zip(*hijos_lineas): 
        
        resultado.append(" ".join(fila))
        
    # Devuelve una lista de  stings (resultado) que son las lineas a imprimir
    # Devuelve la posicion desde la izquierda del nodo padre hasta que empieza a imprimir
    # Mas el ancho del nodo entre dos y el ancho total (todos los hijos)
    return resultado, pos_padre + ancho // 2, total_ancho


def imprimir_arbol(nodo):
    # Cogemos la lista de strings que devuelve el metodo mostrar arbol, y descartamos los otros valores con
    # *_
    lineas, *_ = mostrar_arbol(nodo)
    for linea in lineas: # Recorremos las lineas y las imprimimos
        print(linea) 


def cuadrado(texto):
    """Versión más compacta para nodos"""
    # Limitar el texto a un máximo de 15 caracteres
    if len(texto) > 15:
        texto = texto[:12] + "..."
    
    ancho = len(texto) + 2
    arriba = "*-" + "-" * len(texto) + "-*"
    medio = "| " + texto + " |"
    return [arriba, medio, arriba]

def cuadrado_con_semantica(nodo):
    """Versión compacta que muestra valor y traducción"""
    texto_principal = nodo.valor.split(':')[0]  # Solo el tipo, no el lexema
    
    # Agregar traducción si existe y es corta
    if hasattr(nodo, 'traduccion') and nodo.traduccion is not None:
        trad = nodo.traduccion
        if len(trad) > 10:
            trad = trad[:8] + ".."
        texto = f"{texto_principal}→{trad}"
    else:
        texto = texto_principal
    
    return cuadrado(texto)
