import matplotlib.pyplot as plt
import numpy as np

def graficos(fitness_histories, Max_iter, titulo):
    # grafico
    plt.figure()
    for i, hist in enumerate(fitness_histories):
        plt.plot(range(1, Max_iter + 1), hist)
    plt.xlabel("Iteración")
    plt.ylabel("Fitness")
    plt.title(titulo)
    plt.xlim(1, Max_iter)        
    plt.ylim(0, 50000)            
    #plt.legend()
    plt.grid(True)
    plt.show()

    # BOXPLOT de estabilidad fitness
    # 1) extraer fitness final (última iteración) de cada corrida
    fitness_final = [hist[-1] for hist in fitness_histories] 
    fitness_final = np.array(fitness_final, dtype=float)

    # 2) boxplot
    plt.figure()
    plt.boxplot(
        fitness_final,
        showmeans=True,
        showfliers=True
    )
    plt.xticks([1], ["Mejor configuración BWO"])
    plt.ylim(3000, 6000)
    plt.ylabel("Mejores Fitness")
    plt.title("BWO: Boxplot de Fitness Final (Estabilidad en 30 corridas)")
    plt.grid(True, axis="y")
    plt.show()
    return

