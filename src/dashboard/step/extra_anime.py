from os import system
from util.general import colorize
from util.extra import downloadPoster
from util.api import fetchAnilist, fetchMAL

def stepExtraAnime(showID, media, mediaMAL):
    media["title"]["romaji"] = media["title"]["romaji"].replace('\'', '\\\'')
    media["description"] = media["description"].replace('\'', '\\\'')
    print(f'''INSERT INTO shows (id, title, altTitles, synopsis, episodes, type, status, genres, tags, rating, `group`, season, presets, location, timestamp)
VALUES ('{showID}', '', '{media["title"]["romaji"]}', '{media["description"]}', {media["episodes"]}, {media["format"]}, {media["status"]}, {media["genres"]}, 1
, 0, NULL, NULL, 4, 0, {mediaMAL['timestamp']});\n''')

    selection = input("> Edit? [n]: ")
    selection = "n" if selection == "" else selection
    if selection == "y":
        # TODO: Finish auto-completing for group, season
        mediaTitle = media["title"]["romaji"][:32] if len(media["title"]["romaji"]) > 32 else media["title"]["romaji"]
        showTitle = input(f"> Show title? [{colorize('gray', mediaTitle)}]: ")
        showTitle = media["title"]["romaji"] if showTitle == "" else showTitle
        showEpisodeCount = input(f"> Show episode count? [{colorize('gray', media['episodes'])}]: ")
        showEpisodeCount = media["episodes"] if showEpisodeCount == "" else showEpisodeCount
        animeType = input(f"> Anime type? [{colorize('gray', media['format'])}]: ")
        animeType = media["format"] if animeType == "" else animeType
        showStatus = input(f"> Show status? [{colorize('gray', media['status'])}]: ")
        showStatus = media["status"] if showStatus == "" else showStatus
        showGenres = input(f"> Show genres? [{colorize('gray', media['genres'])}]: ")
        showGenres = media["genres"] if showGenres == "" else showGenres
        showTags = input(f"> Show tags? [{colorize('gray', '1')}]: ")
        showTags = '1' if showTags == "" else showTags
        showRating = input(f"> Show rating? [{colorize('gray', '0')}]: ")
        showRating = '0' if showRating == "" else showRating
        showGroup = input(f"> Show group? [{colorize('gray', 'NULL')}]: ")
        showGroup = 'NULL' if showGroup == "" else f"'{showGroup}'"
        showSeason = input(f"> Show season? [{colorize('gray', 'NULL')}]: ")
        showSeason = 'NULL' if showSeason == "" else f"'{showSeason}'"
        showPresets = input(f"> Show presets? [{colorize('gray', '4')}]: ")
        showPresets = '4' if showPresets == "" else showPresets
        showLocation = input(f"> Show location? [{colorize('gray', '0')}]: ")
        showLocation = '0' if showLocation == "" else showLocation
        showTimestamp = input(f"> Show timestamp? [{colorize('gray', mediaMAL['timestamp'])} (episode {colorize('gray', mediaMAL['_lastEpisode'])})]: ")
        showTimestamp = mediaMAL['timestamp'] if showTimestamp == "" else showTimestamp
        
        print(f'''INSERT INTO shows (id, title, altTitles, synopsis, episodes, type, status, genres, tags, rating, `group`, season, presets, location, timestamp)
    VALUES ('{showID}', '{showTitle}', '', '{media["description"]}', {showEpisodeCount}, {animeType}, {showStatus}, {showGenres}, {showTags}
    , {showRating}, {showGroup}, {showSeason}, {showPresets}, {showLocation}, {showTimestamp});\n''')
        input("Press enter...")

def stepExtraEpisodesAnime(showID, start, length, mediaMAL=None):
    if mediaMAL != None and len(mediaMAL["episodes"]) == (length - start):
        for i in range(length):
            episodeTitle = mediaMAL['episodes'][i].replace('\'', '\\\'')
            print(f"INSERT INTO episodes (id, pos, `show`, title) VALUES ('{showID}-{start+i}', {start+i}, '{showID}', '{episodeTitle}');")
        print("")

        selection = input("> Edit? [n]: ")
        selection = "n" if selection == "" else selection
        if selection == "n":
            return

    result = ""
    for i in range(length):
        episodeTitle = input(f"> Episode {colorize('gray', start+i+1)} title?: ")
        episodeTitle = episodeTitle.replace('\'', '\\\'')
        result += f"INSERT INTO episodes (id, pos, `show`, title) VALUES ('{showID}-{start+i}', {start+i}, {showID}, '{episodeTitle}');\n"

    print(result)
    input("Press enter...")

def stepExtraShowAnime(anilistID, malID, partial = False):
    media = fetchAnilist(anilistID)
    mediaMAL = fetchMAL(malID, media["episodes"])

    if partial == False:
        selection = input("> Download poster? (y/n) [y]: ")
        selection = "y" if selection == "" else selection
        if selection == "y":
            posterUrl = input(f"> Poster URL? [{colorize('gray', media['coverImage']['extraLarge'])}]: ")
            posterUrl = media["coverImage"]["extraLarge"] if posterUrl == "" else posterUrl
            downloadPoster(showID, posterUrl)
        
        selection = input("> Generate SQL query for show? (y/n) [y]: ")
        selection = "y" if selection == "" else selection
        if selection == "y":
            stepExtraAnime(showID, media, mediaMAL)
    
    selection = input("> Generate SQL query for episodes? (y/n) [y]: ")
    selection = "y" if selection == "" else selection
    if selection == "y":
        if partial:
            showStart = int(input(f"> First episode index? [0]: "))
            showStart = 0 if showStart == "" else int(showStart)
            showEpisodes = input(f"> Episode count? [1]: ")
            showEpisodes = 1 if showEpisodes == "" else int(showEpisodes)
            stepExtraEpisodesAnime(showID, showStart, showEpisodes, mediaMAL)
        else:
            showEpisodes = input(f"> Episode count? [{colorize('gray', media['episodes'])}]: ")
            showEpisodes = media["episodes"] if showEpisodes == "" else int(showEpisodes)
            stepExtraEpisodesAnime(showID, 0, showEpisodes, mediaMAL)