# Main.py
# ef1500
# CLI interface

import os
import argparse as ap
import MangadexAPI as ma

from slugify import slugify

if __name__ == "__main__":
    parser = ap.ArgumentParser(description="A CLI tool to download mangas from Mangadex")

    parser.add_argument("--id", help="the ID of the manga")
    parser.add_argument("--title", help="Title of the manga")
    parser.add_argument("--folderformat", help="The Format of the Folder where the images are stored", default="Vol-%Vl_Ch-%Ch")
    parser.add_argument("-p", "--path", help="Download Destination Path", default=os.getcwd())
    parser.add_argument("-c", "--download_covers", help="Only Download the Cover Art", action="store_true")
    parser.add_argument("-l", "--download_latest", help="Only Download the latest chapter, May take a couple minutes", action="store_true")
    parser.add_argument("-a", "--download_all", help="Download all chapters", action="store_true")
    parser.add_argument("-f", "--download_first", help="Download the first chapter, May take a couple minutes", action="store_true")
    parser.add_argument("-i", "--info", help="Write a text file containing information about the manga", action="store_true")

    parser.add_argument("-r", "--download_artist", help="Download All Works By an Author", action="store_true")
    parser.add_argument("--artist_name", help="Artist or Illustrator Name")
    parser.add_argument("--artist_id", help="Artist or Illustrator ID")


    args = parser.parse_args()

    # Resolve IDs, if any 
    if args.title != None:
        args.id = ma.resoveID(args.title)
        
    loaded_mangas = []
    if args.artist_name != None:
        loaded_artist = ma.Author(ma.resolveArtist(args.artist_name)).works
    if args.artist_id != None:
        loaded_artist = ma.Author(args.artist_id).works

    manga = ""
    argpath = ""
    if args.download_artist == False:
        manga = ma.Manga(args.id)
        argpath = os.path.join(args.path, slugify(manga.title, allow_unicode=True))

    # Resolve + Download Chapters
    if args.download_covers == True and args.download_artist == False:
        if os.path.isdir(argpath) != True:
            os.mkdir(argpath)
        covers = ma.Cover_Art(args.id)
        covers.DownloadCovers(argpath)

    if args.download_latest == True and args.download_artist == False:
        if os.path.isdir(argpath) != True:
            os.mkdir(argpath)
        chpt = ma.Chapters(args.id)
        chpt.DownloadLatest(argpath, args.folderformat)

    if args.download_all == True and args.download_artist == False:
        if os.path.isdir(argpath) != True:
            os.mkdir(argpath)
        chpts = ma.Chapters(args.id) 
        chpts.DownloadAll(argpath, args.folderformat) 

    if args.download_first == True:
        if os.path.isdir(argpath) != True:
            os.mkdir(argpath)
        chpt = ma.Chapters(args.id) 
        chpt.DownloadOldest(argpath, args.folderformat)

    if args.info == True and args.download_artist == False:
        manga.writeData(argpath)

    # Download all mangas from a specified artist/author
    if args.download_artist == True:
        for mangas in loaded_artist: 
            l_manga = ma.Manga(mangas)
            mangapath = os.path.join(args.path, slugify(l_manga.title, allow_unicode=True))
            if args.download_covers == True:
                print("Downloading Covers for {mc}".format(mc = l_manga.title))
                if os.path.isdir(mangapath) != True:
                    os.mkdir(mangapath)
                covers = ma.Cover_Art(mangas)
                covers.DownloadCovers(mangapath)
            if args.download_all == True:
                print("Downloading {mn}".format(mn=l_manga.title))
                if os.path.isdir(mangapath) != True:
                    os.mkdir(mangapath)
                chpts = ma.Chapters(mangas)
                chpts.DownloadAll(mangapath, args.folderformat) 
            if args.info == True:
                l_manga.writeData(mangapath)
