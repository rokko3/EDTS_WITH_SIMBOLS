import sys
import Impresora
import analizador
import re

reglas = {}
tokens = {}

# Palabras clave de Python
KEYWORDS = {
    'False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await',
    'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except',
    'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is',
    'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return',
    'try', 'while', 'with', 'yield'
}

def reconocer_comentario(cadena, i):
    if cadena[i] == '#':
        inicio = i
        i += 1
        while i < len(cadena) and cadena[i] != '\n':
            i += 1
        return ["comentario", cadena[inicio:i], i]
    return None

def reconocer_string(cadena, i):
    if i >= len(cadena):
        return None
    
    # Strings triples
    if i + 2 < len(cadena):
        if cadena[i:i+3] in ('"""', "'''"):
            delimitador = cadena[i:i+3]
            inicio = i
            i += 3
            while i < len(cadena):
                if i + 2 < len(cadena) and cadena[i:i+3] == delimitador:
                    i += 3
                    return ["string", cadena[inicio:i], i]
                if cadena[i] == '\\' and i + 1 < len(cadena):
                    i += 2
                else:
                    i += 1
            raise ValueError(f"String sin cerrar en posición {inicio}")
    
    if cadena[i] in ('"', "'"):
        delimitador = cadena[i]
        inicio = i
        i += 1
        while i < len(cadena):
            if cadena[i] == delimitador:
                i += 1
                return ["string", cadena[inicio:i], i]
            if cadena[i] == '\\' and i + 1 < len(cadena):
                i += 2
            else:
                i += 1
        raise ValueError(f"String sin cerrar en posición {inicio}")
    
    return None

def reconocer_numero(cadena, i):
    if i >= len(cadena) or not (cadena[i].isdigit() or (cadena[i] == '0' and i + 1 < len(cadena))):
        return None
    
    inicio = i
    
    if cadena[i] == '0' and i + 1 < len(cadena):
        if cadena[i+1] in 'xX':
            i += 2
            while i < len(cadena) and cadena[i] in '0123456789abcdefABCDEF_':
                i += 1
            return ["hexadecimal", cadena[inicio:i], i]
        elif cadena[i+1] in 'oO':
            i += 2
            while i < len(cadena) and cadena[i] in '01234567_':
                i += 1
            return ["octal", cadena[inicio:i], i]
        elif cadena[i+1] in 'bB':
            i += 2
            while i < len(cadena) and cadena[i] in '01_':
                i += 1
            return ["binario", cadena[inicio:i], i]
    
    while i < len(cadena) and (cadena[i].isdigit() or cadena[i] == '_'):
        i += 1
    
    # Verificar parte decimal
    if i < len(cadena) and cadena[i] == '.':
        if i + 1 < len(cadena) and cadena[i+1].isdigit():
            i += 1
            while i < len(cadena) and (cadena[i].isdigit() or cadena[i] == '_'):
                i += 1
            # Notación científica
            if i < len(cadena) and cadena[i] in 'eE':
                i += 1
                if i < len(cadena) and cadena[i] in '+-':
                    i += 1
                while i < len(cadena) and cadena[i].isdigit():
                    i += 1
            return ["decimal", cadena[inicio:i], i]
    
    # Notación científica para enteros
    if i < len(cadena) and cadena[i] in 'eE':
        i += 1
        if i < len(cadena) and cadena[i] in '+-':
            i += 1
        while i < len(cadena) and cadena[i].isdigit():
            i += 1
        return ["decimal", cadena[inicio:i], i]
    
    return ["entero", cadena[inicio:i], i]

def reconocer_identificador_o_keyword(cadena, i):
    if i >= len(cadena) or not (cadena[i].isalpha() or cadena[i] == '_'):
        return None
    
    inicio = i
    while i < len(cadena) and (cadena[i].isalnum() or cadena[i] == '_'):
        i += 1
    
    lexema = cadena[inicio:i]
    
    if lexema in KEYWORDS:
        return ["keyword", lexema, i]
    else:
        return ["identificador", lexema, i]

def reconocer_operador_compuesto(cadena, i):
    if i >= len(cadena):
        return None
    
    # Operadores de 3 caracteres
    if i + 2 < len(cadena):
        op3 = cadena[i:i+3]
        if op3 in ('//=', '**=', '>>=', '<<='):
            return ["op_asignacion", op3, i+3]
    
    # Operadores de 2 caracteres
    if i + 1 < len(cadena):
        op2 = cadena[i:i+2]
        if op2 in ('==', '!=', '<=', '>=', '//', '**', '<<', '>>', '->'):
            return ["op_comparacion" if op2 in ('==', '!=', '<=', '>=') else "op_aritmetico", op2, i+2]
        elif op2 in ('+=', '-=', '*=', '/=', '%=', '&=', '|=', '^='):
            return ["op_asignacion", op2, i+2]
        elif op2 in ('and', 'or'):
            return ["op_logico", op2, i+2]
    
    return None

def reconocer_operador_simple(cadena, i):
    if i >= len(cadena):
        return None
    
    char = cadena[i]
    
    if char == '+':
        return ["opsuma", char, i+1]
    elif char == '-':
        return ["opresta", char, i+1]
    elif char == '*':
        return ["opmult", char, i+1]
    elif char == '/':
        return ["opdiv", char, i+1]
    elif char == '%':
        return ["opmodulo", char, i+1]
    elif char == '=':
        return ["op_asignacion", char, i+1]
    elif char in '<>':
        return ["op_comparacion", char, i+1]
    elif char in '&|^~':
        return ["op_bitwise", char, i+1]
    
    return None

def reconocer_delimitadores(cadena, i):
    if i >= len(cadena):
        return None
    
    char = cadena[i]
    
    delimitadores = {
        '(': 'parentesis_izq',
        ')': 'parentesis_der',
        '[': 'corchete_izq',
        ']': 'corchete_der',
        '{': 'llave_izq',
        '}': 'llave_der',
        ',': 'coma',
        ':': 'dos_puntos',
        ';': 'punto_coma',
        '.': 'punto',
        '@': 'arroba'
    }
    
    if char in delimitadores:
        return [delimitadores[char], char, i+1]
    
    return None

def reconocer_newline(cadena, i):
    if i < len(cadena) and cadena[i] == '\n':
        return ["newline", "\\n", i+1]
    return None

def lexer(cadena):
    i = 0
    lista_tokens = []
    
    # Lista de funciones reconocedoras en orden de prioridad
    reconocedores = [
        reconocer_comentario,
        reconocer_string,
        reconocer_numero,
        reconocer_identificador_o_keyword,
        reconocer_operador_compuesto,
        reconocer_operador_simple,
        reconocer_delimitadores,
        reconocer_newline,
    ]
    
    while i < len(cadena):
        # Ignorar espacios y tabs (pero no newlines)
        if cadena[i] in ' \t\r':
            i += 1
            continue
        
        reconocido = False
        for reconocedor in reconocedores:
            resultado = reconocedor(cadena, i)
            if resultado:
                tok, lexema, j = resultado
                lista_tokens.append((tok, lexema))
                i = j
                reconocido = True
                break
        
        if not reconocido:
            raise ValueError(f"Error léxico: carácter inesperado '{cadena[i]}' (ASCII {ord(cadena[i])}) en posición {i}")
    
    return lista_tokens
class ParserPredictivo:
    def __init__(self, tabla_prediccion, simbolo_inicial):
        self.tabla = tabla_prediccion
        self.simbolo_inicial = simbolo_inicial
        self.epsilon = 'ε'
        self.tokens = []
        self.pos = 0
        
    def parsear(self, tokens):
        self.tokens = tokens + [('$', '$')]
        self.pos = 0
        
        try:
            self.raiz = self._construir_arbol(self.simbolo_inicial)
            
            # Verificar que se consumieron todos los tokens
            if self.pos < len(self.tokens) - 1: 
                raise SyntaxError(f"Tokens adicionales no parseados: {self.tokens[self.pos:]}")
                
            return True, self.raiz
            
        except SyntaxError as e:
            return False, str(e)
    
    def _construir_arbol(self, simbolo):
        token_actual = self.tokens[self.pos][0] if self.pos < len(self.tokens) else '$'
        
        # Si es terminal
        if simbolo not in self.tabla:
            if simbolo == token_actual:
                # Crear nodo terminal
                valor_nodo = f"{simbolo}:{self.tokens[self.pos][1]}"
                nodo = Impresora.Nodo(valor_nodo)
                
                # ATRIBUTO SEMÁNTICO para terminales
                nodo.traduccion = self.tokens[self.pos][1]  # El lexema
                
                self.pos += 1
                return nodo
            else:
                raise SyntaxError(f"Error: se esperaba '{simbolo}', se encontró '{self.tokens[self.pos][1]}'")
        
        # Si es no terminal
        if token_actual in self.tabla[simbolo]:
            produccion = self.tabla[simbolo][token_actual]
            nodo = Impresora.Nodo(simbolo)
            
            if produccion != (self.epsilon,):
                hijos = []
                for s in produccion:
                    if s != self.epsilon:
                        hijo = self._construir_arbol(s)
                        hijos.append(hijo)
                        nodo.hijos.append(hijo)
                
                # ACCIONES SEMÁNTICAS según la producción
                self._aplicar_acciones_semanticas(nodo, simbolo, produccion, hijos)
            
            else:
                # Producción epsilon
                nodo.traduccion = ""
                
            return nodo
        else:
            esperados = list(self.tabla[simbolo].keys())
            raise SyntaxError(f"Error en {simbolo}: se esperaba {esperados}, se encontró '{token_actual}'")
    
    def _aplicar_acciones_semanticas(self, nodo, simbolo, produccion, hijos):

        if simbolo == "E":
            # E -> T E' 
            traduccion_t = hijos[0].traduccion
            traduccion_eprima = hijos[1].traduccion if len(hijos) > 1 else ""
            
            if traduccion_eprima == "":
                nodo.traduccion = traduccion_t
            else:
              
                nodo.traduccion = traduccion_eprima.replace("_", traduccion_t, 1)
        
        elif simbolo == "E'":
            if len(produccion) == 3 and produccion[0] == 'opsuma':
                # E' -> + T E'
                traduccion_t = hijos[1].traduccion
                traduccion_eprima1 = hijos[2].traduccion
                
                if traduccion_eprima1 == "":
                    # Solo hay una suma: suma(operando_izq, T)
                    nodo.traduccion = f"suma(_, {traduccion_t})"
                else:
                    # Hay más operaciones: suma(operando_izq, E')

                    parte_derecha = traduccion_eprima1.replace("_", traduccion_t, 1)
                    nodo.traduccion = f"suma(_, {parte_derecha})"
                
            elif len(produccion) == 3 and produccion[0] == 'opresta':
                # E' -> - T E'
                traduccion_t = hijos[1].traduccion
                traduccion_eprima1 = hijos[2].traduccion
                
                if traduccion_eprima1 == "":
                    # Solo hay una resta: resta(operando_izq, T)
                    nodo.traduccion = f"resta(_, {traduccion_t})"
                else:

                    parte_derecha = traduccion_eprima1.replace("_", traduccion_t, 1)
                    nodo.traduccion = f"resta(_, {parte_derecha})"
            else:
                # E' -> ε
                nodo.traduccion = ""
        
        elif simbolo == "T":
            # T -> F T' 
            traduccion_f = hijos[0].traduccion
            traduccion_tprima = hijos[1].traduccion if len(hijos) > 1 else ""
            
            if traduccion_tprima == "":
                nodo.traduccion = traduccion_f
            else:
                # T' ya trae la operación completa, reemplazamos el marcador
                nodo.traduccion = traduccion_tprima.replace("_", traduccion_f, 1)
        
        elif simbolo == "T'":
            if len(produccion) == 3 and produccion[0] == 'opmult':
                # T' -> * F T'
                traduccion_f = hijos[1].traduccion
                traduccion_tprima1 = hijos[2].traduccion
                
                if traduccion_tprima1 == "":
                    nodo.traduccion = f"mul(_, {traduccion_f})"
                else:
                    parte_derecha = traduccion_tprima1.replace("_", traduccion_f, 1)
                    nodo.traduccion = f"mul(_, {parte_derecha})"
                    
            elif len(produccion) == 3 and produccion[0] == 'opdiv':
                # T' -> / F T'
                traduccion_f = hijos[1].traduccion
                traduccion_tprima1 = hijos[2].traduccion
                
                if traduccion_tprima1 == "":
                    nodo.traduccion = f"div(_, {traduccion_f})"
                else:
                    parte_derecha = traduccion_tprima1.replace("_", traduccion_f, 1)
                    nodo.traduccion = f"div(_, {parte_derecha})"
            else:
                # T' -> ε
                nodo.traduccion = ""
        
        elif simbolo == "F":
            if produccion[0] == '(':
                # F -> ( E )
                nodo.traduccion = f"({hijos[1].traduccion})"
            else:
                # F -> entero | decimal
                nodo.traduccion = hijos[0].traduccion
        


def construir_tabla_prediccion(prediccion):
    tabla = {}
    
    for (nt, prod), tokens in prediccion.items():
        if nt not in tabla:
            tabla[nt] = {}
        
        for token in tokens:

            token_limpio = token.strip("'")

            if isinstance(prod, list):
                prod_tuple = tuple(prod)
            else:
                prod_tuple = prod
                
            tabla[nt][token_limpio] = prod_tuple
    
    return tabla

def tabla_simbolos(tokens,lexemas):
    tabla = {}
    for tok, lex in zip(tokens, lexemas):
        tabla[lex] = tok
    print("--- TABLA DE SIMBOLOS ---")
    i = 0
    for lex in tabla:
        i+=1
        print(f"[{i}]. {lex}: {tabla[lex]}")
def main():
    
    if len(sys.argv) != 3:
        print("Hace falta uno o mas archivos ")
        return
    

    nombre_archivo = sys.argv[1]
    cadena_prueba= sys.argv[2]

    gramatica,inicial=analizador.leer_gramatica(nombre_archivo)
    print(inicial)
    print("Gramática cargada de:", nombre_archivo)
    for nt in gramatica:
        print(nt, "->", [" ".join(p) for p in gramatica[nt]])
    
    primeros = analizador.calcular_primeros(gramatica)
    siguientes = analizador.calcular_siguientes(gramatica, inicial, primeros)
    pred=analizador.calcular_prediccion(gramatica, primeros, siguientes)
    
    tabla_prediccion = construir_tabla_prediccion(pred)
    parser = ParserPredictivo(tabla_prediccion, inicial)
    
    tokens_lexicos = lexer(cadena_prueba)

    print("\n--- ANALISIS SINTACTICO ---")
    exito, resultado = parser.parsear(tokens_lexicos)
    print(resultado)
    
    if exito:
        print("✓ Analisis sintactico EXITOSO")
        print("\n--- ARBOL DE ANALISIS ---")
        Impresora.imprimir_arbol(resultado)
        
        if hasattr(resultado, 'traduccion'):
            print(f"\n--- TRADUCCION ---")
            print(f"Resultado: {resultado.traduccion}")
    else:
        print("✗ Error sintáctico:", resultado)
        
    print("\n--- TOKENS LEXICOS ---")
    for tok, lexema in tokens_lexicos:
        print(f"{tok}: '{lexema}'")
    tabla_simbolos(*zip(*tokens_lexicos))
    print("\n--- PRIMEROS ---")
    for nt in primeros:
        print(f"PRIMEROS({nt}) = {primeros[nt]}")

    print("\n--- SIGUIENTES ---")
    for nt in siguientes:
        print(f"SIGUIENTES({nt}) = {siguientes[nt]}")
        

    print("\n--- TABLA DE PARSING ---")
    for nt in tabla_prediccion:
        for token, produccion in tabla_prediccion[nt].items():
            print(f"M[{nt}, {token}] = {produccion}")
    
if __name__ == "__main__":
    main()
    
    