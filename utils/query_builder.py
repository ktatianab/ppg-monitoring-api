from typing import Optional
from sqlalchemy.orm import Query


def apply_query_filter(db_query: Query, model, query: Optional[str]) -> Query:
    """
    Applies filters from query parameter.

    Supported:
    ?query=field:value
    ?query=field:value,field2:value2
    ?query=field__gte:value
    """

    if not query:
        return db_query

    filters = query.split(",")

    for filter_item in filters:
        if ":" not in filter_item:
            continue

        field_expr, value = filter_item.split(":", 1)

        if "__" in field_expr:
            field_name, operator = field_expr.split("__", 1)
        else:
            field_name = field_expr
            operator = "eq"

        if not hasattr(model, field_name):
            continue

        column = getattr(model, field_name)

        if value == "":
            value = None

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
            values = value.split("|")
            db_query = db_query.filter(column.in_(values))

    return db_query


def apply_ordering(
    db_query: Query,
    model,
    order_by: Optional[str],
    sort: Optional[str]
) -> Query:
    """
    Applies orderBy and sort parameters.

    Supported:
    ?orderBy=value&sort=asc
    ?orderBy=value&sort=desc
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
    Applies limit and offset parameters.

    Supported:
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
    Applies query, ordering and pagination to a SQLAlchemy query.
    """

    db_query = apply_query_filter(db_query, model, query)
    db_query = apply_ordering(db_query, model, order_by, sort)
    db_query = apply_pagination(db_query, limit, offset)

    return db_query