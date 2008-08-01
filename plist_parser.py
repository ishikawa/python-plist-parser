#!/usr/bin/env python
"""
A `Property Lists`_ is a data representation used in Apple's Mac OS X as
a convenient way to store standard object types, such as string, number,
boolean, and container object.

This file contains a class ``XmlPropertyListParser`` for parse
a property list file and get back a python native data structure.

    :copyright: 2008 by Takanori Ishikawa <takanori.ishikawa@gmail.com>
    :license: MIT (See LICENSE file)

.. _Property Lists: http://developer.apple.com/documentation/Cocoa/Conceptual/PropertyLists/
"""
import xml.sax
from xml.sax import handler, xmlreader


class XmlPropertyListParser(handler.ContentHandler):
    """
    The ``XmlPropertyListParser`` class provides methods that
    convert `Property Lists`_ objects from xml format.
    Property list objects include ``string``, ``unicode``,
    ``list``, ``dict``, ``datetime``, and ``int`` or ``float``.

    .. _Property List: http://developer.apple.com/documentation/Cocoa/Conceptual/PropertyLists/
    """

    class ParseError(Exception):
        """Raised when parsing is failed."""
        pass

    def __init__(self):
        handler.ContentHandler.__init__(self)
        self.__stack = None
        self.__key = None
        self.__characters = None

    def _assert(self, test, message):
        if not test:
            raise XmlPropertyListParser.ParseError(message)

    # ------------------------------------------------
    # SAX2: ContentHandler
    # ------------------------------------------------
    def startDocument(self):
        self.__stack = []
        self.__key = None
        self.__characters = []

    def startElement(self, name, attributes):
        if name in XmlPropertyListParser.START_CALLBACKS:
            XmlPropertyListParser.START_CALLBACKS[name](self, name, attributes)
        if name in XmlPropertyListParser.PARSE_CALLBACKS:
            self.__characters = []

        if name == 'plist':
            self._assert(not self.__stack, "<plist> more than once.")
        else:
            self._assert(self.__stack, "A top level element must be <plist>.")

    def endElement(self, name):
        if name in XmlPropertyListParser.END_CALLBACKS:
            XmlPropertyListParser.END_CALLBACKS[name](self, name)
        if name in XmlPropertyListParser.PARSE_CALLBACKS:
            # Creates character string from buffered characters.
            content = ''.join(self.__characters)
            XmlPropertyListParser.PARSE_CALLBACKS[name](self, name, content)
            self.__characters = None

    def characters(self, content):
        if self.__characters is not None:
            self.__characters.append(content)

    # ------------------------------------------------
    # XmlPropertyListParser private
    # ------------------------------------------------
    def _push_value(self, value):
        if self.__stack:
            top = self.__stack[-1]
            if isinstance(top, dict):
                self._assert(self.__key is not None, "Missing key for dictionary.")
                top[self.__key] = value
                self.__key = None
            elif isinstance(top, list):
                top.append(value)
            else:
                raise XmlPropertyListParser.ParseError(
                    "multiple objects at top level")
        
        if not self.__stack or isinstance(value, (dict, list)):
            self.__stack.append(value)

    def _pop_value(self):
        if len(self.__stack) > 1:
            self.__stack.pop()

    def _start_plist(self, name, attrs):
        self._assert(len(self.__stack) is 0, "<plist> more than once.")
        self._assert(attrs.get('version', '1.0') == '1.0',
            "version 1.0 is only supported, but was '%s'." % attrs.get('version'))

    def _start_array(self, name, attrs):
        self._push_value(list())

    def _start_dict(self, name, attrs):
        self._push_value(dict())

    def _start_true(self, name, attrs):
        self._push_value(True)

    def _start_false(self, name, attrs):
        self._push_value(False)

    def _end_array(self, name):
        self._pop_value()

    def _end_dict(self, name):
        self._pop_value()

    def _parse_key(self, name, content):
        self.__key = content

    def _parse_string(self, name, content):
        self._push_value(content)

    def _parse_data(self, name, content):
        import base64
        self._push_value(base64.b64decode(content))

    def _parse_date(self, name, content):
        import time, datetime
        self._push_value(datetime.datetime(
            *(time.strptime(content, "%Y-%m-%dT%H:%M:%SZ")[0:6])))

    def _parse_real(self, name, content):
        self._push_value(float(content.strip()))

    def _parse_integer(self, name, content):
        self._push_value(int(content.strip()))

    START_CALLBACKS = {
        'plist': _start_plist,
        'array': _start_array,
        'dict': _start_dict,
        'true': _start_true,
        'false': _start_false,
    }

    END_CALLBACKS = {
        'array': _end_array,
        'dict': _end_dict,
    }

    PARSE_CALLBACKS = {
        'key': _parse_key,
        'string': _parse_string,
        'data': _parse_data,
        'date': _parse_date,
        'real': _parse_real,
        'integer': _parse_integer,
    }

    # ------------------------------------------------
    # XmlPropertyListParser
    # ------------------------------------------------
    def parse(self, xml_input):
        """
        Parse the property list (`.plist`, `.xml, for example) ``xml_input``,
        which can be either a string or a file-like object.
        
        >>> parser = XmlPropertyListParser()
        >>> parser.parse(r'<plist version="1.0"><dict><key>Python</key><string>.py</string></dict></plist>')
        {u'Python': u'.py'}
        """

        def make_source(xml_input):
            source = xmlreader.InputSource()
            if isinstance(xml_input, basestring):
                # Creates a string stream for in-memory contents.
                from StringIO import StringIO
                xml_input = StringIO(xml_input)
            source.setByteStream(xml_input)
            return source

        source = make_source(xml_input)
        reader = xml.sax.make_parser()
        reader.setContentHandler(self)
        reader.parse(source)
        self._assert(
            len(self.__stack) is 1,
            "multiple objects at top level.")
        return self.__stack.pop()


if __name__ == '__main__':
    # doctest, and parse .plist specified by ARGV[1]
    #
    # For example, parsing iTunes Liberary on your mac.
    # % python ./plist_parser.py ~/"Music/iTunes/iTunes Music Library.xml"
    #
    import sys
    import doctest
    doctest.testmod()

    if len(sys.argv) > 1:
        xmlin = open(sys.argv[1])
        try:
            print XmlPropertyListParser().parse(xmlin),
        finally:
            xmlin.close()
