from pydantic import BaseModel, ConfigDict


class PropertyPredicates(BaseModel):
    direct: str
    statement: str
    qualifier: str
    reference: str
    value_node: str | None = None

    model_config = ConfigDict(frozen=True)


class PropertyShape(BaseModel):
    pid: str
    datatype: str
    predicates: PropertyPredicates
    labels: dict[str, dict] = {}
    descriptions: dict[str, dict] = {}

    model_config = ConfigDict(frozen=True)
