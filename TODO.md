# TODO

`[ ]` à faire · `[.]` en cours · `[x]` fait → descend dans la liste du bas.

Une tâche qui tourne sans ligne ici est invisible — pour toi pendant qu'elle
tourne, pour la session suivante une fois qu'elle s'arrête. Avant de toucher
quoi que ce soit, cherche la tâche ici ; si elle n'y est pas, ajoute-la, une
ligne, la même voix que ses voisines, et passe-la `[.]` avant la première
édition. Terminée : `[x]`, datée, déplacée dans `## Fait`. Abandonnée : la ligne
revient à `[ ]` — un `[.]` mort est pire que pas de ligne.

La barre : ce qui change ce que le système *est* ou *sait faire*. Une question,
une synchro de config, une coquille, un correctif d'un seul fichier — pas de
ligne, on le fait.

- [.] Construire le répertoire d'événements d'amorçage — ~20 événements suisses
      tirés de Swissvotes et Curia Vista par une règle mécanique, stratifiés sur
      polarisation × Röstigraben, entités de référence validées à la main. Le banc
      de test du liage d'entités, et la comparaison à agenda contrôlé entre médias.
- [ ] Trouver et obtenir le corpus — quelles archives, quelle licence, quelle fenêtre
- [ ] Récupérer les références de validation (Smartvote, votes nominatifs, MARPOR/CHES)
- [ ] Poser le squelette du repo — arborescence `src/`, `scripts/`, `data/`
- [ ] Représenter les résultats en graphe — le biparti média–acteur qui porte la
      mesure, et sa projection média–média qui porte le résultat. L'arête entre
      deux médias dit co-positionnement, jamais influence : undirected, et la
      version résiduelle après VARX à côté de la brute.

## Fait

*On coupe à 3 mois. Plus ancien, ça vit dans le `DEVLOG.md`.*

- [x] 2026-09-11 — L'environnement Python et le manifeste de dépendances
      Python 3.12 dans `.venv`, `pyproject.toml` + `uv.lock` versionnés, le
      paquet `mediapos` sous `src/` installé en editable. Reconstruit depuis
      zéro avec `uv sync --frozen` pour vérifier que le lock suffit.

- [x] 2026-09-11 — Le sujet est cadré
      positionnement politique des médias suisses par la *visibilité* des acteurs,
      pas par le contenu. Le proposal vit dans `docs/proposal.md`, les règles qui
      en découlent dans `CLAUDE.md` — dont la portée honnête : on caractérise le
      co-positionnement, on ne prouve aucune contagion.
- [x] 2026-09-11 — L'outillage porté depuis `ai-trading-algo`
      `TODO.md` et `DEVLOG.md` comme planche et trace, le `.claude/` générique
      (commandes, sous-agents, skills `ship-feature`, règles Python, hook
      DEVLOG après merge), et Ralph activé. Ce qui était propre au trading —
      skills `strategy-*`, `data-sourcing`, `audit-bias` — n'a pas suivi.
