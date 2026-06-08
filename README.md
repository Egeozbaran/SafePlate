# SafePlate: Inferring Dietary Safety through Ingredient-Allergen Knowledge Graphs 🍽️🛡️

![Neo4j](https://img.shields.io/badge/Neo4j-018bff?style=for-the-badge&logo=neo4j&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white)

SafePlate is an advanced Knowledge Graph (KG) reasoning engine designed to automatically infer dietary safety and detect "hidden" allergens in unlabeled recipes. Built for the TU Wien Knowledge Graph Course, this project transforms flat recipe data into a multi-tiered graph (`Meal -> Ingredient -> Allergen`) to support multi-hop reasoning.

## 🌟 Key Features

* **Advanced Entity Resolution:** Uses a probabilistic Confidence Scoring algorithm to accurately map unstructured, human-written recipe ingredients to strict medical allergen taxonomies, filtering out noise from highly processed packaged foods.
* **Multi-Hop Logical Reasoning:** Automatically infers recipe safety based on biological hierarchies (e.g., *Pancakes -> contains -> Milk -> is_a -> Dairy*).
* **Safe Substitutions (Coming Soon):** Utilizes Knowledge Graph Embeddings (KGE) via PyKEEN to recommend structurally similar ingredients that do not share the user's allergen profile.

## 🏗️ Architecture & Data Pipeline

1. **Data Preparation (`src/data_prep.py`):** Ingests raw `RAW_recipes.csv` and `allergies_10k.csv`. Performs data cleaning, tokenization, and Entity Resolution using word probability confidence ratios. Outputs 5 clean CSVs representing Nodes and Edges.
2. **Graph Database (`docker-compose.yml`):** Spins up an official Neo4j instance via Docker, volume-mapped to the local `data/` directory for high-speed bulk ingestion.
3. **Graph Construction (`src/graph_build.py`):** Uses the official Neo4j Python driver to execute Cypher queries that build the schema, create indexes, and load the multi-tiered graph.

## 🚀 Setup & Installation

### Prerequisites
* Python 3.11+
* Docker Desktop

### 1. Environment Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Generate the Data
```bash
python src/data_prep.py
```

### 3. Start Neo4j Database
```bash
docker compose up -d
```
*Wait ~10 seconds for the Neo4j engine to fully boot up.*

### 4. Build the Knowledge Graph
```bash
python src/graph_build.py
```

### 5. Visualize the Graph
Open your web browser and navigate to `http://localhost:7474`.
* **Username:** `neo4j`
* **Password:** `safeplate123`

Run the following Cypher query to see a sample of the graph:
```cypher
MATCH path=(m:Meal)-[:CONTAINS]->(i:Ingredient)-[:IS_A]->(a:Allergen)
RETURN path LIMIT 25
```

## 📁 Project Structure

```text
SafePlate/
├── data/                  # Contains raw datasets and generated Node/Edge CSVs
├── instructions/          # Project requirements and Learning Outcomes (LO) guidelines
├── src/
│   ├── data_prep.py       # Data cleaning and Entity Resolution logic
│   └── graph_build.py     # Neo4j connection and Cypher ingestion script
├── docker-compose.yml     # Neo4j Docker configuration
├── requirements.txt       # Python dependencies
├── progress.md            # Detailed log of completed phases and LO mappings
└── README.md              # Project overview
```
