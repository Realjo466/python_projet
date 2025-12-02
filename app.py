# On importe la bibliothèque Python "re" qui sert à utiliser les expressions régulières.
import re

# On importe Flask et les fonctions nécessaires pour créer des pages et lire les formulaires.
from flask import Flask, render_template

# On importe les blueprints définis dans les fichiers séparés.
from validation_routes import validation_bp
from extraction_routes import extraction_bp
from transformation_routes import transformation_bp

# On crée une instance de l'application Flask.
app = Flask(__name__)

# On enregistre les blueprints : cela "branche" les routes définies dans
# les autres fichiers sur cette application principale.
app.register_blueprint(validation_bp)
app.register_blueprint(extraction_bp)
app.register_blueprint(transformation_bp)

# 1. Dictionnaire contenant des modèles de validation (regex prédéfinies)
# et messages associés : ces éléments ont été déplacés dans validation_routes.py
# pour regrouper la logique de validation au même endroit.
    "email": {
        "success_title": "Adresse e-mail valide",
        "success_text": (
            "L'adresse e-mail respecte le format attendu : une partie avant '@', "
            "un '@', puis un nom de domaine et une extension."
        ),
        "failure_title": "Adresse e-mail invalide",
        "failure_text": (
            "Une adresse e-mail doit ressembler à 'prenom.nom@domaine.com', "
            "avec un '@' et un nom de domaine valide."
        ),
    },
    "phone": {
        "success_title": "Numéro de téléphone plausible",
        "success_text": (
            "Ce numéro utilise uniquement des chiffres, espaces, parenthèses, "
            "tirets et un éventuel '+', avec une longueur minimale raisonnable."
        ),
        "failure_title": "Numéro de téléphone invalide",
        "failure_text": (
            "Un numéro de téléphone général ne doit contenir que des chiffres, "
            "espaces, parenthèses et tirets, et avoir au moins 8 caractères."
        ),
    },
    "postal": {
        "success_title": "Code postal valide",
        "success_text": "Le code postal contient exactement 5 chiffres.",
        "failure_title": "Code postal invalide",
        "failure_text": (
            "Un code postal français standard contient exactement 5 chiffres, "
            "par exemple 75001."
        ),
    },
    "date": {
        "success_title": "Date au format JJ/MM/AAAA",
        "success_text": (
            "La date respecte le format JJ/MM/AAAA (jour sur 2 chiffres, "
            "mois sur 2 chiffres, année sur 4 chiffres)."
        ),
        "failure_title": "Date invalide",
        "failure_text": (
            "Une date au format JJ/MM/AAAA ressemble à 31/12/2025 : "
            "deux chiffres, '/', deux chiffres, '/', quatre chiffres."
     ),
    },
}

# 2. Fonction utilitaire pour construire les flags des regex

# Cette fonction retourne un ensemble d'options selon que l'utilisateur
# a coché IGNORECASE, MULTILINE ou DOTALL.
def build_flags(ignore_case: bool, multiline: bool, dotall: bool) -> int:
    flags = 0  # On commence sans aucune option.
   # par defaut les bool sont sur false 

    # Option : ignorer majuscule/minuscule.
    if ignore_case:
        flags |= re.IGNORECASE

    # Option : autoriser les recherches sur plusieurs lignes.
    if multiline:
        flags |= re.MULTILINE

    # Option : permettre au . de capturer les retours à la ligne.
    if dotall:
        flags |= re.DOTALL

    return flags  # On retourne toutes les options activées.

# 3. ROUTE : Page d'accueil


# @app.route("/") signifie : quand un utilisateur visite "/", on exécute index().

@app.route("/")
def index():
    # On retourne la page HTML "index.html".
    return render_template("index.html")

# 4. ROUTE : Page de validation de données
# -----------------------------------------------------------------------------
# La logique de validation a été déplacée dans validation_routes.py où un
# blueprint (validation_bp) définit la route "/validation" avec tous les
# commentaires détaillés sur les regex.

# -----------------------------------------------------------------------------
# 5. ROUTE : Page d'extraction d'informations
# -----------------------------------------------------------------------------
# La logique d'extraction a été déplacée dans extraction_routes.py où un
# blueprint (extraction_bp) définit la route "/extraction".

# -----------------------------------------------------------------------------
# 6. ROUTE : Transformation et nettoyage de texte
# -----------------------------------------------------------------------------
# La logique de transformation a été déplacée dans transformation_routes.py où un
# blueprint (transformation_bp) définit la route "/transformation".

# -----------------------------------------------------------------------------
# 7. Lancement de l'application Flask
# -----------------------------------------------------------------------------

# Ce bloc s'exécute seulement si on lance ce fichier directement.
if __name__ == "__main__":
    # debug=True : le serveur se recharge automatiquement et affiche les erreurs.
    app.run(debug=True)
