from move import Move

class Piece:
    def __init__(self, color):
        """
        Initialize a piece with a color.
        
        Args:
            color (str): The color of the piece ('White' or 'Black')
        """
        self.color = color
        self.has_moved = False

    def get_valid_moves(self, board, position):
        """
        Abstract method to get valid moves for a piece.
        
        Args:
            board: The current board state
            position (tuple): The current position of the piece (row, col)
            
        Returns:
            list: List of valid move positions (row, col)
        """
        pass
    
    def is_valid_position(self, position):
        """Check if a position is within the board."""
        row, col = position
        return 0 <= row < 8 and 0 <= col < 8
    
    def __str__(self):
        """String representation of the piece."""
        return f"{self.color} {self.__class__.__name__}"


class King(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.value = float('inf')
    
    def get_valid_moves(self, board, position, check_for_check=True):
        """
        Get all valid moves for the King.
        
        Args:
            board: The current board state
            position (tuple): The current position of the king (row, col)
            check_for_check (bool): Whether to check if moves would leave king in check
            
        Returns:
            list: List of valid move positions (row, col)
        """
        row, col = position
        moves = []
        
        # All possible king moves (8 directions)
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if self.is_valid_position((new_row, new_col)):
                piece_at_destination = board.grid[new_row][new_col]
                
                # Empty square or enemy piece
                if piece_at_destination is None or piece_at_destination.color != self.color:
                    # If we're checking for check, verify the move doesn't leave king in check
                    if check_for_check:
                        # Create a temporary board and make the move
                        temp_board = board.clone()
                        # Create and make a move without checking validity
                        temp_move = Move((row, col), (new_row, new_col), self)
                        temp_board.make_move(temp_move, check_validity=False)
                        
                        # Check if king would be in check after move (directly checking opponents)
                        if not self._is_position_under_attack(temp_board, (new_row, new_col)):
                            moves.append((new_row, new_col))
                    else:
                        # Not checking for check, just add the move
                        moves.append((new_row, new_col))
        
        # Check for castling
        if self.can_castle(board, row, col):
            # Kingside castling
            if self.can_castle_kingside(board, row, col):
                moves.append((row, col + 2))
                
            # Queenside castling
            if self.can_castle_queenside(board, row, col):
                moves.append((row, col - 2))
                
        return moves
    
    def _is_position_under_attack(self, board, position):
        """
        Check if a position is under attack by any opponent piece.
        This is a simplified version that avoids recursive calls to is_in_check.
        """
        row, col = position
        opponent_color = "Black" if self.color == "White" else "White"
        
        # Check attacks by pawns
        pawn_direction = 1 if self.color == "White" else -1
        for dc in [-1, 1]:
            attacker_row, attacker_col = row + pawn_direction, col + dc
            if 0 <= attacker_row < 8 and 0 <= attacker_col < 8:
                piece = board.grid[attacker_row][attacker_col]
                if piece and isinstance(piece, Pawn) and piece.color == opponent_color:
                    return True
        
        # Check attacks by knights
        knight_moves = [
            (-2, -1), (-2, 1), (2, -1), (2, 1),
            (-1, -2), (-1, 2), (1, -2), (1, 2)
        ]
        for dr, dc in knight_moves:
            attacker_row, attacker_col = row + dr, col + dc
            if 0 <= attacker_row < 8 and 0 <= attacker_col < 8:
                piece = board.grid[attacker_row][attacker_col]
                if piece and isinstance(piece, Knight) and piece.color == opponent_color:
                    return True
        
        # Check attacks by queens, rooks, and bishops (sliding pieces)
        # Rook-style moves (horizontal and vertical)
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            for distance in range(1, 8):
                attacker_row, attacker_col = row + dr * distance, col + dc * distance
                if not (0 <= attacker_row < 8 and 0 <= attacker_col < 8):
                    break
                
                piece = board.grid[attacker_row][attacker_col]
                if piece:
                    if piece.color == opponent_color and (
                        isinstance(piece, Rook) or isinstance(piece, Queen)
                    ):
                        return True
                    break  # Blocked by some piece
        
        # Bishop-style moves (diagonal)
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dr, dc in directions:
            for distance in range(1, 8):
                attacker_row, attacker_col = row + dr * distance, col + dc * distance
                if not (0 <= attacker_row < 8 and 0 <= attacker_col < 8):
                    break
                
                piece = board.grid[attacker_row][attacker_col]
                if piece:
                    if piece.color == opponent_color and (
                        isinstance(piece, Bishop) or isinstance(piece, Queen)
                    ):
                        return True
                    break  # Blocked by some piece
        
        # Check attacks by the opponent's king (needed for some edge cases)
        king_moves = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]
        for dr, dc in king_moves:
            attacker_row, attacker_col = row + dr, col + dc
            if 0 <= attacker_row < 8 and 0 <= attacker_col < 8:
                piece = board.grid[attacker_row][attacker_col]
                if piece and isinstance(piece, King) and piece.color == opponent_color:
                    return True
        
        return False
    
    def can_castle(self, board, row, col):
        """Check if castling is possible in general."""
        # King cannot castle if it has moved or is in check
        if self.has_moved or board.is_in_check(self.color):
            return False
        return True
        
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
        
    def can_castle_queenside(self, board, row, col):
        """Check if queenside castling is possible."""
        # Already checked if king can castle in general
        if not self.can_castle(board, row, col):
            return False
            
        # Check if rook has moved
        rook_col = 0
        rook = board.grid[row][rook_col]
        if rook is None or not isinstance(rook, Rook) or rook.has_moved:
            return False
            
        # Check if squares between king and rook are empty
        for c in range(rook_col + 1, col):
            if board.grid[row][c] is not None:
                return False
                
        # Check if king would pass through check
        for c in range(col - 1, col - 3, -1):  # King moves 2 spaces
            # Create a temporary board
            temp_board = board.clone()
            # Move the king to this position
            temp_move = Move((row, col), (row, c), self)
            temp_board.make_move(temp_move, check_validity=False)
            
            # If this position is under attack, castling is not allowed
            if self._is_position_under_attack(temp_board, (row, c)):
                return False
                    
        return True
        
    def __str__(self):
        symbol = 'K' if self.color == 'White' else 'k'
        return symbol


class Queen(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.value = 9
        
    def get_valid_moves(self, board, position):
        """
        Get all valid moves for the Queen.
        
        Args:
            board: The current board state
            position (tuple): The current position of the queen (row, col)
            
        Returns:
            list: List of valid move positions (row, col)
        """
        # Queen moves like rook and bishop combined
        row, col = position
        moves = []
        
        # All 8 directions (horizontal, vertical, and diagonal)
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]
        
        for dr, dc in directions:
            for steps in range(1, 8):  # Maximum 7 steps in any direction
                new_row, new_col = row + dr * steps, col + dc * steps
                
                # Break if outside board
                if not self.is_valid_position((new_row, new_col)):
                    break
                    
                piece_at_destination = board.grid[new_row][new_col]
                
                if piece_at_destination is None:
                    # Empty square - valid move
                    moves.append((new_row, new_col))
                elif piece_at_destination.color != self.color:
                    # Enemy piece - valid move (capture)
                    moves.append((new_row, new_col))
                    break  # Can't move further in this direction
                else:
                    # Own piece - can't move here
                    break  # Can't move further in this direction
                    
        return moves
        
    def __str__(self):
        symbol = 'Q' if self.color == 'White' else 'q'
        return symbol


class Rook(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.value = 5
        
    def get_valid_moves(self, board, position):
        """
        Get all valid moves for the Rook.
        
        Args:
            board: The current board state
            position (tuple): The current position of the rook (row, col)
            
        Returns:
            list: List of valid move positions (row, col)
        """
        row, col = position
        moves = []
        
        # Rook moves horizontally and vertically
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        for dr, dc in directions:
            for steps in range(1, 8):  # Maximum 7 steps in any direction
                new_row, new_col = row + dr * steps, col + dc * steps
                
                # Break if outside board
                if not self.is_valid_position((new_row, new_col)):
                    break
                    
                piece_at_destination = board.grid[new_row][new_col]
                
                if piece_at_destination is None:
                    # Empty square - valid move
                    moves.append((new_row, new_col))
                elif piece_at_destination.color != self.color:
                    # Enemy piece - valid move (capture)
                    moves.append((new_row, new_col))
                    break  # Can't move further in this direction
                else:
                    # Own piece - can't move here
                    break  # Can't move further in this direction
                    
        return moves
        
    def __str__(self):
        symbol = 'R' if self.color == 'White' else 'r'
        return symbol


class Bishop(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.value = 3
        
    def get_valid_moves(self, board, position):
        """
        Get all valid moves for the Bishop.
        
        Args:
            board: The current board state
            position (tuple): The current position of the bishop (row, col)
            
        Returns:
            list: List of valid move positions (row, col)
        """
        row, col = position
        moves = []
        
        # Bishop moves diagonally
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        
        for dr, dc in directions:
            for steps in range(1, 8):  # Maximum 7 steps in any direction
                new_row, new_col = row + dr * steps, col + dc * steps
                
                # Break if outside board
                if not self.is_valid_position((new_row, new_col)):
                    break
                    
                piece_at_destination = board.grid[new_row][new_col]
                
                if piece_at_destination is None:
                    # Empty square - valid move
                    moves.append((new_row, new_col))
                elif piece_at_destination.color != self.color:
                    # Enemy piece - valid move (capture)
                    moves.append((new_row, new_col))
                    break  # Can't move further in this direction
                else:
                    # Own piece - can't move here
                    break  # Can't move further in this direction
                    
        return moves
        
    def __str__(self):
        symbol = 'B' if self.color == 'White' else 'b'
        return symbol


class Knight(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.value = 3
        
    def get_valid_moves(self, board, position):
        """
        Get all valid moves for the Knight.
        
        Args:
            board: The current board state
            position (tuple): The current position of the knight (row, col)
            
        Returns:
            list: List of valid move positions (row, col)
        """
        row, col = position
        moves = []
        
        # Knight moves in L-shape: 2 in one direction, 1 in the perpendicular direction
        knight_moves = [
            (-2, -1), (-2, 1), (2, -1), (2, 1),
            (-1, -2), (-1, 2), (1, -2), (1, 2)
        ]
        
        for dr, dc in knight_moves:
            new_row, new_col = row + dr, col + dc
            
            if self.is_valid_position((new_row, new_col)):
                piece_at_destination = board.grid[new_row][new_col]
                
                # Valid move if square is empty or contains enemy piece
                if piece_at_destination is None or piece_at_destination.color != self.color:
                    moves.append((new_row, new_col))
                    
        return moves
        
    def __str__(self):
        symbol = 'N' if self.color == 'White' else 'n'
        return symbol


class Pawn(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.value = 1
        self.en_passant_vulnerable = False
        
    def get_valid_moves(self, board, position):
        """
        Get all valid moves for the Pawn.
        
        Args:
            board: The current board state
            position (tuple): The current position of the pawn (row, col)
            
        Returns:
            list: List of valid move positions (row, col)
        """
        row, col = position
        moves = []
        
        # Direction depends on color (White pawns move up, Black pawns move down)
        direction = -1 if self.color == "White" else 1
        
        # Forward move (1 square)
        new_row = row + direction
        if self.is_valid_position((new_row, col)) and board.grid[new_row][col] is None:
            moves.append((new_row, col))
            
            # Initial two-square move
            if not self.has_moved:
                new_row = row + 2 * direction
                if self.is_valid_position((new_row, col)) and board.grid[new_row][col] is None:
                    moves.append((new_row, col))
                    
        # Capture moves (diagonally)
        for dc in [-1, 1]:
            new_row, new_col = row + direction, col + dc
            
            if not self.is_valid_position((new_row, new_col)):
                continue
                
            # Normal capture
            piece_at_destination = board.grid[new_row][new_col]
            if piece_at_destination and piece_at_destination.color != self.color:
                moves.append((new_row, new_col))
                
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
                    
        return moves
        
    def __str__(self):
        symbol = 'P' if self.color == 'White' else 'p'
        return symbol
