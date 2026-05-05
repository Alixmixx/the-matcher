EXTRACT_CANDIDATE = (
    "Extract a structured candidate profile from the resume. "
    "The candidate ID is in the header line 'CV #NNN — Name'. "
    "Format it as C001, C002, etc. "
    "For available_immediately: set to true if the CV uses phrases like "
    "'immédiatement', 'de suite', 'disponible maintenant', 'sofort verfügbar', or similar. "
    "For available_from: if available_immediately is true, set to null. "
    "Otherwise use the earliest stated availability date, or null if unknown. "
    "For text_content, produce a clean normalized French version "
    "suitable for semantic embedding."
)

EXTRACT_MISSION = (
    "Extract a structured mission from the JSON record. "
    "For text_content, write a single fluent French paragraph "
    "summarising the role, requirements, location and urgency "
    "optimised for semantic similarity search."
)

SCORE_CANDIDATE = (
    "Tu es un expert en recrutement intérimaire. "
    "Évalue la compatibilité entre une mission et un candidat. "
    "Analyse compétences, certifications (vérifie les dates d'expiration), "
    "disponibilité, localisation et expérience sectorielle. "
    "Pour la disponibilité : si available_immediately=true, le candidat est disponible maintenant — "
    "ne l'exclure jamais pour indisponibilité. "
    "Si available_immediately=false et available_from est renseigné, exclure uniquement si "
    "available_from > start_date ET la mission est urgente. "
    "Si le candidat doit être légalement exclu (certification absente ou expirée, "
    "indisponible, ou mobilité insuffisante), marque hard_excluded=true avec la raison précise. "
    "Sinon, donne un score entre 0.00 et 1.00, et une justification claire en français pour le consultant "
    "avec les éléments de preuve issus du profil."
)
