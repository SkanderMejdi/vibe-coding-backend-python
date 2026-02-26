# BFF — Backend For Frontend

> Libérer le front de la logique métier, structurer la donnée côté backend.

## Constat

Le front fait aujourd'hui beaucoup de travail que le back devrait faire :
- **Jointures manuelles** : pain → commande → user, pain → article → recette → forme
- **Calculs métier dupliqués** : prix du pain (max tag.prix_au_kilo × poids_cuit), total par acheteur, groupement par pâte/recette
- **Projections complexes** : `painsByBuyerFinalize`, `painsByPateGroup`, `allPainsWithPate`, `fourUsage`
- **Chargement en cascade** : fetchFournee → fetchCommandes → fetchPains → fetchPates → fetchArticles → fetchRecettes → fetchFormes...

Le back expose des routes CRUD par entité. Le front recompose tout.

## Vision

Des **endpoints orientés page/vue** (BFF pattern) :
- Le back projette la donnée structurée pour chaque vue
- Le front consomme et affiche, sans jointures ni calculs métier
- Un fichier de spec API par page, co-conçu front ↔ back

## Flow de travail — 5 phases

### Phase 1 — Clarification (flux utilisateur)

Objectif : comprendre et documenter le besoin avant de dessiner quoi que ce soit.

1. `/clarify` → conversation pour éclaircir le besoin de la page
2. Produire le fichier `maquettes/{page}/{page}--flux.md` qui décrit :
   - Les **parcours utilisateur** (étape par étape)
   - Les **états possibles** et transitions entre eux
   - Les **règles d'accès** (admin, artisan, public, etc.)
   - Les **actions disponibles** par état
   - Les **cas limites** (vide, erreur, chargement)

### Phase 2 — Maquettes (UX/UI)

Objectif : produire des maquettes visuelles comme on ferait dans Figma, directement en code.

1. Créer les fichiers maquettes selon la nomenclature :
   ```
   maquettes/{page}/{page}--{etat}.vue
   ```
2. **Valeurs en dur** — pas de fetch, pas de mock, pas de store. Du HTML/CSS avec des données statiques représentant l'état.
3. **Design system** : factoriser composants partagés au fur et à mesure.
4. Itérer avec feedback screenshots + skill frontend-design.

### Phase 3 — Contrat API

1. Analyser les maquettes : quelles données chaque état nécessite
2. Prendre en compte le **domaine métier** et les **ressources API existantes** pour factoriser intelligemment
3. Écrire le contrat dans `specs/api/{page}-view.yml` **au format OpenAPI** (sous-ensemble : paths + response schemas)
4. Si nécessaire, implémenter des **mocks** pour tester les transitions d'état
5. Parfois les valeurs en dur de la phase 2 suffisent

### Phase 4 — Backend (hors scope front)

Le back implémente les endpoints selon les specs de la phase 3.
Flow classique : `/specify` → tests → `/implement` → code → `/refactor`

**Validation automatique** : `make check-contract` vérifie que le OpenAPI généré par FastAPI est un surensemble du contrat phase 3. Le contrat définit le minimum garanti, le code peut exposer plus.

### Phase 5 — Dynamisation

1. Brancher le front sur les vrais endpoints
2. Supprimer valeurs en dur / mocks / logique métier dupliquée
3. Garder les composants UI intacts

## Nomenclature fichiers

```
maquettes/
  {page}/
    {page}--flux.md             ← flux utilisateur + règles (phase 1)
    {page}--{etat}.vue          ← maquette visuelle par état (phase 2)

specs/
  api/
    {page}-view.yml             ← contrat API BFF (phase 3)
```

## Pages à migrer

| Page | Complexité front actuelle | Priorité |
|------|--------------------------|----------|
| FourneePage | Très élevée (7+ fetches, jointures, calculs prix) | 1 |
| DashboardPage | Élevée (context state, projections multiples) | 2 |
| ComptaPage | Moyenne (bug CA lié au même problème) | 3 |

## Principes

- **Le front ne fait pas de jointures** — la donnée arrive prête
- **Le front ne calcule pas de métier** — prix, totaux, marges = backend
- **Design system cohérent** — composants factorisés, réutilisables entre pages
- **Contrat API = source de vérité** — le front et le back s'accordent sur la spec
- **Maquettes = Figma en code** — chaque état est un fichier autonome, visuel, statique
