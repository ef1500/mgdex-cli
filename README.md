# mgdex-cli
## Mangadex CLI Downloader

### Installation
To get started, simply run
```
pip install -r requirements.txt
```

### Usage
#### General Arguments

|                                                  Arg                                                   |                                             Explanation                                              |
|--------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------|
| --id                                                                                                   | The Manga ID. Useful if there are other mangas with the same name. (Like Citrus, for example)        |
| --title                                                                                                | The Title of the Manga. Not Needed if you are downloading via ID. use quotes if the title has spaces |
| --path                                                                                                 | The path to download the manga in. Defaults to the current working directory.                                                                    |
| --folderformat                                                                                         | The Format of the Folders that the chapters will be held in (See the next table for more info)       |
| --download_covers                                                                                      | Only Download the Manga Cover Art                                                                    |
| --download_all                                                                                         | Download all chapters                                                                                |
| --download_latest   | Download Latest Chapter (May take a few minutes depending on the number of chapters) |                                                                                                      |
| --download_first                                                                                       | Download the First Chapter (May take a few minutes depending on the number of chapters)              |

Folder Formatting Defaults to `Vol-%Vl_Ch-%Ch`, but you can change how the folders are structured using the following table
| Var |   Explanation    |
|-----|------------------|
| %Vl | Volume           |
| %Ch | Chapter Number   |
| %Ci | Chapter ID       |
| %Ct | Chapter Title    |
| %Sg | Scanlation Group |

##### Example Usage
Download All Chapters of [Citrus +](https://mangadex.org/title/4a30061a-bc66-4efd-9c4b-87daf8313381) to the current working directory
```
python3 mgdex-cli.py --title "Citrus +" -a
````

Download all Chapters and Covers of [Whisper Me a Love Song](https://mangadex.org/title/0e8fac17-979e-4e37-8f45-2c334b25d6dd) to the current working directory
```
python3 mgdex-cli.py --title "Whisper Me a Love Song" -a -c
```
