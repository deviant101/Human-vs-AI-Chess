from abc import ABC, abstractmethod
from minimax import Minimax
from move import Move

class Player(ABC):
    """Abstract base class for players."""
    
    def __init__(self, color):
        """
        Initialize a player.
        
        Args:
            color (str): The color of the player ('White' or 'Black')
        """
        self.color = color

    @abstractmethod
    def get_move(self, board):
        """
        Abstract method to get a move from the player.
        
        Args:
            board: The current board state
            
        Returns:
            Move: A Move object representing the player's move
        """
        pass


class HumanPlayer(Player):
    """Human player that inputs moves manually."""
    
    def __init__(self, color):
        """Initialize a human player."""
        super().__init__(color)
    
    def get_move(self, board):
        """
        Get a move from human input.
        
        Args:
            board: The current board state
            
        Returns:
            Move: A Move object representing the player's move
        """
        while True:
            try:
                move_str = input(f"{self.color}'s move (e.g., 'e2e4' or 'O-O' for castling): ")
                move = Move.from_string(move_str, board)
                
                if move and board.is_valid_move(move):
                    return move
                else:
                    print("Invalid move. Please try again.")
            except Exception as e:
                print(f"Invalid input: {e}")


class AIPlayer(Player):
    """AI player that uses the Minimax algorithm to make moves."""
    
    def __init__(self, color, depth=3):
        """
        Initialize an AI player.
        
        Args:
            color (str): The color of the player ('White' or 'Black')
            depth (int): The search depth for the Minimax algorithm
        """
        super().__init__(color)
        self.minimax = Minimax(depth)
    
    def get_move(self, board):
        """
        Get a move from the AI using Minimax.
        
        Args:
            board: The current board state
            
        Returns:
            Move: A Move object representing the AI's move
        """
        print(f"{self.color} AI is thinking...")
        best_move = self.minimax.find_best_move(board, self.color)
        
        if best_move:
            return best_move
        else:
            # If no best move is found (shouldn't happen unless game is over)
            valid_moves = board.get_all_valid_moves(self.color)
            if valid_moves:
                return valid_moves[0]  # Return any valid move
            return None  # No valid moves (checkmate or stalemate)


class GUIHumanPlayer(HumanPlayer):
    """Human player that interacts through the GUI."""
    
    def __init__(self, color):
        """Initialize a GUI human player."""
        super().__init__(color)
        self.gui_move = None
    
    def set_move(self, move):
        """
        Set the move from the GUI.
        
        Args:
            move: The Move object representing the user's move
        """
        self.gui_move = move
    
    def get_move(self, board):
        """
        Get a move from the GUI input.
        
        Args:
            board: The current board state
            
        Returns:
            Move: A Move object representing the player's move
        """
        # This method is called by the game loop
        # It should wait until a move is set by the GUI
        
        # In a real implementation, this would have a way to wait for GUI input
        # For this simplified version, we'll just return the current move if it exists
        
        # Reset the move so it's not used again
        move = self.gui_move
        self.gui_move = None
        return move
