import random

# 1. Define Warehouse Map
# Each key is an intersection; inner values represent connected aisles and distances (in metres).
warehouse = {
    'S': {'A': 10, 'B': 15},
    'A': {'S': 10, 'C': 12, 'D': 18},
    'B': {'S': 15, 'D': 10, 'E': 20},
    'C': {'A': 12, 'D': 8, 'F': 15},
    'D': {'A': 18, 'B': 10, 'C': 8, 'E': 10},
    'E': {'B': 20, 'D': 10, 'F': 12},
    'F': {'C': 15, 'E': 12}
}

start = 'S'  # Charging Station
end = 'F'    # Packing Station

# 2. Initialize Parameters
num_ants = 30
iterations = 50
a = 1          # Alpha: importance of pheromone
b = 2          # Beta: importance of distance
rho = 0.5      # Evaporation rate
Q = 100        # Pheromone deposit constant

# Set initial pheromone value (c) = 1.0 for all edges
pheromone = {}
for node in warehouse:
    for neighbour in warehouse[node]:
        edge = tuple(sorted((node, neighbour)))
        pheromone[edge] = 1.0

best_route = None
best_distance = float('inf')

# 3. Repeat for 50 Iterations
for iteration in range(iterations):

    all_routes = []

    # A. Construct Solutions
    for ant in range(num_ants):
        route = [start]
        current = start
        distance = 0

        while current != end:
            # Find unvisited neighbouring intersections
            neighbours = [n for n in warehouse[current] if n not in route]

            # Abandon route if dead-end is reached
            if not neighbours:
                break

            # Calculate score for each available neighbour
            scores = []
            for n in neighbours:
                edge = tuple(sorted((current, n)))
                c = pheromone[edge]             # Current pheromone of the edge
                v = 1 / warehouse[current][n]   # Visibility (1 / distance)
                score = (c ** a) * (v ** b)
                scores.append(score)

            # Calculate probability of choosing each path at the intersection
            total_score = sum(scores)
            probabilities = [s / total_score for s in scores]

            # Select next intersection probabilistically and move
            next_node = random.choices(neighbours, weights=probabilities, k=1)[0]
            distance += warehouse[current][next_node]
            route.append(next_node)
            current = next_node

        # Store only completed routes that reached the packing station
        if current == end:
            all_routes.append((route, distance))

    # B. Update Pheromones
    # Evaporate existing pheromone trails for ALL edges in the warehouse
    for edge in pheromone:
        pheromone[edge] = pheromone[edge] * (1 - rho)

    # Deposit pheromones ONLY on edges used in completed routes
    for route, distance in all_routes:
        deposit = Q / distance
        for i in range(len(route) - 1):
            edge = tuple(sorted((route[i], route[i + 1])))
            pheromone[edge] = pheromone[edge] + deposit

    # C. Keep the Best Solution (Elitism)
    for route, distance in all_routes:
        if distance < best_distance:
            best_distance = distance
            best_route = route.copy()

# 4. Output the Best Solution
if best_route is not None:
    print("Optimal Route Found:")
    print("Best Warehouse Route:", " -> ".join(best_route))
    print("Minimum Travel Distance:", best_distance, "metres")
else:
    print("No valid route found.")
