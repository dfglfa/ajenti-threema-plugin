

import csv
import io
import logging
import unicodedata

STANDARD_THREEMA_PREFIX = "dfg"

def replaceUmlauteAndSz(name):
    return name.replace("ä", "ae") \
        .replace("ö", "oe") \
        .replace("ü", "ue") \
        .replace("Ä", "Ae") \
        .replace("Ö", "Oe") \
        .replace("Ü", "Ue") \
        .replace("ß", "ss")


def formatName(firstname, lastname):
    return f"{formatLastname(lastname)}{formatFirstname(firstname)}"


def formatFirstname(firstname):
    return firstname.split()[0]


def formatLastname(lastname):
    return lastname.replace(' ', '')


def sanitizeName(firstname, lastname):
    fn, ln = map(replaceUmlauteAndSz, [firstname, lastname])

    nfkd_form = unicodedata.normalize(
        'NFKD', f"{''.join(ln.split())}{fn.split()[0]}")
    return nfkd_form.encode('ASCII', 'ignore').decode(
        "utf-8").replace("-", "")


def normalizeName(formattedName, className):
    """
    A normalized name contains the class as prefix, followed by an underscore
    and then <lastname><firstname(s)> with capitalized first letters, e.g. 
    "3II_MuellerPeterHansi" for Peter Hansi Müller in the 3ème II.
    """

    if className.lower() in ("teachers", "teacher", "lehrer"):
        return formattedName

    if className not in CLASS_TO_LEVEL.keys():
        classNameCaseInsensitive = [
            c for c in CLASS_TO_LEVEL.keys() if c.lower() == className.lower()]
        if len(classNameCaseInsensitive) == 1:
            className = classNameCaseInsensitive[0]
        elif className in NONSTANDARD_CLASS_NAMES:
            className = NONSTANDARD_CLASS_NAMES[className]
        else:
            # Last chance: nonstandard name, e.g. "5I" instead of "5eI"
            nonstandardClassMatchCaseInsensitive = [
                c for c in NONSTANDARD_CLASS_NAMES.keys() if c.lower() == className.lower()]
            if len(nonstandardClassMatchCaseInsensitive) == 1:
                className = NONSTANDARD_CLASS_NAMES[nonstandardClassMatchCaseInsensitive[0]]
            else:
                logging.warn(
                    f"Cannot find match or correction for class name {className}")

    return f"{className}_{formattedName}"


def normalizeClassName(cls):
    cl = cls.lower()
    for k in CLASS_TO_LEVEL:
        if k.lower() == cl:
            return k
    return cls


def readRecordsFromCSV(csvData):
    records = []
    try:
        reader = csv.DictReader(io.StringIO(csvData), delimiter=";")
        for record in reader:
            records.append(
                {"firstName": record["Prenom"], "lastName": record["Nom"], "class": record["Classe"]})
    except Exception as ex:
        logging.error(
            f"Error while parsing CSV file: {ex}, record was {record}")
    return records


NONSTANDARD_CLASS_NAMES = {"6I": "6eI", "6II": "6eII", "5I": "5eI",
                           "5II": "5eII", "4I": "4eI", "4II": "4eII", "3I": "3eI", "3II": "3eII"}

CLASS_TO_LEVEL = {
    "5a": 5,
    "5b": 5,
    "6a": 6,
    "6b": 6,
    "7a": 7,
    "7b": 7,
    "8a": 8,
    "8b": 8,
    "9a": 9,
    "9b": 9,
    "6eI": 6,
    "6eII": 6,
    "5eI": 7,
    "5eII": 7,
    "4eI": 8,
    "4eII": 8,
    "3eI": 9,
    "3eII": 9,
    "2L1": 10,
    "2L2": 10,
    "2ES": 10,
    "2S1": 10,
    "2S2": 10,
    "1L1": 11,
    "1L2": 11,
    "1ES": 11,
    "1SMP": 11,
    "1SBC1": 11,
    "1SBC2": 11,
    "TL1": 12,
    "TL2": 12,
    "TES": 12,
    "TSMP": 12,
    "TSBC1": 12,
    "TSBC2": 12,
}


def getClassLevel(className):
    return CLASS_TO_LEVEL.get(className)


def getClassDifference(cl1, cl2):
    return CLASS_TO_LEVEL.get(cl1, 100) - CLASS_TO_LEVEL.get(cl2, -100)
