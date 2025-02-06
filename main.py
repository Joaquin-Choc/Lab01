import os.path
from er import ExpressionR
from er import LL1Parser

def main():
    print("Laboratorio 1 Compiladores")
    print("--------------------------------------------------")
    # Solicita la dirección del archivo .txt
    dir = input("Ingrese la ubicación del archivo .txt\n >")

    # Instancia del analizador léxico y del parser LL(1)
    lexer = ExpressionR()
    parser = LL1Parser()

    try:
        with open(dir, 'r') as file:
            linea_num = 1
            for linea in file:
                # Limpia la cola de tokens antes de procesar una nueva línea
                lexer.queue_s = []
                tokens = lexer.analyzer(linea.strip())
                print(f"Tokens en la línea {linea_num}:", tokens)
                try:
                    if parser.parse(tokens.copy()):
                        print(f"Línea {linea_num} aceptada por la gramática.")
                    else:
                        print(f"Línea {linea_num} rechazada por la gramática.")
                except SyntaxError as e:
                    print(f"Error en la línea {linea_num}:", e)
                linea_num += 1

    except FileNotFoundError:
        print("Error: El archivo no fue encontrado.")
    except IOError:
        print("Error: No se pudo acceder al archivo.")

if __name__ == "__main__":
    main()