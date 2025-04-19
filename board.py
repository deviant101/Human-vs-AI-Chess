from move import Move
from pieces import King, Queen, Rook, Bishop, Knight, Pawn
import copy

class Board:
    def __init__(self):
        """Initialize a new chess board with pieces in their starting positions."""
        self.grid = [[None for _ in range(8)] for _ in range(8)]
        self.initialize_board()
        self.current_turn = "White"
        self.last_move = None
        self.move_history = []

    def initialize_board(self):
        """Set up pieces in their initial positions."""
        # Place pawns
        for col in range(8):
            self.grid[1][col] = Pawn("Black")
            self.grid[6][col] = Pawn("White")
            
        # Place rooks
        self.grid[0][0] = Rook("Black")
        self.grid[0][7] = Rook("Black")
        self.grid[7][0] = Rook("White")
        self.grid[7][7] = Rook("White")
        
        # Place knights
        self.grid[0][1] = Knight("Black")
        self.grid[0][6] = Knight("Black")
        self.grid[7][1] = Knight("White")
        self.grid[7][6] = Knight("White")
        
        # Place bishops
        self.grid[0][2] = Bishop("Black")
        self.grid[0][5] = Bishop("Black")
        self.grid[7][2] = Bishop("White")
        self.grid[7][5] = Bishop("White")
        
        # Place queens
        self.grid[0][3] = Queen("Black")
        self.grid[7][3] = Queen("White")
        
        # Place kings
        self.grid[0][4] = King("Black")
        self.grid[7][4] = King("White")

    def get_piece_position(self, piece_type, color):
        """
        Find the position of a specific piece type and color.
        
        Args:
            piece_type: The class of the piece to find
            color: The color of the piece
            
        Returns:
            tuple: (row, col) position of the piece or None if not found
        """
        for row in range(8):
            for col in range(8):
                piece = self.grid[row][col]
                if piece and isinstance(piece, piece_type) and piece.color == color:
                    return (row, col)
        return None

    def get_king(self, color):
        """Get the King piece of the specified color."""
        for row in range(8):
            for col in range(8):
                piece = self.grid[row][col]
                if piece and isinstance(piece, King) and piece.color == color:
                    return piece
        return None
        
    def get_king_position(self, color):
        """Get the position of the king of the specified color."""
        return self.get_piece_position(King, color)

    def create_move(self, source, destination):
        """
        Create a Move object for a move from source to destination.
        
        Args:
            source (tuple): (row, col) of the source square
            destination (tuple): (row, col) of the destination square
            
        Returns:
            Move: A Move object representing the move
        """
        src_row, src_col = source
        dst_row, dst_col = destination
        
        piece = self.grid[src_row][src_col]
        if not piece:
            return None
            
        move_type = "normal"
        captured_piece = None
        promotion_piece = None
        
        # Check for captures
        if self.grid[dst_row][dst_col]:
            move_type = "capture"
            captured_piece = self.grid[dst_row][dst_col]
            
        # Check for castling
        if isinstance(piece, King) and abs(src_col - dst_col) == 2:
            move_type = "castling"
            
        # Check for en passant
        if (isinstance(piece, Pawn) and 
            src_col != dst_col and 
            not self.grid[dst_row][dst_col]):
            move_type = "en_passant"
            captured_piece = self.grid[src_row][dst_col]  # The pawn being captured
            
        # Check for promotion
        if (isinstance(piece, Pawn) and 
            ((dst_row == 0 and piece.color == "White") or 
             (dst_row == 7 and piece.color == "Black"))):
            move_type = "promotion"
            promotion_piece = Queen(piece.color)  # Default promotion to Queen
            
        return Move(source, destination, piece, move_type, captured_piece, promotion_piece)

    def make_move(self, move, check_validity=True):
        """
        Make a move on the board.
        
        Args:
            move: The Move object representing the move
            check_validity: Whether to check if the move is valid
            
        Returns:
            bool: True if the move was made, False otherwise
        """
        if check_validity and not self.is_valid_move(move):
            return False
            
        src_row, src_col = move.source
        dst_row, dst_col = move.destination
        piece = move.piece
        
        # Reset en passant vulnerability for all pawns before making a new move
        for row in range(8):
            for col in range(8):
                if self.grid[row][col] and isinstance(self.grid[row][col], Pawn):
                    self.grid[row][col].en_passant_vulnerable = False
        
        # Update the board
        self.grid[dst_row][dst_col] = piece
        self.grid[src_row][src_col] = None
        piece.has_moved = True
        
        # Handle special moves
        if move.move_type == "castling":
            # Move the rook as well
            if dst_col > src_col:  # Kingside castling
                rook = self.grid[src_row][7]
                self.grid[src_row][7] = None
                self.grid[src_row][dst_col - 1] = rook
                rook.has_moved = True
            else:  # Queenside castling
                rook = self.grid[src_row][0]
                self.grid[src_row][0] = None
                self.grid[src_row][dst_col + 1] = rook
                rook.has_moved = True
                
        elif move.move_type == "en_passant":
            # Remove the captured pawn (which is on the same row as the source, same column as the destination)
            self.grid[src_row][dst_col] = None
            
        elif move.move_type == "promotion":
            # Replace the pawn with the promotion piece
            self.grid[dst_row][dst_col] = move.promotion_piece
        
        # Set en passant vulnerability for pawn double moves
        if isinstance(piece, Pawn) and abs(src_row - dst_row) == 2:
            piece.en_passant_vulnerable = True
            
        # Record the move
        self.last_move = move
        self.move_history.append(move)
        
        # Switch turns
        self.current_turn = "Black" if self.current_turn == "White" else "White"
            
        return True

    def undo_move(self):
        """
        Undo the last move made on the board.
        
        Returns:
            bool: True if a move was undone, False otherwise
        """
        if not self.move_history:
            return False
            
        move = self.move_history.pop()
        src_row, src_col = move.source
        dst_row, dst_col = move.destination
        piece = self.grid[dst_row][dst_col] if move.move_type != "promotion" else move.piece
        
        # Restore the piece to its source position
        self.grid[src_row][src_col] = piece
        
        # Restore any captured piece or clear the destination
        if move.captured_piece:
            if move.move_type == "en_passant":
                self.grid[src_row][dst_col] = move.captured_piece
                self.grid[dst_row][dst_col] = None
            else:
                self.grid[dst_row][dst_col] = move.captured_piece
        else:
            self.grid[dst_row][dst_col] = None
            
        # Restore castling state
        if move.move_type == "castling":
            if dst_col > src_col:  # Kingside castling
                rook = self.grid[src_row][dst_col - 1]
                self.grid[src_row][7] = rook
                self.grid[src_row][dst_col - 1] = None
                rook.has_moved = False
            else:  # Queenside castling
                rook = self.grid[src_row][dst_col + 1]
                self.grid[src_row][0] = rook
                self.grid[src_row][dst_col + 1] = None
                rook.has_moved = False
                
        # Restore piece state
        piece.has_moved = False  # This is simplified; in a real implementation, we'd track the previous state
        
        # Restore the current turn
        self.current_turn = "Black" if self.current_turn == "White" else "White"
        
        # Update last move
        self.last_move = self.move_history[-1] if self.move_history else None
        
        return True

    def is_valid_move(self, move):
        """
        Check if a move is valid.
        
        Args:
            move: The Move object representing the move
            
        Returns:
            bool: True if the move is valid, False otherwise
        """
        src_row, src_col = move.source
        dst_row, dst_col = move.destination
        piece = move.piece
        
        # Basic checks
        if not (0 <= src_row < 8 and 0 <= src_col < 8 and 0 <= dst_row < 8 and 0 <= dst_col < 8):
            return False
            
        if piece.color != self.current_turn:
            return False
            
        # Check if the move is in the list of valid moves for the piece
        valid_destinations = [pos for pos in piece.get_valid_moves(self, (src_row, src_col))]
        if (dst_row, dst_col) not in valid_destinations:
            return False
            
        # Make the move temporarily and check if it puts the king in check
        temp_board = self.clone()
        temp_board.make_move(move, check_validity=False)
        
        if temp_board.is_in_check(piece.color):
            return False
            
        return True

    def is_in_check(self, color):
        """
        Check if the specified color is in check.
        
        Args:
            color: The color to check for
            
        Returns:
            bool: True if the specified color is in check, False otherwise
        """
        king_position = self.get_king_position(color)
        if not king_position:
            return False  # No king found (shouldn't happen in a real game)
            
        # Get the king object
        king_row, king_col = king_position
        king = self.grid[king_row][king_col]
        
        # Use the King's own method to determine if it's under attack
        # This avoids the recursive calls that were causing the stack overflow
        if isinstance(king, King):
            return king._is_position_under_attack(self, king_position)
        
        return False

    def is_checkmate(self, color):
        """
        Check if the specified color is in checkmate.
        
        Args:
            color: The color to check for
            
        Returns:
            bool: True if the specified color is in checkmate, False otherwise
        """
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

    def is_stalemate(self, color):
        """
        Check if the specified color is in stalemate.
        
        Args:
            color: The color to check for
            
        Returns:
            bool: True if the specified color is in stalemate, False otherwise
        """
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

    def is_game_over(self):
        """
        Check if the game is over (checkmate or stalemate).
        
        Returns:
            bool: True if the game is over, False otherwise
        """
        return (self.is_checkmate("White") or 
                self.is_checkmate("Black") or 
                self.is_stalemate("White") or 
                self.is_stalemate("Black"))

    def get_game_result(self):
        """
        Get the result of the game.
        
        Returns:
            str: A string describing the game result
        """
        if self.is_checkmate("White"):
            return "Checkmate! Black wins."
        elif self.is_checkmate("Black"):
            return "Checkmate! White wins."
        elif self.is_stalemate("White") or self.is_stalemate("Black"):
            return "Stalemate! The game is a draw."
        else:
            return "Game in progress."

    def get_all_valid_moves(self, color):
        """
        Get all valid moves for a specific color.
        
        Args:
            color: The color to get moves for
            
        Returns:
            list: List of all valid moves
        """
        moves = []
        
        for row in range(8):
            for col in range(8):
                piece = self.grid[row][col]
                if piece and piece.color == color:
                    for move_pos in piece.get_valid_moves(self, (row, col)):
                        move = self.create_move((row, col), move_pos)
                        if self.is_valid_move(move):
                            moves.append(move)
                            
        return moves

    def clone(self):
        """
        Create a deep copy of the board.
        
        Returns:
            Board: A new Board object with the same state
        """
        new_board = Board()
        new_board.grid = [[None for _ in range(8)] for _ in range(8)]
        
        for row in range(8):
            for col in range(8):
                piece = self.grid[row][col]
                if piece:
                    # Create a new piece of the same type and color
                    piece_type = type(piece)
                    new_piece = piece_type(piece.color)
                    new_piece.has_moved = piece.has_moved
                    if hasattr(piece, 'en_passant_vulnerable'):
                        new_piece.en_passant_vulnerable = piece.en_passant_vulnerable
                    new_board.grid[row][col] = new_piece
                    
        new_board.current_turn = self.current_turn
        new_board.last_move = self.last_move  # Note: this is a shallow copy
        new_board.move_history = copy.copy(self.move_history)  # Shallow copy of move history
        
        return new_board

    def __str__(self):
        """
        Get a string representation of the board.
        
        Returns:
            str: A string representing the current board state
        """
        result = "  a b c d e f g h\n"
        for row in range(8):
            result += f"{8 - row} "
            for col in range(8):
                piece = self.grid[row][col]
                if piece:
                    result += str(piece) + " "
                else:
                    result += ". "
            result += f"{8 - row}\n"
        result += "  a b c d e f g h\n"
        result += f"Current turn: {self.current_turn}\n"
        
        # Add check and checkmate information
        if self.is_checkmate("White"):
            result += "White is in checkmate!"
        elif self.is_checkmate("Black"):
            result += "Black is in checkmate!"
        elif self.is_in_check("White"):
            result += "White is in check!"
        elif self.is_in_check("Black"):
            result += "Black is in check!"
        elif self.is_stalemate("White") or self.is_stalemate("Black"):
            result += "Stalemate! The game is a draw."
            
        return result
