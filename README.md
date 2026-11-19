# BibliIIT – Gestion de Bibliothèque

Application console en Python pour gérer une bibliothèque : recherche, emprunts, retours et suivi des retards.
Les données sont enregistrées dans une base SQLite.

## Fonctionnalités

- Recherche par code, titre ou auteur (insensible à la casse et aux accents).
- Emprunt d'un livre pour une durée de 14 jours.
- Retour d'un livre, qui redevient disponible.
- Affichage des livres en retard avec le nombre de jours de retard.
- Consultation des emprunts en cours, des retours effectués, du catalogue (50 livres), des livres disponibles et de l'historique.

### Règles métier

- Un livre ne peut avoir qu'un seul emprunt actif.
- Un étudiant ne peut pas avoir plus de 3 emprunts actifs.
- Le matricule et le code du livre sont obligatoires.
- Le livre doit exister dans le catalogue.
- Seul l'étudiant qui a emprunté un livre peut l'enregistrer comme rendu.

## Structure du projet

```text
bibliIIT/
├── regles.py          Règles métier (durée, limite, retard) – aucune requête SQL
├── modeles.py         Dataclasses Livre et Emprunt
├── depot_sqlite.py    Accès à SQLite (requêtes paramétrées)
├── service.py         Logique métier : ServiceBibliotheque
├── console.py         Menu interactif
├── actualiser_bd.py   Outil optionnel : crée/met à jour la base et liste le catalogue
├── bibliotheque.db    Base de données (créée automatiquement si absente)
├── README.md
└── tests/
    ├── base.py            Base temporaire commune aux tests
    ├── test_recherche.py
    ├── test_emprunt.py
    ├── test_retour.py
    ├── test_retards.py
    └── test_regles.py
```

Dépendances entre les fichiers : `console` → `service` → `depot_sqlite` → `regles` / `modeles`.

## Installation

1. Installer Python 3.10 ou supérieur.
2. Copier le dossier du projet.
3. Ouvrir un terminal dans ce dossier.

Aucune bibliothèque externe n'est nécessaire.

## Lancement

```bash
python console.py
```

La base de données et les 50 livres de démonstration sont créés automatiquement au premier lancement.

## Menu

```text
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
```

Une mauvaise saisie (choix invalide, matricule vide, livre inexistant, etc.) affiche un message d'erreur sans arrêter le programme.

## Tests

```bash
python -m unittest discover -s tests -v
```

Les tests utilisent une base temporaire : `bibliotheque.db` n'est jamais modifiée. Ils couvrent :

- la recherche (existante, inexistante, par code, accents, caractères spéciaux, terme vide) ;
- l'emprunt (valide, livre déjà emprunté, limite de 3, livre inexistant, champs vides) ;
- le retour (valide, livre non emprunté, mauvais étudiant, double retour) ;
- les retards et les règles métier.

## Base de données

**LIVRES** : `id`, `code` (unique), `titre`, `auteur`, `annee`

**EMPRUNTS** : `id`, `matricule`, `code_livre` (clé étrangère vers `LIVRES.code`), `date_emprunt`, `date_retour_prevue`, `date_retour_effective`, `retourne`

Un index unique empêche deux emprunts actifs pour le même livre.

## Captures d'écran à prévoir

1. Menu principal.
2. Résultat d'une recherche.
3. Confirmation d'un emprunt.
4. Refus d'un emprunt (livre déjà emprunté).
5. Confirmation d'un retour.
6. Affichage des retards.
7. Exécution des tests (`OK`).
