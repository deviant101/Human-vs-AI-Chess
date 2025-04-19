from board import Board
from player import HumanPlayer, AIPlayer, GUIHumanPlayer

class ChessGame:
    def __init__(self, use_gui=False, ai_depth=3):
        """
        Initialize a new chess game.
        
        Args:
            use_gui (bool): Whether to use GUI players
            ai_depth (int): The search depth for the AI player
        """
        self.board = Board()
        if use_gui:
            self.human_player = GUIHumanPlayer("White")
        else:
            self.human_player = HumanPlayer("White")
        self.ai_player = AIPlayer("Black", depth=ai_depth)
        self.current_player = self.human_player
        self.game_status = "In progress"
        self.move_log = []

    def play(self):
        """Start the game loop for console play."""
        while not self.board.is_game_over():
            print(self.board)
            
            if self.current_player == self.human_player:
                print("Your turn (White)")
                move = self.current_player.get_move(self.board)
            else:
                print("AI is thinking...")
                move = self.current_player.get_move(self.board)
                print(f"AI moved: {move}")
                
            if move and self.board.is_valid_move(move):
                self.make_move(move)
            else:
                print("Invalid move. Try again.")
                
        # Game over
        print(self.board)
        print(self.board.get_game_result())

    def make_move(self, move):
        """
        Make a move and update the game state.
        
        Args:
            move: The Move object representing the move to make
            
        Returns:
            bool: True if the move was made successfully
        """
        if not move:
            return False
            
        if self.board.make_move(move):
            self.move_log.append(move)
            self.switch_turn()
            self.update_game_status()
            return True
        return False

    def switch_turn(self):
        """Switch the current player."""
        self.current_player = (
            self.human_player if self.current_player == self.ai_player else self.ai_player
        )

    def update_game_status(self):
        """Update the game status based on the current board state."""
        if self.board.is_checkmate("White"):
            self.game_status = "Checkmate - Black wins"
        elif self.board.is_checkmate("Black"):
            self.game_status = "Checkmate - White wins"
        elif self.board.is_stalemate("White") or self.board.is_stalemate("Black"):
            self.game_status = "Stalemate - Draw"
        elif self.board.is_in_check("White"):
            self.game_status = "White is in check"
        elif self.board.is_in_check("Black"):
            self.game_status = "Black is in check"
        else:
            self.game_status = "In progress"

    def is_game_over(self):
        """Check if the game is over."""
        return self.board.is_game_over()

    def get_game_result(self):
        """Get the result of the game."""
        return self.board.get_game_result()

    def get_status_message(self):
        """Get a status message for display."""
        return self.game_status
        
    def get_current_player_color(self):
        """Get the color of the current player."""
        return self.current_player.color
        
    def handle_gui_move(self, move_str):
        """
        Handle a move from the GUI.
        
        Args:
            move_str (str): String representation of the move
            
        Returns:
            bool: True if the move was valid and executed
        """
        if self.current_player == self.human_player and isinstance(self.human_player, GUIHumanPlayer):
            move = Move.from_string(move_str, self.board)
            if move and self.board.is_valid_move(move):
                return self.make_move(move)
        return False
