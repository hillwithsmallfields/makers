#!/usr/bin/python

from nevow import flat
from nevow import tags as T
import configuration

preamble = None
postamble = None

def page_string(title, content):
    """Make up a complete page as a string."""
    global preamble, postamble
    if preamble is None or postamble is None:
        conf = configuration.get_config()
        preamble = conf['page']['preamble']
        postamble = conf['page']['postamble']
    return flat.flatten(T.html[T.head[T.title[title]],
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

def main():                     # for testing
    print page_string("Test page", "Test content")

if __name__ == "__main__":
    main()
