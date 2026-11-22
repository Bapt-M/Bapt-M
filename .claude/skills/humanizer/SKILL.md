---
name: humanizer
description: Réécrit un texte pour qu'il sonne écrit par une personne et non par une IA. À utiliser quand l'utilisateur demande d'« humaniser », de rendre un texte « plus naturel », « moins IA », « moins robotique », ou de retirer le style ChatGPT d'un mail, post, message, README ou commit. Fonctionne en français et en anglais (humanize, make it sound human, less AI).
---

# Humanizer

Objectif : garder le fond, changer la voix. Le texte final doit se lire comme si quelqu'un l'avait tapé lui-même, sans trace des tics d'écriture des modèles de langage.

## Démarche

1. **Lire tout le texte** et repérer : le destinataire, le registre (mail pro, message à un ami, post LinkedIn, doc technique), la langue, et les faits à ne pas perdre.
2. **Repérer les marqueurs IA** listés plus bas.
3. **Réécrire**, sans ajouter d'information ni en retirer une qui compte. Ne rien inventer (chiffres, anecdotes, opinions).
4. **Relire à voix haute mentalement** : si une phrase ne serait jamais dite par une vraie personne dans ce contexte, la refaire.
5. **Rendre** le texte réécrit seul, prêt à copier. Ajouter au plus une ou deux lignes sur ce qui a changé si c'est utile, ou si l'utilisateur le demande.

Si le registre ou le destinataire n'est pas clair et que ça change vraiment le résultat, poser une seule question. Sinon, choisir le registre le plus probable et le dire en une ligne.

## Marqueurs IA à éliminer

### Vocabulaire
- FR : « crucial », « essentiel », « incontournable », « véritable », « en somme », « il est important de noter que », « n'hésitez pas à », « plonger dans », « au cœur de », « un monde où », « dans un paysage en constante évolution », « fort de », « levier », « synergie », « favoriser », « optimiser » utilisés à vide.
- EN : delve, crucial, pivotal, tapestry, landscape, realm, robust, seamless, leverage, foster, navigate, elevate, unlock, testament to, "it's worth noting", "in today's fast-paced world", "I hope this email finds you well".
- Adverbes d'intensité en série : vraiment, extrêmement, incroyablement, profondément.

### Structures
- Les triplets systématiques (« rapide, fiable et intuitif »). Garder deux éléments, ou un seul, ou quatre : varier.
- « Ce n'est pas seulement X, c'est Y » / "It's not just X, it's Y".
- Questions rhétoriques suivies de leur réponse (« Le résultat ? Un gain de temps. »).
- Phrases d'ouverture qui reformulent la demande, et conclusions qui résument ce qui vient d'être dit (« En conclusion… », « Au final… »).
- Paragraphes tous de la même longueur, phrases toutes de la même longueur. Mélanger phrases courtes et longues.
- Listes à puces et titres là où une personne écrirait juste deux paragraphes. Un mail ou un message n'a presque jamais de titres en gras.

### Ponctuation et forme
- Tirets cadratins (—) à répétition : les remplacer par une virgule, un point, des parenthèses ou deux-points.
- Gras semé dans le texte, emojis décoratifs en début de puce (✅ 🚀 💡).
- Majuscules à chaque mot dans les titres en anglais quand ce n'est pas le style attendu.
- En français, respecter la typographie habituelle de l'auteur (espaces avant « : ; ? ! », guillemets) plutôt qu'en imposer une.

### Ton
- Enthousiasme générique, flatterie, formules de politesse empilées.
- Prudence excessive (« il pourrait être envisageable de potentiellement… »). Affirmer quand on sait.
- Neutralité sans point de vue quand le texte est censé en avoir un.
- Fin par une offre d'aide (« N'hésitez pas si vous avez des questions ! ») sauf si c'est vraiment l'usage dans ce contexte.

## Ce qui rend un texte humain

- Des mots simples et précis plutôt que des mots impressionnants.
- Du concret : un exemple, un nom, un chiffre déjà présent dans le texte source, mis en avant.
- Un rythme irrégulier. Une phrase courte de temps en temps. Ça marche.
- Une voix cohérente avec la personne : tutoiement ou vouvoiement selon l'original, contractions en anglais (it's, don't), « on » plutôt que « nous » dans un registre familier français.
- Accepter un peu d'imperfection naturelle selon le registre (phrase sans verbe, début par « Et » ou « Mais »), sans introduire de fautes.

## Garde-fous

- Ne pas changer le sens, les faits, les chiffres, les noms, les liens ni le code.
- Ne pas allonger le texte : le résultat est en général plus court que l'original.
- Garder la langue d'origine, sauf demande contraire.
- Si l'utilisateur fournit un exemple de son propre style, s'aligner dessus en priorité sur les règles ci-dessus.
- Le but est un texte meilleur et plus naturel, pas de tromper un détecteur : ne pas ajouter de fautes volontaires ni de caractères invisibles.

## Exemple

Avant :
> Dans un monde en constante évolution, il est crucial de rester connecté. C'est pourquoi notre application n'est pas seulement un outil — c'est un véritable compagnon du quotidien, rapide, fiable et intuitif. N'hésitez pas à la tester !

Après :
> Notre appli sert à une chose : ne plus rater les messages importants. Elle est rapide et on la prend en main en deux minutes. Essayez-la.
