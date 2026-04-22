import json
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import parse_response

VALID_PAYLOAD = {
    "diagnostic": {
        "type_client": "scaleup",
        "secteur": "fintech",
        "stade_produit": "MVP",
        "enjeux": ["rétention", "scalabilité"],
        "maturite_tech": "forte",
        "signaux_importants": ["CTO technique", "pas d'équipe design"]
    },
    "intervention": {
        "type": "Évolution produit",
        "justification": "Produit existant avec friction UX identifiée.",
        "duree_estimee": "3-4 mois",
        "profils_suggeres": ["PM", "Product Designer", "Tech Lead"],
        "etapes_cles": ["Audit UX", "Optimisation onboarding", "Renforcement stack"]
    },
    "questions": [
        {"id": 1, "question": "Quel est votre taux de rétention à J30 ?", "objectif": "Qualifier la gravité du churn"},
        {"id": 2, "question": "Avez-vous déjà fait des tests utilisateurs ?", "objectif": "Évaluer la maturité discovery"}
    ],
    "message_consultant": "Le profil correspond à une mission d'évolution produit. Priorité : qualifier le churn."
}


class TestParseResponseRawJson:
    def test_valid_json_string(self):
        raw = json.dumps(VALID_PAYLOAD)
        result = parse_response(raw)
        assert result["diagnostic"]["type_client"] == "scaleup"
        assert len(result["questions"]) == 2

    def test_json_with_leading_trailing_whitespace(self):
        raw = "   " + json.dumps(VALID_PAYLOAD) + "\n"
        result = parse_response(raw)
        assert result["intervention"]["type"] == "Évolution produit"


class TestParseResponseCodeFences:
    def test_markdown_json_fence(self):
        raw = f"```json\n{json.dumps(VALID_PAYLOAD)}\n```"
        result = parse_response(raw)
        assert result["diagnostic"]["secteur"] == "fintech"

    def test_markdown_plain_fence(self):
        raw = f"```\n{json.dumps(VALID_PAYLOAD)}\n```"
        result = parse_response(raw)
        assert result["message_consultant"] != ""

    def test_fence_with_preamble_text(self):
        raw = f"Voici mon analyse :\n```json\n{json.dumps(VALID_PAYLOAD)}\n```"
        result = parse_response(raw)
        assert result["diagnostic"]["stade_produit"] == "MVP"


class TestParseResponseExtraction:
    def test_json_embedded_in_text(self):
        raw = f"Bien sûr, voici le résultat : {json.dumps(VALID_PAYLOAD)} Bonne chance !"
        result = parse_response(raw)
        assert result["diagnostic"]["type_client"] == "scaleup"


class TestParseResponseErrors:
    def test_empty_string_raises(self):
        with pytest.raises((ValueError, json.JSONDecodeError)):
            parse_response("")

    def test_whitespace_only_raises(self):
        with pytest.raises((ValueError, json.JSONDecodeError)):
            parse_response("   \n  ")

    def test_plain_text_raises(self):
        with pytest.raises((ValueError, json.JSONDecodeError)):
            parse_response("Je ne suis pas du JSON.")

    def test_partial_json_raises(self):
        with pytest.raises((ValueError, json.JSONDecodeError)):
            parse_response('{"diagnostic": {')


class TestParseResponseStructure:
    def test_diagnostic_keys_present(self):
        result = parse_response(json.dumps(VALID_PAYLOAD))
        diag = result["diagnostic"]
        assert "type_client" in diag
        assert "stade_produit" in diag
        assert "enjeux" in diag
        assert isinstance(diag["enjeux"], list)

    def test_intervention_keys_present(self):
        result = parse_response(json.dumps(VALID_PAYLOAD))
        interv = result["intervention"]
        assert "type" in interv
        assert "profils_suggeres" in interv
        assert isinstance(interv["etapes_cles"], list)

    def test_questions_are_list(self):
        result = parse_response(json.dumps(VALID_PAYLOAD))
        assert isinstance(result["questions"], list)
        assert result["questions"][0]["id"] == 1
