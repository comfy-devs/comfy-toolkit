import sys

i = "\n".join(sys.argv[1:])
genres = ["Action", "Adventure", "Comedy", "Drama", "Ecchi", "Fantasy", "Horror", "Mahou Shoujou",
          "Mecha", "Music", "Mystery", "Psychological", "Romance", "Sci-Fi", "Slice of Life", "Sports", "Supernatural", "Thriller"]

def getVal(genre):
    return 2 ** (genres.index(genre))

s = 0
for genre in i.split("\n"):
    s += getVal(genre)
print(s)
