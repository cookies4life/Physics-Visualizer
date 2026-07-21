# Physics Visualizer

Physics Visualizer is a desktop learning app with interactive demonstrations for common physics topics. It is built with Python and Tkinter and includes an optional AI whiteboard tutor that can review drawings and answer questions.

## Topics

- Kinematics
- Newton's laws
- Work, energy, and power
- Momentum and collisions
- Rotational motion
- Fluids and statics
- Waves and diffraction
- Quantum mechanics
- AI Whiteboard Tutor

## Requirements

- Python 3.10 or newer
- Tkinter (normally included with Python on Windows and macOS)
- A Gemini API key only if you want to use the Whiteboard Tutor

On some Linux distributions, Tkinter must be installed separately (for example, `python3-tk` on Ubuntu/Debian).

## Setup

Clone the repository and enter its directory:

```bash
git clone <repository-url>
cd Physics-Visualizer
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows, activate it with:

```powershell
.venv\Scripts\Activate.ps1
```

Install the dependencies:

```bash
python -m pip install -r requirements.txt
```

## Run the app

```bash
python main.py
```

Choose a topic from the main menu, then use the controls in its window to change parameters and explore the visualization.

## Whiteboard Tutor

The Whiteboard Tutor is the only feature that requires an internet connection and a Gemini API key. The rest of the app works locally without one.

You can provide the key before launching the app:

```bash
export GEMINI_API_KEY="your-api-key"
python main.py
```

On Windows PowerShell:

```powershell
$env:GEMINI_API_KEY="your-api-key"
python main.py
```

If the environment variable is not set, the app prompts for a key when you first open the tutor and saves it locally in `~/.physics_visualizer/gemini_api_key.txt`.

## Build a standalone app

A PyInstaller specification is included. From an activated environment with the dependencies installed, run:

```bash
pyinstaller "Physics Visualizer.spec"
```

The packaged application is written to the `dist/` directory. The current specification includes macOS app-bundle settings and icons; adjust the icon or bundle configuration when packaging for another platform.

## Project structure

```text
main.py              Application entry point
menu.py              Main topic menu
*_vis.py             Topic-specific visualizations
viz_common.py        Shared drawing and UI helpers
whiteboard_tutor.py  Drawing canvas and Gemini tutor integration
build_assets/        Application icons
```
