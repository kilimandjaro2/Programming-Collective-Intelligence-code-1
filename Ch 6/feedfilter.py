#!/usr/bin/python

import feedparser
import re
import docclass

# take a filename of url of a blog feed and classifies the entries
def read(feed, classifier):
    # get feed entries and loop over them
    f = feedparser.parse(feed)
    for entry in f['entries']:
        print
        print '-----'
        # print the contents of the entry
        print 'Title:   ' + entry['title'].encode('utf-8')
        print 'Publisher:   ' + entry['publisher'].encode('utf-8')
        print
        print entry['summary'].encode('utf-8')

        # combine all the text to create one item for the classifier
        fulltext = '%s\n%s\n%s' % (entry['title'], entry['publisher'],
                                   entry['summary'])

        # print the best guess at the current category
        # print 'Guess: ' + str(classifier.classify(fulltext))
        print 'Guess: ' + str(classifier.classify(entry))

        # ask the user to specify the correct category and train on that
        cl = raw_input('Enter category: ')
        # classifier.train(fulltext, cl)
        classifier.train(entry, cl)

def entryfeatures(entry):
    splitter = re.compile('\\W*')
    f = {}

    # extract the title words and annotate
    titlewords = [s.lower() for s in splitter.split(entry['title'])
                  if len(s) > 2 and len(s) < 20]
    for w in titlewords:
        f['Title:' + w] = 1

    # extract the summary words
    summarywords = [s.lower() for s in splitter.split(entry['summary'])
                    if len(s) > 2 and len(s) < 20]

    # count uppercase words
    uc = 0
    for i in range(len(summarywords)):
        w = summarywords[i]
        f[w] = 1
        if w.isupper():
            uc += 1

        # get word pairs in summar as features
        if i < len(summarywords) - 1:
            twowords = ' '.join(summarywords[i:i+1])
            f[twowords] = 1

    # keep creator and publisher whole
    f['publisher:' + entry['publisher']] = 1

    # UPPERCASE is a virtual word flagging too much shouting
    if float(uc)/len(summarywords) > 0.3:
        f['UPPERCASE'] = 1

    return f


if __name__ == "__main__":
    # cl = docclass.FisherClassifier(docclass.getwords)
    cl = docclass.FisherClassifier(entryfeatures)

    cl.setdb('python_feed.db')

    # four categories:
    # 1. programming language
    # 2. Monty Python
    # 3. python snakes
    # 4. everythong
    read('python_search.xml', cl)
