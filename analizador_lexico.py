# Configuración de tokens
SIMBOLOS = {
    '**=': 'tk_potencia_asig',
    '//=': 'tk_div_entera_asig',
    '+=': 'tk_mas_asig',
    '-=': 'tk_menos_asig',
    '*=': 'tk_mult_asig',
    '/=': 'tk_div_asig',
    '%=': 'tk_mod_asig',
    '==': 'tk_igual',
    '!=': 'tk_distinto',
    '>=': 'tk_mayor_igual',
    '<=': 'tk_menor_igual',
    '**': 'tk_potencia',
    '//': 'tk_div_entera',
    '(': 'tk_par_izq',
    ')': 'tk_par_der',
    '[': 'tk_corchete_izq',
    ']': 'tk_corchete_der',
    '{': 'tk_llave_izq',
    '}': 'tk_llave_der',
    ':': 'tk_dos_puntos',
    ',': 'tk_coma',
    '=': 'tk_asig',
    '>': 'tk_mayor',
    '<': 'tk_menor',
    '+': 'tk_suma',
    '-': 'tk_resta',
    '*': 'tk_mult',
    '/': 'tk_div',
    '%': 'tk_modulo',
    '.': 'tk_punto'
}

PALABRAS_RESERVADAS = {
    'False', 'None', 'True', 'and', 'as', 'break', 'class', 'continue',
    'def', 'del', 'elif', 'else', 'except', 'finally', 'for', 'from',
    'if', 'import', 'in', 'is', 'not', 'or', 'pass', 'return', 'try',
    'while', 'print', 'self','raise'
}

tipos_datos = {'int', 'float', 'str', 'bool', 'list', 'tuple', 'dict', 'set'}


# Clase Token
class Token:
    def __init__(self, tipo, valor=None, fila=0, columna=0):
        self.tipo = tipo
        self.valor = valor
        self.fila = fila
        self.columna = columna

    def __repr__(self):
        return f"Token({self.tipo}, {self.valor}, {self.fila}, {self.columna})"


# Analizador Léxico
def analizador_lexico(codigo):
    """Analiza el código y genera tokens"""
    tokens = []
    lineas = codigo.split("\n")
    pila_indentacion = [0]
    dentro_comentario_multilinea = False
    delimitador_comentario = None
    
    for num_linea, linea_original in enumerate(lineas, start=1):
        # Verificar si estamos dentro de un comentario multilínea
        if dentro_comentario_multilinea:
            # Buscar el cierre del comentario
            if delimitador_comentario in linea_original:
                dentro_comentario_multilinea = False
                delimitador_comentario = None
            continue
        
        # Contar espacios al inicio (solo espacios, no tabs)
        nivel_espacios = 0
        while nivel_espacios < len(linea_original) and linea_original[nivel_espacios] == ' ':
            nivel_espacios += 1
        
        contenido_limpio = linea_original.strip()
        
        # Saltar líneas vacías y comentarios completos
        if not contenido_limpio or contenido_limpio.startswith('#'):
            continue
        
        # Detectar inicio de comentario multilínea
        if contenido_limpio.startswith('"""') or contenido_limpio.startswith("'''"):
            delimitador_comentario = contenido_limpio[:3]
            # Verificar si cierra en la misma línea
            if contenido_limpio.count(delimitador_comentario) >= 2 and len(contenido_limpio) > 3:
                # Comentario completo en una línea, ignorar
                continue
            else:
                # Comentario multilínea, marcar como dentro
                dentro_comentario_multilinea = True
                continue
        
        # Obtener nivel actual de indentación
        nivel_previo = pila_indentacion[-1]
        
        # Manejar cambios de indentación ANTES de procesar tokens
        if nivel_espacios > nivel_previo:
            pila_indentacion.append(nivel_espacios)
            tokens.append(Token("TAB", None, num_linea, 1))
        elif nivel_espacios < nivel_previo:
            while pila_indentacion and nivel_espacios < pila_indentacion[-1]:
                pila_indentacion.pop()
                tokens.append(Token("TABend", None, num_linea, 1))
            
            # Verificar indentación incorrecta
            if pila_indentacion and nivel_espacios != pila_indentacion[-1]:
                raise Exception(f"<{num_linea},{nivel_espacios + 1}> Error sintactico: falla de indentacion")
        
        # Tokenizar el contenido de la línea
        tokens_contenido = procesar_contenido(contenido_limpio, num_linea)
        if tokens_contenido is None:
            return None
        
        tokens.extend(tokens_contenido)
        
        # Determinar si agregar NEWLINE
        # NO agregar si la línea termina en: : , ( [ {
        ultima_palabra = linea_original.rstrip()
        if ultima_palabra and not ultima_palabra.endswith((':', ',', '(', '[', '{')):
            tokens.append(Token("NEWLINE", None, num_linea, len(linea_original)))
    
    # Cerrar todas las indentaciones pendientes
    while len(pila_indentacion) > 1:
        pila_indentacion.pop()
        tokens.append(Token("TABend", None, len(lineas) + 1, 1))
    
    # Agregar marcador de fin
    tokens.append(Token("ENDMARKER", "$", len(lineas) + 1, 0))
    return tokens


def procesar_contenido(linea, num_linea):
    """Tokeniza el contenido de una línea"""
    tokens = []
    posicion = 0
    
    while posicion < len(linea):
        caracter = linea[posicion]
        
        # Saltar espacios en blanco
        if caracter.isspace():
            posicion += 1
            continue
        
        # Comentarios en línea
        if caracter == '#':
            break
        
        # Identificadores y palabras reservadas
        if caracter.isalpha() or caracter == '_':
            inicio = posicion
            while posicion < len(linea) and (linea[posicion].isalnum() or linea[posicion] == '_'):
                posicion += 1
            
            palabra = linea[inicio:posicion]
            
            if palabra in PALABRAS_RESERVADAS:
                tokens.append(Token(palabra, palabra, num_linea, inicio + 1))
            else:
                tokens.append(Token("id", palabra, num_linea, inicio + 1))
            continue
        
        # Números enteros y decimales
        if caracter.isdigit():
            inicio = posicion
            while posicion < len(linea) and linea[posicion].isdigit():
                posicion += 1
            
            # Verificar si hay punto decimal
            tiene_decimal = False
            if posicion < len(linea) and linea[posicion] == '.':
                if posicion + 1 < len(linea) and linea[posicion + 1].isdigit():
                    tiene_decimal = True
                    posicion += 1
                    while posicion < len(linea) and linea[posicion].isdigit():
                        posicion += 1
            
            numero = linea[inicio:posicion]
            tokens.append(Token("tk_entero", numero, num_linea, inicio + 1))
            continue
        
        # Cadenas de texto
        if caracter in ['"', "'"]:
            comilla_tipo = caracter
            inicio = posicion
            posicion += 1
            
            while posicion < len(linea) and linea[posicion] != comilla_tipo:
                if linea[posicion] == '\\' and posicion + 1 < len(linea):
                    posicion += 2
                else:
                    posicion += 1
            
            if posicion >= len(linea):
                print(f"<{num_linea},{inicio + 1}> Error lexico: cadena sin cerrar")
                return None
            
            texto = linea[inicio + 1:posicion]
            tokens.append(Token("tk_cadena", texto, num_linea, inicio + 1))
            posicion += 1
            continue
        
        # Operadores y símbolos (probar de más largo a más corto)
        simbolo_encontrado = False
        for longitud in [3, 2, 1]:
            if posicion + longitud <= len(linea):
                fragmento = linea[posicion:posicion + longitud]
                if fragmento in SIMBOLOS:
                    tokens.append(Token(SIMBOLOS[fragmento], fragmento, num_linea, posicion + 1))
                    posicion += longitud
                    simbolo_encontrado = True
                    break
        
        if simbolo_encontrado:
            continue
        
        # Carácter no reconocido
        print(f"<{num_linea},{posicion + 1}> Error lexico: caracter inesperado '{caracter}'")
        return None
    
    return tokens