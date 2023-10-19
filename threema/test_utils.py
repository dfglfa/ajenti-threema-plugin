from .utils import getClassDifference, formatName


def test_same_class():
    assert getClassDifference("TES", "TSMP") == 0
    assert getClassDifference("TSMP", "TSBC1") == 0
    assert getClassDifference("TSBC1", "TSBC2") == 0
    assert getClassDifference("TSBC2", "TL1") == 0
    assert getClassDifference("TL1", "TL2") == 0
    assert getClassDifference("1ES", "1SMP") == 0
    assert getClassDifference("1SMP", "1SBC1") == 0
    assert getClassDifference("1SBC1", "1SBC2") == 0
    assert getClassDifference("1SBC2", "1L1") == 0
    assert getClassDifference("1L1", "1L2") == 0
    assert getClassDifference("5a", "5b") == 0
    assert getClassDifference("6a", "6eI") == 0
    assert getClassDifference("7a", "5eI") == 0
    assert getClassDifference("8a", "4eI") == 0
    assert getClassDifference("9a", "3eI") == 0


def test_diffs():
    assert getClassDifference("TES", "5a") == 7
    assert getClassDifference("9a", "6eII") == 3
    assert getClassDifference("1SMP", "7a") == 4


def test_unknown():
    assert getClassDifference("TES", "whatever") > 20
    assert getClassDifference("whatever", "whatever") > 20
    assert getClassDifference("whatever", "TES") > 20


def test_formatName():
    assert formatName("Hans", "Müller") == "MüllerHans"
    assert formatName(
        "Hans Michael", "Müller Berndhausen") == "MüllerBerndhausenHans"
    assert formatName("Gaël-Rüdiger", "von Bayern") == "vonBayernGaël-Rüdiger"
