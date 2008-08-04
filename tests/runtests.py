#!/usr/bin/env python

import os
import sys
import unittest
from test import test_support

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from plist_parser import XmlPropertyListParser, PropertyListParseError

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

# Non-ASCII Strings...
JP_JAPANESE = u'\u65e5\u672c\u8a9e' # 'Japanese' in Japanese
JP_HELLO = u'\u3053\u3093\u306b\u3061\u306f' # 'Hello' in Japanese


class XmlPropertyListGenericParserTest(unittest.TestCase):

    def parse(self, xmlin):
        parser = XmlPropertyListParser()
        return parser.parse(xmlin)

    def parsePropertyList(self, name):
        xmlin = open(getPropertyListFilepath(name))
        try:
            return self.parse(xmlin)
        finally:
            xmlin.close()

    def assertNotNone(self, obj):
        self.assert_(obj is not None)

    def assertIsInstance(self, obj, expected_type):
        self.assert_(
            isinstance(obj, expected_type),
            "Expected '%s' instance, but was '%s'" % (expected_type, type(obj)))

    def _testAcceptingStringOrUnicodeInput(self, plist_name):
        contents = readPropertyListContents(plist_name)
        self.assert_(self.parse(contents) is not None)
        unicode_contents = unicode(contents, 'utf-8')
        self.assert_(self.parse(unicode_contents) is not None)
        
    def _testNonASCIIEncoding(self, plist_name):
        plist = self.parsePropertyList(plist_name)
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
        self.assertRaises(
            PropertyListParseError,
            self.parse, '<not-plist />')

    def test_string_or_unicode_input(self):
        self._testAcceptingStringOrUnicodeInput("empty_dict.plist")
        
    def test_multiple_plist(self):
        self.assertRaises(
            PropertyListParseError,
            self.parsePropertyList, 'multiple_plist.plist')

    def test_multiple_top_level_plist(self):
        self.assertRaises(
            PropertyListParseError,
            self.parsePropertyList, 'multiple_top_level.plist')

    def test_invalid_key_plist(self):
        self.assertRaises(
            PropertyListParseError,
            self.parsePropertyList, 'invalid_key.plist')

    def test_empty_dict_plist(self):
        plist = self.parsePropertyList('empty_dict.plist')
        self.assertNotNone(plist)
        self.assertIsInstance(plist, dict)
        self.assert_(len(plist) is 0)

    def test_empty_array_plist(self):
        plist = self.parsePropertyList('empty_array.plist')
        self.assertNotNone(plist)
        self.assertIsInstance(plist, list)
        self.assert_(len(plist) is 0)

    def test_simple_plist(self):
        plist = self.parsePropertyList('simple.plist')
        self.assertNotNone(plist)
        self.assertIsInstance(plist, dict)
        self.assert_('item 1' in plist)
        self.assertEqual(plist['item 1'], 'Hello')

    def test_datetime_plist(self):
        plist = self.parsePropertyList('datetime.plist')
        self.assertNotNone(plist)
        self.assertIsInstance(plist, list)
        self.assertEqual(str(plist[0]), "2008-08-02 05:25:50")
        self.assertEqual(str(plist[1]), "2008-08-02 05:25:00")
        self.assertEqual(str(plist[2]), "2008-08-02 05:00:00")
        self.assertEqual(str(plist[3]), "2008-08-02 00:00:00")
        self.assertEqual(str(plist[4]), "2008-08-01 00:00:00")
        self.assertEqual(str(plist[5]), "2008-01-01 00:00:00")

    def test_not_xml_plist(self):
        self.assertRaises(
            PropertyListParseError,
            self.parsePropertyList,
            'notxml.plist'
        )

    def test_invalid_datetime(self):
        self.assertRaises(PropertyListParseError,
            self.parse,
            '<plist version="1.0"><date></date></plist>')
        self.assertRaises(PropertyListParseError,
            self.parse,
            '<plist version="1.0"><date>kasdhfksahkdfj</date></plist>')
        self.assertRaises(PropertyListParseError,
            self.parse,
            '<plist version="1.0"><date> 2008-08-02T05:25:50Z</date></plist>')
        self.assertRaises(PropertyListParseError,
            self.parse,
            '<plist version="1.0"><date>2008-08-02T05:25:50Z </date></plist>')

    def test_elements_plist(self):
        plist = self.parsePropertyList('elements.plist')
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


class XmlPropertyListSAXParserTest(XmlPropertyListGenericParserTest):

    def parse(self, xmlin):
        parser = XmlPropertyListParser()
        return parser._parse_using_etree(xmlin)
        

class XmlPropertyListEtreeParserTest(XmlPropertyListGenericParserTest):

    def parse(self, xmlin):
        parser = XmlPropertyListParser()
        return parser._parse_using_sax_parser(xmlin)


if __name__ == "__main__":
    loader = unittest.defaultTestLoader
    suite = unittest.TestSuite()
    suite.addTest(loader.loadTestsFromTestCase(XmlPropertyListGenericParserTest))
    suite.addTest(loader.loadTestsFromTestCase(XmlPropertyListSAXParserTest))
    try:
        from xml.etree.cElementTree import iterparse
    except ImportError:
        pass
    else:
        suite.addTest(loader.loadTestsFromTestCase(XmlPropertyListEtreeParserTest))

    runner = unittest.TextTestRunner(verbosity=1)
    result = runner.run(suite)
    sys.exit(not result.wasSuccessful())
