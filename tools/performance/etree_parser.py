import sys
import base64, time, datetime

callbacks = {
    'array': lambda x: [v.text for v in x],
    'dict': lambda x:
        dict((x[i].text, x[i+1].text) for i in range(0, len(x), 2)),
    'key': lambda x: x.text or "",
    'string': lambda x: x.text or "",
    'data': lambda x: base64.b64decode(x.text),
    'date': lambda x: 
        datetime.datetime(
            *(time.strptime(x.text, "%Y-%m-%dT%H:%M:%SZ")[0:6])),
    'real': lambda x: float(x.text),
    'integer': lambda x: int(x.text),
    'true': lambda x: True,
    'false': lambda x: False,
}

def _xml_plist_parse(xml_input, _iterparse):
    parser = _iterparse(xml_input)
    for action, element in parser:
        callback = callbacks.get(element.tag)
        if callback:
            data = callback(element)
            element.clear()
            element.text = data
        elif element.tag != 'plist':
            raise IOError("unknown plist tag: %s" % element.tag)
    return parser.root[0].text

def parse_using_etree(xml_input):
    from xml.etree.ElementTree import iterparse as py_iterparse
    _xml_plist_parse(xml_input, py_iterparse)

def parse_using_cetree(xml_input):
    import xml.etree.cElementTree
    from xml.etree.cElementTree import iterparse as c_iterparse
    _xml_plist_parse(xml_input, c_iterparse)


if __name__ == '__main__':
    xmlin = open(sys.argv[1])
    try:
        assert parse_using_cetree(xmlin)
    finally:
        xmlin.close()
