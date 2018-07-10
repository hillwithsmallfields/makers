#!/usr/bin/python

import throw_out_your_templates_p3 as untemplate
from throw_out_your_templates_p3 import htmltags as T
import configuration
import os

class HtmlPage(object):

    def __init__(self, name, content,
                 visitor_map=untemplate.examples_vmap,
                 input_encoding='utf-8'):
        self.name = name
        self.content = content
        self.visitor_map = visitor_map
        self.input_encoding = input_encoding

    def to_string(self):
        return untemplate.Serializer(self.visitor_map,
                                     self.input_encoding).serialize(self.content)

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
        self.sections[id] = content
        self.presentation_names[id] = name
        self.index.append(id)

    def to_string(self):
        index = [T.div(klass="tab"),
                 [[T.button(klass="tablinks",
                            onclick="openTab(event, '" + sec_id + "')")[self.presentation_names[id]]
                   for sec_id in self.index]]]
        tabs = [[T.div(klass="tabcontent" id=sec_id)[self.sections[sec_id]]]
                   for sec_id in self.index]
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
    return HtmlPage(page_title,
                    untemplate.HTML5Doc([untemplate.safe_unicode(style_text
                                                                 + script_text
                                                                 + preamble),
                                         content,
                                         untemplate.safe_unicode(postamble)],
                                        head=T.head[T.title[page_title]])).to_string()

def expandable_section(section_id, section_tree):
    # from https://stackoverflow.com/questions/16308779/how-can-i-hide-show-a-div-when-a-button-is-clicked
    return [T.button(onclick="toggle_visibility(section_id);")["Toggle"],
            T.div(id=section_id)[section_tree]]

def test_page_section(title, content):
    """Make a section of the overall test page."""
    return [T.h2[title], content]

def error_page(message):
    return page_string(message, message)
