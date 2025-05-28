import math

def calc(expression):
    """Powerful calculator that can evaluate mathematical expressions safely"""
    # Safe evaluation with math functions available
    safe_dict = {
        "__builtins__": {},
        "math": math,
        "sqrt": math.sqrt,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "log": math.log,
        "exp": math.exp,
        "pi": math.pi,
        "e": math.e,
        "abs": abs,
        "round": round,
        "min": min,
        "max": max,
        "sum": sum,
        "pow": pow,
    }
    
    try:
        result = eval(expression, safe_dict)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"

def simple_calc(expr):
    """Simple calculator for basic math"""
    import re
    # Only allow numbers, operators, and parentheses
    if re.match(r'^[0-9+\-*/().\s]+$', expr):
        try:
            return str(eval(expr))
        except:
            return "Error: Invalid expression"
    else:
        return "Error: Only basic math allowed" 