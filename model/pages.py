#!/usr/bin/python

import untemplate.throw_out_your_templates_p3 as untemplate
from untemplate.throw_out_your_templates_p3 import htmltags as T
import model.configuration as configuration
import os

def with_help(content, help_name):
    help_file = os.path.join(configuration.get_config()['page']['help_texts'], help_name + ".html")
    if os.path.isfile(help_file):
        with open(help_file) as helpstream:
            return T.table(class_="help_on_right")[T.tr[T.td(class_="helped")[content],
                                                        T.td(class_="help")[untemplate.safe_unicode(helpstream.read())]]]
    else:
        return content

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
                 input_encoding='utf-8'):
        self.name = name
        self.content = content
        self.visitor_map = visitor_map
        self.input_encoding = input_encoding

    def add_content(self, name, content):
        self.content.append([T.h2[name], content])

    def to_string(self):
        return page_string(self.name, self.content)

class SectionalPage(object):

    """A page which can be rendered as tabs and possibly other styles."""

    def __init__(self, name, top_content):
        self.name = name
        self.top_content = top_content
        self.sections = {}
        self.presentation_names = {}
        self.index = []

    def add_section(self, name, content):
        section_id = name.replace(' ', '_')
        self.sections[section_id] = [T.h2[name], content]
        self.presentation_names[section_id] = name
        self.index.append(section_id)

    def to_string(self):
        index = [T.div(class_="tab")[[T.button(class_="tablinks",
                                               onclick="openTab(event, '" + section_id + "')")[self.presentation_names[section_id]]
                                      for section_id in self.index]]]
        tabs = [[T.div(class_="tabcontent", id_=section_id)[self.sections[section_id]]]
                   for section_id in self.index]
        return page_string(self.name,
                           self.top_content + index + tabs)

def page_string(page_title, content):
    """Make up a complete page as a string."""
    conf = configuration.get_config()
    page_conf = conf['page']
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
    if os.path.exists(stylesheet_name):
        inline = page_conf['style_inline']
        if inline:
            with open(stylesheet_name) as sf:
                style_text = '<style type="text/css">' + sf.read() + '</style>'
        else:
            style_text = '<link rel="stylesheet" type="text/css" href="' + stylesheet_name + '">'
    # todo: put the motd into the preamble
    postamble = page_conf.get('postamble', '')
    # print "Flattening", content
    return RawHtmlPage(page_title,
                    untemplate.HTML5Doc([untemplate.safe_unicode(style_text
                                                                 + script_text
                                                                 + preamble),
                                         T.body[T.h1[page_title],
                                                content],
                                         untemplate.safe_unicode(postamble)],
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
