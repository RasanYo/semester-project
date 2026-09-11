# Ralph Agent Configuration

Faits de build/test/run de ce repo. `ralph-import` n'écrase jamais ce fichier —
ce sont `PROMPT.md`, `fix_plan.md` et `specs/` qui portent la feature courante.
Lis `CLAUDE.md` à la racine en premier s'il existe : il possède les règles
d'architecture que ce fichier ne fait que pointer.

## Project Layout

Le repo démarre presque vide. À la racine :

```
README.md      # ce que le projet est
TODO.md        # le tableau : [ ] à faire, [.] en cours, [x] fait
DEVLOG.md      # la trace chronologique, une entrée par lot fusionné
.claude/       # commandes, skills, sous-agents, hooks (voir .claude/README.md)
.ralph/        # ce dossier — instructions, plan, specs, logs
```

Quand une arborescence source apparaît, décris-la ici — un layout périmé coûte
plus cher que pas de layout du tout.

## Build Instructions

Pas d'étape de build pour l'instant. Projet Python : si un venv existe
(`.venv/`), appelle toujours `.venv/bin/python` — le `python3` système n'a pas
les dépendances. Une dépendance manquante s'ajoute avec
`.venv/bin/python -m pip install <pkg>`, et tu le dis dans le rapport.

## Run Instructions

Rien à lancer pour l'instant. À renseigner dès qu'un point d'entrée existe.

## Test Instructions

```bash
.venv/bin/python -m pytest -q     # ou pytest -q si pas de venv
ruff check .
```

Pas encore de suite : si tu écris du code, écris le test qui le prouve, et ne
déclare rien de vert sans avoir montré la sortie.

## Le tableau et la trace

- Avant de toucher quoi que ce soit, cherche la tâche dans `TODO.md`. Absente ?
  ajoute-la — une ligne, la même voix que ses voisines — et passe-la `[.]` avant
  la première édition. Finie : `[x]`, datée, déplacée dans `## Fait`. Abandonnée :
  la ligne revient à `[ ]`.
- Un lot fusionné dans `develop` qui change ce que le système *est* ou *sait
  faire* mérite une entrée `DEVLOG.md` (format dans `.claude/commands/devlog.md`).
  Pas pour une synchro de config, une coquille, un correctif d'un seul fichier.
