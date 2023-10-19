import pytest

from .utils import formatName, normalizeName, normalizeClassName
from .namematcher import NameMatcher


EXAMPLE_DATA = {("Mueller", "Lisa", "tes"): "TES_MuellerLisa",
                ("Meier", "Rainer", "5eII"): "5eII_MeierRainer",
                ("Maier", "Clara", "2ES"): "2ES_MaierClara",
                ("Fährmann", "Anaïs-Dörte", "8b"): "8b_FährmannAnaïs-Dörte",
                ("Ruß-Mœllerû", "Brìt", "3eII"): "3eII_Ruß-MœllerûBrìt",
                ("Müller", "Hermine", "teachers"): "MüllerHermine"}


@pytest.fixture
def matcher():
    return NameMatcher(MockUserDataProvider())


class MockUserDataProvider():
    def getUserData(self):
        return [{"sn": sn, "givenName": gn, "sophomorixAdminClass": ac,
                 "formattedName": formatName(gn, sn),
                 "cls": normalizeClassName(ac),
                 "normalizedName": normalizeName(formatName(gn, sn), ac)} for sn, gn, ac in EXAMPLE_DATA]


class TestNamematcher():
    def test_normalization(self, matcher: NameMatcher):
        for expected in EXAMPLE_DATA.values():
            assert expected in matcher.normalized_names, f"Name {expected} was not found in normalized name list {matcher.normalized_names}"

    def test_nameExtraction(self, matcher: NameMatcher):
        res = matcher._extractStudentName("3IIMaierClara")
        assert res == "MaierClara"

    def test_exact_match_for_class_change(self, matcher: NameMatcher):
        res = matcher.findMatches("1ES_MuellerLisa")
        assert len(res) == 1
        assert res[0][0] == "TES_MuellerLisa"
        assert res[0][1] == "TES"

    def test_exact_match_for_class_change_with_old_spelling(self, matcher: NameMatcher):
        res = matcher.findMatches("3IIMaierClara")
        assert len(res) == 1
        assert res[0][0] == "2ES_MaierClara"
        assert res[0][1] == "2ES"

    def test_fuzzy_match_for_wrong_spelling(self, matcher: NameMatcher):
        res = matcher.findMatches("8b_FährmannAnais-Doerte")
        assert len(res) == 1
        assert res[0][0] == "8b_FährmannAnaïs-Dörte"
        assert res[0][1] == "8b"

    def test_fuzzy_match_for_missing_underscore(self, matcher: NameMatcher):
        res = matcher.findMatches("TESMuellerLisa")
        assert len(res) == 1
        assert res[0][0] == "TES_MuellerLisa"
        assert res[0][1] == "TES"

    def test_no_fuzzy_match_for_different_firstname(self, matcher: NameMatcher):
        res = matcher.findMatches("5eII_MeierReinhold")
        assert len(
            res) == 0, f"No matches should be found here, but found {res}"
