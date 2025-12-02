import re
from flask import Blueprint, render_template, request

from app import build_flags  # réutilisation de la fonction utilitaire

# Blueprint pour la partie "transformation".
transformation_bp = Blueprint("transformation", __name__)


@transformation_bp.route("/transformation", methods=["GET", "POST"])
def transformation():
    """Transformation / nettoyage de texte via regex (re.subn)."""

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
            # On compile la regex. Si le motif est invalide, re.compile lèvera re.error.
            regex = re.compile(pattern, flags)

            # subn applique le remplacement et renvoie (texte_modifié, nombre_remplacements).
            # C'est l'équivalent d'un Regex.Replace en C#, mais qui renvoie aussi
            # le nombre de remplacements effectués :
            #   - output_text : le texte après substitution
            #   - count       : combien de fois le motif a été trouvé et remplacé
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
