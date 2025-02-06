import re

class ExpressionR:

    def __init__(self):

        # Compila las expresiones regulares una vez al inicializar la clase
        # Expresión regular para identificar nombres de variables (comienza con letra o guion bajo, seguido de letras, números o guiones bajos)
        self.variable_er = re.compile(r"[a-zA-Z_][a-zA-Z0-9_]*")

        # Expresión regular para identificar valores hexadecimales (comienza con 'h' seguido de dígitos hexadecimales)
        self.hex_value = re.compile(r"h[0-9A-F]+")

        # Expresión regular para identificar valores binarios (comienza con 'b' seguido de dígitos binarios)
        self.bin_value = re.compile(r"b[01]+")

        # Expresión regular para identificar valores octales (comienza con 'o' seguido de dígitos octales)
        self.oct_value = re.compile(r"o[0-7]+")

        # Lista de operadores y símbolos especiales
        self.symbols = ['+', '-', '/', '*', '(', ')', '=']

        # Lista de encabezados o palabras reservadas
        self.header = ["bin","hexa","oct"]

        # Cola para almacenar los tokens identificados
        self.queue_s = []

    def analyzer(self, line):
        """
        Analiza una línea de entrada y clasifica cada token según su tipo.

        Args:
            line (str): La línea de entrada que se va a analizar.

        Returns:
            list: Una lista de tokens identificados.

        Raises:
            ValueError: Si se encuentra un token desconocido que no coincide con ninguna expresión regular.
        """
        # Divide la línea en tokens basados en espacios en blanco
        tokens = line.split()

        # Itera sobre cada token
        for token in tokens:

            # Verifica si el token es un valor binario
            if self.bin_value.fullmatch(token):
                self.queue_s.append("numb")  # Agrega "numb" a la cola

            # Verificar si el token es un valor hexadecimal
            elif self.hex_value.fullmatch(token):
                self.queue_s.append("numh")  # Agrega "numh" a la cola

            # Verifica si el token es un valor octal
            elif self.oct_value.fullmatch(token):
                self.queue_s.append("numo")  # Agrega "numo" a la cola

            # Verifica si el token es un símbolo o un encabezado
            elif token in self.symbols or token in self.header:
                self.queue_s.append(token)  # Agrega el símbolo o encabezado a la cola

            # Verifica si el token es un nombre de variable
            elif self.variable_er.fullmatch(token):
                self.queue_s.append("id")  # Agrega "id" a la cola

            # Si el token no coincide con ninguna expresión regular, lanzar un error
            else:
                raise ValueError(f"El valor '{token}' es desconocido para esta gramática")

        # Devuelve la cola de tokens identificados
        return self.queue_s

#Parser LL1
class LL1Parser:
    def __init__(self):
        #Definición de la gramatica
        self.table = {
            # Para el símbolo inicial S
            ("S", "bin"): "Asignacion S",
            ("S", "hexa"): "Asignacion S",
            ("S", "oct"): "Asignacion S",
            ("S", "id"): "E",
            ("S", "numb"): "E",
            ("S", "numh"): "E",
            ("S", "numo"): "E",
            ("S", "("): "E",

            # Producciones para Asignacion
            ("Asignacion", "bin"): "HEADER id = E",
            ("Asignacion", "hexa"): "HEADER id = E",
            ("Asignacion", "oct"): "HEADER id = E",
            ("Asignacion", "id"): "E",      # Si no hay encabezado, se asume que es una expresión, revisarlo para cambiarlo o dejarlo
            ("Asignacion", "numb"): "E",
            ("Asignacion", "numh"): "E",
            ("Asignacion", "numo"): "E",
            ("Asignacion", "("): "E",

            # Producciones para HEADER
            ("HEADER", "bin"): "bin",
            ("HEADER", "hexa"): "hexa",
            ("HEADER", "oct"): "oct",

            # Producciones para E (expresión)
            ("E", "("): "T E'",
            ("E", "id"): "T E'",
            ("E", "numb"): "T E'",
            ("E", "numh"): "T E'",
            ("E", "numo"): "T E'",

            # Producciones para E'
            ("E'", "+"): "+ T E'",
            ("E'", "-"): "- T E'",
            ("E'", "hexa"): "ε",
            ("E'", "bin"): "ε",
            ("E'", "oct"): "ε",
            ("E'", "("): "ε",
            ("E'", ")"): "ε",
            ("E'", "$"): "ε",

            # Producciones para T (término)
            ("T", "("): "F T'",
            ("T", "id"): "F T'",
            ("T", "numb"): "F T'",
            ("T", "numh"): "F T'",
            ("T", "numo"): "F T'",

            # Producciones para T'
            ("T'", "+"): "ε",
            ("T'", "-"): "ε",
            ("T'", "*"): "* F T'",
            ("T'", "/"): "/ F T'",
            ("T'", "hexa"): "ε",
            ("T'", "bin"): "ε",
            ("T'", "oct"): "ε",
            ("T'", "("): "ε",
            ("T'", ")"): "ε",
            ("T'", "$"): "ε",

            # Producciones para F (factor)
            ("F", "("): "( E )",
            ("F", "id"): "id",
            ("F", "numb"): "numb",
            ("F", "numh"): "numh",
            ("F", "numo"): "numo",
        }
    
    def parse(self, tokens):
        """
        Realiza el análisis sintáctico de la secuencia de tokens

        Args:
            tokens (list): Lista de tokens generada por el analizador léxico.
        Returns:
            True si la cadena es aceptada; de lo contrario, lanza un error.
        """
        # Agregar marcador final
        tokens.append("$")
        # Inicializar la pila con el marcador final y el símbolo inicial (S)
        stack = ["$", "S"]
        index = 0  # Índice del token actual

        while stack:
            top = stack.pop()
            current_token = tokens[index]
            
            if top == "ε":
                # Símbolo vacío; se ignora.
                continue

            if top == current_token:
                # Coincidencia de terminal: se consume el token
                index += 1
            elif self.is_terminal(top):
                # Si top es un terminal pero no coincide con el token actual, error
                raise SyntaxError(f"Error sintáctico: se esperaba '{top}' pero se encontró '{current_token}'")
            else:
                # top es un no terminal: consultar la tabla
                key = (top, current_token)
                if key in self.table:
                    production = self.table[key]
                    # Si la producción es ε, no se apilan nuevos símbolos
                    if production != "ε":
                        symbols = production.split()
                        # Se apilan los símbolos en orden inverso
                        for symbol in reversed(symbols):
                            stack.append(symbol)
                else:
                    raise SyntaxError(f"Error sintáctico: no se encontró producción para ({top}, {current_token})")
        # Si se consumieron todos los tokens, la cadena es aceptada.
        if index == len(tokens):
            return True
        else:
            return False
    
    def is_terminal(self, symbol):
        """
        Consideramos como terminales los símbolos que no están en mayúsculas
        o que son símbolos especiales.
        """
        # Lista de terminales
        terminales = ['bin', 'hexa', 'oct', 'id', 'numb', 'numh', 'numo', '+', '-', '*', '/', '(', ')', '=', '$']
        return symbol in terminales


