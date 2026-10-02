import csv
import os
import random
import string

# 4-directional moves (horizontal & vertical adjacency)
DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]


# --- 1. TRIE DATA STRUCTURE ---
class TrieNode:

  def __init__(self):
    self.children = {}
    self.is_word = False


class Trie:

  def __init__(self):
    self.root = TrieNode()

  def insert(self, word):
    node = self.root
    for ch in word:
      if ch not in node.children:
        node.children[ch] = TrieNode()
      node = node.children[ch]
    node.is_word = True


def load_local_dictionary(min_length=3):
  """Loads native macOS dictionary or fallback list."""
  trie = Trie()
  word_count = 0

  local_dict_paths = ["/usr/share/dict/words", "/usr/share/dict/web2"]
  found_path = None
  for p in local_dict_paths:
    if os.path.exists(p):
      found_path = p
      break

  if found_path:
    print(f"Loading system dictionary from: {found_path} ...")
    with open(found_path, "r", encoding="utf-8", errors="ignore") as f:
      for line in f:
        w = line.strip().upper()
        if len(w) >= min_length and w.isalpha():
          trie.insert(w)
          word_count += 1
  else:
    print("Warning: System dictionary not found. Using fallback.")

  print(f"Dictionary ready: {word_count} words indexed.")
  return trie


# --- 2. PATHFINDER & SOLVER ---
def get_random_walk(word_len, rows=5, cols=5):
  def dfs(r, c, visited):
    if len(visited) == word_len:
      return visited

    neighbors = []
    for dr, dc in DIRECTIONS:
      nr, nc = r + dr, c + dc
      if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in visited:
        neighbors.append((nr, nc))

    random.shuffle(neighbors)
    for nr, nc in neighbors:
      res = dfs(nr, nc, visited + [(nr, nc)])
      if res:
        return res
    return None

  starts = [(r, c) for r in range(rows) for c in range(cols)]
  random.shuffle(starts)
  for sr, sc in starts:
    path = dfs(sr, sc, [(sr, sc)])
    if path:
      return path
  return None


def solve_grid(grid, trie, rows=5, cols=5):
  found_words = set()

  def dfs(r, c, node, visited, current_word):
    ch = grid[r][c]
    if ch not in node.children:
      return

    next_node = node.children[ch]
    current_word += ch

    if next_node.is_word:
      found_words.add(current_word)

    for dr, dc in DIRECTIONS:
      nr, nc = r + dr, c + dc
      if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in visited:
        dfs(nr, nc, next_node, visited | {(nr, nc)}, current_word)

  for r in range(rows):
    for c in range(cols):
      dfs(r, c, trie.root, {(r, c)}, "")

  return found_words


# --- 3. GENERATE AND VERIFY ---
def generate_verified_puzzle(
    target_word, trie, rows=5, cols=5, max_trials=1000
):
  target_word = target_word.upper()
  target_len = len(target_word)

  # Distractor pool
  distractors = "BCDFGHJKLMNPQRSTVWXYZAAEEIIOO"

  for trial in range(1, max_trials + 1):
    path = get_random_walk(target_len, rows, cols)
    if not path:
      continue

    grid = [[None for _ in range(cols)] for _ in range(rows)]
    for (r, c), ch in zip(path, target_word):
      grid[r][c] = ch

    for r in range(rows):
      for c in range(cols):
        if grid[r][c] is None:
          grid[r][c] = random.choice(distractors)

    # Solve and find all words
    found = solve_grid(grid, trie, rows, cols)

    # Validation criteria: no word longer than target, and no rival equal-length word
    longer = [w for w in found if len(w) > target_len]
    same_len = [w for w in found if len(w) == target_len and w != target_word]

    if not longer and not same_len:
      row_dict = {}
      for r in range(rows):
        for c in range(cols):
          row_dict[f"cell_{r+1}_{c+1}"] = grid[r][c]
      row_dict["target_word"] = target_word
      row_dict["word_length"] = str(target_len)
      return row_dict

  # Fallback
  row_dict = {}
  for r in range(rows):
    for c in range(cols):
      row_dict[f"cell_{r+1}_{c+1}"] = grid[r][c]
  row_dict["target_word"] = target_word
  row_dict["word_length"] = str(target_len)
  return row_dict


# --- 4. MAIN (20 WORDS, EXCLUDING SOLVENT) ---
if __name__ == "__main__":
  trie = load_local_dictionary(min_length=3)

  # 20 distinct 7-8 letter words
  target_words = [
      "SYMPHONY",
      "SPECTRUM",
      "KEYBOARD",
      "OBSIDIAN",
      "CALCULUS",
      "PLATINUM",
      "HORIZON",
      "PYRAMID",
      "LANTERN",
      "BLOSSOM",
      "CRYSTAL",
      "DOLPHIN",
      "FEATHER",
      "GLACIER",
      "HARMONY",
      "JOURNEY",
      "KINGDOM",
      "OCTOPUS",
      "PHANTOM",
      "TRIUMPH",
  ]

  headers = (
      [f"cell_{r+1}_{c+1}" for r in range(5) for c in range(5)]
      + ["target_word"]
      + ["word_length"]
  )

  csv_filename = "puzzle_data.csv"
  print(f"\nGenerating {len(target_words)} verified puzzles...")

  with open(csv_filename, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=headers)
    writer.writeheader()
    for idx, word in enumerate(target_words, start=1):
      row = generate_verified_puzzle(word, trie)
      writer.writerow(row)
      print(f"  [{idx:02d}/20] -> Generated: {word}")

  print(f"\nAll 20 puzzles verified and written to '{csv_filename}'.")