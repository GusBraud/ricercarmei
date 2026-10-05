from copy import deepcopy

from lxml.builder import E
from lxml.builder import ElementMaker as EM

from utils import get_val, generate_person_attr

MEI_NAMESPACE = "http://www.music-encoding.org/ns/mei"
NSMAP = {None: MEI_NAMESPACE}
MEI = EM(namespace=MEI_NAMESPACE, nsmap=NSMAP)

MAPPING = {
    # Title Statement Mapping
    'fileDesc/titleStmt/title[@type="main"]': 'short_title',
    'fileDesc/titleStmt/composer/persName': 'standardized_name',
    'fileDesc/titleStmt/composer/persName@auth.uri': 'wikidata_id',

    # Source Description Mapping
    'fileDesc/sourceDesc/source/bibl/title': 'source_full_title',
    'fileDesc/sourceDesc/source/bibl/composer/persName': 'standardized_name',
    'fileDesc/sourceDesc/source/bibl/imprint/date': 'publication_date_start',
    'fileDesc/sourceDesc/source/bibl/imprint/settlement': 'fk_publication_city_id',
    'fileDesc/sourceDesc/source/bibl/identifier': 'custom_id_source',

    # Work Mapping
    'workList/work/title': 'short_title',
    'workList/work/creation/date': 'work_creation_start',
    'workList/work/classification/term': 'fk_worktype_id'
}

RESP_STMT = E.respStmt(
   E.corpName(
       E.name("Centre national de la recherche scientifique"),
       E.corpName(
           E.name("UMR 7323, Centre d'études supérieures de la Renaissance"),
           E.corpName(
               E.name("RicercarLab"),
               E.address(
                    E.street("59 rue Néricault Destouches"),
                    E.postBox("BP12050"),
                    E.postCode("37020"),
                    E.settlement("Tours"),
                    E.country("France")
               )
           )
       )
   )
)

PUB_STMT = E.pubStmt(
    E.availability (
        E.useRestrict(
            "© 2026 RicercarLab"
        )
    )
)

EDITION_SOURCES = {
    'modern': {

    },
    'manuscript': {

    },
    'printed': lambda m: E.source(
        E.bibl(
            E.composer(
                E.persName(
                    get_val(m, 'fileDesc/sourceDesc/source/bibl/composer/persName', MAPPING),
                    **generate_person_attr(m, 'fileDesc/sourceDesc/source/bibl/composer/persName', MAPPING)
                )
            ),
            E.title(get_val(m, 'fileDesc/sourceDesc/source/bibl/title', MAPPING), type="main"),
            E.editor(
                E.persName(
                    get_val(m, 'fileDesc/sourceDesc/source/bibl/editor/persName', MAPPING),
                    **generate_person_attr(m, 'fileDesc/sourceDesc/source/bibl/editor/persName', MAPPING)
                )
            ),
            E.imprint(
                E.date(get_val(m, 'fileDesc/sourceDesc/source/bibl/imprint/date', MAPPING)),
                E.settlement(get_val(m, 'fileDesc/sourceDesc/source/bibl/imprint/settlement', MAPPING), 
                             **{
                                 "auth": "Geonames" if get_val(m, 'fileDesc/sourceDesc/source/bibl/imprint/settlement/@auth', MAPPING) == "Geonames" else "",
                                 "auth.uri": get_val(m, 'fileDesc/sourceDesc/source/bibl/imprint/settlement/@authURI', MAPPING)
                             }),
            )
        ),
        recordtype="c"
    )
}

generate_mei = lambda row, edition_type : MEI.mei(
    MEI.meiHead(
        MEI.fileDesc(
            MEI.titleStmt(
                MEI.title(get_val(row, 'fileDesc/titleStmt/title[@type="main"]', MAPPING), type="main"),
                MEI.composer(
                    MEI.persName(
                        get_val(row, 'fileDesc/titleStmt/composer/persName', MAPPING),
                        **generate_person_attr(row, 'fileDesc/titleStmt/composer/persName', MAPPING)
                    )
                ),
                deepcopy(RESP_STMT),
                MEI.funder(
                    MEI.corpName("Centre d'études supérieures de la Renaissance", auth="ROR", auth_uri="https://ror.org/03cv31q28")
                )
            ),
            deepcopy(PUB_STMT),
            MEI.sourceDesc(deepcopy(EDITION_SOURCES[edition_type](row)))
        ), MEI.workList(
            MEI.work(
                MEI.title(get_val(row, 'workList/work/title', MAPPING)),
                MEI.creation(
                    MEI.date(get_val(row, 'workList/work/creation/date', MAPPING))
                ),
                MEI.classification(
                    MEI.term(get_val(row, 'workList/work/classification/term', MAPPING))
                )
            )
        ),
        meiversion="5.1"
    ),
)


