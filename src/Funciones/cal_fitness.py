import numpy as np
def Calculo_fitness(w, Z_M_secuencias, Z_M_tiempos, Vol_piezas, Z_Cost_rutas, Rutas_piezas, MTBF_maq,Cost_break):
    Fitness=0
    fit1=0
    fit2=0

    #______Creación de matriz de datos para cálculo de costos (fitness)

    M_sec_tiem_cell=[]
    for i in range(len(Rutas_piezas)):
        F_sec_tiem_cell=[]
        for j in range(len(MTBF_maq)):
            stc=[] #Vector de datos: Secuencia, Tiempo de producción, Celda, Máquina

            
            if Z_M_secuencias[i][j]>0:
                stc.append(Z_M_secuencias[i][j]) #Número de secuencia
                stc.append(Z_M_tiempos[i][j]) #Tiempo de producción
                stc.append(w[j+len(Rutas_piezas)]) #Celda
                stc.append(j+1) #Máquina

                F_sec_tiem_cell.append(stc)


        F_sec_tiem_cell=sorted(F_sec_tiem_cell, key=lambda x: x[0])

        #print("Después", F_sec_tiem_cell)
        M_sec_tiem_cell.append(F_sec_tiem_cell)


    #Cálculo de MIC (fit1)

    Mov_Int=[]
    for i in range(len(M_sec_tiem_cell)):
        mic_rutas=0
        for j in range(1, len(M_sec_tiem_cell[i])):
            if  M_sec_tiem_cell[i][j][2]!=M_sec_tiem_cell[i][j-1][2]:
                mic_rutas=mic_rutas+1
            else:
                mic_rutas=mic_rutas
        Mov_Int.append(mic_rutas)
    
    for i in range(len(Mov_Int)):
        fit1=fit1+(Mov_Int[i]*Z_Cost_rutas[i]*Vol_piezas[i])    
    
    #Cálculo de Breakdown y Outsourcing (fit2)
    Bk_cost=[]
    F_Bk=[] 
    
    for i in range(len(Z_M_secuencias)):
        Bk=0

        for j in range(len(Z_M_secuencias[i])):
            
            Bk=Bk+((Vol_piezas[i]*Z_M_tiempos[i][j])/(MTBF_maq[j]*60))*((Cost_break[j]))

        F_Bk.append(Bk)
    Bk_cost.append(F_Bk)
    
    fit2=np.sum(Bk_cost)
    
    Fitness=fit1+fit2

    return(Fitness, Mov_Int, Bk_cost, fit1, fit2)
