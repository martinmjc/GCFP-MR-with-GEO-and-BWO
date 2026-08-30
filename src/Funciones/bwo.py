from . import pre_procesamiento as pp
from . import cal_fitness as cf
import copy
import numpy as np
import random
from . import reparador as rp



#-----------------------------------------------PROCREACION
def Procreacion(Parent1, Parent2, Celdas_LB, Celdas_UB, Celdas_canti, Rutas_piezas,MTBF_maq, M_secuencias, M_tiempos, Cost_rutas,Vol_piezas,Cost_break, CR, limites):
    
    # Dimensión del cromosoma
    Nvar = len(Parent1)

    # 1) Elegir Nvar/2 índices únicos
    idxs = random.sample(range(Nvar), Nvar // 2)

    # 2) Crear hijos copiando a los padres
    Child1 = list(Parent1)  
    Child2 = list(Parent2)  

    # cruce solo afecta a nvar/2 genes
    for i in idxs:
        alfa = random.random()
        Child1[i] = round(alfa * Parent1[i] + (1 - alfa) * Parent2[i])
        Child2[i] = round(alfa * Parent2[i] + (1 - alfa) * Parent1[i])

    # Verificación de factibilidad
    Children=[]
    ##Child1
    Indicador_factibilidad_1 = pp.Verificacion_factibilidad_celdas(Child1, Celdas_LB, Celdas_UB, Celdas_canti, Rutas_piezas,MTBF_maq,limites)
    if Indicador_factibilidad_1==1:
        Children.append(Child1)
    else:
        Child1 = rp.reparador(Child1, Celdas_LB, Celdas_UB, Celdas_canti, Rutas_piezas, MTBF_maq, limites)
        Children.append(Child1)
    
    ##Child2
    Indicador_factibilidad_2 = pp.Verificacion_factibilidad_celdas(Child2, Celdas_LB, Celdas_UB, Celdas_canti, Rutas_piezas,MTBF_maq,limites)
    if Indicador_factibilidad_2==1:
        Children.append(Child2)
    else:
        Child2 = rp.reparador(Child2, Celdas_LB, Celdas_UB, Celdas_canti, Rutas_piezas, MTBF_maq, limites)
        Children.append(Child2)

    Fit_children=[]

    for i in range(len(Children)):

        # IMPORTANTE PARA CALCULAR EL FITNESS

        Z_M_secuencias, Z_M_tiempos, Z_Cost_rutas=pp.Seleccion_rutas(Children[i], M_secuencias, M_tiempos, Cost_rutas, Rutas_piezas)
        fit_child, Mov_Int, Bk_cost, fit1, fit2=cf.Calculo_fitness(Children[i], Z_M_secuencias, Z_M_tiempos, Vol_piezas, Z_Cost_rutas, Rutas_piezas, MTBF_maq,Cost_break)
        
        Fit_children.append(fit_child.copy())
    
    Fit_children = np.array(Fit_children)
    sorted_indices = np.argsort(Fit_children)
    Fit_children = Fit_children[sorted_indices]
    Children = np.array(Children)[sorted_indices]

    # Canibalismo de los hijos

    ns = max(1, int(len(Children) * CR)) # Número de sobrevivientes (ns = Number of suvivors)
    Pop2 = copy.deepcopy(Children[:ns])
    Fit_children = copy.deepcopy(Fit_children[:ns])
    return Pop2, Fit_children

# .--------------------------------------------MUTACIÓN
def mutacion(Pop1, PM,Celdas_LB, Celdas_UB, Celdas_canti, Rutas_piezas,M_secuencias, M_tiempos, Cost_rutas,Vol_piezas, MTBF_maq,Cost_break,limites):
    nm = int(len(Pop1)*PM)#numero de mutaciones
    
    Pop3 = []

    Fit_mutation = []

    while len(Pop3) < nm: 
        
        mut = random.choice(Pop1).copy()

        index1, index2 = random.sample(range(len(mut)), k=2)
        mut[index1], mut[index2] = mut[index2], mut[index1]

        # Verificación de factibilidad
        Z_M_secuencias, Z_M_tiempos, Z_Cost_rutas=pp.Seleccion_rutas(mut, M_secuencias, M_tiempos, Cost_rutas, Rutas_piezas)

        Indicador_factibilidad = pp.Verificacion_factibilidad_celdas(mut, Celdas_LB, Celdas_UB, Celdas_canti, Rutas_piezas, MTBF_maq,limites)
        
        if Indicador_factibilidad==1:
            Pop3.append(mut.copy())
        else:
            mut = rp.reparador(mut, Celdas_LB, Celdas_UB, Celdas_canti, Rutas_piezas, MTBF_maq,limites)
            Pop3.append(mut.copy())

        # IMPORTANTE PARA CALCULAR EL FITNESS
        Z_M_secuencias, Z_M_tiempos, Z_Cost_rutas=pp.Seleccion_rutas(mut, M_secuencias, M_tiempos, Cost_rutas, Rutas_piezas)
        fit_mut, Mov_Int, Bk_cost, fit1, fit2=cf.Calculo_fitness(mut, Z_M_secuencias, Z_M_tiempos, Vol_piezas, Z_Cost_rutas, Rutas_piezas, MTBF_maq,Cost_break)

        Fit_mutation.append(fit_mut.copy())
    
    return Pop3, Fit_mutation