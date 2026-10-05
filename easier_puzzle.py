import csv
import random
import urllib.request


import ssl
import urllib.request
import certifi

URL = "https://raw.githubusercontent.com/raun/Scrabble/master/words.txt"
context = ssl.create_default_context(cafile=certifi.where())
with urllib.request.urlopen(URL, context=context) as resp:
  words = {
      line.decode("utf-8").strip().upper()
      for line in resp
      if len(line.strip()) >= 3
  }
  

url = "https://raw.githubusercontent.com/raun/Scrabble/master/words.txt"
filename = "words.txt"

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

print("Downloading words.txt...")
with (
    urllib.request.urlopen(url, context=ctx) as response,
    open(filename, "wb") as out_file,
):
  out_file.write(response.read())

print("Saved words.txt successfully.")

with open("words.txt", "r", encoding="utf-8") as f:
  words = {
      line.strip().upper() for line in f if len(line.strip().upper()) >= 3
  }

prefixes = {w[:i] for w in words for i in range(1, len(w) + 1)}

TARGETS = [
    "CHALLENGE",
    "STRATEGY",
    "NETWORK",
    "OCEAN",
    "FOlLOW",
    "MOUNTAIN",
    "RIVER",
    "PENGUIN",
    "LUNAR",
    "BEACON",
    "CAPTAIN",
    "DOABLE",
    "FANTASY",
    "GLAMOUR",
    "HARVEST",
    "JELAOUS",
    "KNOCKOUT",
    "OCTOPUS",
    "PLATFORM",
    "TREASURE",
    "UNIVERSE",
    "VICTORY",
    "WILDERNESS",
    
]
MOVES = [(-1, 0), (1, 0), (0, -1), (0, 1)]


def solve(grid):
  found = set()

  def dfs(r, c, path, cur):
    if cur not in prefixes:
      return
    if cur in words:
      found.add(cur)
    for dr, dc in MOVES:
      nr, nc = r + dr, c + dc
      if 0 <= nr < 5 and 0 <= nc < 5 and (nr, nc) not in path:
        dfs(nr, nc, path | {(nr, nc)}, cur + grid[nr][nc])

  for r in range(5):
    for c in range(5):
      dfs(r, c, {(r, c)}, grid[r][c])
  return found


def random_walk(length):
  def dfs(r, c, path):
    if len(path) == length:
      return path
    nbrs = [
        (r + dr, c + dc)
        for dr, dc in MOVES
        if 0 <= r + dr < 5 and 0 <= c + dc < 5 and (r + dr, c + dc) not in path
    ]
    random.shuffle(nbrs)
    for nr, nc in nbrs:
      res = dfs(nr, nc, path + [(nr, nc)])
      if res:
        return res

  starts = [(r, c) for r in range(5) for c in range(5)]
  random.shuffle(starts)
  return next((dfs(sr, sc, [(sr, sc)]) for sr, sc in starts if dfs(sr, sc, [(sr, sc)])), None)


# 2. Generate and write CSV
headers = (
    [f"cell_{r+1}_{c+1}" for r in range(5) for c in range(5)]
    + ["target_word"]
    + ["word_length"]
)

with open("puzzle_data.csv", "w", newline="") as f:
  writer = csv.DictWriter(f, fieldnames=headers)
  writer.writeheader()

  for target in TARGETS:
    t_len = len(target)
    while True:
      path = random_walk(t_len)
      grid = [[None] * 5 for _ in range(5)]
      for (r, c), ch in zip(path, target):
        grid[r][c] = ch
      for r in range(5):
        for c in range(5):
          if not grid[r][c]:
            grid[r][c] = random.choice("BCDFGHJKLMNPQRSTVWXYZAAEEIIOO")

      found = solve(grid)
      # Must have no longer words and no other equal-length words
      if not any(
          len(w) > t_len or (len(w) == t_len and w != target) for w in found
      ):
        row = {f"cell_{r+1}_{c+1}": grid[r][c] for r in range(5) for c in range(5)}
        row.update({"target_word": target, "word_length": t_len})
        writer.writerow(row)
        break

print("Generated puzzle_data.csv successfully.")