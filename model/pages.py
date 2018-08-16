#!/usr/bin/python

from untemplate.throw_out_your_templates_p3 import htmltags as T
import bson
import model.configuration as configuration
import model.person
import os
import re
import untemplate.throw_out_your_templates_p3 as untemplate

def with_help(who, content, help_name):
    if not who.show_help:
        return content
    help_file = os.path.join(configuration.get_config()['page']['help_texts'], help_name + ".html")
    if os.path.isfile(help_file):
        with open(help_file) as helpstream:
            return T.table(class_="help_on_right")[T.tr[T.td(class_="helped")[content],
                                                        T.td(class_="help")[untemplate.safe_unicode(helpstream.read())]]]
    else:
        return content

def debug_string(whatever):
    return untemplate.Serializer(untemplate.examples_vmap, 'utf-8').serialize(whatever)

class RawHtmlPage(object):

    def __init__(self, name, content=[],
                 visitor_map=untemplate.examples_vmap,
                 input_encoding='utf-8'):
        self.name = name
        self.content = content
        self.visitor_map = visitor_map
        self.input_encoding = input_encoding

    def add_content(self, name, content):
        self.content.append([T.h2[name], content])

    def to_string(self):
        return untemplate.Serializer(self.visitor_map,
                                     self.input_encoding).serialize(self.content)

class HtmlPage(object):

    def __init__(self, name, content=[],
                 visitor_map=untemplate.examples_vmap,
                 django_request=None,
                 input_encoding='utf-8'):
        self.name = name
        self.content = content
        self.visitor_map = visitor_map
        self.input_encoding = input_encoding
        self.django_request = django_request

    def add_content(self, name, content):
        self.content.append([T.h2[name], content])

    def to_string(self):
        return page_string(self.name, self.content)

class SectionalPage(object):

    """A page which can be rendered as tabs and possibly other styles."""

    def __init__(self, name, top_content, viewer=None, django_request=None):
        self.name = name
        self.top_content = top_content
        self.sections = {}
        self.initial_tab = None
        self.initial_tab_priority = -1
        self.presentation_names = {}
        self.index = []
        self.viewer = viewer
        self.django_request = django_request

    def add_section(self, name, content, priority=1):
        section_id = name.replace(' ', '_')
        self.sections[section_id] = [T.h2[name], content]
        self.presentation_names[section_id] = name
        if priority > self.initial_tab_priority:
            self.initial_tab_priority = priority
            self.initial_tab = section_id
        self.index.append(section_id)

    def to_string(self):
        index = [T.div(class_="tabset")[
            [T.button(class_="tablinks",
                      onclick="openTab(event, '" + section_id + "')",
                      id=section_id+"_button")[self.presentation_names[section_id]]
                                      for section_id in self.index]],
                 T.br(clear='all')]
        tabs = [[T.div(class_="tabcontent", id_=section_id)[self.sections[section_id]]]
                   for section_id in self.index]
        return page_string(self.name,
                           self.top_content + index + tabs,
                           user=self.viewer or (model.person.Person.find(self.django_request.user.link_id)
                                                if self.django_request
                                                else None),
                           initial_tab=(self.initial_tab+"_button") if self.initial_tab else None)

def page_string(page_title, content, user=None, initial_tab=None):
    """Make up a complete page as a string."""
    conf = configuration.get_config()
    page_conf = conf['page']
    org_conf = conf['organization']
    preamble = page_conf.get('preamble', '')
    script_file = page_conf['script_file']
    script_body = ""
    if os.path.exists(script_file):
        with open(script_file) as mfile:
            script_body = mfile.read()
    script_text = """<script type="text/javascript">""" + script_body + """</script>"""
    motd = ""
    motd_file = page_conf['motd_file']
    if os.path.exists(motd_file):
        with open(motd_file) as mfile:
            motd = mfile.read()
    stylesheet_name = page_conf['stylesheet']
    if user and user.stylesheet:
        user_stylesheet_name = os.path.dirname(stylesheet_name) + user.stylesheet + ".css"
        if os.path.exists(user_stylesheet_name):
            stylesheet_name = user_stylesheet_name
    if os.path.exists(stylesheet_name):
        inline = page_conf['style_inline']
        if inline:
            with open(stylesheet_name) as sf:
                style_text = '<style type="text/css">' + sf.read() + '</style>'
        else:
            style_text = '<link rel="stylesheet" type="text/css" href="' + stylesheet_name + '">'
    # todo: put the motd into the preamble
    postamble = page_conf.get('postamble', '')
    final_setup = """<script type="text/javascript">selectTab('""" + initial_tab + """')</script>""" if initial_tab else ""
    page_heading = page_title
    logo = page_conf.get('heading_logo', None)
    if logo:
        logo_height = int(page_conf.get('logo_height', "32"))
        page_heading = T.span[page_heading,
                              T.a(href=org_conf['home_page'])[T.img(align="right",
                                                                    alt=org_conf['title'],
                                                                    height=logo_height,
                                                                    src=logo)]]
    footer = T.footer[T.hr,
                      T.p(class_="the_small_print")
                      ["Produced by the ",
                       T.a(href="https://github.com/hillwithsmallfields/makers/")["makers"],
                       " system.  ",
                       "We use ",
                       T.a(href="https://www.djangoproject.com/")["django"],
                       " to handle login and sessions, and that uses a ",
                       T.a(href="https://docs.djangoproject.com/en/2.1/topics/http/sessions/#using-cookie-based-sessions")["session cookie"],
                       " and a ",
                       T.a(href="https://docs.djangoproject.com/en/2.1/ref/csrf/")["CSRF protection cookie"],
                       ".  ",
                       "We don't use any other cookies that we are aware of, and we neither sell your data nor give it away."]]
    return RawHtmlPage(page_title,
                    untemplate.HTML5Doc([untemplate.safe_unicode(style_text
                                                                 + script_text
                                                                 + preamble),
                                         T.body[T.h1[page_heading],
                                                content,
                                                footer],
                                         untemplate.safe_unicode(postamble),
                                         untemplate.safe_unicode(final_setup)],
                                        head=T.head[T.title[page_title]])).to_string()

def expandable_section(section_id, section_tree):
    # from https://stackoverflow.com/questions/16308779/how-can-i-hide-show-a-div-when-a-button-is-clicked
    return [T.button(onclick="toggle_visibility(section_id);")["Toggle"],
            T.div(id_=section_id)[section_tree]]

def test_page_section(title, content):
    """Make a section of the overall test page."""
    return [T.h2[title], content]

def error_page(message):
    return page_string(message, message)

def unstring_id(poss_id):
    """Convert a representation of an ObjectId back to an ObjectId."""
    if isinstance(poss_id, str):
        matched = re.match("ObjectId\\('([0-9a-fA-F]+)'\\)", poss_id)
        if matched:
            poss_id = matched.group(1)
        if re.match("[0-9a-fA-F]+$", poss_id):
            return bson.objectid.ObjectId(poss_id)
    return poss_id
