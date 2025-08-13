from datetime import date
from .models import Titre


def calculate_redevance(titre: Titre) -> float:
    base_by_type = {
        Titre.Type.LICENCE_1: 1000.0,
        Titre.Type.LICENCE_2: 2000.0,
        Titre.Type.AGREMENT_VENDEURS: 500.0,
        Titre.Type.AGREMENT_INSTALLATEURS: 800.0,
        Titre.Type.CONCESSION: 5000.0,
        Titre.Type.RECEPISSE: 200.0,
    }
    base = base_by_type.get(titre.type, 0.0)
    years = max(1, titre.duree_ans)
    return round(base * years, 2)