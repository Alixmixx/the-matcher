# Conception the Matcher

## Preprocessing

Les 70 profils candidats sont du texte libre non structure
structures differentes
certifications en texte
profils en allemand
Regex separe les blocs par avec `===`, puis chaque bloc est envoye a un LLM (`gpt-nano`, structured output)
qui extrait un profil structure avec : `id`, `name`, `location`, `available_from`, `certs[]`, `note`, et`text_content`
un resume du profil candidat utitise pour la recherche semantique
Le LLM gere le bruit et normalise les profils

## Embedding

`text-embedding-3-small` (OpenAI, 1536 dimensions)
Choix guide par le rapport cost/quality sur un volume faible (70 candidats + 10 missions)
Le text_content est court, traduit en francais, donc un modele small est suffisant (prototype)
L'index FAISS `IndexFlatIP` avec `normalize_L2` donne une similarite cosinus par produit scalaire
suffisant pour 70 vectors

## LLM dans le pipeline

**1. Extraction** (`gpt-nano`)
transforme le texte libre en schema structure pour candidats et missions.
Gere les differentes langues et les fautes

**2. Scoring** (`gpt-mini`)
pour chaque paire (mission, candidat) retenue par FAISS, le LLM recoit:
la mission + le profil brut du candidat.
Il retourne:
un score 0–1, une justification en francais pour le consultant, des preuves issus du CV, et un flag `hard_excluded` si une exclusion s'applique

Le LLM de scoring voit le profil entier, pas seulement le `text_content`, ce qui lui permet de verifier les dates d'expiration et de detecter les faux positifs (R486 != R489).

## Evaluation

aucun candidat legalement exclu ne doit apparaître dans `ranked_candidates`.

les justifications contiennent des elements de preuve concrets issus du CV

les scores sont coherents avec le fit apparent.

**evaluation pratique** :

Revue visuelle des top 5 + justifications sur les 10 missions
Verification des profils pieges : C068 (R486 seulement) exclu des missions R489, candidats avec CACES expire dans `filtered_out`

## Limites connues

**Filtres durs delegues au LLM** : l'exclusion pour certification expiree repose sur le LLM, pas sur une regle deterministe. Risque faible mais non nul.
    Pour ameliorer, ajouter un filtre deterministe, mais les certifications doivent etre standardises

**Localisation** : comparaison de ville uniquement, pas de geocoding ni de rayon kilometrique. Les candidats peuvent etre mal traites.
    Ajouter geocoding

- **Plafond FAISS a 10** : si la majorite des 10 candidats recuperes sont filtres, le resultat final peut contenir moins de 5 candidats. Un top-20 peut etre plus robuste.
    Autre approche plus elegante est de filtrer avant, mais on ignore les profils proches
    Sinon utitliser une incrementation:
        search 10, 20, 40, 80, 160 until max_search
    Une autre idee est de faire 2 search, avec et sans filtre, mais ca double la computation

- **Exact date** : La date est verifie exactement, par example pour M004, le candidat C004 est filtre pour un jour de difference pour une mission non urgente

- **Language** : Le language du candidat n'est pas toujours pris en compte, il devrait apparaitre dans un field
