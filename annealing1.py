# -*- coding: utf-8 -*-
"""
Created on Thu Mar 26 00:49:54 2026

@author: Nico
"""

import numpy as np
from itertools import permutations
import math

#Se le asigna a cada ciudad un numero
#Definir el diccionario este realmente no ayuda mucho xD
cities = {"Strasbourg" : 0, "Nancy" : 1, "Paris" : 2, "Mulhouse" : 3, "Dijon" : 4, "Besancon" : 5}

#Se define la matriz D de distancias entre ciudades
#Como es una matriz simétrica de diagonal 0 solo he tomado la triangular inferior, para no saturar con muchos datos

D = [
    [150],
    [490, 280],
    [110, 200, 540],
    [335, 230, 315, 260],
    [240, 190, 410, 160,  95],
    [120, 210, 325, 400, 110, 370],
    [205, 120, 370, 420, 450, 185, 360]
]


#N es el numero de ciudades
N = len(D)+1

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
J = np.array([p for p in permutations(np.arange(N)) if p[1] < p[-1] and p[0] == init])
J = J.astype(int)

#Para cada combinacion de ciudades, se define un camino abierto Co, que es la suma de las distancias de una ciudad a la otra
#Para el caso anterior seria d(2->3) + d(3->5) + d(5->0)
Co = np.zeros((L, 1))

#El camino cerrado Cc es lo mismo pero volviendo desde la ultima posicion de nuevo a la primera
#Siguiendo con el caso anterior, se le añadiria + d(4->2)
#En este caso hay L/2 caminos posibles y no L porque hemos descartado los caminos recorridos en sentido contrario, lo que los reduce a la mitad
Cc = np.zeros((L//2, 1))

#Ahora rellenamos los vectores Co y Cc con las sumas de distancias
#Supongamos el camino (2 3 5 0 1 4)
#La estrategia va a ser calcular la distancia entre 3 y 4: d(3->5->0->1->4) = d(3->5) + ... + d(1->4), ya que es común al camino cerrado y abierto
#Calculamos aparte dfs = d(2->3) y dfl d(2->4)
#Para el camino cerrado, a d(3->...->4) le sumamos dfs y dfl para enganchar toda la secuencia y que vuelva del final al inicio
#Para nuestro vector de caminos abiertos Co, completamos la primera mitad con d(3->...->4) + dfs que es el camino abierto hacia la derecha
#Y completamos la segunda mitad con d(3->...->4) + dfl, que es el camino abierto hacia la izquierda
#Asi evitamos calculos innecesarios y con un solo d(3->...->4) calculamos 3 caminos de una tacada
for j in range(L//2):
    for i in range(1,N-1):
        Cc[j] += D[max(J[j, i], J[j, i+1])-1][min(J[j, i], J[j, i+1])] 
    dfs = D[max(J[j, 0], J[j, 1])-1][min(J[j, 0], J[j, 1])]
    dfl = D[max(J[j, N-1], J[j, 0])-1][min(J[j, N-1], J[j, 0])]
    Co[j] = Cc[j] + dfs
    Co[L//2+j] = Cc[j] + dfl
    Cc[j] += dfs + dfl
    

#Por ultimo, tanto para Co como para Cc, creamos indices con las posiciones de los caminos con minima distancia: indexCcmin, indexComin
#Comin y Ccmin son la(s) permutacion(es) con un camino minimo, es decir, aquellas que estan en las posiciones que tenemos en los index...

#Para el camino abierto Co hay que hacer un poco mas de trabajo porque solo tenemos L/2 permutaciones en J (lo que nos ahorra calculo)
#Pero como tenemos 2 caminos abiertos (hacia la derecha y hacia la izquierda), Co tiene L elementos, asi que hay que trabajar por separado las 2 mitades
indexComin = np.where(Co==min(Co))[0]
Comin = np.array([J[i] if i < L//2 else np.concatenate(([init], J[i-L//2][:0:-1])) for i in indexComin])

indexCcmin = np.where(Cc==min(Cc))[0]
Ccmin = np.array([J[i] for i in indexCcmin])
