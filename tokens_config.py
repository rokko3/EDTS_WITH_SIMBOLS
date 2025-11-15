SIMBOLOS = {
        '(': 'tk_par_izq', ')': 'tk_par_der', '[': 'tk_corchete_izq', ']': 'tk_corchete_der',
        '{': 'tk_llave_izq', '}': 'tk_llave_der', ':': 'tk_dos_puntos', ',': 'tk_coma',
        '**': 'tk_potencia', '+=': 'tk_mas_asig', '-=': 'tk_menos_asig', '*=': 'tk_mult_asig',
        '/=': 'tk_div_asig', '%=': 'tk_mod_asig', '==': 'tk_igual', '!=': 'tk_distinto',
        '>=': 'tk_mayor_igual', '<=': 'tk_menor_igual',
        '=': 'tk_asig', '>': 'tk_mayor', '<': 'tk_menor',
        '+': 'tk_suma', '-': 'tk_resta', '*': 'tk_mult', '/': 'tk_div', '%': 'tk_modulo',
        '.': 'tk_punto', '//=':'tk_div_entera_asig', '**=':'tk_potencia_asig','"""':'tk_comilla_doble'
    }

PALABRAS_RESERVADAS = {
    'False', 'None', 'True', 'and', 'as', 'break', 'class', 'continue',
    'def', 'del', 'elif', 'else', 'except', 'finally', 'for', 'from',
    'if', 'import', 'in', 'is', 'not', 'or', 'pass', 'return', 'try',
    'while', 'print', 'self'
}

SIMBOLOS_PARSER = {
    'NEWLINE': 'nueva línea',
            'ENDMARKER': 'fin de archivo',
            'TAB': 'indentación',
            'TABend': 'fin de indentación',
            'id': 'identificador',
            'tk_entero': 'número',
            'tk_cadena': 'cadena de texto',
            'numero': 'número',
           
            'if': 'if', 'elif': 'elif', 'else': 'else',
            'while': 'while', 'for': 'for', 'def': 'def',
            'class': 'class', 'return': 'return', 'break': 'break',
            'continue': 'continue', 'pass': 'pass', 'del': 'del',
            'import': 'import', 'from': 'from', 'as': 'as',
            'try': 'try', 'except': 'except', 'finally': 'finally',
            'in': 'in', 'is': 'is', 'and': 'and', 'or': 'or',
            'not': 'not', 'True': 'True', 'False': 'False',
            'None': 'None', 'self': 'self', 'print': 'print'
}

SIMBOLOS_INVERTIDOS = {v: k for k, v in SIMBOLOS.items()}