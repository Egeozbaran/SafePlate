import time
# pyrefly: ignore [missing-import]
from neo4j import GraphDatabase

# Connection details matching the docker-compose.yml
URI = "bolt://localhost:7687"
AUTH = ("neo4j", "safeplate123")

def build_graph():
    print("Connecting to Neo4j...")
    
    # Retry mechanism in case Neo4j is still starting up
    driver = None
    for i in range(5):
        try:
            driver = GraphDatabase.driver(URI, auth=AUTH)
            driver.verify_connectivity()
            break
        except Exception as e:
            print(f"Waiting for Neo4j to be ready... (Attempt {i+1}/5)")
            time.sleep(5)
            
    if not driver:
        print("Failed to connect to Neo4j. Make sure the Docker container is running!")
        return

    with driver.session() as session:
        print("1. Clearing any existing old data...")
        session.run("MATCH (n) DETACH DELETE n")

        print("2. Creating Meal Nodes...")
        session.run("""
            LOAD CSV WITH HEADERS FROM 'file:///nodes_meals.csv' AS row
            MERGE (m:Meal {id: row.id})
            SET m.name = row.name
        """)

        print("3. Creating Ingredient Nodes...")
        session.run("""
            LOAD CSV WITH HEADERS FROM 'file:///nodes_ingredients.csv' AS row
            MERGE (i:Ingredient {name: row.name})
        """)

        print("4. Creating Allergen Nodes...")
        session.run("""
            LOAD CSV WITH HEADERS FROM 'file:///nodes_allergens.csv' AS row
            MERGE (a:Allergen {name: row.name})
        """)
        
        # Creating Indexes for fast Edge creation
        try:
            session.run("CREATE INDEX FOR (m:Meal) ON (m.id)")
            session.run("CREATE INDEX FOR (i:Ingredient) ON (i.name)")
            session.run("CREATE INDEX FOR (a:Allergen) ON (a.name)")
        except Exception:
            pass # Indexes already exist

        print("5. Creating CONTAINS Edges (Meal -> Ingredient)...")
        session.run("""
            LOAD CSV WITH HEADERS FROM 'file:///edges_contains.csv' AS row
            MATCH (m:Meal {id: row.meal_id})
            MATCH (i:Ingredient {name: row.ingredient_name})
            MERGE (m)-[:CONTAINS]->(i)
        """)

        print("6. Creating IS_A Edges (Ingredient -> Allergen)...")
        session.run("""
            LOAD CSV WITH HEADERS FROM 'file:///edges_is_a.csv' AS row
            MATCH (i:Ingredient {name: row.ingredient_name})
            MATCH (a:Allergen {name: row.allergen_name})
            MERGE (i)-[:IS_A]->(a)
        """)

    driver.close()
    print("Graph Construction Complete! All nodes and edges have been loaded into Neo4j.")

if __name__ == "__main__":
    build_graph()
