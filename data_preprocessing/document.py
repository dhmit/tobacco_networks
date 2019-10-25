from name_disambiguation import Person
import name_preprocessing as pp
from pathlib import Path

class Document:
    """

    """
    def __init__(self, tid="", title="", au=[], rc=[], year=-1, date, doc_type, pages,
                 text):
        self.tid = tid
        self.title = title
        self.au = au
        self.rc = rc
        self.year = year
        self.date = date
        self.doc_type = doc_type
        self.pages = pages
        self.text = text

    def __repr__(self):
        return f'{self.tid}, {self.title}, {self.au}, {self.rc}, {self.year}, {self.date},' \
               f'{self.doc_type}, {self.pages}'

def load_docs_csv(path):
    df = pp.load_documents_to_dataframe(path)
    documents = []
    for _, row in df.iterrows():
        documents.append(Document(tid=row['tid'],title=row['title'], au=row['au'], rc=row['rc'],
                                  year=int(row['year']), date=row['date'], doc_type=row['doc_type'],
                                  pages=row['pages'], text=row['text']))
    return documents

def get_au_and_rc_by_document(path) -> list:
    """
    Creates a list of documents such that each element consists of a dict with keys
    'au', 'au_org', 'au_person'

    >>> authors_by_docs = get_au_and_rc_by_document()
    >>> authors_by_docs[0]
    {'au': '', 'au_org': '', 'au_person': 'BOWLING,JC'}

    :return: list
    """

    df = load_documents_to_dataframe(path)
    authors_by_docs = []
    for _, row in df.iterrows():
        authors_by_docs.append({
            'au': parse_column_person(row['au']),
            'au_org': parse_column_org(row['au_org']),
            'au_person': parse_column_person(row['au_person'])
        })
    recipients_by_docs = []
    for _, row in df.iterrows():
        recipients_by_docs.append({
            'rc': parse_column_person(row['rc']),
            'rc_org': parse_column_org(row['rc_org']),
            'rc_person': parse_column_person(row['rc_person'])
        })
    return authors_by_docs, recipients_by_docs




if __name__ == '__main__':
    path = Path('..', 'data', 'name_disambiguation', 'dunn_docs.csv')
    print(load_docs_csv(path))
