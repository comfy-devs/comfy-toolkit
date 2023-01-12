import json, requests, functools
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta

formatMap = {
    "TV": 0,
    "TV_SHORT": 0, 
    "SPECIAL": 1,
    "OVA": 2,
    "MOVIE": 3,
    "ONA": 4,
}
statusMap = {
    "FINISHED": 1,
    "RELEASING": 0,
    "NOT_YET_RELEASED": 0,
    "CANCELLED": 0,
    "HIATUS": 0
}
genreMap = {
    "ACTION": 1,
    "ADVENTURE": 2,
    "COMEDY": 4,
    "DRAMA": 8,
    "ECCHI": 16,
    "FANTASY": 32,
    "HORROR": 64,
    "MAHOU SHOUJO": 128,
    "MECHA": 256,
    "MUSIC": 512,
    "MYSTERY": 1024,
    "PSYCHOLOGICAL": 2048,
    "ROMANCE": 4096,
    "SCI-FI": 8192,
    "SLICE OF LIFE": 16384,
    "SPORTS": 32768,
    "SUPERNATURAL": 65536,
    "THRILLER": 131072
}
months = {
    "Jan": 1,
    "Feb": 2,
    "Mar": 3,
    "Apr": 4,
    "May": 5,
    "Jun": 6,
    "Jul": 7,
    "Aug": 8,
    "Sep": 9,
    "Oct": 10,
    "Nov": 11,
    "Dec": 12
}

def fetchAnilist(showID):
    query= '''
    query ($id: Int) {
        Media (id: $id, type: ANIME) {
            id
            title { romaji }
            format
            status
            description (asHtml: false)
            episodes
            genres
            coverImage { extraLarge }
            relations {
                edges {
                    node { id }
                    relationType (version: 2)
                }
            }
        }
    }
    '''
    response = requests.post("https://graphql.anilist.co", json={ "query": query, "variables": { "id": showID } })
    media = json.loads(response.text)["data"]["Media"]

    media["episodes"] = 0 if media["episodes"] == None else media["episodes"]
    media["format"] = formatMap[media["format"]]
    media["status"] = statusMap[media["status"]]
    media["genres"] = functools.reduce(lambda acc, curr: acc + genreMap[curr.upper()], media["genres"], 0)

    return media

def fetchMAL(showID, episodes):
    r = requests.get(f"https://myanimelist.net/anime/{showID}")
    content = BeautifulSoup(r.content, 'html.parser')
    elements = content.find_all('div', class_='spaceit_pad')

    aired = list(filter(lambda e: "Aired" in e.text, elements))
    aired = aired[0].text
    aired = aired.replace("Aired:", "").strip()
    airedMonth = months[aired[:3]]
    airedDay = int(aired[4:aired.index(",")])
    airedYear = int(aired[(aired.index(", ") + 2):(aired.index(", ") + 6)])

    broadcast = list(filter(lambda e: "Broadcast" in e.text, elements))
    broadcastHour = 0
    broadcastMinute = 0
    if(len(broadcast) > 0):
        broadcast = broadcast[0].text
        if "at " in broadcast:
            broadcast = broadcast[(broadcast.index("at ") + 3):broadcast.index(" (")]
            broadcastHour = int(broadcast[:broadcast.index(":")])
            broadcastMinute = int(broadcast[(broadcast.index(":") + 1):])

    tz = timezone(timedelta(hours=9))
    timestamp = datetime(airedYear, airedMonth, airedDay, broadcastHour, broadcastMinute, 0, 0, tz)

    episodeIndex = 1
    episodes = 9999 if episodes == 0 else episodes
    for i in range(episodes - 1):
        if timestamp + timedelta(days=7) < datetime.now(tz):
            timestamp += timedelta(days=7)
            episodeIndex += 1
        else:
            break

    episodesUrl = content.find_all('a', text='Episodes')[0]["href"]
    r = requests.get(episodesUrl)
    content = BeautifulSoup(r.content, 'html.parser')
    elements = content.find_all('a', class_='fl-l')
    episodes = list(map(lambda e: e.text, elements))
    
    return {
        "_lastEpisode": episodeIndex,
        "episodes": episodes,
        "timestamp": int(timestamp.timestamp()),
    }