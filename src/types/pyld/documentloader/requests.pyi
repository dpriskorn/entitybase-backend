from pyld.jsonld import (
    JsonLdError as JsonLdError,
    LINK_HEADER_REL as LINK_HEADER_REL,
    parse_link_header as parse_link_header,
)

def requests_document_loader(secure: bool = False, **kwargs): ...
