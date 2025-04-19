class Move:
    def __init__(self, source, destination, piece, move_type="normal", captured_piece=None, promotion_piece=None):
        """
        Initialize a Move object.
        
        Args:
            source (tuple): The source position (row, col)
            destination (tuple): The destination position (row, col)
            piece: The piece being moved
            move_type (str): Type of move (normal, capture, castling, en_passant, promotion)
            captured_piece: The piece being captured (if any)
            promotion_piece: The piece to promote to (if pawn promotion)
        """
        self.source = source
        self.destination = destination
        self.piece = piece
        self.move_type = move_type  # normal, capture, castling, en_passant, promotion
        self.captured_piece = captured_piece
        self.promotion_piece = promotion_piece

    def __str__(self):
        """String representation of the move in algebraic notation."""
        files = "abcdefgh"
        ranks = "12345678"
        
        src_file = files[self.source[1]]
        src_rank = ranks[7 - self.source[0]]  # Convert from 0-7 to chess ranks correctly
        dst_file = files[self.destination[1]]
        dst_rank = ranks[7 - self.destination[0]]
        
        if self.move_type == "castling":
            # Kingside or queenside castling
            if self.destination[1] > self.source[1]:
                return "O-O"  # Kingside
            else:
                return "O-O-O"  # Queenside
        
        move_str = f"{src_file}{src_rank}{dst_file}{dst_rank}"
        
        if self.move_type == "promotion" and self.promotion_piece:
            # Add the promotion piece symbol
            piece_symbols = {"Queen": "q", "Rook": "r", "Bishop": "b", "Knight": "n"}
            if self.promotion_piece.__class__.__name__ in piece_symbols:
                move_str += piece_symbols[self.promotion_piece.__class__.__name__]
        
        return move_str
    
    @classmethod
    def from_string(cls, move_str, board):
        """
        Create a Move object from a string representation (e.g., 'e2e4').
        
        Args:
            move_str (str): String representation of the move
            board (Board): Current board state to determine pieces
            
        Returns:
            Move: A new Move object, or None if the string is invalid
        """
        if not move_str or len(move_str) < 4:
            return None
            
        # Handle castling notation
        if move_str == "O-O" or move_str == "0-0":  # Kingside castling
            king = board.get_king(board.current_turn)
            if not king:
                return None
            row = 0 if king.color == "Black" else 7
            return cls((row, 4), (row, 6), king, move_type="castling")
            
        elif move_str == "O-O-O" or move_str == "0-0-0":  # Queenside castling
            king = board.get_king(board.current_turn)
            if not king:
                return None
            row = 0 if king.color == "Black" else 7
            return cls((row, 4), (row, 2), king, move_type="castling")
        
        # Parse standard coordinate notation (e.g., e2e4)
        files = "abcdefgh"
        ranks = "12345678"
        
        if len(move_str) >= 4:
            src_file = move_str[0].lower()
            src_rank = move_str[1]
            dst_file = move_str[2].lower()
            dst_rank = move_str[3]
            
            # Convert to board coordinates
            if (src_file in files and src_rank in ranks and 
                dst_file in files and dst_rank in ranks):
                
                src_col = files.index(src_file)
                src_row = 8 - int(src_rank)  # Corrected: Convert from 1-8 to 0-7 indexing
                dst_col = files.index(dst_file)
                dst_row = 8 - int(dst_rank)  # Corrected: Convert from 1-8 to 0-7 indexing
                
                source = (src_row, src_col)
                destination = (dst_row, dst_col)
                
                # Get the piece at the source
                piece = board.grid[src_row][src_col]
                if not piece:
                    return None
                
                # Determine move type
                move_type = "normal"
                captured_piece = None
                promotion_piece = None
                
                # Check if it's a capture
                if board.grid[dst_row][dst_col] is not None:
                    move_type = "capture"
                    captured_piece = board.grid[dst_row][dst_col]
                
                # Check if it's a pawn promotion
                if piece.__class__.__name__ == "Pawn":
                    if (dst_row == 0 and piece.color == "White") or (dst_row == 7 and piece.color == "Black"):
                        move_type = "promotion"
                        
                        # If promotion piece is specified
                        if len(move_str) > 4:
                            promotion_type = move_str[4].lower()
                            from pieces import Queen, Rook, Bishop, Knight
                            promotion_map = {
                                'q': Queen,
                                'r': Rook,
                                'b': Bishop,
                                'n': Knight
                            }
                            if promotion_type in promotion_map:
                                promotion_piece = promotion_map[promotion_type](piece.color)
                            else:
                                promotion_piece = Queen(piece.color)  # Default to queen if not specified
                        else:
                            from pieces import Queen
                            promotion_piece = Queen(piece.color)  # Default to queen
                
                # Check if it's en passant - Improved detection logic
                if (piece.__class__.__name__ == "Pawn" and 
                    src_col != dst_col and 
                    board.grid[dst_row][dst_col] is None):
                    
                    # Check if this is actually an en passant capture (only if last move was a double pawn move)
                    if board.last_move and board.last_move.piece.__class__.__name__ == "Pawn":
                        last_move = board.last_move
                        # Check if the opponent's pawn just moved two squares and is now adjacent
                        if (abs(last_move.source[0] - last_move.destination[0]) == 2 and
                            last_move.destination[1] == dst_col and
                            last_move.destination[0] == src_row):
                            
                            move_type = "en_passant"
                            captured_row = src_row
                            captured_col = dst_col
                            captured_piece = board.grid[captured_row][captured_col]
                
                return cls(source, destination, piece, move_type, captured_piece, promotion_piece)
        
        return None
