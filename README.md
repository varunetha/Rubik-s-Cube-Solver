# Rubik-s-Cube-Solver
A simple, interactive Python app that uses computer vision to recognize Rubik’s Cube faces and provides step-by-step solution moves. Supports 2x2, 3x3, and 4x4 cubes. 

# Features
User-friendly GUI: Built with Tkinter for quick setup and intuitive operation.

Dynamic camera grid overlay: Live webcam feed with grid lines adapts to the chosen cube size, making face alignment easy.

Automatic face capture: Each face is auto-captured when all grid boxes are filled with detected sticker colors, requiring no key presses from the user.

Supports multiple cube sizes: Choose between 2x2, 3x3, and 4x4 cubes.

Step-by-step solutions: Processes all faces and displays a sequence of moves for solving the cube.

Extensible design: Ready for integration with advanced solving algorithms and custom color recognition improvements.

# How it Works
User opens the app and selects the cube size.

The camera activates and shows a guiding grid for accurate cube face alignment.

Each cube face is displayed in turn; when all grid squares are filled with detected colors, it is auto-captured.

After all six faces are collected, the app computes and shows the solution steps.

The user follows the steps to solve the cube.

# Requirements
Python 3

Tkinter

OpenCV (opencv-python)

Pillow (PIL)

NumPy
