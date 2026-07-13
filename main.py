"""Entry point for the Physics Visualizer application."""

from menu import MainMenu


def main():
	"""Create the main menu window and start the Tkinter event loop."""
	app = MainMenu()
	app.run()



if __name__ == "__main__":
	main()
