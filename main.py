import sys
from PyQt5.QtWidgets import QDialog
from ui.app import ChessApp

if __name__ == "__main__":
    app = ChessApp(sys.argv)
    sys.exit(app.exec_())