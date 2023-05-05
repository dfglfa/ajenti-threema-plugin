import tempfile
from namematcher import NameMatcher

HEADER = "Nom,Prenom,Classe"
DATA = ["Mueller,Lisa,TES", "Meier,Rainer,5II",
        "Fährmann,Anaïs-Dörte,8b", "Ruß-Mœllerû,Brìt,3II"]


def test_normalization():
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
        temp_file.write(HEADER)
        for item in DATA:
            temp_file.write("\n" + item)

    matcher = NameMatcher(temp_file.name)

    for name in ["TES_MuellerLisa", "5II_MeierRainer", "8b_FaehrmannAnaisDoerte", "3II_RussMlleruBrit"]:
        assert name in matcher.normalized_names, f"Name {name} was not found in normalized name list {matcher.normalized_names}"
