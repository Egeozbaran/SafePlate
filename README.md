# SafePlate: Inferring Dietary Safety through Ingredient-Allergen Knowledge Graphs

![Neo4j](https://img.shields.io/badge/Neo4j-018bff?style=for-the-badge&logo=neo4j&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)

SafePlate is an advanced Knowledge Graph reasoning engine designed to automatically infer dietary safety and detect hidden allergens in unlabeled recipes. Developed for the TU Wien Knowledge Graph Course, this project transforms unstructured recipe data into a multi-tiered graph ontology (`Meal -> Ingredient -> Allergen`) to support explicit multi-hop reasoning and implicit latent space clustering.

## Project Overview

SafePlate utilizes a hybrid Neuro-Symbolic Artificial Intelligence architecture:
1. **Symbolic AI (Explicit Rules):** Uses Neo4j and the Cypher query language to traverse the graph and infer deterministic logical rules (e.g., if a meal contains an ingredient, and that ingredient belongs to an allergen taxonomy, the meal is marked as `UNSAFE_FOR` the user).
2. **Neural ML (Implicit Patterns):** Uses PyKEEN (TransE) to project the graph's topology into a high-dimensional mathematical latent space. This allows the system to discover structurally identical, safe substitute meals when a user's selected recipe violates their dietary restrictions.

## Key Technical Features

* **Statistical Entity Resolution:** Implements a probabilistic confidence scoring algorithm to automatically map raw, unstructured recipe ingredients to a strict medical allergen taxonomy. The algorithm precision-filters noise (e.g., preventing "beef" from falsely triggering a dairy allergy) while allowing exact string overrides for ambiguous composites (e.g., mapping "flour" to Wheat, while safely ignoring "almond flour").
* **Automated Graph Ingestion:** A robust Python pipeline that cleans raw CSVs, extracts nodes/edges, and streams them directly into a containerized Neo4j database.
* **Neuro-Symbolic Pipeline:** Merges deterministic Cypher reasoning with Machine Learning similarity search (Cosine Similarity on TransE Embeddings).
* **Interactive UI:** A real-time, responsive web interface built with Streamlit that queries the Neo4j database and PyKEEN models to serve live dietary assessments and AI recommendations.

## Data Sources & Open Source Reproducibility

To ensure this repository is 100% open-source and reproducible without requiring users to download massive raw files, the repository includes a pre-processed subset of the data:
* **`allergies_10k.csv`**: A Kaggle taxonomy mapping ingredients to medical allergens.
* **`recipes_subset_5k.csv`**: A curated 5,000-recipe subset extracted from the massive 280MB+ Food.com Kaggle dataset.

By providing this 5K subset directly in the `/data` folder, anyone who clones this repository can instantly run the full pipeline without hitting GitHub's 100MB file limit or requiring external API keys. If you wish to run the pipeline on the full 500,000 recipe dataset, simply download the raw CSV from Kaggle and point `data_prep.py` to it.

## Setup & Installation

### Prerequisites
* Python 3.11+
* Docker Desktop (Required for Neo4j)

### 1. Environment Setup
```bash
# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Start the Graph Database
```bash
# Start the Neo4j instance in the background
docker compose up -d
```
*Note: Wait approximately 10 seconds for the database engine to fully initialize before proceeding.*

### 3. Run the Backend Pipeline
The entire backend architecture can be built using a single provided shell script. This script will sequentially run data preparation, graph construction, Cypher reasoning, and PyKEEN embedding training.
```bash
# Execute the pipeline
./run_pipeline.sh
```

### 4. Launch the Application
Once the pipeline has completed and the models are trained, launch the interactive user interface:
```bash
streamlit run src/app.py
```

## Project Structure

```text
SafePlate/
├── data/                  # Raw Kaggle datasets, generated CSVs, and PyKEEN TSVs
├── instructions/          # Project academic requirements and Learning Outcomes
├── models/                # Saved TransE neural embeddings
├── neo4j_data/            # Persistent Docker volume for the Graph Database
├── src/
│   ├── data_prep.py       # Data cleaning and probabilistic Entity Resolution
│   ├── graph_build.py     # Neo4j database initialization and population
│   ├── reasoning_engine.py# Cypher logic for multi-hop graph inference
│   ├── train_embeddings.py# PyKEEN ML training script for vector representations
│   └── app.py             # Streamlit User Interface
├── docker-compose.yml     # Neo4j container configuration
├── run_pipeline.sh        # Master execution script for the backend
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation
```

## Developer
Developed by Ege Ozbaran for the TU Wien Knowledge Graphs course.
