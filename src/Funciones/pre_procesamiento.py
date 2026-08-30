
import numpy as np
from . import cal_fitness as cf
from collections import Counter
import random
################################Selección de rutas (Variable Z)
def Seleccion_rutas(w, M_secuencias, M_tiempos, Cost_rutas, Rutas_piezas):
    # Ajuste posicional para w (se le resta 1 a todos los elementos)
    w = [elemento - 1 for elemento in w]
    
    Z_M_secuencias=[]
    Z_M_tiempos=[]
    Z_Cost_rutas=[]

    cont=0
    for i in range(len(Rutas_piezas)):

        cont=int(cont+int(w[i]))

        #print("Cont", cont)
        if cont >= len(M_secuencias): # En la mutación puede que en el último elemento te diga que quiere la ruta 4 de la última pieza y en realidad esa pieza solo tiene 2 rutas
            cont = len(M_secuencias)-1
        
        Z_M_secuencias.append(M_secuencias[cont])
        Z_M_tiempos.append(M_tiempos[cont])
        Z_Cost_rutas.append(Cost_rutas[cont])

        cont=cont-w[i]
        cont=cont+Rutas_piezas[i]


    return(Z_M_secuencias, Z_M_tiempos, Z_Cost_rutas)


################################Verificacion factibilidad celdas (Variable Y)
def Verificacion_factibilidad_celdas(w, Celdas_LB, Celdas_UB, Celdas_canti, Rutas_piezas, MTBF_maq, limites):

    lim_inferior = 1
    veri = 0
    for i, ww in enumerate(w):
        if w[i]>limites[i] or w[i]<lim_inferior:
            #No es factible porque se sale de los limites
            veri += 1
            
    
    #Cantidad de máquinas por celda
    w_cell = []
    for i in range(len(MTBF_maq)):
        w_cell.append(w[i+len(Rutas_piezas)])

    frecuencia_cell = Counter(w_cell)
    if frecuencia_cell[1]>Celdas_UB or frecuencia_cell[1]<Celdas_LB or frecuencia_cell[2]>Celdas_UB or frecuencia_cell[2]<Celdas_LB :
        veri +=1


    if veri == 0:
        Indicador_factibilidad = 1 #el vector solucion si es factible
    else:
        Indicador_factibilidad = 0 #el vector solucion No es factible

    return Indicador_factibilidad

###########################Generación de población inicial factible
def Geracion_población_inicial(N_Pop, Rutas_piezas, Celdas_canti, Celdas_LB, Celdas_UB, MTBF_maq, limites):

    import random

    cont = 0

    Pop = []

    # Generar la población
    while cont < N_Pop:
        w = []
        for i in range(len(Rutas_piezas)):
            w.append(random.randint(1, Rutas_piezas[i]))
        for i in range(len(MTBF_maq)):
            w.append(random.randint(1, Celdas_canti))
        
                
        #Z_M_secuencias, Z_M_tiempos, Z_Cost_rutas=Seleccion_rutas(w, M_secuencias, M_tiempos, Cost_rutas)

        Indicador_factibilidad_celdas=Verificacion_factibilidad_celdas(w, Celdas_LB, Celdas_UB, Celdas_canti, Rutas_piezas, MTBF_maq, limites)

        if Indicador_factibilidad_celdas==1:

            Pop.append(w)
            cont=cont+1
        else:
            cont=cont


    return(Pop)



########################Generacion de Poblacion ordenada
def pop_ordenada(Pop, M_secuencias, M_tiempos, Cost_rutas, Vol_piezas, Rutas_piezas,MTBF_maq,Cost_break):
    Matriz_total_widows=[]
    Matriz_total_G_fitness=[]
    G_fitness=10000000000000000000000

    G_widow=[]
    G_Mov_Int=[]
    G_Bk_cost=[]

    M_fitness=[]

    #Pop = Geracion_población_inicial(N_Pop, Rutas_piezas, Celdas_canti, Celdas_LB, Celdas_UB)

    for i in range(len(Pop)):
        
        # IMPORTANTE PARA CALCULAR EL FITNESS

        Z_M_secuencias, Z_M_tiempos, Z_Cost_rutas=Seleccion_rutas(Pop[i], M_secuencias, M_tiempos, Cost_rutas,Rutas_piezas)
        Fitness, Mov_Int, Bk_cost, fit1, fit2=cf.Calculo_fitness(Pop[i], Z_M_secuencias, Z_M_tiempos, Vol_piezas, Z_Cost_rutas,Rutas_piezas, MTBF_maq,Cost_break)
        
        M_fitness.append(Fitness.copy())
        
        
        if Fitness<G_fitness:
            
            G_fitness=Fitness.copy()
            G_widow=Pop[i].copy()
            G_Mov_Int=Mov_Int.copy() # Cantidad de movientos inter-celulares (Por ruta individual sin volumen de producción)
            G_Bk_cost=Bk_cost.copy() # Costos por el Break-Down
            #print("Local fitness: ", Fitness)

            #-------------BORRAR# #BORRAR# #BORRAR# #BORRAR# #BORRAR# #BORRAR# #BORRAR# #BORRAR# #BORRAR# #BORRAR# 
            G_Z_M_secuencias = Z_M_secuencias.copy()
            G_Z_M_tiempos = Z_M_tiempos.copy()
            G_Vol_piezas = Vol_piezas.copy()
            G_Z_Cost_rutas = Z_Cost_rutas.copy()
            G_fit1=fit1
            G_fit2=fit2
            #-------------BORRAR# #BORRAR# #BORRAR# #BORRAR# #BORRAR# #BORRAR# #BORRAR# #BORRAR# #BORRAR# #BORRAR# 

    if G_fitness==10000000000000000000000:
        print("No se encontraron soluciones factibles")

    else:

        Matriz_total_widows.append(M_fitness)
        Matriz_total_G_fitness.append(G_fitness.copy())

        # Convertimos M_fitness a un array de numpy para facilitar la ordenación
        M_fitness = np.array(M_fitness)
        
        # Obtenemos los índices que ordenarían M_fitness de menor a mayor
        sorted_indices = np.argsort(M_fitness)
        
        # Usamos estos índices para ordenar M_fitness y Pop
        M_fitness = M_fitness[sorted_indices]
        Pop = np.array(Pop)[sorted_indices]
    return Pop, M_fitness, Matriz_total_widows, Matriz_total_G_fitness, G_fitness, G_widow