# Assistant AVV — Matters

**Live : [matters-avv-case.streamlit.app](https://matters-avv-case.streamlit.app)**

Assistant avant-vente conversationnel pour consultants Matters. Colle des notes brutes d'entretien client et obtiens en temps réel : diagnostic client, recommandation d'intervention, questions de cadrage.

## Ce que ça fait

- **Diagnostic client** : type, secteur, stade produit, maturité tech, enjeux, signaux clés
- **Intervention recommandée** : type de mission Matters (MVP, Audit, IA, etc.), durée estimée, équipe, étapes
- **Questions de cadrage** : liste priorisée à poser au client, avec toggle de statut (à poser / posée / répondue)
- **Boucle conversationnelle** : affine le diagnostic au fil des réponses du client

## Stack

- [Streamlit](https://streamlit.io) — UI
- [Claude API](https://anthropic.com) (claude-sonnet-4-6) — LLM
- Python 3.10+

## Lancer en local

```bash
# 1. Cloner le repo
git clone https://github.com/DorianErkens/matters-avv-assistant
cd matters-avv-assistant

# 2. Créer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate  # Windows : venv\Scripts\activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer la clé API
cp .env.example .env
# Éditer .env et ajouter : ANTHROPIC_API_KEY=sk-ant-...

# 5. Lancer
streamlit run app.py
```

L'app sera disponible sur `http://localhost:8501`.

## Tests

```bash
pytest tests/ -v
```

## Deploy Streamlit Cloud

1. Forker / connecter ce repo sur [share.streamlit.io](https://share.streamlit.io)
2. Dans les settings de l'app → **Secrets** → ajouter :
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-..."
   ```
3. Deploy

## Structure

```
├── app.py              # UI Streamlit + logique
├── system_prompt.py    # Connaissance Matters (7 interventions, méthodologie)
├── tests/              # Tests unitaires (pytest)
├── prd/                # PRD du projet
└── requirements.txt
```
