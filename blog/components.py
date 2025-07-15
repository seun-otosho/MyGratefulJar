from fasthtml.common import *

from themes.nemesis.components import (
    magazine_post_card, pagination_nav, blog_sidebar, get_full_post_content, single_post_hero, post_content_body,
    post_footer_section, post_navigation, related_posts_section, comments_section,
)
from themes.nemesis.meta import sample_posts


def blog_listing():
    """Blog listing page with magazine layout"""
    # Get posts for different sections
    featured_post = next((post for post in sample_posts if post['is_featured']), sample_posts[0])
    gallery_posts = sample_posts[1:6]  # Posts for gallery section
    main_posts = sample_posts[2:]  # Posts for main listing
    popular_posts = sample_posts[:4]  # Popular posts for sidebar

    return [
        # Ad Block
        Div(cls="container fbt-elastic-container mb-5")(
            Div(cls="widget fbt-ad-block")(
                Div(cls="fbt_ad text-center")(
                    Div(cls="widget-content")(
                        A(href="#")(
                            Img(alt="", cls="img-fluid lazyloaded", src="/static/images/horizontal_ad.jpg")
                        )
                    )
                )
            )
        ),
        # Main Content Area
        Div(cls="container fbt-elastic-container")(
            Div(cls="row justify-content-center")(
                # Main Content
                Div(cls="fbt-main-wrapper col-lg-8 mb-5 mb-lg-0")(
                    Div(id="main-wrapper")(
                        Div(cls="main-section", id="main_content")(
                            Div(cls="fbt-sep-title")(
                                H4(cls="title title-heading-left")("Recent posts"),
                                Div(cls="title-sep-container")(
                                    Div(cls="title-sep sep-double")
                                )
                            ),
                            Div(cls="blog-posts fbt-index-post-wrap")(
                                *[magazine_post_card(post) for post in main_posts]
                            ),
                            pagination_nav()
                        )
                    )
                ),
                # Sidebar
                blog_sidebar(featured_post, popular_posts)
            )
        )
    ]


def post_detail(post_id: int):
    """Individual post page with full template"""
    post = next((post for post in sample_posts if post['id'] == post_id), None)
    if not post:
        return "Post not found", 404

    # Get full content for this post
    content_data = get_full_post_content(post_id)

    return [

        Div(cls="blog-posts fbt-item-post-wrap")(
            Div(cls="blog-post fbt-item-post")(
                # Hero section
                single_post_hero(post),
                # Post content
                Div(cls="row justify-content-center")(
                    Div(cls="col-xl-8 col-lg-9")(
                        Div(cls="mt-n5")(
                            post_content_body(content_data)
                        )
                    )
                ),
                # Post footer with categories and sharing
                post_footer_section(post, content_data),
                # Post navigation (prev/next)
                post_navigation(post_id),
                # Related posts
                related_posts_section(post_id)
            )
        ),
        # Comments section
        Div(cls="row justify-content-center")(
            Div(cls="col-xl-8 col-lg-9")(
                comments_section(post_id)
            )
        )

    ]
