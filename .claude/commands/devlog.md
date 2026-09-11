---
description: Écrire une entrée DEVLOG.md pour un lot de travail terminé
---

Tu maintiens `DEVLOG.md` à la racine de ce repo : la trace chronologique du
travail effectué, la plus récente en premier.

Ce repo est un projet de semestre (ETHZ). Une entrée DEVLOG parle donc de ce que
le système *sait faire* et de ce qui a été *établi* — une capacité nouvelle, une
donnée acquise, une décision de conception, un résultat et sa preuve — pas de
features produit.

## Quand écrire une entrée

Un lot de travail fusionné dans `develop` qui change ce que le système *est* ou
*peut faire* : une couche remaniée, une table ajoutée, une stratégie, une
capacité nouvelle.

**Pas** une entrée pour : une synchro de config, une coquille, un renommage, un
correctif d'un seul fichier sans conséquence. En cas de doute, demande-toi si
quelqu'un qui revient dans six semaines aurait besoin de lire ça. Sinon, dis-le
et n'écris rien.

## Comment procéder

1. Rassemble le contexte toi-même d'abord :
   `git log --oneline develop..HEAD` ou `git log --oneline -15`, et
   `git diff --stat` sur la plage concernée.
2. **Si tu viens de faire le travail, tu connais déjà les réponses — rédige
   directement.** Ne pose des questions que sur ce que le code et les messages
   de commit ne peuvent pas te dire : l'intention derrière une décision, un
   compromis accepté, ce qui a surpris. Une question à la fois.
3. Rédige l'entrée **en français**, dans ce format, et insère-la **en haut** de
   `DEVLOG.md` juste sous l'en-tête (crée le fichier avec un titre `# DEVLOG`
   s'il n'existe pas) :

```markdown
## [AAAA-MM-JJ] — [une ligne : ce que ça change, pas ce que ça touche]

**Ce qu'on voulait**

[le problème, en clair. Ce qu'on ne pouvait pas faire avant.]

**Comment on a procédé**

[les étapes, dans l'ordre où elles ont eu lieu — pas la liste des fichiers.]

**Le résultat**

[ce qui est vrai maintenant et ne l'était pas. Inclure la preuve quand il y en
a une : « les chiffres n'ont pas bougé, vérifié par X ».]

**Décisions à retenir**

[les choix qu'on ne veut pas rejouer dans six semaines, avec leur raison.
Omettre si aucun.]

**Différé, volontairement**

[ce qu'on a choisi de ne pas faire, et pourquoi. Omettre si rien.]

**Commits :** `abc1234`, `def5678`
```

4. Montre l'entrée et demande confirmation **avant** d'écrire dans le fichier.
5. Commite `DEVLOG.md` seul, avec un message qui dit de quel lot il parle.

## Le ton

Court et simple, comme le reste du repo. Une entrée se lit en une minute.
Explique le *pourquoi*, jamais le *comment* ligne à ligne — le code et les
messages de commit portent déjà ça. Si une décision a un piège, nomme-le : une
entrée qui ne dit que du bien est une entrée inutile.
