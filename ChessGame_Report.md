# Human vs AI Chess Game Implementation Report

## Introduction

This report details the implementation of a chess game application that allows a human player to play against an AI opponent powered by the Minimax algorithm with Alpha-Beta pruning. The application follows an object-oriented design pattern with a clean separation between game logic, AI, and GUI components, and includes all standard chess rules and mechanics.

## Design Architecture

The application follows a well-structured object-oriented design with clear separation of concerns between different components:

### Class Structure

1. **ChessGame**: The main controller class that:
   - Manages the game loop and player turns
   - Tracks game state and history
   - Handles game end conditions

2. **Board**: Represents the 8x8 chessboard and:
   - Tracks the state of all pieces
   - Validates moves according to chess rules
   - Detects check, checkmate, and stalemate conditions
   - Implements special move mechanics (castling, en passant, promotion)

3. **Move**: Encapsulates all aspects of a chess move:
   - Source and destination coordinates
   - Moving piece
   - Move type (normal, capture, castling, promotion, en passant)
   - Captured piece (if any)
   - Promotion piece (if applicable)

4. **Piece Hierarchy**:
   - **Piece**: Abstract base class with common functionality
   - **King, Queen, Rook, Bishop, Knight, Pawn**: Individual piece classes that inherit from Piece
   - Each piece implements its own movement rules via the `get_valid_moves()` method

5. **Player Hierarchy**:
   - **Player**: Abstract base class for all player types
   - **HumanPlayer**: Handles human move input via console
   - **GUIHumanPlayer**: Handles human move input via GUI
   - **AIPlayer**: Implements the AI opponent using Minimax with Alpha-Beta pruning

6. **Minimax**: Implements the AI decision-making algorithm:
   - Searches the game tree to a configurable depth
   - Uses Alpha-Beta pruning to optimize search
   - Evaluates board positions based on material, position, mobility, and king safety

7. **GUI**: Provides a graphical interface using Tkinter:
   - Displays the chessboard and pieces
   - Handles user interactions
   - Shows game status and updates

## AI Implementation

### Minimax Algorithm with Alpha-Beta Pruning

The AI opponent uses the Minimax algorithm with Alpha-Beta pruning to make decisions about moves. The Minimax algorithm is a decision-making algorithm used for finding the optimal move in two-player zero-sum games.

#### Core Components:

1. **Minimax Search**: 
   - Recursively explores possible future game states
   - Alternates between maximizing player (White) and minimizing player (Black)
   - Evaluates terminal states using an evaluation function
   - Backtracks values to determine the best move

2. **Alpha-Beta Pruning**:
   - Optimization technique that significantly reduces the number of nodes explored
   - Maintains two values: alpha (best already explored option for maximizer) and beta (best already explored option for minimizer)
   - Prunes branches that cannot affect the final decision

3. **Search Depth**:
   - The AI searches to a configurable depth (default is 3 plies)
   - Higher depths yield stronger play but require more computation time

4. **Transposition Table** (Not implemented, potential enhancement):
   - Could cache previously evaluated positions to avoid redundant calculations
   - Would significantly improve performance, especially at higher depths

### Board Evaluation Function

The evaluation function assesses board positions based on several factors:

1. **Material Evaluation**:
   - Assigns standard piece values: Pawn (100), Knight (300), Bishop (300), Rook (500), Queen (900), King (∞)
   - Calculates the material balance between White and Black pieces

2. **Positional Evaluation**:
   - Uses piece-square tables to evaluate the positioning of each piece
   - Encourages pieces to occupy strategically advantageous squares
   - Different tables for each piece type, with different values for middlegame and endgame

3. **Mobility Evaluation**:
   - Counts the total number of legal moves available to each side
   - More potential moves generally indicates greater piece activity and flexibility

4. **King Safety Evaluation**:
   - Evaluates king position and surrounding pawn structure
   - Penalizes exposed kings and rewards kings with pawn shields
   - Heavily penalizes kings in check

5. **Weighted Combination**:
   ```python
   score = (
       material_score * 1.0 +    # Material is most important
       positional_score * 0.3 +  # Positional advantage
       mobility_score * 0.2 +    # Mobility
       king_safety_score * 0.5   # King safety
   )
   ```

## Chess Game Mechanics

The implementation includes all standard chess rules and mechanics:

### Basic Movement

All pieces move according to standard chess rules:
- **Pawns**: Move forward one square, or two on their first move; capture diagonally
- **Knights**: Move in an L-shape, jumping over other pieces
- **Bishops**: Move diagonally any number of squares
- **Rooks**: Move horizontally or vertically any number of squares
- **Queens**: Combine the powers of the rook and bishop
- **Kings**: Move one square in any direction

### Special Move Mechanics

#### 1. Castling

Castling allows the king to move two squares toward a rook, with the rook moving to the other side of the king. Requirements:
- Neither the king nor the rook has moved previously
- No pieces between the king and the rook
- The king is not in check
- The king does not pass through or end up on a square that is under attack

**Implementation:**
```python
def can_castle_kingside(self, board, row, col):
    """Check if kingside castling is possible."""
    # Already checked if king can castle in general
    if not self.can_castle(board, row, col):
        return False
        
    # Check if rook has moved
    rook_col = 7
    rook = board.grid[row][rook_col]
    if rook is None or not isinstance(rook, Rook) or rook.has_moved:
        return False
        
    # Check if squares between king and rook are empty
    for c in range(col + 1, rook_col):
        if board.grid[row][c] is not None:
            return False
            
    # Check if king would pass through check
    for c in range(col + 1, col + 3):  # King moves 2 spaces
        # Create a temporary board
        temp_board = board.clone()
        # Move the king to this position
        temp_move = Move((row, col), (row, c), self)
        temp_board.make_move(temp_move, check_validity=False)
        
        # If this position is under attack, castling is not allowed
        if self._is_position_under_attack(temp_board, (row, c)):
            return False
                
    return True
```

**Test Case**: White kingside castling
1. Board state: King at e1, Rook at h1, all squares between empty
2. Move input: `O-O` or `0-0`
3. Result: The king moves to g1 and the rook moves to f1

#### 2. Pawn Promotion

When a pawn reaches the opposite end of the board, it must be promoted to a queen, rook, bishop, or knight.

**Implementation:**
```python
# Check for promotion
if (isinstance(piece, Pawn) and 
    ((dst_row == 0 and piece.color == "White") or 
     (dst_row == 7 and piece.color == "Black"))):
    move_type = "promotion"
    promotion_piece = Queen(piece.color)  # Default promotion to Queen
```

**Test Case**: White pawn promotion to queen
1. Board state: White pawn at e7
2. Move input: `e7e8q`
3. Result: The pawn is promoted to a queen at e8

#### 3. En Passant

When a pawn moves two squares forward from its starting position, an opponent's pawn can capture it "in passing" as if it had only moved one square.

**Implementation:**
```python
# En passant capture
# Check if there's an opponent's pawn adjacent that just moved two squares
if board.grid[new_row][new_col] is None:  # The destination square must be empty
    adjacent_piece = board.grid[row][new_col]  # The piece on the same row but in destination column
    
    if (adjacent_piece and 
        isinstance(adjacent_piece, Pawn) and 
        adjacent_piece.color != self.color and 
        adjacent_piece.en_passant_vulnerable and
        board.last_move and
        board.last_move.piece == adjacent_piece and
        abs(board.last_move.source[0] - board.last_move.destination[0]) == 2):
        
        moves.append((new_row, new_col))  # Add en passant capture
```

**Test Case**: White pawn captures black pawn en passant
1. Board state: Black pawn at d7, White pawn at e5
2. Black moves: `d7d5`
3. White moves: `e5d6`
4. Result: The white pawn moves to d6, and the black pawn at d5 is captured

### Check and Checkmate Detection

The implementation includes robust detection of check, checkmate, and stalemate conditions:

#### 1. Check Detection

The `is_in_check` method determines if a king is under attack:

```python
def is_in_check(self, color):
    """Check if the specified color is in check."""
    king_position = self.get_king_position(color)
    if not king_position:
        return False  # No king found
        
    # Get the king object
    king_row, king_col = king_position
    king = self.grid[king_row][king_col]
    
    # Use the King's own method to determine if it's under attack
    if isinstance(king, King):
        return king._is_position_under_attack(self, king_position)
    
    return False
```

**Test Case**: King in check
1. Board state: White king at e1, Black queen at e8
2. Result: The system correctly identifies that the White king is in check

#### 2. Checkmate Detection

The `is_checkmate` method first checks if the king is in check, then verifies if any move can get the king out of check:

```python
def is_checkmate(self, color):
    """Check if the specified color is in checkmate."""
    if not self.is_in_check(color):
        return False
        
    # Check if any move can get the king out of check
    for row in range(8):
        for col in range(8):
            piece = self.grid[row][col]
            if piece and piece.color == color:
                valid_moves = piece.get_valid_moves(self, (row, col))
                
                for move_pos in valid_moves:
                    move = self.create_move((row, col), move_pos)
                    temp_board = self.clone()
                    temp_board.make_move(move, check_validity=False)
                    
                    if not temp_board.is_in_check(color):
                        return False  # Found a move that gets out of check
                        
    return True
```

**Test Case**: Checkmate
1. Board state: White king at h1, Black queens at g1 and g2
2. Result: The system correctly identifies that White is in checkmate

#### 3. Stalemate Detection

Similar to checkmate detection, but checks if there are no legal moves while not being in check:

```python
def is_stalemate(self, color):
    """Check if the specified color is in stalemate."""
    if self.is_in_check(color):
        return False
        
    # Check if any legal move is available
    for row in range(8):
        for col in range(8):
            piece = self.grid[row][col]
            if piece and piece.color == color:
                valid_moves = piece.get_valid_moves(self, (row, col))
                
                for move_pos in valid_moves:
                    move = self.create_move((row, col), move_pos)
                    temp_board = self.clone()
                    temp_board.make_move(move, check_validity=False)
                    
                    if not temp_board.is_in_check(color):
                        return False  # Found a legal move
                        
    return True
```

**Test Case**: Stalemate
1. Board state: White king at h8, Black queen at f7
2. Result: The system correctly identifies that White is in stalemate

## Graphical User Interface

The GUI is implemented using Tkinter and provides a clean, intuitive interface:

### Key Features:

1. **Visual Board Representation**:
   - 8x8 grid with alternating light and dark squares
   - Pieces represented with Unicode chess symbols
   - Row and column labels (a-h, 1-8)

2. **Move Input Methods**:
   - Text input box accepting algebraic notation (e.g., `e2e4`, `O-O`, `e7e8q`)
   - Click-based movement by selecting a piece and then its destination

3. **Game Status Information**:
   - Current player's turn
   - Game status messages (check, checkmate, stalemate)
   - AI thinking indicator

4. **Visual Feedback**:
   - Selected piece highlighting
   - Message boxes for important events (invalid moves, game over)

## Conclusion

The chess implementation successfully meets all the requirements specified in the assignment. It features:

- A complete chess game with all standard rules and mechanics
- A modular, object-oriented design with clear separation of concerns
- An AI opponent using Minimax with Alpha-Beta pruning
- A functional and user-friendly GUI

### Key Achievements:

1. **Comprehensive Chess Rules**: All standard chess rules are implemented, including special moves like castling, en passant, and pawn promotion.

2. **Robust AI**: The AI uses Minimax with Alpha-Beta pruning and a sophisticated evaluation function that considers material balance, piece positioning, mobility, and king safety.

3. **User-Friendly Interface**: The GUI provides multiple ways to input moves and gives clear feedback about the game state.

### Potential Enhancements:

1. **Performance Optimizations**:
   - Implement a transposition table to avoid re-evaluating positions
   - Use bitboards for faster board representation and move generation

2. **Advanced Features**:
   - Draw by insufficient material
   - Draw by threefold repetition
   - 50-move rule

3. **Improved AI**:
   - Opening book integration
   - Endgame tablebase support
   - Iterative deepening search