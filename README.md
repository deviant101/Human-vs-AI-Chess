# Chess Game with Minimax AI

A fully-featured chess game implementation with an AI opponent powered by the Minimax algorithm with Alpha-Beta pruning. This project was developed as part of an AI course assignment.

## Features

- Complete chess rules implementation with:
  - All standard piece movements
  - Special moves: Castling (kingside/queenside), En passant captures, Pawn promotion
  - Check, checkmate, and stalemate detection

- Human vs AI gameplay:
  - AI powered by Minimax algorithm with Alpha-Beta pruning
  - Configurable search depth
  - Sophisticated evaluation function including material value, piece positioning, mobility, and king safety

- User-friendly GUI (using Tkinter):
  - Visual chess board with Unicode pieces
  - Move input via text box (algebraic notation or coordinate format)
  - Clickable pieces and squares
  - Game status display

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/deviant101/Human-vs-AI-Chess.git
   cd Human-vs-AI-Chess
   ```

2. No external dependencies required beyond the Python standard library!

## How to Play

Run the main script to start the game:

```
python main.py
```

### Playing with the GUI

- **Mouse Control**: Click on a piece to select it, then click on a destination square to move.
- **Text Input**: Enter moves in the following formats:
  - Standard coordinate format: `e2e4` (source square to destination square)
  - Castling: `O-O` or `0-0` (kingside), `O-O-O` or `0-0-0` (queenside)
  - Pawn promotion: `e7e8q` (promote to queen), `e7e8r` (rook), `e7e8b` (bishop), `e7e8n` (knight)

## Project Structure

- `main.py` - Entry point to start the game
- `chess_game.py` - Main game controller
- `board.py` - Chess board representation and move validation
- `pieces.py` - Individual chess piece classes
- `move.py` - Move representation
- `player.py` - Player classes (human and AI)
- `minimax.py` - AI implementation with Minimax and Alpha-Beta pruning
- `gui.py` - Graphical user interface

## AI Implementation

The AI uses the Minimax algorithm with Alpha-Beta pruning to make decisions, evaluating board positions based on:

1. **Material Balance**: Assigns standard values to pieces (Pawn=1, Knight/Bishop=3, Rook=5, Queen=9)
2. **Positional Advantage**: Uses piece-square tables to evaluate piece positioning
3. **Mobility**: Counts number of legal moves available
4. **King Safety**: Evaluates pawn structure around the king and penalizes exposed kings

## Detailed Documentation

For more detailed information about the implementation, see the [Chess Game Report](ChessGame_Report.md).

## Acknowledgments

- Developed as part of an AI course assignment
- Chess piece values and evaluation concepts from standard chess theory
- Piece-square tables adapted from established chess engines