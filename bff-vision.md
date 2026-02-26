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

1. `/front-clarify {page}` → conversation pour éclaircir le besoin de la page, en s'imprégnant du vocabulaire métier
2. Produire le fichier `specs/flows/{page}.md` qui contient :
   - Le **contexte métier** (qui sont les utilisateurs, leur vocabulaire)
   - Un **diagramme Mermaid** avec portes logiques (AND/OR/conditions) montrant tous les scénarios
   - Les **données affichées** par état

### Phase 2 — Maquettes (UX/UI)

Objectif : produire des maquettes visuelles comme on ferait dans Figma, directement en code.

1. `/front-maquette {page}` → crée un mockup par état visuel
2. **`frontend-design` systématique** — design polished et adapté au métier, UX fluide et addictive
3. **Valeurs en dur** — pas de fetch, pas de mock, pas de store. Du HTML/CSS avec des données statiques réalistes (vocabulaire métier).
4. **Design system** : factoriser composants partagés (`/front-refactor`).

### Phase 3 — Contrat API

1. `/front-contract {page}` → analyse les maquettes et sépare les responsabilités :
   - **Back (domaine + adapteur BFF)** : règles métier, calculs, ET exposition formatée (groupement, tri, jointures, agrégations)
   - **Front (UX)** : uniquement la logique d'interaction (navigation, état local, transitions)
2. Écrire le contrat dans `specs/api/{page}-view.yml` **au format OpenAPI** avec contexte métier pour le back
3. Le contrat inclut le vocabulaire métier et les formules de calcul

### Phase 4 — Backend (hors scope front)

Le back implémente les endpoints selon les specs de la phase 3.
Flow : `/back-clarify` → `/back-specify` → tests → `/back-implement` → code + seeders → `/back-refactor`

**Validation automatique** : `make check-contract` vérifie que le OpenAPI généré par FastAPI est un surensemble du contrat phase 3. Le contrat définit le minimum garanti, le code peut exposer plus.

### Phase 5 — Dynamisation

1. `/front-dynamize {page}` → brancher le front sur les vrais endpoints
2. Supprimer valeurs en dur et logique métier que le back gère maintenant
3. Garder les composants UI intacts, ajouter loading/error states

## Nomenclature fichiers

```
specs/
  flows/
    {page}.md                   ← flux utilisateur + diagramme Mermaid (phase 1)
  api/
    {page}-view.yml             ← contrat API BFF OpenAPI (phase 3)

maquettes/
  {page}/
    {page}--{etat}.vue          ← maquette visuelle par état (phase 2)
  components/
    {Component}.vue             ← composants partagés (design system)
```

## Pages à migrer

| Page | Complexité front actuelle | Priorité |
|------|--------------------------|----------|
| FourneePage | Très élevée (7+ fetches, jointures, calculs prix) | 1 |
| DashboardPage | Élevée (context state, projections multiples) | 2 |
| ComptaPage | Moyenne (bug CA lié au même problème) | 3 |

## Principes

- **Le front ne fait pas de jointures** — la donnée arrive prête
- **Le front ne calcule pas de métier back** — prix, totaux, marges = backend
- **Le front gère son propre métier UX** — navigation, état local, interactions (pas de dépendance back pour ça)
- **Le back expose la donnée formatée** — groupement, tri, agrégation = responsabilité de l'adapteur BFF, piloté par le contrat
- **Design system cohérent** — composants factorisés, réutilisables entre pages (`/front-refactor`)
- **Contrat API = source de vérité** — le front et le back s'accordent sur la spec, validé par `make check-contract`
- **Maquettes = Figma en code** — chaque état est un fichier autonome, visuel, statique, design-first
