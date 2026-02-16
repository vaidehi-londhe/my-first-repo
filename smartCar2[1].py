import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Rectangle, Circle


fig, ax = plt.subplots(figsize=(12, 9))

ax.set_xlim(-20, 180) 
ax.set_ylim(-40, 160)
ax.set_title("Smart Car Security: Start in Safe Zone & Breach Alert", fontsize=14, fontweight='bold')

# Base towers 
towers = [(20, 25), (140, 25), (25, 110), (140, 110), (80, 75)]
tower_names = ["BTS-1", "BTS-2", "BTS-3", "BTS-4", "Serving BTS"]
for i, (tx, ty) in enumerate(towers):
    ax.plot(tx, ty, 'g^', markersize=14)
    ax.text(tx-3, ty+5, tower_names[i], fontweight='bold', fontsize=8)

# GPRS Satellites
satellites = [(30, 130), (75, 135), (120, 130)]
for i, (sx, sy) in enumerate(satellites):
    ax.add_patch(Circle((sx, sy), 2, fill=True, color='orange'))
    ax.text(sx-3, sy+4, f"SAT{i+1}", fontsize=8)

# Circular Geo-Fence
F_CENTER = (65, 50)
F_RADIUS = 35
geofence = Circle(F_CENTER, F_RADIUS, fill=True, color='green', alpha=0.1, ls='--', lw=2.5)
ax.add_patch(geofence)

# Infrastructure
cloud = Rectangle((110, -25), 35, 15, fill=True, edgecolor='blue', facecolor='lightblue', lw=2.5)
phone = Rectangle((15, -25), 12, 20, facecolor="#34495e", alpha=0.9, edgecolor="black")
ax.add_patch(cloud); ax.add_patch(phone)
ax.text(127.5, -20, "Server", ha='center', weight='bold')
ax.text(21, -12, "Phone", color="white", ha='center', weight='bold', fontsize=7)

# Vehicle 
car = Rectangle((0, 0), 4, 2, color='red', zorder=10)
ax.add_patch(car)

# Signal Path Lines
alert_path, = ax.plot([], [], 'red', lw=3, alpha=0)  
tracking_path, = ax.plot([], [], color='blue', lw=3, ls='--', alpha=0) 
# Prominent GPS signals 
gps_signals = [ax.plot([], [], color='orange', lw=2.5, ls=':', alpha=0.6)[0] for _ in satellites]

# Fixed status label using transAxes
status_label = ax.text(0.02, 0.95, "INITIALIZING...", transform=ax.transAxes, 
                       fontsize=10, family='monospace', bbox=dict(facecolor='white', alpha=0.8))

#path logic
frames = 350
path_x = [45 + 0.3 * i for i in range(frames)]
path_y = [50 + 20 * math.sin(0.06 * i) for i in range(frames)]

state = {"breach_frame": -1}

def update(frame):
    x, y = path_x[frame], path_y[frame]
    car.set_xy((x, y))
    
    # Handover Logic
    dists = [math.sqrt((x-tx)**2 + (y-ty)**2) for tx, ty in towers]
    nearest_idx = np.argmin(dists)
    current_bts = towers[nearest_idx]

    # GPS Update
    for i, (sx, sy) in enumerate(satellites):
        gps_signals[i].set_data([sx, x+2], [sy, y+1])

    # Calculate distance using indexed tuple values
    dist_from_center = math.sqrt((x - F_CENTER[0])**2 + (y - F_CENTER[1])**2)
    is_outside = dist_from_center > F_RADIUS
    
    if frame == 0: state["breach_frame"] = -1

    if is_outside:
        if state["breach_frame"] == -1: 
            state["breach_frame"] = frame 
            
        # Alert Path
        if frame < state["breach_frame"] + 25:
            alert_path.set_data([x+2, current_bts[0], 21], [y+1, current_bts[1], -5])
            alert_path.set_alpha(1.0)
        else:
            alert_path.set_alpha(0)
            
        # tracking the car
        tracking_path.set_data([x+2, current_bts[0], 127], [y+1, current_bts[1], -10])
        tracking_path.set_alpha(0.9 if frame % 4 != 0 else 0.3)
        msg = f"!!! THEFT DETECTED !!!\nCONNECTED: {tower_names[nearest_idx]}\nMODE: GPRS STREAMING"
    else:
        msg = f"STATUS: SECURE\nCONNECTED: {tower_names[nearest_idx]}\nMONITORING..."
        tracking_path.set_alpha(0)
        alert_path.set_alpha(0)

    status_label.set_text(msg)
    return [car, alert_path, tracking_path, status_label] + gps_signals

ani = FuncAnimation(fig, update, frames=frames, interval=40, blit=True, repeat=True)
plt.show()
