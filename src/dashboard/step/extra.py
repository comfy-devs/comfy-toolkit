from os import system
from util.general import colorize
from util.api import fetchAnilist, fetchMAL

def downloadPoster(anilistID, posterUrl):
    system(f"wget -O /usr/src/nyananime/processed/{anilistID}/poster_in {posterUrl} > /dev/null")
    system(f"convert /usr/src/nyananime/processed/{anilistID}/poster_in /usr/src/nyananime/processed/{anilistID}/poster.jpg")
    system(f"cwebp -quiet -q 90 /usr/src/nyananime/processed/{anilistID}/poster_in -o /usr/src/nyananime/processed/{anilistID}/poster.webp")
    system(f"rm /usr/src/nyananime/processed/{anilistID}/poster_in")

def stepExtraAnime(anilistID, media, mediaMAL):
    media["title"]["romaji"] = media["title"]["romaji"].replace('\'', '\\\'')
    media["description"] = media["description"].replace('\'', '\\\'')
    print(f'''INSERT INTO animes (id, title, synopsis, episodes, type, status, genres, tags, rating, `group`, season, presets, location, timestamp)
VALUES ('{anilistID}', '{media["title"]["romaji"]}', '{media["description"]}', {media["episodes"]}, {media["format"]}, {media["status"]}, {media["genres"]}, 1
, 0, NULL, NULL, 4, 0, {mediaMAL['timestamp']});\n''')

    selection = input("> Edit? [n]: ")
    selection = "n" if selection == "" else selection
    if selection == "y":
        # TODO: Finish auto-completing for group, season
        mediaTitle = media["title"]["romaji"][:32] if len(media["title"]["romaji"]) > 32 else media["title"]["romaji"]
        animeTitle = input(f"> Anime title? [{colorize('gray', mediaTitle)}]: ")
        animeTitle = media["title"]["romaji"] if animeTitle == "" else animeTitle
        animeEpisodeCount = input(f"> Anime episode count? [{colorize('gray', media['episodes'])}]: ")
        animeEpisodeCount = media["episodes"] if animeEpisodeCount == "" else animeEpisodeCount
        animeType = input(f"> Anime type? [{colorize('gray', media['format'])}]: ")
        animeType = media["format"] if animeType == "" else animeType
        animeStatus = input(f"> Anime status? [{colorize('gray', media['status'])}]: ")
        animeStatus = media["status"] if animeStatus == "" else animeStatus
        animeGenres = input(f"> Anime genres? [{colorize('gray', media['genres'])}]: ")
        animeGenres = media["genres"] if animeGenres == "" else animeGenres
        animeTags = input(f"> Anime tags? [{colorize('gray', '1')}]: ")
        animeTags = '1' if animeTags == "" else animeTags
        animeRating = input(f"> Anime rating? [{colorize('gray', '0')}]: ")
        animeRating = '0' if animeRating == "" else animeRating
        animeGroup = input(f"> Anime group? [{colorize('gray', 'NULL')}]: ")
        animeGroup = 'NULL' if animeGroup == "" else f"'{animeGroup}'"
        animeSeason = input(f"> Anime season? [{colorize('gray', 'NULL')}]: ")
        animeSeason = 'NULL' if animeSeason == "" else f"'{animeSeason}'"
        animePresets = input(f"> Anime presets? [{colorize('gray', '4')}]: ")
        animePresets = '4' if animePresets == "" else animePresets
        animeLocation = input(f"> Anime location? [{colorize('gray', '0')}]: ")
        animeLocation = '0' if animeLocation == "" else animeLocation
        animeTimestamp = input(f"> Anime timestamp? [{colorize('gray', mediaMAL['timestamp'])} (episode {colorize('gray', mediaMAL['_lastEpisode'])})]: ")
        animeTimestamp = mediaMAL['timestamp'] if animeTimestamp == "" else animeTimestamp
        
        print(f'''INSERT INTO animes (id, title, synopsis, episodes, type, status, genres, tags, rating, `group`, season, presets, location, timestamp)
    VALUES ('{anilistID}', '{animeTitle}', '{media["description"]}', {animeEpisodeCount}, {animeType}, {animeStatus}, {animeGenres}, {animeTags}
    , {animeRating}, {animeGroup}, {animeSeason}, {animePresets}, {animeLocation}, {animeTimestamp});\n''')
        input("Press enter...")

def stepExtraEpisodes(anilistID, start, length, mediaMAL=None):
    if mediaMAL != None and len(mediaMAL["episodes"]) == (length - start):
        for i in range(length):
            episodeTitle = mediaMAL['episodes'][i].replace('\'', '\\\'')
            print(f"INSERT INTO episodes (id, pos, anime, title) VALUES ('{anilistID}-{start+i}', {start+i}, {anilistID}, '{episodeTitle}');")
        print("")

        selection = input("> Edit? [n]: ")
        selection = "n" if selection == "" else selection
        if selection == "n":
            return

    result = ""
    for i in range(length):
        episodeTitle = input(f"> Episode {colorize('gray', start+i+1)} title?: ")
        episodeTitle = episodeTitle.replace('\'', '\\\'')
        result += f"INSERT INTO episodes (id, pos, anime, title) VALUES ('{anilistID}-{start+i}', {start+i}, {anilistID}, '{episodeTitle}');\n"

    print(result)
    input("Press enter...")

def stepExtra(anilistID, malID, partial = False):
    media = fetchAnilist(anilistID)
    mediaMAL = fetchMAL(malID, media["episodes"])

    if partial == False:
        selection = input("> Download poster? (y/n) [y]: ")
        selection = "y" if selection == "" else selection
        if selection == "y":
            posterUrl = input(f"> Poster URL? [{colorize('gray', media['coverImage']['extraLarge'])}]: ")
            posterUrl = media["coverImage"]["extraLarge"] if posterUrl == "" else posterUrl
            downloadPoster(anilistID, posterUrl)
        
        selection = input("> Generate SQL query for anime? (y/n) [y]: ")
        selection = "y" if selection == "" else selection
        if selection == "y":
            stepExtraAnime(anilistID, media, mediaMAL)
    
    selection = input("> Generate SQL query for episodes? (y/n) [y]: ")
    selection = "y" if selection == "" else selection
    if selection == "y":
        if partial:
            animeStart = int(input(f"> First episode index? [0]: "))
            animeStart = 0 if animeStart == "" else int(animeStart)
            animeEpisodes = input(f"> Episode count? [1]: ")
            animeEpisodes = 1 if animeEpisodes == "" else int(animeEpisodes)
            stepExtraEpisodes(anilistID, animeStart, animeEpisodes, mediaMAL)
        else:
            animeEpisodes = input(f"> Episode count? [{colorize('gray', media['episodes'])}]: ")
            animeEpisodes = media["episodes"] if animeEpisodes == "" else int(animeEpisodes)
            stepExtraEpisodes(anilistID, 0, animeEpisodes, mediaMAL)