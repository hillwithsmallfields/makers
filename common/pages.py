#!/usr/bin/python

from nevow import flat
from nevow import tags as T
import config

preamble = None
postamble = None

def page_string(title, content):
    """Make up a complete page as a string."""
    global preamble, postamble
    if preamble is None or postamble is None:
        conf = config.get_config()
        preamble = conf['page']['preamble']
        postamble = conf['page']['postamble']
    return flat.flatten(T.html[T.head[T.title[title]],
                               T.body[preamble,
                                      T.h1[title],
                                      content,
                                      postamble]])

def error_page(message):
    return page_string(message, message)

def main():                     # for testing
    print page_string("Test page", "Test content")

if __name__ == "__main__":
    main()
