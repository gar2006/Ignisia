from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application
)
from sympy import simplify
import re
import random

# Enable implicit multiplication
transformations = standard_transformations + (implicit_multiplication_application,)


def normalize_expression(expr):
    expr = expr.lower()

    # Remove spaces
    expr = expr.replace(" ", "")

    # Replace power symbol
    expr = expr.replace("^", "**")

    # Handle fractions like ½
    expr = expr.replace("½", "1/2")

    # Replace common words → symbols
    expr = expr.replace("mass", "m")
    expr = expr.replace("velocity", "v")
    expr = expr.replace("energy", "e")

    # Remove units
    expr = re.sub(r'(m/s|kg|n|j|cm|m)', '', expr)

    # Take RHS if equation
    if "=" in expr:
        expr = expr.split("=")[-1]

    return expr.strip()


def numeric_check(expr1, expr2, variables):
    for _ in range(3):
        subs = {var: random.randint(1, 10) for var in variables}
        try:
            val1 = expr1.evalf(subs=subs)
            val2 = expr2.evalf(subs=subs)
            if abs(val1 - val2) > 1e-6:
                return False
        except:
            return False
    return True


def validate_equation(student_expr, correct_expr):
    try:
        student_expr = normalize_expression(student_expr)
        correct_expr = normalize_expression(correct_expr)

        # Extract variables
        vars_student = set(re.findall(r'[a-zA-Z]+', student_expr))
        vars_correct = set(re.findall(r'[a-zA-Z]+', correct_expr))
        all_vars = vars_student.union(vars_correct)

        # Create symbols
        local_dict = {var: parse_expr(var) for var in all_vars}

        # Parse expressions
        student = simplify(parse_expr(student_expr, local_dict=local_dict, transformations=transformations))
        correct = simplify(parse_expr(correct_expr, local_dict=local_dict, transformations=transformations))

        # Symbolic check
        if simplify(student - correct) == 0:
            return True

        # Numeric fallback
        return numeric_check(student, correct, all_vars)

    except Exception as e:
        print("Math error:", e)
        return False
