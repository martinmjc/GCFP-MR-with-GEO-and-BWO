import numpy as np

#funcion que permite calcular la norma de un vector o matriz A
#p = 2  # Norma Euclidiana
#dim = 1  # Calcular a lo largo de las filas (dim=1)

def VecNorm(A, p, dim, Mantener=True):
    # Sumar las potencias de A elevado a la p, a lo largo de la dimensión especificada
    sum_pot_dim = np.sum(np.power(A, p), axis=dim, keepdims=Mantener)
    # Calcular la raíz p-ésima
    N = np.power(sum_pot_dim, 1/p) #lo mismo que sum_pot_dim ** 1/p
    return N

