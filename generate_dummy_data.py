import sys
from threema.utils import CLASS_TO_LEVEL, normalizeName, sanitizeName
from random import choice

FIRSTNAMES = ["Jörg-Rüdiger", "Zoé", "Anaïs-Clémence", "Pétér-Gerhard", "Rainer", "Bernd-Bartholomäus",
              "Clarissa-Elsbeth", "Rita", "Petra", "Gerda", "Reinhold", "Burkardt", "Therése", "Claudio", "Brunhilde-Bernadette"]
LASTNAMES = ["von Müller-Lüdenscheidt", "Meier-Vorfelder", "Müller", "Meier", "Schmitt",
             "Schmidt", "Trézegue", "Blüthenweiß", "von Petermann", "Dreyfuß", "Barfuß-Gelb"]


num_students = int(sys.argv[1]) if len(sys.argv) == 2 else 50


def get_random_student():
    return choice(FIRSTNAMES), choice(LASTNAMES), choice(list(CLASS_TO_LEVEL.keys()))


with open("ent_dummy_data.csv", "w") as ENT, open("threema_dummy_data.csv", "w") as THREEMA:
    ENT.write("Centre,Classe,Nom,Prenom,Genre,Date,Regime,Bourse,Langue,Transport,Religion,Medical,Redoublant,,,,,,,,,\n")

    generated_names = set([])
    for _ in range(num_students):
        while True:
            student = get_random_student()
            if student not in generated_names:
                generated_names.add(student)
                break

        firstname, lastname, classname = student
        ENT.write(",".join(["Deutsch-französische Sekundarstufe II", classname, lastname, firstname, "H", "2007-01-01",
                  "EA", "N", "fr", "Keine", "Paris", "Frankreich-Deutschland", "foo@bar.de", "7", "", "", "", "", "", "", "", ""]) + "\n")

        THREEMA.write(",".join([normalizeName(sanitizeName(
            firstname, lastname), classname), "1234567!", lastname, firstname]) + "\n")
