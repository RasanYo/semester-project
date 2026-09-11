# .ralph

Configuration et état d'exécution de la [boucle de dev autonome Ralph](https://github.com/frankbria/ralph-claude-code).

## Why?

Ralph fait tourner Claude Code en boucle avec coupe-circuits, limitation de
débit et détection de sortie à double condition. Ce dossier tient les
instructions qu'il suit, le plan qu'il déroule, et l'état qu'il traîne d'une
itération à l'autre.

## Architecture

- `PROMPT.md` — instructions maîtresses relues à chaque boucle (objectifs,
  tests, format de rapport, scénarios de sortie)
- `AGENT.md` — les faits build/test/run de ce repo ; `ralph-import` ne l'écrase
  jamais
- `fix_plan.md` — la checklist priorisée que Ralph déroule
- `specs/` — les spécifications, écrites à la main ou générées par `ralph-import`
- `logs/` — un log par boucle, plus les métriques
- `docs/generated/` — documentation auto-générée
- `.ralphrc` (racine du repo) — débit, seuils de coupe-circuit, outils
  autorisés, session

Les fichiers d'état (`.call_count`, `.circuit_breaker_state`, `.exit_signals`,
`status.json`, …) sont gitignorés.

## Usage

```bash
ralph-import <fichier-spec.md>   # convertit une spec en PROMPT.md + fix_plan.md + specs/
ralph --monitor                  # lance la boucle dans tmux avec le moniteur
ralph --live                     # lance la boucle en direct, sans tmux
ralph --status                   # où elle en est
ralph --dry-run                  # simule sans appeler l'API
```

Le skill `ship-feature` automatise l'enchaînement : il crée l'issue et la
branche, génère les fichiers ici, lance Ralph, et finit sur une PR.
