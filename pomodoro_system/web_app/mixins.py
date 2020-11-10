from typing import List, Mapping, Optional, Union

from flask import g, request
from foundation.interfaces import Paginator
from pony.orm import Optional as ORMOptional
from pony.orm import Required, desc
from pony.orm.core import Query  # noqa
from web_app.utils import load_int_query_parameter


class PaginatedQueryMixin:
    @staticmethod
    def get_paginator() -> Optional[Paginator]:
        if not request:
            return

        page = load_int_query_parameter(request.args.get("page"))
        page_size = load_int_query_parameter(request.args.get("page_size"))
        prepared_paginator = Paginator(page=page, page_size=page_size or Paginator.page_size)

        if prepared_paginator.is_usable():
            return prepared_paginator
        return None

    def get_paginated_query(self, query: Query) -> Query:
        if not query:
            return query

        paginator = self.get_paginator()
        if paginator:
            return query.page(paginator.page, paginator.page_size)
        return query


class SortedQueryMixin:
    @staticmethod
    def get_sort_params(
        available_sort_params_mapping: Mapping[str, Union[ORMOptional, Required]]
    ) -> List[Union[ORMOptional, Required]]:

        if not request:
            return []

        params_list = request.args.getlist("sort")

        valid_sort_params = list(
            filter(lambda param: param.lstrip("-").lower() in available_sort_params_mapping, params_list)
        )
        mapped_sort_fields = list(
            map(
                lambda param: desc(available_sort_params_mapping[param.lstrip("-")])
                if param.startswith("-")
                else available_sort_params_mapping[param],
                valid_sort_params,
            )
        )

        return mapped_sort_fields

    def get_sorted_query(self, query: Query) -> Query:
        if not query:
            return query

        if g:
            available_sort_params_mapping = getattr(g, "available_sort_params_mapping", {})
        else:
            available_sort_params_mapping = {}

        sort_params = self.get_sort_params(available_sort_params_mapping)

        if sort_params:
            return query.order_by(*sort_params)
        return query
