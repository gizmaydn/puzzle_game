import csv
import random
import ssl
import urllib.request

# 1. Download and load word list
url = "https://raw.githubusercontent.com/raun/Scrabble/master/words.txt"
filename = "words.txt"

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

try:
    with open(filename, "r", encoding="utf-8") as f:
        words = {line.strip().upper() for line in f if len(line.strip().upper()) >= 3}
except FileNotFoundError:
    print("Downloading words.txt...")
    with urllib.request.urlopen(url, context=ctx) as response, open(filename, "wb") as out_file:
        out_file.write(response.read())
    with open(filename, "r", encoding="utf-8") as f:
        words = {line.strip().upper() for line in f if len(line.strip().upper()) >= 3}

prefixes = {w[:i] for w in words for i in range(1, len(w) + 1)}

TARGETS = [
    "CHALLENGE", "STRATEGY", "NETWORK", "OCEAN", "FOLLOW",
    "MOUNTAIN", "RIVER", "PENGUIN", "LUNAR", "BEACON",
    "CAPTAIN", "DOABLE", "FANTASY", "GLAMOUR", "HARVEST",
    "JEALOUS", "KNOCKOUT", "OCTOPUS", "PLATFORM", "TREASURE",
    "UNIVERSE", "VICTORY", "WILDERNESS",
]

MOVES = [(-1, 0), (1, 0), (0, -1), (0, 1)]

# Weighted letter distribution (English letter frequencies)
# Biasing toward real English frequencies produces naturally occurring secondary words.
LETTER_BAG = (
    "E" * 12 + "A" * 9 + "I" * 9 + "O" * 8 + "N" * 6 + "R" * 6 + "T" * 6 +
    "L" * 4 + "S" * 4 + "U" * 4 + "D" * 4 + "G" * 3 + "B" * 2 + "C" * 2 +
    "M" * 2 + "P" * 2 + "F" * 2 + "H" * 2 + "V" * 2 + "W" * 2 + "Y" * 2 + "K" * 1
)

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
    + ["target_word", "word_length", "bonus_words_count", "bonus_words_sample"]
)

# Minimum quality thresholds for engaging grids
MIN_TOTAL_WORDS = 10       # At least 10 valid words in the grid
MIN_MEDIUM_WORDS = 2      # At least 2 words of length 4 to 6 (satisfying sub-finds)

with open("puzzle_data.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=headers)
    writer.writeheader()

    for target in TARGETS:
        t_len = len(target)
        attempts = 0

        while True:
            attempts += 1
            path = random_walk(t_len)
            grid = [[None] * 5 for _ in range(5)]

            # Place target word
            for (r, c), ch in zip(path, target):
                grid[r][c] = ch

            # Fill remaining cells with natural frequency distribution
            for r in range(5):
                for c in range(5):
                    if not grid[r][c]:
                        grid[r][c] = random.choice(LETTER_BAG)

            found = solve(grid)

            # Verification conditions:
            # 1. Target must remain the sole unique maximum-length word
            valid_max = not any(len(w) > t_len or (len(w) == t_len and w != target) for w in found)
            if not valid_max:
                continue

            # 2. Extract secondary/decoy words (excluding the target)
            secondary_words = [w for w in found if w != target]
            medium_words = [w for w in secondary_words if 4 <= len(w) <= 6]

            # 3. Check richness criteria (relaxed if too many attempts pass)
            if len(secondary_words) >= MIN_TOTAL_WORDS and len(medium_words) >= MIN_MEDIUM_WORDS:
                sample_bonus = ", ".join(sorted(medium_words, key=len, reverse=True)[:5])

                row = {f"cell_{r+1}_{c+1}": grid[r][c] for r in range(5) for c in range(5)}
                row.update({
                    "target_word": target,
                    "word_length": t_len,
                    "bonus_words_count": len(secondary_words),
                    "bonus_words_sample": sample_bonus,
                })
                writer.writerow(row)
                print(f"Generated {target:<12} (Attempts: {attempts}, Bonus words: {len(secondary_words)})")
                break

print("Generated puzzle_data.csv successfully.")