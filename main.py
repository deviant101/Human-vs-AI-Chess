import argparse
from chess_game import ChessGame
from gui import ChessGUI

def main():
    """Main entry point for the chess game."""
    parser = argparse.ArgumentParser(description='Chess Game - Human vs AI')
    parser.add_argument('--console', action='store_true', help='Run in console mode (no GUI)')
    parser.add_argument('--depth', type=int, default=3, help='AI search depth (default: 3)')
    args = parser.parse_args()
    
    if args.console:
        # Run in console mode
        game = ChessGame(use_gui=False, ai_depth=args.depth)
        game.play()
    else:
        # Run with GUI
        game = ChessGame(use_gui=True, ai_depth=args.depth)
        gui = ChessGUI(game)
        gui.run()

if __name__ == "__main__":
    main()