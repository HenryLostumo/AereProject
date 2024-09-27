import numpy as np
from matplotlib import pyplot as pl
import pint

ur = pint.UnitRegistry()

empty_mass = 29500 * ur.kg
payload = 2000 * ur.kg
fuel_mass = 500000 * ur.kg
tsfc = 3.5e-4 * (ur.second / ur.meter)
full_thrust = 7.6e6 * ur.newton
G = 6.674e-11 * (ur.meter ** 3 / (ur.kg * ur.second ** 2))
earth_mass = 5.98e24 * ur.kg
earth_diameter = 1.27e7 * ur.meter
earth_velocity = 460 * (ur.meter / ur.second)

vec_pos = np.array([earth_diameter.magnitude / 2.0,
                    0.0])  # * ur.meter               FUCK PINT TODO: add units back, fucks up arrow plot when units are added
vec_vel = np.array([earth_velocity.magnitude, 0]) * (ur.meter / ur.second)

thrust_angle = 30.0 * ur.degree  # counter clock wise from horizontal
vec_thrust = np.array([np.cos(thrust_angle.to(ur.radians)), np.sin(thrust_angle.to(ur.radians))])


def event_handler(event):
    global vec_thrust
    if event.key == ',':
        vec_thrust += 10 * ur.degree
        pass
    elif event.key == '.':
        vec_thrust -= 10 * ur.degree
        pass
    elif hasattr(event, "button") and event.button == 1:
        if event.xdata < 0:
            vec_thrust += 10 * ur.degree
            pass
        else:
            vec_thrust -= 10 * ur.degree
            pass
        pass

    pass


pl.ion()
fig = pl.figure()
ax = fig.gca()

pl.axis((6e6, 7.5e6, -1e6, 1e6))
pl.grid()

earth = pl.Circle((0, 0), float(earth_diameter / 2.0 / ur.meter), color='g')
ax.add_artist(earth)

arrowplt = pl.arrow(vec_pos[0], vec_pos[1], vec_thrust[0] * 500000,
                    vec_thrust[1] * 500000)  # TODO: 500000 thing might fuck this up

fig.canvas.mpl_connect('key_press_event', event_handler)
fig.canvas.mpl_connect('button_press_event', event_handler)

pl.show()

dt = 1 * ur.second

for t in range(0, 1000):
    if fuel_mass.magnitude > 0:
        dt = 1 * ur.second  # Use 1 second time step during ascent
        # Decrease fuel mass (simple model, adjust fuel consumption logic as needed)
        change_fuel_mass = (-tsfc * full_thrust).to(ur.kg / ur.second)
        fuel_mass -= change_fuel_mass * dt
        if fuel_mass < 0 * ur.kg:
            fuel_mass = 0 * ur.kg  # Ensure fuel mass does not go negative
        else:
            dt = 10 * ur.second  # Use 10 seconds time step once fuel is depleted
