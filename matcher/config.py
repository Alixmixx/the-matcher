from pathlib import Path

ROOT = Path(__file__).parent.parent
DATA = ROOT / "data"
OUTPUTS = ROOT / "outputs"

# Input data
CANDIDATES_FILE = DATA / "candidats.txt"
MISSIONS_FILE = DATA / "missions.json"

# Output files
CANDIDATES_OUT = OUTPUTS / "candidates.json"
MISSIONS_OUT = OUTPUTS / "missions.json"
FAISS_INDEX = OUTPUTS / "candidates.faiss"
FAISS_META = OUTPUTS / "candidates_meta.json"
RESULTS_OUT = OUTPUTS / "results.json"
FINAL_OUT = OUTPUTS / "final.json"

# Models
EXTRACT_MODEL = "gpt-5.4-nano"
SCORE_MODEL = "gpt-5.4-mini"
EMBED_MODEL = "text-embedding-3-small"

# Tuning
EMBED_BATCH_SIZE = 100
TOP_K = 10  # FAISS candidates per mission
TOP_N = 5   # final ranked candidates
