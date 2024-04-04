from collections import Counter
import math


# Inicializace globálních proměnných
login = "xlogin00"
attributes = {}
classes = []
objects = []

# Načtení dat ze souboru
def read_and_parse_data():
    file = open("model-"+login+".txt", "r")
    obj_id = 1
    for line in file:
        line = line.strip()
        if not line:
            continue
        if line.startswith("attributes"):
            line = file.readline().strip()
            while line != "}":
                attribute,value = line.split(":", 1)
                value = value.strip().split(" ")
                attributes[attribute] = value
                line = file.readline().strip()
        elif line.startswith("class"):
            line = file.readline().strip()
            while line != "}":
                classes.append(line)
                line = file.readline().strip()
        elif line.startswith("objects"):
            line = file.readline().strip()
            while line != "}":
                obj = {"id": obj_id}
                for value in line.split()[1:]:
                    if value in classes:
                        obj["class"] = value
                    else:
                        for attribute in attributes:
                            if value in attributes[attribute]:
                                obj[attribute] = value
                objects.append(obj)
                obj_id += 1
                line = file.readline().strip()
    file.close()

# Funkce pro výpočet entropy
def entropy(data):
    total = len(data)
    count = dict(Counter(data))
    entropy = 0
    for value in count.values():
        probability = value / total
        entropy -= probability * math.log2(probability)
    return entropy

# Funkce pro výběr nejlepšího atributu
def select_best_attribute(objects, attributes, classes):
    max_gain = float("-inf")
    best_attribute = None
    for attribute in attributes:
        total_entropy = entropy([obj["class"] for obj in objects])
        attribute_entropy = 0
        for value in attributes[attribute]:
            subset = [obj for obj in objects if obj[attribute] == value]
            attribute_entropy += len(subset) / len(objects) * entropy([obj["class"] for obj in subset])
        gain = total_entropy - attribute_entropy
        if gain > max_gain:
            max_gain = gain
            best_attribute = attribute
    return best_attribute

# Vytvoření stromu rozhodování s entropií v každém uzlu
def create_decision_tree(objects, attributes, classes):
    if len(set([obj["class"] for obj in objects])) == 1:
        return {"class": objects[0]["class"], "entropy": entropy([obj["class"] for obj in objects])}
    if not attributes:
        return {"class": max(set([obj["class"] for obj in objects]), key=[obj["class"] for obj in objects].count), "entropy": entropy([obj["class"] for obj in objects])}
    best_attribute = select_best_attribute(objects, attributes, classes)
    tree = {"attribute": best_attribute, "entropy": entropy([obj["class"] for obj in objects]), "attribute_entropies": {}}
    for attribute in attributes:
        attribute_entropy = 0
        for value in attributes[attribute]:
            subset = [obj for obj in objects if obj[attribute] == value]
            attribute_entropy += len(subset) / len(objects) * entropy([obj["class"] for obj in subset])
        tree["attribute_entropies"][attribute] = attribute_entropy
    tree["branches"] = {}
    for value in attributes[best_attribute]:
        subset = [obj for obj in objects if obj[best_attribute] == value]
        if not subset:
            tree["branches"][value] = {"class": max(set([obj["class"] for obj in objects]), key=[obj["class"] for obj in objects].count), "entropy": entropy([obj["class"] for obj in objects])}
        else:
            remaining_attributes = attributes.copy()
            del remaining_attributes[best_attribute]
            tree["branches"][value] = create_decision_tree(subset, remaining_attributes, classes)
    return tree

# Vytvoření grafu stromu rozhodování s vypsanými seznamy objektů v každém přechodu
def create_graph(node, parent=None):
    if "class" in node:
        return f'{parent} [shape=box, style=rounded, label="{node["class"]}"];\n'
    else:
        attribute_entropy_label = "|".join([f'{attribute}={entropy:.4f}' for attribute, entropy in node["attribute_entropies"].items()])
        main_attribute_label = node["attribute"]
        graph = f'{parent} [shape=record, label="{main_attribute_label.replace(" ","")}|{{{attribute_entropy_label.replace(" ","")}}}"];\n'
        for value, branch in node["branches"].items():
            # Gather object indices for this branch
            object_ids = [str(obj["id"]) for obj in objects if obj[node["attribute"]] == value]
            # Add object indices as labels
            branch_label = ", ".join(object_ids)
            graph += create_graph(branch, f'{parent}{value}')
            graph += f'{parent} -> {parent}{value} [label="{value} {{{branch_label.replace(" ","")}}}"];\n'
        return graph


read_and_parse_data()

decision_tree = create_decision_tree(objects, attributes, classes)

print(decision_tree)

dot_graph = "digraph DecisionTree {\n"
dot_graph += create_graph(decision_tree, "root")
dot_graph += "}\n"

file = open(login+".dot", "w")
file.write(dot_graph)
file.close()
