import streamlit as st
from neo4j import GraphDatabase
import torch
from pykeen.pipeline import pipeline
from pykeen.triples import TriplesFactory
import os
import time

# --- Configuration ---
st.set_page_config(page_title="SafePlate", page_icon="🍽️", layout="centered")

URI = "bolt://localhost:7687"
AUTH = ("neo4j", "safeplate123")

# --- Caching Data Loading to keep app fast ---
@st.cache_resource
def get_neo4j_driver():
    return GraphDatabase.driver(URI, auth=AUTH)

@st.cache_data
def fetch_all_meals():
    driver = get_neo4j_driver()
    with driver.session() as session:
        result = session.run("MATCH (m:Meal) RETURN m.name AS name ORDER BY m.name")
        return [record["name"] for record in result]

@st.cache_data
def fetch_all_allergens():
    driver = get_neo4j_driver()
    with driver.session() as session:
        result = session.run("MATCH (a:Allergen) RETURN a.name AS name ORDER BY a.name")
        return [record["name"] for record in result]

@st.cache_resource
def load_kge_model():
    model_path = 'models/transe_model'
    if not os.path.exists(model_path):
        return None, None
    
    # Load PyKEEN model
    model = torch.load(os.path.join(model_path, 'trained_model.pkl'), map_location='cpu', weights_only=False)
    tf = TriplesFactory.from_path('data/triples.tsv')
    return model, tf

# --- Helper Functions ---
def get_ingredients_for_meal(meal_name):
    driver = get_neo4j_driver()
    with driver.session() as session:
        query = "MATCH (m:Meal {name: $meal_name})-[:CONTAINS]->(i:Ingredient) RETURN i.name AS ing"
        result = session.run(query, meal_name=meal_name)
        return [record["ing"] for record in result]

def get_dangerous_ingredients(meal_name, allergen_name):
    driver = get_neo4j_driver()
    with driver.session() as session:
        query = """
        MATCH (m:Meal {name: $meal_name})-[:CONTAINS]->(i:Ingredient)-[:IS_A]->(a:Allergen {name: $allergen_name})
        RETURN i.name AS ing
        """
        result = session.run(query, meal_name=meal_name, allergen_name=allergen_name)
        return [record["ing"] for record in result]

def find_safe_meal_alternative(unsafe_meal_name, user_allergies, model, tf):
    driver = get_neo4j_driver()
    # 1. Get the meal ID from Neo4j
    with driver.session() as session:
        res = session.run("MATCH (m:Meal {name: $name}) RETURN m.id AS meal_id LIMIT 1", name=unsafe_meal_name).single()
        if not res:
            return "No alternative found (Meal not in database)."
        unsafe_meal_id = str(res["meal_id"])

    if not model or unsafe_meal_id not in tf.entity_to_id:
        return "No alternative found (model missing or meal unknown)."

    target_id = tf.entity_to_id[unsafe_meal_id]
    entity_embeddings = model.entity_representations[0](indices=None).detach()
    target_emb = entity_embeddings[target_id]
    
    # Cosine Similarity
    cos = torch.nn.CosineSimilarity(dim=1, eps=1e-6)
    similarities = cos(target_emb.unsqueeze(0), entity_embeddings)
    
    # Search the entire graph to guarantee we find a safe meal
    num_entities = len(tf.entity_to_id)
    top_indices = torch.topk(similarities, num_entities).indices.tolist()
    id_to_entity = {v: k for k, v in tf.entity_to_id.items()}
    
    with driver.session() as session:
        for idx in top_indices:
            candidate_id_str = id_to_entity[idx]
            
            # 1. Skip if it's the exact same meal
            if candidate_id_str == unsafe_meal_id:
                continue
                
            # 2. Check if the candidate is actually a Meal AND fetch its name
            query = """
            MATCH (m:Meal {id: $candidate})
            RETURN m.name AS name
            """
            res_meal = session.run(query, candidate=candidate_id_str).single()
            if not res_meal:
                continue
                
            candidate_name = res_meal["name"]
                
            # 3. Check if the candidate meal triggers ANY of the user's allergies
            safety_query = """
            MATCH (m:Meal {id: $candidate})-[:UNSAFE_FOR]->(a:Allergen)
            WHERE a.name IN $user_allergies
            RETURN count(a) AS bad_count
            """
            res_safety = session.run(safety_query, candidate=candidate_id_str, user_allergies=user_allergies).single()
            
            if res_safety["bad_count"] == 0:
                # We found the structurally closest, 100% SAFE meal!
                return candidate_name
                
    return "No safe alternative found."

st.set_page_config(page_title="SafePlate", page_icon="🍽️", layout="wide")

# Add a background image and custom CSS for professional UI
page_bg_img = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif !important;
}

.stApp {
    background: linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.8)), url("https://images.unsplash.com/photo-1498837167922-ddd27525d352?q=80&w=2000&auto=format&fit=crop") !important;
    background-size: cover !important;
    background-position: center !important;
    background-attachment: fixed !important;
}

h1 {
    font-size: 3.5rem !important;
    font-weight: 600 !important;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    letter-spacing: -1px;
}

h3 {
    font-weight: 300 !important;
    color: #E9ECEF !important;
}

/* Style the selectboxes to look glassy */
div[data-baseweb="select"] > div {
    background-color: rgba(0, 0, 0, 0.4) !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    border-radius: 8px !important;
}

/* Footer style */
.footer {
    position: fixed;
    bottom: 15px;
    right: 25px;
    font-size: 0.85rem;
    color: rgba(255, 255, 255, 0.4);
    font-style: italic;
    z-index: 100;
}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)

ALLERGEN_EMOJIS = {
    "dairy": "🥛",
    "tree nuts": "🌰",
    "peanuts": "🥜",
    "shellfish": "🦐",
    "fish": "🐟",
    "wheat": "🌾",
    "soybeans": "🫘",
    "eggs": "🥚"
}

st.title("🍽️ SafePlate")
st.subheader("Knowledge Graph Dietary Safety Engine")

st.markdown("---")

# 1. Input Section
col1, col2 = st.columns(2)

with col1:
    meals = fetch_all_meals()
    # Streamlit's selectbox has a built-in search bar!
    selected_meal = st.selectbox("🔍 Search for a Recipe", meals, index=None, placeholder="Type or select a recipe...")

with col2:
    allergens = fetch_all_allergens()
    selected_allergies = st.multiselect("⚠️ Select your Allergies", allergens)

st.markdown("---")

# 2. Action Section
if st.button("Check Safety & Find Alternatives"):
    if not selected_meal:
        st.warning("Please search for a recipe first!")
    elif not selected_allergies:
        st.success(f"**{selected_meal.title()}** is SAFE because you didn't select any allergies!")
    else:
        with st.spinner("Querying Knowledge Graph..."):
            driver = get_neo4j_driver()
            
            unsafe_allergies_found = []
            with driver.session() as session:
                # Query the explicit reasoning edge we created in Phase 4!
                query = """
                MATCH (m:Meal {name: $meal_name})-[:UNSAFE_FOR]->(a:Allergen)
                WHERE a.name IN $user_allergies
                RETURN a.name AS allergen
                """
                result = session.run(query, meal_name=selected_meal, user_allergies=selected_allergies)
                unsafe_allergies_found = [record["allergen"] for record in result]
            
            if not unsafe_allergies_found:
                st.success(f"✅ **{selected_meal.title()}** is 100% SAFE for you!")
                
                with st.sidebar:
                    st.markdown(f"### 🧺 Ingredients in {selected_meal.title()}")
                    current_ingredients = get_ingredients_for_meal(selected_meal)
                    for ing in current_ingredients:
                        st.warning(f"✅ {ing.title()} (Safe)")
            else:
                st.error(f"❌ **WARNING:** {selected_meal.title()} is UNSAFE!")
                
                # Load PyKEEN model for substitute generation
                model, tf = load_kge_model()
                
                all_bad_ings = set()
                
                for bad_allergy in unsafe_allergies_found:
                    emoji = ALLERGEN_EMOJIS.get(bad_allergy.lower(), "⚠️")
                    st.markdown(f"### {emoji} Violations for **{bad_allergy.title()}**:")
                    
                    # Find exactly which ingredients caused the violation
                    bad_ings = get_dangerous_ingredients(selected_meal, bad_allergy)
                    all_bad_ings.update(bad_ings)
                    
                    for bad_ing in bad_ings:
                        st.error(f"Contains **{bad_ing.title()}**")
                
                with st.sidebar:
                    st.markdown(f"### 🧺 Ingredients in {selected_meal.title()}")
                    current_ingredients = get_ingredients_for_meal(selected_meal)
                    for ing in current_ingredients:
                        if ing in all_bad_ings:
                            st.error(f"❌ {ing.title()} (Unsafe)")
                        else:
                            st.warning(f"✅ {ing.title()} (Safe)")
                
                st.markdown("---")
                st.markdown("### 💡 AI Recommendation")
                safe_meal = find_safe_meal_alternative(selected_meal, selected_allergies, model, tf)
                st.markdown(f"##### Instead of <span style='color:#FF4B4B;'>{selected_meal.title()}</span>, you should try cooking: <span style='color:#4CAF50; font-style:italic;'>{safe_meal.title()}</span>", unsafe_allow_html=True)
                
                if safe_meal and safe_meal != "No safe alternative found.":
                    with st.expander(f"👀 View Ingredients for {safe_meal.title()}"):
                        safe_meal_ingredients = get_ingredients_for_meal(safe_meal)
                        if safe_meal_ingredients:
                            for ing in safe_meal_ingredients:
                                st.write(f"- {ing.title()}")
                        else:
                            st.write("Ingredient list not available.")

# Footer
st.markdown("<div class='footer'>Developed by Ege Ozbaran</div>", unsafe_allow_html=True)
