# .claude

Configuration Claude Code de ce projet : commandes, skills, sous-agents, règles
et scripts de hook. Claude Code les ramasse tout seul dans n'importe quelle
session ouverte ici.

Le tout est porté depuis `ai-trading-algo` — la part générique seulement. Ce qui
y était propre au trading (les skills `strategy-*`, `data-sourcing`, la commande
`audit-bias`, le sous-agent `strategy-evaluator`) n'a pas suivi.

## Architecture

- `commands/` — commandes slash, invoquées avec `/nom` : `devlog`, `doc`,
  `explore`, `oneshot`, plus les sous-commandes `git/`.
- `agents/` — sous-agents de dev, dépêchés pour du travail ciblé et
  parallélisable (exploration, planification, documentation). Chaque fichier
  épingle son modèle et ses outils dans son frontmatter ; plusieurs tournent sur
  Haiku, l'exploration étant fréquente et bon marché.
- `rules/` — conventions chargées automatiquement selon le chemin
  (`python.md` s'applique à tout `**/*.py`).
- `skills/` — workflows multi-étapes : `ship-feature` (CLI locale),
  `ship-feature-cloud` (onglet Claude Code web), `playwright`.
- `scripts/devlog-reminder.sh` — hook `PostToolUse` : après un merge, rappelle
  d'écrire l'entrée `DEVLOG.md`. Il *rappelle* seulement, il ne bloque rien.
- `settings.json` — réglages partagés (hooks, permissions), committé.
- `settings.local.json` — surcharges locales, non committé.

Le statusline et les sons de notification vivent dans le `settings.json` global
(`~/.claude/settings.json`) — inutile de les redéclarer ici. Le hook
`PreToolUse` pointe vers le validateur de commandes global,
`~/.claude/scripts/command-validator/`, plutôt que d'en dupliquer une copie.

## Quelle variante de ship-feature

| Environnement | Skill | Pourquoi |
|---------------|-------|----------|
| CLI locale (`claude` au terminal) | `/ship-feature` | Prend tout le cycle git : branche, push, PR |
| Onglet Claude Code (web) | `/ship-feature-cloud` | La session a déjà sa branche, pas de PR à créer |

## Usage

```bash
/devlog                       # écrire l'entrée DEVLOG du lot qui vient de tomber
/doc <dossier>                # générer le README d'un dossier
/explore <sujet>              # recherche codebase + docs + web
/oneshot <feature>            # implémentation rapide : explore → code → test
/ship-feature "<feature>"     # issue, branche, Ralph, PR
/git:commit
```
