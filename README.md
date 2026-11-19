BibliIIT – Système de gestion de bibliothèque

BibliIIT est une application console développée en Python permettant d’assurer la gestion des activités d’une bibliothèque universitaire. Elle facilite la recherche de livres, la gestion des emprunts et des retours, ainsi que le suivi des retards.

Les données sont stockées dans une base de données SQLite afin de garantir leur conservation entre les différentes exécutions de l’application.

Fonctionnalités principales

* Recherche de livres : recherche par code, titre ou auteur, sans distinction entre majuscules, minuscules et accents.
* Gestion des emprunts : enregistrement d’un emprunt pour une durée de 14 jours.
* Gestion des retours : enregistrement du retour d’un livre et mise à jour automatique de sa disponibilité.
* Suivi des retards : identification des livres non retournés à la date prévue et calcul du nombre de jours de retard.
* Emprunts en cours : consultation des livres actuellement empruntés.
* Retours effectués : consultation des emprunts ayant fait l’objet d’un retour.
* Catalogue : affichage des 50 livres enregistrés dans la bibliothèque.
* Disponibilité : consultation des livres actuellement disponibles.
* Historique : consultation de l’ensemble des opérations d’emprunt et de retour.

Règles de gestion

L’application applique les règles suivantes :

1. Un livre ne peut faire l’objet que d’un seul emprunt actif à la fois.
2. Un étudiant ne peut pas avoir plus de trois emprunts actifs simultanément.
3. Le matricule de l’étudiant et le code du livre sont obligatoires.
4. Le livre demandé doit obligatoirement exister dans le catalogue.
5. Seul l’étudiant ayant effectué un emprunt peut enregistrer le retour du livre correspondant.
6. Un emprunt déjà clôturé ne peut pas faire l’objet d’un second retour.

Architecture du projet

Le projet est organisé en plusieurs modules afin de séparer les responsabilités et de faciliter la maintenance du code.

bibliIIT/
│
├── regles.py              # Règles métier : durée, limites et retards
├── modeles.py             # Modèles de données : Livre et Emprunt
├── depot_sqlite.py        # Gestion des accès à la base SQLite
├── service.py             # Logique métier : ServiceBibliotheque
├── console.py             # Interface utilisateur en ligne de commande
├── actualiser_bd.py       # Création, mise à jour et initialisation de la base
├── bibliotheque.db        # Base de données SQLite
├── README.md              # Documentation du projet
│
└── tests/
    ├── base.py            # Configuration de la base temporaire de test
    ├── test_recherche.py  # Tests de la recherche
    ├── test_emprunt.py    # Tests des emprunts
    ├── test_retour.py     # Tests des retours
    ├── test_retards.py    # Tests du suivi des retards
    └── test_regles.py     # Tests des règles métier

Organisation des dépendances

Les modules sont organisés selon le principe de séparation des responsabilités :

* console.py : gère les interactions avec l’utilisateur.
* service.py : applique les règles métier et coordonne les opérations.
* depot_sqlite.py : assure les échanges avec la base de données.
* regles.py : centralise les règles de gestion indépendantes de la base de données.
* modeles.py : définit les structures de données utilisées dans l’application.

Installation

Prérequis

* Python 3.10 ou une version supérieure.
* SQLite (inclus dans les installations standards de Python).
* Un terminal ou un environnement de développement compatible avec Python.

Aucune dépendance externe n’est nécessaire.

Mise en place

1. Copier ou télécharger le dossier du projet.
2. Ouvrir un terminal.
3. Se positionner dans le répertoire bibliIIT.

Exécution de l’application

Pour démarrer l’application, exécuter la commande suivante :

python console.py

Au premier lancement, l’application initialise automatiquement la base de données SQLite et y ajoute les 50 livres de démonstration, si la base n’existe pas encore.

Menu principal

L’application propose le menu interactif suivant :

========== BibliIIT ==========
1. Rechercher un livre
2. Emprunter un livre
3. Retourner un livre
4. Retards
5. Emprunts en cours
6. Retours effectués
7. Afficher le catalogue
8. Afficher les livres disponibles
9. Consulter l'historique
0. Quitter
==============================

Chaque option permet d’accéder à une fonctionnalité spécifique.

Les erreurs de saisie et les situations particulières sont prises en charge : choix invalide, matricule vide, livre inexistant, livre déjà emprunté ou tentative de retour non autorisée.

Ces erreurs sont signalées à l’utilisateur sans provoquer l’arrêt de l’application.

Tests automatisés

Le projet dispose d’une suite de tests automatisés basée sur le module unittest de Python.

Pour exécuter l’ensemble des tests, utiliser la commande suivante :

python -m unittest discover -s tests -v

Couverture des tests

Les tests vérifient notamment :

* Recherche : résultats existants et inexistants, recherche par code, gestion des accents, caractères spéciaux et termes vides.
* Emprunts : emprunt valide, livre déjà emprunté, limite de trois emprunts, livre inexistant et champs obligatoires.
* Retours : retour valide, livre non emprunté, mauvais matricule et tentative de double retour.
* Retards : identification des emprunts en retard et calcul du nombre de jours de retard.
* Règles métier : vérification des durées, des limites et des conditions de gestion.

Les tests utilisent une base de données temporaire indépendante. Ils ne modifient donc pas le contenu de bibliotheque.db.

Structure de la base de données

La base de données SQLite repose sur deux tables principales.

Table LIVRES

Champ	Description
id	Identifiant unique du livre
code	Code unique du livre
titre	Titre du livre
auteur	Auteur du livre
annee	Année de publication

Table EMPRUNTS

Champ	Description
id	Identifiant unique de l’emprunt
matricule	Matricule de l’étudiant
code_livre	Code du livre emprunté
date_emprunt	Date à laquelle le livre a été emprunté
date_retour_prevue	Date limite de retour
date_retour_effective	Date réelle du retour
retourne	Indique si le livre a été rendu

Contraintes et intégrité des données

* Le champ code de la table LIVRES possède une contrainte d’unicité.
* Le champ code_livre de la table EMPRUNTS référence le champ code de la table LIVRES.
* Un index unique partiel garantit qu’un même livre ne peut pas avoir plusieurs emprunts actifs simultanément.



Technologies utilisées

* Python 3.10+ : développement de l’application et implémentation de la logique métier.
* SQLite : stockage et gestion des données.
* unittest : automatisation des tests.
* Dataclasses : structuration des modèles de données.

⸻

BibliIIT – Gestion de bibliothèque universitaire

Application développée en Python dans le cadre d’un projet informatique.