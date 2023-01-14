from os import system

def downloadPoster(showID, posterUrl):
    system(f"wget -O /usr/src/comfy/processed/{showID}/poster_in {posterUrl} > /dev/null")
    system(f"convert /usr/src/comfy/processed/{showID}/poster_in /usr/src/comfy/processed/{showID}/poster.jpg")
    system(f"cwebp -quiet -q 90 /usr/src/comfy/processed/{showID}/poster_in -o /usr/src/comfy/processed/{showID}/poster.webp")
    system(f"rm /usr/src/comfy/processed/{showID}/poster_in")