# Note — Passage a 50k

## Ce qui ne change pas

Le pipeline reste valide: 
    extraction
    embedding
    vector search
    scoring LLM + filter. 

## Ce qui change

**Vector search**
    L'utilisation de IndexFlatIP est une recherche exacte en O(N).
    a 70 candidats c'est faible, a 50 000 c'est encore rapide (~10ms), mais l'index ne tient plus en memoire a chaque requete.
    Il faut une base vectorielle persistante avec  des mises a jour incrementales (pgvector, Qdrant, Weaviate).
    Aussi l'index HNSW devient pertinent pour des millions de profils (graph).

**Mises a jour en continu**
    Les modification de candidat doit declencher un re-embedding du seul candidat.
    Potentielement un system de webhook ou event.

**Extraction LLM a l'ingestion**
    Pour 50k profils, l'extraction LLM devrait etre un job async et utiliser l'api batch pour reduire les couts.
    Le coût sans batch est non negligable (~$0.001/profil × 50k = $50)

**Scoring LLM**
Le score reste limite aux top-K (10 candidats par mission), donc le coût par requete ne change pas.

**Add and remove**
    Un candidat doit pouvoir etre ajouter ou supprime
