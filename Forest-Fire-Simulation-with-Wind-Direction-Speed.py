import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QSlider, QVBoxLayout, QWidget, QLabel, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.colors import ListedColormap

class ForestFireSimulation(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Forest Fire Simulation")
        self.setGeometry(200, 200, 1200, 800)  # Adjust the window size as needed

        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)
        mainLayout = QHBoxLayout()
        centralWidget.setLayout(mainLayout)

        self.figure = Figure(figsize=(10, 8), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        mainLayout.addWidget(self.canvas)
        self.ax = self.figure.add_subplot(111)
        self.cmap = ListedColormap(['white', 'green', 'red'])

        self.grid_size = 200
        self.p_growth = 0.01
        self.wind_direction = 90  # East by default
        self.wind_strength = 5
        self.humidity = 30

        self.forest_grid = np.random.choice([0, 1], size=(self.grid_size, self.grid_size), p=[0.7, 0.3])

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_simulation)
        self.timer.start(200)

        controlLayout = QVBoxLayout()
        mainLayout.addLayout(controlLayout)

        # Growth Probability Slider
        self.slider_growth = self.create_slider("Growth Probability", 1, 100, self.p_growth * 100, self.change_growth)
        controlLayout.addWidget(QLabel('Growth Probability'))
        controlLayout.addWidget(self.slider_growth)

        # Wind Direction Slider
        self.slider_wind_direction = self.create_slider("Wind Direction", 0, 360, self.wind_direction, self.change_wind_direction)
        controlLayout.addWidget(QLabel('Wind Direction'))
        controlLayout.addWidget(self.slider_wind_direction)

        # Wind Strength Slider
        self.slider_wind_strength = self.create_slider("Wind Strength", 0, 20, self.wind_strength, self.change_wind_strength)
        controlLayout.addWidget(QLabel('Wind Strength'))
        controlLayout.addWidget(self.slider_wind_strength)

        # Humidity Slider
        self.slider_humidity = self.create_slider("Humidity", 0, 100, self.humidity, self.change_humidity)
        controlLayout.addWidget(QLabel('Humidity'))
        controlLayout.addWidget(self.slider_humidity)

        # Connect the canvas click event
        self.canvas.mpl_connect('button_press_event', self.on_click)

    def create_slider(self, label, min_value, max_value, initial_value, callback):
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(min_value)
        slider.setMaximum(max_value)
        slider.setValue(int(initial_value))
        slider.valueChanged[int].connect(callback)
        return slider

    def change_growth(self, value):
        self.p_growth = value / 100.0

    def change_wind_direction(self, value):
        self.wind_direction = value

    def change_wind_strength(self, value):
        self.wind_strength = value

    def change_humidity(self, value):
        self.humidity = value

    def update_simulation(self):
        wind_effect = self.wind_strength / 10.0  # Adjust this factor as needed
        humidity_effect = 1 - self.humidity / 100

        wind_dx = -int(np.round(np.sin(np.radians(self.wind_direction))))
        wind_dy = -int(np.round(np.cos(np.radians(self.wind_direction))))  # Invert direction for y-axis

        new_grid = self.forest_grid.copy()
        
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if self.forest_grid[i, j] == 0:
                    new_grid[i, j] = 1 if np.random.random() < self.p_growth else 0
                elif self.forest_grid[i, j] == 1:
                    fire_nearby = False
                    for di in [-1, 0, 1]:
                        for dj in [-1, 0, 1]:
                            if di == 0 and dj == 0:
                                continue
                            ni, nj = (i + di) % self.grid_size, (j + dj) % self.grid_size
                            if self.forest_grid[ni, nj] == 2:
                                # Adjust fire spread probability based on wind direction and strength
                                spread_chance = 0.3  # Base spread chance without wind
                                if di == wind_dx and dj == wind_dy:
                                    spread_chance += wind_effect  # Increase spread chance in wind direction
                                elif di == -wind_dx and dj == -wind_dy:
                                    spread_chance -= wind_effect  # Decrease spread chance against wind direction
                                spread_chance *= humidity_effect  # Adjust spread chance by humidity
                                spread_chance = max(0, min(spread_chance, 1))  # Ensure probability is between 0 and 1

                                if np.random.random() < spread_chance:
                                    fire_nearby = True
                                    break
                        if fire_nearby:
                            new_grid[i, j] = 2
                            break
                elif self.forest_grid[i, j] == 2:
                    new_grid[i, j] = 0  # Burnt trees turn to empty space

        self.forest_grid = new_grid
        self.ax.clear()
        self.ax.imshow(self.forest_grid, cmap=self.cmap, interpolation='nearest')
        self.ax.axis('off')
        self.canvas.draw()

        # Draw an arrow for wind direction
        arrow_start = (0.1 * self.grid_size, 0.9 * self.grid_size)  # Starting point of the arrow
        dx = np.cos(np.radians(self.wind_direction)) * 20  # Calculate change in x based on direction
        dy = np.sin(np.radians(self.wind_direction)) * 20  # Calculate change in y based on direction
        self.ax.arrow(arrow_start[0], arrow_start[1], dx, dy, head_width=5, head_length=10, fc='blue', ec='blue')

        # Display wind strength
        wind_strength_text = f"Wind Strength: {self.wind_strength} m/s"
        self.ax.text(0.1 * self.grid_size, 0.85 * self.grid_size, wind_strength_text, color='blue')

        self.canvas.draw()

    def on_click(self, event):
        if event.xdata is not None and event.ydata is not None:
            ix, iy = int(event.xdata), int(event.ydata)
            if 0 <= ix < self.grid_size and 0 <= iy < self.grid_size:
                self.forest_grid[iy, ix] = 2
                self.update_simulation()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ForestFireSimulation()
    ex.show()
    sys.exit(app.exec_())