#!/usr/bin/env python

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from plist_parser import XmlPropertyListParser

# the directory contains sample .plist files
PLIST_DIR = os.path.join(os.path.dirname(__file__), 'plist')

def getPropertyListFilepath(name):
    return os.path.join(PLIST_DIR, name)

def readPropertyListContents(name):
    xmlin = open(getPropertyListFilepath(name))
    try:
        return xmlin.read()
    finally:
        xmlin.close()

def parsePropertyList(name):
    parser = XmlPropertyListParser()
    xmlin = open(getPropertyListFilepath(name))
    try:
        return parser.parse(xmlin)
    finally:
        xmlin.close()


# Non-ASCII Strings...
JP_JAPANESE = u'\u65e5\u672c\u8a9e' # 'Japanese' in Japanese
JP_HELLO = u'\u3053\u3093\u306b\u3061\u306f' # 'Hello' in Japanese


class XmlPropertyListParserTest(unittest.TestCase):

    def assertNotNone(self, obj):
        self.assert_(obj is not None)

    def assertIsInstance(self, obj, expected_type):
        self.assert_(
            isinstance(obj, expected_type),
            "Expected '%s' instance, but was '%s'" % (expected_type, type(obj)))

    def _testAcceptingStringOrUnicodeInput(self, plist_name):
        parser = XmlPropertyListParser()
        contents = readPropertyListContents(plist_name)
        self.assert_(parser.parse(contents) is not None)
        unicode_contents = unicode(contents, 'utf-8')
        self.assert_(parser.parse(unicode_contents) is not None)
        
    def _testNonASCIIEncoding(self, plist_name):
        plist = parsePropertyList(plist_name)
        self.assertNotNone(plist)
        self.assertIsInstance(plist, dict)
        self.assert_(JP_JAPANESE in plist)
        self.assertEqual(plist[JP_JAPANESE], JP_HELLO)

    def test_init(self):
        self.assert_(XmlPropertyListParser())

    def test_non_ascii_plist(self):
        self._testNonASCIIEncoding('utf8.plist')
        #self._testNonASCIIEncoding('sjis.plist')


    def test_no_plist_xml(self):
        parser = XmlPropertyListParser()
        self.assertRaises(
            XmlPropertyListParser.ParseError,
            parser.parse, '<not-plist />')

    def test_string_or_unicode_input(self):
        self._testAcceptingStringOrUnicodeInput("empty_dict.plist")
        
    def test_multiple_plist(self):
        self.assertRaises(
            XmlPropertyListParser.ParseError,
            parsePropertyList, 'multiple_plist.plist')

    def test_empty_dict_plist(self):
        plist = parsePropertyList('empty_dict.plist')
        self.assertNotNone(plist)
        self.assertIsInstance(plist, dict)
        self.assert_(len(plist) is 0)

    def test_empty_array_plist(self):
        plist = parsePropertyList('empty_array.plist')
        self.assertNotNone(plist)
        self.assertIsInstance(plist, list)
        self.assert_(len(plist) is 0)

    def test_simple_plist(self):
        plist = parsePropertyList('simple.plist')
        self.assertNotNone(plist)
        self.assertIsInstance(plist, dict)
        self.assert_('item 1' in plist)
        self.assertEqual(plist['item 1'], 'Hello')

    def test_datetime_plist(self):
        plist = parsePropertyList('datetime.plist')
        self.assertNotNone(plist)
        self.assertIsInstance(plist, list)
        self.assertEqual(str(plist[0]), "2008-08-02 05:25:50")
        self.assertEqual(str(plist[1]), "2008-08-02 05:25:00")
        self.assertEqual(str(plist[2]), "2008-08-02 05:00:00")
        self.assertEqual(str(plist[3]), "2008-08-02 00:00:00")
        self.assertEqual(str(plist[4]), "2008-08-01 00:00:00")
        self.assertEqual(str(plist[5]), "2008-01-01 00:00:00")

    def test_invalid_datetime(self):
        parser = XmlPropertyListParser()
        self.assertRaises(XmlPropertyListParser.ParseError,
            parser.parse,
            '<plist version="1.0"><date></date></plist>')
        self.assertRaises(XmlPropertyListParser.ParseError,
            parser.parse,
            '<plist version="1.0"><date>kasdhfksahkdfj</date></plist>')

    def test_elements_plist(self):
        plist = parsePropertyList('elements.plist')
        self.assertNotNone(plist)
        self.assertIsInstance(plist, dict)

        self.assertEqual(plist['string item'], 'string value')
        self.assertEqual(plist['long long string item'], """There, he campaigned for the amalgamation of Northern and Southern Rhodesia. Although unsuccessful, he succeeded in the formation of the Federation of Rhodesia and Nyasaland""")
        self.assertEqual(plist['integer number item'], 12345)
        self.assertEqual(plist['real number item'], 123.45)

        item = plist['nested dictionary']
        self.assertIsInstance(item, dict)
        self.assertEqual(item['true item'], True)
        self.assertEqual(item['false item'], False)

        item = item['array item']
        self.assertIsInstance(item, list)
        self.assertEqual(item[0], 'hello')
        self.assertEqual(str(item[1]), "2008-08-01 06:16:37")
        self.assertIsInstance(item[2], list)
        self.assertIsInstance(item[2][0], dict)
        self.assertEqual(item[2][0]['item'], 1)


if __name__ == "__main__":
    unittest.main()
