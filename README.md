# 5x5 Boggle-Style Word Grid Generator

A Python pipeline that procedurally generates valid, high-engagement 5x5 word search / Boggle-style puzzles. Each grid embeds a specific target word along an orthogonal continuous path while ensuring the target
is the unique longest word and the surrounding letter distribution produces engaging secondary bonus words.



## Features

- **Embedded Orthogonal Paths**: Generates non-self-intersecting random walks on a 5x5 grid (cardinal moves: Up, Down, Left, Right).
- **Target Uniqueness Guarantee**: Runs a Trie/Prefix-pruned DFS solver across every generated board to verify that no accidental words equal or exceed the target word's length.
- **Natural Secondary Word Density**: Fills empty cells using Scrabble/English-weighted letter distributions, ensuring realistic vocabulary formation.
- **Engaging Difficulty Thresholds**: Filters out dry boards by requiring a minimum number of total valid words ($\ge 10$) and medium-length bonus words ($\ge 2$ words of length 4–6).
- **Automated Dictionary Fetching**: Automatically pulls and caches a standard Scrabble word list on first execution.
- **Structured CSV Export**: Exports flat 25-cell grid definitions alongside difficulty metrics and sample bonus words for game engines or frontend applications.



## How It Works

1. **Dictionary Loading & Prefix Indexing**: 
   Downloads `words.txt` (Scrabble lexicon), strips terms under 3 letters, and builds a prefix set to enable high-speed $O(1)$ pruning during board validation.
2. **Target Path Generation**:
   Selects a random cell on a 5x5 grid and performs a randomized recursive backtracking walk of length $N = \text{len}(\text{target})$.
3. **Board Filling**:
   Places the target letters sequentially along the path, then populates remaining cells using a weighted English letter distribution (`LETTER_BAG`).
4. **Validation & Quality Checks**:
   - Board is searched via Depth-First Search for all valid words $\ge 3$ characters.
   - Rejects the board if any word is longer than the target, or if another distinct word matches the target's length.
   - Rejects boards failing the richness threshold (`MIN_TOTAL_WORDS` and `MIN_MEDIUM_WORDS`).
5. **CSV Generation**:
   Writes qualifying grids to `puzzle_data.csv`.



## Prerequisites

- **Python 3.8+**
- Standard Python library only (`csv`, `random`, `ssl`, `urllib.request`). No external package dependencies required.



## Getting Started

1. Clone or download the repository:
   ```bash
   git clone <repository-url>
   cd <repository-folder>
