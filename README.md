# SafePlate-Inferring-Dietary-Safety-through-Ingredient-Allergen-Knowledge-Graphs
A Knowledge Graph-based reasoning engine that automatically infers hidden food allergens in recipes using multi-hop logic and recommends safe dietary substitutes via graph embeddings. Built for TU Wien KG Course.
# SafePlate: Ingredient-Allergen Knowledge Graph 🍽️🛡️

SafePlate is a Knowledge Graph (KG) project designed to automatically infer dietary safety and detect "hidden" allergens in unlabeled recipes. By decoupling flat recipe data into a multi-tiered graph (Meal -> Ingredient -> Allergen), the system utilizes logical reasoning to flag unsafe meals and applies graph embeddings to recommend safe ingredient substitutes. 

This project was developed to demonstrate core Knowledge Graph principles, including entity resolution, scalable reasoning, and structural embeddings.

##  Key Features
* **Multi-Hop Reasoning:** Automatically infers recipe safety based on biological ingredient taxonomies (e.g., *Pancakes -> contains -> Milk -> is_a -> Dairy*).
* **Safe Substitutions:** Utilizes Knowledge Graph Embeddings (KGE) to find structurally similar ingredients that do not share the user's allergen profile.
* **Heterogeneous Data Integration:** Built by mapping unstructured recipe datasets to structured medical/allergen taxonomies.

## Tech Stack
* **Language:** Python 3.x
* **Graph Database:** Neo4j (Cypher)
* **Data Processing:** Pandas (Entity Resolution & Cleaning)
* **Embeddings:** PyKEEN / Node2Vec
