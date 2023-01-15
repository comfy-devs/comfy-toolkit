from os import system
from util.general import colorize
from util.extra import downloadPoster

def stepExtraOther(showID):
    showTitle = input(f"> Show title? [{colorize('gray', 'title')}]: ")
    showTitle = "title" if showTitle == "" else showTitle
    showEpisodeCount = input(f"> Show episode count? [{colorize('gray', '1')}]: ")
    showEpisodeCount = 1 if showEpisodeCount == "" else showEpisodeCount
    showStatus = input(f"> Show status? [{colorize('gray', '1')}]: ")
    showStatus = "1" if showStatus == "" else showStatus
    showGenres = input(f"> Show genres? [{colorize('gray', '0')}]: ")
    showGenres = "0" if showGenres == "" else showGenres
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
    showTimestamp = input(f"> Show timestamp? [{colorize('gray', 'NULL')}]: ")
    showTimestamp = 'NULL' if showTimestamp == "" else showTimestamp
    
    print(f'''INSERT INTO shows (id, title, altTitles, synopsis, episodes, type, status, genres, tags, rating, `group`, season, presets, location, timestamp)
VALUES ('{showID}', '{showTitle}', '', 'somebody forgor to fill this out.', {showEpisodeCount}, 0, {showStatus}, {showGenres}, {showTags}
, {showRating}, {showGroup}, {showSeason}, {showPresets}, {showLocation}, {showTimestamp});\n''')
    input("Press enter...")

def stepExtraEpisodesOther(showID, start, length):
    result = ""
    for i in range(length):
        episodeTitle = input(f"> Episode {colorize('gray', start+i+1)} title?: ")
        episodeTitle = episodeTitle.replace('\'', '\\\'')
        result += f"INSERT INTO episodes (id, pos, `show`, title) VALUES ('{showID}-{start+i}', {start+i}, '{showID}', '{episodeTitle}');\n"

    print(result)
    input("Press enter...")

def stepExtraShowOther(showID, partial = False):
    if partial == False:
        selection = input(f"> Download poster? (y/n) [{colorize('gray', 'y')}]: ")
        selection = "y" if selection == "" else selection
        if selection == "y":
            posterUrl = input(f"> Poster URL?: ")
            downloadPoster(showID, posterUrl)
        
        selection = input(f"> Generate SQL query for show? (y/n) [{colorize('gray', 'y')}]: ")
        selection = "y" if selection == "" else selection
        if selection == "y":
            stepExtraOther(showID)
    
    selection = input(f"> Generate SQL query for episodes? (y/n) [{colorize('gray', 'y')}]: ")
    selection = "y" if selection == "" else selection
    if selection == "y":
        if partial:
            showStart = int(input(f"> First episode index? [0]: "))
            showStart = 0 if showStart == "" else int(showStart)
            showEpisodes = input(f"> Episode count? [{colorize('gray', '1')}]: ")
            showEpisodes = 1 if showEpisodes == "" else int(showEpisodes)
            stepExtraEpisodesOther(showID, showStart, showEpisodes)
        else:
            showEpisodes = input(f"> Episode count? [{colorize('gray', '1')}]: ")
            showEpisodes = 1 if showEpisodes == "" else int(showEpisodes)
            stepExtraEpisodesOther(showID, 0, showEpisodes)