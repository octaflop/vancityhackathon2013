# coding: utf-8
import urllib2
from urllib2 import HTTPError
from StringIO import StringIO as stio
from bs4 import BeautifulSoup
import zipfile
import pprint
import simplejson

def robot():
    robot = urllib2.build_opener()
    robot.addheaders = [('User-agent', 'Mozilla/5.0')]

    return robot


def gorobot(url):
    try:
        infile = robot().open(url).read()
        soup = BeautifulSoup(infile)
    except HTTPError:
        soup = False

    return soup


def gardener(treezipurl):
    infile = robot().open(treezipurl)
    page = infile.read()

    return page


def harvester(treezipurl):
    tfs = []
    pprint.pprint("Fetching and unzipping the trees from: %s" % treezipurl)
    for treejsonf in zipfile.ZipFile(stio(gardener(treezipurl))).namelist():
        with open(treejsonf) as tf:
            tdb = simplejson.load(tf)
        tfs.append(tdb)

    return tfs


def photographer(treehtml):
    img_src = treehtml.find_all(class_="infobox")[0].find_next("img")['src']
    img_title = treehtml.title.getText().replace(" - Wikipedia, the free encyclopedia", "").replace("_", "")
    pprint.pprint("For the %s, I got this image url: %s" % (img_title, img_src))
    imgf = robot().open("http:%s" % img_src).read()
    with open("./%s.jpg" % img_title, "w") as f:
        f.write(imgf)
        pprint.pprint("Wrote: ./%s.jpg" % img_title)
    f.close()

    return img_src


def researcher(treeset):
    wikiurl = 'http://en.wikipedia.org/w/index.php?title=%s&printable=yes'
    fetchlist = [wikiurl % tree.capitalize().replace(" ", "_") for tree in treeset]
    pprint.pprint("Hello, researcher here. I have %s trees to look at" % len(fetchlist))
    dropped, got, tried, photos = [], [], [], []
    for treeurl in fetchlist:
        try:
            tried.append(treeurl)
            pprint.pprint("Fetching: %s" % (treeurl))
            img_src = photographer(gorobot(treeurl))
            photos.append(img_src)
            pprint("Photo? %s" % photos[len(photos) - 1])
            got.append(treeurl)
            pprint.pprint("Fetched & Photograped: %s, & %s" % (treeurl, photos[len(photos - 1)]))
        except:
            dropped.append(treeurl)
    pprint.pprint("I tried: %(tr)s, dropped: %(dr)s, and got: %(go)s. Which I returned" % {
        "tr": len(tried),
        "dr": len(dropped),
        "go": len(got)
        })

    return photos, len(got)


def logstuff(**kwargs):
    treeset = kwargs['treeset']
    photos = kwargs['photos']
    researched = kwargs['researched']

    def _logfile(logvar, fn):
        with open("./%s.log" % fn, "w") as f:
            f.write(repr(logvar))
        f.close()
        return "./%s.log" % logvar

    return (_logfile(treeset, "treeset"), _logfile(photos, "photos"), _logfile(researched, "researched"))


def querynames(tdbs):
    """
    Queries the db for COMMON_NAME and returns set of all names
    """
    treeset = set()
    names = [j["COMMON_NAME"] for j in tdbs]
    for treename in names:
        treeset.add(treename)
    return treeset


def main():
    # TODO ☺
    # vanparksurl = "ftp://webftp.vancouver.ca/opendata/json/weekendplayfieldstatus.json"
    vantreeurl = "ftp://webftp.vancouver.ca/OpenData/json/json_street_trees.zip"
    tdb = harvester(vantreeurl)
    # Woah
    tdbs = [treejson for db in tdb for treejson in db]
    treeset = querynames(tdbs)
    len(treeset)
    photos, researched = researcher(treeset)
    pprint.pprint(logstuff(photos=photos, researched=researched, treeset=treeset))

if __name__ == "__main__":
    main()
