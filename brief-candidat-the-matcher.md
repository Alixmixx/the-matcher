# Brief candidat — The Matcher

> Ce document est envoyé au candidat **48h avant le Round 2**.
> Fichiers joints : `candidats.txt` + `missions.json`

---

## Contexte

ENSO construit **Tempo X**, un ERP SaaS pour les agences d'intérim. Notre vision 2026 : passer d'un logiciel transactionnel à une plateforme où des agents IA prennent en charge les opérations répétitives, pendant que les consultants se concentrent sur la relation et le jugement.

Le premier use case stratégique : **The Matcher** — un agent qui, à partir d'une demande de mission client, identifie automatiquement les meilleurs candidats disponibles dans le vivier.

Aujourd'hui, un consultant passe en moyenne 45 minutes à chercher manuellement dans le vivier pour chaque nouvelle mission. Il filtre par compétences, vérifie les disponibilités, et s'appuie beaucoup sur sa mémoire des candidats. On veut un système qui fait ce premier travail de façon fiable et explicable.

---

## Ta mission

Construire un prototype de **The Matcher** : un système qui, pour chaque demande de mission, retourne les **5 meilleurs candidats** avec un **score** et une **justification lisible par une consultante**.

La justification est aussi importante que le score. Une consultante qui voit un candidat proposé doit comprendre en 10 secondes pourquoi il est là.

---

## Ce qu'on te fournit

**`candidats.txt`** — 70 profils candidats en texte libre. Les données sont volontairement hétérogènes : certains profils sont structurés, d'autres informels, certains sont en allemand, les certifications sont exprimées de façons différentes selon les candidats, certains champs sont absents. C'est représentatif de la vraie donnée qu'on manipule.

**`missions.json`** — 10 demandes de mission en format semi-structuré, telles qu'elles seraient saisies par une consultante dans l'outil.

Quelques précisions importantes :

- Certaines certifications sont **légalement obligatoires** pour certains postes (CACES pour conduite d'engins, habilitations électriques pour interventions BT). Un candidat sans certification valide **ne peut jamais** être proposé sur ce type de mission, indépendamment de son score sur les autres critères.
- Les profils sont **bruités** : même compétence exprimée différemment ("cariste", "conduite d'engins", "chariots élévateurs"), certifications avec des libellés variables, notes consultants parfois contradictoires avec le CV.
- Certains candidats ont peu ou pas d'historique. Comment tu les traites ?

---

## Livrables attendus

**1. Un prototype fonctionnel** qui tourne sur les 10 missions et retourne les 5 meilleurs candidats pour chacune. La sortie doit être au format JSON structuré suivant :

```json
{
  "mission_id": "M001",
  "ranked_candidates": [
    {
      "candidate_id": "C003",
      "score": 0.87,
      "justification": "Cariste multi-CACES (1B, 3, 5) tous valides, 12 mois d'expérience entrepôt Mulhouse, disponible immédiatement. CACES cat. 5 en bonus pour rangement grande hauteur."
    }
  ],
  "filtered_out": [
    {
      "candidate_id": "C002",
      "reason": "CACES R489 expiré depuis décembre 2025 — certification légalement requise manquante"
    }
  ]
}
```

La section `filtered_out` liste les candidats qui auraient pu matcher sémantiquement mais qui sont exclus par un filtre dur (certification expirée, indisponibilité, etc.). La stack est libre — pas besoin d'UI.

Contraintes techniques à respecter :
- Le scoring doit intégrer une **mesure de similarité sémantique** entre l'expérience du candidat et les exigences de la mission — pas uniquement du matching de mots-clés.
- La **justification doit être générée par LLM**, pas par un template fixe. Elle doit être utile à une consultante qui n'a pas lu le CV.

**2. Un doc de conception (max 1 page)** répondant à :
- Comment tu as prétraité et représenté les données candidats avant de les comparer aux missions ?
- Quel modèle d'embedding as-tu utilisé et pourquoi ?
- Comment le LLM intervient-il dans ton pipeline — à quelle(s) étape(s) et pour quoi faire ?
- Comment tu évaluerais que ton matcher est bon ? C'est quoi ta définition de "ça marche" ?
- Qu'est-ce que ton prototype ne gère pas encore, et pourquoi ?

**3. Une note courte** (pas de code) sur la question suivante : *"Ton prototype tourne sur 70 candidats. Qu'est-ce qui change fondamentalement si le vivier passe à 50 000 profils mis à jour en continu ?"*

---

## Ce qu'on ne juge pas

- La beauté du code — on veut voir la logique, pas le polish
- Que tu traites tous les cas limites — 5 candidats par mission suffit
- Le choix du modèle ou du framework — utilise ce que tu maîtrises

---

## Livraison

Envoie-nous ton repo (GitHub/GitLab, ou archive zip) **24h avant le Round 2**. Le repo doit contenir :
- Le code source
- Le fichier de sortie JSON déjà généré (résultat d'une exécution chez toi)
- Le doc de conception
- La note "at scale"

On ne fera pas tourner ton code nous-mêmes — on lira ta sortie JSON et ton code avant l'entretien. Pendant le Round 2, tu auras ton env ouvert en partage d'écran et on pourra te demander de relancer ou modifier quelque chose en live.

---

## Format du Round 2

60 min avec Alexis (architecte) et David (CTPO). Partage d'écran, ton environnement de dev ouvert.

- **Walk-through** (10 min) — Tu présentes tes choix de conception : pipeline, modèles, compromis. Pas de slides, on veut voir le code et la sortie.
- **Review technique** (35 min) — On rentre dans le détail avec toi : prétraitement des données, choix d'embedding, rôle du LLM dans le pipeline, gestion des filtres durs (certifications, disponibilité). On te demandera probablement d'ouvrir certains fichiers, d'expliquer des décisions, et potentiellement de relancer le système sur un cas précis.
- **Mise en situation** (15 min) — On te soumet un scénario nouveau qui n'était pas dans le dataset. On veut voir comment tu raisonnes en temps réel face à une contrainte inattendue.
