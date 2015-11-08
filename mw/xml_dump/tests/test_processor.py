import io
from multiprocessing import Queue

from nose.tools import eq_, raises

from ..processor import DONE, Processor


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



def test_processor():

    pathq = Queue()
    pathq.put(io.StringIO(SAMPLE_XML))

    outputq = Queue()

    def process_dump(dump, path):
        for page in dump:
            yield page.id


    processor = Processor(pathq, outputq, process_dump)
    processor.start()

    error, item = outputq.get()
    assert not error
    eq_(item, 1)

    error, item = outputq.get()
    assert not error
    eq_(item, 2)

    error, item = outputq.get()
    assert not error
    eq_(item, DONE)

def test_processor_error():

    pathq = Queue()
    pathq.put(io.StringIO(SAMPLE_XML))

    outputq = Queue()

    def process_dump(dump, path):
        raise Exception("foo")


    processor = Processor(pathq, outputq, process_dump)
    processor.start()

    error, item = outputq.get()
    assert error

    error, item = outputq.get()
    assert not error
    eq_(item, DONE)
