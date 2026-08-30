import numpy as np
from . import vecNorm

def convergencia(AttackVectorInitial):
# Calcular el radio (norma L2 a lo largo de las filas=dim=1)
    Radius = vecNorm.VecNorm(AttackVectorInitial,2,1, False)#  A elevado a p en dimension 1filas 0columnas
    #print("Radius_ANTES", Radius)
    
    # Determinar águilas convergidas y no convergidas
    ConvergedEagles = Radius == 0  # Águilas que han convergido (radio = 0)
    #print("ConvergedEagles", ConvergedEagles)
    Radius = vecNorm.VecNorm(AttackVectorInitial,2,1, True)
    UnconvergedEagles = ~ConvergedEagles  # Águilas que no han convergido # # # (NO son 0)
    #print("Radius_DESPUÉS", Radius)
    
    return ConvergedEagles, UnconvergedEagles, Radius

def ataque_geo(PopulationSize, FlockMemoryX, x, AttackPropensity, CurrentIteration):
    # Selección de presas (mapeo uno a uno)
    DestinationEagle = np.random.permutation(PopulationSize) #permutacion aleatoria de indices
    
    # Calcular AttackVectorInitial (Ecuación 1 en el artículo)
    AttackVectorInitial = FlockMemoryX[DestinationEagle, :] - x
    
    ConvergedEagles, UnconvergedEagles, Radius = convergencia(AttackVectorInitial)
    
    # Corregir vectores para águilas convergidas
    AttackVectorInitial[ConvergedEagles, :] = 0  # Establecer a 0 para águilas convergidas
    
    # Calcular vectores unitarios
    AttackVectorUnit = AttackVectorInitial / vecNorm.VecNorm(AttackVectorInitial, 2, 1)

    # Corregir vectores para las águilas convergentes
    AttackVectorUnit[ConvergedEagles, :] = 0
    
    # Calcular vectores de movimiento (Ecuación 6 en el artículo: r*p*[Ai/llAill]) 
    AttackVector = np.random.rand(PopulationSize, 1) * AttackPropensity[CurrentIteration] * AttackVectorUnit * Radius ####

    return AttackVectorInitial, AttackVector




def cruce_geo(AttackVectorInitial, PopulationSize, nvars, CruisePropensity, CurrentIteration, ConvergedEagles, UnconvergedEagles, Radius):

    # Inicializar CruiseVectorInitial (valores aleatorios en el intervalo [-1, 1])
    #CruiseVectorInitial = 2 * np.random.rand(PopulationSize, nvars) - 1
    CruiseVectorInitial = np.random.rand(PopulationSize, nvars) # # # Intervalo de 0 a 1 (En el parrafo posterior a la Ec. 5)

    CruiseVectorInitial[ConvergedEagles, :] = 0 
    
    # Determinar variables restringidas y libres
    for i1 in range(PopulationSize):
        if UnconvergedEagles[i1]:
            # 
            vConstrained = np.zeros(nvars, dtype=bool)  # Máscara
            idx = np.random.choice(np.where(AttackVectorInitial[i1, :])[0], size=1, replace=False)
            vConstrained[idx] = True
            vFree = ~vConstrained
            d=sum(AttackVectorInitial[i1]*CruiseVectorInitial[i1])
            CruiseVectorInitial[i1, idx] = (d - np.sum(AttackVectorInitial[i1, vFree] * CruiseVectorInitial[i1, vFree], axis=0)) / AttackVectorInitial[i1, vConstrained]

     # Calcular vectores unitarios
    CruiseVectorUnit = CruiseVectorInitial / vecNorm.VecNorm(CruiseVectorInitial, 2, 1)

    # Corregir vectores para las águilas convergentes
    CruiseVectorUnit[ConvergedEagles, :] = 0
    
    
    # Calcular vectores de movimiento (Ecuación 6 en el artículo: r*p*[Ai/llAill]) 
    CruiseVector = np.random.rand(PopulationSize, 1) * CruisePropensity[CurrentIteration] * CruiseVectorUnit * Radius
    
    return CruiseVector