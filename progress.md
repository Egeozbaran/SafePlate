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
* **[IN PROGRESS]** Entity Resolution Planning: Outlined the 4-step logic to map messy recipe ingredients to the allergen taxonomy using Keyword Matching (Normalization -> Dictionary Building -> Matching -> Edge Formatting).

* **[COMPLETED]** Entity Resolution Code: Wrote the actual Python logic inside `src/data_prep.py`. The script dynamically builds a keyword dictionary based on word frequencies from `allergies_10k.csv` and maps the ingredients from `recipes_subset_5k.csv`.
  * *Outputs Generated:* `nodes_meals.csv`, `nodes_ingredients.csv`, `nodes_allergens.csv`, `edges_contains.csv`, `edges_is_a.csv`.

---
## Phase 3: Graph Construction
*Next Steps:*
* *Start up a local Neo4j database instance.*
* *Write a new Python script (`src/graph_build.py`) to connect to Neo4j using the official driver and push the generated nodes and edges using Cypher queries.*
