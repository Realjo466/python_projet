# On importe la bibliothèque Python "re" qui sert à utiliser les expressions régulières.
import re

# On importe Flask et les fonctions nécessaires pour créer des pages et lire les formulaires.
from flask import Flask, render_template, request

# On crée une instance de l'application Flask.
app = Flask(__name__)

# 1. Dictionnaire contenant des modèles de validation (regex prédéfinies)


# VALIDATION_PATTERNS associe un nom (email, phone...) à une expression régulière.
VALIDATION_PATTERNS = {

    # Regex simple pour valider un email.
    
    "email": r"^[\w\.-]+@[\w\.-]+\.\w{2,}$",  # mail de type josias@gmail.com

    # Regex simplifiée pour un numéro de téléphone togolais.
    "phone": r"^(?:\+228\s?)?(?:7[0-3]|9[0-3,6-9])\d{6}$",          

    # Un code postal français(courament utilise au togo) contient exactement 5 chiffres.
    "postal": r"^\d{5}$",

    # Une date au format JJ/MM/AAAA (sans vérifier les vrais mois/jours).
    "date": r"^([0-2]\d|3[01])/(0\d|1[0-2])/\d{4}$",
}

# Messages explicatifs pour chaque type de validation prédéfini
VALIDATION_FEEDBACK = {
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

@app.route("/validation", methods=["GET", "POST"])
def validation():
    # 
    # Cette fonction gère l'écran où l'utilisateur vérifie une valeur (email, téléphone...).
   

    # Variables initialisées pour qu'elles existent même avant envoi du formulaire.
    result = None          # True / False / "invalid_pattern"
    pattern_used = None    # Regex appliquée
    value = ""             # Valeur entrée par l'utilisateur  (le champ texte)
    validation_type = ""   # Type sélectionné (email, phone , code postal ,date)
    custom_pattern = ""    # Regex personnalisée  personna
    error_message = None   # Message d'erreur si la regex est fausse
    feedback_title = None  # Titre explicatif (ex. "Adresse e-mail invalide")
    feedback_text = None   # Texte plus détaillé pour aider l'utilisateur

    # Si l'utilisateur a soumis le formulaire en POST :
    if request.method == "POST":            # requette HTTP
        
        # On lit la valeur entrée dans le champ "value".
        value = request.form.get("value", "")
        # Le type choisi : email / phone / postal / date / custom.
        validation_type = request.form.get("validation_type", "")
        # Si custom, l'utilisateur fournit lui-même sa regex.
        custom_pattern = request.form.get("custom_pattern", "")

        # --- Cas 1 : L'utilisateur a choisi un modèle prédéfini
        if validation_type in VALIDATION_PATTERNS:
            # On récupère la regex correspondante.
            pattern_used = VALIDATION_PATTERNS[validation_type]
            # On teste la valeur avec re.fullmatch (correspondance totale).
            is_match = re.fullmatch(pattern_used, value)
            # On convertit en True/False.
            result = bool(is_match)

        # --- Cas 2 : L'utilisateur a écrit sa propre regex
        elif validation_type == "custom":
            pattern_used = custom_pattern
            try:
                # On essaie d'appliquer la regex.
                is_match = re.fullmatch(pattern_used, value)
                result = bool(is_match)
            except re.error as e:
                # Si la regex est mauvaise, Python renvoie une erreur.
                result = "invalid_pattern"
                error_message = f"Erreur dans le pattern : {e}"

    # Préparer un message explicatif convivial en fonction du type et du résultat
    if result in (True, False):
        if validation_type in VALIDATION_FEEDBACK:
            msgs = VALIDATION_FEEDBACK[validation_type]
            if result:
                feedback_title = msgs.get("success_title")
                feedback_text = msgs.get("success_text")
            else:
                feedback_title = msgs.get("failure_title")
                feedback_text = msgs.get("failure_text")
        elif validation_type == "custom":
            if result:
                feedback_title = "Motif personnalisé respecté"
                feedback_text = (
                    "La valeur respecte le motif regex que vous avez défini. "
                    "Vous pouvez l'ajuster pour être plus strict ou plus large si besoin."
                )
            else:
                feedback_title = "Motif personnalisé non respecté"
                feedback_text = (
                    "La valeur ne respecte pas le motif regex que vous avez défini. "
                    "Vérifiez que la regex décrit bien le format attendu (par exemple un numéro spécifique)."
                )

    # On renvoie la page avec les résultats et les valeurs entrées.
    return render_template(
        "validation.html",
        result=result,
        pattern_used=pattern_used,
        value=value,
        validation_type=validation_type,
        custom_pattern=custom_pattern,
        error_message=error_message,
        feedback_title=feedback_title,
        feedback_text=feedback_text,
    )

# -----------------------------------------------------------------------------
# 5. ROUTE : Page d'extraction d'informations
# -----------------------------------------------------------------------------

@app.route("/extraction", methods=["GET", "POST"])
def extraction():
    """
    L'utilisateur entre un texte + une regex → on retourne toutes les occurrences trouvées.
    """

    # Valeurs par défaut avant envoi du formulaire.
    text = ""
    pattern = ""
    matches = []      # Liste des résultats trouvés
    error_message = None

    # Si l'utilisateur a envoyé le formulaire :
    if request.method == "POST":
        # On lit le texte et le pattern saisis.
        text = request.form.get("text", "")
        pattern = request.form.get("pattern", "")

        # On lit les options (checkbox).
        ignore_case = request.form.get("ignore_case") == "on"
        multiline = request.form.get("multiline") == "on"
        dotall = request.form.get("dotall") == "on"

        # On construit les flags grâce à la fonction utilitaire.
        flags = build_flags(ignore_case, multiline, dotall)

        try:
            # On compile la regex avec ses options.
            regex = re.compile(pattern, flags)

            # On parcourt CHAQUE correspondance trouvée dans le texte.
            for m in regex.finditer(text):
                matches.append({
                    "match": m.group(0),      # texte trouvé
                    "groups": list(m.groups()),  # groupes capturés
                    "start": m.start(),          # position début
                    "end": m.end(),              # position fin
                })

        except re.error as e:
            # Si la regex est mauvaise → erreur affichée.
            error_message = f"Erreur dans le pattern : {e}"

    # On renvoie la page template avec les résultats.
    return render_template(
        "extraction.html",
        text=text,
        pattern=pattern,
        matches=matches,
        error_message=error_message,
    )

# -----------------------------------------------------------------------------
# 6. ROUTE : Transformation et nettoyage de texte
# -----------------------------------------------------------------------------

@app.route("/transformation", methods=["GET", "POST"])
def transformation():
    """
    L'utilisateur fournit :
        - un texte
        - une regex
        - un texte de remplacement
    On applique re.subn pour transformer le texte.
    """

    # Valeurs par défaut
    text = ""
    pattern = ""
    replacement = ""
    output_text = None
    count = 0
    error_message = None

    if request.method == "POST":
        # On lit les champs fournis dans le formulaire.
        text = request.form.get("text", "")
        pattern = request.form.get("pattern", "")
        replacement = request.form.get("replacement", "")

        # On lit les options de regex.
        ignore_case = request.form.get("ignore_case") == "on"
        multiline = request.form.get("multiline") == "on"
        dotall = request.form.get("dotall") == "on"

        # On construit les flags.
        flags = build_flags(ignore_case, multiline, dotall)

        try:
            # On compile la regex.
            regex = re.compile(pattern, flags)

            # subn applique le remplacement et renvoie (texte_modifié, nombre_remplacements).
            output_text, count = regex.subn(replacement, text)

        except re.error as e:
            # Si la regex est mauvaise → erreur.
            error_message = f"Erreur dans le pattern : {e}"

    # On renvoie les résultats à la page.
    return render_template(
        "transformation.html",
        text=text,
        pattern=pattern,
        replacement=replacement,
        output_text=output_text,
        count=count,
        error_message=error_message,
    )

# -----------------------------------------------------------------------------
# 7. Lancement de l'application Flask
# -----------------------------------------------------------------------------

# Ce bloc s'exécute seulement si on lance ce fichier directement.
if __name__ == "__main__":
    # debug=True : le serveur se recharge automatiquement et affiche les erreurs.
    app.run(debug=True)
