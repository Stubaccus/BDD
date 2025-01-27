# SAE Base de Données (2024)

## Membre du groupe

- BRUN Dylan
- CASTRE Théo
- BIOUT Julien
- HALBOT Baptiste
- DUPORGE Gregory

## Description

Site web contenant toutes les informations sur les Jeux Olympiques et Paralympiques de 2024.

### Langages utilisés:

- HTML
- CSS
- JavaScript
- Python
- SQL (et SQLite)


## Fiche technique Base de Donnée JO 2024

Une BD déjà remplie existe dans le répertoire, elle se nomme
NPC_BD.sqlite. Si vous décidez d’exécuter les instructions
suivantes, une nouvelle BD se créera dans ce même répertoire
sous le nom : jo2024.sqlite.

### I] Création et Remplissage de la base de donnée

Note: nous utilisons Python 3.11, il n'est pas sur que d'autres versions marchent

Pour exécuter les scripts, plusieurs dépendances sont nécessaires,
afin de faciliter leur installation nous utilisons le gestionnaire d'environnement virtuel poetry.
Pour installer ces dépendances vous proceder ainsi (dans le dossier "principal" du projet, celui de l'archive):
- pip install poetry
- poetry install
- poetry env use OU Sélectionner l'interpréteur de l'environnement virtuel dans VS Code

Alternativement vous pouvez essayer d'installer les dépendances présentent dans pyproject.toml manuellements
Et n'hésitez pas à nous contacter en cas de problèmes (dans le pire des cas, la base de donnée préfournie, peut être utilisé)

La création de la base de donnée se réalise grâce au programme
nommée “build.py” dans le dossier db, il a pour but:
- de créer la base donnée (fichier jo2024.sqlite)
- d'exécuter le script sql créant les tables (groupe_NPC.sql)
- d'exécuter les scripts sql remplissant statiquement les tables
Ce script exécute également les scripts de scrapping:
- athlete_data.py: Scrap Olympedia, recupere les données sur les athltetes permet de remplir les tables Sportif, Participe et Nationalite
- result.py: Scrap L'Equipe, recupere les données sur les resultats permet de remplir les tables Resultat et Appartient

IMPORTANT: le script build.py est à exécuter depuis le dossier "principal" du projet (db)

### II] Visionnages de la base de donnée

Nous avons créé un serveur python afin de mettre en place notre page internet permettant la visualisation de notre base de donnée. Le manque de temps ne nous a pas permit de 
faire quelque chose de très esthétique, mais la grande majorité des informations sont présentes et le site est pour la grande majorité opérationnel.