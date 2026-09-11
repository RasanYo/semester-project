# agents — sous-agents de dev Claude Code

Sous-agents dépêchés pour du travail ciblé et parallélisable. À la différence
d'une commande slash (qu'un humain invoque), ceux-ci sont appelés par une
commande ou par la session elle-même, et rendent un résultat plutôt qu'une
transcription.

## Architecture

- `action.md` — exécuteur conditionnel : vérifie une condition avant d'agir.
- `documentation-manager.md` — met à jour les docs quand le code change ;
  donne-lui la liste des fichiers touchés pour qu'il sache où regarder.
- `explore-codebase.md` — cherche motifs, fichiers et implémentations existantes.
- `explore-docs.md` — documentation de librairies via le MCP Context7.
- `planner.md` — produit un plan d'implémentation détaillé. Lecture seule.
- `websearch.md` — recherches web rapides, résumées.

Chaque fichier épingle son modèle et ses outils autorisés dans son frontmatter.

## Usage

Dépêchés comme sous-agents, pas invoqués directement :

```
subagent_type="explore-codebase"   prompt="Trouve tous les appels à X"
subagent_type="planner"            prompt="Plan pour Y"
```
