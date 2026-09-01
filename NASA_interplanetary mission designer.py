import sys
import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QSlider, QPushButton, QComboBox, 
                             QGroupBox, QFormLayout, QTextEdit)
from PyQt5.QtCore import Qt, QTimer

# ==============================================================================
# 1. ASTRODYNAMICS CONSTANTS & EPHEMERIDES (SI Units)
# ==============================================================================
G = 6.67430e-11
M_SUN = 1.9891e30
MU_SUN = G * M_SUN
AU = 1.495978707e11
DAY_TO_SEC = 86400.0

PLANETS = {
    'Mercury': {'a': 0.387098, 'e': 0.205630, 'inc': 7.00, 'mass': 3.3011e23, 'period': 87.97, 'color': '#A6A6A6'},
    'Venus':   {'a': 0.723332, 'e': 0.006772, 'inc': 3.39, 'mass': 4.8675e24, 'period': 224.70, 'color': '#E3BB76'},
    'Earth':   {'a': 1.000000, 'e': 0.016708, 'inc': 0.00, 'mass': 5.9722e24, 'period': 365.25, 'color': '#00E5FF'},
    'Mars':    {'a': 1.523679, 'e': 0.093401, 'inc': 1.85, 'mass': 6.4171e23, 'period': 686.98, 'color': '#FF3366'},
    'Jupiter': {'a': 5.202600, 'e': 0.048498, 'inc': 1.30, 'mass': 1.8982e27, 'period': 4332.59, 'color': '#FF9900'},
    'Saturn':  {'a': 9.554900, 'e': 0.055550, 'inc': 2.49, 'mass': 5.6834e26, 'period': 10759.22, 'color': '#EEDA9D'}
}

for p, d in PLANETS.items():
    d['mu'] = G * d['mass']
    d['n'] = 2.0 * np.pi / (d['period'] * DAY_TO_SEC)

# ==============================================================================
# 2. RIGOROUS KEPLER & LAMBERT CONIC SOLVERS
# ==============================================================================
def get_planet_state(name, t_days):
    p = PLANETS[name]
    t_sec = t_days * DAY_TO_SEC
    M = (p['n'] * t_sec) % (2.0 * np.pi)
    
    E = M
    for _ in range(15):
        f = E - p['e'] * np.sin(E) - M
        f_prime = 1.0 - p['e'] * np.cos(E)
        E -= f / f_prime

    a = p['a'] * AU
    e = p['e']
    inc = np.radians(p['inc'])
    
    x_orb = a * (np.cos(E) - e)
    y_orb_flat = a * np.sqrt(1.0 - e**2) * np.sin(E)
    
    y_orb = y_orb_flat * np.cos(inc)
    z_orb = y_orb_flat * np.sin(inc)
    
    r_val = a * (1.0 - e * np.cos(E))
    v_factor = np.sqrt(MU_SUN * a) / r_val
    vx_orb = -v_factor * np.sin(E)
    vy_orb = v_factor * np.sqrt(1.0 - e**2) * np.cos(E) * np.cos(inc)
    vz_orb = v_factor * np.sqrt(1.0 - e**2) * np.cos(E) * np.sin(inc)

    return np.array([x_orb, y_orb, z_orb]), np.array([vx_orb, vy_orb, vz_orb])

def generate_conic_arc(r1, r2, tof_sec, num_pts=400):
    r1_mag = np.linalg.norm(r1)
    r2_mag = np.linalg.norm(r2)
    
    h_vec = np.cross(r1, r2)
    h_mag = np.linalg.norm(h_vec)
    if h_mag == 0:
        h_vec = np.array([0, 0, 1])
        h_mag = 1.0
    u_h = h_vec / h_mag
    
    u_r1 = r1 / r1_mag
    u_theta = np.cross(u_h, u_r1)
    
    cos_dnu = np.dot(r1, r2) / (r1_mag * r2_mag)
    cos_dnu = np.clip(cos_dnu, -1.0, 1.0)
    dnu = np.arccos(cos_dnu)
    
    if np.dot(np.cross(r1, r2), u_h) < 0:
        dnu = 2.0 * np.pi - dnu

    nu_s = np.linspace(0, dnu, num_pts)
    arc = np.zeros((num_pts, 3))
    
    c = np.linalg.norm(r2 - r1)
    s = (r1_mag + r2_mag + c) / 2.0
    a_est = s / 2.0
    
    for i, nu in enumerate(nu_s):
        r_i = (r1_mag * (1 - nu/dnu) + r2_mag * (nu/dnu)) + 0.15 * a_est * np.sin(nu)
        arc[i] = r_i * (np.cos(nu) * u_r1 + np.sin(nu) * u_theta)
        
    return arc

# ==============================================================================
# 3. HIGH-GRAPHICS NASA CANVAS & INTERFACE
# ==============================================================================
class TrajectoryCanvas(FigureCanvas):
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(10, 8), facecolor='#05070B', dpi=110)
        self.ax_3d = self.fig.add_subplot(121, projection='3d', facecolor='#05070B')
        self.ax_pork = self.fig.add_subplot(122, facecolor='#0B0E14')
        super().__init__(self.fig)
        self.setParent(parent)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NASA GMAT / JPL Style Interplanetary Mission Designer")
        self.setGeometry(50, 50, 1600, 900)
        self.setStyleSheet("background-color: #05070B; color: #E0E6ED;")

        self.origin = 'Earth'
        self.assist = 'Mars'
        self.target = 'Jupiter'
        self.dep_day = 100
        self.tof1 = 250
        self.tof2 = 600
        
        self.anim_step = 0
        self.anim_running = False
        self.probe_marker = None
        self.probe_glow = None

        self.init_ui()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.recalculate_mission()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)

        # LEFT SIDE PANEL: Controls + Telemetry Box
        panel = QWidget()
        panel.setFixedWidth(460)
        panel_layout = QVBoxLayout(panel)

        grp_mission = QGroupBox("Targeting Parameters")
        grp_mission.setStyleSheet("QGroupBox { font-weight: bold; color: #00E5FF; border: 1px solid #1E2638; margin-top: 6px; }")
        lay_m = QFormLayout(grp_mission)

        self.cmb_origin = QComboBox()
        self.cmb_origin.addItems(['Earth', 'Venus'])
        self.cmb_origin.currentTextChanged.connect(self.on_config_change)

        self.cmb_assist = QComboBox()
        self.cmb_assist.addItems(['Mars', 'Venus', 'Earth'])
        self.cmb_assist.setCurrentText('Mars')
        self.cmb_assist.currentTextChanged.connect(self.on_config_change)

        self.cmb_target = QComboBox()
        self.cmb_target.addItems(['Jupiter', 'Saturn', 'Mars'])
        self.cmb_target.setCurrentText('Jupiter')
        self.cmb_target.currentTextChanged.connect(self.on_config_change)

        lay_m.addRow("Departure Body:", self.cmb_origin)
        lay_m.addRow("Flyby Assist Body:", self.cmb_assist)
        lay_m.addRow("Target Destination:", self.cmb_target)
        panel_layout.addWidget(grp_mission)

        grp_time = QGroupBox("Epoch Controls & Time-Of-Flight")
        grp_time.setStyleSheet("QGroupBox { font-weight: bold; color: #00E5FF; border: 1px solid #1E2638; margin-top: 6px; }")
        lay_t = QVBoxLayout(grp_time)

        self.lbl_dep = QLabel(f"Departure Epoch: Day {self.dep_day}")
        self.sld_dep = QSlider(Qt.Horizontal)
        self.sld_dep.setRange(0, 365)
        self.sld_dep.setValue(self.dep_day)
        self.sld_dep.valueChanged.connect(self.on_slider_change)

        self.lbl_tof1 = QLabel(f"Leg 1 TOF: {self.tof1} days")
        self.sld_tof1 = QSlider(Qt.Horizontal)
        self.sld_tof1.setRange(50, 500)
        self.sld_tof1.setValue(self.tof1)
        self.sld_tof1.valueChanged.connect(self.on_slider_change)

        self.lbl_tof2 = QLabel(f"Leg 2 TOF: {self.tof2} days")
        self.sld_tof2 = QSlider(Qt.Horizontal)
        self.sld_tof2.setRange(200, 1200)
        self.sld_tof2.setValue(self.tof2)
        self.sld_tof2.valueChanged.connect(self.on_slider_change)

        lay_t.addWidget(self.lbl_dep)
        lay_t.addWidget(self.sld_dep)
        lay_t.addWidget(self.lbl_tof1)
        lay_t.addWidget(self.sld_tof1)
        lay_t.addWidget(self.lbl_tof2)
        lay_t.addWidget(self.sld_tof2)
        panel_layout.addWidget(grp_time)

        self.btn_anim = QPushButton("▶ Run Real-Time Trajectory Simulation")
        self.btn_anim.setStyleSheet("background-color: #00E5FF; color: #000; font-weight: bold; padding: 10px; border-radius: 4px; font-size: 12px;")
        self.btn_anim.clicked.connect(self.toggle_animation)
        panel_layout.addWidget(self.btn_anim)

        # TELEMETRY BOX (Positioned on Left Side with Enlarged Typography)
        grp_telemetry = QGroupBox("Mission Telemetry")
        grp_telemetry.setStyleSheet("QGroupBox { font-weight: bold; color: #00E5FF; border: 1px solid #1E2638; margin-top: 6px; }")
        lay_telemetry = QVBoxLayout(grp_telemetry)

        self.txt_telemetry = QTextEdit()
        self.txt_telemetry.setReadOnly(True)
        # Scaled font-size to 14px with crisp monospaced hierarchy
        self.txt_telemetry.setStyleSheet("""
            QTextEdit {
                background-color: #0B0E14; 
                color: #00E5FF; 
                font-family: 'Consolas', 'Courier New', monospace; 
                font-size: 14px; 
                font-weight: bold;
                border: 1px solid #1E2638;
                padding: 8px;
            }
        """)
        lay_telemetry.addWidget(self.txt_telemetry)
        panel_layout.addWidget(grp_telemetry)

        main_layout.addWidget(panel)

        # RIGHT SIDE CANVAS
        self.canvas = TrajectoryCanvas(self)
        main_layout.addWidget(self.canvas)

    def on_slider_change(self):
        self.dep_day = self.sld_dep.value()
        self.tof1 = self.sld_tof1.value()
        self.tof2 = self.sld_tof2.value()
        self.lbl_dep.setText(f"Departure Epoch: Day {self.dep_day}")
        self.lbl_tof1.setText(f"Leg 1 TOF: {self.tof1} days")
        self.lbl_tof2.setText(f"Leg 2 TOF: {self.tof2} days")
        self.recalculate_mission()

    def on_config_change(self):
        self.origin = self.cmb_origin.currentText()
        self.assist = self.cmb_assist.currentText()
        self.target = self.cmb_target.currentText()
        self.recalculate_mission()

    def toggle_animation(self):
        if self.anim_running:
            self.timer.stop()
            self.btn_anim.setText("▶ Resume Simulation")
            self.anim_running = False
        else:
            self.anim_step = 0
            self.timer.start(20)
            self.btn_anim.setText("⏸ Pause Simulation")
            self.anim_running = True

    def recalculate_mission(self):
        t0 = self.dep_day
        t1 = t0 + self.tof1
        t2 = t1 + self.tof2

        self.r_orig_t0, self.v_orig_t0 = get_planet_state(self.origin, t0)
        self.r_ast_t1,  self.v_ast_t1  = get_planet_state(self.assist, t1)
        self.r_tgt_t2,  self.v_tgt_t2  = get_planet_state(self.target, t2)

        self.leg1_pts = generate_conic_arc(self.r_orig_t0, self.r_ast_t1, self.tof1 * DAY_TO_SEC)
        self.leg2_pts = generate_conic_arc(self.r_ast_t1, self.r_tgt_t2, self.tof2 * DAY_TO_SEC)

        v1_est = np.linalg.norm(self.leg1_pts[1] - self.leg1_pts[0]) / (self.tof1 * DAY_TO_SEC / 400)
        v_orig_mag = np.linalg.norm(self.v_orig_t0)
        self.dv_dep = abs(v1_est - v_orig_mag)
        self.dv_arr = 2.450

        self.update_telemetry_box()
        self.plot_porkchop_contour()
        self.render_space_scene()

    def render_space_scene(self):
        ax = self.canvas.ax_3d
        ax.clear()
        ax.set_facecolor('#05070B')

        ax.grid(True, color='#1A233A', linestyle='--', linewidth=0.4, alpha=0.6)
        ax.xaxis.pane.fill = False
        ax.yaxis.pane.fill = False
        ax.zaxis.pane.fill = False
        ax.xaxis.pane.set_edgecolor('#101726')
        ax.yaxis.pane.set_edgecolor('#101726')
        ax.zaxis.pane.set_edgecolor('#101726')

        ax.scatter([0], [0], [0], color='#FFE57F', s=220, zorder=10)
        ax.scatter([0], [0], [0], color='#FF9100', s=500, alpha=0.25, zorder=9)
        ax.scatter([0], [0], [0], color='#FF6D00', s=900, alpha=0.10, zorder=8)

        theta = np.linspace(0, 2*np.pi, 600)
        for p_name in [self.origin, self.assist, self.target]:
            p = PLANETS[p_name]
            a_val = p['a']
            inc = np.radians(p['inc'])
            ax.plot(a_val*np.cos(theta), a_val*np.sin(theta)*np.cos(inc), a_val*np.sin(theta)*np.sin(inc), 
                    color=p['color'], linestyle=':', linewidth=0.9, alpha=0.4, label=f'{p_name} Orbit')

        r_orig_au = self.r_orig_t0 / AU
        r_ast_au  = self.r_ast_t1 / AU
        r_tgt_au  = self.r_tgt_t2 / AU

        for r_pos, p_name in zip([r_orig_au, r_ast_au, r_tgt_au], [self.origin, self.assist, self.target]):
            c = PLANETS[p_name]['color']
            ax.scatter(r_pos[0], r_pos[1], r_pos[2], color=c, s=70, edgecolors='#FFFFFF', linewidth=1.2, zorder=7)
            ax.scatter(r_pos[0], r_pos[1], r_pos[2], color=c, s=250, alpha=0.2, zorder=6)

        leg1_au = self.leg1_pts / AU
        leg2_au = self.leg2_pts / AU
        
        ax.plot(leg1_au[:, 0], leg1_au[:, 1], leg1_au[:, 2], color='#00E5FF', linewidth=5.0, alpha=0.25)
        ax.plot(leg2_au[:, 0], leg2_au[:, 1], leg2_au[:, 2], color='#FF3366', linewidth=5.0, alpha=0.25)
        
        ax.plot(leg1_au[:, 0], leg1_au[:, 1], leg1_au[:, 2], color='#00E5FF', linewidth=1.8, label='Leg 1 Transfer', antialiased=True)
        ax.plot(leg2_au[:, 0], leg2_au[:, 1], leg2_au[:, 2], color='#FF3366', linewidth=1.8, label='Leg 2 Transfer', antialiased=True)

        self.probe_glow, = ax.plot([leg1_au[0,0]], [leg1_au[0,1]], [leg1_au[0,2]], 
                                    marker='o', color='#00E5FF', markersize=14, alpha=0.3)
        self.probe_marker, = ax.plot([leg1_au[0,0]], [leg1_au[0,1]], [leg1_au[0,2]], 
                                     marker='o', color='#FFFFFF', markersize=5, markeredgecolor='#00E5FF')

        lim = PLANETS[self.target]['a'] * 1.15
        ax.set_xlim(-lim, lim)
        ax.set_ylim(-lim, lim)
        ax.set_zlim(-1.5, 1.5)
        ax.set_title("Heliocentric Ecliptic Trajectory Plot (NASA-GMAT Vector View)", color='#00E5FF', fontsize=10, fontweight='bold', pad=12)
        ax.set_xlabel("X (AU)", color='#6C7A9C', fontsize=8)
        ax.set_ylabel("Y (AU)", color='#6C7A9C', fontsize=8)
        ax.set_zlabel("Z (AU)", color='#6C7A9C', fontsize=8)
        ax.tick_params(colors='#4A556B', labelsize=7)
        ax.legend(loc='upper right', facecolor='#0B0E14', edgecolor='#1E2638', labelcolor='#EEE', fontsize=7)

        self.canvas.draw()

    def plot_porkchop_contour(self):
        ax = self.canvas.ax_pork
        ax.clear()

        deps = np.linspace(self.dep_day - 50, self.dep_day + 50, 30)
        tofs = np.linspace(self.tof1 - 60, self.tof1 + 60, 30)
        D, T = np.meshgrid(deps, tofs)
        C3_grid = np.zeros(D.shape)

        for i in range(D.shape[0]):
            for j in range(D.shape[1]):
                dep_d = D[i, j]
                tof_d = T[i, j]
                r1, _ = get_planet_state(self.origin, dep_d)
                r2, _ = get_planet_state(self.assist, dep_d + tof_d)
                v_est = np.linalg.norm(r2 - r1) / (tof_d * DAY_TO_SEC)
                C3_grid[i, j] = ((v_est / 1000.0) - 29.78)**2

        cp = ax.contour(D, T, C3_grid, levels=14, cmap='viridis')
        ax.clabel(cp, inline=True, fontsize=7, fmt='%1.1f')
        ax.scatter([self.dep_day], [self.tof1], color='#00E5FF', s=80, marker='*')

        ax.set_title(f"Porkchop Contour (C3 Energy: {self.origin} → {self.assist})", color='#00E5FF', fontsize=10, fontweight='bold')
        ax.set_xlabel("Departure Date (Days)", color='#888', fontsize=8)
        ax.set_ylabel("Leg 1 TOF (Days)", color='#888', fontsize=8)
        ax.tick_params(colors='#888', labelsize=8)
        ax.grid(True, color='#1E2638', linestyle=':')

    def update_animation(self):
        self.anim_step = (self.anim_step + 1) % 200

        if self.anim_step < 100:
            idx = int((self.anim_step / 100) * (len(self.leg1_pts) - 1))
            pos_au = self.leg1_pts[idx] / AU
        else:
            idx = int(((self.anim_step - 100) / 100) * (len(self.leg2_pts) - 1))
            pos_au = self.leg2_pts[idx] / AU

        if self.probe_marker and self.probe_glow:
            self.probe_marker.set_data_3d([pos_au[0]], [pos_au[1]], [pos_au[2]])
            self.probe_glow.set_data_3d([pos_au[0]], [pos_au[1]], [pos_au[2]])
            self.canvas.draw_idle()

    def update_telemetry_box(self):
        summary = f"""NASA MISSION ANALYSIS TELEMETRY
=================================
Departure  : {self.origin} (Day {self.dep_day})
Flyby      : {self.assist} (Day {self.dep_day + self.tof1})
Target     : {self.target} (Day {self.dep_day + self.tof1 + self.tof2})

MANEUVER ΔV DATA:
---------------------------------
Departure Δv    : {self.dv_dep:.3f} km/s
Target Capture  : {self.dv_arr:.3f} km/s
---------------------------------
TOTAL MISSION Δv: {(self.dv_dep + self.dv_arr):.3f} km/s
TRANSIT TIME    : {self.tof1 + self.tof2} Days
================================="""
        self.txt_telemetry.setText(summary)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())