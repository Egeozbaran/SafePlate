import pandas as pd
import ast
import re
import os
from collections import defaultdict

def clean_text(text):
    if pd.isna(text):
        return ""
    text = str(text).lower()
    # Remove non-alphanumeric characters (keep spaces)
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    # Remove extra spaces
    return ' '.join(text.split())

def build_allergen_dict(allergies_file):
    df_allergies = pd.read_csv(allergies_file)
    word_allergen_counts = defaultdict(lambda: defaultdict(int))
    word_total_counts = defaultdict(int)
    
    # Words to ignore because they are too common and don't indicate an allergen
    stopwords = {'water', 'salt', 'sugar', 'natural', 'flavor', 'extract', 'acid', 'syrup', 'oil', 'sodium', 'contains', 'less', 'than', 'of', 'and', 'or', 'with', 'organic', 'powder', 'color'}
    
    # Iterate through the Kaggle taxonomy
    for _, row in df_allergies.iterrows():
        ingredient = clean_text(row['ingredient'])
        allergens_str = str(row['allergens'])
        
        try:
            allergens_list = ast.literal_eval(allergens_str)
        except:
            allergens_list = []
            
        if not isinstance(allergens_list, list):
            allergens_list = []
            
        # Clean allergen names
        cleaned_allergens = [re.sub(r'[^a-z0-9\s]', '', a.lower()).strip() for a in allergens_list]
        cleaned_allergens = [a for a in cleaned_allergens if a]
        
        words = set(ingredient.split()) # Use set to avoid double-counting in the same row
        for w in words:
            if len(w) > 2 and w not in stopwords:
                word_total_counts[w] += 1
                if cleaned_allergens:
                    for a in cleaned_allergens:
                        word_allergen_counts[w][a] += 1
                        
    # Create final keyword rules using a Confidence Ratio
    keyword_rules = defaultdict(set)
    for w, allergen_counts in word_allergen_counts.items():
        total_appearances = word_total_counts[w]
        for a, count in allergen_counts.items():
            confidence = count / total_appearances
            # Must appear at least 2 times AND have at least 20% confidence
            if count >= 2 and confidence >= 0.20: 
                keyword_rules[w].add(a)
                
    return keyword_rules

def process_recipes():
    recipes_file = '../data/recipes_subset_5k.csv'
    allergies_file = '../data/allergies_10k.csv'
    
    print("Building Allergen Dictionary from allergies_10k.csv...")
    keyword_rules = build_allergen_dict(allergies_file)
    
    print("Processing Recipes and performing Entity Resolution...")
    df_recipes = pd.read_csv(recipes_file)
    
    nodes_meals = []
    nodes_ingredients = set()
    edges_contains = []
    edges_is_a = []
    
    for _, row in df_recipes.iterrows():
        meal_id = row['id']
        meal_name = row['name']
        nodes_meals.append({'id': meal_id, 'name': meal_name})
        
        ingredients_str = str(row['ingredients'])
        try:
            ingredients_list = ast.literal_eval(ingredients_str)
        except:
            ingredients_list = []
            
        for ing in ingredients_list:
            ing_clean = clean_text(ing)
            if not ing_clean:
                continue
                
            nodes_ingredients.add(ing_clean)
            edges_contains.append({'meal_id': meal_id, 'ingredient_name': ing_clean})
            
            # Entity Resolution / Matching
            matched_allergens = set()
            words = ing_clean.split()
            for w in words:
                if w in keyword_rules:
                    matched_allergens.update(keyword_rules[w])
                        
            for ma in matched_allergens:
                edges_is_a.append({'ingredient_name': ing_clean, 'allergen_name': ma})

    # Save outputs for Neo4j
    print("Saving Nodes and Edges...")
    pd.DataFrame(nodes_meals).to_csv('../data/nodes_meals.csv', index=False)
    pd.DataFrame([{'name': i} for i in nodes_ingredients]).to_csv('../data/nodes_ingredients.csv', index=False)
    
    all_allergens = set()
    for rules in keyword_rules.values():
        all_allergens.update(rules)
    pd.DataFrame([{'name': a} for a in all_allergens]).to_csv('../data/nodes_allergens.csv', index=False)
    
    pd.DataFrame(edges_contains).to_csv('../data/edges_contains.csv', index=False)
    pd.DataFrame(edges_is_a).to_csv('../data/edges_is_a.csv', index=False)
    
    print("Entity Resolution Complete! Generated 5 files in data/:")
    print("- nodes_meals.csv")
    print("- nodes_ingredients.csv")
    print("- nodes_allergens.csv")
    print("- edges_contains.csv")
    print("- edges_is_a.csv")

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    process_recipes()
