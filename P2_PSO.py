import random

# 1. DEFINE TRAFFIC INTERSECTION
DIRECTIONS = ["North", "South", "East", "West"]

TRAFFIC_VOLUME = {
    "North": 8.5,
    "South": 7.5,
    "East": 6.5,
    "West": 5.5
}

TOTAL_CYCLE_TIME = 120
TRANSITION_TIME = 20

TOTAL_GREEN_TIME = TOTAL_CYCLE_TIME - TRANSITION_TIME

MIN_GREEN = 10
MAX_GREEN = 40

SATURATION_FLOW = 0.8


# 2. INITIALIZE PSO PARAMETERS

NUM_PARTICLES = 30
MAX_ITERATIONS = 100

W = 0.7
C1 = 1.5
C2 = 1.5

random.seed(42)

# 3. OBJECTIVE FUNCTION


def calculate_fitness(position):

    total_delay = 0
    total_vehicles = sum(TRAFFIC_VOLUME.values())

    for i, direction in enumerate(DIRECTIONS):

        green = position[i]

        # Calculate road-handling capacity
        capacity = (
            SATURATION_FLOW * green * 60 / TOTAL_CYCLE_TIME
        )

        # Calculate degree of saturation
        saturation = TRAFFIC_VOLUME[direction] / capacity

        # Estimate red-light waiting time
        red_time = TOTAL_CYCLE_TIME - green

        red_delay = (red_time ** 2) / (2 * TOTAL_CYCLE_TIME)

        # Calculate congestion penalty
        congestion_penalty = (
            30 * max(0, saturation - 0.85) ** 2
        )

        if saturation > 1:
            congestion_penalty += (
                120 * (saturation - 1) ** 2
            )

        waiting_time = red_delay + congestion_penalty

        # Weight waiting time by traffic volume
        total_delay += TRAFFIC_VOLUME[direction] * waiting_time

    return total_delay / total_vehicles


# 4. ADJUST GREEN-LIGHT ALLOCATIONS

def repair_position(position):

    position = [
        max(MIN_GREEN, min(MAX_GREEN, x))
        for x in position
    ]

    # Maintain the total available green time
    while abs(TOTAL_GREEN_TIME - sum(position)) > 0.000001:

        difference = TOTAL_GREEN_TIME - sum(position)

        if difference > 0:
            available = [
                i for i in range(4)
                if position[i] < MAX_GREEN
            ]
        else:
            available = [
                i for i in range(4)
                if position[i] > MIN_GREEN
            ]

        if not available:
            break

        change = difference / len(available)

        for i in available:
            position[i] = max(
                MIN_GREEN,
                min(MAX_GREEN, position[i] + change)
            )

    return position



# 5. INITIALIZE PARTICLES AND VELOCITIES


particles = []

for i in range(NUM_PARTICLES):

    # Position = Green-light duration of each direction
    position = [
        random.uniform(MIN_GREEN, MAX_GREEN)
        for _ in range(4)
    ]

    position = repair_position(position)

    particles.append(position)


# Velocity = Change in green-light duration
velocities = [
    [random.uniform(-2, 2) for _ in range(4)]
    for _ in range(NUM_PARTICLES)
]



# 6. INITIALIZE PBEST AND GBEST


personal_best = [p.copy() for p in particles]

personal_best_scores = [
    calculate_fitness(p) for p in particles
]

best_index = personal_best_scores.index(
    min(personal_best_scores)
)

global_best = personal_best[best_index].copy()

global_best_score = personal_best_scores[best_index]


print("--- Starting Traffic Signal Optimization ---")



# 7. PSO OPTIMIZATION


for iteration in range(MAX_ITERATIONS):

    for i in range(NUM_PARTICLES):

        # Update velocity for each direction
        for j in range(4):

            r1 = random.random()
            r2 = random.random()

            velocities[i][j] = (
                W * velocities[i][j]
                + C1 * r1 * (
                    personal_best[i][j] - particles[i][j]
                )
                + C2 * r2 * (
                    global_best[j] - particles[i][j]
                )
            )

        # Update green-light durations
        new_position = [
            particles[i][j] + velocities[i][j]
            for j in range(4)
        ]

        particles[i] = repair_position(new_position)

        # Calculate new average waiting time
        fitness = calculate_fitness(particles[i])

        # Update Personal Best
        if fitness < personal_best_scores[i]:

            personal_best[i] = particles[i].copy()
            personal_best_scores[i] = fitness

        # Update Global Best
        if fitness < global_best_score:

            global_best = particles[i].copy()
            global_best_score = fitness



# 8. DISPLAY OPTIMAL SOLUTION


print("\n" + "=" * 50)
print(" OPTIMAL TRAFFIC SIGNAL ALLOCATION")
print("=" * 50)

for i, direction in enumerate(DIRECTIONS):

    print(
        f"{direction}: {global_best[i]:.2f} seconds"
    )

print("-" * 50)

print(
    f"Total Green Time: {sum(global_best):.2f} seconds"
)

print(
    f"Minimum Average Waiting Time: "
    f"{global_best_score:.2f} seconds"
)

print("=" * 50)
