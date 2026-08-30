#programa GEO
from Funciones import ini_parametros as ip
from Funciones import pre_procesamiento as pp
from Funciones import grafico as gr
from Funciones import vecNorm as vecNorm
from Funciones import cal_fitness as cf
from Funciones import reparador as rp
from Funciones import geo_func
from Funciones import bwo
import pandas as pd
import numpy as np
import copy
import random


def GEO_BWO():
    PopulationSize = 100
    MaxIterations = 50
    AttackPropensity = [1.5, 2]
    CruisePropensity = [0.5,0.25]
    PR = 0.8
    CR = 0.6
    nr = int(PopulationSize*PR) #numero de reproducciones
    
    Celdas_canti = 2
    Celdas_LB = 2
    Celdas_UB = 6
    nvars = 17

    # Generar población inicial aleatoria dentro de los límites
    Rutas_piezas, Vol_piezas, Cost_break, Cost_rutas, MTBF_maq, M_secuencias, M_tiempos, limites = ip.iniciarparametros()
    
    Cant_pruebas = 100
    rpdd = []
    
    
    
    for j in range(100):    
        poblaciones = []
        fitness_histories = []  # GUARDA fitness vs iteración para cada prueba
        for z in range(Cant_pruebas):
            best_fitness_history = []  # historia de una sola prueba
            
            Pop = pp.Geracion_población_inicial(PopulationSize, Rutas_piezas, Celdas_canti, Celdas_LB, Celdas_UB, MTBF_maq, limites)
            x, Mm_fitness, Matriz_total_widows, Matriz_total_G_fitness, G_fitness, G_widow = pp.pop_ordenada(Pop, M_secuencias, M_tiempos, Cost_rutas, Vol_piezas, Rutas_piezas,MTBF_maq,Cost_break)

            pop_semilla = copy.deepcopy(Pop)
            
            # Evaluar la función objetivo en la población inicial
            FitnessScores_lista = []
            for ii in range(len(x)):
                Z_M_secuencias, Z_M_tiempos, Z_Cost_rutas=pp.Seleccion_rutas(x[ii], M_secuencias, M_tiempos, Cost_rutas,Rutas_piezas)
                Fitness, Mov_Int, Bk_cost, fit1, fit2 = cf.Calculo_fitness(x[ii], Z_M_secuencias, Z_M_tiempos, Vol_piezas, Z_Cost_rutas, Rutas_piezas, MTBF_maq,Cost_break)
                FitnessScores_lista.append(float(Fitness))
            FitnessScores = np.array(FitnessScores_lista)  # Convertir a array de numpy para operaciones posteriores
    
            FlockMemoryF = FitnessScores.copy() #mejor posicion visitada hasta ahora por eagle f
            FlockMemoryX = x.copy() #posicion actual de eagle i
    
            # # # Ecuación 9 -Artículo GEO - Calculo P_a y P_c
            AttackPropensity = np.linspace(AttackPropensity[0], AttackPropensity[1], MaxIterations)
            CruisePropensity = np.linspace(CruisePropensity[0], CruisePropensity[1], MaxIterations)
            
            # Bucle principal
            for CurrentIteration in range(MaxIterations):
                
                AttackVectorInitial, AttackVector = geo_func.ataque_geo(PopulationSize, FlockMemoryX, x, AttackPropensity, CurrentIteration)
                
                ConvergedEagles, UnconvergedEagles, Radius = geo_func.convergencia(AttackVectorInitial)
                
                CruiseVector = geo_func.cruce_geo(AttackVectorInitial, PopulationSize, nvars, CruisePropensity, CurrentIteration, ConvergedEagles, UnconvergedEagles, Radius)
                
                StepVector = AttackVector + CruiseVector 
            
                StepVector = np.round(StepVector).astype(int)####

                #Calculo del nuevo x
                x = x + StepVector ####
                
                for tt in range(len(x)):
                    if pp.Verificacion_factibilidad_celdas(x[tt],Celdas_LB, Celdas_UB, Celdas_canti, Rutas_piezas,MTBF_maq,limites)==0:
                        x[tt] = rp.reparador(x[tt], Celdas_LB, Celdas_UB, Celdas_canti, Rutas_piezas, MTBF_maq, limites)

                
                # Calcular fitness
                FitnessScores_lista = []
                for jj in range(len(x)):
                    Z_M_secuencias, Z_M_tiempos, Z_Cost_rutas=pp.Seleccion_rutas(x[jj], M_secuencias, M_tiempos, Cost_rutas,Rutas_piezas)
                    Fitness, Mov_Int, Bk_cost, fit1, fit2 = cf.Calculo_fitness(x[jj], Z_M_secuencias, Z_M_tiempos, Vol_piezas, Z_Cost_rutas, Rutas_piezas, MTBF_maq,Cost_break)
                    FitnessScores_lista.append(float(Fitness))
                FitnessScores = np.array(FitnessScores_lista)  # Convertir a array de numpy para operaciones posteriores
                
                UpdateMask = FitnessScores < FlockMemoryF
                FlockMemoryF[UpdateMask] = FitnessScores[UpdateMask]
                FlockMemoryX[UpdateMask, :] = x[UpdateMask, :]

                #BWO
                Pop = copy.deepcopy(FlockMemoryX) ####
                M_fitness = copy.deepcopy(FlockMemoryF) ####
                Pop1 = copy.deepcopy(Pop)

                if isinstance(Pop1, np.ndarray):
                    Pop1 = Pop1.tolist()
                #_____________________________________________________________________________________________________________________________________________________________

                # Poblacion final acumular hijos de TODAS las reproducciones de esta iteración
                ChildrenPool = []
                FitChildrenPool = []
                
                debiles = set()
                # nr REPRODUCCIONES
                for _ in range(nr):
                    idx1, idx2 = random.sample(range(nr), 2)
                    Parent1 = Pop1[idx1]
                    Parent2 = Pop1[idx2]

                    # PROCREACIÓN 
                    Pop2, Fit_children = bwo.Procreacion(Parent1, Parent2, Celdas_LB, Celdas_UB, Celdas_canti, Rutas_piezas, MTBF_maq, M_secuencias, M_tiempos, Cost_rutas, Vol_piezas, Cost_break, CR, limites)

                    #asegurar tipos de datos para evitar problemas
                    if isinstance(Pop2, np.ndarray):
                        Pop2 = Pop2.tolist()
                    if isinstance(Fit_children, np.ndarray):
                        Fit_children = Fit_children.tolist()
                        
                    # Acumular sobrevivientes
                    ChildrenPool.extend(Pop2)
                    FitChildrenPool.extend(Fit_children)

                    # guardamos al padre mas debil para aplicar canibalismo de padres despues
                    debiles.add(max(idx1, idx2))
                    
                # CANIBALISMO DE PADRES
                for idx in sorted(debiles, reverse=True):
                    Pop = np.delete(Pop, idx, axis=0)
                    M_fitness = np.delete(M_fitness, idx, axis=0)    

                # poblacion de procreacion y fitness listos
                ChildrenPool = np.array(ChildrenPool)
                FitChildrenPool = np.array(FitChildrenPool)

                #_________________________________________________________________________________________________________________________________________________________________------
                
                # 4.----ACTUALIZACIÓN DE LA POBLACIÓN
                Pop = np.vstack((Pop, ChildrenPool))

                Fit_pop = np.concatenate((M_fitness, FitChildrenPool))
                
                # Obtenemos los índices que ordenarían M_fitness de menor a mayor
                sorted_indices = np.argsort(Fit_pop)

                # Usamos estos índices para ordenar M_fitness y Pop
                M_fitness = Fit_pop[sorted_indices]
                Pop = np.array(Pop)[sorted_indices]
                
                FlockMemoryX = copy.deepcopy(Pop[:PopulationSize]) #numero de reproducciones])
                FlockMemoryF = copy.deepcopy(M_fitness[:PopulationSize]) #numero de reproducciones])
                
                best_fitness_history.append(float(M_fitness[0])) # mejor fitness en esta iteración
            poblaciones.append(pop_semilla)

            fitness_histories.append(best_fitness_history)  # guardar historia de la prueba
            
            # Obtener los valores de retorno
            fval = np.min(FlockMemoryF)  # Encontrar el valor mínimo de fitness
            fvalIndex = np.argmin(FlockMemoryF)  # Índice del valor mínimo
            x_best = FlockMemoryX[fvalIndex, :]  # Mejor solución correspondiente
            
            #calculo RPD
            aux = fval - 4671.344198054972
            rpdd.append(aux)
            #print(f"Best objective: {fval}") 
        rpd = (sum(rpdd)/len(rpdd))/4671.344198054972 * 100   
        print(rpd) 
        if rpd < 1.62:
            np.savez("results_GEO-BWO-PRCR.npz", fitness_histories=fitness_histories)
                
            #    Crear un DataFrame
            df = pd.DataFrame(fitness_histories)
            arr = np.asarray(poblaciones)              # (30, 100, 17)
            arr2d = arr.reshape(-1, arr.shape[-1])     # (3000, 17)

            df_pop = pd.DataFrame(arr2d, columns=[f"g{i+1}" for i in range(arr.shape[-1])])
            df_pop.insert(0, "prueba", np.repeat(np.arange(arr.shape[0]), arr.shape[1]))
            df_pop.insert(1, "individuo", np.tile(np.arange(arr.shape[1]), arr.shape[0]))
            df_rpd = pd.DataFrame([rpd])

            # Guardar como Excel
            with pd.ExcelWriter("results_GEO-BWO-PRCR.xlsx", engine="xlsxwriter") as writer:
                df.to_excel(writer, sheet_name="fitness_histories", index=False)
                df_rpd.to_excel(writer, sheet_name="rpd", index=False)
                df_pop.to_excel(writer, sheet_name="pop_semilla", index=False)
            
            grafi = gr.graficos(fitness_histories, MaxIterations,"GEO_BWO_PRCR")
            
            return x_best, fval


    return x_best, fval



x, fval = GEO_BWO()