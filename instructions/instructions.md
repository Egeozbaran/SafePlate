# SafePlate: Ingredient-Allergen Knowledge Graph 🍽️🛡️
## Comprehensive Project Specification

This document serves as the master specification for the **SafePlate** mini-project, developed for the TU Wien Knowledge Graphs course. It outlines the project's academic goals, dataset selections, technical architecture, and execution strategy.

---

## 1. Project Identity & Context

* **Domain:** Food Safety & Health Informatics.
* **Core Objective:** Build a Knowledge Graph (KG) that uses multi-hop reasoning to identify "hidden" allergens in recipes where labels are missing or incomplete, and utilizes embeddings to suggest safe ingredient substitutes.
* **Workload / Scope:** 3 ECTS (Approx. 40 hours of work).
* **Target Grade:** B3 or S1 (Requires satisfying at least 10 Learning Outcomes).
* **Deadline Strategy:** "Early Track" (Submission by June 16). This provides a safety net by reducing the required Learning Outcomes (LOs) by one if needed.

---

## 2. Academic Requirements & Grading Strategy

To achieve the target grade while minimizing extreme technical risks, the project targets **10 specific Learning Outcomes (LOs)** and deliberately excludes Graph Neural Networks (LO3).

### Focus Areas (Deep Implementation)
* **LO2: Logical Knowledge:** Defining the explicit rule that if a meal contains an ingredient, and that ingredient belongs to an allergen class, the meal is unsafe.
* **LO6: Scalable Reasoning:** Applying this logical rule programmatically across thousands of unlabeled recipes simultaneously to infer safety.

### Basic Proficiency Areas
* **LO1: KG Embeddings:** Using vector similarity to find safe ingredient substitutes (e.g., finding an ingredient structurally similar to butter but not linked to dairy).
* **LO4: Data Models:** Designing a 3-tier schema: `Meal -> Ingredient -> AllergenClass`.
* **LO5: Architectures:** Building the data pipeline from raw CSV ingestion to Neo4j graph storage.
* **LO7: KG Creation:** Performing Entity Resolution to merge heterogeneous datasets (Food.com recipes + Kaggle medical taxonomy).
* **LO8: KG Evolution:** Documenting how the system can dynamically update when new recipes or medical allergen guidelines are introduced.
* **LO9: Real-World Applications:** Positioning the project as a health-tech tool for allergy sufferers.
* **LO10: Financial KGs:** Addressed conceptually in the portfolio by comparing our "hidden allergen" link-analysis to "hidden ownership" link-analysis in banking.
* **LO11: Services:** Designing a query interface (e.g., "Is this recipe safe for me?" or "Suggest a substitute").
* **LO12: Connections:** Explaining how Graph Data Science techniques improve standard text-based search.

### Excluded
* **LO3: Graph Neural Networks:** Excluded to ensure the project remains within the 40-hour scope and avoids high-risk coding hurdles.

---

## 3. Data Strategy

To prove **LO7 (KG Creation)**, we must integrate two heterogeneous datasets. To maintain performance and clean data, we will use a *subset* approach rather than massive, messy datasets.

### Dataset A: The "Recipe" Dataset (Source Nodes)
* **Source:** Food.com Recipes & User Interactions (Kaggle).
* **Scope:** A curated subset of 2,000–5,000 recipes.
* **Content:** Contains the meal name and ingredient list (e.g., *Pancakes -> Flour, Milk, Eggs*).
* **Crucial Feature:** It does **not** contain allergen labels. This allows the KG to do the "work" of discovering them.

### Dataset B: The "Allergen" Dataset (Knowledge Layer)
* **Source:** Ingredients with 17 Allergen Tags (Kaggle).
* **Content:** A taxonomy mapping raw ingredients to biological allergen categories (e.g., *Milk -> Dairy*, *Flour -> Gluten*).

### Entity Resolution (The Join)
* The datasets will be merged on the `Ingredient` string.
* Preprocessing will involve lowercase normalization, string cleaning, and substring matching (e.g., mapping "organic whole milk" from Dataset A to "milk" in Dataset B).

---

## 4. Technical Architecture

The tech stack is optimized for rapid development and straightforward graph querying.

* **Primary Language:** Python 3.x
* **IDE:** Google Antigravity (Utilizing the built-in AI agent for boilerplate code, data pipeline setup, and Cypher query generation).
* **Data Processing & Cleaning:** `pandas`
* **Graph Database:** Neo4j (Allows for visual validation and uses the Cypher query language for reasoning rules).
* **Graph Bridge:** `py2neo` (To push pandas dataframes into Neo4j).
* **Embeddings:** `PyKEEN` or `Node2Vec` (For standard out-of-the-box substitute recommendations).

---

## 5. Core Execution Logic

### Phase 1: The Safety Check (Reasoning)
The core logic mirrors the "Indirect Company Control" example from the course material.
* **Mathematical Rule:** `Meal(m) ∧ contains(m, i) ∧ is_allergen(i, a) → is_unsafe(m, a)`
* **Cypher Implementation Idea:**
  ```cypher
  MATCH (m:Meal)-[:CONTAINS]->(i:Ingredient)-[:IS_A]->(a:Allergen)
  RETURN m.name, a.name
  Phase 2: The Safe Substitute (Embeddings)

Instead of just blocking a recipe, the system will offer a fix.

Method: Run graph embeddings on the network.

Action: If a user wants to make a Dairy-heavy recipe but has a Dairy allergy, the system finds the closest vector to the required ingredient that does not have an edge connecting to the Dairy node.

### 6. Development Milestones
Setup: Initialize the Antigravity workspace, configure the Python virtual environment, and install pandas, py2neo, and pykeen.

Data Prep: Extract 5,000 rows from Food.com, clean ingredient strings, and map them to the 17-tag dataset.

Graph Build: Push the Nodes (Meal, Ingredient, Allergen) and Edges (CONTAINS, IS_A) to a local Neo4j instance.

Logic Implementation: Write and test the Cypher reasoning queries.

Embedding Service: Train a basic PyKEEN model on the graph to extract similar ingredients.

Documentation: Compile the final portfolio PDF mapping the technical work to the 10 Learning Outcomes.