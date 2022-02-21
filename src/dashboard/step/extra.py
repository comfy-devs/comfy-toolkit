import subprocess, os
from os import system, path
from util.general import colorize
from util.api import fetchAnilist, fetchMAL

def stepExtra():
    system("clear")
    print(f'{colorize("gray", f"Nyan Anime Toolkit - Extra")}')
    opt_id = input("> Anime ID? (ID from anilist.co): ")
    opt_mal_id = input("> Anime ID? (ID from myanimelist.net): ")

    media = fetchAnilist(opt_id)
    media_mal = None
    if opt_mal_id != "":
        media_mal = fetchMAL(opt_mal_id, media["episodes"])

    opt_poster = input("> Download poster? (y/n) [y]: ")
    opt_poster = "y" if opt_poster == "" else opt_poster
    if opt_poster == "y":
        opt_poster_url = input(f"> Poster URL? [{colorize('gray', media['coverImage']['extraLarge'])}]: ")
        opt_poster_url = media["coverImage"]["extraLarge"] if opt_poster_url == "" else opt_poster_url
        system(f"wget -O /usr/src/nyananime/dest-episodes/{opt_id}/poster_in {opt_poster_url}")
        system(f"cwebp -q 90 /usr/src/nyananime/dest-episodes/{opt_id}/poster_in -o /usr/src/nyananime/dest-episodes/{opt_id}/poster.webp")
        system(f"rm /usr/src/nyananime/dest-episodes/{opt_id}/poster_in")

    # TODO: Finish auto-completing for group, season
    opt_sql_anime = input("> Generate SQL query for anime? (y/n) [y]: ")
    opt_sql_anime = "y" if opt_sql_anime == "" else opt_sql_anime
    if opt_sql_anime == "y":
        mediaTitle = media["title"]["romaji"][:32] if len(media["title"]["romaji"]) > 32 else media["title"]["romaji"]
        opt_sql_anime_title = input(f"> Anime title? [{colorize('gray', mediaTitle)}]: ")
        opt_sql_anime_title = media["title"]["romaji"] if opt_sql_anime_title == "" else opt_sql_anime_title
        opt_sql_anime_title = opt_sql_anime_title.replace('\'', '\\\'')
        # mediaSynopsis = media["description"][:32] if len(media["description"]) > 32 else media["description"]
        # opt_sql_anime_synopsis = input(f"> Anime synopsis? [{colorize('gray', mediaSynopsis + '...')}]: ")
        # opt_sql_anime_synopsis = media["description"] if opt_sql_anime_synopsis == "" else opt_sql_anime_synopsis
        opt_sql_anime_synopsis = input(f"> Anime synopsis?: ")
        opt_sql_anime_episodes = input(f"> Anime episode count? [{colorize('gray', media['episodes'])}]: ")
        opt_sql_anime_episodes = media["episodes"] if opt_sql_anime_episodes == "" else opt_sql_anime_episodes
        opt_sql_anime_type = input(f"> Anime type? [{colorize('gray', media['format'])}]: ")
        opt_sql_anime_type = media["format"] if opt_sql_anime_type == "" else opt_sql_anime_type
        opt_sql_anime_status = input(f"> Anime status? [{colorize('gray', media['status'])}]: ")
        opt_sql_anime_status = media["status"] if opt_sql_anime_status == "" else opt_sql_anime_status
        opt_sql_anime_genres = input(f"> Anime genres? [{colorize('gray', media['genres'])}]: ")
        opt_sql_anime_genres = media["genres"] if opt_sql_anime_genres == "" else opt_sql_anime_genres
        opt_sql_anime_tags = input(f"> Anime tags? [{colorize('gray', '1')}]: ")
        opt_sql_anime_tags = '1' if opt_sql_anime_tags == "" else opt_sql_anime_tags
        opt_sql_anime_rating = input(f"> Anime rating? [{colorize('gray', '0')}]: ")
        opt_sql_anime_rating = '0' if opt_sql_anime_rating == "" else opt_sql_anime_rating
        opt_sql_anime_group = input(f"> Anime group? [{colorize('gray', 'NULL')}]: ")
        opt_sql_anime_group = 'NULL' if opt_sql_anime_group == "" else f"'{opt_sql_anime_group}'"
        opt_sql_anime_season = input(f"> Anime season? [{colorize('gray', 'NULL')}]: ")
        opt_sql_anime_season = 'NULL' if opt_sql_anime_season == "" else f"'{opt_sql_anime_season}'"
        opt_sql_anime_presets = input(f"> Anime presets? [{colorize('gray', '4')}]: ")
        opt_sql_anime_presets = '4' if opt_sql_anime_presets == "" else opt_sql_anime_presets
        opt_sql_anime_location = input(f"> Anime location? [{colorize('gray', '0')}]: ")
        opt_sql_anime_location = '0' if opt_sql_anime_location == "" else opt_sql_anime_location

        opt_sql_anime_timestamp = "0"
        if media_mal != None:
            opt_sql_anime_timestamp = input(f"> Anime timestamp? [{colorize('gray', media_mal['timestamp'])} (episode {colorize('gray', media_mal['lastEpisode'])})]: ")
            opt_sql_anime_timestamp = media_mal['timestamp'] if opt_sql_anime_timestamp == "" else opt_sql_anime_timestamp
        else:
            opt_sql_anime_timestamp = input(f"> Anime timestamp? [{colorize('gray', '0')}]: ")
            opt_sql_anime_timestamp = "0" if opt_sql_anime_timestamp == "" else opt_sql_anime_timestamp

        print(f'''INSERT INTO animes (id, title, synopsis, episodes, type, status, genres, tags, rating, `group`, season, presets, location, timestamp)
VALUES ('{opt_id}', '{opt_sql_anime_title}', '{""}', {opt_sql_anime_episodes}, {opt_sql_anime_type}, {opt_sql_anime_status}, {opt_sql_anime_genres}, {opt_sql_anime_tags}
, {opt_sql_anime_rating}, {opt_sql_anime_group}, {opt_sql_anime_season}, {opt_sql_anime_presets}, {opt_sql_anime_location}, {opt_sql_anime_timestamp});''')
        input("Press enter...")

    opt_sql_episodes = input("> Generate SQL query for episodes? (y/n) [y]: ")
    opt_sql_episodes = "y" if opt_sql_episodes == "" else opt_sql_episodes
    if opt_sql_episodes == "y":
        opt_sql_episodes_result = ""
        opt_sql_anime_episodes = input(f"> Anime episode count? [{colorize('gray', media['episodes'])}]: ")
        opt_sql_anime_episodes = media["episodes"] if opt_sql_anime_episodes == "" else opt_sql_anime_episodes

        for i in range(int(opt_sql_anime_episodes)):
            opt_sql_episode_title = input(f"> Episode '{colorize('gray', i)}' title?: ")
            opt_sql_episode_title = opt_sql_episode_title.replace('\'', '\\\'')
            opt_sql_episodes_result += f"INSERT INTO episodes (id, pos, anime, title) VALUES ('{opt_id}-{i}', {i}, {opt_id}, '{opt_sql_episode_title}');\n"

        print(opt_sql_episodes_result)
        input("Press enter...")