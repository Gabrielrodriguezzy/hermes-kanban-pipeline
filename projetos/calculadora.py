#!/usr/bin/env python3
"""Calculadora Simples — operações básicas no terminal."""

import sys


def calcular(a, op, b):
    """Executa a operação e retorna o resultado."""
    if op == "+":
        return a + b
    elif op == "-":
        return a - b
    elif op == "*":
        return a * b
    elif op == "/":
        if b == 0:
            return "Erro: divisão por zero"
        return a / b
    elif op == "**":
        return a ** b
    elif op == "%":
        return a % b
    else:
        return f"Operador inválido: {op}"


def main():
    if len(sys.argv) == 4:
        # Modo argumentos: python3 calculadora.py 10 + 5
        try:
            a = float(sys.argv[1])
            op = sys.argv[2]
            b = float(sys.argv[3])
        except ValueError:
            print("Erro: use números válidos. Ex: calculadora.py 10 + 5")
            sys.exit(1)
    else:
        # Modo interativo
        print("Calculadora Simples")
        print("Operadores: +  -  *  /  **  %")
        print("Digite 'sair' para encerrar.\n")
        try:
            expr = input(">>> ").strip()
            if expr.lower() in ("sair", "exit", "quit", "q"):
                return
            partes = expr.split()
            if len(partes) != 3:
                print("Uso: <num> <op> <num>  (ex: 10 + 5)")
                return
            a_str, op, b_str = partes
            a = float(a_str)
            b = float(b_str)
        except (ValueError, EOFError):
            print("Erro: entrada inválida")
            return

    resultado = calcular(a, op, b)
    print(f"{a} {op} {b} = {resultado}")


if __name__ == "__main__":
    main()
