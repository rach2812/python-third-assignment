"""
CSSE1001 Assignment 3
Semester 1, 2017
"""

import tkinter as tk
from tkinter import messagebox

import random

import model
import view
from game_regular import RegularGame
# # For alternative game modes
# from game_make13 import Make13Game
# from game_lucky7 import Lucky7Game
# from game_unlimited import UnlimitedGame
from highscores import HighScoreManager

__author__ = "Rachel Quilligan"
__email__ = "rachel.quilligan@uqconnect.edu.au"

__version__ = "1.0.2"

from base import BaseLoloApp

# Define your classes here

class LoloApp(BaseLoloApp):
    """Class for a Lolo game."""

    def __init__(self, master, game=None, grid_view=None):
        """Constructor

        Parameters:
            master (tk.Tk|tk.Frame): The parent widget.
            game (model.AbstractGame): The game to play. Defaults to a
                                       game_regular.RegularGame.
            grid_view (view.GridView): The view to use for the game. Optional.

        Raises:
            ValueError: If grid_view is supplied, but game is not.
        """
        self._master = master
        super().__init__(self._master, game=None, grid_view=None)
        
        self._highscores = HighScoreManager()

        self._master.title("LoLo :: {} Game".format(self._game.get_name()))

        self._grid_view.pack_forget()
        logo = LoloLogo(self._master)
        logo.pack(side=tk.TOP, expand=True)

        self._statusbar = StatusBar(self._master)
        self._statusbar.pack(side=tk.TOP, expand=True, padx=10, pady=10)
        self._statusbar.set_game(self._game.get_name())
        
        self._grid_view.pack(side=tk.TOP, padx=10, pady=10)

        self._lightning_count = 1
        self._lightning_on = False
        self._lightningBtn = tk.Button(self._master, text="Lightning ({})"
                                       .format(self._lightning_count),
                                       bg="white",command=self.toggle_lightning)
        self._lightningBtn.pack(side=tk.TOP, expand=True, padx=10, pady=10)

        menubar = tk.Menu(self._master)
        self._master.config(menu=menubar)

        filemenu = tk.Menu(menubar)
        menubar.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="New Game", command=self.reset)
        filemenu.add_command(label="Exit", command=self.exit)

        self._master.bind_all("<Control-n>", self.shortcut_reset)
        self._master.bind("<Control-l>", self.shortcut_toggle_lightning)
        
    def set_name(self, name):
        """Gets the player's name from input entry on loading screen."""
        self._player_name = name
        
    def score(self, points):
        """Handles increase in score."""
        self._statusbar.set_score(self._game.get_score())
        self.add_lightning()

    def toggle_lightning(self):
        """Toggles lightning ability (which removes a tile on activate) on and
        off.
        """
        if self._lightning_on:
            self._lightning_on = False
            self._lightningBtn.config(text="Lightning ({})".format
                                      (self._lightning_count))
        else:
            self._lightning_on = True
            self._lightningBtn.config(text="LIGHTNING ACTIVE ({})"
                                      .format(self._lightning_count))

    def shortcut_toggle_lightning(self, event):
        """Also toggles lightning ability, via a keyboard shortcut."""
        self.toggle_lightning()

    def check_lightning(self):
        """Checks if there are lightning available to use."""
        if self._lightning_count == 0:
            self._lightningBtn.config(text="Lightning ({})"
                                      .format(self._lightning_count))
            self._lightning_on = False
            self._lightningBtn.config(state="disabled")
        elif self._lightning_count > 0:
            self._lightningBtn.config(state="normal")
            if self._lightning_on:
                self._lightningBtn.config(text="LIGHTNING ACTIVE ({})"
                                          .format(self._lightning_count))
            else:
                self._lightningBtn.config(text="Lightning ({})"
                                      .format(self._lightning_count))
            
    def add_lightning(self):
        """Adds lightning to user's count."""
        if self._game.get_score() % 10 == 0:
            self._lightning_count += 1
            self.check_lightning()

    def reset(self):
        """Starts a new game of the same game type."""
        self._lightning_count = 0
        self._lightning_on = False
        self._game.reset()
        self._grid_view.draw(self._game.grid, self._game.find_connections())
        
    def shortcut_reset(self, event):
        """Also starts a new game, using a keyboard shortcut."""
        self.reset()
        
    def activate(self, position):
        """Attempts to activate the tile at the given position.

        Parameters:
            position (tuple<int, int>): Row-column position of the tile.

        Raises:
            IndexError: If position cannot be activated.
        """
        # Magic. Do not touch.
        if position is None:
            return

        if self._game.is_resolving():
            return

        if position in self._game.grid:

            if self._lightning_on:
                self.remove(position)
                self._lightning_count -= 1
                self.check_lightning()

            else:
                if not self._game.can_activate(position):
                    messagebox.showerror(title="Oops!",
                                         message=("Cannot activate position {}"
                                                  .format(position)))
                def finish_move():
                    self._grid_view.draw(self._game.grid,
                                         self._game.find_connections())

                def draw_grid():
                    self._grid_view.draw(self._game.grid)

                animation = self.create_animation(self._game.activate(position),
                                                  func=draw_grid,
                                                  callback=finish_move)
                animation()
    
    def game_over(self):
        """Handles game ending"""
        if self._lightning_count == 0:
            if self._game.game_over():
                messagebox.showinfo(title="Game over!", message=
                                    "There are no moves left. You scored: {}"
                                    .format(self._game.get_score()))
                self._highscores.record(self._game.get_score(),
                                        self._game, self._set_name())

    def exit(self):
        """Exits the app"""
        self._master.destroy()

class StatusBar(tk.Frame):
    """A widget containg the score and game mode displays"""

    def __init__(self, parent):
        """Widget that contails displays.
        Constructor: StatusBar(tk.Widget)
        Parameters:
            parent (tk.Tk|tk.Toplevel): The parent widget.
        """
        super().__init__(parent)

        self._game_mode_name = tk.Label(self, text="Game", width=40)
        self._game_mode_name.pack(side=tk.LEFT)

        self._score = tk.Label(self, text="Score: ", width=40)
        self._score.pack(side=tk.RIGHT)

    def set_game(self, game_mode):
        """Change the game mode name label to show name of game."""
        self._game_mode_name.config(text="{0} Game".format(game_mode))

    def set_score(self, score):
        """Change the score label to show current score."""
        self._score.config(text="Score: {}".format(score))

class LoloLogo(tk.Canvas):
    """A customised Canvas that displays the Lolo logo"""
    
    def __init__(self, parent):
        """Create and initialise a screen.
        Constructor: Screen(tk.Widget)

        Parameters:
            parent (tk.Frame|tk.Tk): The parent widget.

        """
        super().__init__(parent, bg="white", width=400, height=150)

        #Draw the first "L"
        super().create_rectangle(50, 50, 80, 150, fill="purple", width=0)
        super().create_rectangle(80, 120, 120, 150, fill="purple", width=0)

        #Draw the first "o"
        centre1 = (170, 115)
        radius1 = 35
        super().create_oval(centre1[0]-radius1, centre1[1]-radius1,
                                 centre1[0]+radius1, centre1[1]+radius1,
                                 fill="purple", width=0)
        centre2 = (170, 115)
        radius2 = 15
        super().create_oval(centre2[0]-radius2, centre2[1]-radius2,
                                 centre2[0]+radius2, centre2[1]+radius2,
                                 fill="white", width=0)
        #Draw the second "L"
        super().create_rectangle(220, 50, 250, 150,
                                      fill="purple", width=0)
        super().create_rectangle(250, 120, 290, 150,
                                      fill="purple", width=0)
        #Draw the second "o"
        centre3 = (340, 115)
        radius3 = 35
        super().create_oval(centre3[0]-radius3, centre3[1]-radius3,
                                 centre3[0]+radius3, centre3[1]+radius3,
                                 fill="purple", width=0)
        centre4 = (340, 115)
        radius4 = 15
        super().create_oval(centre4[0]-radius4, centre4[1]-radius4,
                                 centre4[0]+radius4, centre4[1]+radius4,
                                 fill="white", width=0)

class AutoPlayingGame(BaseLoloApp):
    """A version of Lolo that automatically plays the game. Upon finish it
    begins again with a new version."""

    def __init__(self, master, game=None, grid_view=None):
        """Constructor
        Parameters:
            master (tk.Tk |tk.Frame): The parent widget.
            game (mode.AbstractGame): The game to play. Defaults to a
            game_regular.RegularGame.
            grid_view(view.GridView): The view to use for the game. Optional.
        Raises:
            ValueError: If grid_view is supplied, but game is not.
    """
        self._master = master
        self._game = game
        self._grid_view = grid_view
        super().__init__(self._master, game=None, grid_view=None)
        self._move_delay = 500
        self._master.after(self._move_delay, self.move)
        self._grid_view.pack_forget()
        self._grid_view.pack(side=tk.TOP, padx=10, pady=10)

    def bind_events(self):
        """Binds relevant events."""
        self._game.on('resolve', self.resolve)
        self._game.on('game_over', self._game.reset)

    def resolve(self, delay=None):
        """Makes a move after a given delay."""
        if delay is None:
            delay = self._move_delay
        self._master.after(delay, self.move)

    def move(self):
        """Finds a connected tile randomly and activates it."""
        connections = list(self._game.find_groups())

        if connections:
            # pick random valid move
            cells = list()

            for connection in connections:
                for cell in connection:
                    cells.append(cell)

            self.activate(random.choice(cells))
            
class LoadingScreen(tk.Frame):
    """Displays a loading screen with all the associated functionality."""
    def __init__(self, master):
        """Constructor
        Parameters:
            master (tk.Tk|tk.Frame): The parent widget.
            width: The width of the Frame.
            height: The height of the Frame.
        """
        super().__init__(master, bg="white", width=1000, height=800)
        self._master = master
        self._master.title("Lolo")
        #Put in the logo
        logo = LoloLogo(self._master)
        logo.pack(side=tk.TOP, expand=True)
        #Put in the name widget
        name = tk.Frame(self._master)
        name.pack(side=tk.TOP)
        playernameLabel = tk.Label(name, text="Your name: ")
        playernameLabel.pack(side=tk.LEFT)
        self._playernameEntry = tk.Entry(name)
        self._playernameEntry.pack(side=tk.LEFT)
        self._playerName = self._playernameEntry.get()


        #Create button
        BUTTON_WIDTH = 40
        buttons = tk.Frame(self._master)
        buttons.pack(side=tk.LEFT, padx=20, pady=20)
        playgameBtn = tk.Button(buttons, text="Play game", width=BUTTON_WIDTH,
                                command=self.start_game)
        playgameBtn.pack(side=tk.TOP, expand=True, pady=50)
        highscoresBtn = tk.Button(buttons, text="High scores",
                                  width=BUTTON_WIDTH,
                                  command=self.open_highscores)
        highscoresBtn.pack(side=tk.TOP, expand=True, pady=50)
        exitBtn = tk.Button(buttons, text="Exit game",
                            width=BUTTON_WIDTH, pady=50,
                            command=self.exit_game)
        exitBtn.pack(side=tk.TOP, expand=True)
        #Put in the auto playing game
        auto_game_frame = tk.Frame(self._master)
        auto_game_frame.pack(side=tk.RIGHT, padx=10, pady=10)
        auto_game = AutoPlayingGame(auto_game_frame)

    def start_game(self):
        """Begins a new game."""
        root = tk.Toplevel(self)
        app = LoloApp(root)
        app.set_name(self._playerName)
        root.mainloop()

    def exit_game(self):
        """Exits the app."""
        self._master.destroy()

    def open_highscores(self):
        """Opens highscore window"""
        highscore_window = tk.Toplevel(self)
        highscore_window.title("Leaderboard")
        highscores = Leaderboard(highscore_window)

class Leaderboard(tk.Frame):
    """Displays leaderboard including top ten high scorers, best player, and
    static game representation of the best player's high scoring game.
    Parameters:
        master(tk.Tk|tk.Frame): The parent widget.
    """
    def __init__(self, master):
        super().__init__(master)
        self._master = master
        self._highscore = HighScoreManager()
        highest = self._highscore.get_sorted_data()[0]
        best_player = tk.Label(self._master, text=("Best Player: "+
                                                   highest['name'] + " with "+
                                                   str(highest['score'])))
        best_player.pack(side=tk.TOP, expand=True)
        
        grid_list = highest['grid']
        self._game_grid = RegularGame.deserialize(grid_list)
        HighScoreGame(self._master, game=RegularGame(types=3),
                      grid_view=self._game_grid)

        #Create the leaderboard frame
        players_list = tk.Frame(self._master, width=400)
        players_list.pack(side=tk.TOP, padx=30, pady=30)
        players_list_title = tk.Label(players_list, text="Leaderboard")
        players_list_title.pack(side=tk.TOP, expand=True)

        #Create the leaderboard entries
        leader_name = tk.Frame(players_list)
        leader_name.pack(side=tk.LEFT, expand=True, padx=40)

        leader_score = tk.Frame(players_list)
        leader_score.pack(side=tk.RIGHT, padx=40)
        
        top_scorers = self._highscore.get_sorted_data()
        for entry in top_scorers:
            player_name = tk.Label(leader_name, text=(entry['name']))
            player_name.pack(side=tk.TOP, anchor='w')
            player_score = tk.Label(leader_score, text=(str(entry['score'])))
            player_score.pack(side=tk.TOP, anchor='e')

class HighScoreGame(BaseLoloApp):
    """Static representation of the best player's highest scoring game."""

    def __init__(self, master, game=None, grid_view=None):
        """Constructor
        Parameters:
            master (tk.Tk|tk.Frame): The parent widget.
            game (model.AbstractGame): The game to play. Defaults to a
                                       game_regular.RegularGame.
            grid_view (view.GridView): The view to use for the game. Optional.

        Raises:
            ValueError: If grid_view is supplied, but game is not."""
        
        self._master = master
        self._game = game
        self._grid_view = grid_view
        super().__init__(self._master, game=None, grid_view=None)

    def bind_events(self):
        """Binds relevant events."""
        self._game.on('resolve', self.resolve)
        self._game.on('game_over', self._game.reset)

    def resolve(self, delay=None):
        """Makes a move after a given movement delay."""
        if delay is None:
            delay = self._move_delay
        self._master.after(delay, self.move)

    def move(self):
        """Finds a connected tile randomly and activates it."""
        connections = list(self._game.find_groups())

        if connections:
            # pick random valid move
            cells = list()

            for connection in connections:
                for cell in connection:
                    cells.append(cell)

            self.activate(random.choice(cells))

            
def main():
    """Main function that runs the game."""
    root = tk.Tk()
    app = LoadingScreen(root)
    root.mainloop()


if __name__ == "__main__":
    main()
