# SafePlate Project Progress Log

This document tracks the step-by-step progress, decisions made, and milestones achieved during the development of the SafePlate Knowledge Graph project.

## Phase 1: Setup
* **[COMPLETED]** Virtual Environment: Initialized a Python virtual environment (`venv`) to isolate project dependencies.
* **[COMPLETED]** Dependencies: Created a `requirements.txt` file and installed the necessary libraries:
  * `pandas` (for data cleaning and entity resolution)
  * `neo4j` (chose the official Neo4j driver over py2neo for better bulk ingestion performance and compatibility)
  * `pykeen` (for Knowledge Graph Embeddings)
  * `jupyter` (for potential data exploration)

## Phase 2: Data Preparation
* **[COMPLETED]** Dataset Acquisition: Verified the presence of the two primary datasets in the `data/` folder:
  1. `RAW_recipes.csv` (Food.com recipes dataset).
  2. `allergies_10k.csv` (17-tag Allergen taxonomy dataset).
* **[COMPLETED]** Data Subsetting: To keep the Knowledge Graph manageable and performant for the scope of this project, we wrote and executed a Python script (`src/data_prep.py`) to extract exactly 5,000 recipes.
  * *Output Generated:* `recipes_subset_5k.csv` (containing only `id`, `name`, and `ingredients` columns).
* **[COMPLETED]** Entity Resolution Planning: Outlined the 4-step logic to map messy recipe ingredients to the allergen taxonomy using Keyword Matching (Normalization -> Dictionary Building -> Matching -> Edge Formatting).

* **[COMPLETED]** Entity Resolution Code: Wrote the actual Python logic inside `src/data_prep.py`. The script originally used a basic keyword frequency threshold, but was upgraded to use a **Confidence Scoring Ratio** algorithm (Word Probability) to prevent false positives from highly processed packaged foods. (Fulfills **LO7: Entity Resolution**)
  * *Outputs Generated:* `nodes_meals.csv`, `nodes_ingredients.csv`, `nodes_allergens.csv`, `edges_contains.csv`, `edges_is_a.csv`.

---
## Phase 3: Graph Construction (LO5)
* **[COMPLETED]** Start up a local Neo4j database instance: Created a `docker-compose.yml` file to spin up an official Neo4j container with a volume mapped to the `data/` folder for instant CSV reading.
* **[COMPLETED]** Write a new Python script (`src/graph_build.py`) to connect to Neo4j using the official driver and push the generated nodes and edges using Cypher queries. (Fulfills **LO5: Architectures**)

## Phase 4: Reasoning & Services (LO2, LO6, LO1, LO11)
* **[COMPLETED]** Logical Knowledge & Scalable Reasoning: Wrote a Python reasoning engine (`src/reasoning_engine.py`) executing a Cypher query to deduce if a meal is unsafe based on the rule `Meal(m) ∧ contains(m, i) ∧ is_allergen(i, a) → is_unsafe(m, a)` and dynamically drew new `UNSAFE_FOR` edges across the entire graph. (Fulfills **LO2: Logical Knowledge** and **LO6: Scalable Reasoning** - Focus Areas)
* **[COMPLETED]** KG Embeddings: Wrote `src/train_embeddings.py` to extract `CONTAINS` and `IS_A` edges into TSV triples. Trained a PyKEEN `TransE` model over 50 epochs to learn mathematical vector representations of the nodes and relations. Verified that the model successfully groups structurally similar baking ingredients (like flour, sugar, and vegetable oil) near 'butter'. (Fulfills **LO1: KG Embeddings**)
* **[COMPLETED]** Services: Built an interactive pure-Python web dashboard using Streamlit (`src/app.py`). It allows users to search the 5,000-recipe catalog using a dropdown, select their allergies, instantly query Neo4j for safety violations, and receive PyKEEN-powered safe substitute recommendations via heuristic post-filtering. (Fulfills **LO11: Services**)

## Phase 5: Portfolio & Documentation (LO8, LO9, LO10, LO12)
* **[TO DO]** Document how the system dynamically updates with new recipes. (Fulfills **LO8: KG Evolution**)
* **[TO DO]** Position project as a health-tech tool. (Fulfills **LO9: Real-World Applications**)
* **[TO DO]** Compare hidden allergens to hidden ownership link-analysis. (Fulfills **LO10: Financial KGs**)
* **[TO DO]** Explain how Graph Data Science improves text-based search. (Fulfills **LO12: Connections**)
