import tkinter as tk
from tkinter import messagebox, ttk
import threading
import time
from move import Move

class ChessGUI:
    def __init__(self, game):
        """
        Initialize the Chess GUI.
        
        Args:
            game: The ChessGame instance to display
        """
        self.game = game
        self.root = tk.Tk()
        self.root.title("Chess Game - Human vs AI")
        
        # Set up the main window
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        self.root.config(bg="#2c3e50")
        
        # Board colors
        self.light_square = "#f0d9b5"  # Light brown
        self.dark_square = "#b58863"   # Dark brown
        self.highlight_color = "#646d40"  # Highlight for selected squares
        
        # Piece images (will be loaded later)
        self.piece_images = {}
        self.square_size = 64  # Size of each square in pixels
        
        # Selected square for moves
        self.selected_square = None
        
        # Status of last AI move in progress
        self.ai_move_in_progress = False
        
        self.create_widgets()
        self.load_piece_images()
        self.update_board()
        
    def create_widgets(self):
        """Create all the GUI elements."""
        # Main layout frames
        self.left_frame = tk.Frame(self.root, bg="#2c3e50")
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.right_frame = tk.Frame(self.root, bg="#2c3e50", width=200)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=10, pady=10)
        self.right_frame.pack_propagate(False)
        
        # Chess board (8x8 grid of labels with fixed size)
        self.board_frame = tk.Frame(self.left_frame, bg="#1e272e", padx=20, pady=20)
        self.board_frame.pack(padx=10, pady=10)
        
        # Configure rows and columns to have equal weight
        for i in range(8):
            self.board_frame.grid_columnconfigure(i, weight=1, minsize=self.square_size)
            self.board_frame.grid_rowconfigure(i, weight=1, minsize=self.square_size)
        
        self.squares = []
        for row in range(8):
            row_squares = []
            for col in range(8):
                # Create a label for each square with fixed size
                square = tk.Label(
                    self.board_frame, 
                    width=4, 
                    height=2,
                    bg=self.light_square if (row + col) % 2 == 0 else self.dark_square,
                    borderwidth=0
                )
                square.grid(row=row, column=col, sticky="nsew")  # Make the label fill the entire cell
                square.bind("<Button-1>", lambda e, r=row, c=col: self.square_clicked(r, c))
                row_squares.append(square)
            self.squares.append(row_squares)
            
        # Add row and column labels around the board
        files = "abcdefgh"
        ranks = "87654321"  # Top to bottom in the GUI
        
        # Configure the label column and row to have minimal size
        self.board_frame.grid_columnconfigure(8, weight=0, minsize=20)
        self.board_frame.grid_rowconfigure(8, weight=0, minsize=20)
        
        # Row labels (ranks)
        for i in range(8):
            rank_label = tk.Label(
                self.board_frame, 
                text=ranks[i], 
                bg="#1e272e", 
                fg="white",
                font=("Arial", 12)
            )
            rank_label.grid(row=i, column=8, padx=5, sticky="w")
        
        # Column labels (files)
        for i in range(8):
            file_label = tk.Label(
                self.board_frame, 
                text=files[i], 
                bg="#1e272e", 
                fg="white",
                font=("Arial", 12)
            )
            file_label.grid(row=8, column=i, pady=5, sticky="n")
            
        # Right side panel for game info and controls
        # Status display
        self.status_label = tk.Label(
            self.right_frame, 
            text="Game Status: In progress", 
            bg="#2c3e50", 
            fg="white",
            font=("Arial", 12),
            wraplength=180
        )
        self.status_label.pack(pady=10)
        
        # Turn display
        self.turn_label = tk.Label(
            self.right_frame, 
            text="Current Turn: White", 
            bg="#2c3e50", 
            fg="white",
            font=("Arial", 12)
        )
        self.turn_label.pack(pady=10)
        
        # Move input box
        move_frame = tk.Frame(self.right_frame, bg="#2c3e50")
        move_frame.pack(pady=20)
        
        move_label = tk.Label(
            move_frame, 
            text="Enter move:", 
            bg="#2c3e50", 
            fg="white",
            font=("Arial", 12)
        )
        move_label.pack(anchor="w")
        
        self.move_entry = tk.Entry(move_frame, font=("Arial", 12), width=15)
        self.move_entry.pack(pady=5)
        self.move_entry.bind("<Return>", self.make_move_from_input)
        
        move_button = tk.Button(
            move_frame, 
            text="Make Move", 
            command=self.make_move_from_input,
            bg="#3498db", 
            fg="white",
            font=("Arial", 10, "bold"),
            padx=10
        )
        move_button.pack(pady=5)
        
        # Help text for move format
        help_text = """Move format examples:
- e2e4 (standard move)
- O-O or 0-0 (kingside castle)
- O-O-O or 0-0-0 (queenside castle)
- e7e8q (pawn promotion to queen)
- e7e8r (promotion to rook)
- e7e8b (promotion to bishop)
- e7e8n (promotion to knight)
"""
        help_label = tk.Label(
            self.right_frame, 
            text=help_text, 
            bg="#2c3e50", 
            fg="#bdc3c7",
            font=("Arial", 10),
            justify=tk.LEFT,
            wraplength=180
        )
        help_label.pack(pady=10, anchor="w")
        
        # New game and quit buttons
        button_frame = tk.Frame(self.right_frame, bg="#2c3e50")
        button_frame.pack(side=tk.BOTTOM, pady=20)
        
        new_game_button = tk.Button(
            button_frame, 
            text="New Game", 
            command=self.new_game,
            bg="#27ae60", 
            fg="white",
            font=("Arial", 10, "bold"),
            padx=10
        )
        new_game_button.pack(side=tk.LEFT, padx=5)
        
        quit_button = tk.Button(
            button_frame, 
            text="Quit", 
            command=self.root.destroy,
            bg="#e74c3c", 
            fg="white",
            font=("Arial", 10, "bold"),
            padx=10
        )
        quit_button.pack(side=tk.LEFT, padx=5)

    def load_piece_images(self):
        """Create simple text representations for chess pieces."""
        # For a real implementation, you would load actual images
        # For this simple version, we'll use text representations
        piece_symbols = {
            'K': '♔', 'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘', 'P': '♙',  # White pieces
            'k': '♚', 'q': '♛', 'r': '♜', 'b': '♝', 'n': '♞', 'p': '♟'   # Black pieces
        }
        
        for symbol, unicode_char in piece_symbols.items():
            self.piece_images[symbol] = unicode_char

    def update_board(self):
        """Update the board display based on the current game state."""
        for row in range(8):
            for col in range(8):
                square = self.squares[row][col]
                piece = self.game.board.grid[row][col]
                
                # Set background color (and handle highlighting)
                is_highlighted = (self.selected_square == (row, col))
                if is_highlighted:
                    square.config(bg=self.highlight_color)
                else:
                    square.config(bg=self.light_square if (row + col) % 2 == 0 else self.dark_square)
                
                # Display piece if there is one
                if piece:
                    piece_symbol = str(piece)
                    if piece_symbol in self.piece_images:
                        # Use a larger font size for the chess pieces
                        square.config(text=self.piece_images[piece_symbol], font=("Arial", 32))
                    else:
                        square.config(text=piece_symbol, font=("Arial", 14))
                else:
                    square.config(text="")
                    
        # Update status and turn labels
        self.status_label.config(text=f"Game Status: {self.game.get_status_message()}")
        self.turn_label.config(text=f"Current Turn: {self.game.get_current_player_color()}")

    def square_clicked(self, row, col):
        """Handle click on a square - for selecting pieces and showing valid moves."""
        if self.ai_move_in_progress:
            return  # Ignore clicks during AI's turn
            
        # If we're not on the human player's turn, do nothing
        if self.game.current_player != self.game.human_player:
            return
            
        piece = self.game.board.grid[row][col]
        
        # If no square is selected yet and clicked on our own piece
        if self.selected_square is None and piece and piece.color == self.game.human_player.color:
            self.selected_square = (row, col)
            self.update_board()  # Update to highlight the selected square
            return
            
        # If a square is already selected
        if self.selected_square:
            src_row, src_col = self.selected_square
            
            # Try to make a move
            move = self.game.board.create_move((src_row, src_col), (row, col))
            
            if move and self.game.board.is_valid_move(move):
                # Valid move - execute it
                success = self.game.make_move(move)
                if success:
                    # Update the board
                    self.update_board()
                    
                    # If game is not over, let AI make its move
                    if not self.game.is_game_over():
                        self.schedule_ai_move()
                    else:
                        messagebox.showinfo("Game Over", self.game.get_game_result())
            
            # Reset selection either way
            self.selected_square = None
            self.update_board()
        else:
            # Clicked on empty square or opponent's piece with no selection
            pass

    def make_move_from_input(self, event=None):
        """Handle move input from the text box."""
        if self.ai_move_in_progress:
            return  # Ignore input during AI's turn
            
        # If we're not on the human player's turn, do nothing
        if self.game.current_player != self.game.human_player:
            return
            
        move_str = self.move_entry.get().strip()
        if not move_str:
            return
            
        # Clear the input box
        self.move_entry.delete(0, tk.END)
        
        # Parse the move string
        move = Move.from_string(move_str, self.game.board)
        
        if move and self.game.board.is_valid_move(move):
            # Valid move - execute it
            success = self.game.make_move(move)
            if success:
                # Update the board
                self.update_board()
                
                # If game is not over, let AI make its move
                if not self.game.is_game_over():
                    self.schedule_ai_move()
                else:
                    messagebox.showinfo("Game Over", self.game.get_game_result())
        else:
            messagebox.showerror("Invalid Move", "The move you entered is not valid. Please try again.")

    def schedule_ai_move(self):
        """Schedule AI move in a separate thread to keep the UI responsive."""
        self.ai_move_in_progress = True
        self.status_label.config(text="AI is thinking...")
        self.root.update_idletasks()
        
        # Run AI move in a separate thread
        ai_thread = threading.Thread(target=self.make_ai_move)
        ai_thread.daemon = True
        ai_thread.start()

    def make_ai_move(self):
        """Have the AI make its move."""
        # Add a small delay to make it more natural
        time.sleep(1)
        
        # Get AI's move
        move = self.game.ai_player.get_move(self.game.board)
        
        # Make the move
        if move:
            self.game.make_move(move)
            
        # Update UI after the move
        self.root.after(0, self.after_ai_move)

    def after_ai_move(self):
        """Update UI after AI's move."""
        self.ai_move_in_progress = False
        self.update_board()
        
        # Check if game is over
        if self.game.is_game_over():
            messagebox.showinfo("Game Over", self.game.get_game_result())

    def new_game(self):
        """Reset the game."""
        # Reinitialize the game
        self.game.__init__(use_gui=True)
        self.selected_square = None
        self.ai_move_in_progress = False
        self.update_board()
        messagebox.showinfo("New Game", "New game started. You play as White.")

    def run(self):
        """Start the main GUI loop."""
        self.root.mainloop()
