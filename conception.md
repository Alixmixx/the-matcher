# Conception

## Brainstorming

### Candidat preprocessing
    How to extract the data?
        - regex?
            pas possible, data n'est pas structure
            regex uniquement pour delimiter les profiles

        - LLM?
            llm extract parait meilleur -> bruit et langues
            attention mauvaise extraction (date, certis)

        - preprocessing?
            semi-structured CV pour chaque profil
            pas besoin de strict pour semantic search -> verbose

            profile summary?


### Embedding et index
    - embed profil entier?
        simple, risque dilution -> peut etre suffisant ici
    
    - embed section?
        definir poids sections, complexe

    - profile + summary -> with semi-structured should be enough


    Return les 5 meilleurs apres filtre


### Filtering
    - avant retrieval?
        impossible de creer le filtered_out

    -> Filter after retrival
        top-N, then filter
        we cannot make sure k valid are in the n retrived
        retrieve top 10 then filter out
            simple solution for now


    - run seach on filter + not filter
        requires 2 search

### Score + LLM reason
    LLM scoring pour le match + reason

    - llm rerank on the output
        llm match score + justification for accepted and not


# Pipeline
    1. Preprocessing: extraction LLM -> structured outputs
        candidats + missions
    2. Embedding: embedding candidats resume
    3. Search: cosine search sur la mission
    4. Filter: filtre sur les certs, dates et location
        filtered_out
    4. Scoring + reason: llm rerank -> score + explication
        ranked_candidates + filtered_out

## Architecture

### Preprocessing
    LLM extraction par candidat
        Candidat:
            id int
            name str
            location str
            resume str
            raw_resume str
            certs List[str]
            note str
            available_from date

        Mission:
            id int
            title str
            location str
            start_date date
            duration_months int
            urgency str
            description str
            sector str
            summary str

### Embedding
    text-embedding-3-small -> cheap and good enough for the task

    small dataset so in memory search, but pick a vector db for scale potential
        FAISS -> open source and local

### Filtering
    Filtre sur les categories suivantes:
        - dispo: available_from > start_date
        - location: exact match 
        - cert: exact match
        - note: extra note info

### Scoring
    cosine sur tout les candidats -> return top 10


### LLM uses
    - Extraction:
        Petit model -> gpt-nano 
            pas cher et bon pour structured output
            openai sdk simple for structured output

    - Rerank + reason:
        petit/moyen model -> Haiku pour commencer
            return score + reason


### Evalutation
    - common errors: R486 != R489
    - evaluation visuel top 5 + justifications
    - goldset avec llm-as-judge
    
### Limites
    utilisation de la ville seulement pout la localisation
    certs avec llm et seulement match exact
