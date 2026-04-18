"""Módulo con las operaciones matemáticas de la calculadora."""

AUTORES = "Isis Amaya | Santiago Rozo | Santiago Higuita | Samuel Oviedo"


def sumar(a, b):
    """Retorna la suma de a y b."""
    return a + b


def restar(a, b):
    """Retorna la resta de a menos b."""
    return a - b


def multiplicar(a, b):
    """Retorna el producto de a y b."""
    return a * b


def dividir(a, b):
    """Retorna la división de a entre b. Lanza ZeroDivisionError si b es 0."""
    if b == 0:
        raise ZeroDivisionError("No se puede dividir por cero")
    return a / b


def potencia(a, b):
    """Retorna a elevado a la potencia b."""
    return a**b


def modulo(a, b):
    """Retorna el residuo de dividir a entre b. Lanza ZeroDivisionError si b es 0."""
    if b == 0:
        raise ZeroDivisionError("No se puede dividir por cero")
    return a % b
