import sys
import numpy as np
import random
import matplotlib.pyplot as plt 
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class SkyWebUltimateSimulation(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SKY-WEB | STRATEGIC SWARM COMMAND v6.2")
        self.setFixedSize(1500, 950)

        # --- High-Fidelity Parameters ---
        self.P_peak = 1800          
        self.E_th = 1500           
        self.dt = 0.1               
        self.frame_counter = 0      
        self.origin = np.array([31.2001, 29.9187]) 

        # Defense Swarm (25 Units)
        self.swarm = []
        for i in range(25):
            self.swarm.append({
                'id': i,
                'pos': self.origin + np.random.uniform(-0.02, 0.02, 2), 
                'active': True,
                'angle_offset': (2 * np.pi / 25) * i
            })

        # Enemy Raid (15 Units)
        self.enemies = [
            {
                'id': f"BOGEY-{i:02d}",
                'pos': self.origin + np.random.uniform(0.08, 0.12, 2) * (1 if random.random() > 0.5 else -1), 
                'vel': np.random.uniform(-0.0003, -0.0005, 2), 
                'active': True,
                'energy': 0.0
            } for i in range(15)
        ]

        self.init_ui()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_simulation)
        self.timer.start(400) # بطيء جداً للتحليل العسكري

    def init_ui(self):
        main_widget = QWidget(); main_widget.setStyleSheet("background-color: #010101;")
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        
        # Radar View
        self.fig = Figure(facecolor='#010101', tight_layout=True)
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas, 3)
        self.ax = self.fig.add_subplot(111, facecolor='#010101')
        
        # Side Control Panel
        right_panel = QVBoxLayout()
        title = QLabel("TACTICAL HUD")
        title.setStyleSheet("color: #00ff41; font-weight: bold; font-size: 16pt; border-bottom: 2px solid #00ff41; padding-bottom: 10px;")
        right_panel.addWidget(title)

        # زر الـ Pause (الخيار اللي كان ناقص)
        self.pause_btn = QPushButton("ENGAGE / STANDBY")
        self.pause_btn.clicked.connect(self.toggle_simulation)
        self.pause_btn.setStyleSheet("""
            QPushButton { 
                background-color: #001a00; 
                color: #00ff41; 
                border: 2px solid #00ff41; 
                padding: 20px; 
                font-weight: bold; 
                font-family: 'Consolas'; 
                font-size: 12pt;
            }
            QPushButton:hover { background-color: #00ff41; color: #000; }
        """)
        right_panel.addWidget(self.pause_btn)

        # Log Window
        self.log = QTextEdit(); self.log.setReadOnly(True)
        self.log.setStyleSheet("background: #000; color: #00ff41; font-family: 'Consolas'; font-size: 8pt; border: 1px solid #111;")
        right_panel.addWidget(self.log)
        
        layout.addLayout(right_panel, 1)

    def toggle_simulation(self):
        # وظيفة التحكم في الإيقاف والتشغيل
        if self.timer.isActive():
            self.timer.stop()
            self.log.append("<font color='yellow'>> [!] SYSTEM PAUSED: DATA FREEZE ENABLED</font>")
        else:
            self.timer.start(400)
            self.log.append("<font color='#00ff41'>> [!] SYSTEM RESUMED: CONTINUING INTERCEPTION</font>")

    def is_safe_to_fire(self, shooter, target_pos):
        # منع النيران الصديقة
        for ally in self.swarm:
            if ally['id'] == shooter['id'] or not ally['active']: continue
            vec_to_target = target_pos - shooter['pos']
            vec_to_ally = ally['pos'] - shooter['pos']
            if np.linalg.norm(vec_to_ally) > np.linalg.norm(vec_to_target): continue
            
            dot = np.dot(vec_to_target/np.linalg.norm(vec_to_target), vec_to_ally/np.linalg.norm(vec_to_ally))
            if np.arccos(np.clip(dot, -1, 1)) < np.radians(8): return False
        return True

    def update_simulation(self):
        self.ax.clear()
        self.frame_counter += 1
        self.ax.set_xlim(self.origin[1]-0.15, self.origin[1]+0.15)
        self.ax.set_ylim(self.origin[0]-0.15, self.origin[0]+0.15)
        self.ax.grid(color='#0a0a0a', linestyle='-', linewidth=0.5)
        self.ax.set_xticks([]); self.ax.set_yticks([])

        active_enemies = [e for e in self.enemies if e['active']]
        is_pulsing = self.frame_counter % 2 == 0

        # 1. Neutralization Logic (Physically realistic)
        for enemy in self.enemies:
            if not enemy['active']: continue
            intensity_sum = 0
            for drone in self.swarm:
                if not drone['active']: continue
                dist = np.linalg.norm(drone['pos'] - enemy['pos'])
                if dist < 0.05 and is_pulsing:
                    if self.is_safe_to_fire(drone, enemy['pos']):
                        intensity = self.P_peak / (4 * np.pi * ((dist + 0.01)**2))
                        intensity_sum += intensity
                        self.ax.plot([drone['pos'][1], enemy['pos'][1]], [drone['pos'][0], enemy['pos'][0]], 
                                     color='#00ff41', alpha=0.4, linewidth=0.8)

            enemy['energy'] += (intensity_sum * self.dt) / 15
            enemy['pos'] += enemy['vel']
            prog = min(enemy['energy']/self.E_th, 1.0)
            self.ax.scatter(enemy['pos'][1], enemy['pos'][0], color='red' if prog < 0.9 else 'orange', s=100, marker='X')
            
            if enemy['energy'] >= self.E_th:
                enemy['active'] = False
                self.log.append(f"<font color='red'>[KILLED] {enemy['id']} neutralized.</font>")

        # 2. Encirclement Movement Logic
        for drone in self.swarm:
            if not drone['active']: continue
            if active_enemies:
                target = min(active_enemies, key=lambda e: np.linalg.norm(drone['pos'] - e['pos']))
                radius = 0.025
                orbit_pos = target['pos'] + np.array([
                    radius * np.cos(drone['angle_offset'] + self.frame_counter * 0.02),
                    radius * np.sin(drone['angle_offset'] + self.frame_counter * 0.02)
                ])
                move_dir = orbit_pos - drone['pos']
                dist = np.linalg.norm(move_dir)
                if dist > 0.001:
                    drone['pos'] += (move_dir / dist) * 0.0015
            self.ax.scatter(drone['pos'][1], drone['pos'][0], color='#00aaff', marker='^', s=30)

        self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SkyWebUltimateSimulation()
    window.show()
    sys.exit(app.exec_())