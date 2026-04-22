# CLAUDE.md — Assistant AVV Matters

## Contexte projet

Assistant avant-vente conversationnel pour Matters (studio produit & tech). Permet à un consultant de structurer une proposition d'intervention en cours d'entretien client, à partir de notes brutes.

## Stack

- **Frontend** : Streamlit (Python)
- **LLM** : Claude API claude-sonnet-4-6 via SDK `anthropic`
- **State** : `st.session_state` uniquement, pas de DB
- **Deploy** : Streamlit Cloud

## Lancer l'app

```bash
source venv/bin/activate
streamlit run app.py
```

## Lancer les tests

```bash
pytest tests/ -v
```

## Architecture

- `app.py` — UI + logique : `parse_response()`, `analyze_notes()`, `send_chat()`, `toggle_question()`
- `system_prompt.py` — connaissance Matters complète (ne pas modifier sans mettre à jour les tests)
- `tests/test_parse_response.py` — tests unitaires du parser JSON
- `tests/test_system_prompt.py` — tests de contenu du system prompt

## Règles importantes

- Le LLM doit toujours répondre en JSON structuré (voir format dans `system_prompt.py`)
- `parse_response()` gère plusieurs formats : JSON brut, code fences, JSON embarqué dans du texte
- `send_chat()` ajoute un rappel de format JSON à chaque message pour éviter les dérives
- La clé API est dans `.env` (jamais commitée) — variable `ANTHROPIC_API_KEY`
- Sur Streamlit Cloud : clé dans Settings → Secrets (format TOML)

## Session state keys

| Key | Type | Description |
|-----|------|-------------|
| `history` | list | Historique complet des messages Claude |
| `diagnostic` | dict | Diagnostic client courant |
| `intervention` | dict | Intervention recommandée courante |
| `questions` | list | Questions avec statut (a_poser / posee / repondue) |
| `last_message` | str | Message consultant du dernier appel |
| `analyzed` | bool | Si l'analyse initiale a été faite |

## Types d'intervention Matters (référence)

1. MVP — Du prototype au Minimum Viable Product
2. Évolution produit — Optimisation & renforcement
3. Innovation — Accélération d'initiatives
4. Boost équipes Produit & Tech
5. FinOPS — Pilotage et optimisation cloud
6. Audit Tech/UX et due-diligence
7. IA maîtrisée et pragmatique
