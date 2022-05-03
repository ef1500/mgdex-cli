# Main.py
# ef1500
# CLI interface

import os
import argparse as ap
import MangadexAPI as ma

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

    args = parser.parse_args()

    if args.title != None:
        args.id = ma.resoveID(args.title)

    manga = ma.Manga(args.id)

    argpath = os.path.join(args.path, manga.title)

    if args.download_covers == True:
        if os.path.isdir(argpath) != True:
            os.mkdir(argpath)
        covers = ma.Cover_Art(args.id)
        covers.DownloadCovers(argpath)

    if args.download_latest == True:
        if os.path.isdir(argpath) != True:
            os.mkdir(argpath)
        chpt = ma.Chapters(args.id)
        chpt.DownloadLatest(argpath, args.folderformat)

    if args.download_all == True:
        if os.path.isdir(argpath) != True:
            os.mkdir(argpath)
        chpts = ma.Chapters(args.id) 
        chpts.DownloadAll(argpath, args.folderformat) 

    if args.download_first == True:
        if os.path.isdir(argpath) != True:
            os.mkdir(argpath)
        chpt = ma.Chapters(args.id) 
        chpt.DownloadLatest(argpath, args.folderformat)

    if args.info == True:
        manga.writeData(argpath)
