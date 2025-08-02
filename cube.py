import tkinter as tk
from tkinter import messagebox, simpledialog
import cv2
from PIL import Image, ImageTk
import numpy as np

def detect_colors_in_grid(frame, grid_start_x, grid_start_y, size, n):
    box_size = size // n
    detected_colors = []
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # HSV ranges for Rubik's cube colors (tune for your environment)
    color_ranges = {
        'white': ([0, 0, 180], [180, 55, 255]),
        'yellow': ([20, 100, 100], [30, 255, 255]),
        'red1': ([0, 110, 110], [10, 255, 255]),       # Lower red
        'red2': ([160, 110, 110], [180, 255, 255]),    # Upper red
        'orange': ([10, 110, 100], [20, 255, 255]),
        'green': ([40, 50, 50], [90, 255, 255]),
        'blue': ([100, 100, 50], [130, 255, 255])
    }

    for row in range(n):
        for col in range(n):
            x = grid_start_x + col * box_size
            y = grid_start_y + row * box_size
            sample_area = hsv[y+box_size//4:y+3*box_size//4, x+box_size//4:x+3*box_size//4]
            if sample_area.size == 0:
                detected_colors.append(None)
                continue
            mean_color = cv2.mean(sample_area)[:3]
            hsv_val = np.array(mean_color, dtype=np.uint8)
            detected = None
            for key, (lower, upper) in color_ranges.items():
                lower = np.array(lower, dtype=np.uint8)
                upper = np.array(upper, dtype=np.uint8)
                if key in ('red1', 'red2'):
                    # red spans HSV boundary
                    if all(lower[i] <= hsv_val[i] <= upper[i] for i in range(3)):
                        detected = 'red'
                        break
                else:
                    if all(lower[i] <= hsv_val[i] <= upper[i] for i in range(3)):
                        detected = key
                        break
            detected_colors.append(detected)
    return detected_colors

class CubeSolverApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Rubik's Cube Solver")

        self.cube_size = None
        self.captured_faces = []
        self.face_colors = ["U", "R", "F", "D", "L", "B"]
        self.current_face = 0
        self.camera_on = False
        self.steps = []

        # Buttons
        self.btn_scramble = tk.Button(master, text="Scramble", command=self.scramble)
        self.btn_reset = tk.Button(master, text="Reset", command=self.reset)
        self.btn_steps = tk.Button(master, text="Steps", command=self.show_steps)
        self.btn_quit = tk.Button(master, text="Quit", command=master.quit)
        self.btn_capture = tk.Button(master, text="Start Camera & Capture Faces", command=self.start_camera)

        self.btn_scramble.pack(pady=6)
        self.btn_reset.pack(pady=6)
        self.btn_steps.pack(pady=6)
        self.btn_capture.pack(pady=6)
        self.btn_quit.pack(pady=6)

        self.label = tk.Label(master, text="Welcome! Choose Cube Size.")
        self.label.pack(pady=14)

        # Camera display
        self.frame_label = tk.Label(master)
        self.frame_label.pack()

        # Ask for cube size at start
        self.ask_cube_size()

    def ask_cube_size(self):
        self.cube_size = simpledialog.askinteger("Cube Size", "Enter cube size (2, 3, or 4):", minvalue=2, maxvalue=4)
        if self.cube_size not in [2, 3, 4]:
            messagebox.showerror("Error", "Only 2x2, 3x3, and 4x4 supported")
            self.master.destroy()

    def scramble(self):
        messagebox.showinfo("Scramble", "Please manually scramble your cube and press 'Start Camera'.")

    def reset(self):
        self.current_face = 0
        self.captured_faces = []
        self.camera_on = False
        self.label.config(text="Faces reset. Press 'Start Camera' to capture again.")
        self.steps = []

    def show_steps(self):
        if not self.steps:
            messagebox.showinfo("Steps", "No solution calculated yet. Capture all 6 sides first!")
        else:
            steps_str = "\n".join(self.steps)
            messagebox.showinfo("Solution Steps", steps_str)

    def start_camera(self):
        self.cap = cv2.VideoCapture(0)
        self.camera_on = True
        self.label.config(text=f"Show the {self.face_colors[self.current_face]} face to the camera. Hold it until grid boxes are filled.")
        self.update_frame()
        self.master.unbind('<space>')  # Don't use spacebar; auto-capture

    def update_frame(self):
        if self.camera_on:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.flip(frame, 1)
                h, w, _ = frame.shape
                n = self.cube_size
                margin = 40
                size = min(h, w) - 2 * margin
                start_x = (w - size) // 2
                start_y = (h - size) // 2

                # Draw grid
                cv2.rectangle(frame, (start_x, start_y), (start_x + size, start_y + size), (0, 255, 0), 2)
                for i in range(1, n):
                    x = start_x + int(size * i / n)
                    y = start_y + int(size * i / n)
                    cv2.line(frame, (x, start_y), (x, start_y + size), (0, 255, 0), 1)
                    cv2.line(frame, (start_x, y), (start_x + size, y), (0, 255, 0), 1)

                # Color detection & auto-capture
                try:
                    detected = detect_colors_in_grid(frame, start_x, start_y, size, n)
                except Exception:
                    detected = [None for _ in range(n * n)]
                filled = all(c is not None for c in detected)

                # Show filled/total status
                cv2.putText(frame,
                            f'Boxes filled: {sum(c is not None for c in detected)}/{n*n}',
                            (start_x, start_y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,0,0), 2)

                if filled:
                    self.captured_faces.append(frame.copy())
                    self.current_face += 1
                    if self.current_face < 6:
                        self.label.config(text=f"Show the {self.face_colors[self.current_face]} face. Rotate and hold for auto-capture.")
                    else:
                        self.label.config(text="Processing cube faces...")
                        self.cap.release()
                        self.camera_on = False
                        self.process_cube()
                    # Wait before next capture so user can rotate the cube
                    self.master.after(1200, self.update_frame)
                    return

                # Show in Tkinter
                img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(img)
                imgtk = ImageTk.PhotoImage(image=img)
                self.frame_label.imgtk = imgtk
                self.frame_label.configure(image=imgtk)
            self.master.after(30, self.update_frame)

    def process_cube(self):
        # Demo: placeholder moves (replace with your solver)
        if self.cube_size == 2:
            self.steps = [
                "R U R' U R U2 R'",
                "(Sample 2x2 moves)"
            ]
            self.label.config(text="Sample 2x2 solution ready! Press 'Steps'.")
        elif self.cube_size == 3:
            self.steps = [
                "F R U R' U' F'",
                "R U R' U R U2 R'",
                "(Sample 3x3 moves)"
            ]
            self.label.config(text="Sample 3x3 solution ready! Press 'Steps'.")
        elif self.cube_size == 4:
            self.steps = [
                "Reduction: solve centers",
                "Pair edges",
                "Solve like 3x3",
                "Handle 4x4 parity",
                "(Sample 4x4 steps)"
            ]
            self.label.config(text="Sample 4x4 steps ready! Press 'Steps'.")
        else:
            self.steps = ["Unsupported cube size."]
            self.label.config(text="Error.")

if __name__ == '__main__':
    root = tk.Tk()
    app = CubeSolverApp(root)
    root.mainloop()
