"""
The Person class parses raw name strings into Person objects
"""

import copy
import re
import unittest
from collections import Counter

from nameparser import HumanName
from nameparser.config import CONSTANTS
from name_preprocessing import get_clean_org_names

CONSTANTS.titles.remove(*CONSTANTS.titles)


# dict that converts raw organization names to clean, official organization names
RAW_ORG_TO_CLEAN_ORG_DICT = get_clean_org_names()


class Person:
    """A Person object represents information of a person (possibly parsed from raw strings,
    or merged from different strings)

    Attributes:
        last (str): official parsed last name
        first (str): official parsed first name
        middle (str): official parsed middle name
        position (str): most likely organization of the person
        positions (Counter of str): counter of all parsed organizations/extra information (must
                                    be clean official org names; can be in lower case)
        aliases (list of str): list of raw names that correspond to the person
        count (int): number of times the alias appeared in the data
    """
    def __init__(self, name_raw=None, last='', first='', middle='',       # pylint: disable=R0913
                 position='not calculated', positions=None, aliases=None, count=1):
        """
        Returns a person object
        :param name_raw: raw string for the name (str)
        :param last: official parsed last name (if known) (str)
        :param first: official parsed first name (if known) (str)
        :param middle: official parsed middle name (if known) (str)
        :param position: official organization (if known; default is "not calculated") (str)
        :param positions: compilation of organizations/other information (if known) (Counter of str)
        :param aliases: list of raw strings that correspond to this person object (if known) (
        list of str)
        :param count: number of times the alias appeared in the data (int)
        """

        # if raw name is given, parse it using parse_raw_name() to get first, middle, last,
        # and positions
        if name_raw:
            first, middle, last, positions = self.parse_raw_name(name_raw, count)

        # initialize positions as an empty Counter if it is not given
        if positions is None:
            positions = Counter()

        # by default, the raw name is an alias of the person
        # (we're changing the first/middle names based on new information, so keeping the original
        # name as an alias is important
        if aliases is None:
            if name_raw is None:
                aliases = []
            else:
                aliases = [name_raw]

        # set last, first, middle, position, positions: all converted to upper case
        # set aliases and count
        self.last = last.upper()
        self.first = first.upper()
        self.middle = middle.upper()
        self.position = position
        # remove periods and convert to upper case
        if isinstance(positions, Counter):
            self.positions = positions
        else:
            # initialize positions as a Counter
            self.positions = Counter()
            for i in positions:
                cleaned = re.sub(r'\.', '', i)
                self.positions[cleaned.upper()] += count
        self.aliases = aliases
        self.count = count

    def __repr__(self):
        """
        Returns string representation of first, middle, last name, positions,
        and all aliases
        :return: str of first, middle, last, positions, aliases
        """
        str_name = f'{self.first} {self.middle} {self.last}'
        str_name = str_name + ", Position: " + str(self.positions) + ", Aliases: " + \
            str(self.aliases) + ", count: " + str(self.count)
        return str_name

    def __eq__(self, other):
        """
        Compares two person object using hash (which hashes the string of last, first, middle,
        position, positions, aliases, and count)
        :param other: another person object
        :return: bool (if two person objects are the same)
        """
        return \
            self.last == other.last and self.first == other.first\
            and self.middle == other.middle and self.position == other.position\
            and self.positions == other.positions and self.aliases == other.aliases

    def copy(self):
        """
        Copies a person object
        :return: a copied person object
        """
        return Person(last=self.last, first=self.first, middle=self.middle,
                      position=self.position,
                      positions=copy.deepcopy(self.positions),
                      aliases=copy.deepcopy(self.aliases), count=self.count)

    def __hash__(self):
        """
        Hashes the person
        :return: hash (int)
        """
        return hash(f'{self.last} {self.first} {self.middle} {self.positions} {self.aliases}')

    def stemmed(self):
        """
        Returns only the official name ("LAST FIRST MIDDLE") of the person
        :return: str of official name
        """
        return f'{self.last} {self.first} {self.middle}'

    def set_likely_position(self):
        """
        Calculates and sets position as the organization with the highest number of count
        :return: None
        """
        likely_position = self.positions.most_common(1)[0][0]
        self.position = likely_position

    @staticmethod
    def remove_privlog_info(name_raw):
        """
        :param name_raw: the raw name alias
        :return: name_raw with privlog info tag removed
        """
        # remove privlog info, e.g. 'Temko, Stanley L [Privlog:] TEMKO,SL'. It confuses
        # the name parser
        privlog_id = name_raw.find('[Privlog:]')
        if privlog_id == 0:
            return name_raw[privlog_id:]
        elif privlog_id > 0:
            return name_raw[:name_raw.find('[Privlog:]')]
        else:
            return name_raw

    @staticmethod
    def parse_raw_name(name_raw: str, count: int) -> (str, str, str, Counter):
        """
        Parses a (usually messy) raw name and returns
        first, middle, last names and a set of extracted positions

        :param name_raw: str
        :param count: int
        :return: str, str, str, Counter (first name, middle name, last name, positions Counter)
        """
        name_raw = Person.remove_privlog_info(name_raw)
        # position is often attached with a dash,
        # e.g. 'BAKER, T E - NATIONAL ASSOCIATION OF ATTORNEYS'
        if name_raw.find(" - ") > -1 and len(name_raw.split(' - ')) == 2:
            name_raw, extracted_position = name_raw.split(" - ")
            extracted_positions = [extracted_position.strip()]
        else:
            extracted_positions = []

        # extract positions in parens e.g. Henson, A (Chadbourne & Park)
        paren_positions = re.findall(r'\([^(]+\)', name_raw)
        for position in paren_positions:
            extracted_positions.append(position.strip(',#() '))
            name_raw = name_raw.replace(position, '')

        # Search for known raw_org strings in name_raw, extract them as positions if necessary
        name_raw, new_positions = Person.extract_raw_org_names_from_name(name_raw)
        extracted_positions += new_positions

        # delete any leftover hashtags
        name_raw = name_raw.strip(' #')

        # Delete dashes between last name and initials
        # DUNN-W -> Dunn W
        if name_raw[-2] == '-':
            name_raw = name_raw[:-2] + " " + name_raw[-1:]
        # DUNN-WL -> DUNN WL
        if len(name_raw) > 2 and name_raw[-3] == '-':
            name_raw = name_raw[:-3] + " " + name_raw[-2:]

        # Parse current string using HumanName
        name = HumanName(name_raw)

        # e.g. Dunn W -> parsed as last name W. -> switch first/last
        if len(name.last) <= 2 < len(name.first):
            name.first, name.last = name.last, name.first

        # remove periods from initials
        if len(name.first) == 2 and name.first[1] == '.':
            name.first = name.first[0]
        if len(name.middle) == 2 and name.middle[1] == '.':
            name.middle = name.middle[0]

        # If first name is length 2 (Teague, CE), the two letters are most likely initials.
        if len(name.first) == 2:
            name.middle = name.first[1].upper()
            name.first = name.first[0].upper()

        # If first and middle initials have periods but not spaces -> separate, e.g. "R.K. Teague"
        if re.match(r'[a-zA-Z]\.[a-zA-Z]\.', name.first):
            name.middle = name.first[2]
            name.first = name.first[0]

        name.last = name.last.capitalize()
        name.first = name.first.capitalize()
        name.middle = name.middle.capitalize()

        # if multiple names are passed, they often end up in the middle name
        # e.g. 'Holtzman, A.,  Murray, J. ,  Henson, A.  -> only allow one comma or set to empty
        if name.middle.count(',') > 1:
            name.middle = ''

        if len(name.suffix) > 20 and name.suffix.count('.') > 2:
            name.suffix = ''

        if name.suffix:
            extracted_positions.append(name.suffix)

        # map organization names to clean official names (if they are in the dict) using
        # RAW_ORG_TO_CLEAN_ORG_DICT
        clean_orgs = []
        for raw_org in extracted_positions:
            if raw_org in RAW_ORG_TO_CLEAN_ORG_DICT:
                clean_org = RAW_ORG_TO_CLEAN_ORG_DICT[raw_org]
                if clean_org != '@skip@':
                    clean_orgs.append(clean_org)
            else:
                clean_orgs.append(raw_org)
        extracted_positions = clean_orgs

        # convert mapped positions into a counter
        result_positions = Counter()
        for position in extracted_positions:
            cleaned = re.sub(r'\.', '', position)
            result_positions[cleaned.upper()] += count

        # print(name.first, name.middle, name.last, result_positions)
        return name.first, name.middle, name.last, result_positions

    @staticmethod
    def extract_raw_org_names_from_name(name_raw):
        """
        Finds raw org names like "B&W" in a name string, standarizes them (e.g. to
        "Brown & Williamson," and returns the name without that raw org name

        :param name_raw: str
        :return:
        """
        extracted_positions = []

        for raw_org, clean_org in RAW_ORG_TO_CLEAN_ORG_DICT.items():

            while True:
                search_hit = None
                # this is a bit of an ugly hack to get the last (rather than the first) search hit
                # for a string: we iterate over all matches and the last one gets stored in
                # search_hit
                for search_hit in re.finditer(r'\b' + raw_org + r'\b', name_raw):
                    pass

                if not search_hit:
                    break

                if len(raw_org) >= 3:
                    name_raw = name_raw[0:search_hit.start()] + name_raw[search_hit.end():]
                    if not clean_org == "@skip@":
                        extracted_positions.append(clean_org)

                elif len(raw_org) == 2:
                    name_raw_test = name_raw[0:search_hit.start()] + name_raw[search_hit.end():]

                    # test if deleted, there exists first & middle name
                    name = HumanName(name_raw_test)
                    # if first & middle name do not exist after deletion, the deleted org might
                    # actually be initials, so ignore the match
                    if not name.first and not name.middle:
                        break

                    # last names without middle names ("TEMKO") get interpreted as first names
                    # without last names. Skip those cases
                    if not name.last:
                        break
                    # if not, do extract raw_org
                    extracted_positions.append(clean_org)
                    name_raw = name_raw_test

        name_raw = name_raw.strip(', ')
        return name_raw, extracted_positions


class TestNameParser(unittest.TestCase):
    """Tests name parsing (parse_raw_name) of the Person class
    Attributes:
        test_raw_names: dict that corresponds raw names (str) to the expected Person object
    """
    # TODO: fix it so that all tests run even if the first assertion fails
    def setUp(self):
        self.test_raw_names = {
        }

    # Not sure what the correct parsing is!
    # This one breaks. But I don't think it can be avoided.
    # >> > n = Person('Holtz, Jacob Alexander, Jacob & Medinger')
    # >> > n.last, n.first, n.middle, " ".join(n.positions).upper()
    # ('Holtz', '', '', 'JACOB ALEXANDER, JACOB & MEDINGER')

    def test_parse_name_1(self):
        # Also test Person constructor: use list as positions
        self.assertEqual(Person(last="Teague", first="C", middle="E", positions=["JR"],
                                aliases=["TEAGUE CE JR"]),
                         Person(name_raw="TEAGUE CE JR"))

    def test_parse_name_2(self):
        # Also test Person constructor: use Counter as positions
        self.assertEqual(Person(last="Teague", first="C", middle="E", positions=Counter(["JR"]),
                                aliases=["teague ce jr"]),
                         Person(name_raw="teague ce jr"))

    def test_parse_name_3(self):
        # TODO parse JR & PHD in positions into two separate strings
        # (currently parse them together, which is suboptimal but acceptable)
        self.assertEqual(Person(last="Teague", first="Claude", middle="Edward",
                                positions={"JR", "PHD"},
                                aliases=["Teague, Claude Edward, Jr., Ph.D."]),
                         Person(name_raw="Teague, Claude Edward, Jr., Ph.D."))

    def test_parse_name_4(self):
        # Test parsing of dashes
        self.assertEqual(Person(last="Baker", first="T", middle="E",
                                positions={"NATIONAL ASSOCIATION OF ATTORNEYS GENERAL"},
                                aliases=["BAKER, T E - NATIONAL ASSOCIATION OF ATTORNEYS GENERAL"]
                                ),
                         Person(name_raw="BAKER, T E - NATIONAL ASSOCIATION OF ATTORNEYS GENERAL"))

    def test_parse_name_5(self):
        self.assertEqual(Person(last="Baker", first="C", middle="J", positions={},
                                aliases=["BAKER-cj"]),
                         Person(name_raw="BAKER-cj"))

    def test_parse_name_6(self):
        # Not specify positions: test to make sure Person constructor can handle no data
        # Here we assume for "Baker, JR", it is more likely that JR are initials and not junior
        self.assertEqual(Person(last="Baker", first="J", middle="R", aliases=["Baker, JR"]),
                         Person(name_raw="Baker, JR"))

    def test_parse_name_7(self):
        # Test if parser ignores special characters
        self.assertEqual(Person(last="Dunn", first="W", middle="L", aliases=["DUNN WL #"]),
                         Person(name_raw="DUNN WL #"))

    def test_parse_name_8(self):
        self.assertEqual(Person(last="Dunn", first="W", middle="L", aliases=["Dunn, W. L."]),
                         Person(name_raw="Dunn, W. L."))

    def test_parse_name_9(self):
        self.assertEqual(Person(last="Temko", first="S", middle="L",
                                positions=["COVINGTON & BURLING"],
                                aliases=["TEMKO SL, COVINGTON AND BURLING"]),
                         Person(name_raw="TEMKO SL, COVINGTON AND BURLING"))

    def test_parse_name_10(self):
        # Test if Privlog and information after it is disregarded
        self.assertEqual(Person(last="Temko", first="Stanley", middle="L",
                                aliases=["Temko, Stanley L [Privlog:] TEMKO,SL"]),
                         Person(name_raw="Temko, Stanley L [Privlog:] TEMKO,SL"))

    def test_parse_name_11(self):
        self.assertEqual(Person(last="Temko", first="S", middle="L",
                                positions=["Covington & Burling"],
                                aliases=["Temko-SL, Covington & Burling"]),
                         Person(name_raw="Temko-SL, Covington & Burling"))

    def test_parse_name_12(self):
        # Test if info inside parentheses is taken as positions
        self.assertEqual(Person(last="Henson", first="A", middle="",
                                positions=["AMERICAN SENIOR VICE PRESIDENT AND GENERAL COUNSEL"],
                                aliases=["HENSON, A. (AMERICAN SENIOR VICE PRESIDENT AND GENERAL "
                                         "COUNSEL)"]),
                         Person(name_raw="HENSON, A. (AMERICAN SENIOR VICE PRESIDENT AND GENERAL "
                                         "COUNSEL)"))

    def test_parse_name_13(self):
        # Test if
        self.assertEqual(Person(last="Henson", first="A", middle="",
                                positions=["CHADBOURNE, PARK, WHITESIDE & WOLFF"],
                                aliases=["HENSON, A. (CHADBOURNE, PARKE, WHITESIDE & WOLFF, "
                                         "AMERICAN OUTSIDE COUNSEL) (HANDWRITTEN NOTES)"]),
                         Person(name_raw="HENSON, A. (CHADBOURNE, PARKE, WHITESIDE & WOLFF, "
                                         "AMERICAN OUTSIDE COUNSEL) (HANDWRITTEN NOTES)"))

    def test_parse_name_14(self):
        """
        checks to see that a raw name is parsed correctly
        """
        # TODO fix when multiple names are in the same string, not parse remaining name as positions
        # This one does not discard the rest of the names and instead stores in positions
        # (see test_parse_name_14b which correctly handles the situation, when there are more names)
        print("positions: ", Person(name_raw="Holtzman, A.,  Murray, J. ,  Henson, A.").positions)
        self.assertEqual(Person(last="Holtzman", first="A", middle="", positions=[],
                                aliases=["Holtzman, A.,  Murray, J. ,  Henson, A."]),
                         Person(name_raw="Holtzman, A.,  Murray, J. ,  Henson, A."))

    def test_parse_name_14b(self):
        """
        checks to see that a raw name is parsed correctly
        """
        print("positions: ", Person(name_raw="Holtzman, A.,  Murray, J. ,  Henson, A. ,  "
                                    "Pepples, E. ,  Stevens, A. ,  Witt, S.").positions)
        self.assertEqual(Person(last="Holtzman", first="A", middle="", positions=[],
                                aliases=["Holtzman, A.,  Murray, J. ,  Henson, A. ,  "
                                         "Pepples, E. ,  Stevens, A. ,  Witt, S."]),
                         Person(name_raw="Holtzman, A.,  Murray, J. ,  Henson, A. ,  "
                                         "Pepples, E. ,  Stevens, A. ,  Witt, S."))

    def test_parse_name_15(self):
        """
        checks to see that a raw name is parsed correctly
        """
        self.assertEqual(Person(last="Holtz", first="Jacob", middle="",
                                positions=["Jacob & Medinger"],
                                aliases=["Holtz, Jacob, Jacob & Medinger"]),
                         Person(name_raw="Holtz, Jacob, Jacob & Medinger"))

    def test_parse_name_16(self):
        """
        checks to see that a raw name is parsed correctly
        """
        self.assertEqual(Person(last="Proctor", first="D", middle="F",
                                positions=["Johns Hopkins University"],
                                aliases=["PROCTOR DF, JOHNS HOPKINS SCHOOL OF HYGIENE"]),
                         Person(name_raw="PROCTOR DF, JOHNS HOPKINS SCHOOL OF HYGIENE"))

    def test_parse_name_17(self):
        """
        checks to see that a raw name is parsed correctly
        """
        self.assertEqual(Person(last="Smith", first="Andy", middle="B", positions=["JR"],
                                aliases=["Smith, Andy B, J.R."]),
                         Person(name_raw="Smith, Andy B, J.R."))

    def test_parse_name_18(self):
        """
        checks to see that a raw name is parsed correctly
        """
        self.assertEqual(Person(last="Cantrell", first="D", middle="",
                                positions=["BROWN & WILLIAMSON"], aliases=["D Cantrell, B&W"]),
                         Person(name_raw="D Cantrell, B&W"))

    def test_parse_name_19(self):
        """
        checks to see that a raw name is parsed correctly
        """
        self.assertEqual(Person(last="Cantrell", first="A", middle="B",
                                positions=["BROWN & WILLIAMSON"], aliases=["A B Cantrell, BW"]),
                         Person(name_raw="A B Cantrell, BW"))


class TestOrgParser(unittest.TestCase):
    """
    Tests organization parser and extracter in extract_raw_org_names_from_name
    """

    def test_parse_org_1(self):
        self.assertEqual(
            Person.extract_raw_org_names_from_name('TEMKO SL, COVINGTON AND BURLING'),
            ('TEMKO SL', ['Covington & Burling'])
        )

    def test_parse_org_2(self):
        # if an organization could also be name initials, keep the initials
        self.assertEqual(
            Person.extract_raw_org_names_from_name('TEMKO PM'),
            ('TEMKO PM', [])
        )

    def test_parse_org_3(self):
        self.assertEqual(
            Person.extract_raw_org_names_from_name('TEMKO PM, PM'),
            ('TEMKO PM', ['Philip Morris'])
        )

    def test_parse_org_4(self):
        # organizations in @skip@ like UNK (unknown) should be deleted
        self.assertEqual(
            Person.extract_raw_org_names_from_name('TEMKO PM, UNK'),
            ('TEMKO PM', [])
        )

if __name__ == '__main__':
    unittest.main()
