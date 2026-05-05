import json
from pathlib import Path

import pytest

FINAL_JSON = Path(__file__).parent.parent / "outputs" / "final.json"

ALL_MISSIONS = [f"M{i:03d}" for i in range(1, 11)]


@pytest.fixture(scope="module")
def final():
    with open(FINAL_JSON, encoding="utf-8") as f:
        data = json.load(f)
    return {r["mission_id"]: r for r in data}


def filtered_ids(result):
    return {c["candidate_id"] for c in result["filtered_out"]}


def ranked_ids(result):
    return {c["candidate_id"] for c in result["ranked_candidates"]}


@pytest.mark.parametrize("mid", ALL_MISSIONS)
def test_all_missions_present(final, mid):
    assert mid in final


@pytest.mark.parametrize("mid", ALL_MISSIONS)
def test_at_most_five_ranked(final, mid):
    assert len(final[mid]["ranked_candidates"]) <= 5


@pytest.mark.parametrize("mid", ALL_MISSIONS)
def test_scores_in_range(final, mid):
    for c in final[mid]["ranked_candidates"]:
        assert 0.0 <= c["score"] <= 1.0, f"{c['candidate_id']}: {c['score']}"


@pytest.mark.parametrize("mid", ALL_MISSIONS)
def test_no_duplicate_ranked(final, mid):
    ids = [c["candidate_id"] for c in final[mid]["ranked_candidates"]]
    assert len(ids) == len(set(ids))


@pytest.mark.parametrize("mid", ALL_MISSIONS)
def test_ranked_and_filtered_disjoint(final, mid):
    overlap = ranked_ids(final[mid]) & filtered_ids(final[mid])
    assert not overlap, f"{overlap} in both ranked and filtered for {mid}"


@pytest.mark.parametrize("mid", ALL_MISSIONS)
def test_justification_not_empty(final, mid):
    for c in final[mid]["ranked_candidates"]:
        assert c.get(
            "justification", ""
        ).strip(), f"{c['candidate_id']} has no justification"


# M001 — Opérateur cariste (CACES R489 required, Mulhouse)


def test_m001_expired_r489_filtered(final):
    # C002: R489 expired Dec 2025
    assert "C002" in filtered_ids(final["M001"])


def test_m001_r486_not_r489_filtered(final):
    # C068: holds R486 (nacelle), not R489 — easy to confuse
    assert "C068" in filtered_ids(final["M001"])


def test_m001_no_unqualified_ranked(final):
    assert not ({"C002", "C068"} & ranked_ids(final["M001"]))


# M007 — Technicien maintenance, habilitation BR exigée (Colmar)


def test_m007_expired_habilitation_filtered(final):
    # C013: B1V expired Nov 2025
    assert "C013" in filtered_ids(final["M007"])


def test_m007_b0_only_filtered(final):
    # C012: B0 = consignation only, not enough for BR work
    assert "C012" in filtered_ids(final["M007"])


def test_m007_no_br_filtered(final):
    assert "C014" in filtered_ids(final["M007"])


def test_m007_hv_only_filtered(final):
    # C050: H0V is haute tension — irrelevant for BT interventions
    assert "C050" in filtered_ids(final["M007"])


# M010 — Cariste urgent (CACES R489, démarrage immédiat)


def test_m010_expired_r489_filtered(final):
    assert "C002" in filtered_ids(final["M010"])


# M008 — Gestionnaire de paie (keyword trap: paie ≠ stock)


def test_m008_stock_profile_not_ranked(final):
    # C056 is logistics/stock — only assert if the FAISS top-10 even surfaced them
    if "C056" in filtered_ids(final["M008"]) or "C056" in ranked_ids(final["M008"]):
        assert "C056" in filtered_ids(final["M008"])
