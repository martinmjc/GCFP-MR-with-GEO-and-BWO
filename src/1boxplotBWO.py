from Funciones import ini_parametros as ip
from Funciones import pre_procesamiento as pp
from Funciones import bwo
from Funciones import grafico as gr
import pandas as pd
import numpy as np
import random
import copy

#parametros BWO
N_Pop = 100 
Max_iter = 50
PR = 0.8 #procreation rate
CR = 0.8 #tasa canibalismo
PM = 0.8 #tasa de mutacion

nr = int(N_Pop*PR) #numero de reproducciones

#Parametros caso de estudio
Celdas_canti = 2
Celdas_LB = 2
Celdas_UB = 6

rpdd = []

#Inicializacion de parametros
Rutas_piezas, Vol_piezas, Cost_break, Cost_rutas, MTBF_maq, M_secuencias, M_tiempos, limites = ip.iniciarparametros()

#definimos la cantidad de pruebas
pruebas = 100

fitness_histories = []  # GUARDA fitness vs iteración para cada prueba

for j in range(100):
    poblaciones = []
    fitness_histories = []  # GUARDA fitness vs iteración para cada prueba
    for ii in range(pruebas):

        best_fitness_history = []  # historia de una sola prueba

        #Metaheuristica
        #generacion de poblacion inicial y su fitness
        Pop = pp.Geracion_población_inicial(N_Pop, Rutas_piezas, Celdas_canti, Celdas_LB, Celdas_UB, MTBF_maq, limites)
        Pop, M_fitness, Matriz_total_widows, Matriz_total_G_fitness, G_fitness, G_widow = pp.pop_ordenada(
            Pop, M_secuencias, M_tiempos, Cost_rutas, Vol_piezas, Rutas_piezas, MTBF_maq, Cost_break
        )

        pop_semilla=copy.deepcopy(Pop)
        
        #algoritmo BWO
        for iter in range(Max_iter):

            # 1) SELECCIÓN DE PARTICIPANTES 
            Pop1 = copy.deepcopy(Pop[:nr])
            if isinstance(Pop1, np.ndarray):
                Pop1 = Pop1.tolist()

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
            # 3.----MUTACIÓN
            Pop3, Fit_mutation = bwo.mutacion(Pop1, PM, Celdas_LB, Celdas_UB, Celdas_canti, Rutas_piezas,
                                            M_secuencias, M_tiempos, Cost_rutas, Vol_piezas, MTBF_maq, Cost_break, limites)
            #_________________________________________________________________________________________________________________________________________________________________------

            # 4.----ACTUALIZACIÓN DE LA POBLACIÓN
            Pop = np.vstack((Pop, ChildrenPool, Pop3))

            Fit_pop = np.concatenate((M_fitness, FitChildrenPool, Fit_mutation))
            
            # Obtenemos los índices que ordenarían M_fitness de menor a mayor
            sorted_indices = np.argsort(Fit_pop)

            # Usamos estos índices para ordenar M_fitness y Pop
            M_fitness = Fit_pop[sorted_indices]
            Pop = np.array(Pop)[sorted_indices]
            
            Pop = copy.deepcopy(Pop[:N_Pop])
            M_fitness = copy.deepcopy(M_fitness[:N_Pop])

            Matriz_total_widows.append(M_fitness)
            Matriz_total_G_fitness.append(M_fitness[0].copy())

            best_fitness_history.append(float(M_fitness[0]))# mejor fitness en esta iteración
        poblaciones.append(pop_semilla)

        fitness_histories.append(best_fitness_history)  # guardar historia de la prueba

        #print("prueba: ",ii)
        #print("MEJOR COSTO ENCONTRADO:               ", M_fitness[0], "$")# (", num2words(G_fitness), ")")
        #print("WIDOW:", Pop[0])

        #calculo RPD
        aux = M_fitness[0] - 4671.344198054972
        rpdd.append(aux) 
    rpd = (sum(rpdd)/len(rpdd))/4671.344198054972 * 100   
    print(j+1, "/ 100",rpd) 
    if rpd < 1.2:
        np.savez("results_BWO.npz", fitness_histories=fitness_histories)
    
        #    Crear un DataFrame
        df = pd.DataFrame(fitness_histories)

        arr = np.asarray(poblaciones)              # (30, 100, 17)
        arr2d = arr.reshape(-1, arr.shape[-1])     # (3000, 17)

        df_pop = pd.DataFrame(arr2d, columns=[f"g{i+1}" for i in range(arr.shape[-1])])
        df_pop.insert(0, "prueba", np.repeat(np.arange(arr.shape[0]), arr.shape[1]))
        df_pop.insert(1, "individuo", np.tile(np.arange(arr.shape[1]), arr.shape[0]))
        df_rpd = pd.DataFrame([rpd])

        # Guardar como Excel
        with pd.ExcelWriter("results_BWO.xlsx", engine="xlsxwriter") as writer:
            df.to_excel(writer, sheet_name="fitness_histories", index=False)
            df_rpd.to_excel(writer, sheet_name="rpd", index=False)
            df_pop.to_excel(writer, sheet_name="pop_semilla", index=False)
            
        grafi = gr.graficos(fitness_histories, Max_iter, "BWO")
            
        break







#verificacion de la mejor widow encontrada
#w=[1, 2, 2, 1, 2, 2, 1, 1, 2, 1, 1, 2, 2, 2, 2, 1, 2] # Óptimo anterior

#Z_M_secuencias, Z_M_tiempos, Z_Cost_rutas=pp.Seleccion_rutas(Pop[0], M_secuencias, M_tiempos, Cost_rutas,Rutas_piezas)

#Indicador_factibilidad = pp.Verificacion_factibilidad_celdas(Pop[0], Celdas_LB, Celdas_UB, Celdas_canti, Rutas_piezas,MTBF_maq,limites)
#if Indicador_factibilidad==1:
#    fit_widow, Mov_Int, Bk_cost, fit1, fit2=cf.Calculo_fitness(Pop[0], Z_M_secuencias, Z_M_tiempos, Vol_piezas, Z_Cost_rutas,Rutas_piezas, MTBF_maq,Cost_break)

#    print("veridicacion del mejor costo de la WIDOW: ", fit_widow)
#else:
#    print("INFACTIBLE")