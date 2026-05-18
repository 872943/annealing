import numpy as np
from itertools import permutations
import math
import random
import matplotlib.pyplot as plt

#%%FUNCTIONS
def calculate_route_distance(route, D, is_closed_path):
    """
    Calculate the total distance of a specific route.
    'route' is a list of cities J and 'matrix' is the distance matrix D
    """
    total_dist = 0
    # We loop through the route, summing the distance between each pair of cities
    for i in range(len(route) - 1):
        total_dist += D[route[i], route[i+1]]

    if is_closed_path: # If the value of is_closed_path is True, we need to add the distance from the last city back to the first one to close the loop
        total_dist += D[route[-1], route[0]]
    return total_dist

def swap_cities(route, is_start_fixed):
    new_path = route.copy()
    
    # We choose two random indices to swap, ensuring we don't swap the starting city if it's fixed.
    # If the start is fixed, the first index we can choose is 1. (from 1 to the end, skipping 0)
    # If it's free, the first index is 0.
    # range(1, 6) gives us the indices 1, 2, 3, 4, 5
    start_idx = 1 if is_start_fixed else 0
    idx1, idx2 = random.sample(range(start_idx, len(route)), 2)
    
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
    #We generate an initial route according to the configuration
    if is_start_fixed:
        cities_to_permute = list(range(1, N)) # We create a list excluding Strasbourg (0)
        random.shuffle(cities_to_permute) 
        current_route = np.array([0] + cities_to_permute) # We put Strasbourg at the beginning and then add the permuted cities
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
    #So, we will save the values of beta and the best distance at each step to be able to plot them later.
    cont=0
    beta_values = []
    best_distances = []



    #Let's start with the metropolis algorithm
    while beta < beta_max:

        for nn in range(Niter):

            # We propose a change (swap)

            new_route = swap_cities(current_route, is_start_fixed) 
            new_dist = calculate_route_distance(new_route, D, is_closed_path)
            
            # we calculate the change in energy (distance) that this swap would produce
            delta_E = new_dist - current_dist
            
            # Metropolis criterion: if the new route is better (delta_E <= 0), we accept it. 
            if delta_E <= 0:
                accept = True
            else:
                # The route is worse, but we see if we accept it or not
                # We generate a random number between 0 and 1
                r = random.random()
                # We calculate the acceptance probability (umbral) using the Boltzmann factor
                umbral = math.exp(-beta * delta_E)
                
                if r < umbral:
                    accept = True  
                else:
                    accept = False 
            if accept:
                current_route = new_route
                current_dist = new_dist
                
                # We check if this new route is the best one we have found so far
                if current_dist < best_dist:
                    best_dist = current_dist
                    best_route = current_route.copy()
        
        
        if ((cont<200 and cont%5==0) or cont%10==0 ):
            beta_values.append(beta)
            best_distances.append(best_dist)

        #We cool down the system by increasing beta
        beta = beta + beta_growth
        cont+=1
    return best_route, best_dist, beta_values, best_distances

def create_matrix_distances(city_data):
    """
    Create a distance matrix between cities using the Haversine formula.
     'city_data' is a dictionary with the city name as key and a tuple (latitude, longitude) as value.
    """
    cities = list(city_data.keys())
    N = len(cities)
    D = np.zeros((N, N))
    
    for i in range(N):
        for j in range(i+1, N):
            lat1, lon1 = city_data[cities[i]]
            lat2, lon2 = city_data[cities[j]]
            D[i, j] = haversine_distance(lat1, lon1, lat2, lon2)
            D[j, i] = D[i, j]  # Symmetric matrix, distance from i to j is the same as from j to i
    
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
        disttemp = np.min(Co[:,i])  #the minimum distance for the OPEN path starting with city i is the minimum of the column i of Co
        indextemp = np.where(Co[:,i]==disttemp)[0] #the indices of the sortest path in the column i 
        stemp = np.size(indextemp) #number of indices associated to the minimum distance
        sind = indexComin.shape[0] 
        
        #The code takes into account as well the possibility of having 2 different paths with the shortest distance 
        #So in this case we enlarge the indices matrix to allow for more indices associated to minimal paths   
        if stemp > sind:
            indexComin = np.append(indexComin, np.full((stemp-sind, N), np.nan), axis = 0)
            
        indexComin[0:stemp, i] = indextemp
        distComin[0,i] = disttemp
    
#To determine the associated OPEN path we need to distinguish indices in the upper half of Co from those in the lower
#Thus, we can determine if we get a "forward" or a "backward" path
    indrow = indexComin.shape[0] #number of rows of the indices matrix, which is the number of paths with the minimum distance among all the paths starting with city i
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
print(f"\nBest CLOSED PATH: {distCcmin} km")
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

N = D.shape[0]  # Number of cities

#PARAMETERS (beta is proportional to 1/temperature, so a small beta means a hot system and a large beta means a cold system)
beta = 0.01          # We start with a small beta (very hot system)
beta_max = 10.0      # We will stop when the beta becomes large (cold system)
beta_growth = 0.01  # At each step, we will sum this to beta to make it grow, that is, to cool down the system
#These results we are going to compare with those calculated by 'brute force' 
#There are three results to compare, the idea is to be able to do everything with the same code, simply changing these parameters below.
is_closed_path = True    # Do we close the path? (True/False)
is_start_fixed = True   # Do we always start from Strasbourg? (True/False)

current_route=current_route_func(N, is_start_fixed)

#Niter is the number of iterations we do at each temperature

Niter=100
best_route, best_dist, beta_values, best_distances = metropolis(beta, beta_max, beta_growth, 1,D, current_route, is_closed_path, is_start_fixed)
    

# --- FINAL RESULTS ---
print("\n" + "="*35)
print("      ANNEALING COMPLETE")
print("="*35)
print(f"\nBest CLOSED PATH: {best_route}")
print(f"Distance: {best_dist} km")
print("-" * 30)

# OPEN path starting from Strasbourg (0)
is_closed_path = False
best_route, best_dist, beta_values, best_distances = metropolis(beta, beta_max, beta_growth, 1,D, current_route, is_closed_path, is_start_fixed)

print(f"Best OPEN PATH (Fix Start):  {best_route}")
print(f"Distance: {best_dist} km")
print("="*30 + "\n")

is_start_fixed = False
current_route=current_route_func(N, is_start_fixed)
best_route, best_dist, beta_values, best_distances = metropolis(beta, beta_max, beta_growth, 1,D, current_route, is_closed_path, is_start_fixed)


print(f"Absolute Best OPEN PATH (Flexible Start):  {best_route}")
print(f"Distance: {best_dist} km")
print("="*30 + "\n")



'''
#We plot the best distance found at each step as a function of beta, to see how the annealing process has evolved. 
#We plot the relative improvement of the best distance compared to the final best distance, that is, (best_distance - best_distance_final)/best_distance_final, to see how much we have improved compared to the final result.
plt.figure(figsize=(10, 6))
plt.plot(beta_values, (best_distances-best_distances[-1])/best_distances[-1], marker='o', linestyle='--')
plt.xlabel('Beta')
plt.ylabel(r"$\sigma_{Best\ Distance}$")
plt.title('Annealing Progress')
plt.show()
'''

#in order to measure the time it takes to run the annealing algorithm


#Now we are going to do the same but with 18 cities around the world, to see how the algorithm performs with a larger number of cities. 
# Paris, Madrid, Athens, Helsinki, Beyrouth, New Delhi, Bangkok, Beijing, Tokyo, Seoul, Sidney, Buenos Aires,
#Brasilia, Caracas, Mexico City, Chicago, Quebec, Reykjavik 


#in order to apply the annealing algorithm to these cities, we need to define the distance matrix D for these cities.
#we copy their geographical coordinates (latitude and longitude) and then we calculate the distance between them using the Haversine formula, 
#which gives us the straight-line distance between two points on the surface of the Earth.

#city, latitude, longitude

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



#Now we have 18 cities, so the number of possible paths is 18! = 6402373705728000, which is a very large number, 
#so we cannot use the brute force method to find the optimal path.


'''
is_closed_path = True
is_start_fixed = True   
curren_route_M =current_route_func(N_M, is_start_fixed)
best_route_M, best_dist_M,beta_values_M,beta_dist_M = metropolis(beta, beta_max, beta_growth, Niter, D_mundo, curren_route_M, is_closed_path, is_start_fixed)
    

# --- FINAL RESULTS ---
print("\n" + "="*35)
print("      ANNEALING COMPLETE FOR WORLD CITIES")
print("="*35)
print(f"\nBest CLOSED PATH: {best_route_M}")
print(f"Distance: {best_dist_M} km")
print("-" * 30)




# OPEN path starting from Strasbourg (0)
is_closed_path = False
curren_route_M =current_route_func(N_M, is_start_fixed)
best_route_M, best_dist_M,beta_values_M,beta_dist_M = metropolis(beta, beta_max, beta_growth, Niter, D_mundo, curren_route_M, is_closed_path, is_start_fixed)

print(f"Best OPEN PATH (Fix Start):  {best_route_M}")
print(f"Distance: {best_dist_M} km")
print("="*30 + "\n")




is_start_fixed = False
current_route=current_route_func(N_M, is_start_fixed)
best_route_M, best_dist_M, beta_values_M, best_distances_M = metropolis(beta, beta_max, beta_growth, 1,D_mundo, current_route, is_closed_path, is_start_fixed)

print(f"Absolute Best OPEN PATH (Flexible Start):  {best_route_M}")
print(f"Distance: {best_dist_M} km")
print("="*30 + "\n")



#We can also compare the results for different values of Niter, to see how the number of iterations at each temperature affects the results.

Nite_array=[1,20, 50, 100, 500, 1000]
best_dist_M_array =[]

for Niter in Nite_array:
    best_route_M, best_dist_M,beta_values_M,beta_dist_M = metropolis(beta, beta_max, beta_growth, Niter, D_mundo, curren_route_M, is_closed_path, is_start_fixed)
    best_dist_M_array.append(beta_dist_M)

#We plot the relative improvement to beta for different values of Niter.
plt.figure(figsize=(10, 6))
for fila in best_dist_M_array:
    plt.plot(beta_values_M, (fila-fila[-1])/fila[-1], marker='o', linestyle='--', ms=2, label=f'Niter={Nite_array[best_dist_M_array.index(fila)]}')

plt.xlabel('Beta')
plt.ylabel(r"$\sigma_{Best\ Distance}$")
plt.title('Annealing Progress for different Niter')
plt.legend()
plt.show()



#we want to see how the final distance changes as we increase Niter, to see if it improves or not as we increase the number of iterations.
#but we want to do several runs for each Niter, to see the variability of the results. For that, I'm going to make a loop inside the Niter loop, 
#that does several runs and saves the best result of each one. Then I'll make a graph with the best result of each run for each Niter.

plt.figure(figsize=(10, 6))

for Niter in Nite_array:
    best_dist_M_array =[]
    for corrida in range(10): # Hacemos 10 corridas para cada Niter
        best_route_M, best_dist_M,beta_values_M,beta_dist_M = metropolis(beta, beta_max, beta_growth, Niter, D_mundo, curren_route_M, is_closed_path, is_start_fixed)
        best_dist_M_array.append(beta_dist_M[-1]) # Guardamos solo la distancia final de cada corrida
    
    plt.plot(range(10), best_dist_M_array, marker='o', linestyle='--', label=f'Niter={Niter}') # Ploteamos la distancia final de cada corrida para este Niter
    print(Niter)


plt.xlabel('Run')
plt.ylabel('Best Distance at Final Beta')
plt.title(f'Best Distance vs Run for Niter')
plt.legend()
plt.show()
'''


#we have seen that the better route is not always the one with the largest Niter,
#this means that the algorithm is not guaranteed to find the optimal solution, and that it can get stuck in local minima, 
#so it has a great dependence on the initial route and on the random choices made during the process.

#Finally, in order to find the best paths, we should do several runs of the algorithm, and then compare the results to find the best one among all the runs.
#In that way, we will be able to avoid getting stuck in local minima and increase our chances of finding the global minimum, that is, the best path among all the possible paths.
Niter=250
ninic=100

#in the array mejor_ruta we are going to put for each iteration, the minimum distance and then the numbers of the route that correspond to that minimum distancet.
mejor_ruta=np.zeros((ninic, N_M+1)) 
is_closed_path = True
is_start_fixed = True 

for p in range(ninic):
    current_route_M = current_route_func(N_M, is_start_fixed)
    best_route_M, best_dist_M,beta_values_M,beta_dist_M = metropolis(beta, beta_max, beta_growth, 500, D_mundo, current_route_M, is_closed_path, is_start_fixed)
    mejor_ruta[p,0]=best_dist_M
    mejor_ruta[p,1:]=best_route_M


minima_distancia = np.min(mejor_ruta[:,0])
minima_distancia_index = np.where(mejor_ruta[:,0] == minima_distancia)[0][0]
best_route_M = mejor_ruta[minima_distancia_index, 1:].astype(int)
    

# --- FINAL RESULTS ---
print("\n" + "="*35)
print("      ANNEALING COMPLETE FOR WORLD CITIES")
print("="*35)
print(f"\nBest CLOSED PATH: {best_route_M}")
print(f"Distance: {best_dist_M} km")
print("-" * 30)




# OPEN path starting from Strasbourg (0)
is_closed_path = False

for p in range(ninic):
    current_route_M = current_route_func(N_M, is_start_fixed)
    best_route_M, best_dist_M,beta_values_M,beta_dist_M = metropolis(beta, beta_max, beta_growth, 500, D_mundo, current_route_M, is_closed_path, is_start_fixed)
    mejor_ruta[p,0]=best_dist_M
    mejor_ruta[p,1:]=best_route_M


minima_distancia = np.min(mejor_ruta[:,0])
minima_distancia_index = np.where(mejor_ruta[:,0] == minima_distancia)[0][0]
best_route_M = mejor_ruta[minima_distancia_index, 1:].astype(int)



print(f"Best OPEN PATH (Fix Start):  {best_route_M}")
print(f"Distance: {best_dist_M} km")
print("="*30 + "\n")




is_start_fixed = False
for p in range(ninic):
    current_route_M = current_route_func(N_M, is_start_fixed)
    best_route_M, best_dist_M,beta_values_M,beta_dist_M = metropolis(beta, beta_max, beta_growth, 500, D_mundo, current_route_M, is_closed_path, is_start_fixed)
    mejor_ruta[p,0]=best_dist_M
    mejor_ruta[p,1:]=best_route_M


minima_distancia = np.min(mejor_ruta[:,0])
minima_distancia_index = np.where(mejor_ruta[:,0] == minima_distancia)[0][0]
best_route_M = mejor_ruta[minima_distancia_index, 1:].astype(int)



print(f"Absolute Best OPEN PATH (Flexible Start):  {best_route_M}")
print(f"Distance: {best_dist_M} km")
print("="*30 + "\n")






