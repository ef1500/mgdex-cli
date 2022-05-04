# Mangadex API
# Written by ef1500
# So I can download ALL the yuri!

import os
import json as js
import regex as re
import requests as rx
import time as tm

from requests_futures.sessions import FuturesSession
from concurrent.futures import ThreadPoolExecutor
from slugify import slugify

# Resolve Author Information
class Author:
    def __init__(self, aid):
        rq = rx.get("https://api.mangadex.org/author/{ax}".format(ax = aid)) 
        rqd = js.loads(rq.text)

        self.author_id = aid

        self.name = rqd["data"]["attributes"]["name"]
        self.bio = rqd["data"]["attributes"]["biography"]
        self.twitter_handle = rqd["data"]["attributes"]["twitter"]
        self.pixiv = rqd["data"]["attributes"]["pixiv"]
        self.melonBook = rqd["data"]["attributes"]["melonBook"]
        self.fanBox = rqd["data"]["attributes"]["fanBox"]
        self.booth = rqd["data"]["attributes"]["booth"]
        self.nicoVideo = rqd["data"]["attributes"]["nicoVideo"]
        self.skeb = rqd["data"]["attributes"]["skeb"]
        self.fantia = rqd["data"]["attributes"]["fantia"]
        self.tumblr = rqd["data"]["attributes"]["tumblr"]
        self.youtube = rqd["data"]["attributes"]["youtube"]
        self.weibo = rqd["data"]["attributes"]["weibo"]
        self.naver = rqd["data"]["attributes"]["naver"]
        self.website = rqd["data"]["attributes"]["website"]

        self.works = [] 
        
        # Put the IDs of all the author/illustrations into a list
        # Actually, I just realized, I could just put Manga Class Objects In here
        for work in rqd["data"]["relationships"]:
            if work["type"] == "manga":
                self.works.append(work["id"])

        

# Resolve Scanlation Group Name And Additional Information
class Scanlation_Group:
    def __init__(self, sid):
        rq = rx.get("https://api.mangadex.org/group/{sx}".format(sx = sid))
        rqd = js.loads(rq.text)

        self.name = rqd["data"]["attributes"]["name"]
        self.website = rqd["data"]["attributes"]["website"]
        self.ircServer = rqd["data"]["attributes"]["ircServer"]
        self.ircChannel = rqd["data"]["attributes"]["ircChannel"]
        self.discord_server = rqd["data"]["attributes"]["discord"]
        self.twitter_handle = rqd["data"]["attributes"]["twitter"]
        self.description = rqd["data"]["attributes"]["description"]
        self.contact_email = rqd["data"]["attributes"]["contactEmail"]

class Manga:
    def __init__(self, id):
        rq = rx.get("https://api.mangadex.org/manga/{ix}?includes[]=author&includes[]=artist&includes[]=cover_art".format(ix = id))
        rqd = js.loads(rq.text)

        self.title = rqd["data"]["attributes"]["title"]["en"]
        self.alt_titles = rqd["data"]["attributes"]["altTitles"]

        self.description = ""
        try:
            self.description = rqd["data"]["attributes"]["description"]["en"]
        except:
            pass

        self.trackers = {
            "Kitsu" : "",
            "Anilist" : "",
            "MAL" : "",
            "AnimePlanet" : "",
            "MangaUpdates" : ""
        }

        if "kt" in rqd["data"]["attributes"]["links"]:
            self.trackers["Kitsu"] = "https://kitsu.io/manga/" + rqd["data"]["attributes"]["links"]["kt"]
        if "al" in rqd["data"]["attributes"]["links"]:
            self.trackers["Anilist"] = "https://anilist.co/manga/" + rqd["data"]["attributes"]["links"]["al"]
        if "mal" in rqd["data"]["attributes"]["links"]:
            self.trackers["MAL"] = "https://myanimelist.net/manga/" + rqd["data"]["attributes"]["links"]["mal"]
        if "ap" in rqd["data"]["attributes"]["links"]:
            self.trackers["AnimePlanet"] = "https://anime-planet.com/manga/" + rqd["data"]["attributes"]["links"]["ap"]
        if "mu" in rqd["data"]["attributes"]["links"]:
            self.trackers["MangaUpdates"] = "https://www.mangaupdates.com/series.html?id=" + rqd["data"]["attributes"]["links"]["mu"]


        # Mangadex has various ways of storing tags
        # Genre and Theme

        self.genres = []
        self.themes = []
        for tag in rqd["data"]["attributes"]["tags"]:
            if tag["attributes"]["group"] == "genre":
                self.genres.append(([tag["attributes"]["name"]["en"]], tag["id"]))
            if tag["attributes"]["group"] == "theme":
                self.themes.append(([tag["attributes"]["name"]["en"]], tag["id"]))

        self.status = rqd["data"]["attributes"]["status"]
        self.illustrator = ""
        self.author = ""

        self.illustobj = None
        self.authorobj = None

        for mangaka in rqd["data"]["relationships"]:
            if mangaka["type"] == "author":
                self.authorobj = Author(mangaka["id"])
                self.author = mangaka["attributes"]["name"]
            if mangaka["type"] == "artist":
                self.illustobj = Author(mangaka["id"])
                self.illustrator = mangaka["attributes"]["name"]
    
    # Function to write all of the Manga Information to a text file
    def writeData(self, folderpath):
        with open(os.path.join(folderpath, "info.txt"), "a+", encoding='utf8') as datawriter:
            datawriter.write("Title: " + self.title + '\n' + '\n')
            datawriter.write("Alt Titles " + '\n')
            for alt_title in self.alt_titles:
                t_lst = list(alt_title.items())
                datawriter.writelines(t_lst[0][0] + ' : ' + t_lst[0][1] + '\n')

            datawriter.write('\n')
            datawriter.writelines(["Author: ", self.author + '\n'])
            datawriter.writelines(["Illustrator: ", self.illustrator + '\n'])
            datawriter.write('\n')

            datawriter.writelines(['\n', '\n'])
            datawriter.write("Description "+'\n')
            datawriter.write(self.description +'\n')

            datawriter.writelines(['\n', '\n'])

            datawriter.write("Genres " + '\n')
            for genre in self.genres:
                datawriter.write(genre[0][0] + ' : ' + genre[1] + '\n')
            datawriter.write('\n')

            datawriter.write('\n')

            datawriter.write("Themes " + '\n')
            for theme in self.themes:
                datawriter.write(theme[0][0] + ' : ' + theme[1] + '\n')
            datawriter.write('\n')

            datawriter.write("Trackers:" + '\n')

            ttrackers = []
            for key, val in self.trackers.items(): 
                ttrackers.append([key, val]) 
            for tracker in ttrackers:
                datawriter.writelines([tracker[0] + ' : ', tracker[1] + '\n']) 


            datawriter.close()

            

# Class For getting Cover Art
class Cover_Art:
    def __init__(self, id):
        rq = rx.get("https://api.mangadex.org/cover?limit=100&manga%5B%5D={ix}&order%5BcreatedAt%5D=asc&order%5BupdatedAt%5D=asc&order%5Bvolume%5D=asc".format(ix = id))
        rqd = js.loads(rq.text)

        self.covers = []
        for cover in rqd["data"]:
            coverlink = "https://uploads.mangadex.org/covers/{ix}/{iy}".format(ix = id, iy = cover["attributes"]["fileName"])
            saveAsFilename = "Vol_{v}.jpg".format(v = cover["attributes"]["volume"])
            self.covers.append((saveAsFilename, coverlink))
   
    def DownloadCovers(self, path):
        folderpath = os.path.join(path, "covers")
        os.mkdir(folderpath)
        for cover in self.covers:
            image_data = rx.get(cover[1])
            fx = open(os.path.join(folderpath, cover[0]), "wb")
            fx.write(image_data.content)
            fx.close()


class Chapter:
    def __init__(self, ch_id, vol, ch, title, pages, scanlationGroup, publishtime):
        self.volume = vol
        self.chapter = ch
        self.title = title
        self.pages = pages
        self.chapter_id = ch_id
        self.publishAt = publishtime
        self.scanlation_group = scanlationGroup

        # Get Chapter Data
        # If it fails whilst in the class, then the frontend will be responsible for handling
        # The Failure
        rq = rx.get("https://api.mangadex.org/at-home/server/{cid}".format(cid = self.chapter_id)) 
        rqd = js.loads(rq.text)

        if rqd["result"] == "error":
            print("Ran into a timeout! Waiting 60 Seconds before resuming operation...")
            tm.sleep(60)
            rq = rx.get("https://api.mangadex.org/at-home/server/{cid}".format(cid = self.chapter_id))
            rqd = js.loads(rq.text)


        self.chapter_hash = rqd["chapter"]["hash"]
        self.base_url = rqd["baseUrl"]

        self.page_data = []

        for ch_pages in rqd["chapter"]["data"]:
            self.page_data.append((ch_pages, "{bu}/data/{h}/{pg}".format(bu = self.base_url, h = self.chapter_hash, pg = ch_pages))) 

    def DownloadChapter(self, path, folderformat):
        #Folder Formatting
        #%Vl - Volume
        #%Ch - Chapter Number
        #%Ci - Chapter ID
        #%Ct - Chapter Title
        #%Sg - Scanlation Group

        #Ex. Vol-%Vl_Ch-%Ch_%Ct
        replacewith = lambda ix, pt, replacewith : re.sub(pt, replacewith, ix, re.IGNORECASE)
        
        folderformat = replacewith(folderformat, '%Vl', self.volume)
        folderformat = replacewith(folderformat, '%Ch', self.chapter)
        folderformat = replacewith(folderformat, '%Ci', self.chapter_id)
        folderformat = replacewith(folderformat, '%Ct', slugify(self.title, allow_unicode=True))
        folderformat = replacewith(folderformat, '%Sg', slugify(self.scanlation_group.name, allow_unicode=True)) 

        # Make the directory for the chapter
        folderpath = os.path.join(path, folderformat)
        os.mkdir(folderpath)

        def downloadPage(pgs, ses):
            image_data = ses.get(pgs[1])
            img_dat = image_data.result()
            with open(os.path.join(folderpath, pgs[0]), "wb") as f:
                f.write(img_dat.content)

        # See line 251 for explanation why this isn't os.cpu_count()*2
        session = FuturesSession(max_workers=os.cpu_count())
        for pgs in self.page_data:
            downloadPage(pgs, session)

# Get The Chapter List
# And for each Chapter, Get all of the Proper Files
class Chapters:
    def __init__(self, id):
        # NOTE: If there's more than 100 chapters, then offset will have to be used
        # To grab the rest of the chapters.
        self.indexURL = "https://api.mangadex.org/chapter?limit=100&manga={ix}&translatedLanguage%5B%5D=en&contentRating%5B%5D=safe&contentRating%5B%5D=suggestive&contentRating%5B%5D=erotica&contentRating%5B%5D=pornographic&includeFutureUpdates=1&order%5BcreatedAt%5D=asc&order%5BupdatedAt%5D=asc&order%5BpublishAt%5D=asc&order%5BreadableAt%5D=asc&order%5Bvolume%5D=asc&order%5Bchapter%5D=asc"
        self.indexOldestURL = "https://api.mangadex.org/chapter?limit=1&manga={ix}&translatedLanguage%5B%5D=en&contentRating%5B%5D=safe&contentRating%5B%5D=suggestive&contentRating%5B%5D=erotica&contentRating%5B%5D=pornographic&includeFutureUpdates=1&order%5BcreatedAt%5D=asc&order%5BupdatedAt%5D=asc&order%5BpublishAt%5D=asc&order%5BreadableAt%5D=asc&order%5Bvolume%5D=asc&order%5Bchapter%5D=asc"
        self.indexLatestURL = "https://api.mangadex.org/chapter?limit=1&manga={ix}&translatedLanguage%5B%5D=en&contentRating%5B%5D=safe&contentRating%5B%5D=suggestive&contentRating%5B%5D=erotica&contentRating%5B%5D=pornographic&includeFutureUpdates=1&order%5BcreatedAt%5D=desc&order%5BupdatedAt%5D=desc&order%5BpublishAt%5D=asc&order%5BreadableAt%5D=desc&order%5Bvolume%5D=desc&order%5Bchapter%5D=desc"

        self.manga_id = id

        self.chapter_list = []

    # Slap the indexer into a function so that we don't have to wait so long just to index the latest chapter
    def indexAllChapters(self):

        # NOTE: If there's more than 100 chapters, then offset will have to be used
        # To grab the rest of the chapters.
        rq = rx.get(self.indexURL.format(ix = self.manga_id))
        rqd = js.loads(rq.text)

        for chp in rqd["data"]:
            chp_id = chp["id"]

            volume = chp["attributes"]["volume"]
            chapter = chp["attributes"]["chapter"]
            title = chp["attributes"]["title"]

            if volume == None:
                volume = "No_Volume"
            if chapter == None:
                chapter = "Unknown Chapter"
            if title == None:
                title = ""

            pages = chp["attributes"]["pages"]

            pubTime = chp["attributes"]["publishAt"]

            scanlation_group = None
            for relation in chp["relationships"]:
                if relation["type"] == "scanlation_group":
                    scanlation_group = Scanlation_Group(relation["id"])

            self.chapter_list.append(Chapter(chp_id, volume, chapter, title, pages, scanlation_group, pubTime)) 

            collected_chapters = rqd["limit"]
            offset = rqd["limit"]
            while collected_chapters <= rqd["total"]:
                rq = rx.get("https://api.mangadex.org/chapter?limit=100&offset={ox}&manga={ix}&translatedLanguage%5B%5D=en&contentRating%5B%5D=safe&contentRating%5B%5D=suggestive&contentRating%5B%5D=erotica&contentRating%5B%5D=pornographic&includeFutureUpdates=1&order%5BcreatedAt%5D=asc&order%5BupdatedAt%5D=asc&order%5BpublishAt%5D=asc&order%5BreadableAt%5D=asc&order%5Bvolume%5D=asc&order%5Bchapter%5D=asc".format(ox = offset, ix = id))
                rqd = js.loads(rq.text)

                for chp in rqd["data"]:
                    chp_id = chp["id"]

                    volume = chp["attributes"]["volume"]
                    chapter = chp["attributes"]["chapter"]
                    title = chp["attributes"]["title"]

                    if volume == None:
                        volume = "No_Volume"
                    if chapter == None:
                        chapter = "Unknown Chapter"
                    if title == None:
                        title = ""

                    pages = chp["attributes"]["pages"]

                    pubTime = chp["attributes"]["publishAt"]

                    scanlation_group = ""
                    for relation in chp["relationships"]:
                        if relation["type"] == "scanlation_group":
                            scanlation_group = Scanlation_Group(relation["id"]).name

                    self.chapter_list.append(Chapter(chp_id, volume, chapter, title, pages, scanlation_group, pubTime)) 
                collected_chapters += rqd["limit"]
                offset += rqd["limit"]

    def indexLatestChapter(self):
        rq = rx.get(self.indexLatestURL.format(ix = self.manga_id))
        rqd = js.loads(rq.text)

        for chp in rqd["data"]:
            chp_id = chp["id"]

            volume = chp["attributes"]["volume"]
            chapter = chp["attributes"]["chapter"]
            title = chp["attributes"]["title"]

            if volume == None:
                volume = "No_Volume"
            if chapter == None:
                chapter = "Unknown Chapter"
            if title == None:
                title = ""

            pages = chp["attributes"]["pages"]

            pubTime = chp["attributes"]["publishAt"]

            scanlation_group = None
            for relation in chp["relationships"]:
                if relation["type"] == "scanlation_group":
                    scanlation_group = Scanlation_Group(relation["id"])

            self.chapter_list.append(Chapter(chp_id, volume, chapter, title, pages, scanlation_group, pubTime)) 

    def indexOldestChapter(self):
        rq = rx.get(self.indexOldestURL.format(ix = self.manga_id))
        rqd = js.loads(rq.text)

        for chp in rqd["data"]:
            chp_id = chp["id"]

            volume = chp["attributes"]["volume"]
            chapter = chp["attributes"]["chapter"]
            title = chp["attributes"]["title"]

            if volume == None:
                volume = "No_Volume"
            if chapter == None:
                chapter = "Unknown Chapter"
            if title == None:
                title = ""

            pages = chp["attributes"]["pages"]

            pubTime = chp["attributes"]["publishAt"]

            scanlation_group = None
            for relation in chp["relationships"]:
                if relation["type"] == "scanlation_group":
                    scanlation_group = Scanlation_Group(relation["id"])

            self.chapter_list.append(Chapter(chp_id, volume, chapter, title, pages, scanlation_group, pubTime))

    def DownloadAll(self, path, folderformat):

        self.indexAllChapters()
        # os.cpu_count() * 2 for full throttle, but we're going to split that throttle among
        # the chapter downloader and the page downloader
        with ThreadPoolExecutor(max_workers=os.cpu_count()) as threadpool:
            for chpts in self.chapter_list:
                threadpool.submit(chpts.DownloadChapter, path, folderformat) 

    def DownloadLatest(self, path, folderformat):
        self.indexLatestChapter()
        chpt = self.chapter_list[0]
        chpt.DownloadChapter(path, folderformat)

    def DownloadOldest(self, path, folderformat):
        self.indexOldestChapter()
        chpt = self.chapter_list[0]
        chpt.DownloadChapter(path, folderformat)

# Function to resolve a manga ID based upon user given input
def resoveID(mangaName):
    rq = rx.get("https://api.mangadex.org/manga?title={mx}&limit=1&order[relevance]=desc".format(mx=mangaName))
    rqd = js.loads(rq.text)

    id = ""
    if rqd["total"] == 0:
        print("Manga Not found")
    else:
        for entry in rqd["data"]:
            id = entry["id"]
        return id

# Function to Resolve an Author ID based upon user input
def resolveArtist(artistName):
    rq = rx.get("https://api.mangadex.org/author?name={ax}&limit=1".format(ax=artistName))
    rqd = js.loads(rq.text)

    id = ""
    if rqd["response"] == "collection":
        print("Author/Artist Not found")
    else:
        for entry in rqd["data"]:
            id = entry["id"]
        return id
