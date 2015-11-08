import io

from nose.tools import eq_, raises

from ..map import map


SAMPLE_XML = """
<mediawiki xmlns="http://www.mediawiki.org/xml/export-0.8/"
           xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
           xsi:schemaLocation="http://www.mediawiki.org/xml/export-0.8/
           http://www.mediawiki.org/xml/export-0.8.xsd"
           version="0.8" xml:lang="en">
  <siteinfo>
    <sitename>Wikipedia</sitename>
    <base>http://en.wikipedia.org/wiki/Main_Page</base>
    <generator>MediaWiki 1.22wmf2</generator>
    <case>first-letter</case>
    <namespaces>
      <namespace key="0" case="first-letter" />
      <namespace key="1" case="first-letter">Talk</namespace>
    </namespaces>
  </siteinfo>
  <page>
    <title>Foo</title>
    <ns>0</ns>
    <id>1</id>
    <revision>
      <id>1</id>
      <timestamp>2004-08-09T09:04:08Z</timestamp>
      <contributor>
        <username>Gen0cide</username>
        <id>92182</id>
      </contributor>
      <text xml:space="preserve">Revision 1 text</text>
      <sha1>g9chqqg94myzq11c56ixvq7o1yg75n9</sha1>
      <model>wikitext</model>
      <format>text/x-wiki</format>
    </revision>
    <revision>
      <id>2</id>
      <timestamp>2004-08-10T09:04:08Z</timestamp>
      <contributor>
        <ip>222.152.210.109</ip>
      </contributor>
      <text xml:space="preserve">Revision 2 text</text>
      <sha1>g9chqqg94myzq11c56ixvq7o1yg75n9</sha1>
      <model>wikitext</model>
      <comment>Comment 2</comment>
      <format>text/x-wiki</format>
    </revision>
  </page>
  <page>
    <title>Bar</title>
    <ns>1</ns>
    <id>2</id>
    <revision>
      <id>3</id>
      <timestamp>2004-08-11T09:04:08Z</timestamp>
      <contributor>
        <ip>222.152.210.22</ip>
      </contributor>
      <text xml:space="preserve">Revision 3 text</text>
      <sha1>g9chqqg94myzq11c56ixvq7o1yg75n9</sha1>
      <model>wikitext</model>
      <format>text/x-wiki</format>
    </revision>
  </page>
</mediawiki>"""


def test_map():
    f = io.StringIO(SAMPLE_XML)

    def process_dump(dump, path):
        for page in dump:
            count = 0
            for rev in page:
                count += 1

            yield {'page_id': page.id, 'revisions': count}

    pages = 0
    for doc in map([f], process_dump):
        page_id = doc['page_id']
        revisions = doc['revisions']
        if page_id == 1:
            eq_(revisions, 2)
        elif page_id == 2:
            eq_(revisions, 1)
        else:
            assert False

        pages += 1

    eq_(pages, 2)


def test_dict_yield():
    def test_map():
        f = io.StringIO(SAMPLE_XML)

        def process_dump(dump, path):
            for page in dump:
                count = 0
                for rev in page:
                    count += 1

                yield {'page_id': page.id, 'revisions': count}

        pages = 0
        for doc in map([f], process_dump):
            page_id = doc['page_id']
            revisions = doc['revisions']
            if page_id == 1:
                eq_(revisions, 2)
            elif page_id == 2:
                eq_(revisions, 1)
            else:
                assert False

            pages += 1

        eq_(pages, 2)


@raises(TypeError)
def test_map_error():
    f = io.StringIO(SAMPLE_XML)

    def process_dump(dump, path):
        for page in dump:

            if page.id == 2:
                raise TypeError("Fake error")

    pages = 0
    for doc in map([f], process_dump):
        page_id = doc['page_id']


def test_map_error_handler():
    f = io.StringIO(SAMPLE_XML)

    def process_dump(dump, path, handle_error=lambda exp, stack: None):
        for page in dump:
            count = 0

            for rev in page:
                count += 1

            if count > 2:
                raise TypeError("Fake type error.")

            yield {'page_id': page.id, 'revisions': count}

    pages = 0
    for doc in map([f], process_dump):
        page_id = doc['page_id']
        revisions = doc['revisions']
        if page_id == 1:
            eq_(revisions, 2)
        elif page_id == 2:
            eq_(revisions, 1)
        else:
            assert False

        pages += 1

    eq_(pages, 2)
