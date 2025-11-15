class Simbolo:
    def __init__(self, nombre, tipo, valor=None, linea=None, columna=None, scope=None):
        self.nombre = nombre
        self.tipo = tipo  
        self.valor = valor
        self.linea = linea
        self.columna = columna
        self.scope = scope  # Ámbito donde se declaró
        self.atributos = {}  # Atributos adicionales 
    
    def __repr__(self):
        return f"Simbolo(nombre='{self.nombre}', tipo='{self.tipo}', valor={self.valor}, scope='{self.scope}')"
    
    def __str__(self):
        return f"{self.nombre} [{self.tipo}]"


class TablaSimbolos:

    
    def __init__(self):
        self.scopes = []  # Stack de ámbitos
        self.scope_actual = 'global'
        self.tablas = {'global': {}}  # Diccionario de tablas por ámbito
        self.contador_scopes = 0
        
    def agregar_simbolo(self, nombre, tipo, valor=None, linea=None, columna=None):
 
        if self.scope_actual not in self.tablas:
            self.tablas[self.scope_actual] = {}
        
        # Verificar si el símbolo ya existe en el scope actual
        if nombre in self.tablas[self.scope_actual]:
            simbolo_existente = self.tablas[self.scope_actual][nombre]
            print(f"Advertencia: El símbolo '{nombre}' ya existe en el scope '{self.scope_actual}' "
                  f"(línea {simbolo_existente.linea}). Se sobrescribirá.")
        
        simbolo = Simbolo(nombre, tipo, valor, linea, columna, self.scope_actual)
        self.tablas[self.scope_actual][nombre] = simbolo
        
        return simbolo
    
    def buscar_simbolo(self, nombre, buscar_en_padres=True):

        # Primero buscar en el scope actual
        if self.scope_actual in self.tablas and nombre in self.tablas[self.scope_actual]:
            return self.tablas[self.scope_actual][nombre]
        
        # Si no se encuentra y se permite buscar en padres
        if buscar_en_padres:
            # Buscar en scopes desde el más interno al más externo
            for scope in reversed(self.scopes):
                if scope in self.tablas and nombre in self.tablas[scope]:
                    return self.tablas[scope][nombre]
            
            # Finalmente buscar en el scope global
            if 'global' in self.tablas and nombre in self.tablas['global']:
                return self.tablas['global'][nombre]
        
        return None
    
    def existe_simbolo(self, nombre, solo_scope_actual=False):

        if solo_scope_actual:
            return self.scope_actual in self.tablas and nombre in self.tablas[self.scope_actual]
        else:
            return self.buscar_simbolo(nombre) is not None
    
    def actualizar_simbolo(self, nombre, valor=None, **kwargs):

        simbolo = self.buscar_simbolo(nombre)
        if simbolo:
            if valor is not None:
                simbolo.valor = valor
            # Actualizar tipo si se proporciona en kwargs
            if 'tipo' in kwargs:
                simbolo.tipo = kwargs.pop('tipo')
            simbolo.atributos.update(kwargs)
            return True
        return False
    
    def entrar_scope(self, nombre_scope=None):

        if nombre_scope is None:
            self.contador_scopes += 1
            nombre_scope = f"scope_{self.contador_scopes}"
        
        self.scopes.append(self.scope_actual)
        self.scope_actual = nombre_scope
        
        if nombre_scope not in self.tablas:
            self.tablas[nombre_scope] = {}
        
        return nombre_scope
    
    def salir_scope(self):

        if self.scopes:
            self.scope_actual = self.scopes.pop()
        else:
            self.scope_actual = 'global'
        
        return self.scope_actual
    
    def obtener_simbolos_scope_actual(self):

        if self.scope_actual in self.tablas:
            return self.tablas[self.scope_actual].copy()
        return {}
    
    def obtener_todos_simbolos(self):

        return self.tablas.copy()
    
    def imprimir_tabla(self, mostrar_todos_scopes=True):

        print("TABLA DE SÍMBOLOS")

        
        scopes_a_mostrar = []
        if mostrar_todos_scopes:
            # Mostrar en orden: global, luego otros scopes
            if 'global' in self.tablas:
                scopes_a_mostrar.append('global')
            scopes_a_mostrar.extend([s for s in self.tablas.keys() if s != 'global'])
        else:
            scopes_a_mostrar = [self.scope_actual]
        
        for scope in scopes_a_mostrar:
            if scope not in self.tablas or not self.tablas[scope]:
                continue
            
            print(f"\n--- SCOPE: {scope} ---")
            print(f"{'#':<4} {'Nombre':<20} {'Tipo':<15} {'Valor':<20} ")
            print("-" * 80)
            
            for i, (nombre, simbolo) in enumerate(self.tablas[scope].items(), 1):
                valor_str = str(simbolo.valor) if simbolo.valor is not None else 'N/A'
                if len(valor_str) > 20:
                    valor_str = valor_str[:17] + '...'
                
                linea_str = str(simbolo.linea) if simbolo.linea is not None else 'N/A'
                
                print(f"{i:<4} {nombre:<20} {simbolo.tipo:<15} {valor_str:<20} ")
                
                # Mostrar atributos adicionales si existen
                if simbolo.atributos:
                    for key, val in simbolo.atributos.items():
                        print(f"     └─ {key}: {val}")
    
    def limpiar(self):
        self.scopes = []
        self.scope_actual = 'global'
        self.tablas = {'global': {}}
        self.contador_scopes = 0
    
    def estadisticas(self):
        """Retorna estadísticas de la tabla de símbolos"""
        total_simbolos = sum(len(tabla) for tabla in self.tablas.values())
        total_scopes = len(self.tablas)
        
        tipos_count = {}
        for tabla in self.tablas.values():
            for simbolo in tabla.values():
                tipos_count[simbolo.tipo] = tipos_count.get(simbolo.tipo, 0) + 1
        
        return {
            'total_simbolos': total_simbolos,
            'total_scopes': total_scopes,
            'scope_actual': self.scope_actual,
            'tipos': tipos_count
        }
