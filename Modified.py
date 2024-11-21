import numpy as np
from matplotlib import pyplot as pl
import pint

ur = pint.UnitRegistry()

planetary_presets = {
    "Earth": {
        "mass": 5.98e24 * ur.kg,
        "diameter": 1.27e7 * ur.meter,
        "rotation_velocity": 460 * (ur.meter / ur.second),
        "color": "blue"
    },
    "Moon": {
        "mass": 7.35e22 * ur.kg,
        "diameter": 3.474e6 * ur.meter,
        "rotation_velocity": 4.6 * (ur.meter / ur.second),
        "color": "gray"
    },
    "Mars": {
        "mass": 6.39e23 * ur.kg,
        "diameter": 6.779e6 * ur.meter,
        "rotation_velocity": 240 * (ur.meter / ur.second),
        "color": "red"
    },
    "Sun": {
        "mass": 1.989e30 * ur.kg,
        "diameter": 1.3927e9 * ur.meter,
        "rotation_velocity": 2000 * (ur.meter / ur.second),
        "color": "yellow"
    }
}

print("Choose a planet or celestial body:")
for i, planet in enumerate(planetary_presets.keys()):
    print(f"{i + 1}. {planet}")
print(f"{len(planetary_presets) + 1}. Custom")

selection = int(input("Enter the number of your choice: "))

if 1 <= selection <= len(planetary_presets):
    chosen_body = list(planetary_presets.keys())[selection - 1]
    planet_data = planetary_presets[chosen_body]
    print(f"You selected: {chosen_body}")
else:
    print("Custom Planet Selected:")
    custom_mass = float(input("Enter the mass of the planet (kg): ")) * ur.kg
    custom_diameter = float(input("Enter the diameter of the planet (m): ")) * ur.meter
    custom_rotation_velocity = float(input("Enter the equatorial rotation velocity (m/s): ")) * (ur.meter / ur.second)
    custom_color = input("Enter the color for the planet (e.g., 'blue', 'red'): ").strip() or "green"

    planet_data = {
        "mass": custom_mass,
        "diameter": custom_diameter,
        "rotation_velocity": custom_rotation_velocity,
        "color": custom_color
    }
    print("Custom planet created.")

earth_mass = planet_data["mass"]
earth_diameter = planet_data["diameter"]
earth_velocity = planet_data["rotation_velocity"]
planet_color = planet_data["color"]

empty_mass = 29500 * ur.kg
payload_mass = 2000 * ur.kg
fuel_mass = 500000 * ur.kg
initial_mass = empty_mass + payload_mass + fuel_mass

tsfc = 3.5e-4 * (ur.second / ur.meter)
full_thrust = 7.6e6 * ur.newton
G = 6.674e-11 * (ur.meter ** 3 / (ur.kg * ur.second ** 2))

vec_pos = np.array([earth_diameter.magnitude / 2.0, 0.0]) * ur.meter
vec_vel = np.array([earth_velocity.magnitude, 0.0]) * (ur.meter / ur.second)
thrust_angle = 30.0 * ur.degree  # counterclockwise from horizontal
dir_thrust = np.array([np.cos(np.radians(thrust_angle)), np.sin(np.radians(thrust_angle))])

pl.ion()
fig = pl.figure()

planet = pl.Circle((0, 0), float(earth_diameter / 2.0 / ur.meter), color=planet_color)
fig.gca().add_artist(planet)

arrow_length = earth_diameter.magnitude / 20
arrow_width_factor = arrow_length / 15

arrowplt = pl.arrow(vec_pos.magnitude[0], vec_pos.magnitude[1],
                    ((dir_thrust[0]) * arrow_length), ((dir_thrust[1]) * arrow_length),
                    width=arrow_width_factor, color='r')

t = 0 * ur.s


def event_handler(event):
    global thrust_angle
    if event.key == ',':
        thrust_angle += 10.0 * ur.degree
    elif event.key == '.':
        thrust_angle -= 10.0 * ur.degree


def norm(vec):
    return np.sqrt(vec.dot(vec))


def force_gravity(r, m_1, m_2):
    return -(G * m_1 * m_2) / r ** 2


def unit_vec(vec):
    return vec / norm(vec)


fig.canvas.mpl_connect('key_press_event', event_handler)
pl.show()
pl.grid()

dt = 1 * ur.second
current_mass = initial_mass

while t <= 3600 * ur.second:
    t += dt

    dir_thrust = np.array([np.cos(np.radians(thrust_angle)), np.sin(np.radians(thrust_angle))])

    if fuel_mass.magnitude > 0:
        dt = 1 * ur.second
        change_fuel_mass = ((-tsfc * full_thrust) * dt).to(ur.kg)
        fuel_mass += change_fuel_mass
        current_mass += change_fuel_mass
    elif fuel_mass < 0 * ur.kg:
        print("Out of Fuel")
        fuel_mass = 0 * ur.kg
        dt = 10 * ur.second
        current_mass = initial_mass - 500000 * ur.kg
    else:
        dt = 10 * ur.second
        current_mass = initial_mass - 500000 * ur.kg

    if fuel_mass > 0:
        vec_thrust = dir_thrust * full_thrust
    else:
        vec_thrust = 0

    vec_gravity = unit_vec(vec_pos) * force_gravity(norm(vec_pos), earth_mass, current_mass)
    vec_accel = (vec_gravity + vec_thrust) / current_mass

    vec_vel = vec_vel + (vec_accel * dt)
    vec_pos = vec_pos + (vec_vel * dt)

    arrowplt.remove()

    arrow_length = max(norm(vec_pos.magnitude) / 10, earth_diameter.magnitude / 50)
    arrowplt = pl.arrow(vec_pos.magnitude[0], vec_pos.magnitude[1],
                        dir_thrust[0] * arrow_length, dir_thrust[1] * arrow_length,
                        width=arrow_length / 15, color='r')

    pos_magnitude = norm(vec_pos.magnitude)
    plot_scale = max(pos_magnitude * 1.2, earth_diameter.magnitude / 2.0 * 1.5)
    pl.axis((-plot_scale, plot_scale, -plot_scale, plot_scale))

    fig.canvas.draw()
    fig.canvas.flush_events()

    pl.title(f'Fuel Remaining: {fuel_mass.magnitude:.0f} kg')
    pl.xlabel(f'Current Time: {t.magnitude:.0f} seconds')
