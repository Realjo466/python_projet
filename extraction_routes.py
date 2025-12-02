import re
from flask import Blueprint, render_template, request

from utils import build_flags  

# Blueprint pour la partie "extraction".
extraction_bp = Blueprint("extraction", __name__)


@extraction_bp.route("/extraction", methods=["GET", "POST"])
def extraction():
    """L'utilisateur entre un texte + une regex → on retourne toutes les occurrences trouvées."""

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
            # On compile la regex avec ses options. C'est l'équivalent de créer un
            # objet Regex réutilisable en C# (new Regex(pattern, options)).
            # Si "pattern" est invalide (mauvaise syntaxe), re.compile lève re.error.
            regex = re.compile(pattern, flags)

            # regex.finditer(text) parcourt CHAQUE correspondance trouvée dans le
            # texte. À chaque fois, on récupère :
            #   - m.group(0)  : le texte complet qui matche la regex
            #   - m.groups()  : les groupes capturants (parenthèses dans le motif)
            #   - m.start()/m.end() : positions de début et de fin dans "text".
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
