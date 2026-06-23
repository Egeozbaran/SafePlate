import os
import pandas as pd
from pykeen.pipeline import pipeline
from pykeen.triples import TriplesFactory
import torch

def prepare_data():
    print("1. Preparing Triples from CSVs...")
    
    # Load CONTAINS edges
    df_contains = pd.read_csv('data/edges_contains.csv', dtype=str)
    df_contains.columns = ['head', 'tail']
    df_contains['relation'] = 'CONTAINS'
    df_contains = df_contains[['head', 'relation', 'tail']]
    
    # Load IS_A edges
    df_isa = pd.read_csv('data/edges_is_a.csv', dtype=str)
    df_isa.columns = ['head', 'tail']
    df_isa['relation'] = 'IS_A'
    df_isa = df_isa[['head', 'relation', 'tail']]
    
    # Combine into one huge DataFrame of triples
    df_triples = pd.concat([df_contains, df_isa], ignore_index=True)
    
    # Drop any NaN rows just in case
    df_triples.dropna(inplace=True)
    
    # Save as TSV which PyKEEN expects
    os.makedirs('data', exist_ok=True)
    tsv_path = 'data/triples.tsv'
    df_triples.to_csv(tsv_path, sep='\t', index=False, header=False)
    print(f"-> Saved {len(df_triples)} triples to {tsv_path}")
    
    return tsv_path

def train_model(tsv_path):
    print("2. Loading Triples into PyKEEN...")
    tf = TriplesFactory.from_path(tsv_path)
    
    # Split into train/test for the pipeline
    training, testing = tf.split([0.8, 0.2], random_state=42)
    
    print("3. Training TransE Model (this may take 1-2 minutes)...")
    # Using a fast, basic configuration suitable for a local machine
    result = pipeline(
        training=training,
        testing=testing,
        model='TransE',
        training_kwargs=dict(num_epochs=50, batch_size=256),
        random_seed=1234,
        device='cpu' # Assuming MacBook
    )
    
    print("-> Training Complete!")
    
    # Save the model
    os.makedirs('models', exist_ok=True)
    model_path = 'models/transe_model'
    result.save_to_directory(model_path)
    print(f"4. Model saved to {model_path}")
    
    return result.model, tf

def test_butter(model, tf):
    print("\n--- 5. Quick Embedding Test: Closest to Butter ---")
    try:
        # Get the ID for 'butter'
        butter_id = tf.entity_to_id['butter']
        
        # We want to find entities structurally similar to butter
        # Extract the raw entity embeddings
        entity_embeddings = model.entity_representations[0](indices=None).detach()
        butter_emb = entity_embeddings[butter_id]
        
        # Calculate cosine similarity between Butter and ALL other entities
        # A simple mathematical check for "distance" in the vector space
        cos = torch.nn.CosineSimilarity(dim=1, eps=1e-6)
        similarities = cos(butter_emb.unsqueeze(0), entity_embeddings)
        
        # Get top 15 closest entities
        top_indices = torch.topk(similarities, 15).indices.tolist()
        top_scores = torch.topk(similarities, 15).values.tolist()
        
        id_to_entity = {v: k for k, v in tf.entity_to_id.items()}
        
        print("Most structurally similar ingredients to Butter:")
        for idx, score in zip(top_indices, top_scores):
            entity_name = id_to_entity[idx]
            if entity_name != 'butter':
                print(f"  - {entity_name} (Similarity: {score:.4f})")
    except KeyError:
        print("'butter' not found in the graph entities.")

if __name__ == "__main__":
    tsv_path = prepare_data()
    model, tf = train_model(tsv_path)
    test_butter(model, tf)
