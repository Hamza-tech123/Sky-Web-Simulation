import sys
import numpy as np
import random
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class SkyWebProSimulation(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SKY-WEB: DECENTRALIZED DEFENSE SYSTEM v3.0")
        self.setFixedSize(1400, 900)
        
        # --- Tactical Settings ---
        self.origin = np.array([31.2001, 29.9187]) # إحداثيات الإسكندرية كمثال
        self.swarm = [{'pos': self.origin + np.random.uniform(-0.02, 0.02, 2), 'active': True} for _ in range(12)]
        self.enemies = [{'pos': self.origin + np.random.uniform(0.06, 0.08, 2), 
                         'vel': np.random.uniform(-0.0015, -0.0025, 2), 'active': True} for _ in range(5)]
        
        self.init_ui()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_simulation)
        self.timer.start(500)

    def init_ui(self):
        main_widget = QWidget()
        layout = QHBoxLayout()
        
        # الرادار (Matplotlib)
        self.fig = Figure(facecolor='#050505')
        self.canvas = FigureCanvas(self.fig)
        self.ax = self.fig.add_subplot(111)
        # إضافة زرار التحكم
        self.pause_btn = QPushButton("Pause / Resume")
        self.pause_btn.clicked.connect(self.toggle_simulation)
        self.pause_btn.setStyleSheet("background: #222; color: #00ff41; font-weight: bold; border: 1px solid #00ff41; padding: 5px;")
        layout.addWidget(self.pause_btn) # هيظهر فوق الـ Log على اليمين
        layout.addWidget(self.canvas, 4)
        
        # لوحة البيانات (Tactical Log)
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setStyleSheet("background: #000; color: #00ff41; font-family: 'Consolas'; border: 1px solid #00ff41;")
        layout.addWidget(self.log, 1)
        
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)
        self.log.append("--- SKY-WEB SYSTEM ONLINE ---")

    def update_simulation(self):
        self.ax.clear()
        self.ax.set_facecolor('#050505')
        self.ax.set_xlim(29.85, 30.05) # حدود الخريطة الافتراضية
        self.ax.set_ylim(31.15, 31.30)
        
        # 1. محاكاة الـ Self-Healing (سقوط عشوائي لدرون صديقة لإثبات المرونة)
        active_drones = [d for d in self.swarm if d['active']]
        if random.random() < 0.003 and len(active_drones) > 4:
            lost_idx = random.choice([i for i, d in enumerate(self.swarm) if d['active']])
            self.swarm[lost_idx]['active'] = False
            self.log.append("<font color='orange'>[!] ALERT: UNIT LOST. RE-CALIBRATING SWARM GRID...</font>")

        # 2. تحديث حركة الأعداء
        for enemy in self.enemies:
            if enemy['active']:
                enemy['pos'] += enemy['vel']
                self.ax.scatter(enemy['pos'][1], enemy['pos'][0], color='red', marker='X', s=120, label='Threat')

        # 3. توزيع المهام والاشتباك (Swarm Intelligence)
        for drone in self.swarm:
            if not drone['active']: continue
            
            # إيجاد أقرب عدو نشط
            closest_enemy = None
            min_dist = float('inf')
            for enemy in self.enemies:
                if enemy['active']:
                    dist = np.linalg.norm(enemy['pos'] - drone['pos'])
                    if dist < min_dist:
                        min_dist = dist
                        closest_enemy = enemy
            
            if closest_enemy:
                # التحرك الذكي (Intercept)
                move_dir = closest_enemy['pos'] - drone['pos']
                drone['pos'] += (move_dir / min_dist) * 0.0028
                
                # رسم "خيوط الشبكة" (The Sky-Web)
                self.ax.plot([drone['pos'][1], closest_enemy['pos'][1]], 
                             [drone['pos'][0], closest_enemy['pos'][0]], 
                             color='#00ff41', alpha=0.15, lw=1)
                
                # التحييد (HPM Strike)
                if min_dist < 0.004:
                    closest_enemy['active'] = False
                    self.log.append("<font color='cyan'>[+] TARGET NEUTRALIZED BY ENERGY GRID.</font>")

            # رسم الدرون الصديقة
            self.ax.scatter(drone['pos'][1], drone['pos'][0], color='#00aaff', marker='^', s=80)

        self.canvas.draw()
    def toggle_simulation(self):
        if self.timer.isActive():
            self.timer.stop()
            self.log.append("<font color='yellow'>[||] SIMULATION PAUSED - READY FOR SCREENSHOT</font>")
        else:
            self.timer.start(250) # سرعة بطيئة (ربع ثانية) عشان تلحق تشرح
            self.log.append("<font color='green'>[>] SIMULATION RESUMED</font>")
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SkyWebProSimulation()
    window.show()
    sys.exit(app.exec_())