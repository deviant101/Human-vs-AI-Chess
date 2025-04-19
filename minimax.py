import math
from pieces import King, Queen, Rook, Bishop, Knight, Pawn

class Minimax:
    def __init__(self, depth=3):
        """
        Initialize the Minimax algorithm.
        
        Args:
            depth (int): Maximum search depth
        """
        self.depth = depth
        # Define positional values for each piece type
        
        # Pawn position values - better in center and advanced positions
        self.pawn_table = [
            [0,  0,  0,  0,  0,  0,  0,  0],
            [50, 50, 50, 50, 50, 50, 50, 50],
            [10, 10, 20, 30, 30, 20, 10, 10],
            [5,  5, 10, 25, 25, 10,  5,  5],
            [0,  0,  0, 20, 20,  0,  0,  0],
            [5, -5,-10,  0,  0,-10, -5,  5],
            [5, 10, 10,-20,-20, 10, 10,  5],
            [0,  0,  0,  0,  0,  0,  0,  0]
        ]
        
        # Knight position values - better in center
        self.knight_table = [
            [-50,-40,-30,-30,-30,-30,-40,-50],
            [-40,-20,  0,  0,  0,  0,-20,-40],
            [-30,  0, 10, 15, 15, 10,  0,-30],
            [-30,  5, 15, 20, 20, 15,  5,-30],
            [-30,  0, 15, 20, 20, 15,  0,-30],
            [-30,  5, 10, 15, 15, 10,  5,-30],
            [-40,-20,  0,  5,  5,  0,-20,-40],
            [-50,-40,-30,-30,-30,-30,-40,-50]
        ]
        
        # Bishop position values - better on diagonals
        self.bishop_table = [
            [-20,-10,-10,-10,-10,-10,-10,-20],
            [-10,  0,  0,  0,  0,  0,  0,-10],
            [-10,  0, 10, 10, 10, 10,  0,-10],
            [-10,  5,  5, 10, 10,  5,  5,-10],
            [-10,  0,  5, 10, 10,  5,  0,-10],
            [-10,  5,  5,  5,  5,  5,  5,-10],
            [-10,  0,  5,  0,  0,  0,  0,-10],
            [-20,-10,-10,-10,-10,-10,-10,-20]
        ]
        
        # Rook position values - better on open files
        self.rook_table = [
            [0,  0,  0,  0,  0,  0,  0,  0],
            [5, 10, 10, 10, 10, 10, 10,  5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [0,  0,  0,  5,  5,  0,  0,  0]
        ]
        
        # Queen position values
        self.queen_table = [
            [-20,-10,-10, -5, -5,-10,-10,-20],
            [-10,  0,  0,  0,  0,  0,  0,-10],
            [-10,  0,  5,  5,  5,  5,  0,-10],
            [-5,   0,  5,  5,  5,  5,  0, -5],
            [0,    0,  5,  5,  5,  5,  0, -5],
            [-10,  5,  5,  5,  5,  5,  0,-10],
            [-10,  0,  5,  0,  0,  0,  0,-10],
            [-20,-10,-10, -5, -5,-10,-10,-20]
        ]
        
        # King position values for middlegame - want to stay protected
        self.king_middle_table = [
            [-30,-40,-40,-50,-50,-40,-40,-30],
            [-30,-40,-40,-50,-50,-40,-40,-30],
            [-30,-40,-40,-50,-50,-40,-40,-30],
            [-30,-40,-40,-50,-50,-40,-40,-30],
            [-20,-30,-30,-40,-40,-30,-30,-20],
            [-10,-20,-20,-20,-20,-20,-20,-10],
            [20, 20,  0,  0,  0,  0, 20, 20],
            [20, 30, 10,  0,  0, 10, 30, 20]
        ]
        
        # King position values for endgame - want to be active
        self.king_end_table = [
            [-50,-40,-30,-20,-20,-30,-40,-50],
            [-30,-20,-10,  0,  0,-10,-20,-30],
            [-30,-10, 20, 30, 30, 20,-10,-30],
            [-30,-10, 30, 40, 40, 30,-10,-30],
            [-30,-10, 30, 40, 40, 30,-10,-30],
            [-30,-10, 20, 30, 30, 20,-10,-30],
            [-30,-30,  0,  0,  0,  0,-30,-30],
            [-50,-30,-30,-30,-30,-30,-30,-50]
        ]

    def find_best_move(self, board, color):
        """
        Find the best move for the given color using Minimax with Alpha-Beta Pruning.
        
        Args:
            board: Current board state
            color: Color to find the best move for
            
        Returns:
            Move: The best move found
        """
        best_score = float('-inf')
        best_move = None
        alpha = float('-inf')
        beta = float('inf')
        
        # Check all possible moves
        valid_moves = board.get_all_valid_moves(color)
        
        # If no moves available, return None
        if not valid_moves:
            return None
            
        for move in valid_moves:
            # Make the move on a temporary board
            temp_board = board.clone()
            temp_board.make_move(move)
            
            # Call minimax recursively for opponent's move
            score = self.minimax(temp_board, self.depth - 1, alpha, beta, False if color == "White" else True)
            
            # Undo the move (not needed with cloned board)
            if score > best_score:
                best_score = score
                best_move = move
                
            # Update alpha for pruning
            alpha = max(alpha, best_score)
            
        return best_move

    def minimax(self, board, depth, alpha, beta, maximizing_white):
        """
        Minimax algorithm with Alpha-Beta Pruning.
        
        Args:
            board: Current board state
            depth: Current search depth
            alpha: Alpha value for pruning
            beta: Beta value for pruning
            maximizing_white: True if maximizing for White, False if for Black
            
        Returns:
            float: The evaluation score
        """
        # Terminal conditions
        if depth == 0 or board.is_game_over():
            return self.evaluate_board(board, maximizing_white)
            
        color = "White" if maximizing_white else "Black"
        opponent_color = "Black" if maximizing_white else "White"
        
        # Check for checkmate or stalemate
        if board.is_checkmate(color):
            return float('-inf')  # worst possible outcome for current player
        elif board.is_checkmate(opponent_color):
            return float('inf')   # best possible outcome for current player
        elif board.is_stalemate(color) or board.is_stalemate(opponent_color):
            return 0  # draw
            
        # Get all valid moves for the current player
        valid_moves = board.get_all_valid_moves(color)
        
        if maximizing_white:
            max_eval = float('-inf')
            for move in valid_moves:
                temp_board = board.clone()
                temp_board.make_move(move)
                
                eval = self.minimax(temp_board, depth - 1, alpha, beta, False)
                max_eval = max(max_eval, eval)
                
                # Alpha-Beta Pruning
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
                    
            return max_eval
            
        else:
            min_eval = float('inf')
            for move in valid_moves:
                temp_board = board.clone()
                temp_board.make_move(move)
                
                eval = self.minimax(temp_board, depth - 1, alpha, beta, True)
                min_eval = min(min_eval, eval)
                
                # Alpha-Beta Pruning
                beta = min(beta, eval)
                if beta <= alpha:
                    break
                    
            return min_eval

    def evaluate_board(self, board, white_perspective=True):
        """
        Evaluate the current board position from the perspective of White (if white_perspective is True).
        
        Args:
            board: Current board state
            white_perspective (bool): True if evaluating from White's perspective
            
        Returns:
            float: Evaluation score
        """
        score = 0
        
        # Count material and positional advantages
        material_score = self.evaluate_material(board)
        
        # Evaluate piece positions
        positional_score = self.evaluate_positions(board)
        
        # Evaluate piece mobility (number of valid moves)
        mobility_score = self.evaluate_mobility(board)
        
        # Evaluate king safety
        king_safety_score = self.evaluate_king_safety(board)
        
        # Combine scores with weights
        score = (
            material_score * 1.0 +       # Material is most important
            positional_score * 0.3 +     # Positional advantage
            mobility_score * 0.2 +       # Mobility
            king_safety_score * 0.5      # King safety
        )
        
        # Negate the score if evaluating from Black's perspective
        if not white_perspective:
            score = -score
            
        return score
    
    def evaluate_material(self, board):
        """Evaluate the material balance on the board."""
        white_score = 0
        black_score = 0
        
        for row in range(8):
            for col in range(8):
                piece = board.grid[row][col]
                if piece:
                    # Use the piece value
                    if isinstance(piece, Pawn):
                        value = 100
                    elif isinstance(piece, Knight) or isinstance(piece, Bishop):
                        value = 300
                    elif isinstance(piece, Rook):
                        value = 500
                    elif isinstance(piece, Queen):
                        value = 900
                    else:  # King
                        value = 0  # Not counting king's material value
                        
                    if piece.color == "White":
                        white_score += value
                    else:
                        black_score += value
                        
        return white_score - black_score
    
    def evaluate_positions(self, board):
        """Evaluate piece positions using piece-square tables."""
        white_score = 0
        black_score = 0
        
        for row in range(8):
            for col in range(8):
                piece = board.grid[row][col]
                if piece:
                    if isinstance(piece, Pawn):
                        table = self.pawn_table
                    elif isinstance(piece, Knight):
                        table = self.knight_table
                    elif isinstance(piece, Bishop):
                        table = self.bishop_table
                    elif isinstance(piece, Rook):
                        table = self.rook_table
                    elif isinstance(piece, Queen):
                        table = self.queen_table
                    else:  # King
                        # Use different tables for middle and endgame
                        is_endgame = self.is_endgame(board)
                        table = self.king_end_table if is_endgame else self.king_middle_table
                        
                    # Get position value from appropriate table
                    if piece.color == "White":
                        # White pieces are at the bottom, so use the table as is
                        pos_value = table[row][col]
                        white_score += pos_value
                    else:
                        # Black pieces are at the top, so flip the table
                        pos_value = table[7 - row][col]
                        black_score += pos_value
                        
        return white_score - black_score
    
    def evaluate_mobility(self, board):
        """Evaluate piece mobility (number of legal moves)."""
        white_mobility = len(board.get_all_valid_moves("White"))
        black_mobility = len(board.get_all_valid_moves("Black"))
        
        return white_mobility - black_mobility
    
    def evaluate_king_safety(self, board):
        """Evaluate king safety."""
        white_king_pos = board.get_king_position("White")
        black_king_pos = board.get_king_position("Black")
        
        white_safety = 0
        black_safety = 0
        
        # Check if king is in check
        if board.is_in_check("White"):
            white_safety -= 50
        if board.is_in_check("Black"):
            black_safety -= 50
            
        # Count the number of pieces around the king (defenders)
        if white_king_pos:
            white_safety += self.count_protectors(board, white_king_pos, "White") * 10
        if black_king_pos:
            black_safety += self.count_protectors(board, black_king_pos, "Black") * 10
            
        # Evaluate pawn shield
        if white_king_pos:
            white_safety += self.evaluate_pawn_shield(board, white_king_pos, "White") * 5
        if black_king_pos:
            black_safety += self.evaluate_pawn_shield(board, black_king_pos, "Black") * 5
            
        return white_safety - black_safety
    
    def count_protectors(self, board, king_pos, color):
        """Count the number of friendly pieces around the king."""
        row, col = king_pos
        protectors = 0
        
        # Check all 8 squares around the king
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue  # Skip the king's position
                    
                new_row, new_col = row + dr, col + dc
                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    piece = board.grid[new_row][new_col]
                    if piece and piece.color == color:
                        protectors += 1
                        
        return protectors
    
    def evaluate_pawn_shield(self, board, king_pos, color):
        """Evaluate the pawn shield in front of the king."""
        row, col = king_pos
        shield_value = 0
        
        # Define the direction to look for pawns based on color
        direction = -1 if color == "White" else 1
        
        # Check the three columns in front of the king
        for dc in [-1, 0, 1]:
            shield_col = col + dc
            if 0 <= shield_col < 8:
                # Check one and two rows in front
                for steps in [1, 2]:
                    shield_row = row + direction * steps
                    if 0 <= shield_row < 8:
                        piece = board.grid[shield_row][shield_col]
                        if piece and isinstance(piece, Pawn) and piece.color == color:
                            shield_value += (3 - steps)  # More value for closer pawns
                            break  # Only count the first pawn in the column
                            
        return shield_value
    
    def is_endgame(self, board):
        """Determine if the current position is an endgame."""
        # Count the total material value excluding pawns
        total_value = 0
        for row in range(8):
            for col in range(8):
                piece = board.grid[row][col]
                if piece and not isinstance(piece, Pawn) and not isinstance(piece, King):
                    if isinstance(piece, Queen):
                        total_value += 900
                    elif isinstance(piece, Rook):
                        total_value += 500
                    elif isinstance(piece, Knight) or isinstance(piece, Bishop):
                        total_value += 300
                        
        # Consider it endgame if total material is less than 2300 
        # (less than a queen + rook + knight/bishop)
        return total_value < 2300
