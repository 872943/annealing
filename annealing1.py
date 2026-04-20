# -*- coding: utf-8 -*-
"""
Created on Thu Mar 26 00:49:54 2026

@author: Nico
"""

import numpy as np
from itertools import permutations
import math
import random

#%%FUNCTIONS
def calculate_route_distance(route, D, is_closed_path):
    """
    Calcula la distancia total de una ruta específica.
    'route' es una lista de ciudades J y 'matrix' es la matriz D.
    """
    total_dist = 0
    # Recorremos la ruta sumando la distancia entre cada par de ciudades
    for i in range(len(route) - 1):
        total_dist += D[route[i], route[i+1]]

    if is_closed_path: # Si la variable que le pasamos es True, suma la vuelta
        total_dist += D[route[-1], route[0]]
    return total_dist


def swap_cities(route, is_start_fixed):
    # Creamos una copia para no liarla con la ruta original
    new_path = route.copy()
    
    # Elegimos dos índices al azar 
    # Si el inicio es fijo, el primer índice que podemos elegir es el 1. (del 1 al final, saltándonos el 0)
    # Si es libre, el primer índice es el 0.
    # range(1, 6) nos da los índices 1, 2, 3, 4, 5
    start_idx = 1 if is_start_fixed else 0
    idx1, idx2 = random.sample(range(start_idx, len(route)), 2)
    
    # El truco de Python para intercambiar valores en una línea:
    new_path[idx1], new_path[idx2] = new_path[idx2], new_path[idx1]
    
    return new_path
#%%DATA:
#Se le asigna a cada ciudad un numero
#Definir el diccionario este realmente no ayuda mucho xD
cities = {"Strasbourg" : 0, "Nancy" : 1, "Paris" : 2, "Mulhouse" : 3, "Dijon" : 4, "Besancon" : 5}

#Se define la matriz D de distancias entre ciudades
#Como es una matriz simétrica de diagonal 0 solo he tomado la triangular inferior, para no saturar con muchos datos
#NICO CREO QUE ES MUY POCO PRACTICO PONERLO ASI 
'''
D = [
    [150],
    [490, 280],
    [110, 200, 540],
    [335, 230, 315, 260],
    [240, 190, 410, 160,  95],
    [120, 210, 325, 400, 110, 370],
    [205, 120, 370, 420, 450, 185, 360]
]
'''
D = np.array([
    [0,   156, 491, 116, 310, 249], # 0: Strasbourg
    [156, 0,   386, 164, 219, 160], # 1: Nancy
    [491, 386, 0,   539, 315, 411], # 2: Paris
    [116, 164, 539, 0,   199, 134], # 3: Mulhouse
    [310, 219, 315, 199, 0,   95],  # 4: Dijon
    [249, 160, 411, 134, 95,  0]    # 5: Besançon
])

#%%PRIMERA PARTE:
#N es el numero de ciudades
#N = len(D)+1
N = len(D)

#L es el numero de posibles caminos
#Corresponde a (N-1)! no a N! porque se fija la primera ciudad
#Esto lo hago porque en el camino abierto es importante la ciudad de la que se empiece
#En el camino cerrado da igual, porque la ultima engancha con la primera
#Pero habria varios caminos que serian equivalentes mediante un desplazamiento de todos los numeros hacia la derecha
#Por ejemplo (0 1 2 3 4 5) (5 0 1 2 3 4) (3 4 5 0 1 2) serian equivalentes, y esto se soluciona fijando la primera ciudad
L = math.factorial(N-1)

#init es el numero de la ciudad inicial
init = 0

#J son todas las permutaciones, es decir, todos los caminos posibles
#init va a estar fijado como el primer valor de todas las filas, es decir, la primera ciudad de cualquier camino
#Tambien se establece como criterio que el 2do valor sea menor que el ultimo
#Esto es para evitar, en el caso del camino cerrado, que se consideren de forma separada 2 caminos que son el mismo pero en sentido inverso: (2 4 5 1 0 3) y (2 3 0 1 5 4)
#Si init = 2, una de sus filas sería por ejemplo: (2 3 5 0 1 4)

#en esta linea, creamos un camino J[0,1,2,3,4,5] y hacemos todas las permutaciones posibles. Nos quedamos solo con aquellas que cumplan las dos condiciones y las ponemos en una matriz J
J_fix = np.array([p for p in permutations(np.arange(N)) if p[1] < p[-1] and p[0] == init])
J_fix = J_fix.astype(int) 

#Para cada combinacion de ciudades, se define un camino abierto Co, que es la suma de las distancias de una ciudad a la otra
#Para el caso anterior seria d(2->3) + d(3->5) + d(5->0) + d(0,1) + d(1,4)
Co_fix = np.zeros((L, 1))

#El camino cerrado Cc es lo mismo pero volviendo desde la ultima posicion de nuevo a la primera
#Siguiendo con el caso anterior, se le añadiria + d(4->2)
#En este caso hay L/2 caminos posibles y no L porque hemos descartado los caminos recorridos en sentido contrario, lo que los reduce a la mitad
Cc_fix = np.zeros((L//2, 1))

#Ahora rellenamos los vectores Co y Cc con las sumas de distancias
#Supongamos el camino (2 3 5 0 1 4)
#La estrategia va a ser calcular la distancia entre 3 y 4: d(3->5->0->1->4) = d(3->5) + ... + d(1->4), ya que es común al camino cerrado y abierto
#Calculamos aparte dfs = d(2->3) y dfl d(2->4)
#Para el camino cerrado, a d(3->...->4) le sumamos dfs y dfl para enganchar toda la secuencia y que vuelva del final al inicio
#Para nuestro vector de caminos abiertos Co, completamos la primera mitad con d(3->...->4) + dfs que es el camino abierto hacia la derecha
#Y completamos la segunda mitad con d(3->...->4) + dfl, que es el camino abierto hacia la izquierda
#Asi evitamos calculos innecesarios y con un solo d(3->...->4) calculamos 3 caminos de una tacada
'''
for j in range(L//2):
    for i in range(1,N-1):
        Cc[j] += D[max(J[j, i], J[j, i+1])-1][min(J[j, i], J[j, i+1])] 
    dfs = D[max(J[j, 0], J[j, 1])-1][min(J[j, 0], J[j, 1])]
    dfl = D[max(J[j, N-1], J[j, 0])-1][min(J[j, N-1], J[j, 0])]
    Co[j] = Cc[j] + dfs
    Co[L//2+j] = Cc[j] + dfl
    Cc[j] += dfs + dfl
    '''
#yo lo veo mucho mas fácil asi nose
for j in range(L//2):
    # 1. Calculamos el "núcleo" del camino
    for i in range(1, N-1):
        # Acceso directo:
        Cc_fix[j] += D[J_fix[j, i], J_fix[j, i+1]] 
    
    # 2. Los enganches con la ciudad inicial
    dfs = D[J_fix[j, 0], J_fix[j, 1]]      # Distancia Inicio -> Primera parada
    dfl = D[J_fix[j, N-1], J_fix[j, 0]]    # Distancia Última parada -> Inicio
    
    # 3. Guardamos los resultados (esto se queda igual)
    Co_fix[j] = Cc_fix[j] + dfs            # Abierto hacia adelante
    Co_fix[L//2 + j] = Cc_fix[j] + dfl     # Abierto hacia atrás
    Cc_fix[j] += dfs + dfl             # Cerrar el círculo

    
#Por ultimo, tanto para Co como para Cc, creamos indices con las posiciones de los caminos con minima distancia: indexCcmin, indexComin
#Comin y Ccmin son la(s) permutacion(es) con un camino minimo, es decir, aquellas que estan en las posiciones que tenemos en los index...

#Para el camino abierto Co hay que hacer un poco mas de trabajo porque solo tenemos L/2 permutaciones en J (lo que nos ahorra calculo)
#Pero como tenemos 2 caminos abiertos (hacia la derecha y hacia la izquierda), Co tiene L elementos, asi que hay que trabajar por separado las 2 mitades
indexComin_fix = np.where(Co_fix==min(Co_fix))[0] #Lista con los números de las filas donde la distancia es mín
Comin_fix = np.array([J_fix[i] if i < L//2 else np.concatenate(([init], J_fix[i-L//2][:0:-1])) for i in indexComin_fix])

indexCcmin_fix = np.where(Cc_fix==min(Cc_fix))[0]
Ccmin_fix = np.array([J_fix[i] for i in indexCcmin_fix])

#Ahora nos falta hallar el camino mas corto pero sin fijar el punto de inicio

# Generamos todas las permutaciones posibles de las 6 ciudades (6! = 720)
# Usamos la condición p[0] < p[-1] para no calcular el camino inverso. La llamo J_free porque el inicio es libre
J_free = np.array([p for p in permutations(np.arange(N)) if p[0] < p[-1]])

# Creamos un vector de ceros para guardar la distancia de cada una de estas 360 rutas únicas
Co_free = np.zeros(len(J_free))

# Calculamos la distancia de cada ruta usando nuestra función 'calculate_route_distance'
for i in range(len(J_free)):
    Co_free[i] = calculate_route_distance(J_free[i], D, False)

# Buscamos los índices del mínimo 
indexComin_free = np.where(Co_free == min(Co_free))[0]

# 5. Buscamos qué ruta(s) tienen esa distancia mínima
Comin_free = J_free[indexComin_free]


print("\n" + "="*30)
print("RESULTS")
print("="*30)

# Resultados Camino CERRADO
print(f"\nBest CLOSED PATH (FIX Start): {np.min(Cc_fix)} km")
print(f"Optimal Route(s): {Ccmin_fix}")

print("-" * 30)

# Resultados Camino ABIERTO
print(f"Best OPEN PATH (Fix Start): {np.min(Co_fix)} km")
print(f"Optimal Route(s): {Comin_fix}")
print("="*30 + "\n")

# Resultados Camino ABIERTO sin fijar inicio
print("-" * 30)
print(f"Absolute Best OPEN PATH (Flexible Start): {np.min(Co_free)} km")
print(f"Optimal Route(s): {Comin_free}")
print("="*30 + "\n")

#%%SIMULATED ANNEALING:

#PARAMETERS (beta es inversamente proporcional a T)
beta = 0.01          # Empezamos con una beta pequeña (sistema muy caliente)
beta_max = 10.0      # Pararemos cuando la beta sea alta (sistema frío)
beta_growth = 1.001  # En cada paso, multiplicaremos beta por esto para que crezca poco a poco
#Estos resultados los vamos a comparar a los calculados mediante la 'fuerza bruta', vamos el codigo de antes. Hay tres resultados
#que comparar, la idea es poder hacer todo con el mismo código, simplemente cambiando estos parámetros de abajo.
is_closed_path = True   # ¿Volvemos al inicio? (True/False)
is_start_fixed = True   # ¿Empezamos siempre en Estrasburgo? (True/False)


# Generamos una ruta inicial según la configuración
if is_start_fixed:
    cities_to_permute = list(range(1, N)) # Creamos una lista con las ciudades sin contar estrasburgo
    random.shuffle(cities_to_permute) # Las desordenamos al azar
    current_route = np.array([0] + cities_to_permute) # Le añadimos a la ruta Estrasbuego como primera ciudad 
else:
    all_cities = list(range(N))
    random.shuffle(all_cities)
    current_route = np.array(all_cities)


# Calculamos su distancia inicial
current_dist = calculate_route_distance(current_route, D, is_closed_path)

# Vamos a ir guardando la mejor ruta junto con su distancia mínima en una variable 
best_route = current_route.copy()
best_dist = current_dist

#Vamos con el algoritmo de metropolis
while beta < beta_max:
    # Propongo un cambio (Swap)
    # Importante: swap_cities debe elegir índices entre 1 y (N-1) para no mover el [0]
    new_route = swap_cities(current_route, is_start_fixed) 
    new_dist = calculate_route_distance(new_route, D, is_closed_path)
    
    # Calculamos la diferencia de "energía" (distancia)
    delta_E = new_dist - current_dist
    
    # Criterio de Metrópolis: decidicmo si aceptamos o no el cambio
    if delta_E <= 0:
        accept = True
    else:
        # La ruta es peor, pero vemos si la aceoptamos o no
        # Generamos un número aleatorio entre 0 y 1
        r = random.random()
        
        # Calculamos el umbral de aceptación
        umbral = math.exp(-beta * delta_E)
        
        if r < umbral:
            accept = True  # Aceptamos una ruta peor para seguir explorando
        else:
            accept = False # No la aceptamos
    if accept:
        current_route = new_route
        current_dist = new_dist
        
        # Vemos si la ruta que acabamos de aceptar es la mejor que hemos visto hasta ahora
        if current_dist < best_dist:
            best_dist = current_dist
            best_route = current_route.copy()
    # Hacemos que el sistema se enfríe un poquito para la siguiente iteración
    beta = beta * beta_growth

# --- RESULTADOS FINALES ---
print("\n" + "="*35)
print("      ANNEALING COMPLETE")
print("="*35)
print(f"Best Route found: {best_route}")
print(f"Distance: {best_dist} km")
print(f"Final Beta reaching: {beta:.2f}")


#FALTA 