#!/usr/bin/python

import re
import math
import sqlite3

def getwords(doc):
    splitter = re.compile('\\W*')
    # split the words by non-alpha characters
    words = [s.lower() for s in splitter.split(doc)
             if len(s) > 2 and len(s) < 20]

    # return the unique set of words only
    return dict([(w, 1) for w in words])


class Classifier:
    def __init__(self, getfeatures, filename = None):
        # counts of feature/category combinations
        # self.fc = {}
        # counts of documents in each category
        # self.cc = {}
        self.getfeatures = getfeatures

    def incf(self, f, cat):
        '''increase the count of a feature/category pair'''
        # nested dict needs initialize
        # self.fc.setdefault(f, {})
        # self.fc[f].setdefault(cat, 0)
        # self.fc[f][cat] += 1

        count = self.fcount(f, cat)
        if count == 0:
            self.con.execute('INSERT INTO fc VALUES ("%s", "%s", 1)' % (f, cat))
        else:
            self.con.execute(
                'UPDATE fc SET count = %d \
                 WHERE feature = "%s" AND category = "%s"' \
                 % (count + 1, f, cat))

    def incc(self, cat):
        '''increase the count of a category'''
        # self.cc.setdefault(cat, 0)
        # self.cc[cat] += 1

        count = self.catcount(cat)
        if count == 0:
            self.con.execute('INSERT INTO cc VALUES ("%s", 1)' % (cat))
        else:
            self.con.execute('UPDATE cc SET count = %d WHERE category = "%s"' \
                             % (count + 1, cat))

    def fcount(self, f, cat):
        '''the number of times a feature has appeared in a category'''
        # if f in self.fc and cat in self.fc[f]:
        #     return float(self.fc[f][cat])
        # return 0.0

        res = self.con.execute(
            'SELECT count FROM fc WHERE feature = "%s" AND category = "%s"' \
            % (f, cat)).fetchone()
        if res == None:
            return 0.0
        return float(res[0])

    def catcount(self, cat):
        '''the number of items in a category'''
        # if cat in self.cc:
        #     return float(self.cc[cat])
        # return 0.0

        res = self.con.execute('SELECT count FROM cc WHERE category = "%s"' \
                                % (cat)).fetchone()
        if res == None:
            return 0.0
        return float(res[0])

    def totalcount(self):
        '''the total number of items'''
        # return sum(self.cc.values())

        res = self.con.execute('SELECT SUM(count) FROM cc').fetchone()
        if res == None:
            return 0
        return res[0]

    def categories(self):
        '''the list of all categories'''
        # return self.cc.keys()

        cur = self.con.execute('SELECT category FROM cc')
        return [d[0] for d in cur]

    def train(self, item, cat):
        features = self.getfeatures(item)
        # increment the count for every feature with this category
        for f in features:
            self.incf(f, cat)

        # increment the count for this category
        self.incc(cat)

        self.con.commit()

    def fprob(self, f, cat):
        '''calculate conditional Pr(f | cat)'''
        if self.catcount(cat) == 0:
            return 0
        # the total number of times this feature appeared in this
        # category divided by the total number of items in this category
        return self.fcount(f, cat)/self.catcount(cat)

    def weightedprob(self, f, cat, prf, weight = 1.0, ap = 0.5):
        '''combine assumed probability'''
        # calculate current probability
        basicprob = prf(f, cat)

        # count the number of times the feature has appeared in all categories
        totals = sum([self.fcount(f, c) for c in self.categories()])

        # calculate the weighted average
        bp = ((weight * ap) + (totals * basicprob))/(weight + totals)
        return bp

    def setdb(self, dbfile):
        self.con = sqlite3.connect(dbfile)
        self.con.execute(
            'CREATE TABLE if not exists fc(feature, category, count)')
        self.con.execute('CREATE TABLE if not exists cc(category, count)')


class NaiveBayes(Classifier):
    def __init__(self, getfeatures):
        Classifier.__init__(self, getfeatures)
        self.thresholds = {}

    def docprob(self, item, cat):
        '''calculate Pr(doc | cat)'''
        features = self.getfeatures(item)

        # multiple the probabilities of all the features together
        p = 1
        for f in features:
            p *= self.weightedprob(f, cat, self.fprob)
        return p

    def prob(self, item, cat):
        '''calculate Pr(cat | doc)'''
        catprob = self.catcount(cat)/self.totalcount()
        docprob = self.docprob(item, cat)
        return docprob * catprob

    def setthreshold(self, cat, t):
        self.thresholds[cat] = t

    def getthreshold(self, cat):
        if cat not in self.thresholds:
            return 1.0
        return self.thresholds[cat]

    def classify(self, item, default = None):
        probs = {}
        # find the category with the highest probability
        max = 0.0
        for cat in self.categories():
            probs[cat] = self.prob(item, cat)
            if probs[cat] > max:
                max = probs[cat]
                best = cat

        # make sure the probability exceeds threshold * next best
        for cat in probs:
            if cat == best:
                continue
            if probs[cat]*self.getthreshold(best) > probs[best]:
                return default
        return best

class FisherClassifier(Classifier):
    def __init__(self, getfeatures):
        Classifier.__init__(self, getfeatures)
        self.minimums = {}

    def cprob(self, f, cat):
        '''calculate Pr(cat | f)'''
        # the frequency of this feature in this category
        clf = self.fprob(f, cat)
        if clf == 0:
            return 0

        # the frequency of this feature in all the categories
        freqsum = sum([self.fprob(f, c) for c in self.categories()])

        # the probability is the frequency in this category divided by
        # the overall frequency
        p = clf/freqsum

        return p

    def fisherprob(self, item, cat):
        # multiply all the probabilities together
        p = 1
        features = self.getfeatures(item)
        for f in features:
            p *= self.weightedprob(f, cat, self.cprob)

        # take the nature log and multiply by -2
        fscore = -2 * math.log(p)

        # use the inverse chi2 function to get a probability
        return self.invchi2(fscore, len(features) * 2)

    def invchi2(self, chi, df):
        m = chi / 2.0
        sum = term = math.exp(-m)
        for i in range(1, df/2):
            term *= m / i
            sum += term
        return min(sum, 1.0)

    def setminimum(self, cat, min):
        self.minimums[cat] = min

    def getminimum(self, cat):
        if cat not in self.minimums:
            return 0
        return self.minimums[cat]

    def classify(self, item, default = None):
        # loop through looking for the best result
        best = default
        max = 0.0
        for c in self.categories():
            p = self.fisherprob(item, c)
            # make sure it exceeds its minimum
            if p > self.getminimum(c) and p > max:
                best = c
                max = p
        return best


def sampletrain(cl):
    cl.train('Nobody owns the water.', 'good')
    cl.train('the quick rabbit jumps fences', 'good')
    cl.train('buy pharmaceuticals now', 'bad')
    cl.train('make quick money at the online casino', 'bad')
    cl.train('the quick brown fox jumps', 'good')


if __name__ == "__main__":
    ## test case
    # cl = Classifier(getwords)
    # cl.train('the quick quick brown fox jumps over the lazy dog', 'good')
    # cl.train('make quick money in the online casino', 'bad')
    # print 'Class 1: ', cl.fcount('quick', 'good') # 1.0
    # print 'Class 2: ', cl.fcount('quick', 'bad') # 1.0

    # cl = Classifier(getwords)
    # sampletrain(cl)
    # print "Basic probability", cl.fprob('money', 'good')
    # print "Weighted probability", cl.weightedprob('money', 'good', cl.fprob)

    cl = NaiveBayes(getwords)
    cl.setdb('testNaiveBayes.db')
    sampletrain(cl)
    print cl.prob('quick rabbit', 'good')
    print cl.prob('quick rabbit', 'bad')
    print 'quick rabbit ->', cl.classify('quick rabbit', default = 'unknown')
    print 'quick money ->', cl.classify('quick money', default = 'unknown')
    cl.setthreshold('bad', 3.0)
    print 'quick money (thresold = 3.0) ->', \
          cl.classify('quick money', default = 'unknown')

    cl = FisherClassifier(getwords)
    cl.setdb('testFisher.db')
    sampletrain(cl)
    print cl.fisherprob('quick rabbit', 'good')
    print cl.fisherprob('quick rabbit', 'bad')
    print 'quick rabbit ->', cl.classify('quick rabbit', default = 'unknown')
    print 'quick money ->', cl.classify('quick money', default = 'unknown')
    cl.setminimum('bad', 0.8)
    print 'quick money (minimum = 0.8) ->', \
          cl.classify('quick money', default = 'unknown')
