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

def brute_force(D):
    
#N is the number of cities
    N = D.shape[0]

#L is the number of possible paths
#It corresponds to (N-1)! not to N! because we fix the first city
#We do that to avoid doing too many calculations and computing too many permutations
#In a CLOSED path, many paths which start with different numbers are equivalent
#For instance (0 1 2 3 4 5) (5 0 1 2 3 4) (3 4 5 0 1 2), which are the same paths just moving all the numbers to the right
#By fixing the first city, we have avoid this multiplicity
    L = math.factorial(N-1)

#J is a matrix whose rows contain all the permutations, that is, all the possible paths
#As well as fixing the first city, we require the 2nd number to be smaller than the last
#We do so to avoid, in the CLOSED path case, considering 2 separate paths that are actually the same but in the opposite way: (0 4 5 1 2 3) and (0 3 2 1 5 4)
#This is the minimum amount of permutations necessary to build all the CLOSED path, and we take advantage of it to build the OPEN paths as well
    J = np.array([p for p in permutations(np.arange(N)) if p[1] < p[-1] and p[0] == 0])
    J = J.astype(int)

#For each combination of cities, we define N OPEN paths, each of them corresponding to the same path starting from a different city
#For instance (0 4 5 1 2 3) would give as well (4 5 1 2 3 0) starting with 4 or (1 2 3 0 4 5) starting with 1
#For an OPEN path (0 1 5 4 2 3), for example, we store in Co the total distance, calculated as d(0->1) + d(1->5) + d(5->4) + d(4->2) + d(2->3)
    Co = np.zeros((L, N))

#For the CLOSED path we do the same, but coming back from the last city to the first
#In the previous commented example, we would need to add d(3->0)
#The length of Cc is half the length of Co, because we have ruled out the paths which are walked the other way
    Cc = np.zeros((L//2, 1))

#We now fill Co and Cc with the total distance of each path
#Let's suppose the path (2 3 5 0 1 4)
#The strategy is to calculate first the distance of the CLOSED path
#For the OPEN path cases, we take the paths strarting with each number, so let's focus for instance of 3
#If we substract d(2->3) to the CLOSED path distance, we end up with the distance associated to the OPEN path (3 5 0 1 4 2)
#If we substract d(3->5), we end up with the distance of the OPEN path (3 2 4 1 0 5), which is the same path starting from 3 but the opposite way
#So for all the paths starting with 3, we store the distance of the "forward" paths in the first half of Co and the distance of the "backward" paths in the second half
#By doing so with all the numbers associated to cities, we calculate with just 1 CLOSED path all the 2N OPEN paths that we need
    for j in range(L//2):
        path = J[j]
        dist = calculate_route_distance(path, D, True)
        Cc[j] = dist
    
        for k in range(N-1):
            o = path[k-1]
            p = path[k]
            q = path[k+1]
        
            Co[j,p] = dist - D[p,o]
            Co[L//2+j,p] = dist - D[p,q]
        
        o = path[4]
        p = path[5]
        q = path[0]
        Co[j,p] = dist - D[p,o]
        Co[L//2+j,p] = dist - D[p,q]
        
#Last but not least, we calculate the shortest distances for both the CLOSED and OPEN cases
#From this, we can get their indices, that is, the label which is necessary to find them in J
#Using this, we find the associated paths in J
    indexComin = np.zeros([1,N])
    distComin = np.zeros([1,N])
    for i in range(N):
        disttemp = np.min(Co[:,i]) 
        indextemp = np.where(Co[:,i]==disttemp)[0]
        stemp = np.size(indextemp)
        sind = indexComin.shape[0]
        
#The code takes into account as well the possibility of having 2 different paths with the shortest distance 
#So in this case we enlarge the indices matrix to allow for more indices associated to minimal paths   
        if stemp > sind:
            indexComin = np.append(indexComin, np.full((stemp-sind, N), np.nan), axis = 0)
            
        indexComin[0:stemp, i] = indextemp
        distComin[0,i] = disttemp
    
#To determine the associated OPEN path we need to distinguish indices in the upper half of Co from those in the lower
#Thus, we can determine if we get a "forward" or a "backward" path
    indrow = indexComin.shape[0]
    indcol = indexComin.shape[1]
    Comin = np.full((indrow, indcol, N), np.nan)
    for i in range(indrow):
        for j in range(indcol):
            index = indexComin[i,j].astype(int)
            if not np.isnan(index):
                if index < L//2:
                    path = J[index,:]
                    pos = np.where(path==j)[0][0]
                    path = np.concatenate((path[pos::], path[0:pos]))
                    Comin[i,j] = path
                else:
                    path = J[index-L//2,:]
                    pos = np.where(path==j)[0][0]
                    path = np.concatenate((path[pos::-1], path[-1:pos:-1]))
                    Comin[i,j] = path

#We do the same for CLOSED paths, what is much easier
    distCcmin = np.min(Cc)
    indexCcmin = np.where(Cc==distCcmin)[0]
    Ccmin = np.array([J[i] for i in indexCcmin])
    
#Among all the OPEN paths starting from different cities, we determine the overall shortest path as well as its distance
#This code is also prepared for the situation of different paths being equally the shortest
    absdistComin = np.min(distComin)
    absindex = np.array(np.where(distComin == absdistComin))
    num = absindex.shape[1]
    absComin = np.zeros([num, N])
    for i in range(num):
        absComin[i,:] = Comin[absindex[0,i], absindex[1,i]]
    
    return distCcmin, Ccmin.astype(int), distComin, Comin.astype(int), absdistComin, absComin.astype(int)


D = np.array([
    [0,   156, 491, 116, 310, 249], # 0: Strasbourg
    [156, 0,   386, 164, 219, 160], # 1: Nancy
    [491, 386, 0,   539, 315, 411], # 2: Paris
    [116, 164, 539, 0,   199, 134], # 3: Mulhouse
    [310, 219, 315, 199, 0,   95],  # 4: Dijon
    [249, 160, 411, 134, 95,  0]    # 5: Besançon
])

distCcmin, Ccmin, distComin, Comin, absdistComin, absComin = brute_force(D)

print("\n" + "="*30)
print("RESULTS")
print("="*30)

# CLOSED path
print(f"\nBest CLOSED PATH (FIX Start): {distCcmin} km")
print(f"Optimal Route(s): {Ccmin}")

print("-" * 30)

# OPEN path starting from Strasbourg (0)
print(f"Best OPEN PATH (Fix Start): {distComin[0,0]} km")
print(f"Optimal Route(s): {Comin[0,0]}")
print("="*30 + "\n")

# Overall OPEN path
print("-" * 30)
print(f"Absolute Best OPEN PATH (Flexible Start): {absdistComin} km")
print(f"Optimal Route(s): {absComin}")
print("="*30 + "\n")



#%%SIMULATED ANNEALING:
#a

N = D.shape[0]  # Número de ciudades

#PARAMETERS (beta es inversamente proporcional a T)
beta = 0.01          # Empezamos con una beta pequeña (sistema muy caliente)
beta_max = 10.0      # Pararemos cuando la beta sea alta (sistema frío)
beta_growth = 0.01  # En cada paso, multiplicaremos beta por esto para que crezca poco a poco
#hola, te lo he cambiado y he puesto suma para que estuviesen equidistantes las temperaturas
#Estos resultados los vamos a comparar a los calculados mediante la 'fuerza bruta', vamos el codigo de antes. Hay tres resultados
#que comparar, la idea es poder hacer todo con el mismo código, simplemente cambiando estos parámetros de abajo.
is_closed_path = False   # ¿Volvemos al inicio? (True/False)
is_start_fixed = False   # ¿Empezamos siempre en Estrasburgo? (True/False)

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


#vamos a descubrir cual es el mejor camino cerrado sin inicio fijo
is_closed_path = False
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



#queremos ver cual es la ruta que corresponde a esa distancia minima, para compararla con el resultado de la fuerza bruta
ruta_correspondiente = mejor_ruta[mejor_ruta[:,0] == minima_distancia, 1:].astype(int)
print(f"Ruta correspondiente a la mejor distancia: {ruta_correspondiente}")

'''
ciudades = list(data_mundo.keys())
perm = [ 0 , 1 , 2 , 3 , 17 , 16 , 15 , 14 , 13 , 11 , 12 , 4 , 5 , 6 , 7 , 9 , 8 , 10 ]

ruta = [ciudades[i] for i in perm]

print(ruta)
'''





