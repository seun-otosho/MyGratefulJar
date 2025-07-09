from fasthtml.common import *
# from fasthtml.xtend import Form, A

from config.pages import base_template


def create_search_page(query="", results=None):
    """Create search results page in FastHTML"""
    content = Div(
        H1("Search"),
        Form(
            Input(
                type="text",
                placeholder="Search...",
                name="query",
                value=query,
                cls="search-input"
            ),
            Button("Search", type="submit", cls="search-button"),
            action="/search/",
            method="get",
            cls="search-form"
        ),
        Div(
            H2("Search Results") if query else "",
            Div(
                [Div(
                    H3(A(result.title, href=result.url)),
                    P(result.description or ""),
                    cls="search-result"
                ) for result in (results or [])]
            ) if results else P("No results found." if query else ""),
            cls="search-results"
        ),
        cls="search-page"
    )

    return base_template(
        title=f"Search{' - ' + query if query else ''}",
        body_class="template-searchresults",
        content=content
    )
