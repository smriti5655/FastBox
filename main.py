import json
import math


# This function calculates the straight-line distance between two points
# point1 and point2 are both lists like [x, y]
def calculate_distance(point1, point2):
    x1 = point1[0]
    y1 = point1[1]
    x2 = point2[0]
    y2 = point2[1]

    distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return distance


# This function checks every agent and finds the one closest to the warehouse
def find_nearest_agent(warehouse_position, agents):
    best_agent = None
    best_distance = float("inf")  # start with a very big number

    for agent_name, agent_position in agents.items():
        distance = calculate_distance(agent_position, warehouse_position)

        # if this agent is closer than the best one we found so far, update it
        if distance < best_distance:
            best_agent = agent_name
            best_distance = distance

    return best_agent, best_distance


# This function simulates the whole day of deliveries
def simulate_deliveries(packages, warehouses, agents):
    # keep track of where each agent currently is (they move after each delivery)
    current_positions = {}
    for agent_name, position in agents.items():
        current_positions[agent_name] = position

    # this will store how many packages and how much distance each agent has
    results = {}
    for agent_name in agents:
        results[agent_name] = {"packages_delivered": 0, "total_distance": 0}

    # go through every package one by one
    for package in packages:
        warehouse_name = package["warehouse"]
        warehouse_position = warehouses[warehouse_name]
        destination = package["destination"]

        # find which agent should deliver this package
        nearest_agent, distance = find_nearest_agent(warehouse_position, agents)

        # get where this agent currently is (not always their starting position)
        agent_current_position = current_positions[nearest_agent]

        # distance from agent's current spot to the warehouse
        distance_to_warehouse = calculate_distance(agent_current_position, warehouse_position)

        # distance from the warehouse to the package's destination
        distance_to_destination = calculate_distance(warehouse_position, destination)

        # total distance for this one delivery trip
        trip_distance = distance_to_warehouse + distance_to_destination

        # update this agent's totals
        results[nearest_agent]["packages_delivered"] = results[nearest_agent]["packages_delivered"] + 1
        results[nearest_agent]["total_distance"] = results[nearest_agent]["total_distance"] + trip_distance

        # the agent is now standing at the destination, so update their position
        current_positions[nearest_agent] = destination

    return results


# This function builds the final report with efficiency and the best agent
def generate_report(delivery_results):
    report = {}
    best_agent = None
    best_efficiency = float("inf")

    for agent_name, info in delivery_results.items():
        packages_delivered = info["packages_delivered"]
        total_distance = info["total_distance"]

        # efficiency = total distance divided by packages delivered
        # a lower number means the agent travelled less per package (better)
        if packages_delivered > 0:
            efficiency = total_distance / packages_delivered
        else:
            efficiency = 0

        report[agent_name] = {
            "packages_delivered": packages_delivered,
            "total_distance": round(total_distance, 2),
            "efficiency": round(efficiency, 2)
        }

        # check if this agent is the best (lowest efficiency) so far
        if packages_delivered > 0 and efficiency < best_efficiency:
            best_efficiency = efficiency
            best_agent = agent_name

    report["best_agent"] = best_agent
    return report


# This function saves the report dictionary into a JSON file
def save_report(report, filename):
    with open(filename, "w") as file:
        json.dump(report, file, indent=4)


# This function checks that every single package was actually delivered
def verify_all_delivered(report, packages):
    total_delivered = 0
    for agent_name, info in report.items():
        if agent_name != "best_agent":  # skip this key, it's not an agent
            total_delivered = total_delivered + info["packages_delivered"]

    total_packages = len(packages)

    if total_delivered == total_packages:
        print("Verification passed:", total_delivered, "of", total_packages, "delivered.")
    else:
        print("ERROR: Mismatch!", total_delivered, "delivered but", total_packages, "expected.")


# ---------------- MAIN PROGRAM STARTS HERE ----------------

# Step 1: open data.json and load it into Python
with open("data.json", "r") as file:
    data = json.load(file)

# Step 2: pull out the three parts we need
warehouses = data["warehouses"]
agents = data["agents"]
packages = data["packages"]

# Step 3: simulate the whole day of deliveries
delivery_results = simulate_deliveries(packages, warehouses, agents)

# Step 4: build the final report (with efficiency and best agent)
final_report = generate_report(delivery_results)

# Step 5: save the report into report.json
save_report(final_report, "report.json")

# Step 6: check that all packages were delivered correctly
verify_all_delivered(final_report, packages)

# Step 7: print the report so we can see it on screen too
print(json.dumps(final_report, indent=4))