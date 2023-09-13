
from .namematcher import NameMatcher

DATA = [("Mueller", "Lisa", "tes"),
        ("Meier", "Rainer", "5eII"),
        ("Fährmann", "Anaïs-Dörte", "8b"),
        ("Ruß-Mœllerû", "Brìt", "3eII"),
        ("Müller", "Hermine", "teachers")]


class MockUserDataProvider():
    def getUserData(self):
        return [{"sn": sn, "givenName": gn, "sophomorixAdminClass": ac} for sn, gn, ac in DATA]


def test_normalization():
    matcher = NameMatcher(MockUserDataProvider())

    for name in ["TES_MuellerLisa", "5eII_MeierRainer", "8b_FährmannAnaïs-Dörte", "3eII_Ruß-MœllerûBrìt", "MüllerHermine"]:
        assert name in matcher.normalized_names, f"Name {name} was not found in normalized name list {matcher.normalized_names}"
