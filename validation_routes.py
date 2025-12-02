import re
from flask import Blueprint, render_template, request

# On crée un "blueprint" pour regrouper les routes liées à la validation.
# Ce blueprint sera enregistré dans l'application principale (app.py).
validation_bp = Blueprint("validation", __name__)

# Dictionnaire des patterns de validation (copié depuis app.py pour clarté).
# Idéalement, si tu veux aller plus loin, on pourrait aussi extraire ces
# constantes dans un autre module commun, mais pour l'instant on garde
# exactement la même logique.
VALIDATION_PATTERNS = {

    # --- EMAIL -----------------------------------------------------------------
    # r"^[\w\.-]+@[\w\.-]+\.\w{2,}$" signifie :
    #   ^              → début de la chaîne
    #   [\w\.-]+      → un ou plusieurs caractères parmi :
    #                     - \w : lettre, chiffre ou underscore (_)
    #                     - .  : point littéral
    #                     - -  : tiret
    #   @              → le caractère arobase
    #   [\w\.-]+      → nom de domaine (même logique que la partie avant @)
    #   \.            → un point littéral (".")
    #   \w{2,}        → au moins 2 caractères "mot" (ex: fr, com, info)
    #   $              → fin de la chaîne
    # Exemple accepté : "prenom.nom@domaine.com".
    "email": r"^[\w\.-]+@[\w\.-]+\.\w{2,}$",  # mail de type josias@gmail.com

    # --- TÉLÉPHONE TOGOLAIS ----------------------------------------------------
    # r"^(?:\+228\s?)?(?:7[0-3]|9[0-3,6-9])\d{6}$" signifie :
    #   ^                        → début de la chaîne
    #   (?:\+228\s?)?           → éventuellement le préfixe international "+228"
    #                               avec 0 ou 1 espace après (\s? = espace facultatif)
    #   (?:7[0-3]|9[0-3,6-9])    → début du numéro national :
    #                               - 7 suivi d'un chiffre entre 0 et 3 (70, 71, 72, 73)
    #                               - OU 9 suivi d'un chiffre entre 0-3 ou 6-9
    #   \d{6}                   → exactement 6 chiffres supplémentaires
    #   $                        → fin de la chaîne
    # Cette regex décrit donc un numéro togolais plausible, avec ou sans "+228".
    "phone": r"^(?:\+228\s?)?(?:7[0-3]|9[0-3,6-9])\d{6}$",          

    # --- CODE POSTAL -----------------------------------------------------------
    # r"^\d{5}$" signifie :
    #   ^       → début
    #   \d{5}  → exactement 5 chiffres
    #   $       → fin
    # Exemple : "75001". Aucune lettre ou espace n'est autorisé.
    "postal": r"^\d{5}$",

    # --- DATE JJ/MM/AAAA -------------------------------------------------------
    # r"^([0-2]\d|3[01])/(0\d|1[0-2])/\d{4}$" signifie :
    #   ^                            → début
    #   ([0-2]\d|3[01])             → le jour :
    #                                   - 0x, 1x ou 2x (00 à 29)
    #                                   - OU 30 ou 31
    #   /                            → un slash littéral
    #   (0\d|1[0-2])                 → le mois : 00 à 09 ou 10 à 12
    #   /                            → un deuxième slash
    #   \d{4}                       → l'année sur 4 chiffres (ex : 2025)
    #   $                            → fin
    # Remarque : on vérifie le *format* JJ/MM/AAAA, pas la validité du calendrier.
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


@validation_bp.route("/validation", methods=["GET", "POST"])
def validation():
    """
    Route de validation de données (email, téléphone, code postal, date ou regex
    personnalisée). Le code et les commentaires sont les mêmes que dans app.py,
    simplement déplacés ici.
    """

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
            # On récupère la regex correspondante dans le dictionnaire ci-dessus
            # (email, phone, postal, date). Chaque motif décrit la forme complète
            # attendue de la valeur.
            pattern_used = VALIDATION_PATTERNS[validation_type]

            # re.fullmatch impose que *toute* la chaîne "value" respecte le motif.
            # Attention : contrairement à re.search qui cherche "quelque chose"
            # n'importe où dans le texte, fullmatch doit couvrir toute la valeur.
            # Exemple :
            #   pattern_used = r"^\d{5}$" (5 chiffres)
            #   value = "75001"   → match OK
            #   value = "75001-Paris" → pas de match (il y a du texte en plus).
            is_match = re.fullmatch(pattern_used, value)

            # is_match est soit un objet de type Match, soit None → on convertit
            # en booléen simple (True si match, False sinon).
            result = bool(is_match)

        # --- Cas 2 : L'utilisateur a écrit sa propre regex
        elif validation_type == "custom":
            # Dans ce cas, l'utilisateur écrit lui-même son motif regex dans le
            # formulaire. On le récupère tel quel dans "custom_pattern".
            pattern_used = custom_pattern
            try:
                # On essaie d'appliquer la regex avec re.fullmatch, comme pour les
                # motifs prédéfinis. Si le motif est syntaxiquement incorrect
                # (parenthèse manquante, crochet non fermé, etc.), re.fullmatch
                # lève une exception de type re.error.
                is_match = re.fullmatch(pattern_used, value)
                result = bool(is_match)
            except re.error as e:
                # Si la regex est mauvaise, Python renvoie une erreur → on informe
                # l'utilisateur en lui renvoyant un message lisible.
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
