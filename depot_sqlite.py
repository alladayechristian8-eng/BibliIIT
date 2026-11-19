
"""Couche d'accès aux données SQLite de BibliIIT."""

import sqlite3
import unicodedata
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import date
from pathlib import Path

from modeles import Livre, Emprunt
from regles import livre_disponible, peut_emprunter

# Chemin d'une base SQLite (None = base par défaut du projet).
CheminDB = str | Path | None


# ==========================================================
# 1. CONFIGURATION DE LA BASE DE DONNÉES
# ==========================================================

CHEMIN_DB = Path(__file__).resolve().parent / "bibliotheque.db"


def _sans_accent(texte: str | None) -> str:
    """Met le texte en minuscules et retire les accents (pour la recherche)."""
    if texte is None:
        return ""
    decompose = unicodedata.normalize("NFD", str(texte))
    return "".join(c for c in decompose if not unicodedata.combining(c)).lower()


@contextmanager
def connexion(db_path: CheminDB = None) -> Iterator[sqlite3.Connection]:
    """
    Ouvre une connexion SQLite.
    Valide ou annule la transaction, puis ferme la connexion.
    """
    chemin = Path(db_path) if db_path is not None else CHEMIN_DB
    chemin.parent.mkdir(parents=True, exist_ok=True)

    cn = sqlite3.connect(chemin, timeout=10)
    cn.row_factory = sqlite3.Row
    cn.execute("PRAGMA foreign_keys = ON")
    # Fonction SQL utilisée par la recherche (insensible aux accents/casse).
    cn.create_function("sans_accent", 1, _sans_accent, deterministic=True)

    try:
        yield cn
        cn.commit()

    except Exception:
        cn.rollback()
        raise

    finally:
        cn.close()


# ==========================================================
# 2. DONNÉES INITIALES : 50 LIVRES
# ==========================================================

def obtenir_livres_demo() -> list[tuple[str, str, str, int]]:
    """Retourne les 50 livres de démonstration (L001 à L005 : voir le sujet)."""

    livres = [
        # Livres imposés par le sujet
        ("L001", "Python pour débutants", "Auteur inconnu", 2023),
        ("L002", "Réseaux informatiques", "Auteur inconnu", 2022),
        ("L003", "Algèbre linéaire", "Auteur inconnu", 2021),
        ("L004", "Les Soleils des Indépendances", "Ahmadou Kourouma", 1968),
        ("L005", "Django en pratique", "Auteur inconnu", 2024),

        # Programmation et informatique
        ("L006", "Apprendre Python", "Gérard Swinnen", 2012),
        ("L007", "Le langage C", "Brian Kernighan et Dennis Ritchie", 1988),
        ("L008", "Clean Code", "Robert C. Martin", 2008),
        ("L009", "L'art de la programmation", "Donald Knuth", 1997),
        ("L010", "Introduction à l'algorithmique", "Thomas H. Cormen", 2022),
        ("L011", "Structures de données", "Niklaus Wirth", 1976),
        ("L012", "Programmation Java", "Herbert Schildt", 2018),
        ("L013", "Programmation en C++", "Bjarne Stroustrup", 2013),
        ("L014", "JavaScript pour les débutants", "David Flanagan", 2020),

        # Réseaux et systèmes
        ("L015", "Computer Networking", "James F. Kurose", 2021),
        ("L016", "TCP/IP Illustrated", "W. Richard Stevens", 1994),
        ("L017", "Systèmes d'exploitation", "Abraham Silberschatz", 2018),
        ("L018", "Linux pour les débutants", "William Shotts", 2019),
        ("L019", "Administration des réseaux", "Guy Pujolle", 2014),
        ("L020", "Sécurité informatique", "William Stallings", 2017),
        ("L021", "Cryptographie appliquée", "Bruce Schneier", 1996),

        # Bases de données et développement web
        ("L022", "Database System Concepts", "Abraham Silberschatz", 2019),
        ("L023", "SQL pour les débutants", "John J. Patrick", 2008),
        ("L024", "Learning SQL", "Alan Beaulieu", 2020),
        ("L025", "Fluent Python", "Luciano Ramalho", 2022),
        ("L026", "HTML et CSS", "Jon Duckett", 2011),
        ("L027", "JavaScript: The Good Parts", "Douglas Crockford", 2008),

        # Mathématiques et sciences
        ("L028", "Analyse mathématique", "Walter Rudin", 1976),
        ("L029", "Mathématiques pour l'informatique", "Eric Lehman", 2017),
        ("L030", "Probabilités et statistiques", "Sheldon Ross", 2014),
        ("L031", "Logique mathématique", "George Boole", 1854),
        ("L032", "Physique générale", "Douglas C. Giancoli", 2013),
        ("L033", "Intelligence artificielle", "Stuart Russell et Peter Norvig", 2021),

        # Littérature africaine
        ("L034", "Une si longue lettre", "Mariama Bâ", 1979),
        ("L035", "L'Aventure ambiguë", "Cheikh Hamidou Kane", 1961),
        ("L036", "Le Monde s'effondre", "Chinua Achebe", 1958),
        ("L037", "Ville cruelle", "Mongo Beti", 1954),
        ("L038", "Allah n'est pas obligé", "Ahmadou Kourouma", 2000),
        ("L039", "Les Bouts de bois de Dieu", "Ousmane Sembène", 1960),
        ("L040", "L'Enfant noir", "Camara Laye", 1953),

        # Littérature générale et développement personnel
        ("L041", "Le Petit Prince", "Antoine de Saint-Exupéry", 1943),
        ("L042", "Les Misérables", "Victor Hugo", 1862),
        ("L043", "L'Étranger", "Albert Camus", 1942),
        ("L044", "1984", "George Orwell", 1949),
        ("L045", "Le Vieil Homme et la Mer", "Ernest Hemingway", 1952),
        ("L046", "L'Alchimiste", "Paulo Coelho", 1988),
        ("L047", "Père riche, père pauvre", "Robert T. Kiyosaki", 1997),
        ("L048", "Les 7 habitudes de ceux qui réalisent tout", "Stephen Covey", 1989),
        ("L049", "Réfléchissez et devenez riche", "Napoleon Hill", 1937),
        ("L050", "L'homme le plus riche de Babylone", "George S. Clason", 1926),
    ]

    return livres


# ==========================================================
# 3. MIGRATION ET CRÉATION DES TABLES
# ==========================================================

def _colonnes_table(cn: sqlite3.Connection, table: str) -> set[str]:
    """Retourne les colonnes d'une table SQLite."""

    return {
        ligne["name"]
        for ligne in cn.execute(
            f"PRAGMA table_info({table})"
        ).fetchall()
    }


def _ajouter_colonne(cn: sqlite3.Connection, table: str, colonne: str, definition: str) -> None:
    """Ajoute une colonne uniquement si elle n'existe pas."""

    colonnes = _colonnes_table(cn, table)

    if colonne not in colonnes:
        cn.execute(
            f"ALTER TABLE {table} ADD COLUMN {colonne} {definition}"
        )


def _migrer_structure(cn: sqlite3.Connection) -> None:
    """
    Met à jour les anciennes structures sans supprimer les données.
    """

    # ------------------------------------------------------
    # MIGRATION DE LA TABLE LIVRES
    # ------------------------------------------------------

    _ajouter_colonne(cn, "LIVRES", "code", "TEXT")
    _ajouter_colonne(cn, "LIVRES", "titre", "TEXT")
    _ajouter_colonne(cn, "LIVRES", "auteur", "TEXT")
    _ajouter_colonne(cn, "LIVRES", "annee", "INTEGER")

    # Identifiants pour les éventuelles anciennes lignes sans code.
    cn.execute("""
        UPDATE LIVRES
        SET code = 'LEGACY-' || rowid
        WHERE code IS NULL OR TRIM(code) = ''
    """)

    # ------------------------------------------------------
    # MIGRATION DE LA TABLE EMPRUNTS
    # ------------------------------------------------------

    anciennes_colonnes = _colonnes_table(cn, "EMPRUNTS")

    _ajouter_colonne(cn, "EMPRUNTS", "id", "INTEGER")
    _ajouter_colonne(cn, "EMPRUNTS", "matricule", "TEXT")
    _ajouter_colonne(cn, "EMPRUNTS", "code_livre", "TEXT")
    _ajouter_colonne(cn, "EMPRUNTS", "date_emprunt", "TEXT")
    _ajouter_colonne(cn, "EMPRUNTS", "date_retour_prevue", "TEXT")
    _ajouter_colonne(cn, "EMPRUNTS", "date_retour_effective", "TEXT")
    _ajouter_colonne(
        cn, "EMPRUNTS", "retourne",
        "INTEGER NOT NULL DEFAULT 0"
    )

    # Les anciens enregistrements reçoivent un identifiant.
    cn.execute("""
        UPDATE EMPRUNTS
        SET id = rowid
        WHERE id IS NULL
    """)

    # Récupération éventuelle d'une ancienne colonne de retour.
    if "date_retour" in anciennes_colonnes:
        cn.execute("""
            UPDATE EMPRUNTS
            SET date_retour_effective = date_retour
            WHERE date_retour_effective IS NULL
              AND date_retour IS NOT NULL
        """)

    # Si un ancien retour est renseigné, le livre est considéré rendu.
    cn.execute("""
        UPDATE EMPRUNTS
        SET retourne = 1
        WHERE date_retour_effective IS NOT NULL
          AND TRIM(date_retour_effective) <> ''
          AND retourne = 0
    """)


def _creer_index(cn: sqlite3.Connection) -> None:
    """Crée les index utiles lorsque les données le permettent."""

    # Index unique sur le code des livres.
    doublon_livre = cn.execute("""
        SELECT code
        FROM LIVRES
        GROUP BY code
        HAVING COUNT(*) > 1
        LIMIT 1
    """).fetchone()

    if doublon_livre is None:
        cn.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_livres_code
            ON LIVRES(code)
        """)

    # Index sur les matricules.
    cn.execute("""
        CREATE INDEX IF NOT EXISTS idx_emprunts_matricule
        ON EMPRUNTS(matricule)
    """)

    # Index sur les dates de retour.
    cn.execute("""
        CREATE INDEX IF NOT EXISTS idx_emprunts_retour
        ON EMPRUNTS(date_retour_prevue)
    """)

    # Un seul emprunt actif par livre.
    doublon_actif = cn.execute("""
        SELECT code_livre
        FROM EMPRUNTS
        WHERE retourne = 0
        GROUP BY code_livre
        HAVING COUNT(*) > 1
        LIMIT 1
    """).fetchone()

    if doublon_actif is None:
        cn.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_un_emprunt_actif
            ON EMPRUNTS(code_livre)
            WHERE retourne = 0
        """)


def creer_tables(db_path: CheminDB = None) -> None:
    """Crée les tables et met à jour leur structure."""

    with connexion(db_path) as cn:

        cn.execute("""
            CREATE TABLE IF NOT EXISTS LIVRES (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL UNIQUE,
                titre TEXT NOT NULL,
                auteur TEXT NOT NULL,
                annee INTEGER NOT NULL CHECK(annee > 0)
            )
        """)

        cn.execute("""
            CREATE TABLE IF NOT EXISTS EMPRUNTS (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                matricule TEXT NOT NULL,
                code_livre TEXT NOT NULL,
                date_emprunt TEXT NOT NULL,
                date_retour_prevue TEXT NOT NULL,
                date_retour_effective TEXT,
                retourne INTEGER NOT NULL DEFAULT 0
                    CHECK(retourne IN (0, 1)),
                FOREIGN KEY(code_livre)
                    REFERENCES LIVRES(code)
            )
        """)

        _migrer_structure(cn)
        _creer_index(cn)


def mettre_a_jour_base(db_path: CheminDB = None) -> None:
    """Met à jour la structure de la base sans perdre les données."""

    creer_tables(db_path)


def initialiser_base(db_path: CheminDB = None) -> None:
    """Initialise complètement la base de données."""

    creer_tables(db_path)
    inserer_livres_demo(db_path)


# ==========================================================
# 4. INSERTION DES LIVRES DE DÉMONSTRATION
# ==========================================================

def inserer_livres_demo(db_path: CheminDB = None) -> None:
    """Insère les livres de démonstration sans doublons."""

    livres = obtenir_livres_demo()

    with connexion(db_path) as cn:

        for livre in livres:
            cn.execute("""
                INSERT INTO LIVRES (code, titre, auteur, annee)
                SELECT ?, ?, ?, ?
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM LIVRES
                    WHERE code = ?
                )
            """, (*livre, livre[0]))


# ==========================================================
# 5. AJOUT D'UN LIVRE
# ==========================================================

def ajouter_livre(livre: Livre, db_path: CheminDB = None) -> None:
    """Ajoute un livre au catalogue."""

    with connexion(db_path) as cn:
        cn.execute("""
            INSERT INTO LIVRES (code, titre, auteur, annee)
            VALUES (?, ?, ?, ?)
        """, (
            livre.code,
            livre.titre,
            livre.auteur,
            livre.annee
        ))


# ==========================================================
# 6. CONVERSION DES DONNÉES
# ==========================================================

def convertir_livre(ligne: sqlite3.Row) -> Livre:
    """Convertit une ligne SQLite en objet Livre."""

    return Livre(
        ligne["code"],
        ligne["titre"],
        ligne["auteur"],
        ligne["annee"]
    )


# ==========================================================
# 7. RECHERCHE D'UN LIVRE
# ==========================================================

def rechercher_livre(terme: str, db_path: CheminDB = None) -> list[Livre]:
    """Recherche par code, titre ou auteur (sans tenir compte des accents)."""

    # On échappe % et _ pour qu'ils soient cherchés comme de simples caractères.
    propre = _sans_accent(terme.strip())
    propre = propre.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    motif = f"%{propre}%"

    with connexion(db_path) as cn:
        lignes = cn.execute("""
            SELECT code, titre, auteur, annee
            FROM LIVRES
            WHERE sans_accent(code)   LIKE ? ESCAPE '\\'
               OR sans_accent(titre)  LIKE ? ESCAPE '\\'
               OR sans_accent(auteur) LIKE ? ESCAPE '\\'
            ORDER BY titre
        """, (motif, motif, motif)).fetchall()

    return [convertir_livre(ligne) for ligne in lignes]


# ==========================================================
# 8. CATALOGUE COMPLET
# ==========================================================

def tous_les_livres(db_path: CheminDB = None) -> list[Livre]:
    """Retourne tous les livres."""

    with connexion(db_path) as cn:
        lignes = cn.execute("""
            SELECT code, titre, auteur, annee
            FROM LIVRES
            ORDER BY titre
        """).fetchall()

    return [convertir_livre(ligne) for ligne in lignes]


# ==========================================================
# 9. RÉCUPÉRER UN LIVRE
# ==========================================================

def recuperer_livre(code: str, db_path: CheminDB = None) -> Livre | None:
    """Recherche un livre par son code."""

    with connexion(db_path) as cn:
        ligne = cn.execute("""
            SELECT code, titre, auteur, annee
            FROM LIVRES
            WHERE code = ?
        """, (code,)).fetchone()

    return convertir_livre(ligne) if ligne else None


# ==========================================================
# 10. DISPONIBILITÉ D'UN LIVRE
# ==========================================================

def livre_est_emprunte(code: str, db_path: CheminDB = None) -> bool:
    """Vérifie si un livre possède un emprunt actif."""

    with connexion(db_path) as cn:
        ligne = cn.execute("""
            SELECT 1
            FROM EMPRUNTS
            WHERE code_livre = ?
              AND retourne = 0
            LIMIT 1
        """, (code,)).fetchone()

    return ligne is not None


# ==========================================================
# 11. NOMBRE D'EMPRUNTS ACTIFS
# ==========================================================

def nombre_emprunts_actifs(matricule: str, db_path: CheminDB = None) -> int:
    """Compte les emprunts actifs d'un étudiant."""

    with connexion(db_path) as cn:
        resultat = cn.execute("""
            SELECT COUNT(*)
            FROM EMPRUNTS
            WHERE matricule = ?
              AND retourne = 0
        """, (matricule,)).fetchone()

    return resultat[0]


# ==========================================================
# 12. EFFECTUER UN EMPRUNT
# ==========================================================

def emprunter_livre(emprunt: Emprunt, db_path: CheminDB = None) -> str:
    """
    Vérifie les règles métier puis enregistre un emprunt (transaction atomique).

    Retourne : "ok", "livre_inexistant", "indisponible" ou "limite_atteinte".
    """

    with connexion(db_path) as cn:

        cn.execute("BEGIN IMMEDIATE")

        livre = cn.execute("""
            SELECT 1
            FROM LIVRES
            WHERE code = ?
        """, (emprunt.code_livre,)).fetchone()

        if livre is None:
            return "livre_inexistant"

        deja_emprunte = cn.execute("""
            SELECT 1
            FROM EMPRUNTS
            WHERE code_livre = ?
              AND retourne = 0
        """, (emprunt.code_livre,)).fetchone() is not None

        if not livre_disponible(deja_emprunte):
            return "indisponible"

        nombre = cn.execute("""
            SELECT COUNT(*)
            FROM EMPRUNTS
            WHERE matricule = ?
              AND retourne = 0
        """, (emprunt.matricule,)).fetchone()[0]

        if not peut_emprunter(nombre):
            return "limite_atteinte"

        try:
            cn.execute("""
                INSERT INTO EMPRUNTS (
                    matricule,
                    code_livre,
                    date_emprunt,
                    date_retour_prevue,
                    date_retour_effective,
                    retourne
                )
                VALUES (?, ?, ?, ?, NULL, 0)
            """, (
                emprunt.matricule,
                emprunt.code_livre,
                emprunt.date_emprunt,
                emprunt.date_retour_prevue
            ))

        except sqlite3.IntegrityError:
            return "indisponible"

    return "ok"


# Ancien nom conservé pour compatibilité.
effectuer_emprunt = emprunter_livre


# ==========================================================
# 13. RETOURNER UN LIVRE
# ==========================================================

def retourner_livre(
    code: str,
    matricule: str,
    db_path: CheminDB = None
) -> bool:
    """Enregistre le retour d'un livre."""

    with connexion(db_path) as cn:

        curseur = cn.execute("""
            UPDATE EMPRUNTS
            SET retourne = 1,
                date_retour_effective = ?
            WHERE code_livre = ?
              AND matricule = ?
              AND retourne = 0
        """, (
            date.today().isoformat(),
            code,
            matricule
        ))

    return curseur.rowcount == 1


# ==========================================================
# 14. EMPRUNTS ACTIFS D'UN ÉTUDIANT
# ==========================================================

def emprunts_actifs_etudiant(matricule: str, db_path: CheminDB = None) -> list[dict]:
    """Retourne les emprunts actifs d'un étudiant."""

    with connexion(db_path) as cn:
        lignes = cn.execute("""
            SELECT
                e.*,
                l.titre
            FROM EMPRUNTS e
            INNER JOIN LIVRES l
                ON e.code_livre = l.code
            WHERE e.matricule = ?
              AND e.retourne = 0
            ORDER BY e.date_emprunt
        """, (matricule,)).fetchall()

    return [dict(ligne) for ligne in lignes]


# ==========================================================
# 15. HISTORIQUE DES EMPRUNTS
# ==========================================================

def historique_emprunts(matricule: str | None = None, db_path: CheminDB = None) -> list[dict]:
    """Retourne l'historique général ou celui d'un étudiant."""

    with connexion(db_path) as cn:

        if matricule:
            lignes = cn.execute("""
                SELECT e.*, l.titre
                FROM EMPRUNTS e
                INNER JOIN LIVRES l
                    ON e.code_livre = l.code
                WHERE e.matricule = ?
                ORDER BY e.id DESC
            """, (matricule,)).fetchall()

        else:
            lignes = cn.execute("""
                SELECT e.*, l.titre
                FROM EMPRUNTS e
                INNER JOIN LIVRES l
                    ON e.code_livre = l.code
                ORDER BY e.id DESC
            """).fetchall()

    return [dict(ligne) for ligne in lignes]


# ==========================================================
# 16. LIVRES DISPONIBLES
# ==========================================================

def livres_disponibles(db_path: CheminDB = None) -> list[Livre]:
    """Retourne les livres qui ne sont pas empruntés."""

    with connexion(db_path) as cn:
        lignes = cn.execute("""
            SELECT l.code, l.titre, l.auteur, l.annee
            FROM LIVRES l
            WHERE NOT EXISTS (
                SELECT 1
                FROM EMPRUNTS e
                WHERE e.code_livre = l.code
                  AND e.retourne = 0
            )
            ORDER BY l.titre
        """).fetchall()

    return [convertir_livre(ligne) for ligne in lignes]


# ==========================================================
# 17. LIVRES EN RETARD
# ==========================================================

def livres_en_retard(db_path: CheminDB = None) -> list[dict]:
    """Retourne les emprunts dont la date limite est dépassée."""

    aujourd_hui = date.today().isoformat()

    with connexion(db_path) as cn:
        lignes = cn.execute("""
            SELECT
                e.*,
                l.titre
            FROM EMPRUNTS e
            INNER JOIN LIVRES l
                ON e.code_livre = l.code
            WHERE e.retourne = 0
              AND e.date_retour_prevue IS NOT NULL
              AND e.date_retour_prevue <> ''
              AND e.date_retour_prevue < ?
            ORDER BY e.date_retour_prevue
        """, (aujourd_hui,)).fetchall()

    return [dict(ligne) for ligne in lignes]


# ==========================================================
# 18. STATISTIQUES
# ==========================================================

def statistiques(db_path: CheminDB = None) -> dict[str, int]:
    """Retourne les statistiques générales."""

    aujourd_hui = date.today().isoformat()

    with connexion(db_path) as cn:

        total_livres = cn.execute("""
            SELECT COUNT(*) FROM LIVRES
        """).fetchone()[0]

        emprunts_actifs = cn.execute("""
            SELECT COUNT(*)
            FROM EMPRUNTS
            WHERE retourne = 0
        """).fetchone()[0]

        emprunts_rendus = cn.execute("""
            SELECT COUNT(*)
            FROM EMPRUNTS
            WHERE retourne = 1
        """).fetchone()[0]

        retards = cn.execute("""
            SELECT COUNT(*)
            FROM EMPRUNTS
            WHERE retourne = 0
              AND date_retour_prevue IS NOT NULL
              AND date_retour_prevue <> ''
              AND date_retour_prevue < ?
        """, (aujourd_hui,)).fetchone()[0]

    return {
        "livres": total_livres,
        "emprunts_actifs": emprunts_actifs,
        "emprunts_rendus": emprunts_rendus,
        "retards": retards
    }


# ==========================================================
# 19. LISTE DES EMPRUNTS ACTIFS
# ==========================================================

def liste_emprunts_actifs(db_path: CheminDB = None) -> list[dict]:
    """Retourne tous les emprunts qui ne sont pas rendus."""

    with connexion(db_path) as cn:
        lignes = cn.execute("""
            SELECT
                e.id,
                e.matricule,
                e.code_livre,
                l.titre,
                e.date_emprunt,
                e.date_retour_prevue
            FROM EMPRUNTS e
            INNER JOIN LIVRES l
                ON e.code_livre = l.code
            WHERE e.retourne = 0
            ORDER BY e.date_emprunt DESC
        """).fetchall()

    return [dict(ligne) for ligne in lignes]


# ==========================================================
# 20. LISTE DES RETOURS EFFECTUÉS
# ==========================================================

def liste_retours(db_path: CheminDB = None) -> list[dict]:
    """Retourne tous les livres déjà rendus."""

    with connexion(db_path) as cn:
        lignes = cn.execute("""
            SELECT
                e.id,
                e.matricule,
                e.code_livre,
                l.titre,
                e.date_emprunt,
                e.date_retour_prevue,
                e.date_retour_effective
            FROM EMPRUNTS e
            INNER JOIN LIVRES l
                ON e.code_livre = l.code
            WHERE e.retourne = 1
            ORDER BY e.date_retour_effective DESC
        """).fetchall()

    return [dict(ligne) for ligne in lignes]


# Nom demandé par le sujet : livres actuellement empruntés.
livres_empruntes = liste_emprunts_actifs
