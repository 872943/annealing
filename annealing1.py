# -*- coding: utf-8 -*-
"""
Created on Thu Mar 26 00:49:54 2026

@author: Nico
"""

import numpy as np
from itertools import permutations
import math
import random
import matplotlib.pyplot as plt

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

def haversine_distance(lat1, lon1, lat2, lon2):

    u1=np.array((np.cos(np.radians(lat1))*np.cos(np.radians(lon1)),
                 np.cos(np.radians(lat1))*np.sin(np.radians(lon1)),
                 np.sin(np.radians(lat1))))
    u2=np.array((np.cos(np.radians(lat2))*np.cos(np.radians(lon2)),
                 np.cos(np.radians(lat2))*np.sin(np.radians(lon2)),
                 np.sin(np.radians(lat2))))
    
    R=6371000

    return R*np.arccos(np.dot(u1,u2))

def current_route_func(N, is_start_fixed):
    # Generamos una ruta inicial según la configuración
    if is_start_fixed:
        cities_to_permute = list(range(1, N)) # Creamos una lista con las ciudades sin contar estrasburgo
        random.shuffle(cities_to_permute) # Las desordenamos al azar
        current_route = np.array([0] + cities_to_permute) # Le añadimos a la ruta Estrasbuego como primera ciudad 
    else:
        all_cities = list(range(N))
        random.shuffle(all_cities)
        current_route = np.array(all_cities)
    return current_route

def metropolis (beta, beta_max,beta_growth, Niter, D,current_route, is_closed_path, is_start_fixed):
        
    best_route = current_route.copy()
    best_dist = calculate_route_distance(current_route, D, is_closed_path)
    current_dist = best_dist

    # A plot of C(Jopt) vs T is usually instructive.
    #asi que nos vamos a ir guardando tmb la mejor distancia para algunas temps para plotearlo luego.
    cont=0
    beta_values = []
    best_distances = []



    #Vamos con el algoritmo de metropolis
    while beta < beta_max:
        #eminbeta=current_dist

        for nn in range(Niter):

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
        
        if ((cont<200 and cont%5==0) or cont%10==0 ):
            beta_values.append(beta)
            best_distances.append(best_dist)

        
        beta = beta + beta_growth
        cont+=1
    return best_route, best_dist, beta_values, best_distances


def create_matrix_distances(city_data):
    """
    Crea una matriz de distancias entre ciudades usando la fórmula de Haversine.
    'city_data' es un diccionario con el nombre de la ciudad como clave y una tupla (latitud, longitud) como valor.
    """
    cities = list(city_data.keys())
    N = len(cities)
    D = np.zeros((N, N))
    
    for i in range(N):
        for j in range(i+1, N):
            lat1, lon1 = city_data[cities[i]]
            lat2, lon2 = city_data[cities[j]]
            D[i, j] = haversine_distance(lat1, lon1, lat2, lon2)
            D[j, i] = D[i, j]  # La matriz es simétrica
    
    return D




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
N = len(D)       #da el numero de filas 

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
#a

#PARAMETERS (beta es inversamente proporcional a T)
beta = 0.01          # Empezamos con una beta pequeña (sistema muy caliente)
beta_max = 10.0      # Pararemos cuando la beta sea alta (sistema frío)
beta_growth = 0.01  # En cada paso, multiplicaremos beta por esto para que crezca poco a poco
#hola, te lo he cambiado y he puesto suma para que estuviesen equidistantes las temperaturas
#Estos resultados los vamos a comparar a los calculados mediante la 'fuerza bruta', vamos el codigo de antes. Hay tres resultados
#que comparar, la idea es poder hacer todo con el mismo código, simplemente cambiando estos parámetros de abajo.
is_closed_path = True   # ¿Volvemos al inicio? (True/False)
is_start_fixed = True   # ¿Empezamos siempre en Estrasburgo? (True/False)

current_route=current_route_func(N, is_start_fixed)

# Calculamos su distancia inicial
#current_dist = calculate_route_distance(current_route, D, is_closed_path)

# Vamos a ir guardando la mejor ruta junto con su distancia mínima en una variable 
#best_route = current_route.copy()
#best_dist = current_dist



Niter=100
best_route, best_dist, beta_values, best_distances = metropolis(beta, beta_max, beta_growth, 1,D, current_route, is_closed_path, is_start_fixed)
    
    
    

# --- RESULTADOS FINALES ---
print("\n" + "="*35)
print("      ANNEALING COMPLETE")
print("="*35)
print(f"Best Route found: {best_route}")
print(f"Distance: {best_dist} km")
print(f"Final Beta reaching: {beta:.2f}")

#print(beta_values)


'''
#ploteamos la mejor energia frente a la temperatura
plt.figure(figsize=(10, 6))
plt.plot(beta_values, (best_distances-best_distances[-1])/best_distances[-1], marker='o', linestyle='--')
plt.xlabel('Beta')
plt.ylabel(r"$\sigma_{Best\ Distance}$")
plt.title('Annealing Progress')
plt.show()

'''

#para medir el tiempo ponemos en la terminal: Measure-Command { python metropolis.py }


#Ahora vamos a incluir mas ciudades: 
# Paris, Madrid, Athens, Helsinki, Beyrouth, New Delhi, Bangkok, Beijing, Tokyo, Seoul, Sidney, Buenos Aires,
#Brasilia, Caracas, Mexico City, Chicago, Quebec, Reykjavik 

#para definirlas, vamos a copiar sus coordenadas geográficas y luego calcular la distancia entre ellas usando la fórmula de Haversine, 
# #que nos da la distancia en línea recta entre dos puntos en la superficie de la Tierra.

#definimos un array con las coordenadas de cada ciudad (latitud, longitud)
#ciudad, latitud, longitud
data_mundo = {
    "Paris": (48.85727373179059, 2.3487507137355794),
    "Madrid": (40.41704657265242, -3.70803243496023),
    "Athens": (37.9862372667943, 23.72640888479879),  
    "Helsinki": (60.16896597966013, 24.946582578872317),
    "Beyrouth": (33.89805278387125, 35.501106563967475), 
    "New Delhi": (28.624435389566685, 77.19284892838382),
    "Bangkok": (13.783291710781231, 100.49234847321351),
    "Beijing": (39.90939504666152, 116.42011820700647),
    "Tokyo": (35.76161198744289, 139.95777186157952),
    "Seoul": (37.56433181860934, 126.99370869973836),
    "Sidney": (-33.857367781259526, 151.20869289677037),
    "Buenos Aires": (-34.602542951927646, -58.403601029193716),
    "Brasilia": (-15.767259807670667, -44.94460952350091),
    "Caracas": (10.480545406973002, -66.90581537009965),
    "Mexico City": (19.423762766036422, -99.14395596938738),
    "Chicago": (41.880761212875186, -87.64055514320192),
    "Quebec": (46.811107141383225, -71.2072430221403),
    "Reykjavik": (64.14635365890997, -21.937594180058724)
}

D_mundo=create_matrix_distances(data_mundo)
cities = list(data_mundo.keys())
N_M = len(cities)

#Ahora tenemos 18 ciudades, esto corresponde a 18! permutaciones posibles
#En caso de camino abierto, teniendo en cuenta los caminos inversos, tendriamos que calcular

No=np.exp(18*np.log(18))/2
#print(No)

#como vemos, tenemos un orden de magnitud bastante grande, por lo que no merece la pena 

beta = 0.01          # Empezamos con una beta pequeña (sistema muy caliente)
beta_max = 10.0      # Pararemos cuando la beta sea alta (sistema frío)
beta_growth = 0.01  # En cada paso, multiplicaremos beta por esto para
curren_route_M =current_route_func(N_M, is_start_fixed)
best_dist_M_array =[]

Nite_array=[1,20, 50, 100, 500, 1000]
'''

for Niter in Nite_array:
    best_route_M, best_dist_M,beta_values_M,beta_dist_M = metropolis(beta, beta_max, beta_growth, Niter, D_mundo, curren_route_M, is_closed_path, is_start_fixed)
    best_dist_M_array.append(beta_dist_M)

'''

'''

#ploteamos la mejor energia frente a la temperatura
plt.figure(figsize=(10, 6))
for fila in best_dist_M_array:
    plt.plot(beta_values_M, (fila-fila[-1])/fila[-1], marker='o', linestyle='--', ms=2, label=f'Niter={Nite_array[best_dist_M_array.index(fila)]}')

#plt.plot(beta_values_M, (best_distances_M-best_distances_M[-1])/best_distances_M[-1], marker='o', linestyle='--')
plt.xlabel('Beta')
plt.ylabel(r"$\sigma_{Best\ Distance}$")
plt.title('Annealing Progress for different Niter')
plt.legend()
plt.show()
'''

'''
plt.figure(figsize=(10, 6))
plt.plot(Nite_array, [dist[-1] for dist in best_dist_M_array], marker='o', linestyle='--')
plt.xlabel('Niter')
plt.ylabel('Best Distance at Final Beta')
plt.title('Best Distance vs Niter')
plt.show()
'''
#quiero hacer una grafica con la distancia final en función de Niter, para ver si mejora o no a medida que aumentamos el numero de iteraciones.
#pero quiero hacer para cada Niter varias corridas, para ver la variabilidad de los resultados. Para eso, voy a hacer un bucle dentro del bucle de Niter, que haga varias corridas y guarde el mejor resultado de cada una. Luego haré una gráfica con el mejor resultado de cada corrida para cada Niter.
'''
plt.figure(figsize=(10, 6))

for Niter in Nite_array:
    best_dist_M_array =[]
    for corrida in range(10): # Hacemos 10 corridas para cada Niter
        best_route_M, best_dist_M,beta_values_M,beta_dist_M = metropolis(beta, beta_max, beta_growth, Niter, D_mundo, curren_route_M, is_closed_path, is_start_fixed)
        best_dist_M_array.append(beta_dist_M[-1]) # Guardamos solo la distancia final de cada corrida
    
    plt.plot(range(10), best_dist_M_array, marker='o', linestyle='--', label=f'Niter={Niter}') # Ploteamos la distancia final de cada corrida para este Niter
    print(Niter)


plt.xlabel('Corrida')
plt.ylabel('Best Distance at Final Beta')
plt.title(f'Best Distance vs Corrida for Niter')
plt.legend()
plt.show()
'''
'''
#fuerte dependencia con la semilla, asi que vamos a fijarla para poder comparar resultados entre diferentes Niter

plt.figure(figsize=(10, 6))

for Niter in Nite_array:
    random.seed(42)
    
    best_dist_M_array =[]
    for corrida in range(10): # Hacemos 10 corridas para cada Niter
        random.seed(42)
        current_route_M = current_route_func(N_M, is_start_fixed)
        best_route_M, best_dist_M,beta_values_M,beta_dist_M = metropolis(beta, beta_max, beta_growth, Niter, D_mundo, curren_route_M, is_closed_path, is_start_fixed)
        best_dist_M_array.append(beta_dist_M[-1]) # Guardamos solo la distancia final de cada corrida
    
    plt.plot(range(10), best_dist_M_array, marker='o', linestyle='--', label=f'Niter={Niter}') # Ploteamos la distancia final de cada corrida para este Niter
    print(Niter)


plt.xlabel('Corrida')
plt.ylabel('Best Distance at Final Beta')
plt.title(f'Best Distance vs Corrida for Niter')
plt.legend()
plt.show()
'''
'''

#vamos a descubrir cual es el mejor camino cerrado sin inicio fijo
is_closed_path = True
is_start_fixed = False
#en el array vamos a poner para cada iteraccion, la distancia minima y luego los numeros de la ruta que corresponden a esa distancia minima, para poder luego comparar con el resultado de la fuerza bruta y ver si coincide o no.
mejor_ruta=np.zeros((50, N_M+1)) #50 filas, N_M+1 columnas (la primera para la distancia y las siguientes para la ruta)

for p in range(50):
    print(p)
    current_route_M = current_route_func(N_M, is_start_fixed)
    best_route_M, best_dist_M,beta_values_M,beta_dist_M = metropolis(beta, beta_max, beta_growth, 500, D_mundo, current_route_M, is_closed_path, is_start_fixed)
    mejor_ruta[p,0]=best_dist_M
    mejor_ruta[p,1:]=best_route_M


minima_distancia = np.min(mejor_ruta[:,0])
print(f"Mejor distancia encontrada: {minima_distancia} km")
'''


#queremos ver cual es la ruta que corresponde a esa distancia minima, para compararla con el resultado de la fuerza bruta
#ruta_correspondiente = mejor_ruta[mejor_ruta[:,0] == minima_distancia, 1:].astype(int)
#print(f"Ruta correspondiente a la mejor distancia: {ruta_correspondiente}")

ciudades = list(data_mundo.keys())
perm = [0, 3, 17, 16, 15, 14, 13, 12, 11, 10, 8, 9, 7, 6, 5, 4, 2, 1]

ruta = [ciudades[i] for i in perm]

print(ruta)






