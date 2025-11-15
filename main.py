import sys
import Impresora
import analizador
from tabla_simbolos import TablaSimbolos
from codigo_tres_direcciones import generar_tac_desde_traduccion

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
        self.tabla_simbolos = TablaSimbolos()  # Instancia de la tabla de símbolos
        self.linea_actual = 1
        self.columna_actual = 1
    
    def _inferir_tipo_expresion(self, nodo_expresion):
        if not nodo_expresion:
            return 'desconocido'
        
        # Buscar el primer terminal (literal) en la expresión
        def buscar_primer_literal(nodo):
            if not nodo:
                return 'desconocido'
            
            # Los nodos usan 'valor' para almacenar el símbolo
            simbolo_nodo = getattr(nodo, 'valor', None)
            
            # Si tiene produccion, verificar qué tipo de nodo es
            if hasattr(nodo, 'produccion'):
                # FACTOR puede tener directamente el literal
                if simbolo_nodo and 'FACTOR' in str(simbolo_nodo):
                    if len(nodo.produccion) == 1:
                        # FACTOR -> literal directo
                        tipo_literal = nodo.produccion[0]
                        if tipo_literal in ('hexadecimal', 'octal', 'binario', 'decimal', 'entero'):
                            return tipo_literal
            
            # Si es un nodo terminal (tiene valor pero no hijos o es lista vacía)
            if simbolo_nodo:
                if not hasattr(nodo, 'hijos') or not nodo.hijos:
                    # Terminal - extraer el tipo del valor (formato: "tipo:literal")
                    if ':' in str(simbolo_nodo):
                        tipo = str(simbolo_nodo).split(':')[0]
                        if tipo in ('hexadecimal', 'octal', 'binario', 'decimal', 'entero'):
                            return tipo
                        elif tipo == 'identificador':
                            # Buscar el tipo del identificador en la tabla de símbolos
                            if hasattr(nodo, 'traduccion') and nodo.traduccion:
                                simbolo = self.tabla_simbolos.buscar_simbolo(nodo.traduccion)
                                if simbolo and simbolo.tipo != 'desconocido':
                                    return simbolo.tipo
                            return 'identificador'
            
            # Buscar recursivamente en los hijos
            if hasattr(nodo, 'hijos') and nodo.hijos:
                tipo_id_encontrado = None
                for hijo in nodo.hijos:
                    resultado = buscar_primer_literal(hijo)
                    if resultado not in ('desconocido',):
                        if resultado != 'identificador':
                            return resultado
                        else:
                            tipo_id_encontrado = 'identificador'
                # Si solo encontramos identificadores, devolver 'identificador'
                if tipo_id_encontrado:
                    return tipo_id_encontrado
            
            return 'desconocido'
        
        return buscar_primer_literal(nodo_expresion)
        
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
        
        # Para keywords, usar el lexema en lugar del tipo
        if token_actual == 'keyword':
            token_actual = self.tokens[self.pos][1]
        
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
        
        
        if simbolo == "PROGRAMA":
            # PROGRAMA -> SENTENCIAS
            if len(hijos) >= 1:
                nodo.traduccion = hijos[0].traduccion if hasattr(hijos[0], 'traduccion') else ""
        
        elif simbolo == "SENTENCIA":
            # SENTENCIA puede tener diferentes formas
            if len(produccion) == 2 and produccion[0] == 'identificador':
                # SENTENCIA -> identificador SENTENCIA_ID
                id_name = hijos[0].traduccion if hasattr(hijos[0], 'traduccion') else ""
                id_token_tipo = hijos[0].simbolo if hasattr(hijos[0], 'simbolo') else 'identificador'
                sentencia_id = hijos[1] if len(hijos) > 1 else None
                
                if sentencia_id and hasattr(sentencia_id, 'es_asignacion') and sentencia_id.es_asignacion:
                    # Es una asignación
                    op = sentencia_id.operador
                    expr = sentencia_id.expresion
                    
                    # Inferir tipo de la expresión
                    nodo_expr = sentencia_id.nodo_expresion if hasattr(sentencia_id, 'nodo_expresion') else None
                    tipo_inferido = self._inferir_tipo_expresion(nodo_expr)
                    
                    # AGREGAR A TABLA DE SÍMBOLOS
                    simbolo_existente = self.tabla_simbolos.buscar_simbolo(id_name)
                    if simbolo_existente:
                        self.tabla_simbolos.actualizar_simbolo(id_name, valor=expr, tipo=tipo_inferido)
                    else:
                        self.tabla_simbolos.agregar_simbolo(
                            nombre=id_name,
                            tipo=tipo_inferido,
                            valor=expr,
                            linea=self.linea_actual,
                            columna=self.columna_actual
                        )
                    
                    nodo.traduccion = f"{id_name} {op} {expr}"
                else:
                    # Es una expresión
                    resto = sentencia_id.traduccion if sentencia_id and hasattr(sentencia_id, 'traduccion') else ""
                    if resto and resto.startswith("_"):
                        nodo.traduccion = resto.replace("_", id_name, 1)
                    else:
                        nodo.traduccion = f"{id_name}{resto}"
            elif len(produccion) == 2 and produccion[0] in ('entero', 'decimal', 'hexadecimal', 'octal', 'binario'):
                # SENTENCIA -> numero EXPRESION_REST
                num = hijos[0].traduccion if hasattr(hijos[0], 'traduccion') else ""
                rest = hijos[1].traduccion if len(hijos) > 1 and hasattr(hijos[1], 'traduccion') else ""
                if rest and rest.startswith("_"):
                    nodo.traduccion = rest.replace("_", num, 1)
                else:
                    nodo.traduccion = f"{num}{rest}"
            elif produccion == ('parentesis_izq', 'EXPRESION', 'parentesis_der', 'EXPR_PRIMA'):
                # SENTENCIA -> parentesis_izq EXPRESION parentesis_der EXPR_PRIMA
                expr = hijos[1].traduccion if len(hijos) > 1 and hasattr(hijos[1], 'traduccion') else ""
                expr_prima = hijos[3].traduccion if len(hijos) > 3 and hasattr(hijos[3], 'traduccion') else ""
                if expr_prima:
                    nodo.traduccion = expr_prima.replace("_", f"({expr})", 1)
                else:
                    nodo.traduccion = f"({expr})"
            elif len(produccion) == 4 and produccion[0] in ('opsuma', 'opresta'):
                # SENTENCIA -> opsuma/opresta FACTOR TERMINO_PRIMA EXPR_PRIMA
                op = hijos[0].traduccion if hasattr(hijos[0], 'traduccion') else ""
                factor = hijos[1].traduccion if len(hijos) > 1 and hasattr(hijos[1], 'traduccion') else ""
                termino_prima = hijos[2].traduccion if len(hijos) > 2 and hasattr(hijos[2], 'traduccion') else ""
                expr_prima = hijos[3].traduccion if len(hijos) > 3 and hasattr(hijos[3], 'traduccion') else ""
                
                result = f"{op}{factor}"
                if termino_prima:
                    result = termino_prima.replace("_", result, 1)
                if expr_prima:
                    result = expr_prima.replace("_", result, 1)
                nodo.traduccion = result
            elif len(hijos) > 0:
                nodo.traduccion = hijos[0].traduccion if hasattr(hijos[0], 'traduccion') else ""
        
        elif simbolo == "SENTENCIA_ID":
            # SENTENCIA_ID -> op_asignacion EXPRESION (asignación)
            # SENTENCIA_ID -> EXPRESION_REST (expresión)
            if len(produccion) > 0 and produccion[0] == 'op_asignacion':
                # Es una asignación
                op = hijos[0].traduccion if hasattr(hijos[0], 'traduccion') else "="
                expr = hijos[1].traduccion if len(hijos) > 1 and hasattr(hijos[1], 'traduccion') else ""
                
                # Guardar temporalmente para que el padre lo use
                nodo.es_asignacion = True
                nodo.operador = op
                nodo.expresion = expr
                nodo.nodo_expresion = hijos[1] if len(hijos) > 1 else None  # Guardar nodo para inferir tipo
                nodo.traduccion = f"{op} {expr}"
            else:
                # Es una expresión
                rest = hijos[0].traduccion if hasattr(hijos[0], 'traduccion') else ""
                nodo.traduccion = rest
        
        elif simbolo == "EXPRESION_REST":
            # EXPRESION_REST -> TERMINO_PRIMA EXPR_PRIMA
            termino_p = hijos[0].traduccion if hasattr(hijos[0], 'traduccion') else ""
            expr_p = hijos[1].traduccion if len(hijos) > 1 and hasattr(hijos[1], 'traduccion') else ""
            
            result = "_"
            if termino_p:
                result = termino_p.replace("_", result, 1)
            if expr_p:
                result = expr_p.replace("_", result, 1)
            nodo.traduccion = result
        
        elif simbolo == "EXPRESION":
            # EXPRESION -> TERMINO EXPR_PRIMA
            termino = hijos[0].traduccion if hasattr(hijos[0], 'traduccion') else ""
            expr_prima = hijos[1].traduccion if len(hijos) > 1 and hasattr(hijos[1], 'traduccion') else ""
            
            if expr_prima == "":
                nodo.traduccion = termino
            else:
                # Reemplazar marcador _ con el término izquierdo
                nodo.traduccion = expr_prima.replace("_", termino, 1)
        
        elif simbolo == "EXPR_PRIMA":
            if len(produccion) > 1 and produccion[0] != 'ε':
                # EXPR_PRIMA -> + TERMINO EXPR_PRIMA | - TERMINO EXPR_PRIMA
                operador = hijos[0].traduccion if hasattr(hijos[0], 'traduccion') else ""
                termino = hijos[1].traduccion if len(hijos) > 1 and hasattr(hijos[1], 'traduccion') else ""
                expr_prima = hijos[2].traduccion if len(hijos) > 2 and hasattr(hijos[2], 'traduccion') else ""
                
                if expr_prima == "":
                    nodo.traduccion = f"_ {operador} {termino}"
                else:
                    # Construir expresión anidada
                    parte_derecha = expr_prima.replace("_", termino, 1)
                    nodo.traduccion = f"_ {operador} {parte_derecha}"
            else:
                nodo.traduccion = ""
        
        elif simbolo == "SENTENCIAS":
            if len(produccion) > 1 and produccion[0] != 'ε':
                # SENTENCIAS -> SENTENCIA SENTENCIAS_PRIMA
                sent = hijos[0].traduccion if hasattr(hijos[0], 'traduccion') else ""
                sents_prima = hijos[1].traduccion if len(hijos) > 1 and hasattr(hijos[1], 'traduccion') else ""
                if sents_prima:
                    nodo.traduccion = f"{sent}\n{sents_prima}"
                else:
                    nodo.traduccion = sent
            else:
                nodo.traduccion = ""
        
        elif simbolo == "SENTENCIAS_PRIMA":
            if len(produccion) > 1 and produccion[0] != 'ε':
                # SENTENCIAS_PRIMA -> newline SENTENCIAS
                sents = hijos[1].traduccion if len(hijos) > 1 and hasattr(hijos[1], 'traduccion') else ""
                nodo.traduccion = sents
            else:
                nodo.traduccion = ""
        
        elif simbolo == "TERMINO":
            # TERMINO -> FACTOR TERMINO_PRIMA
            factor = hijos[0].traduccion if hasattr(hijos[0], 'traduccion') else None
            termino_prima = hijos[1].traduccion if len(hijos) > 1 and hasattr(hijos[1], 'traduccion') else None
            
            # Asegurarse de que no sean None
            if factor is None:
                factor = ""
            if termino_prima is None:
                termino_prima = ""
            
            if termino_prima == "":
                nodo.traduccion = factor
            else:
                nodo.traduccion = termino_prima.replace("_", factor, 1)
        
        elif simbolo == "TERMINO_PRIMA":
            if len(produccion) > 1 and produccion[0] != 'ε':
                # TERMINO_PRIMA -> * FACTOR TERMINO_PRIMA | / FACTOR TERMINO_PRIMA
                operador = hijos[0].traduccion if hasattr(hijos[0], 'traduccion') else ""
                factor = hijos[1].traduccion if len(hijos) > 1 and hasattr(hijos[1], 'traduccion') else ""
                termino_prima = hijos[2].traduccion if len(hijos) > 2 and hasattr(hijos[2], 'traduccion') else ""
                
                if termino_prima == "":
                    nodo.traduccion = f"_ {operador} {factor}"
                else:
                    parte_derecha = termino_prima.replace("_", factor, 1)
                    nodo.traduccion = f"_ {operador} {parte_derecha}"
            else:
                nodo.traduccion = ""
        
        elif simbolo == "FACTOR":
            if len(produccion) == 1:
                # FACTOR -> entero | decimal | binario | identificador
                nodo.traduccion = hijos[0].traduccion if hasattr(hijos[0], 'traduccion') else ""
            elif len(produccion) == 3 and produccion[0] == 'parentesis_izq':
                # FACTOR -> parentesis_izq EXPRESION parentesis_der
                expr = hijos[1].traduccion if len(hijos) > 1 and hasattr(hijos[1], 'traduccion') else ""
                nodo.traduccion = f"({expr})"
        
        else:
            # Por defecto, propagar la traducción del primer hijo
            if len(hijos) > 0 and hasattr(hijos[0], 'traduccion'):
                nodo.traduccion = hijos[0].traduccion
            else:
                nodo.traduccion = ""

        


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

def main():
    
    if len(sys.argv) != 3:
        print("Hace falta uno o mas archivos ")
        return
    

    nombre_archivo = sys.argv[1]
    cadena_prueba= sys.argv[2]
    with open(cadena_prueba, 'r', encoding='utf-8') as f:
        cadena_prueba = f.read()
        tokens_lexicos = lexer(cadena_prueba)
        

    gramatica,inicial=analizador.leer_gramatica(nombre_archivo)
    print(inicial)
    print("Gramática cargada de:", nombre_archivo)
    # for nt in gramatica:
    #     print(nt, "->", [" ".join(p) for p in gramatica[nt]])
    
    primeros = analizador.calcular_primeros(gramatica)
    siguientes = analizador.calcular_siguientes(gramatica, inicial, primeros)
    pred=analizador.calcular_prediccion(gramatica, primeros, siguientes)
    
    tabla_prediccion = construir_tabla_prediccion(pred)
    parser = ParserPredictivo(tabla_prediccion, inicial)
    
    

    print("\n--- ANALISIS SINTACTICO ---")
    exito, resultado = parser.parsear(tokens_lexicos)
    print(resultado)
    
    if exito:
        print("Analisis sintactico EXITOSO")
        print("\n--- ARBOL DE ANALISIS ---")
        Impresora.imprimir_arbol(resultado)
        
        if hasattr(resultado, 'traduccion'):
            print(f"\n--- TRADUCCION ---")
            print(f"Resultado: {resultado.traduccion}")
        
        
        print("\n Codigo de tres direcciones:")
        generador_tac = generar_tac_desde_traduccion(resultado.traduccion)
        generador_tac.imprimir_codigo()
        
       
        parser.tabla_simbolos.imprimir_tabla()
    else:
        print("[ERROR] Error sintactico:", resultado)
        
    print("\n--- TOKENS LEXICOS ---")
    for tok, lexema in tokens_lexicos:
        print(f"{tok}: '{lexema}'")
    #tabla_simbolos(*zip(*tokens_lexicos))
    """
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
    """
    
if __name__ == "__main__":
    main()
    
    