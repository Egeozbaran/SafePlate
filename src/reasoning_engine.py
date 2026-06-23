# pyrefly: ignore [missing-import]
from neo4j import GraphDatabase

# Connection details
URI = "bolt://localhost:7687"
AUTH = ("neo4j", "safeplate123")

def run_reasoning_engine():
    print("Connecting to SafePlate Knowledge Graph...")
    
    try:
        driver = GraphDatabase.driver(URI, auth=AUTH)
        driver.verify_connectivity()
    except Exception as e:
        print("Failed to connect to Neo4j. Is the Docker container running?")
        return

    with driver.session() as session:
        print("Executing Scalable Reasoning Rule...")
        print("Rule: ∀m, i, a : Meal(m) ∧ contains(m, i) ∧ is_allergen(i, a) → is_unsafe(m, a)")
        
        # The Cypher query that infers and saves the new relationship
        query = """
            MATCH (m:Meal)-[:CONTAINS]->(i:Ingredient)-[:IS_A]->(a:Allergen)
            MERGE (m)-[r:UNSAFE_FOR]->(a)
            RETURN a.name AS allergen, count(DISTINCT m) AS flagged_meals
            ORDER BY flagged_meals DESC
        """
        
        results = session.run(query)
        
        print("\n--- Reasoning Complete ---")
        print("Total Meals Flagged as Unsafe by Allergen Category:")
        
        total_flags = 0
        for record in results:
            allergen = record["allergen"]
            count = record["flagged_meals"]
            total_flags += count
            print(f"- {allergen.capitalize()}: {count} unsafe meals")
            
        print(f"\nSuccessfully drew {total_flags} new [UNSAFE_FOR] connections in the graph!")

    driver.close()

if __name__ == "__main__":
    run_reasoning_engine()
