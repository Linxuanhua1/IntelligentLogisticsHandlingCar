import sympy as sp


def integrate_func(integrate_times: int, var_coe: float, constant: float) -> (sp.Symbol, sp.core.expr.Expr):
    x = sp.symbols('x')
    f = var_coe * x + constant
    for i in range(integrate_times):
        f = sp.integrate(f, x)
    return f, x


f, x = integrate_func(3, 1, 15)
print(int(f.subs(x, 5)))
