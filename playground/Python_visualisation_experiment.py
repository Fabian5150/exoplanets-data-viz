import numpy as np
import plotly.graph_objects as go
import pandas as pd
from numpy.ma.core import negative
import plotly.subplots as sp

# Load dataset
file_path = "../data/nasa_aggregated.csv"  # Asegúrate de que el archivo esté en tu directorio de trabajo
df = pd.read_csv(file_path)

# Filtrar planetas tipo "Earth-like"
earth_like_planets = df[df["pl_type"] == "Earth-like"].copy()

while True:
    print("\nSelect an Earth-like exoplanet:")
    planet_names = earth_like_planets["pl_name"].unique()
    for i, planet in enumerate(planet_names):
        print(f"{i+1}. {planet}")

    try:
        selection = int(input("\nEnter number (or 0 to exit): "))
        if selection == 0:
            break  # Salir completamente del programa
        selected_planet = planet_names[selection - 1]
        selected_row = earth_like_planets[earth_like_planets["pl_name"] == selected_planet].iloc[0]
        print("\nSelected planet data:")
        print(selected_row)
    except (ValueError, IndexError):
        print("Invalid input, please enter a valid number.")
        continue  # Volver a pedir la selección del exoplaneta


    # Añadir manualmente la Tierra al dataset
    earth_data = {
        "pl_name": "Earth",
        "pl_rade": 1.0,  # Radio de la Tierra en radios terrestres
        "pl_type": "Earth-like"
    }

    # Function to generate a procedural texture with strong color separation
    def generate_texture(size, planet_type, seed):
        """Generates a procedural texture using different color patterns for Earth and Exoplanet."""
        np.random.seed(seed)  # Ensure unique patterns for each planet
        noise = np.random.rand(size, size)  # Generate random noise for texture variation

        # Normalize noise between 0 and 1
        normalized_noise = (noise - np.min(noise)) / (np.max(noise) - np.min(noise))

        texture = np.zeros((size, size, 3))  # Initialize RGB texture

        if planet_type == "earth":
            # Strong separation for ocean, land, and mountains
            texture[..., 0] = 0.2 + 0.4 * (1 - normalized_noise)  # Brown (mountains)
            texture[..., 1] = 0.4 + 0.5 * (1 - normalized_noise)  # Green (forests)
            texture[..., 2] = 0.8 * (1 - normalized_noise)  # Blue (oceans)

        elif planet_type == "exoplanet":
            # More alien-like colors (purple, cyan, red)
            texture[..., 0] = 0.7 * (1 - normalized_noise)  # Strong Magenta tone
            texture[..., 1] = 0.2 + 0.6 * normalized_noise  # Electric Cyan
            texture[..., 2] = 0.8 * normalized_noise  # Deep Purple tone

        return texture

    # Generate unique textures with different seeds
    earth_texture = generate_texture(50, "earth", seed=42)  # Earth seed
    exoplanet_texture = generate_texture(50, "exoplanet", seed=99)  # Exoplanet seed

    # Earth's data with real scientific values
    earth_data = {
        "pl_name": "Earth",  # Name of the planet
        "pl_rade": 6371,  # Earth's radius in kilometers
        "pl_bmasse": 5.972e24,  # Earth's mass in kilograms
        "pl_dens": 5.51,  # Earth's density in g/cm³
        "pl_orbsmax": 1.496e8,  # Earth's average distance from the Sun in kilometers (1 AU)
        "pl_eqt": 288  # Earth's average surface temperature in Kelvin
    }

    # Planetary data
    planets = ["Earth", selected_row["pl_name"]]

    radius_km = [earth_data["pl_rade"], earth_data["pl_rade"] * selected_row["pl_rade"]]  # Radius in km
    mass = [earth_data["pl_bmasse"], earth_data["pl_bmasse"] * selected_row["pl_bmasse"]]  # Mass in kg
    density = [earth_data["pl_dens"], selected_row["pl_dens"]]  # Density in g/cm³
    temperature = [earth_data["pl_eqt"], selected_row["pl_eqt"]]  # Temperature in K

    # Parameters to compare
    parameters = {
        "Radius (km)": radius_km,
        "Mass (kg)": mass,
        "Density (g/cm³)": density,
        "Temperature (K)": temperature
    }


    # Function to create a 3D sphere with procedural texture mapping
    def create_sphere_with_texture(radius, center_x, texture):
        """Creates a 3D sphere with a generated texture."""
        size = texture.shape[0]  # Get the texture resolution
        u = np.linspace(0, 2 * np.pi, size)
        v = np.linspace(0, np.pi, size)
        x = radius * np.outer(np.cos(u), np.sin(v)) + center_x
        y = radius * np.outer(np.sin(u), np.sin(v))
        z = radius * np.outer(np.ones(np.size(u)), np.cos(v))

        # Convert RGB to grayscale for Plotly's surfacecolor
        surfacecolor = np.dot(texture[..., :3], [0.2989, 0.5870, 0.1140])

        return go.Surface(
            x=x, y=y, z=z,
            surfacecolor=surfacecolor,  # Map grayscale depth from the texture
            colorscale="plasma" if center_x > 0 else "viridis",  # Earth (viridis), Exoplanet (plasma)
            showscale=False
        )

    # Function to update figure dynamically
    def update_figure(selected_param):
        values = parameters[selected_param]  # Get selected parameter values
        print(selected_param)
        # Create new figure from scratch
        fig = sp.make_subplots(
            rows=1, cols=2,
            specs=[[{"type": "surface"}, {"type": "bar"}]],
            subplot_titles=("Planetary Comparison", f"{selected_param} Comparison")
        )

        # Add planets in 3D with procedural textures
        fig.add_trace(create_sphere_with_texture(radius_km[0] / 10000, -1, earth_texture), row=1, col=1)  # Earth

        fig.add_trace(create_sphere_with_texture(radius_km[1] / 10000, 1, exoplanet_texture), row=1, col=1)  # Exoplanet

        # Add bar chart for selected parameter
        fig.add_trace(go.Bar(
            x=planets,
            y=values,
            name=selected_param,
            marker=dict(color=["blue", "red"])
        ), row=1, col=2)

        # Update layout
        fig.update_layout(
            title=f"Earth vs Exoplanet X - {selected_param} Comparison",
            scene=dict(
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                zaxis=dict(visible=False)
            ),
            template="plotly_dark",
            showlegend=False
        )

        fig.show()


    while True:
        print("\nSelect a parameter to compare:")
        for i, param in enumerate(parameters.keys()):
            print(f"{i + 1}. {param}")

        try:
            selection = int(input("\nEnter number (or 0 to select a new exoplanet): "))
            if selection == 0:
                break  # Regresar a la selección de exoplanetas
            if 1 <= selection <= len(parameters):
                selected_param = list(parameters.keys())[selection - 1]
                update_figure(selected_param)
            else:
                print("Invalid input, please enter a valid number.")
        except (ValueError, IndexError):
            print("Error, something has gone wrong.")
