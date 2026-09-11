# skills

Workflows multi-étapes que Claude Code peut dérouler sur demande. Un dossier par
skill, avec son `SKILL.md` ; les plus longs ajoutent un `steps/`.

## Architecture

- `ship-feature/` — sessions CLI locales : crée l'issue et la branche, génère
  les fichiers Ralph, lance Ralph, finit sur un lien de PR.
- `ship-feature-cloud/` — sessions onglet Claude Code (web) : pareil, sans la
  création de branche ni la PR, la session ayant déjà sa branche. Utiliser le
  bouton « Create PR » de l'UI web à la fin.
- `playwright/` — automatisation navigateur via la CLI Playwright, avec
  persistance de session.

## Quelle variante de ship-feature

| Environnement | Skill | Pourquoi |
|---------------|-------|----------|
| CLI locale (`claude` au terminal) | `/ship-feature` | Prend tout le cycle git : branche, push, PR |
| Onglet Claude Code (web) | `/ship-feature-cloud` | La session a déjà sa branche, pas de PR à créer |

## Usage

```bash
/ship-feature "Ajouter X"
/ship-feature-cloud "Ajouter X"
/playwright open http://localhost:5173
```
