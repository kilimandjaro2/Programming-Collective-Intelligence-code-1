#!/usr/bin/python

import random
from math import sqrt
from PIL import Image, ImageDraw

class bicluster:
    '''Represent the hierarchical tree.'''
    def __init__(self, vec, left = None, right = None,
                 distance = 0.0, id = None):
        self.left = left
        self.right = right
        self.vec = vec
        self.id = id
        self.distance = distance


def readfile(filename):
    lines = [line for line in file(filename)]

    # first line is the column titile
    colnames = lines[0].strip().split('\t')[1:]
    rownames = []
    data = []
    for line in lines[1:]:
        p = line.strip().split('\t')
        # first column in each row is the rowname
        rownames.append(p[0])
        # the data for this row is the remainder of the row
        data.append([float(x) for x in p[1:]])
    return rownames, colnames, data

def pearson(v1, v2):
    sum1 = sum(v1)
    sum2 = sum(v2)
    sum1Sq = sum([pow(v, 2) for v in v1])
    sum2Sq = sum([pow(v, 2) for v in v2])
    pSum = sum([v1[i] * v2[i] for i in range(len(v1))])

    num = pSum - (sum1 * sum2 / len(v1))
    den = sqrt((sum1Sq - pow(sum1, 2) / len(v1)) * \
               (sum2Sq - pow(sum2, 2) / len(v2)))
    if den == 0:
        return 0
    return 1 - num / den # sma;;er distance => more similar

def hcluster(rows, distance = pearson):
    distances = {}
    currentclustid = -1

    # clusters are initially just the rows
    clust = [bicluster(rows[i], id = i) for i in range(len(rows))]

    # until only one cluster remains
    while len(clust) > 1:
        lowestpair = (0, 1)
        closest = distance(clust[0].vec, clust[1].vec)

        # loop through every pair looking for the smallest distance
        for i in range(len(clust)):
            for j in range(i + 1, len(clust)):
                # distances is the cache of distance calculations
                if (clust[i].id, clust[j].id) not in distances:
                    distances[((clust[i].id, clust[j].id))] = \
                        distance(clust[i].vec, clust[j].vec)

                d = distances[(clust[i].id, clust[j].id)]

                if d < closest:
                    closest = d
                    lowestpair = (i, j)

        # calculate the average of the two clusters
        mergevec = [(clust[lowestpair[0]].vec[i] +
                     clust[lowestpair[1]].vec[i]) / 2.0
                    for i in range(len(clust[0].vec))]

        # create the new cluster
        newcluster = bicluster(mergevec,
                               left = clust[lowestpair[0]],
                               right = clust[lowestpair[1]],
                               distance = closest,
                               id = currentclustid)

        # cluster ids that weren't in the original set are negative
        currentclustid -= 1
        # delete the latter one first to avoid shift in index
        del clust[lowestpair[1]]
        del clust[lowestpair[0]]
        clust.append(newcluster)

    return clust[0]

def printclust(clust, labels = None, n = 0):
    '''Print clustering tree recursively.'''
    # indent to make a hiearchy layout
    for i in range(n):
        print ' ',

    if clust.id < 0:
        # negative id means that this is a branch
        print '-'
    else:
        # postive id means that this is an endpoint
        if labels == None:
            print clust.id
        else:
            print labels[clust.id]

    # now print the left and right branches
    if clust.left != None:
        printclust(clust.left, labels = labels, n = n + 1)
    if clust.right != None:
        printclust(clust.right, labels = labels, n = n + 1)

def getheight(clust):
    '''Total height of a node.'''
    # Is this an endpoint? Then the height is just 1
    if clust.left == None and clust.right == None:
        return 1

    # otherwise the height is the same of the heights of each branch
    return getheight(clust.left) + getheight(clust.right)

def getdepth(clust):
    '''Error depth of a node.'''
    # the distance of an endpoint is 0.0
    if clust.left == None and clust.right == None:
        return 0

    # the distance of a branch is the greater of its two sides
    # plus its own distance
    return max(getdepth(clust.left), getdepth(clust.right)) + clust.distance

def drawdendrogram(clust, labels, jpeg = 'clusters.jpg'):
    # height and width
    h = getheight(clust) * 20
    w = 1200
    depth = getdepth(clust)

    # width is fixed, so scale distances accordingly
    scaling = float(w - 150)/depth

    # create a new image with a white background
    img = Image.new('RGB', (w, h), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    draw.line((0, h/2, 10, h/2), fill = (255, 0, 0))

    # draw the first node
    drawnode(draw, clust, 10, h/2, scaling, labels)
    img.save(jpeg, 'JPEG')

def drawnode(draw, clust, x, y, scaling, labels):
    if clust.id < 0:
        h1 = getheight(clust.left) * 20
        h2 = getheight(clust.right) * 20
        top = y - (h1 + h2) / 2
        bottom = y + (h1 + h2) / 2
        # line length
        ll = clust.distance * scaling
        # vertical line from this cluster to children
        draw.line((x, top + h1/2, x, bottom - h2/2), fill = (255, 0, 0))
        # horizontal line to left item
        draw.line((x,top + h1/2, x + ll, top + h1/2), fill = (255, 0, 0))
        # horizontal line to right item
        draw.line((x, bottom - h2/2, x + ll, bottom - h2/2), fill = (255, 0, 0))
        # call the function to draw the left and right nodes
        drawnode(draw, clust.left, x + ll, top + h1/2, scaling, labels)
        drawnode(draw, clust.right, x + ll, bottom - h2/2, scaling, labels)
    else:
        # if this end point, draw the item label
        draw.text((x + 5, y - 7), labels[clust.id], (0, 0, 0))

def rotatematrix(data):
    newdata = []
    for i in range(len(data[0])):
        newrow = [data[j][i] for j in range(len(data))]
        newdata.append(newrow)
    return newdata

def kcluster(rows, distance = pearson, k = 4):
    '''K-means clustering.'''
    # determine the minimum and maximum values for each point
    ranges = [(min(row[i] for row in rows), max([row[i] for row in rows]))
              for i in range(len(rows[0]))]

    # create k randomly placed centroids
    clusters = [[random.random() * (ranges[i][1]-ranges[i][0]) + ranges[i][0]
                 for i in range(len(rows[0]))] for j in range(k)]

    lastmatches = None
    for t in range(100):
        print "Iteration %d" % t
        bestmatches = [[] for i in range(k)]

        # find which centroid is the closest for each row
        for j in range(len(rows)):
            row = rows[j]
            bestmatch = 0
            for i in range(k):
                d = distance(clusters[i], row)
                if d < distance(clusters[bestmatch], row):
                    bestmatch = i
            bestmatches[bestmatch].append(j)

        # if the results are the same as last time, this is complete
        if bestmatches == lastmatches:
            break
        lastmatches = bestmatches

        # move the entroids to the average of their members
        for i in range(k):
            avgs = [0.0] * len(rows[0])
            if len(bestmatches[i]) > 0:
                for rowid in bestmatches[i]:
                    for m in range(len(rows[rowid])):
                        avgs[m] += rows[rowid][m]
                for j in range(len(avgs)):
                    avgs[j] /= len(bestmatches[i])
                clusters[i] = avgs
    return bestmatches

def tanamoto(v1, v2):
    '''Tanimoto coefficient (0.0 - 1.0).'''
    c1, c2, shr = 0, 0, 0
    for i in range(len(v1)):
        if v1[i] != 0:
            c1 += 1
        if v2[i] != 0:
            c2 += 1
        if v1[i] != 0 and v2[i] != 0:
            shr += 1
    return 1.0 - float(shr)/(c1 + c2 - shr)

def scaledown(data, distance = pearson, rate = 0.1):
    '''multidimensional scaling'''
    n = len(data)

    # the real distance between every pair of items
    realdist = [[distance(data[i], data[j]) for j in range(n)]
                for i in range(n)]

    # randomly initialize the starting points of the locations in 2D
    loc = [[random.random(), random.random()] for i in range(n)]
    fakedist = [[0.0 for j in range(n)] for i in range(n)]

    lasterror = None
    for m in range(1000):
        # find projected distance
        for i in range(n):
            for j in range(n):
                fakedist[i][j] = sqrt(sum([pow(loc[i][x] - loc[j][x], 2)
                                           for x in range(len(loc[i]))]))

        # move points
        grad = [[0.0, 0.0] for i in range(n)]

        totalerror = 0
        for k in range(n):
            for j in range(n):
                if j == k:
                    continue
                # the error is percent difference between the distances
                errorterm = (fakedist[j][k] - realdist[j][k])/realdist[j][k]

                # each point needs to be moved away from or towards the other
                # point in proportion to how much error it has
                grad[k][0] += ((loc[k][0] - loc[j][0])/fakedist[j][k]) *\
                              errorterm
                grad[k][1] += ((loc[k][1] - loc[j][1])/fakedist[j][k]) *\
                              errorterm

                # keep track of the total error
                totalerror += abs(errorterm)
        print totalerror

        # if the answer got worse by moving the points, we are done
        if lasterror and lasterror < totalerror:
            break
        lasterror = totalerror

        # move eawch of the points by the learning rate times the gradient
        for k in range(n):
            loc[k][0] -= rate * grad[k][0]
            loc[k][1] -= rate * grad[k][1]
    return loc

def draw2d(coords, labels, jpeg = 'mds2d.jpg'):
    img = Image.new('RGB', (4000, 4000), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    for i in range(len(coords)):
        x = (coords[i][0] + 0.5) * 1000
        y = (coords[i][1] + 0.5) * 1000
        draw.text((x, y), labels[i], (0, 0, 0))
    img.save(jpeg, 'JPEG')


if __name__ == "__main__":
    ## data from blogdata.txt
    blognames, words, data = readfile('blogdata.txt')

    # blog clustering
    # clust = hcluster(data)
    # printclust(clust, labels = blognames)
    # drawdendrogram(clust, blognames, jpeg = 'blogclust.jpg')

    # word clustering
    # rdata = rotatematrix(data)
    # wordclust = hcluster(rdata)
    # drawdendrogram(wordclust, words, jpeg = 'wordclust.jpg')

    # K-means
    # kclust = kcluster(data, k = 10)
    # print [[blognames[r] for r in kclust[c]] for c in range(len(kclust))]

    ## data from zebo.txt
    # wants, people, data = readfile('zebo.txt')
    # clust = hcluster(data, distance = tanamoto)
    # drawdendrogram(clust, wants, jpeg = 'zebo.jpg')

    ## multidimensional scaling
    coords = scaledown(data)
    draw2d(coords, blognames, jpeg = 'blogs2d.jpg')
