
import random

# ==========================================
# 1. DEFINE THE MAP NETWORK & TRAFFIC DELAYS
# ==========================================
# City Map Model: Intersections and the time delay (in minutes) to cross each street.
# High numbers = Heavy gridlock/slow movement. Low numbers = Fast, free-flowing streets.
MAP_NETWORK = {
    "Source": {"Node_A": 4, "Node_B": 12}, # Node_B has heavy early delays
    "Node_A": {"Source": 4, "Node_C": 25, "Node_D": 5}, # Node_C is severely gridlocked (25 mins)
    "Node_B": {"Source": 12, "Node_D": 3, "Node_E": 4},
    "Node_C": {"Node_A": 25, "Dest": 6},
    "Node_D": {"Node_A": 5, "Node_B": 3, "Dest": 18}, # Direct highway to Dest has roadwork (18 mins)
    "Node_E": {"Node_B": 4, "Dest": 5},
    "Dest": {"Node_C": 6, "Node_D": 18, "Node_E": 5}
}

def calculate_fitness(path):
    """
    Mathematical objective function. Calculates total travel delay.
    Goal: Minimize total time. Output is negative (0 is perfect, -14 is better than -45).
    """
    total_delay = 0
   
    # Safety Check: Discard broken or invalid paths instantly
    if not path or path[0] != "Source" or path[-1] != "Dest":
        return -99999
       
    for i in range(len(path) - 1):
        current_node = path[i]
        next_node = path[i + 1]
       
        # Conflict Check: If the road doesn't exist, hit it with a wall-like delay penalty
        if next_node not in MAP_NETWORK[current_node]:
            return -99999  
           
        # Add the real-world street time delay to our trip total
        street_delay = MAP_NETWORK[current_node][next_node]
        total_delay += street_delay
       
    return -total_delay

def generate_random_path():
    """Generates a random connected street route from Source to Dest to seed the pool"""
    path = ["Source"]
    current = "Source"
    max_steps = 10
   
    while current != "Dest" and max_steps > 0:
        neighbors = list(MAP_NETWORK[current].keys())
        unvisited = [n for n in neighbors if n not in path]
        if not unvisited:
            unvisited = neighbors # Backtrack option if stuck
           
        next_node = random.choice(unvisited)
        path.append(next_node)
        current = next_node
        max_steps -= 1
       
    return path

# ==========================================
# 2. INITIALIZE ALGORITHM PARAMETERS
# ==========================================
POPULATION_SIZE = 30
GENERATIONS = 40
MUTATION_RATE = 0.20
CROSSOVER_RATE = 0.85
ELITE_COUNT = 1

# Create our first raw batch of random paths
population = [generate_random_path() for _ in range(POPULATION_SIZE)]

best_global_score = -float('inf')
best_global_route = None

print("--- Launching Delay-Reduction Routing Loop ---")

# ==========================================
# 3. EVOLUTIONARY ITERATION TIMELINE
# ==========================================
for gen in range(GENERATIONS):
    # 4. Evaluate Fitness (Calculate trip times)
    scored_pop = [(calculate_fitness(sched), sched) for sched in population]
    scored_pop.sort(key=lambda x: x[0], reverse=True) # Fastest times to the top
   
    current_best_score, current_best_route = scored_pop[0]
   
    # Track the all-time fastest route discovered
    if current_best_score > best_global_score:
        best_global_score = current_best_score
        best_global_route = current_best_route
       
    next_generation = []
   
    # Save the absolute fastest route untouched (Elitism)
    next_generation.append(current_best_route.copy())
   
    while len(next_generation) < POPULATION_SIZE:
        # 5. Selection (Breed from the top-performing fast routes)
        parent1 = random.choice(scored_pop[:12])[1]
        parent2 = random.choice(scored_pop[:12])[1]
       
        child1, child2 = parent1.copy(), parent2.copy()
       
        # 6. Crossover (Stitch routes together at a shared intersection to bypass delays)
        if random.random() < CROSSOVER_RATE:
            common_nodes = set(parent1[1:-1]).intersection(set(parent2[1:-1]))
            if common_nodes:
                shared = random.choice(list(common_nodes))
                idx1 = parent1.index(shared)
                idx2 = parent2.index(shared)
               
                child1 = parent1[:idx1] + parent2[idx2:]
                child2 = parent2[:idx2] + parent1[idx1:]
               
        # 7. Mutation (Tear down a segment and find a sudden detour to skip traffic jams)
        for child in [child1, child2]:
            if random.random() < MUTATION_RATE and len(child) > 2:
                mutate_idx = random.randint(1, len(child) - 2)
                mutate_node = child[mutate_idx]
               
                neighbors = list(MAP_NETWORK[mutate_node].keys())
                new_neighbor = random.choice(neighbors)
               
                child = child[:mutate_idx + 1] + [new_neighbor]
                current = new_neighbor
                safety = 5
               
                while current != "Dest" and safety > 0:
                    current = random.choice(list(MAP_NETWORK[current].keys()))
                    if current not in child:
                        child.append(current)
                    safety -= 1
                   
            if len(next_generation) < POPULATION_SIZE and child[-1] == "Dest":
                next_generation.append(child)
               
    population = next_generation

# ==========================================
# 4. OUTPUT THE OPTIMAL TIME ROUTE REPORT
# ==========================================
print("\n" + "="*24 + " FASTEST DELAY-MINIMIZED PATH " + "="*24)
print(f"Total Journey Time: {abs(best_global_score)} Minutes")
print("-" * 74)
print(" -> ".join(best_global_route))
print("="*74)
