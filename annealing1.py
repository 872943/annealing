# -*- coding: utf-8 -*-
"""
Created on Thu Mar 26 00:49:54 2026

@author: Nico
"""

#distances: Str, Nan, Par, Mulh, Dij, Bes
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
    [240, 190, 410, 160,  95]
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
init = 2

#J son todas las permutaciones, es decir, todos los caminos posibles
#init va a estar fijado como el primer valor de todas las filas, es decir, la primera ciudad de cualquier camino
#Si init = 2, una de sus filas sería por ejemplo: (2 3 5 0 1 4)
vec = np.arange(N)
vec = vec[vec != 2]
J = np.array(list(permutations(vec)))
J = np.concatenate((init*np.ones((L, 1)), J), axis = 1)
J = J.astype(int)

#Para cada combinacion de ciudades, se define un camino abierto Co, que es la suma de las distancias de una ciudad a la otra
#Para el caso anterior seria d(2->3) + d(3->5) + d(5->0)
Co = np.zeros((L, 1))

#El camino cerrado Cc es lo mismo pero volviendo desde la ultima posicion de nuevo a la primera
#Siguiendo con el caso anterior, se le añadiria + d(4->2)
Cc = np.zeros((L, 1))

#Ahora rellenamos los vectores Co y Cc con las sumas de distancias
for j in range(L):
    i = 0
    while i < N-1:
        Co[j] += D[max(J[j, i]-1, J[j, i+1]-1)][min(J[j, i]-1, J[j, i+1]-1)]
        i += 1
    Cc[j] = Co[j] + D[max(J[j, i]-1, J[j, 0]-1)][min(J[j, i]-1, J[j, 0]-1)]

#Por ultimo, tanto para Co como para Cc, creamos indices con las posiciones de los caminos minimos: indexCcmin, indexComin
#Comin y Ccmin son la(s) permutacion(es) con un camino minimo, p ej: (0 3 1 5 4 2)
indexComin = np.where(Co==min(Co))[0]
Comin = np.array([J[i] for i in indexComin])

indexCcmin = np.where(Cc==min(Cc))[0]
Ccmin = np.array([J[i] for i in indexCcmin])

