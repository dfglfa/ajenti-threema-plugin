
from .namematcher import NameMatcher

EXAMPLE_DATA = {("Mueller", "Lisa", "tes"): "TES_MuellerLisa",
                ("Meier", "Rainer", "5eII"): "5eII_MeierRainer",
                ("Fährmann", "Anaïs-Dörte", "8b"): "8b_FährmannAnaïs-Dörte",
                ("Ruß-Mœllerû", "Brìt", "3eII"): "3eII_Ruß-MœllerûBrìt",
                ("Müller", "Hermine", "teachers"): "MüllerHermine"}


class MockUserDataProvider():
    def getUserData(self):
        return [{"sn": sn, "givenName": gn, "sophomorixAdminClass": ac} for sn, gn, ac in EXAMPLE_DATA]


def test_normalization():
    matcher = NameMatcher(MockUserDataProvider())

    for expected in EXAMPLE_DATA.values():
        assert expected in matcher.normalized_names, f"Name {expected} was not found in normalized name list {matcher.normalized_names}"
