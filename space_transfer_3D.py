import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Button

plt.rcParams['toolbar'] = 'none'

#ASTRODYNAMICS CONSTANTS
G = 6.67430e-11
M_SUN = 1.989e30
AU = 1.496e11

R_EARTH_AU = 1.0
R_MARS_AU = 1.524
T_EARTH_DAYS = 365.25
T_MARS_DAYS = 686.98

W_EARTH = 2 * np.pi / T_EARTH_DAYS
W_MARS = 2 * np.pi / T_MARS_DAYS

a_trans_au = (R_EARTH_AU + R_MARS_AU) / 2.0
a_trans_m = a_trans_au * AU
tof_seconds = np.pi * np.sqrt(a_trans_m**3 / (G * M_SUN))
tof_days = tof_seconds / (24 * 3600)

required_phase_angle = np.pi - (W_MARS * tof_days)
optimal_launch_day = (required_phase_angle % (2 * np.pi)) / (W_EARTH - W_MARS)
if optimal_launch_day < 0:
    optimal_launch_day += 365.25

print(f"\n=======================================================")
print(f" SUGGESTED OPTIMAL LAUNCH WINDOW: Day of the year {optimal_launch_day:.1f}")
print(f"=======================================================\n")

user_input = input(f"Enter Departure Day (1-365) [Press Enter for Optimal Day {optimal_launch_day:.0f}]: ")
if user_input.strip() == "":
    dept_day = optimal_launch_day
else:
    try:
        dept_day = float(user_input)
    except ValueError:
        dept_day = optimal_launch_day

#POSITIONAL COMPUTATIONS
th_e_dept = W_EARTH * dept_day
th_m_dept = W_MARS * dept_day
arr_day = dept_day + tof_days
th_m_arr = W_MARS * arr_day

e_trans = (R_MARS_AU - R_EARTH_AU) / (R_MARS_AU + R_EARTH_AU)
nu = np.linspace(0, np.pi, 200)

d_theta = (th_m_arr - th_e_dept) % (2 * np.pi)
r_craft_path = (a_trans_au * (1 - e_trans**2)) / (1 + e_trans * np.cos(nu))
theta_craft_path = th_e_dept + (nu * (d_theta / np.pi))

x_path = r_craft_path * np.cos(theta_craft_path)
y_path = r_craft_path * np.sin(theta_craft_path)

v_earth = np.sqrt(G * M_SUN / (R_EARTH_AU * AU))
v_mars = np.sqrt(G * M_SUN / (R_MARS_AU * AU))
v_perihelion = np.sqrt(G * M_SUN * (2/(R_EARTH_AU*AU) - 1/a_trans_m))
v_aphelion = np.sqrt(G * M_SUN * (2/(R_MARS_AU*AU) - 1/a_trans_m))

delta_v_dept = abs(v_perihelion - v_earth) / 1000.0
delta_v_arr = abs(v_mars - v_aphelion) / 1000.0

fig = plt.figure(figsize=(10, 8), facecolor='#0a0c10')
ax = fig.add_subplot(111, projection='3d', facecolor='#0a0c10')

plt.subplots_adjust(left=0.02, right=0.98, bottom=0.10, top=0.88)

#Background Orbits
theta = np.linspace(0, 2*np.pi, 300)
ax.plot(R_EARTH_AU*np.cos(theta), R_EARTH_AU*np.sin(theta), 0, color='#4ba3e3', linestyle=':', alpha=0.35, label='Earth Orbit')
ax.plot(R_MARS_AU*np.cos(theta), R_MARS_AU*np.sin(theta), 0, color='#e25822', linestyle=':', alpha=0.35, label='Mars Orbit')

# Sun
ax.scatter([0], [0], [0], color='#ffcc00', s=350, label='Sun')

# Static Planned Arc
ax.plot(x_path, y_path, np.zeros_like(x_path), color='#00ffcc', linestyle='--', alpha=0.35, label='Transfer Path')

# Animated Elements
earth_marker, = ax.plot([], [], [], 'o', color='#4ba3e3', markersize=9, label='Earth')
mars_marker, = ax.plot([], [], [], 'o', color='#e25822', markersize=8, label='Mars')
craft_marker, = ax.plot([], [], [], '^', color='#00ffcc', markersize=7, label='Spacecraft')
craft_trail, = ax.plot([], [], [], color='#00ffcc', linewidth=2.2, label='Active Path')

# Equalize axis scaling to prevent 3D distortion
ax.set_xlim(-1.8, 1.8)
ax.set_ylim(-1.8, 1.8)
ax.set_zlim(-0.6, 0.6)
ax.set_box_aspect([1, 1, 0.35])  
ax.set_axis_off()

ax.legend(facecolor='#161b22', edgecolor='#30363d', labelcolor='white', loc='lower right', bbox_to_anchor=(0.98, 0.02))

# Telemetry Display 
phase_diff_deg = np.degrees((th_m_dept - th_e_dept) % (2*np.pi) - required_phase_angle)
info = (
    f"--- MISSION TELEMETRY ---\n"
    f"Departure Day        : Day {dept_day:.0f}\n"
    f"Arrival Day          : Day {arr_day:.0f}\n"
    f"Transit Time         : {tof_days:.1f} Days\n"
    f"Earth Departure Burn : +{delta_v_dept:.2f} km/s\n"
    f"Mars Insertion Burn  : +{delta_v_arr:.2f} km/s\n"
    f"Alignment Error      : {phase_diff_deg:+.1f}° "
    f"({'PERFECT INTERSECT' if abs(phase_diff_deg) < 5 else 'CORRECTION NEEDED'})"
)
ax.text2D(0.03, 0.85, info, transform=ax.transAxes, color='white', fontsize=9, fontfamily='monospace',
          bbox=dict(boxstyle="round,pad=0.6", facecolor="#161b22", edgecolor="#30363d", alpha=0.9))

trail_x, trail_y = [], []
anim = None

def update(frame):
    sim_day = dept_day + frame
    
    th_e = W_EARTH * sim_day
    th_m = W_MARS * sim_day

    earth_marker.set_data([R_EARTH_AU * np.cos(th_e)], [R_EARTH_AU * np.sin(th_e)])
    earth_marker.set_3d_properties([0])
    
    mars_marker.set_data([R_MARS_AU * np.cos(th_m)], [R_MARS_AU * np.sin(th_m)])
    mars_marker.set_3d_properties([0])

    transit_progress = frame / tof_days
    if 0 <= transit_progress <= 1.0:
        idx = int(transit_progress * (len(x_path) - 1))
        c_x, c_y = x_path[idx], y_path[idx]

        trail_x.append(c_x)
        trail_y.append(c_y)

        craft_marker.set_data([c_x], [c_y])
        craft_marker.set_3d_properties([0])

        craft_trail.set_data(trail_x, trail_y)
        craft_trail.set_3d_properties(np.zeros(len(trail_x)))

    return earth_marker, mars_marker, craft_marker, craft_trail

def start_animation(event=None):
    global anim, trail_x, trail_y
    trail_x.clear()
    trail_y.clear()
    craft_trail.set_data([], [])
    craft_trail.set_3d_properties([])
    
    if anim is not None:
        anim.event_source.stop()
        
    anim = animation.FuncAnimation(
        fig, update, frames=int(tof_days) + 1, interval=20, blit=False, repeat=False
    )
    fig.canvas.draw_idle()

# --- RESTART BUTTON AT BOTTOM CENTER ---
ax_btn = plt.axes([0.40, 0.02, 0.20, 0.045])
btn = Button(ax_btn, 'Re-Launch Mission', color='#238636', hovercolor='#2ea043')
btn.label.set_color('white')
btn.label.set_fontweight('bold')
btn.on_clicked(start_animation)

start_animation()
plt.show()