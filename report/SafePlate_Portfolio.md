# Portfolio Report: SafePlate - Inferring Dietary Safety through Ingredient-Allergen Knowledge Graphs

*Developed for the TU Wien Knowledge Graphs Course*

---


## 1. Scenario

### 1.1 Domain
The domain of this Knowledge Graph (KG) application is **Food Safety & Health Informatics (LO9)**. Food allergies are a life-threatening reality for millions. Traditional recipe platforms rely on humans to manually tag recipes as "Dairy-Free" or "Gluten-Free," creating a high risk of fatal oversight if a tag is forgotten. SafePlate shifts the burden of safety from human data-entry to algorithmic inference by automatically auditing every ingredient against a strict medical taxonomy to detect "hidden" allergens.

Interestingly, this logic mirrors anti-money laundering (AML) algorithms used in **Financial Knowledge Graphs (LO10)**. In banking, bad actors obscure illegal activities through webs of shell companies, forcing KGs to use link-analysis to detect "Hidden Ownership" (e.g., *Company A -> owned by -> Company B -> owned by -> Sanctioned Individual*). SafePlate uses the exact same multi-hop traversal logic to detect "Hidden Allergens" (e.g., *Pancakes -> contains -> Butter -> is_a -> Dairy*). 

### 1.2 Service
SafePlate provides an interactive **Dietary Assessment and Recommendation Service (LO11)**. 
* **Query Execution:** Users input a recipe name and their specific allergies. The KG instantly returns a deterministic safety assessment.
> **[INSERT SCREENSHOT 1 HERE: Image of the opening Streamlit UI (Empty Search State)]**
> 
> **[INSERT SCREENSHOT 2 HERE: Image of the user selecting a specific food and allergy from the dropdowns]**
> 
> **[INSERT SCREENSHOT 3 HERE: Image of the final result showing the safety assessment and the AI recommendation]**

---

## 2. KG Construction

### 2.1 Datasets & Creation
To demonstrate **KG Creation from heterogeneous data (LO7)**, two unstructured datasets were merged:
1. **Food.com Recipes (Source Nodes):** A curated 5,000-recipe subset containing meals and ingredient lists, but critically lacking allergen labels.
2. **Allergies 10k (Taxonomy Layer):** A medical dataset mapping raw ingredients to 17 biological allergen categories.

**Entity Resolution:** Because "flour" in a recipe doesn't directly map to "Gluten," a probabilistic confidence scoring algorithm was built in Python. It analyzed word frequencies to map raw text to the taxonomy. To handle ambiguous cases (e.g., ensuring "almond flour" doesn't falsely trigger a gluten alert), exact string overrides were injected into the logic. 

### 2.2 Technologies & Architecture
The system employs a decoupled, highly scalable **Architecture (LO5)**:
* **Data Processing:** `pandas` and custom Python scripts.
* **Graph Storage:** Dockerized **Neo4j** instance.
* **Embeddings:** PyTorch and **PyKEEN**.
* **Interface:** Streamlit.

### 2.3 Data Model & Evolution
The graph relies on a strict 3-tier **Data Model (LO4)**: `(Meal)-[:CONTAINS]->(Ingredient)-[:IS_A]->(Allergen)`. 

* **3 Concrete Construction Examples:**
  1. `Meal` nodes were constructed by extracting unique strings from the 'name' column in the Food.com dataset (e.g., creating a node `(m:Meal {name: 'Pancakes'})`).
  2. `[:CONTAINS]` edges were constructed by tokenizing the string arrays in the 'ingredients' column and drawing directed edges from the meal to the individual ingredients.
  3. `[:IS_A]` edges were constructed by iterating over the 10k medical taxonomy and drawing edges from the parsed ingredient nodes to biological allergen nodes.

To support **KG Evolution (LO8)**, the system utilizes an automated `run_pipeline.sh` script. When new recipes or updated FDA allergen rules are provided, the script re-runs the Entity Resolution, wipes Neo4j, repopulates the schema, and retrains the ML models automatically, preventing the need for complex, manual schema migrations.

---

## 3. ML-based Representation

### 3.1 Chosen Representation
To satisfy **LO1 (KG Embeddings)**, the system uses the **TransE** algorithm trained via PyKEEN. 
* **5 Concrete Examples of Vector Representations:** 
  1. `Meal` Node (e.g., *Pancakes*)
  2. `Ingredient` Node (e.g., *Butter*)
  3. `Allergen` Node (e.g., *Dairy*)
  4. `[:CONTAINS]` Edge (structural culinary relationship)
  5. `[:IS_A]` Edge (biological medical relationship)
* **True Positive Example:** TransE correctly learned that `Butter` and `Vanilla` exist extremely close together in the latent vector space (Similarity: 0.60+), predicting a structural culinary relationship that is true to real-world baking.
* **False Positive Example:** A notable false positive prediction occurred where TransE clustered `Almond Flour` closely to `Wheat Flour` because they share identical structural `[:CONTAINS]` usage across baking recipes. While structurally true, this falsely implied they share the exact same safety profile before our deterministic logic rules intervened.

### 3.2 Evolution & Completion
The ML representation is used to implicitly **complete the KG** by bridging gaps that pure logic cannot solve. While logic can block an unsafe meal, TransE embeddings allow the service to find the closest vector to the blocked meal that lacks the user's specific allergen edges, thereby offering a safe, culinary substitute.

### 3.3 Context & Limitations
While TransE is highly scalable, it struggles with modeling 1-to-N or complex transitive relations compared to more advanced models like RotatE. However, for identifying structural recipe similarities, it proved highly efficient.

---

## 4. Logic-based Representation

### 4.1 Chosen Representation
To satisfy **LO2 (Logical Knowledge)**, deterministic Cypher rules were applied.
* **5 Concrete Examples of Logic & Queries:**
  1. **Schema Inference:** `MATCH (m:Meal)-[:CONTAINS]->(i:Ingredient) RETURN m.name, i.name`
  2. **Rule-Based Filtering:** `MATCH (i:Ingredient)-[:IS_A]->(a:Allergen {name: 'dairy'}) RETURN i.name`
  3. **Multi-Hop Conditional:** `MATCH (m:Meal)-[:CONTAINS]->(i:Ingredient)-[:IS_A]->(a:Allergen) WHERE a.name IN ['wheat', 'gluten'] RETURN m`
  4. **Recursive Exploration:** `MATCH path = (m:Meal)-[:CONTAINS|IS_A*1..5]->(a:Allergen) RETURN path` (This allows arbitrarily deep graph traversal if the taxonomy expands into nested sub-allergens).
  5. **Edge Creation (The Core Rule):** `MATCH (m:Meal)-[:CONTAINS]->(i:Ingredient)-[:IS_A]->(a:Allergen) MERGE (m)-[r:UNSAFE_FOR]->(a)` (This explicitly draws a permanent new risk relationship in the graph).

### 4.2 Evolution
This logic is used to actively **update and correct the KG**. By running this query, thousands of new `[:UNSAFE_FOR]` edges are explicitly created and permanently drawn in the database, actively evolving the knowledge graph's capabilities.

### 4.3 Context & Limitations
This approach demonstrates **Scalable Reasoning (LO6)**, executing across 5,000 recipes and thousands of ingredients in O(1) traversal time per edge within Neo4j. The limitation of pure logic is its brittleness; if an ingredient string is misspelled in the raw data, the deterministic edge will fail to draw, which is why the ML representations are used as a fallback.

---

## 5. Reflection

### 5.1 Outcome of Service
The final Streamlit application successfully acts as an automated safety-net. Users can seamlessly query meals and receive immediate, deterministically proven safety warnings along with AI-driven substitute recommendations.

> **[INSERT SCREENSHOT 4 HERE: Image of the Neo4j Browser (localhost:7474) showing the visual Meal -> Ingredient -> Allergen graph]**

### 5.2 Data Model Reflection
If this project were built in a Relational Database (SQL), executing the multi-hop safety check would require 3 computationally expensive `JOIN` operations. By using a Graph Data Model, relationships act as physical pointers, making multi-hop traversal infinitely faster. Furthermore, the graph topology was a strict prerequisite; PyKEEN embeddings cannot be trained on flat SQL tables. 

### 5.3 Connections: AI, ML, and Data Science
SafePlate demonstrates the power of **Neuro-Symbolic AI (LO12)**. Traditional recipe websites use standard text-based search (e.g., SQL `LIKE "%gluten-free%"`). This is brittle; if a recipe contains "flour" but the author forgot to write "gluten," standard search fails. SafePlate understands the semantic *meaning* of the data. 
By combining **Symbolic AI** (deterministic Cypher logic for absolute medical safety) with **Machine Learning** (TransE embeddings for flexible, implicit culinary substitutions), the system overcomes the individual limitations of both fields, yielding a highly intelligent, specialized Data Science pipeline.
