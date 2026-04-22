# PRD — Assistant AVV Matters

---

## 1. Idea

Un assistant conversationnel d'avant-vente pour consultants Matters. L'utilisateur colle ses notes brutes d'un entretien client → l'assistant génère un diagnostic rapide, une ébauche d'intervention recommandée, et des questions de cadrage à poser pour continuer à creuser. L'échange est itératif : les réponses du client alimentent l'assistant qui affine en temps réel.

---

## 2. Goal

**Permettre à un consultant Matters de structurer une proposition d'intervention en cours d'entretien client**, sans perdre le fil de la conversation et sans repartir de zéro à chaque brief.

- Réduire le temps de cadrage post-entretien
- Améliorer la qualité des questions posées au client pendant le meeting
- Produire une ébauche d'intervention exploitable immédiatement après l'appel

---

## 3. Strategic Alignment

**Goal 🎯**: AI Feature Validation — démontrer la valeur d'un outil AI interne dans un contexte avant-vente

**OKR cible**:
- 🚩 Activation : l'assistant produit un diagnostic utile à partir de notes brutes en < 30 secondes
- 📈 Adoption : utilisé sur le case de recrutement live (1 session de validation)
- ⏳ Benefits : structuration AVV perçue comme plus claire et plus rapide vs sans assistant

**Plateformes**: Web (desktop)
**Feature area**: Outillage consultant / Avant-vente
**Team**: Solo (Dorian) — *Assumption : pas d'autres contributeurs pour le prototype*

---

## 4. ICE Score

```
ICE : 4 × 0.6 / 3 = 0.8

- Impact (I) : 4 (S) — usage individuel AVV, gain sur structuration et cadrage en entretien
- Confidence (C) : 0.6
  - [x] #1 Self-conviction (+0.1)
  - [ ] #2 Trends marché (+0.1)
  - [x] #4 Estimations faisabilité (+0.4)
  - [ ] #3 Feedback client anecdotique (+0.4)
  - [ ] #5 Market research / surveys (+1.0)
  - [ ] #6 Customer preference data (+1.0)
  - [ ] #7 Interviews validation (+2.5)
  - [ ] #8 User studies prototype (+2.5–3.0)
  - [ ] #9 MVP launch + metrics (+3.0+)
- Effort (E) : 3 — frontend léger + LLM call, 1-2 jours solo
```

---

## 5. Steps — Expériences de validation (GIST)

1. **Prototype fonctionnel** — builder l'interface deux colonnes avec un LLM branché
2. **Test sur case réel** — utiliser sur le case de recrutement Matters (session live)
3. **Évaluation qualitative** — est-ce que le diagnostic et les questions générées sont pertinents vs ce qu'un consultant expérimenté aurait produit ?

---

## 6. Prototype Scope

### Interface — Deux colonnes (desktop)

**Colonne gauche — Zone de travail**
- Grande zone de texte libre pour saisir les notes brutes
- Bouton "Analyser" pour déclencher le premier diagnostic
- Zone de chat en dessous pour la boucle conversationnelle (questions / réponses)

**Colonne droite — Panel persistant (mis à jour à chaque tour)**
- `Diagnostic` : type de client, stade produit, enjeux détectés, maturité tech
- `Intervention recommandée` : type de mission Matters (MVP, Audit, Discovery, etc.), durée estimée, profils suggérés
- `Questions à creuser` : liste ordonnée de questions à poser au client pour affiner

### User flows critiques

**Flow 1 — Analyse initiale**
1. Utilisateur colle ses notes dans la zone gauche
2. Clique "Analyser"
3. Le panel droit se peuple : Diagnostic + Intervention recommandée + 3-5 questions prioritaires
4. L'utilisateur pose les questions au client, revient avec les réponses

**Flow 2 — Boucle d'affinage**
1. Utilisateur tape dans le chat (ex: "le client a dit qu'il a déjà une équipe tech de 5 personnes")
2. L'assistant met à jour le panel droit en tenant compte de cette info
3. Le diagnostic et les questions s'affinent

**Flow 3 — Relance à froid**
1. Utilisateur arrive avec un nouveau brief sans notes
2. L'assistant lui pose des questions de cadrage structurées pour construire le contexte progressivement

### Logique fonctionnelle attendue dans l'interface

**Système prompt** — l'assistant doit :
- Connaître les 7 types d'intervention Matters (MVP, Évolution produit, Innovation, Support équipes, FinOPS, Audit, IA pragmatique)
- Détecter : taille client, secteur, stade produit, maturité tech, urgence, budget signaux
- Recommander le bon type d'intervention avec une justification en 1-2 lignes
- Générer des questions de cadrage inspirées des pratiques Discovery / GIST
- Rester dans le registre "studio produit & tech", pas conseil générique

**Règles de mise à jour du panel droit :**
- Toute nouvelle info dans le chat → recalcul partiel ou complet du panel
- Les questions déjà posées disparaissent ou sont marquées "répondu"
- L'intervention recommandée peut évoluer (ex: passe de "Audit" à "MVP" si le client est plus avancé que prévu)

### Données mockées

- Pas de base de données — tout en mémoire de session
- Les types d'intervention Matters sont hard-codés dans le système prompt
- Exemple de notes mockées pour le demo : *"Client B2B SaaS, 50 salariés, produit existant avec des problèmes de rétention, pas d'équipe design, CTO technique, budget non défini, veulent aller vite"*

---

## 7. Success Criteria (prototype)

| Critère | Seuil |
|--------|-------|
| Diagnostic généré en < 30s après collage des notes | ✅ |
| Type d'intervention Matters correctement identifié sur le cas mock | ✅ |
| 3+ questions de cadrage pertinentes générées (non génériques) | ✅ |
| Panel droit mis à jour après une info ajoutée en chat | ✅ |
| Utilisable sans formation sur le case de recrutement | ✅ |

---

## 8. Notes pour Claude Code

**Stack recommandée**
- Frontend : Streamlit (Python)
- LLM : Claude API (claude-sonnet-4-6)
- State : st.session_state, pas de DB
- Deploy : local (python -m streamlit run app.py)
- Auth : aucune — clé API via .env

**Système prompt — éléments clés à inclure**
```
Tu es un assistant avant-vente pour Matters, studio produit & tech.
- 50+ experts, 18 ans d'expérience, 200+ produits lancés
- Positionnement : "On transforme vos idées en produits utiles et bien pensés"
- Clients : scaleups, grands groupes, startups
- Approche : vision globale — pas uniquement tech, ni produit, mais vision métier

=== EXPERTISES MATTERS ===

Discovery : recherche utilisateurs, études d'opportunité, tests sur prototypes, pilotage par les données
Stratégie : modèle d'affaires, expérience utilisateurs/clients, go-to-market, croissance
IA : prototypage IA, architecture de solutions, stratégie IA et mise en place opérationnelle
Product Design : design systems, UX/UI, design produit complet
Développement : full-stack, mobile, no-code, back-offices, refontes/migrations
Delivery : méthodes agiles, roadmap produit, pilotage projet, recette & tests

=== TYPES D'INTERVENTION ===

1. MVP — Du prototype au Minimum Viable Product
   Méthodologie en 5 étapes :
   - Compréhension marché & utilisateurs (5-10j) : interviews, analyse marché, exploration comportements
   - Définition modèle business (5-7j) : revenus, pricing, modèle durable
   - Priorisation fonctionnalités (5-10j) : analyse valeur/effort, périmètre MVP, wireflows
   - Prototypage & tests (10-12j/itération) : prototypes interactifs, UI kit, synthèse feedback
   - Développement MVP (1-6 mois) : produit fonctionnel, archi propre et maintenable
   Signaux d'éligibilité : idée à valider, pas encore de produit, besoin d'aller vite sur le marché
   Profils : PM senior, Product Designer, Tech Lead, Full-Stack Dev, Product Builder (no-code)

2. Évolution produit — Optimisation & renforcement
   "On identifie ce qui marche, ce qui freine, ce qui manque. On optimise l'expérience, renforce la base technique, optimise ce qui crée de la valeur et automatise."
   Signaux d'éligibilité : produit existant, problèmes de rétention/adoption, dette technique, besoin d'optimisation UX
   Profils : PM, Product Designer, Tech Lead, Full-Stack Dev

3. Innovation — Accélération d'initiatives
   Méthodologie en 5 étapes :
   - Explorer & identifier opportunités : ateliers idéation, exploration utilisateurs, market research
   - Clarifier objectifs (3-5j) : objectifs business, utilisateur, produit
   - Cadrer & prioriser (5-10j) : roadmaps, évaluation valeur/effort
   - Exécuter produit (4-12 semaines) : design, prototype, dev, tests
   - Soutenir labs d'innovation : coaching continu, montée en compétences
   Signaux d'éligibilité : initiatives stratégiques à concrétiser, ambitions sans exécution, grands groupes innovants
   Clients types : Société Générale, RATP, Somfy, La Fabrique

4. Boost équipes Produit & Tech
   "Parce que les vrais enjeux commencent après le MVP"
   Méthodologie en 5 étapes :
   - Clarifier objectifs & roadmap (4-7j d'ateliers d'alignement)
   - Structurer organisation & process (audit + ateliers d'amélioration)
   - Renforcer delivery produit & tech (intégration continue dans les cycles)
   - Coacher profils clés (mentoring PM, tech leads, designers)
   - Amélioration produit continue (cycles discovery & delivery + suivi KPIs)
   Modèles d'engagement : squads de renforcement, coaching profils clés, interim CPO/CTO
   Signaux d'éligibilité : équipe existante qui scale, post-MVP, problèmes de delivery, besoin de structure
   Clients types : Decathlon, RATP, Société Générale, YouSign

5. FinOPS — Pilotage et optimisation cloud
   "Vision complète de l'infrastructure, pilotage coûts et risques en temps réel"
   Signaux d'éligibilité : coûts cloud non maîtrisés, croissance infra rapide, besoin de visibilité

6. Audit Tech/UX et due-diligence
   Durée : 1-2 semaines
   Livrables : cartographie des risques, actions prioritaires, rapport clair et actionnable (roadmap post-investissement)
   Approche : "pragmatique et deal-oriented" — pas un rapport statique mais une feuille de route
   Périmètre : stack technique, expérience utilisateur, évaluation de l'équipe, delivery
   Clients : fonds d'investissement, équipes M&A
   Signaux d'éligibilité : due diligence pré-investissement, acquisition, évaluation risques

7. IA maîtrisée et pragmatique — Du diagnostic au déploiement
   Méthodologie en 4 étapes :
   - Diagnostic IA (1-2 semaines) : évaluation opportunités et état des lieux
   - Priorisation fonctionnalités (2-3 semaines) : identification des cas d'usage IA à fort impact
   - Implémentation (1-2 sprints) : build & déploiement de la feature IA
   - Scaling : optimisation production et économie du modèle
   Livrables : cartographie des opportunités IA priorisées, prototypes fonctionnels intégrés, solutions production + dashboards d'adoption
   Signaux d'éligibilité : veut intégrer l'IA dans son produit, diagnostic IA nécessaire, pas d'équipe IA interne
   Stack IA : Gemini, Lovable, TypeScript, Next.js

=== ÉQUIPES TYPES ===
- Product Manager : chef d'orchestre, aligne business/utilisateurs/tech, sensibilité entrepreneuriale
- Product Designer : UX de bout en bout, du low-fi au design system
- Tech Lead : garant architecture, code, mentor, arbitrage technique
- Full-Stack Developer : TypeScript, Next.js, Node, Postgres, React, Flutter
- Product Builder : no-code (Retool, Airtable, Zapier, Supabase, Webflow), solutions autonomes de A à Z

=== TON RÔLE ===
À partir des notes d'entretien fournies :
1. Produire un diagnostic structuré (type client, stade produit, enjeux, maturité tech)
2. Recommander le type d'intervention Matters le plus pertinent avec justification courte
3. Générer 3-5 questions de cadrage prioritaires à poser au client pour affiner

Sois concis, structuré, orienté business. Pas de prose inutile.
Adopte le registre de Matters : pragmatique, vision métier, pas que tech.
```

**Composants UI prioritaires**
1. `NotesInput` — textarea + bouton Analyser
2. `ChatThread` — messages user/assistant
3. `DiagnosticPanel` — 3 sections : Diagnostic / Intervention recommandée / Questions
4. `QuestionItem` — question + état (à poser / posée / répondue)

**Ordre de build suggéré**
1. Layout deux colonnes statique
2. Branchement LLM + système prompt
3. Panel droit dynamique (parsing de la réponse structurée)
4. Boucle chat d'affinage
5. Polish UI pour le demo

**Format de réponse LLM attendu (JSON structuré)**
```json
{
  "diagnostic": {
    "type_client": "...",
    "stade_produit": "...",
    "enjeux": ["...", "..."],
    "maturite_tech": "..."
  },
  "intervention": {
    "type": "...",
    "justification": "...",
    "duree_estimee": "...",
    "profils_suggeres": ["..."]
  },
  "questions": [
    { "id": 1, "question": "...", "objectif": "..." }
  ]
}
```
