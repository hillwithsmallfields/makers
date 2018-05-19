#!/usr/bin/python

from nevow import flat
from nevow import tags as T
import configuration
import os

def page_string(title, content):
    """Make up a complete page as a string."""
    conf = configuration.get_config()
    page_conf = conf['page']
    preamble = page_conf['preamble']
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
    postamble = page_conf['postamble']
    return flat.flatten(T.html[T.head[T.raw(style_text),
                                      T.title[title]],
                               # todo: set the encoding
                               # todo: include a stylesheet as set in the config file
                               T.body[T.raw(preamble),
                                      T.h1[title],
                                      content,
                                      T.raw(postamble)]])

def test_page_section(title, content):
    """Make a section of the overall test page."""
    return [T.h2[title], content]

def error_page(message):
    return page_string(message, message)
