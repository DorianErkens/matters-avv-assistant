# Code Review — Matters AVV Assistant

**Date :** 2026-04-22
**Fichiers analysés :** `app.py`, `system_prompt.py`
**Contexte :** Assistant avant-vente conversationnel Streamlit + Claude API
**Profondeur :** Standard (lecture complète + analyse contextuelle)

---

## Résumé exécutif

Le code est propre, lisible et fonctionnel pour un MVP interne. L'architecture est cohérente (séparation state / appel API / rendu), le prompt est bien structuré, et le parsing JSON dispose déjà d'un mécanisme de fallback. Les problèmes identifiés sont principalement des risques de crash sur des edge cases non couverts, des failles XSS potentielles liées à `unsafe_allow_html`, et plusieurs points de robustesse qui peuvent se déclencher en production.

**Bilan :** 4 HIGH · 5 MEDIUM · 4 LOW

---

## HIGH — Risques de crash ou de sécurité

### H-01 · XSS via `unsafe_allow_html` sur du contenu LLM non sanitisé

**Fichier :** `app.py`, lignes 396–398, 415–417, 428–429, 433–434, 444–447, 456–459, 465–467, 483–489

**Problème :**
Le contenu retourné par Claude (chaînes extraites du JSON) est injecté directement dans du HTML via `st.markdown(..., unsafe_allow_html=True)` sans aucun échappement. Si Claude retourne une valeur contenant du HTML (ex. `<script>alert(1)</script>` ou un lien `<a href="javascript:...">`), il sera rendu tel quel dans le navigateur.

Exemples de variables non échappées injectées dans HTML :
- `diag["secteur"]`, `diag["enjeux"]`, `diag["signaux_importants"]`
- `interv["type"]`, `interv["justification"]`, `interv["etapes_cles"]`
- `q["question"]`, `q["objectif"]`
- `st.session_state.last_message`

**Fix :**
```python
import html

# Wrapper à appliquer sur toute valeur issue du LLM avant injection HTML
def h(value: str) -> str:
    return html.escape(str(value))

# Exemple d'utilisation
st.markdown(
    f'<div class="card-label">{h(label)}</div><div class="card-value">{h(val)}</div>',
    unsafe_allow_html=True,
)
```

---

### H-02 · `response.content[0]` sans vérification — crash si réponse vide

**Fichier :** `app.py`, ligne 245

**Code actuel :**
```python
return response.content[0].text
```

**Problème :**
Si l'API Anthropic retourne une réponse avec `content` vide (ex. lors d'un refus de contenu, d'un timeout interne, ou d'une `stop_reason` inattendue), l'accès à l'index `[0]` lève une `IndexError` non interceptée qui crash l'application avec une traceback brute côté utilisateur.

**Fix :**
```python
if not response.content:
    raise ValueError("Réponse Claude vide (aucun bloc content retourné)")
return response.content[0].text
```

---

### H-03 · `parse_response` : extraction JSON trop permissive (`rfind("}")`)

**Fichier :** `app.py`, lignes 271–274

**Code actuel :**
```python
start = raw.find("{")
end = raw.rfind("}") + 1
if start != -1 and end > start:
    return json.loads(raw[start:end])
```

**Problème :**
`rfind("}")` retourne la position du dernier `}` dans la chaîne. Si Claude retourne du texte après le JSON (ex. une note, une explication), cette heuristique peut inclure des caractères parasites ou, pire, couper un objet JSON imbriqué de façon incorrecte (ex. si le texte contient `}` dans une chaîne). Le `json.loads` lèvera alors une `JSONDecodeError` non gérée à cet endroit.

**Fix :**
Gérer l'exception localement et produire un message d'erreur actionnable :
```python
start = raw.find("{")
end = raw.rfind("}") + 1
if start != -1 and end > start:
    try:
        return json.loads(raw[start:end])
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON extrait invalide ({e}): {raw[start:end][:200]}")
```

---

### H-04 · `toggle_question` : `KeyError` si `statut` absent ou valeur inattendue

**Fichier :** `app.py`, lignes 321–324

**Code actuel :**
```python
def toggle_question(idx: int):
    cycle = {"a_poser": "posee", "posee": "repondue", "repondue": "a_poser"}
    q = st.session_state.questions[idx]
    st.session_state.questions[idx]["statut"] = cycle[q["statut"]]
```

**Problème :**
Si `q["statut"]` contient une valeur absente du dictionnaire `cycle` (ce qui peut arriver si le JSON retourné par Claude contient un champ `statut` inattendu), `cycle[q["statut"]]` lève une `KeyError`. L'index `idx` lui-même n'est pas validé non plus.

**Fix :**
```python
def toggle_question(idx: int):
    cycle = {"a_poser": "posee", "posee": "repondue", "repondue": "a_poser"}
    if idx < 0 or idx >= len(st.session_state.questions):
        return
    q = st.session_state.questions[idx]
    current = q.get("statut", "a_poser")
    st.session_state.questions[idx]["statut"] = cycle.get(current, "a_poser")
```

---

## MEDIUM — Bugs potentiels et robustesse

### M-01 · Le client Anthropic est recréé à chaque appel LLM

**Fichier :** `app.py`, lignes 233–238

**Problème :**
`call_claude()` instancie un nouveau `anthropic.Anthropic(api_key=...)` et relit `os.getenv()` à chaque appel. En plus d'être légèrement inefficace, cela signifie que la connexion HTTP n'est jamais réutilisée (pas de keep-alive entre les appels successifs dans un même cycle conversation).

**Fix :**
Initialiser le client une seule fois au démarrage ou en cache Streamlit :
```python
@st.cache_resource
def get_anthropic_client() -> anthropic.Anthropic:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError("ANTHROPIC_API_KEY manquante")
    return anthropic.Anthropic(api_key=api_key)
```

Et dans `call_claude` :
```python
def call_claude(messages: list) -> str:
    client = get_anthropic_client()
    response = client.messages.create(...)
    return response.content[0].text
```

---

### M-02 · `send_chat` : les statuts de questions sont perdus si une question est supprimée par Claude

**Fichier :** `app.py`, lignes 314–318

**Code actuel :**
```python
old_statuses = {q["id"]: q["statut"] for q in st.session_state.questions}
st.session_state.questions = [
    {**q, "statut": old_statuses.get(q["id"], "a_poser")}
    for q in data.get("questions", [])
]
```

**Problème :**
Si une question disparaît de la liste retournée par Claude (logique fonctionnelle valide — Claude peut affiner la liste), son statut (`posee` / `repondue`) est simplement abandonné sans aucune trace. Inversement, si Claude retourne une question avec un `id` déjà existant mais une formulation différente, le statut est conservé silencieusement sur une question qui a changé de sens.

**Fix (pragmatique) :**
Ajouter un mécanisme de merge explicite basé sur `id` avec conservation prioritaire des questions déjà interagies :
```python
old_by_id = {q["id"]: q for q in st.session_state.questions}
merged = []
for q in data.get("questions", []):
    old = old_by_id.get(q["id"])
    statut = old["statut"] if old else "a_poser"
    merged.append({**q, "statut": statut})
st.session_state.questions = merged
```

---

### M-03 · `analyze_notes` : aucune gestion d'erreur API — crash silencieux

**Fichier :** `app.py`, lignes 279–291

**Problème :**
`analyze_notes()` n'a aucun bloc `try/except`. Si `call_claude()` lève une exception réseau (`anthropic.APIConnectionError`, `anthropic.RateLimitError`, timeout...) ou si `parse_response()` échoue, l'exception remonte jusqu'à Streamlit qui affiche une traceback brute. L'état `st.session_state.analyzed` reste à `False` mais `history` peut rester dans un état intermédiaire.

**Fix :**
```python
def analyze_notes(notes: str):
    try:
        messages = [{"role": "user", "content": f"Notes d'entretien :\n\n{notes}"}]
        raw = call_claude(messages)
        data = parse_response(raw)
    except Exception as e:
        st.error(f"Erreur lors de l'analyse : {e}")
        return

    st.session_state.history = messages + [{"role": "assistant", "content": raw}]
    st.session_state.diagnostic = data.get("diagnostic", {})
    st.session_state.intervention = data.get("intervention", {})
    st.session_state.last_message = data.get("message_consultant", "")
    st.session_state.questions = [
        {**q, "statut": "a_poser"} for q in data.get("questions", [])
    ]
    st.session_state.analyzed = True
```

---

### M-04 · Le chat history affiche le reminder injecté dans le message utilisateur

**Fichier :** `app.py`, lignes 296–297 et 365–379

**Problème :**
Dans `send_chat()`, le message utilisateur est enrichi d'un suffix technique :
```python
reminder = "\n\n[Rappel : réponds uniquement en JSON valide, même format que précédemment.]"
new_msg = {"role": "user", "content": user_message + reminder}
```

Ce message enrichi est ensuite stocké dans `st.session_state.history` et affiché tel quel dans l'historique de chat (lignes 365–379). L'utilisateur voit donc son message avec le suffix technique en clair, ce qui nuit à l'expérience.

**Fix :**
Séparer le message affiché du message envoyé à Claude :
```python
display_msg = {"role": "user", "content": user_message}  # pour l'affichage
api_msg = {"role": "user", "content": user_message + reminder}  # pour l'API

# Stocker display_msg dans history, utiliser api_msg uniquement pour l'appel
messages = st.session_state.history + [api_msg]
raw = call_claude(messages)
# ...
st.session_state.history = st.session_state.history + [display_msg, {"role": "assistant", "content": raw}]
```

---

### M-05 · `questions` dans le JSON : `id` non validé, peut être une string

**Fichier :** `app.py`, lignes 288–290 et 314

**Problème :**
Le système prompt définit `"id": 1` (entier), mais Claude peut parfois retourner `"id": "1"` (string) ou des ids non séquentiels. La clé `q['id']` est utilisée dans le dictionnaire `old_statuses` et comme partie de clé Streamlit (`key=f"q_{i}_{q['id']}"`). Si l'id change de type entre deux appels, la préservation des statuts est silencieusement cassée.

**Fix :**
Normaliser l'id à la réception :
```python
st.session_state.questions = [
    {**q, "id": str(q.get("id", i)), "statut": "a_poser"}
    for i, q in enumerate(data.get("questions", []))
]
```

---

## LOW — Qualité de code et maintenabilité

### L-01 · `st.stop()` dans `call_claude` interrompt le rendu de façon agressive

**Fichier :** `app.py`, ligne 236

**Problème :**
`st.stop()` stoppe immédiatement l'exécution du script Streamlit. Appelé depuis une fonction utilitaire profondément imbriquée, ce comportement crée un couplage fort entre la logique métier et le framework de rendu. Difficile à tester et à déboguer.

**Fix :**
Lever une exception et laisser la couche d'affichage gérer l'erreur :
```python
def call_claude(messages: list) -> str:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError("ANTHROPIC_API_KEY manquante dans le fichier .env")
    # ...
```

---

### L-02 · CSS inline dans un long bloc — maintenance difficile

**Fichier :** `app.py`, lignes 17–215

**Problème :**
Le CSS (198 lignes) est embarqué directement dans le code Python via `st.markdown()`. Cela rend la maintenance difficile : pas de coloration syntaxique, pas d'autocomplétion, mélange responsabilités logique / présentation.

**Fix :**
Extraire le CSS dans un fichier séparé et le charger dynamiquement :
```python
# utils.py ou app.py
def load_css(path: str):
    with open(path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("styles.css")
```

---

### L-03 · `init_state` à chaque re-render — pas de problème fonctionnel, mais pattern fragile

**Fichier :** `app.py`, lignes 218–229

**Observation :**
Le pattern `if key not in st.session_state` est correct et idiomatique Streamlit. Cependant, la clé `"last_message"` est initialisée à `""` (string vide) alors qu'elle est parfois testée avec `if st.session_state.last_message:` (vérité Python). Ce pattern est cohérent mais mérite d'être documenté : une string vide est falsy, donc le comportement est correct — mais fragile si la valeur par défaut change.

**Fix (mineur) :**
Ajouter un commentaire explicatif, ou remplacer par `None` et adapter le test :
```python
"last_message": None,
# ...
if st.session_state.last_message:  # None ou "" → pas affiché
```

---

### L-04 · Le system prompt mentionne une stack IA spécifique (`Gemini, TypeScript, Next.js`)

**Fichier :** `system_prompt.py`, ligne 77

**Observation :**
La ligne `Stack IA : Gemini, TypeScript, Next.js` dans la section "IA maîtrisée" semble être un résidu ou une information partiellement correcte. L'outil lui-même utilise Claude (Anthropic), pas Gemini. Si cette stack est présentée au client via l'output de l'assistant, elle peut créer de la confusion ou une promesse incorrecte.

**Fix :**
Vérifier si Matters utilise effectivement Gemini pour ses propres projets IA clients (auquel cas c'est correct) ou si c'est une erreur de copy-paste. Si c'est une erreur, supprimer ou corriger la ligne.

---

## Récapitulatif

| ID   | Sévérité | Catégorie          | Description courte                                           |
|------|----------|--------------------|--------------------------------------------------------------|
| H-01 | HIGH     | Sécurité (XSS)     | Contenu LLM injecté en HTML sans échappement                |
| H-02 | HIGH     | Bug / Crash        | `response.content[0]` sans garde sur liste vide              |
| H-03 | HIGH     | Bug / Robustesse   | `rfind("}")` dans parse_response non protégé par try/except  |
| H-04 | HIGH     | Bug / Crash        | `KeyError` dans `toggle_question` si statut invalide         |
| M-01 | MEDIUM   | Performance        | Client Anthropic recréé à chaque appel                       |
| M-02 | MEDIUM   | Bug / UX           | Statuts de questions perdus si Claude supprime une question   |
| M-03 | MEDIUM   | Robustesse         | `analyze_notes` sans try/except — crash brut sur erreur API  |
| M-04 | MEDIUM   | UX / Bug           | Reminder technique affiché dans l'historique chat utilisateur |
| M-05 | MEDIUM   | Robustesse         | `id` de question non normalisé (int vs string)               |
| L-01 | LOW      | Qualité            | `st.stop()` dans une fonction utilitaire — couplage fort      |
| L-02 | LOW      | Maintenabilité     | CSS embarqué dans Python (198 lignes)                        |
| L-03 | LOW      | Qualité            | `last_message` initialisé à `""` — pattern fragile           |
| L-04 | LOW      | Contenu            | Stack IA "Gemini" dans system_prompt à vérifier              |

---

*Revue réalisée le 2026-04-22 — Reviewer : Claude (gsd-code-reviewer) — Depth : standard*
