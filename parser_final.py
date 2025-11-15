import sys
from analizador_lexico import SIMBOLOS


class ParserLL1Completo:
    def __init__(self):
        self.gramatica = self._definir_gramatica()
        
        # Conjuntos calculados
        self.first = {}
        self.follow = {}
        self.tabla_parsing = {}
        
        # Símbolos especiales
        self.epsilon = 'ε'
        self.endmarker = 'ENDMARKER'
        
        self.tokens = []
        self.pos = 0
        self.token_actual = None
        self.errores = []
        
        # Mapeo de tokens a símbolos legibles para mensajes de error
        self.TOKEN_A_SIMBOLO = self._crear_mapeo_tokens()
        
    def _crear_mapeo_tokens(self):
        """Crea un mapeo de tipos de token a símbolos legibles para el usuario"""
        # Invertir SIMBOLOS para obtener token -> símbolo
        mapeo = {v: k for k, v in SIMBOLOS.items()}
        
        # Agregar tokens especiales y palabras reservadas
        mapeo.update({
            'NEWLINE': 'nueva línea',
            'ENDMARKER': 'fin de archivo',
            'TAB': 'indentación',
            'TABend': 'dedentación',
            'id': 'identificador',
            'tk_entero': 'número',
            'tk_cadena': 'cadena',
            # Palabras reservadas
            'if': 'if', 'elif': 'elif', 'else': 'else',
            'while': 'while', 'for': 'for', 'def': 'def',
            'class': 'class', 'return': 'return', 'break': 'break',
            'continue': 'continue', 'pass': 'pass', 'del': 'del',
            'import': 'import', 'from': 'from', 'as': 'as',
            'try': 'try', 'except': 'except', 'finally': 'finally',
            'in': 'in', 'is': 'is', 'and': 'and', 'or': 'or',
            'not': 'not', 'True': 'True', 'False': 'False',
            'None': 'None', 'self': 'self', 'print': 'print'
        })
        
        return mapeo
        
    def _definir_gramatica(self):
        return {
            # Programa principal
            'programa': [
                ['declaraciones']
            ],
            
            'declaraciones': [
                ['declaracion', 'declaraciones'],
                ['ε']
            ],
            
            'declaracion': [
                ['sentencia', 'NEWLINE'],
                ['sentencia_compuesta'],
                ['def_stmt'],
                ['class_stmt'],
                ['NEWLINE']
            ],
            
            # Sentencias simples
            'sentencia': [
                ['raise_stmt'],
                ['id', 'sentencia_id'],
                ['self', 'sentencia_self'],
                ['return_stmt'],
                ['break'],
                ['continue'],
                ['pass'],
                ['del_stmt'],
                ['import_stmt'],
                ['print_stmt']
            ],
            'raise_stmt': [
                ['raise', 'raise_excepcion']
            ],
            'raise_excepcion': [
                ['expresion', 'raise_from'],  
                ['ε'] 
            ],

            'raise_from': [
                ['from', 'expresion'],  # raise Exception from cause
                ['ε']  # solo raise Exception
            ],
            
            'sentencia_id': [
                ['op_asignacion', 'expresion'],
                ['tk_corchete_izq', 'expresion', 'tk_corchete_der', 'asignacion_indexada'],
                ['tk_par_izq', 'args_opt', 'tk_par_der'],
                ['tk_punto', 'id', 'sentencia_id_dot']
            ],
            
            'asignacion_indexada': [
                ['tk_asig', 'expresion'],
                ['ε']
            ],
            
            'sentencia_self': [
                ['tk_punto', 'id', 'sentencia_id_dot'],
                ['tk_par_izq', 'args_opt', 'tk_par_der']
            ],
            
            'sentencia_id_dot': [
                ['op_asignacion', 'expresion'],
                ['tk_corchete_izq', 'expresion', 'tk_corchete_der', 'asignacion_indexada'],
                ['tk_par_izq', 'args_opt', 'tk_par_der'],
                ['tk_punto', 'id', 'sentencia_id_dot'],
                ['ε']
            ],
            
            'op_asignacion': [
                ['tk_asig'],
                ['tk_mas_asig'],
                ['tk_menos_asig'],
                ['tk_mult_asig'],
                ['tk_div_asig'],
                ['tk_mod_asig']
            ],
            
            'return_stmt': [
                ['return', 'expresion_opt']
            ],
            
            'expresion_opt': [
                ['expresion'],
                ['ε']
            ],
            
            'del_stmt': [
                ['del', 'id']
            ],
            
            'import_stmt': [
                ['import', 'id', 'import_as'],
                ['from', 'id', 'import', 'id', 'import_as']
            ],
            
            'import_as': [
                ['as', 'id'],
                ['ε']
            ],
            
            'print_stmt': [
                ['print', 'tk_par_izq', 'args_opt', 'tk_par_der']
            ],
            
            # Sentencias compuestas
            'sentencia_compuesta': [
                ['if_stmt'],
                ['while_stmt'],
                ['for_stmt'],
                ['try_stmt']
            ],
            
            'if_stmt': [
                ['if', 'expresion', 'tk_dos_puntos', 'bloque', 'elif_chain', 'else_opt']
            ],
            
            'elif_chain': [
                ['elif', 'expresion', 'tk_dos_puntos', 'bloque', 'elif_chain'],
                ['ε']
            ],
            
            'else_opt': [
                ['else', 'tk_dos_puntos', 'bloque'],
                ['ε']
            ],
            
            'while_stmt': [
                ['while', 'expresion', 'tk_dos_puntos', 'bloque']
            ],
            
            'for_stmt': [
                ['for', 'id', 'in', 'expresion', 'tk_dos_puntos', 'bloque']
            ],
            
            'def_stmt': [
                ['def', 'id', 'tk_par_izq', 'parametros', 'tk_par_der', 'tk_dos_puntos', 'bloque']
            ],
            
            'parametros': [
                ['parametro', 'lista_parametros'],
                ['ε']
            ],
            
            'lista_parametros': [
                ['tk_coma', 'parametro', 'lista_parametros'],
                ['ε']
            ],
            
            'parametro': [
                ['id', 'param_anotacion'],
                ['self', 'param_default']
            ],
            
            'param_anotacion': [
                ['tk_dos_puntos', 'tipo_anotacion', 'param_default'],
                ['param_default']
            ],
            
            'tipo_anotacion': [
                ['id', 'tipo_suffix']
            ],

            'tipo_suffix': [
                ['tk_punto', 'id', 'tipo_suffix'],
                ['tk_corchete_izq', 'tipo_anotacion', 'tk_corchete_der', 'tipo_suffix'],
                ['ε']
            ],
            
            'param_default': [
                ['tk_asig', 'expresion'],
                ['ε']
            ],
            
            'class_stmt': [
                ['class', 'id', 'herencia_opt', 'tk_dos_puntos', 'bloque']
            ],
            
            'herencia_opt': [
                ['tk_par_izq', 'id', 'tk_par_der'],
                ['ε']
            ],
            
            'try_stmt': [
                ['try', 'tk_dos_puntos', 'bloque', 'except_clauses', 'finally_opt']
            ],
            
            'except_clauses': [
                ['except', 'except_tipo', 'tk_dos_puntos', 'bloque', 'except_clauses'],
                ['ε']
            ],
            
            'except_tipo': [
                ['id'],
                ['ε']
            ],
            
            'finally_opt': [
                ['finally', 'tk_dos_puntos', 'bloque'],
                ['ε']
            ],
            
            # Bloque
            'bloque': [
                ['TAB', 'cuerpo_bloque', 'TABend']
            ],
            
            'cuerpo_bloque': [
                ['declaraciones']
            ],
            
            # Expresiones
            'expresion': [
                ['expr_or']
            ],
            
            'expr_or': [
                ['expr_and', 'expr_or_prime']
            ],
            
            'expr_or_prime': [
                ['or', 'expr_and', 'expr_or_prime'],
                ['ε']
            ],
            
            'expr_and': [
                ['expr_not', 'expr_and_prime']
            ],
            
            'expr_and_prime': [
                ['and', 'expr_not', 'expr_and_prime'],
                ['ε']
            ],
            
            'expr_not': [
                ['not', 'expr_not'],
                ['expr_comparacion']
            ],
            
            'expr_comparacion': [
                ['expr_aritmetica', 'expr_comp_prime']
            ],
            
            'expr_comp_prime': [
                ['op_comparacion', 'expr_aritmetica', 'expr_comp_prime'],
                ['ε']
            ],
            
            'op_comparacion': [
                ['tk_igual'],
                ['tk_distinto'],
                ['tk_menor'],
                ['tk_menor_igual'],
                ['tk_mayor'],
                ['tk_mayor_igual'],
                ['in'],
                ['is', 'is_not_opt']
            ],
            
            'is_not_opt': [
                ['not'],
                ['ε']
            ],
            
            'expr_aritmetica': [
                ['termino', 'expr_arit_prime']
            ],
            
            'expr_arit_prime': [
                ['tk_suma', 'termino', 'expr_arit_prime'],
                ['tk_resta', 'termino', 'expr_arit_prime'],
                ['ε']
            ],
            
            'termino': [
                ['factor', 'termino_prime']
            ],
            
            'termino_prime': [
                ['tk_mult', 'factor', 'termino_prime'],
                ['tk_div', 'factor', 'termino_prime'],
                ['tk_modulo', 'factor', 'termino_prime'],
                ['ε']
            ],
            
            'factor': [
                ['tk_suma', 'factor'],
                ['tk_resta', 'factor'],
                ['potencia']
            ],
            
            'potencia': [
                ['atom', 'potencia_prime']
            ],
            
            'potencia_prime': [
                ['tk_potencia', 'factor'],
                ['ε']
            ],
            
            'atom': [
                ['id', 'atom_suffix'],
                ['self', 'atom_suffix'],
                ['tk_entero'],
                ['tk_cadena'],
                ['True'],
                ['False'],
                ['None'],
                ['tk_par_izq', 'expresion_o_tupla'],
                ['lista'],
                ['diccionario_o_conjunto']
            ],
            
            'expresion_o_tupla': [
                ['expresion', 'tupla_o_expr'],
                ['tk_par_der']
            ],
            
            'tupla_o_expr': [
                ['tk_coma', 'elementos_tupla_tail', 'tk_par_der'],
                ['tk_par_der']
            ],
            
            'atom_suffix': [
                ['tk_par_izq', 'args_opt', 'tk_par_der', 'atom_suffix'],
                ['tk_corchete_izq', 'expresion', 'tk_corchete_der', 'atom_suffix'],
                ['tk_punto', 'id', 'atom_suffix'],
                ['ε']
            ],
            
            'args_opt': [
                ['args'],
                ['ε']
            ],
            
            'args': [
                ['expresion', 'args_tail']
            ],
            
            'args_tail': [
                ['tk_coma', 'expresion', 'args_tail'],
                ['ε']
            ],
            
            'lista': [
                ['tk_corchete_izq', 'elementos_lista', 'tk_corchete_der']
            ],
            
            'elementos_lista': [
                ['expresion', 'elementos_lista_tail'],
                ['ε']
            ],
            
            'elementos_lista_tail': [
                ['tk_coma', 'expresion', 'elementos_lista_tail'],
                ['ε']
            ],
            
            'elementos_tupla_tail': [
                ['expresion', 'elementos_tupla_tail_cont'],
                ['ε']
            ],
            
            'elementos_tupla_tail_cont': [
                ['tk_coma', 'expresion', 'elementos_tupla_tail_cont'],
                ['ε']
            ],
            
            'diccionario_o_conjunto': [
                ['tk_llave_izq', 'dict_o_set_contenido']
            ],
            
            'dict_o_set_contenido': [
                ['expresion', 'dict_o_set_decision'],
                ['tk_llave_der']
            ],
            
            'dict_o_set_decision': [
                ['tk_dos_puntos', 'expresion', 'elementos_dict_tail', 'tk_llave_der'],
                ['elementos_conjunto_tail', 'tk_llave_der']
            ],
            
            'elementos_dict_tail': [
                ['tk_coma', 'par_dict', 'elementos_dict_tail'],
                ['ε']
            ],
            
            'par_dict': [
                ['expresion', 'tk_dos_puntos', 'expresion']
            ],
            
            'elementos_conjunto_tail': [
                ['tk_coma', 'expresion', 'elementos_conjunto_tail'],
                ['ε']
            ]
        }
    
    def calcular_first(self, verbose=False):
        """Calcula el conjunto FIRST para cada símbolo de la gramática"""
        if verbose:
            print("=" * 80)
            print("CONJUNTOS PRIMEROS (FIRST)")
            print("=" * 80)
        
        for no_terminal in self.gramatica.keys():
            self.first[no_terminal] = set()
        
        terminales = self._obtener_terminales()
        for terminal in terminales:
            self.first[terminal] = {terminal}
        
        self.first[self.epsilon] = {self.epsilon}
        
        cambios = True
        while cambios:
            cambios = False
            
            for no_terminal, producciones in self.gramatica.items():
                first_anterior = len(self.first[no_terminal])
                
                for produccion in producciones:
                    self._agregar_first_produccion(no_terminal, produccion)
                
                if len(self.first[no_terminal]) > first_anterior:
                    cambios = True
        
        if verbose:
            for simbolo in sorted(self.gramatica.keys()):
                first_legible = self._convertir_set_a_legible(self.first[simbolo])
                print(f"FIRST({simbolo:25s}) = {{{first_legible}}}")
        
        return self.first
    
    def _agregar_first_produccion(self, no_terminal, produccion):
        if produccion[0] == self.epsilon:
            self.first[no_terminal].add(self.epsilon)
            return
        
        for i, simbolo in enumerate(produccion):
            if simbolo in self.first:
                self.first[no_terminal].update(self.first[simbolo] - {self.epsilon})
                
                if self.epsilon not in self.first[simbolo]:
                    break
                
                if i == len(produccion) - 1:
                    self.first[no_terminal].add(self.epsilon)
            else:
                self.first[no_terminal].add(simbolo)
                break
    
    def calcular_follow(self, verbose=False):
        """Calcula el conjunto FOLLOW para cada no terminal"""
        if verbose:
            print("\n" + "=" * 80)
            print("CONJUNTOS SIGUIENTES (FOLLOW)")
            print("=" * 80)
        
        for no_terminal in self.gramatica.keys():
            self.follow[no_terminal] = set()
        
        simbolo_inicial = 'programa'
        self.follow[simbolo_inicial].add(self.endmarker)
        
        cambios = True
        while cambios:
            cambios = False
            
            for no_terminal, producciones in self.gramatica.items():
                for produccion in producciones:
                    if produccion[0] == self.epsilon:
                        continue
                    
                    for i, simbolo in enumerate(produccion):
                        if simbolo not in self.gramatica:
                            continue
                        
                        follow_anterior = len(self.follow[simbolo])
                        
                        if i < len(produccion) - 1:
                            siguiente = produccion[i + 1]
                            
                            if siguiente in self.first:
                                self.follow[simbolo].update(
                                    self.first[siguiente] - {self.epsilon}
                                )
                            
                            if siguiente in self.first and self.epsilon in self.first[siguiente]:
                                self.follow[simbolo].update(self.follow[no_terminal])
                        else:
                            self.follow[simbolo].update(self.follow[no_terminal])
                        
                        if len(self.follow[simbolo]) > follow_anterior:
                            cambios = True
        
        if verbose:
            for simbolo in sorted(self.gramatica.keys()):
                follow_legible = self._convertir_set_a_legible(self.follow[simbolo])
                print(f"FOLLOW({simbolo:25s}) = {{{follow_legible}}}")
        
        return self.follow
    
    def construir_tabla_parsing(self, verbose=False):
        """Construye la tabla de análisis sintáctico LL(1)"""
        if verbose:
            print("\n" + "=" * 80)
            print("TABLA DE PREDICCIÓN LL(1)")
            print("=" * 80)
        
        conflictos = []
        
        for no_terminal, producciones in self.gramatica.items():
            for idx, produccion in enumerate(producciones):
                first_prod = self._calcular_first_produccion(produccion)
                
                for terminal in first_prod:
                    if terminal == self.epsilon:
                        continue
                    
                    if (no_terminal, terminal) in self.tabla_parsing:
                        conflictos.append({
                            'no_terminal': no_terminal,
                            'terminal': terminal,
                            'produccion1': self.tabla_parsing[(no_terminal, terminal)],
                            'produccion2': produccion
                        })
                    else:
                        self.tabla_parsing[(no_terminal, terminal)] = produccion
                
                if self.epsilon in first_prod:
                    for terminal in self.follow[no_terminal]:
                        if (no_terminal, terminal) in self.tabla_parsing:
                            conflictos.append({
                                'no_terminal': no_terminal,
                                'terminal': terminal,
                                'produccion1': self.tabla_parsing[(no_terminal, terminal)],
                                'produccion2': produccion
                            })
                        else:
                            self.tabla_parsing[(no_terminal, terminal)] = produccion

        if verbose:
            tabla_agrupada = {}
            for (nt, term), prod in sorted(self.tabla_parsing.items()):
                if nt not in tabla_agrupada:
                    tabla_agrupada[nt] = []
                term_legible = self._obtener_simbolo_esperado(term)
                prod_legible = ' '.join([self._obtener_simbolo_esperado(s) if s != 'ε' else 'ε' for s in prod])
                tabla_agrupada[nt].append(f"  [{term_legible:20s}] -> {prod_legible}")
            
            for nt in sorted(tabla_agrupada.keys()):
                print(f"\n{nt}:")
                for entrada in tabla_agrupada[nt]:
                    print(entrada)
        
        
        return self.tabla_parsing, conflictos
    
    def _calcular_first_produccion(self, produccion):
        resultado = set()
        
        if produccion[0] == self.epsilon:
            return {self.epsilon}
        
        for simbolo in produccion:
            if simbolo in self.first:
                resultado.update(self.first[simbolo] - {self.epsilon})
                if self.epsilon not in self.first[simbolo]:
                    break
            else:
                resultado.add(simbolo)
                break
        else:
            resultado.add(self.epsilon)
        
        return resultado
    
    def _obtener_terminales(self):
        terminales = set()
        for producciones in self.gramatica.values():
            for produccion in producciones:
                for simbolo in produccion:
                    if simbolo not in self.gramatica and simbolo != self.epsilon:
                        terminales.add(simbolo)
        return terminales
    
    def _convertir_set_a_legible(self, conjunto):
        legibles = []
        for token in sorted(conjunto):
            if token == self.epsilon:
                legibles.append('ε')
            else:
                legibles.append(self._obtener_simbolo_esperado(token))
        return ', '.join(legibles)
    
    def parsear(self, tokens):
        """Analiza sintácticamente una lista de tokens"""
        self.tokens = tokens
        self.pos = 0
        self.token_actual = tokens[0] if tokens else None
        self.errores = []
        
        try:
            self._parsear_no_terminal('programa')
            
            # Verificar que llegamos al final
            if self.token_actual.tipo != 'ENDMARKER':
                self._reportar_error_sintactico('programa')
            
            return True, "El analisis sintactico ha finalizado exitosamente."
        except SyntaxError as e:
            return False, str(e)
    
    def _parsear_no_terminal(self, no_terminal):
        if no_terminal == self.epsilon:
            return
        
        terminal_actual = self.token_actual.tipo
        
        if (no_terminal, terminal_actual) in self.tabla_parsing:
            produccion = self.tabla_parsing[(no_terminal, terminal_actual)]
            
            for simbolo in produccion:
                if simbolo == self.epsilon:
                    continue
                elif simbolo in self.gramatica:
                    self._parsear_no_terminal(simbolo)
                else:
                    self._match(simbolo)
        else:
            self._reportar_error_sintactico(no_terminal)
    
    def _match(self, tipo_esperado):
        if self.token_actual.tipo == tipo_esperado:
            self._avanzar()
        else:
            self._reportar_error_match(tipo_esperado)

    def _avanzar(self):
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
            self.token_actual = self.tokens[self.pos]
    
    def _obtener_lexema_token(self, token):
        if token.valor is not None:
            return str(token.valor)
        elif token.tipo in self.TOKEN_A_SIMBOLO:
            return self.TOKEN_A_SIMBOLO[token.tipo]
        else:
            return token.tipo
    
    def _obtener_simbolo_esperado(self, tipo_token):
        if tipo_token in self.TOKEN_A_SIMBOLO:
            return self.TOKEN_A_SIMBOLO[tipo_token]
        else:
            return tipo_token
    
    def _obtener_tokens_esperados(self, no_terminal):
        esperados = []
        
        for (nt, terminal), produccion in self.tabla_parsing.items():
            if nt == no_terminal:
                simbolo = self._obtener_simbolo_esperado(terminal)
                esperados.append(simbolo)
        
        return esperados
    
    def _reportar_error_sintactico(self, no_terminal):
        """Reporta un error sintáctico en el formato requerido"""
        linea = self.token_actual.fila
        columna = self.token_actual.columna
        lexema_encontrado = self._obtener_lexema_token(self.token_actual)
        tokens_esperados = self._obtener_tokens_esperados(no_terminal)
        
        # Detectar error de indentación específico
        if self.token_actual.tipo == 'TAB' and 'indentación' not in tokens_esperados:
            error_msg = f'<{linea},{columna}> Error sintactico: falla de indentacion.'
            raise SyntaxError(error_msg)
        
        # Si esperamos TAB (inicio de bloque) pero encontramos otra cosa
        if 'TAB' in [t for (nt, t), _ in self.tabla_parsing.items() if nt == no_terminal]:
            if self.token_actual.tipo in ('ENDMARKER', 'TABend', 'NEWLINE'):
                error_msg = f'<{linea},{columna}> Error sintactico: se esperaba un bloque indentado.'
                raise SyntaxError(error_msg)
        
        if 'dedentación' in tokens_esperados and self.token_actual.tipo not in ('TABend', 'ENDMARKER'):
            error_msg = f'<{linea},{columna}> Error sintactico: dedentación incorrecta.'
            raise SyntaxError(error_msg)
        
        # Formatear tokens esperados
        if tokens_esperados:
            esperados_str = ', '.join([f'"{t}"' for t in sorted(set(tokens_esperados))])
        else:
            esperados_str = '(ninguno)'
        
        error_msg = f'<{linea},{columna}> Error sintactico: se encontro: "{lexema_encontrado}"; se esperaba: {esperados_str}.'
        raise SyntaxError(error_msg)
    
    def _reportar_error_match(self, tipo_esperado):
        linea = self.token_actual.fila
        columna = self.token_actual.columna
        lexema_encontrado = self._obtener_lexema_token(self.token_actual)
        simbolo_esperado = self._obtener_simbolo_esperado(tipo_esperado)
        
        error_msg = f'<{linea},{columna}> Error sintactico: se encontro: "{lexema_encontrado}"; se esperaba: "{simbolo_esperado}".'
        raise SyntaxError(error_msg)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python parr.py <archivo.py> [--mostrar-tablas]")
        sys.exit(1)
    
    archivo = sys.argv[1]
    mostrar_tablas = '--mostrar-tablas' in sys.argv
    
    try:
        from analizador_lexico import analizador_lexico
        
        with open(archivo, 'r', encoding='utf-8') as f:
            codigo = f.read()
        
        tokens = analizador_lexico(codigo)
        
        parser = ParserLL1Completo()
        parser.calcular_first(verbose=mostrar_tablas)
        parser.calcular_follow(verbose=mostrar_tablas)
        parser.construir_tabla_parsing(verbose=mostrar_tablas)
        
        if mostrar_tablas:
            print("\n" + "=" * 80)
            print("INICIANDO ANÁLISIS SINTÁCTICO")
            print("=" * 80 + "\n")
        
        exito, mensaje = parser.parsear(tokens)
        
        print(mensaje)
        
        sys.exit(0 if exito else 1)
            
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{archivo}'")
        sys.exit(1)
    except Exception as e:
        print(f"{e}")
        sys.exit(1)