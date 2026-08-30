from collections import Counter
import random
            
            
def reparador(w, Celdas_LB, Celdas_UB, Celdas_canti, Rutas_piezas, MTBF_maq, limites):   

    lim_inferior = 1
    for i, ww in enumerate(w):
        if w[i]>limites[i] or w[i]<=0:
            #print(f' {w[i]} es mayor que {limites[i]}')
            correccion = random.randint(lim_inferior, limites[i])
            w[i]=correccion
    
    #Cantidad de máquinas por celda
    veri =0
    while veri == 0:
        w_cell = []
        for i in range(len(MTBF_maq)):
            w_cell.append(w[i+len(Rutas_piezas)])

        frecuencia_cell = Counter(w_cell)

        if frecuencia_cell[1]>Celdas_UB or frecuencia_cell[1]<Celdas_LB or frecuencia_cell[2]>Celdas_UB or frecuencia_cell[2]<Celdas_LB :
            indice_corregir = random.randint(0, len(w_cell)-1)
            w[len(Rutas_piezas)+indice_corregir] = random.randint(lim_inferior,Celdas_canti)
            #print(w)
            #print("No por CELDAS UB")
        else:
            veri +=1

    return w



#Rutas_piezas = [3, 3, 2, 2, 2, 2, 4, 2]
#Vol_piezas = [75, 130, 110, 145, 110, 105, 140, 115] 
#MTBF_maq = [90, 51, 73, 60, 76, 62, 71, 58, 65]

#Celdas_canti = 2
#Celdas_LB = 2
#Celdas_UB = 6

#w=        [-1, 0, 2, 1, 2, 2, 5, 1, 2, 1, 1, 1, 2, 1, 1, 1, 10]
#w=        [3, 3, 2, 1, 2, 2, 2, 1, 2, 1, 1, 2, 2, 2, 2, 1, 1]
#limites = [3, 3, 2, 2, 2, 2, 4, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2] 
#x = reparador(w, limites)
#print(x)

#x = reparador(w, Celdas_LB, Celdas_UB, Celdas_canti, Rutas_piezas, MTBF_maq, limites)
#print(x)