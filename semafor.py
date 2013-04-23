import sys
from datetime import datetime
from lxml import etree

CORPUS_DATE_FORMAT = "%a %b %d %H:%M:%S %Z %Y"

class Corpus(object):

    def __init__(self, name, date, docs=[]):
        self.name = name
        self.date = date
        self.docs = docs

    def get_sentences(self):
        sentence_set = []
        for d in self.docs:
            for p in d.paragraphs:
                for s in p.sentences:
                    sentence_set.append(s)
        return sentence_set

class Document(object):

    def __init__(self, description, paragraphs=[]):
        self.description = description
        self.paragraphs = paragraphs

class Paragraph(object):

    def __init__(self, sentences=[]):
        self.sentences = sentences

class Sentence(object):

    def __init__(self, key, text, frames=[]):
        self.key = key
        self.text = text
        self.frames = frames

class Frame(object):

    def __init__(self, name, target, roles=[]):
        self.name = name
        self.target = target
        self.roles = roles

class LexUnit(object):

    def __init__(self, name, lexunit, start, end):
        self.name = name
        self.lexunit = lexunit
        self.start = start
        self.end = end

def parse_from_xml(xml): 
    corpus = etree.fromstring(xml)
    return parse_from_root(corpus)
    
def parse_from_fileobj(f):
    doc = etree.parse(f)
    corpus = doc.getroot()
    return parse_from_root(corpus)

def parse_from_root(corpus_tag):
    name = corpus_tag.get('name')
    date = datetime.strptime(corpus_tag.get('XMLCreated'), CORPUS_DATE_FORMAT)
    docs = [parse_doc(d) for d in corpus_tag.iterdescendants(tag='document')]
    return Corpus(name, date, docs)

def parse_doc(doc_tag):
    description = doc_tag.get('description', '')
    paragraphs = [parse_paragraph(p) for p in doc_tag.iterdescendants(tag='paragraph')]
    return Document(description, paragraphs)

def parse_paragraph(par_tag):
    sentences = [parse_sentence(s) for s in par_tag.iterdescendants(tag='sentence')]
    return Paragraph(sentences)

def parse_sentence(s_tag):
    key = s_tag.get('ID')
    text = s_tag.find('text').text
    frames = [parse_frame(a, text) for a in s_tag.iterdescendants(tag='annotationSet')]
    return Sentence(key, text, frames)

def parse_frame(ann_tag, text):
    name = ann_tag.get('frameName')
    target_label = ann_tag.xpath('.//layer[@name="Target"]//label')[0]
    target = parse_label(target_label, text)
    roles = [parse_label(r, text) for r in ann_tag.xpath('.//layer[@name="FE"]//label')]
    return Frame(name, target, roles)

def parse_label(label, text):
    name = label.get('name')
    start = int(label.get('start'))
    end = int(label.get('end'))
    target = text[start:end + 1]
    return LexUnit(name, target, start, end)


# default writeln function (stdout)
def stdout(s):
    print str(s)

def dump_textual(sentence, writeln=None): 
    # inner fuction, dumps a lexical unit
    def lu_tostring(lu):
        return '%s: %s (%d, %d)' % (lu.name, lu.lexunit, lu.start, lu.end)
    
    if not writeln: writeln = stdout
    writeln('========================================')
    writeln('SENTENCE#' + str(sentence.key) + ': ' + sentence.text)
    writeln('========================================')
    for f in sentence.frames:
        writeln('FRAME: ' + f.name)
        writeln(lu_tostring(f.target))
        for r in f.roles:
            writeln('(ROLE) ' + lu_tostring(r))
        writeln('----------------------------------------')
    writeln('\n')

def dump_graphics(sentence, writeln=None):
    if not writeln: writeln = stdout
    N = len(sentence.text)

    def lu_tostring(lu, label):
        line = N * '-'
        line = line[:lu.start] + lu.lexunit + line[lu.end + 1:]
        line = line + ' ' + label
        return line

    writeln('SENTENCE#' + str(sentence.key) + ':')
    writeln('=' * N)
    writeln(sentence.text)
    writeln('=' * N)
    for f in sentence.frames:
        writeln('FRAME: ' + f.name)
        writeln(sentence.text)
        writeln(lu_tostring(f.target, 'TARGET'))
        for r in f.roles:
            writeln(lu_tostring(r, r.name))
        writeln('=' * N)
    writeln('\n')
    pass


# command line interface stuff
def print_help(): 
    print 'semafor.py -- by Giulio Petrucci'
    print ''
    print 'Usage:'
    print '\tpython semafor.py -g|[t] <input> [<output>]'
    print 
    print '-g\toutput in the graphical form'
    print '-t\toutput in textual form (default)'
    print '<input>\ta SEMAFOR 1.0 output file'
    print '<output>\tthe output file (stdout if none)'
    print ''
    print '(if you liked this help, type \'python semafor.py -h\')'

if __name__ == "__main__":
    dump = dump_textual
    writeln = stdout
    args = sys.argv[1:]

    if len(args) == 0 or args[0] == '-h':
        print_help()
        sys.exit(0)
    if args[0] == '-t':
        args = args[1:]
    if args[0] == '-g':
        dump = dump_graphics
        args = args[1:]
    if len(args) == 0:
        print_help()
        sys.exit(0)

    infile_path = args[0]
    infile = open(infile_path, 'r')
    
    outfile_path = None 
    if len(args) >0: 
        outfile_path = args[1]
    outfile = None
    if outfile_path:
        outfile = open(outfile_path, 'w')
        writeln = lambda s: outfile.write(s + '\n')
    corpus = parse_from_fileobj(infile)
    for s in corpus.get_sentences():
        dump(s, writeln)
    infile.close()
    if outfile: 
        outfile.close()
    print ' -- done -- '
    
        