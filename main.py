from menu import MainMenu
import kinematics_vis


def main():
	app = MainMenu()
	# Open the kinematics visualizer automatically on startup
	kinematics_vis.open_kinematics_window(app.root)
	app.run()


if __name__ == "__main__":
	main()
