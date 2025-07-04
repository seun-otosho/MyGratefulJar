from fasthtml.common import *
from datetime import datetime

# Custom CSS and JS headers to match the original template
custom_hdrs = [
    Link(rel="shortcut icon", href="favicon.ico", type="image/x-icon"),
    Link(href="https://fonts.googleapis.com/css?family=Montserrat:900%7CNunito:400,700%7COswald%7CRoboto", rel="stylesheet"),
    Link(href="./css/animate.min.css", rel="stylesheet", media="screen"),
    Link(href="./css/fonts.css", rel="stylesheet", media="screen"),
    Link(href="./css/bootstrap.min.css", rel="stylesheet", media="screen"),
    Link(href="./css/style.css", rel="stylesheet", media="screen"),
    Script(src="./js/jquery.min.js"),
    Script(src="./js/bootstrap.bundle.min.js"),
    Script(src="./js/plugins.js"),
    Script(src="./js/main.js"),
]

app, rt = fast_app(hdrs=custom_hdrs)

# Sample blog post data (we'll replace this with database later)
sample_posts = [
    {
        "id": 1,
        "title": "Etiam nec enim id mi maximus consequat sed ut tortor.",
        "excerpt": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec facilisis leo et bibendum pretium. Suspendisse li...",
        "author": "fbtemplates",
        "date": "March 08, 2017",
        "image": "./images/img-1.jpg",
        "is_featured": True,
        "is_video": False,
        "category": "Design"
    },
    {
        "id": 2,
        "title": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        "excerpt": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec facilisis leo et bibendum pretium. Suspendisse li...",
        "author": "fbtemplates",
        "date": "June 19, 2019",
        "image": "./images/img-2.jpg",
        "is_featured": False,
        "is_video": False,
        "category": "Lifestyle"
    },
    {
        "id": 3,
        "title": "Nunc tellus libero, tempus id luctus eget, fermentum.",
        "excerpt": "Donec dolor elit, pellentesque a massa pellentesque, euismod sagittis ipsum. Nullam a diam ac turpis iaculis vu...",
        "author": "fbtemplates",
        "date": "June 05, 2019",
        "image": "./images/img-3.jpg",
        "is_featured": False,
        "is_video": False,
        "category": "Friends"
    },
    {
        "id": 4,
        "title": "The future of news blogger themes. Custom post carousel.",
        "excerpt": "Fames dictumst massa massa, qui sapien per, mauris id sed cubilia suspendisse neque. Proin natoque consectetuer...",
        "author": "fbtemplates",
        "date": "September 13, 2018",
        "image": "./images/img-4.jpg",
        "is_featured": False,
        "is_video": True,
        "category": "Technology"
    },
    {
        "id": 5,
        "title": "Lorem ipsum dolor sit amet. Custom Post Gallery.",
        "excerpt": "Phasellus deserunt. Convallis perspiciatis fusce fermentum accumsan, arcu aliquam, velit venenatis augue proin...",
        "author": "fbtemplates",
        "date": "May 26, 2018",
        "image": "./images/img-5.jpg",
        "is_featured": False,
        "is_video": False,
        "category": "Lifestyle"
    },
    {
        "id": 6,
        "title": "Mihi vero, inquit, placet agi subtilius et pressius.",
        "excerpt": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec facilisis leo et bibendum pretium...",
        "author": "fbtemplates",
        "date": "June 19, 2019",
        "image": "./images/mag-img-18.jpg",
        "is_featured": False,
        "is_video": True,
        "category": "Sport"
    },
    {
        "id": 7,
        "title": "Ne amores quidem sanctos alienos esse.",
        "excerpt": "Donec dolor elit, pellentesque a massa pellentesque, euismod sagittis ipsum...",
        "author": "fbtemplates",
        "date": "June 19, 2019",
        "image": "./images/mag-img-19.jpg",
        "is_featured": False,
        "is_video": False,
        "category": "Business"
    },
    {
        "id": 8,
        "title": "Suspendisse sed tortor eget justo aliquam.",
        "excerpt": "Phasellus deserunt. Convallis perspiciatis fusce fermentum accumsan, arcu aliquam...",
        "author": "fbtemplates",
        "date": "June 19, 2019",
        "image": "./images/mag-img-21.jpg",
        "is_featured": False,
        "is_video": False,
        "category": "Design"
    }
]

def search_overlay():
    """Search overlay component"""
    return Div(
        id="fbt-content-overlay",
        onclick="closeNav()"
    )

def search_form():
    """Search form component"""
    return Form(
        autocomplete="off",
        id="search",
        role="search"
    )(
        Div(cls="input")(
            Input(cls="search", name="search", placeholder="Search...", type="text"),
            Button(cls="submit fa fa-search", type="submit", value="")
        ),
        Button(id="close", type="reset", value="×")
    )

def navbar():
    """Main navigation component"""
    return Nav(cls="navbar navbar-expand-xl navbar-fbt fbt-nav-skin fbt_sticky_nav")(
        Div(cls="container nav-mobile-px clearfix")(
            Div(cls="navbar-brand order-2 order-xl-1 m-auto")(
                A(href="/")(
                    Img(alt="Nemesis", src="./images/logo_nemesis.png")
                )
            ),
            Button(
                cls="navbar-toggler order-1 order-xl-2",
                aria_expanded="false", aria_label="Toggle navigation", data_target="#navbar-menu", data_toggle="collapse",
                type="button"
            )("☰"),
            Div(cls="header-buttons order-3 order-lg-4")(
                Span(cls="fa fa-search navbar-search search-trigger"),
                Span(cls="fbt-sidenav ml-1 active", onclick="openNav()")("☰")
            ),
            Div(cls="collapse navbar-collapse order-4 order-xl-3 clearfix", id="navbar-menu")(
                Ul(cls="navbar-nav m-auto clearfix")(
                    Li(cls="nav-item dropdown")(
                        A(href="#", cls="nav-link dropdown-toggle", aria_haspopup="true", aria_expanded="false", data_toggle="dropdown")("Home"),
                        Div(cls="dropdown-menu")(
                            A(href="/", cls="dropdown-item")("Home 1"),
                            A(href="/blog", cls="dropdown-item")("Blog"),
                        )
                    ),
                    Li(cls="nav-item")(
                        A(href="/contact", cls="nav-link")("Contact")
                    ),
                    Li(cls="nav-item")(
                        A(href="#", cls="nav-link")("Sport")
                    ),
                    Li(cls="nav-item")(
                        A(href="#", cls="nav-link")("Policy")
                    ),
                    Li(cls="nav-item")(
                        A(href="#", cls="nav-link")("Lifestyle")
                    )
                )
            )
        )
    )

def hero_slider(featured_post):
    """Hero slider component with featured post"""
    return Div(cls="slider-container")(
        Div(cls="slider-container-row", id="slider-posts")(
            Div(cls="widget fbt_fp-slider")(
                Div(cls="widget-content")(
                    Div(cls="container")(
                        Div(cls="row align-items-center slider-width")(
                            Div(cls="col-lg-7")(
                                Div(cls="fbt-shape-container")(
                                    Div(cls="fbt-item-thumbnail radius-10")(
                                        A(cls="post-image-link", href=f"/post/{featured_post['id']}")(
                                            Img(alt="", cls="post-thumbnail lazyloaded", src=featured_post['image'])
                                        )
                                    )
                                )
                            ),
                            Div(cls="col-lg-5 mt-4 mt-lg-0")(
                                Div(cls="fbt-shape-title pl-xl-5 pl-lg-4")(
                                    H1(cls="display-4")(
                                        A(href=f"/post/{featured_post['id']}")(featured_post['title'])
                                    ),
                                    Div(cls="post-meta my-4")(
                                        Span(cls="post-author")(featured_post['author']),
                                        Span(cls="post-date published")(featured_post['date'])
                                    ),
                                    A(href=f"/post/{featured_post['id']}")(
                                        Span(cls="fbt_read_more btn btn-primary-slider radius-25 px-5 mt-2")("Keep reading ...")
                                    )
                                )
                            )
                        )
                    )
                )
            )
        )
    )

def blog_post_card(post):
    """Individual blog post card component"""
    video_icon = Span(cls="video-icon")(I(cls="fa fa-play")) if post['is_video'] else ""
    
    return Div(cls="blog-post fbt-index-post card radius-10")(
        Div(cls="fbt-post-thumbnail")(
            A(href=f"/post/{post['id']}")(
                Img(alt="", cls="post-thumbnail lazyloaded", src=post['image'])
            ),
            video_icon
        ),
        Div(cls="fbt-post-caption card-body")(
            H3(cls="post-title h4 card-title")(
                A(href=f"/post/{post['id']}")(post['title'])
            ),
            Div(cls="post-meta")(
                Span(cls="post-author")(A(href="#")(post['author'])),
                Span(cls="post-date published")(post['date'])
            ),
            P(cls="post-excerpt card-text")(post['excerpt'])
        )
    )

def sidebar():
    """Sidebar component"""
    return Div(cls="sidebar-wrapper", id="sidebar-wrapper")(
        Div(cls="sidebar-wrapper__content")(
            Div(cls="navigation-container clearfix")(
                Span(cls="closebtn", onclick="closeNav()")("×")
            ),
            Div(cls="sidebar-top section", id="menu_sidebar")(
                Div(cls="widget LinkList")(
                    Div(cls="widget-content fbt-sidebar--menu")(
                        Ul(cls="list-group")(
                            Li(cls="list-group-item")(A(href="/")("HOME")),
                            Li(cls="list-group-item")(A(href="#")("ABOUT")),
                            Li(cls="list-group-item")(A(href="#")("SERVICES")),
                            Li(cls="list-group-item")(A(href="/contact")("CONTACT")),
                            Li(cls="list-group-item")(A(href="#")("PRIVACY"))
                        )
                    )
                )
            ),
            Div(cls="sidebar section", id="main_sidebar")(
                Div(cls="widget Label")(
                    Div(cls="fbt-sep-title")(
                        H4(cls="title title-heading-left")("Categories"),
                        Div(cls="title-sep-container")(
                            Div(cls="title-sep sep-double")
                        )
                    ),
                    Div(cls="widget-content cloud-label--widget-content")(
                        A(href="#")(Span(cls="badge badge-success py-1 px-2 mb-1")("Business")),
                        A(href="#")(Span(cls="badge badge-success py-1 px-2 mb-1")("Design")),
                        A(href="#")(Span(cls="badge badge-success py-1 px-2 mb-1")("Entertainment")),
                        A(href="#")(Span(cls="badge badge-success py-1 px-2 mb-1")("Lifestyle")),
                        A(href="#")(Span(cls="badge badge-success py-1 px-2 mb-1")("Technology")),
                        A(href="#")(Span(cls="badge badge-success py-1 px-2 mb-1")("Sport"))
                    )
                )
            )
        )
    )

def newsletter_section():
    """Newsletter subscription section"""
    return Div(cls="fbt-bottom-section clearfix", id="fbt_bottom_section")(
        Div(cls="widget FollowByEmail")(
            Div(cls="widget-content")(
                Div(cls="container")(
                    Div(cls="row justify-content-center")(
                        Div(cls="follow-by-email-inner subscriber-form col-lg-10")(
                            Div(cls="card radius-10 p-5")(
                                Div(cls="row justify-content-center align-items-center py-3")(
                                    Div(cls="col-lg-3")(
                                        H2(cls="title h1 mb-4 mb-lg-0 text-center text-lg-left")("Subscribe to our Newsletter")
                                    ),
                                    Div(cls="col-lg-8 pl-lg-4")(
                                        Form(action="#", cls="fbt-email-form", method="post")(
                                            Input(autocomplete="off", cls="follow-by-email-address", name="email", placeholder="Enter your Email", type="email"),
                                            Input(cls="follow-by-email-submit", type="submit", value="Subscribe")
                                        )
                                    )
                                )
                            )
                        )
                    )
                )
            )
        )
    )

def headline_section():
    """Top headline section with navigation and social links"""
    return Div(cls="fbt-headline clearfix", id="headline")(
        Div(cls="container")(
            Div(cls="row align-items-center justify-content-between py-1 py-md-0")(
                Div(cls="col-md-7 left-headline-content")(
                    Div(cls="fbt-left-headline", id="left-headline")(
                        Ul(cls="nav justify-content-center justify-content-md-start")(
                            Li(cls="nav-item")(A(cls="nav-link", href="#")("About")),
                            Li(cls="nav-item")(A(cls="nav-link", href="#")("Services")),
                            Li(cls="nav-item")(A(cls="nav-link", href="/contact")("Contact"))
                        )
                    )
                ),
                Div(cls="col-md-5 right-headline-content")(
                    Div(cls="fbt-right-headline", id="right-headline")(
                        Ul(cls="nav justify-content-center justify-content-md-end social-icons")(
                            Li(cls="nav-item")(A(cls="nav-link", href="#")(I(cls="fa fa-facebook"))),
                            Li(cls="nav-item")(A(cls="nav-link", href="#")(I(cls="fa fa-twitter"))),
                            Li(cls="nav-item")(A(cls="nav-link", href="#")(I(cls="fa fa-instagram"))),
                            Li(cls="nav-item")(A(cls="nav-link", href="#")(I(cls="fa fa-linkedin"))),
                            Li(cls="nav-item")(A(cls="nav-link", href="#")(I(cls="fa fa-youtube-play")))
                        )
                    )
                )
            )
        )
    )

def magazine_navbar():
    """Magazine-style navigation with mega menus"""
    return Nav(cls="navbar navbar-expand-xl navbar-fbt fbt-nav-skin fbt_sticky_nav m-0")(
        Div(cls="container nav-mobile-px clearfix")(
            Div(cls="navbar-brand order-2 order-xl-1 m-auto")(
                A(href="/blog")(
                    Img(alt="Nemesis", src="./images/logo_nemesis.png")
                )
            ),
            Button(
                cls="navbar-toggler order-1 order-xl-2",
                aria_expanded="false", aria_label="Toggle navigation", 
                data_target="#navbar-menu", data_toggle="collapse",
                type="button"
            )("☰"),
            Div(cls="header-buttons order-3 order-lg-4")(
                Span(cls="fa fa-search navbar-search search-trigger"),
                Span(cls="fbt-sidenav ml-1 active", onclick="openNav()")("☰")
            ),
            Div(cls="collapse navbar-collapse order-4 order-xl-3 clearfix", id="navbar-menu")(
                Ul(cls="navbar-nav m-auto clearfix")(
                    Li(cls="nav-item dropdown")(
                        A(href="#", cls="nav-link dropdown-toggle", aria_haspopup="true", aria_expanded="false", data_toggle="dropdown")("Home"),
                        Div(cls="dropdown-menu")(
                            A(href="/", cls="dropdown-item")("Home 1"),
                            A(href="/blog", cls="dropdown-item")("Blog"),
                        )
                    ),
                    Li(cls="nav-item")(
                        A(href="/contact", cls="nav-link")("Contact")
                    ),
                    Li(cls="nav-item")(
                        A(href="/blog", cls="nav-link")("Blog")
                    ),
                    Li(cls="nav-item")(
                        A(href="#", cls="nav-link")("Policy")
                    )
                )
            )
        )
    )

def gallery_section(featured_posts):
    """Gallery section with featured posts"""
    return Div(cls="fbt-gallery bg-light py-5 mt-n5 mb-5")(
        Div(cls="container-fluid fbt-elastic-container fbt-gallery-1 px-lg-5")(
            Div(cls="row px-2")(
                *[gallery_post_card(post) for post in featured_posts[:5]]
            )
        )
    )

def gallery_post_card(post):
    """Individual gallery post card"""
    video_icon = Span(cls="video-icon")(I(cls="fa fa-play")) if post.get('is_video') else ""
    
    return Div(cls="col-lg col-md-6 mb-4 mb-lg-0 px-2")(
        Div(cls="post-item card")(
            Div(cls="fbt-post-thumbnail")(
                A(href=f"/post/{post['id']}")(
                    Img(alt="", cls="post-thumbnail lazyloaded", src=post['image'])
                ),
                video_icon
            ),
            Div(cls="fbt-post-caption")(
                Div(cls="title-caption text-center p-4")(
                    Div(cls="post-meta mb-2")(
                        Span(cls="post-author")(A(href="#")(post['author'])),
                        Span(cls="post-date published")(post['date'])
                    ),
                    H3(cls="post-title")(
                        A(href=f"/post/{post['id']}")(post['title'])
                    )
                )
            )
        )
    )

def magazine_post_card(post):
    """Magazine-style post card for main listing"""
    video_icon = Span(cls="video-icon")(I(cls="fa fa-play")) if post.get('is_video') else ""
    
    return Div(cls="fbt_magazine-blog-post fbt-index-post row align-items-center justify-content-between")(
        Div(cls="col-xl-6 col-md-5")(
            Div(cls="fbt-post-thumbnail")(
                A(href=f"/post/{post['id']}")(
                    Img(alt="", cls="post-thumbnail lazyloaded", src=post['image'])
                ),
                video_icon
            )
        ),
        Div(cls="col-xl-6 col-md-7")(
            Div(cls="fbt-post-caption mt-3 mt-md-0")(
                Span(cls="post-tag index-post-tag")(post.get('category', 'General')),
                H3(cls="post-title")(
                    A(href=f"/post/{post['id']}")(post['title'])
                ),
                Div(cls="post-meta mb-2")(
                    Span(cls="post-author")(A(href="#")(post['author'])),
                    Span(cls="post-date published")(post['date'])
                ),
                P(cls="post-excerpt")(post['excerpt'])
            )
        )
    )

def blog_sidebar(featured_post, popular_posts):
    """Blog sidebar with featured post and popular posts"""
    return Div(cls="fbt-main-sidebar col-lg-4")(
        Div(cls="fbt-main-sidebar__content h-100 pl-lg-3")(
            # Featured Post Widget
            Div(cls="widget FeaturedPost mb-5")(
                Div(cls="fbt-sep-title")(
                    H4(cls="title title-heading-left")("Featured Post"),
                    Div(cls="title-sep-container")(
                        Div(cls="title-sep sep-double")
                    )
                ),
                Div(cls="widget-content")(
                    Div(cls="FeaturedPostContainer")(
                        Div(cls="fbt-item-thumbnail")(
                            A(cls="post-image-link", href=f"/post/{featured_post['id']}")(
                                Img(alt="", cls="post-thumbnail lazyloaded", src=featured_post['image'])
                            )
                        ),
                        Div(cls="fbt-title-section mt-3")(
                            Div(cls="post-meta mb-2")(
                                Span(cls="post-author")(featured_post['author']),
                                Span(cls="post-date published")(featured_post['date'])
                            ),
                            H3(cls="post-title")(
                                A(href=f"/post/{featured_post['id']}")(featured_post['title'])
                            ),
                            P(cls="post-excerpt")(featured_post['excerpt'])
                        )
                    )
                )
            ),
            # Popular Posts Widget
            Div(cls="widget fbt_list_posts mb-5")(
                Div(cls="fbt-sep-title")(
                    H4(cls="title title-heading-left")("Popular Posts"),
                    Div(cls="title-sep-container")(
                        Div(cls="title-sep sep-double")
                    )
                ),
                Div(cls="widget-content")(
                    *[popular_post_item(post) for post in popular_posts]
                )
            )
        )
    )

def popular_post_item(post):
    """Individual popular post item"""
    return Article(cls="post mb-3")(
        Div(cls="post-content media align-items-center")(
            Div(cls="fbt-item-thumbnail clearfix")(
                A(href=f"/post/{post['id']}")(
                    Img(alt="", cls="post-thumbnail lazyloaded", src=post['image'])
                )
            ),
            Div(cls="ml-3 fbt-title-caption media-body")(
                Span(cls="pp-post-tag")(post.get('category', 'General')),
                H3(cls="post-title")(
                    A(href=f"/post/{post['id']}")(post['title'])
                ),
                Div(cls="post-meta")(
                    Span(cls="post-date published")(post['date'])
                )
            )
        )
    )

def contact_hero_section():
    """Contact page hero section with background image"""
    return Div(cls="slider-container")(
        Div(cls="row align-items-center")(
            Div(cls="col-lg-12")(
                Div(cls="fbt-shape-container card shadow-none")(
                    Div(cls="fbt-item-thumbnail radius-10")(
                        Img(alt="Contact Us", cls="post-thumbnail", src="./images/page-img-1.jpg")
                    ),
                    Div(cls="card-img-overlay radius-10")(
                        Div(cls="fbt-page-shape-title d-table w-100")(
                            Div(cls="d-table-cell align-middle")(
                                Div(cls="row justify-content-center")(
                                    Div(cls="col-xl-8 col-lg-9 p-0")(
                                        H1(cls="post-title display-4 text-white text-center")("Contact Us")
                                    )
                                )
                            )
                        )
                    )
                )
            )
        )
    )

def contact_form():
    """Contact form component"""
    return Form(id="fbt-contact-form", cls="contact-form", method="POST", action="/contact")(
        Div(cls="row")(
            Div(cls="col-md-9")(
                Div(cls="form-group")(
                    Label(**{"for": "name"})("Name*"),
                    Input(cls="form-control shadow-none radius-0", id="name", name="name", type="text", required=True)
                )
            ),
            Div(cls="col-md-9")(
                Div(cls="form-group")(
                    Label(**{"for": "email"})("E-mail*"),
                    Input(cls="form-control shadow-none radius-0", id="email", name="email", type="email", required=True)
                )
            ),
            Div(cls="col-md-9")(
                Div(cls="form-group")(
                    Label(**{"for": "website"})("Website"),
                    Input(cls="form-control shadow-none radius-0", id="website", name="website", type="url")
                )
            )
        ),
        Div(cls="row mb-4")(
            Div(cls="col-md-12")(
                Div(cls="form-group")(
                    Label(**{"for": "message"})("Message*"),
                    Textarea(cls="form-control shadow-none radius-0", rows="9", id="message", name="message", required=True)
                )
            )
        ),
        Button(cls="btn btn-success radius-0", type="submit", id="submit-contact")(
            I(cls="fa fa-paper-plane-o mr-2"),
            "Submit Message"
        )
    )

def contact_info_sidebar():
    """Contact information sidebar"""
    return Div(cls="col-xl-3 col-lg-4 pl-lg-5 order-1 order-lg-2")(
        Div(cls="fbt-sep-title")(
            H4(cls="title title-heading-left")("Contact Us"),
            Div(cls="title-sep-container")(
                Div(cls="title-sep sep-double")
            )
        ),
        P(cls="mb-4")(
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
            "Ut porttitor leo vel nulla posuere accumsan. "
            "Suspendisse sed tortor eget justo aliquam euismod. "
            "Morbi ut massa et neque iaculis lacinia a eu..."
        ),
        Div(cls="fbt-contact-info")(
            # Address
            Div(cls="fbt-contact-info-box")(
                Div(cls="fbt-contact-info-box-content")(
                    Div(cls="fbt-sep-title")(
                        H4(cls="title title-heading-left")("Webagency"),
                        Div(cls="title-sep-container")(
                            Div(cls="title-sep sep-double")
                        )
                    ),
                    P("Vouliagmenis Ave 325,", Br(), "Athens CA 17575")
                )
            ),
            # Email
            Div(cls="fbt-contact-info-box")(
                Div(cls="fbt-contact-info-box-content")(
                    Div(cls="fbt-sep-title")(
                        H4(cls="title title-heading-left")("Email Us"),
                        Div(cls="title-sep-container")(
                            Div(cls="title-sep sep-double")
                        )
                    ),
                    P("info@nemesis.com")
                )
            ),
            # Phone
            Div(cls="fbt-contact-info-box")(
                Div(cls="fbt-contact-info-box-content")(
                    Div(cls="fbt-sep-title")(
                        H4(cls="title title-heading-left")("Call Us"),
                        Div(cls="title-sep-container")(
                            Div(cls="title-sep sep-double")
                        )
                    ),
                    P("+123-456-7890")
                )
            )
        )
    )

def pagination_nav(current_page=2, total_pages=3):
    """Pagination navigation"""
    return Div(cls="pagenav", id="blog-pager")(
        Span(cls="showpageOf")(f"{current_page} / {total_pages}"),
        Span(cls="showpage firstpage")(
            A(href="#")(I(cls="fa fa-angle-double-left"))
        ),
        Span(cls="showpage")(
            A(href="#")(I(cls="fa fa-angle-left"))
        ),
        Span(cls="displaypageNum")(A(href="#")("1")),
        Span(cls="page current")("2"),
        Span(cls="displaypageNum")(A(href="#")("3")),
        Span(cls="displaypageNum")(
            A(href="#")(I(cls="fa fa-angle-right"))
        ),
        Span(cls="displaypageNum lastpage")(
            A(href="#")(I(cls="fa fa-angle-double-right"))
        )
    )

def footer():
    """Footer component"""
    return Div(cls="footer-dark pt-4", id="footer-content")(
        Div(cls="container pb-4")(
            Div(cls="row clearfix")(
                Div(cls="col-lg-4")(
                    Div(cls="footer-1", id="footer-1")(
                        Div(cls="logoImage")(
                            Div(cls="widget-content")(
                                Img(alt="", src="./images/logo-light.png")
                            )
                        ),
                        Div(cls="widget Text")(
                            Div(cls="widget-content")(
                                P("Phasellus deserunt. Convallis perspiciatis fusce fermentum accumsan, arcu aliquam, velit venenatis augue proin, enim etiam dolor. Mi ac lectus vitae cum, fusce purus posuere.")
                            )
                        )
                    )
                ),
                Div(cls="col-lg-2 ml-lg-auto")(
                    Div(cls="footer-2 section", id="footer-2")(
                        Div(cls="widget")(
                            H4(cls="title title-heading")("About"),
                            Div(cls="widget-content list-label-widget-content")(
                                Ul(cls="list-unstyled")(
                                    Li(A(cls="label-name", href="/")("Home")),
                                    Li(A(cls="label-name", href="#")("Lifestyle")),
                                    Li(A(cls="label-name", href="#")("People")),
                                    Li(A(cls="label-name", href="#")("Sport"))
                                )
                            )
                        )
                    )
                ),
                Div(cls="col-lg-2")(
                    Div(cls="footer-3 section", id="footer-3")(
                        Div(cls="widget")(
                            H4(cls="title title-heading")("Categories"),
                            Div(cls="widget-content list-label-widget-content")(
                                Ul(cls="list-unstyled")(
                                    Li(A(cls="label-name", href="#")("Business")),
                                    Li(A(cls="label-name", href="#")("Design")),
                                    Li(A(cls="label-name", href="#")("Lifestyle")),
                                    Li(A(cls="label-name", href="#")("Technology"))
                                )
                            )
                        )
                    )
                )
            )
        ),
        Div(id="credits")(
            Div(cls="container")(
                Div(cls="row divider py-4")(
                    Div(cls="col-lg-6")(
                        Div(cls="copyright-section text-center text-lg-left")(
                            f"© {datetime.now().year} Nemesis | All Rights Reserved"
                        )
                    ),
                    Div(cls="col-lg-6")(
                        Div(cls="footer-menu section", id="footer-menu")(
                            Div(cls="widget socialList")(
                                Div(cls="widget-content")(
                                    Ul(cls="nav")(
                                        Li(cls="nav-item")(A(cls="nav-link", href="#")(I(cls="fa fa-facebook"))),
                                        Li(cls="nav-item")(A(cls="nav-link", href="#")(I(cls="fa fa-twitter"))),
                                        Li(cls="nav-item")(A(cls="nav-link", href="#")(I(cls="fa fa-instagram"))),
                                        Li(cls="nav-item")(A(cls="nav-link", href="#")(I(cls="fa fa-linkedin"))),
                                        Li(cls="nav-item")(A(cls="nav-link", href="#")(I(cls="fa fa-youtube-play")))
                                    )
                                )
                            )
                        )
                    )
                )
            )
        )
    )

@rt("/")
def homepage():
    """Homepage route"""
    # Get featured post and regular posts
    featured_post = next((post for post in sample_posts if post['is_featured']), sample_posts[0])
    regular_posts = [post for post in sample_posts if not post['is_featured']]
    
    return (
        Title("Nemesis | Minimal Blog HTML Template"),
        Meta(name="viewport", content="width=device-width, initial-scale=1.0"),
        search_overlay(),
        search_form(),
        Div(id="page-wrapper", cls="feed-view")(
            navbar(),
            hero_slider(featured_post),
            Div(cls="outer-wrapper clearfix", id="outer-wrapper")(
                Div(cls="container fbt-elastic-container")(
                    Div(cls="row justify-content-center")(
                        Div(cls="fbt-main-wrapper col-xl-12")(
                            Div(id="main-wrapper")(
                                Div(cls="main-section", id="main_content")(
                                    Div(cls="blog-posts fbt-index-post-wrap card-columns")(
                                        *[blog_post_card(post) for post in regular_posts]
                                    ),
                                    Div(cls="blog-pager", id="blog-pager")(
                                        Div(cls="list-inline")(
                                            A(cls="blog-pager-older-link list-inline-item", href="#", title="More posts")(
                                                Div(cls="fbt-bp-message text-uppercase font-weight-bold")("More posts"),
                                                Span(aria_hidden="true", cls="fa fa-angle-down")
                                            )
                                        )
                                    )
                                )
                            )
                        ),
                        sidebar()
                    )
                )
            ),
            newsletter_section(),
            Div(cls="fbt-bottom-shape")(
                # SVG wave shape
                NotStr('''<svg class="fbt-footer-wave-big" preserveAspectRatio="none" version="1.1" viewBox="5 0 1366 222" width="100%">
                    <path d="M-2.19,238H1366v-4.27c-67.87-24-146.44-43.08-230.75-53.19-253.33-27.78-293.94,51.64-541.13,29.89C318.08,186.31,289.49,32.92,6.9,11.73c-5.21-.42-10.56-.7-15.9-1V238Z" transform="translate(9.5 -10.22)"></path>
                </svg>''')
            ),
            footer()
        )
    )

@rt("/blog")
def blog_listing():
    """Blog listing page with magazine layout"""
    # Get posts for different sections
    featured_post = next((post for post in sample_posts if post['is_featured']), sample_posts[0])
    gallery_posts = sample_posts[1:6]  # Posts for gallery section
    main_posts = sample_posts[2:]  # Posts for main listing
    popular_posts = sample_posts[:4]  # Popular posts for sidebar
    
    return (
        Title("Nemesis | Magazine Blog HTML Template"),
        Meta(name="viewport", content="width=device-width, initial-scale=1.0"),
        search_overlay(),
        search_form(),
        Div(id="page-wrapper", cls="magazine-view feed-view")(
            headline_section(),
            magazine_navbar(),
            Div(cls="outer-wrapper my-5", id="outer-wrapper")(
                gallery_section(gallery_posts),
                # Ad Block
                Div(cls="container fbt-elastic-container mb-5")(
                    Div(cls="widget fbt-ad-block")(
                        Div(cls="fbt_ad text-center")(
                            Div(cls="widget-content")(
                                A(href="#")(
                                    Img(alt="", cls="img-fluid lazyloaded", src="./images/horizontal_ad.jpg")
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
            ),
            newsletter_section(),
            Div(cls="fbt-bottom-shape")(
                NotStr('''<svg class="fbt-footer-wave-big" preserveAspectRatio="none" version="1.1" viewBox="5 0 1366 222" width="100%">
                    <path d="M-2.19,238H1366v-4.27c-67.87-24-146.44-43.08-230.75-53.19-253.33-27.78-293.94,51.64-541.13,29.89C318.08,186.31,289.49,32.92,6.9,11.73c-5.21-.42-10.56-.7-15.9-1V238Z" transform="translate(9.5 -10.22)"></path>
                </svg>''')
            ),
            footer()
        )
    )

@rt("/contact")
def contact_page():
    """Contact page with form and information"""
    return (
        Title("Contact Us - Nemesis Blog"),
        Meta(name="viewport", content="width=device-width, initial-scale=1.0"),
        search_overlay(),
        search_form(),
        Div(id="page-wrapper", cls="page-view")(
            navbar(),
            Div(cls="outer-wrapper clearfix", id="outer-wrapper")(
                Div(cls="container fbt-elastic-container")(
                    Div(cls="row justify-content-center")(
                        Div(cls="fbt-main-wrapper col-xl-12")(
                            Div(id="main-wrapper")(
                                Div(cls="main-section", id="main_content")(
                                    Div(cls="blog-posts fbt-item-post-wrap")(
                                        Div(cls="blog-post fbt-item-post")(
                                            contact_hero_section(),
                                            Div(cls="row justify-content-center")(
                                                Div(cls="col-xl-8 col-lg-8 order-2 order-lg-1 mt-4 mt-lg-0")(
                                                    contact_form()
                                                ),
                                                contact_info_sidebar()
                                            )
                                        )
                                    )
                                )
                            )
                        ),
                        sidebar()
                    )
                )
            ),
            Div(cls="fbt-bottom-shape")(
                NotStr('''<svg class="fbt-footer-wave-big" preserveAspectRatio="none" version="1.1" viewBox="5 0 1366 222" width="100%">
                    <path d="M-2.19,238H1366v-4.27c-67.87-24-146.44-43.08-230.75-53.19-253.33-27.78-293.94,51.64-541.13,29.89C318.08,186.31,289.49,32.92,6.9,11.73c-5.21-.42-10.56-.7-15.9-1V238Z" transform="translate(9.5 -10.22)"></path>
                </svg>''')
            ),
            footer()
        )
    )

@rt("/contact", methods=["POST"])
def contact_form_submit(name: str, email: str, website: str = "", message: str = ""):
    """Handle contact form submission"""
    # Here you would typically save to database, send email, etc.
    # For now, we'll just return a success message
    
    return (
        Title("Message Sent - Nemesis Blog"),
        Meta(name="viewport", content="width=device-width, initial-scale=1.0"),
        Div(cls="container mt-5")(
            Div(cls="alert alert-success", role="alert")(
                H4(cls="alert-heading")("Message Sent Successfully!"),
                P(f"Thank you {name}, your message has been received. We'll get back to you at {email} soon."),
                Hr(),
                P(cls="mb-0")("Your message: ", Em(message[:100] + "..." if len(message) > 100 else message))
            ),
            A(href="/contact", cls="btn btn-primary mt-3")("← Back to Contact"),
            A(href="/", cls="btn btn-secondary mt-3 ml-2")("← Back to Home")
        )
    )

@rt("/post/{post_id}")
def post_detail(post_id: int):
    """Individual post page (placeholder for now)"""
    post = next((post for post in sample_posts if post['id'] == post_id), None)
    if not post:
        return "Post not found", 404
    
    return (
        Title(f"{post['title']} - Nemesis Blog"),
        Meta(name="viewport", content="width=device-width, initial-scale=1.0"),
        Div(cls="container mt-5")(
            H1(post['title']),
            P(f"By {post['author']} on {post['date']} | Category: {post.get('category', 'General')}"),
            Img(src=post['image'], cls="img-fluid mb-3"),
            P(post['excerpt']),
            Hr(),
            A(href="/", cls="btn btn-primary mr-2")("← Back to Home"),
            A(href="/blog", cls="btn btn-secondary")("← Back to Blog")
        )
    )

serve()