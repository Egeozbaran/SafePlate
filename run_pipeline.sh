#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

echo "==========================================="
echo "   SafePlate Graph Generation Pipeline     "
echo "==========================================="

# Activate virtual environment
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
else
    echo "Virtual environment not found. Please create one with 'python3 -m venv venv'."
    exit 1
fi

echo "-------------------------------------------"
echo "Step 1: Data Preparation & Entity Resolution"
echo "-------------------------------------------"
python src/data_prep.py

echo "-------------------------------------------"
echo "Step 2: Building the Neo4j Knowledge Graph"
echo "-------------------------------------------"
python src/graph_build.py

echo "-------------------------------------------"
echo "Step 3: Running Cypher Reasoning Engine"
echo "-------------------------------------------"
python src/reasoning_engine.py

echo "-------------------------------------------"
echo "Step 4: Training TransE Neural Embeddings"
echo "-------------------------------------------"
python src/train_embeddings.py

echo "==========================================="
echo " Pipeline Complete! You can now run the UI "
echo " by typing: streamlit run src/app.py       "
echo "==========================================="
