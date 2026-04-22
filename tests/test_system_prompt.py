import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from system_prompt import SYSTEM_PROMPT

INTERVENTION_TYPES = [
    "MVP",
    "Évolution produit",
    "Innovation",
    "Boost équipes",
    "FinOPS",
    "Audit",
    "IA maîtrisée",
]

REQUIRED_KEYS = [
    '"diagnostic"',
    '"intervention"',
    '"questions"',
    '"message_consultant"',
]


class TestSystemPromptContent:
    def test_prompt_not_empty(self):
        assert len(SYSTEM_PROMPT.strip()) > 500

    def test_all_intervention_types_mentioned(self):
        for intervention in INTERVENTION_TYPES:
            assert intervention in SYSTEM_PROMPT, f"Intervention manquante : {intervention}"

    def test_json_format_keys_specified(self):
        for key in REQUIRED_KEYS:
            assert key in SYSTEM_PROMPT, f"Clé JSON manquante dans le prompt : {key}"

    def test_json_only_instruction_present(self):
        prompt_lower = SYSTEM_PROMPT.lower()
        assert "uniquement en json" in prompt_lower or "uniquement un json" in prompt_lower

    def test_matters_identity_present(self):
        assert "Matters" in SYSTEM_PROMPT
        assert "studio produit" in SYSTEM_PROMPT.lower() or "Studio Produit" in SYSTEM_PROMPT

    def test_signal_detection_fields(self):
        assert "stade_produit" in SYSTEM_PROMPT
        assert "maturite_tech" in SYSTEM_PROMPT
        assert "signaux_importants" in SYSTEM_PROMPT
