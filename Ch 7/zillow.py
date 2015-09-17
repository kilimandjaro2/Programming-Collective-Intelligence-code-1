#!/usr/bin/python

import xml.dom.minidom
import urllib2
import treepredict

zwskey = "X1-ZWz1chwxis15aj_9skq6"

def getaddressdata(address, city):
    escad = address.replace(' ', '+')

    # construct the url
    url = 'http://www.zillow.com/webservice/GetDeepSearchResults.htm?'
    url += 'zws-id=%s&address=%s&citystatezip=%s' % (zwskey,escad,city)

    # parse resulting xml
    doc = xml.dom.minidom.parseString(urllib2.urlopen(url).read())
    code = doc.getElementsByTagName('code')[0].firstChild.data

    # code 0 means success; otherwise, there was an error
    if code != '0':
        return None

    # extract the info about this property
    try:
        zipcode = doc.getElementsByTagName('zipcode')[0].firstChild.data
        use = doc.getElementsByTagName('useCode')[0].firstChild.data
        year = doc.getElementsByTagName('yearBuilt')[0].firstChild.data
        bath = doc.getElementsByTagName('bathrooms')[0].firstChild.data
        bed = doc.getElementsByTagName('bedrooms')[0].firstChild.data
        rooms = doc.getElementsByTagName('totalRooms')[0].firstChild.data
        price = doc.getElementsByTagName('amount')[0].firstChild.data
    except:
        return None

    return zipcode, use, int(year), float(bath), int(bed), int(rooms), price

def getpricelist():
    l1 = []
    for line in file('addresslist.txt'):
        data = getaddressdata(line.strip(), 'Cambridge+MA')
        l1.append(data)
    return l1


if __name__ == "__main__":
    housedata = getpricelist()
    housedata = [data for data in housedata if data != None]
    housetree = treepredict.buildtree(housedata, treepredict.variance)
    treepredict.drawtree(housetree, 'housetree.jpg')
