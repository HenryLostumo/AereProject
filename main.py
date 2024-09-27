import numpy as np
from matplotlib import pyplot as pl
import pint

ur = pint.UnitRegistry()

empty_mass = 29500 * ur.kg
payload_mass = 2000 * ur.kg
fuel_mass = 500000 * ur.kg

initial_mass = (empty_mass + payload_mass + fuel_mass)

tsfc = 3.5e-4 * (ur.second / ur.meter)
full_thrust = 7.6e6 * ur.newton
G = 6.674e-11 * (ur.meter ** 3 / (ur.kg * ur.second ** 2))
earth_mass = 5.98e24 * ur.kg
earth_diameter = 1.27e7 * ur.meter
earth_velocity = 460 * (ur.meter / ur.second)

vec_pos = np.array([earth_diameter.magnitude / 2.0, 0.0]) * ur.meter
vec_vel = np.array([earth_velocity.magnitude, 0]) * (ur.meter / ur.second)
thrust_angle = 30.0 * ur.degree  # counter clock wise from horizontal
dir_thrust = np.array([np.cos(thrust_angle.to(ur.radians)), np.sin(thrust_angle.to(ur.radians))])

t = 0 * ur.s


def event_handler(event):
    global dir_thrust
    if event.key == ',':
        dir_thrust += 10 * ur.degree
        pass
    elif event.key == '.':
        dir_thrust -= 10 * ur.degree
        pass
    elif hasattr(event, "button") and event.button == 1:
        if event.xdata < 0:
            dir_thrust += 10 * ur.degree
            pass
        else:
            dir_thrust -= 10 * ur.degree
            pass
        pass

    pass


def norm(vec):
    vecs_unit = vec.units
    return np.sqrt(vec.dot(vec))  # * ur.vecs_unit


def force_gravity(r, m_1, m_2):
    return -(G * m_1 * m_2) / r ** 2


def unit_vec(vec):
    return vec / norm(vec)


pl.ion()
fig = pl.figure()
ax = fig.gca()

pl.axis((6e6, 7.5e6, -1e6, 1e6))
pl.grid()

earth = pl.Circle((0, 0), float(earth_diameter / 2.0 / ur.meter), color='g')
ax.add_artist(earth)

arrow_length = 500000

arrowplt = pl.arrow(vec_pos.magnitude[0], vec_pos.magnitude[1], dir_thrust[0] * 500000,
                    dir_thrust[1] * 500000)  # TODO: 500000 thing might fuck this up

fig.canvas.mpl_connect('key_press_event', event_handler)
fig.canvas.mpl_connect('button_press_event', event_handler)

pl.show()

dt = 1 * ur.second

while t <= 3600 * ur.second:
    t += 1 * ur.second
    if fuel_mass.magnitude > 0:
        pl.axis((5.5e6, 8e6, -1e6, 1e6))
        dt = 1 * ur.second
        change_fuel_mass = ((-tsfc * full_thrust) * dt).to(ur.kg)
        # print(change_fuel_mass)
        fuel_mass += change_fuel_mass
        if fuel_mass < 0 * ur.kg:
            print("Out of Fuel")
            pl.axis((-1e7, 1e7, -1e7, 1e7))
            fuel_mass = 0 * ur.kg
        else:
            pl.axis((-1e7, 1e7, -1e7, 1e7))
            dt = 10 * ur.second
        pl.title(f'Fuel Remaining {np.round((fuel_mass.magnitude / 500000) * 100, 2)}%')
        pl.xlabel(f'Current Time: {t}s')
        arrowplt.remove()

        current_mass = initial_mass + change_fuel_mass

        vec_gravity = unit_vec(vec_pos) * force_gravity(norm(vec_pos), earth_mass, current_mass)

        if fuel_mass > 0:
            vec_thrust = ((np.sqrt(dir_thrust.dot(dir_thrust))) / dir_thrust) * full_thrust
        else:
            vec_thrust = 0

        vec_accel = (vec_gravity + vec_thrust) / current_mass
        print(vec_accel)
        print(vec_vel)
        vec_vel = vec_vel + vec_accel * dt  # Cannot do += here?

        vec_pos += vec_vel * dt  # TODO: update rocket position based on gravity type shit

        # Draw the new arrow
        arrowplt = pl.arrow(vec_pos.magnitude[0], vec_pos.magnitude[1],
                            dir_thrust[0] * arrow_length, dir_thrust[1] * arrow_length,
                            width=300000, color='r')

        fig.canvas.draw()
        fig.canvas.flush_events()
