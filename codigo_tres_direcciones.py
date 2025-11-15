

class GeneradorTAC:
    def __init__(self):
        self.codigo = []  # Lista de instrucciones TAC
        self.contador_temporal = 0  # Contador para variables temporales
        self.contador_etiqueta = 0  # Contador para etiquetas
    
    def nuevo_temporal(self):
        temp = f"t{self.contador_temporal}"
        self.contador_temporal += 1
        return temp
    
    def nueva_etiqueta(self):
        etiq = f"L{self.contador_etiqueta}"
        self.contador_etiqueta += 1
        return etiq
    
    def emitir(self, instruccion):

        self.codigo.append(instruccion)
    
    def generar_expresion(self, nodo):
  
        if not hasattr(nodo, 'traduccion'):
            return None
        
        traduccion = nodo.traduccion
        
        # Si es un número o identificador simple, retornarlo directamente
        if self._es_simple(traduccion):
            return traduccion
        
        # Parsear la expresión y generar TAC
        return self._generar_tac_expresion(traduccion)
    
    def _es_simple(self, expr):
        expr = expr.strip()

        return (expr.replace('.', '').replace('_', '').isalnum() or 
                expr.startswith('0x') or expr.startswith('0o') or expr.startswith('0b'))
    
    def _generar_tac_expresion(self, expr):
        expr = expr.strip()

        if expr.startswith('(') and expr.endswith(')'):
            return self._generar_tac_expresion(expr[1:-1])
        

        for op in ['+', '-']:
            nivel_paren = 0
            for i in range(len(expr) - 1, -1, -1):
                if expr[i] == ')':
                    nivel_paren += 1
                elif expr[i] == '(':
                    nivel_paren -= 1
                elif nivel_paren == 0 and expr[i] == op and i > 0:
                    # Encontramos el operador principal
                    izq = expr[:i].strip()
                    der = expr[i+1:].strip()
                    
                    temp_izq = self._generar_tac_expresion(izq)
                    temp_der = self._generar_tac_expresion(der)
                    
                    # Generar nueva temporal para el resultado
                    temp_res = self.nuevo_temporal()
                    self.emitir(f"{temp_res} = {temp_izq} {op} {temp_der}")
                    return temp_res

        for op in ['*', '/', '%']:
            nivel_paren = 0
            for i in range(len(expr) - 1, -1, -1):
                if expr[i] == ')':
                    nivel_paren += 1
                elif expr[i] == '(':
                    nivel_paren -= 1
                elif nivel_paren == 0 and expr[i] == op and i > 0:
                    izq = expr[:i].strip()
                    der = expr[i+1:].strip()
                    
                    temp_izq = self._generar_tac_expresion(izq)
                    temp_der = self._generar_tac_expresion(der)
                    
                    temp_res = self.nuevo_temporal()
                    self.emitir(f"{temp_res} = {temp_izq} {op} {temp_der}")
                    return temp_res

        return expr
    
    def generar_asignacion(self, variable, expresion):
        temp_expr = self._generar_tac_expresion(expresion)
        self.emitir(f"{variable} = {temp_expr}")
    
    def generar_condicional(self, condicion, etiq_verdadero, etiq_falso):
        temp_cond = self._generar_tac_expresion(condicion)
        self.emitir(f"if {temp_cond} goto {etiq_verdadero}")
        self.emitir(f"goto {etiq_falso}")
    
    def generar_etiqueta(self, etiqueta):

        self.emitir(f"{etiqueta}:")
    
    def generar_salto(self, etiqueta):

        self.emitir(f"goto {etiqueta}")
    
    def generar_llamada(self, funcion, parametros, destino=None):

        # Pasar parámetros
        for i, param in enumerate(parametros):
            temp_param = self._generar_tac_expresion(param)
            self.emitir(f"param {temp_param}")
        
        # Llamada
        if destino:
            self.emitir(f"{destino} = call {funcion}, {len(parametros)}")
        else:
            self.emitir(f"call {funcion}, {len(parametros)}")
    
    def generar_retorno(self, expresion=None):

        if expresion:
            temp_expr = self._generar_tac_expresion(expresion)
            self.emitir(f"return {temp_expr}")
        else:
            self.emitir("return")
    
    def generar_desde_ast(self, nodo):

        if not hasattr(nodo, 'valor'):
            return
        
        valor = nodo.valor
        traduccion = nodo.traduccion if hasattr(nodo, 'traduccion') else ""
        
        if 'SENTENCIA' in valor:
            # Analizar si es asignación
            if '=' in traduccion and not any(op in traduccion for op in ['==', '!=', '<=', '>=']):
                partes = traduccion.split('=', 1)
                if len(partes) == 2:
                    variable = partes[0].strip()
                    expresion = partes[1].strip()
                    self.generar_asignacion(variable, expresion)
        
        # Recursivamente procesar hijos
        if hasattr(nodo, 'hijos'):
            for hijo in nodo.hijos:
                self.generar_desde_ast(hijo)
    
    def obtener_codigo(self):

        return '\n'.join(self.codigo)
    
    def imprimir_codigo(self):
        """Imprime el código TAC generado"""
        print("\n" + "="*80)
        print("CÓDIGO DE TRES DIRECCIONES (TAC)")
        print("="*80)
        for i, instruccion in enumerate(self.codigo, 1):
            print(f"{i:3}. {instruccion}")
        print("="*80)


def generar_tac_desde_traduccion(traduccion):

    generador = GeneradorTAC()
    
    # Separar por líneas
    lineas = traduccion.strip().split('\n')
    
    for linea in lineas:
        linea = linea.strip()
        if not linea:
            continue
        
        # Detectar asignaciones
        if '=' in linea and not any(op in linea for op in ['==', '!=', '<=', '>=']):
            partes = linea.split('=', 1)
            if len(partes) == 2:
                variable = partes[0].strip()
                expresion = partes[1].strip()
                generador.generar_asignacion(variable, expresion)
    
    return generador
