
from typing import Optional
import sqlalchemy
from sqlalchemy.orm import Query
 
 
def _cast_value(column, value: str):
    """
    Castea el valor string al tipo correcto según la columna del modelo.
    """
    try:
        col_type = type(column.property.columns[0].type)
 
        if col_type in (sqlalchemy.Integer,):
            return int(value)
 
        elif col_type in (sqlalchemy.Float, sqlalchemy.Numeric):
            return float(value)
 
        elif col_type in (sqlalchemy.Boolean,):
            return value.lower() in ("true", "1", "yes")
 
    except (AttributeError, ValueError):
        pass
 
    return value
 
 
def _apply_operator(db_query: Query, column, operator: str, value) -> Query:
    """
    Aplica un operador de comparacion sobre una columna.
    """
    if operator == "eq":
        db_query = db_query.filter(column == value)
    elif operator == "gt":
        db_query = db_query.filter(column > value)
    elif operator == "lt":
        db_query = db_query.filter(column < value)
    elif operator == "gte":
        db_query = db_query.filter(column >= value)
    elif operator == "lte":
        db_query = db_query.filter(column <= value)
    elif operator == "contains":
        db_query = db_query.filter(column.contains(value))
    elif operator == "in":
        values = [_cast_value(column, v) for v in value.split("|")]
        db_query = db_query.filter(column.in_(values))
 
    return db_query
 
 
def _resolve_relationship(model, fk_field: str):
    """
    Dado un modelo y un nombre de campo FK (ej: "id_session"),
    devuelve (relationship_attr, related_model) o (None, None).
 
    Estrategia 1: convencion id_X -> relationship "X"
    Estrategia 2: busqueda por columnas FK en el mapper
    """
    relationship_name = fk_field[3:] if fk_field.startswith("id_") else fk_field
 
    if hasattr(model, relationship_name):
        rel_attr = getattr(model, relationship_name)
        try:
            related_model = rel_attr.property.mapper.class_
            return rel_attr, related_model
        except AttributeError:
            pass
 
    try:
        mapper = sqlalchemy.inspect(model)
        for rel in mapper.relationships:
            local_cols = [col.key for col in rel.local_columns]
            if fk_field in local_cols:
                rel_attr = getattr(model, rel.key)
                related_model = rel.mapper.class_
                return rel_attr, related_model
    except Exception:
        pass
 
    return None, None
 
 
def _apply_nested_filter(db_query: Query, model, field_expr: str, operator: str, value) -> Query:
    """
    Maneja filtros anidados con uno o mas niveles de punto.
 
    1 nivel:  ?query=id_session.id_user:1
                JOIN monitoring_session, filtrar por id_user
 
    2 niveles: ?query=id_session.id_user.id_city:2
                JOIN monitoring_session, JOIN app_user, filtrar por id_city
 
    3 niveles: ?query=id_session.id_user.id_city.id_country:3
                JOIN monitoring_session, JOIN app_user, JOIN city, filtrar por id_country
    """
    parts = field_expr.split(".")
    fk_chain = parts[:-1]
    final_field = parts[-1]
 
    current_model = model
 
    for fk_field in fk_chain:
        rel_attr, related_model = _resolve_relationship(current_model, fk_field)
 
        if rel_attr is None:
            return db_query
 
        db_query = db_query.join(rel_attr)
        current_model = related_model
 
    if not hasattr(current_model, final_field):
        return db_query
 
    final_column = getattr(current_model, final_field)
 
    if value is not None and operator != "in":
        value = _cast_value(final_column, value)
 
    db_query = _apply_operator(db_query, final_column, operator, value)
 
    return db_query
 
 
def apply_query_filter(db_query: Query, model, query: Optional[str]) -> Query:
    """
    Aplica filtros desde el parametro query.
 
    Soportado:
      ?query=field:value                         -> filtro simple
      ?query=field:value,field2:value2           -> multiples filtros (AND)
      ?query=field__gte:value                    -> operadores (gt, lt, gte, lte, contains, in)
      ?query=fk.campo:value                      -> JOIN un nivel
      ?query=fk1.fk2.campo:value                -> JOIN dos niveles
      ?query=fk1.fk2.fk3.campo:value            -> JOIN N niveles
    """
 
    if not query:
        return db_query
 
    filters = query.split(",")
 
    for filter_item in filters:
        filter_item = filter_item.strip()
        if ":" not in filter_item:
            continue
 
        field_expr, value = filter_item.split(":", 1)
 
        if "__" in field_expr:
            field_name, operator = field_expr.split("__", 1)
        else:
            field_name = field_expr
            operator = "eq"
 
        if value == "":
            value = None
 
        if "." in field_name:
            db_query = _apply_nested_filter(db_query, model, field_name, operator, value)
            continue
 
        if not hasattr(model, field_name):
            continue
 
        column = getattr(model, field_name)
 
        if value is not None and operator != "in":
            value = _cast_value(column, value)
 
        db_query = _apply_operator(db_query, column, operator, value)
 
    return db_query
 
 
def apply_ordering(
    db_query: Query,
    model,
    order_by: Optional[str],
    sort: Optional[str]
) -> Query:
    """
    Aplica los parametros orderBy y sort.
 
    Soportado:
      ?orderBy=field&sort=asc
      ?orderBy=field&sort=desc
    """
 
    if not order_by:
        return db_query
 
    if not hasattr(model, order_by):
        return db_query
 
    column = getattr(model, order_by)
 
    if sort == "desc":
        return db_query.order_by(column.desc())
 
    return db_query.order_by(column.asc())
 
 
def apply_pagination(
    db_query: Query,
    limit: Optional[int],
    offset: Optional[int]
) -> Query:
    """
    Aplica los parametros limit y offset.
 
    Soportado:
      ?limit=5&offset=10
    """
 
    if offset is not None:
        db_query = db_query.offset(offset)
 
    if limit is not None:
        db_query = db_query.limit(limit)
 
    return db_query
 
 
def apply_get_query_params(
    db_query: Query,
    model,
    query: Optional[str] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    order_by: Optional[str] = None,
    sort: Optional[str] = "asc"
) -> Query:
    """
    Aplica filtro, ordenamiento y paginacion a un query de SQLAlchemy.
    Orden: filtro -> ordenamiento -> paginacion
    """
 
    db_query = apply_query_filter(db_query, model, query)
    db_query = apply_ordering(db_query, model, order_by, sort)
    db_query = apply_pagination(db_query, limit, offset)
 
    return db_query
 