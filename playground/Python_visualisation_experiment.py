import numpy as np
import plotly.graph_objects as go
import plotly.subplots as sp

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

# Planetary data
planets = ["Earth", "Exoplanet X"]
radius_km = [6371, 6371 * 2]  # Radius in km (Earth and Exoplanet 2x)
mass = [5.97, 5.97 * 8]  # Mass in 10^24 kg
density = [5.51, 4.2]  # g/cm³
temperature = [288, 500]  # K
water_percentage = [71, 30]  # % of surface covered with water

# Parameters to compare
parameters = {
    "Radius (km)": radius_km,
    "Mass (10^24 kg)": mass,
    "Density (g/cm³)": density,
    "Temperature (K)": temperature,
    "Water Surface (%)": water_percentage
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

    # Convert RGB to grayscale for Plotly's `surfacecolor`
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

    # Create new figure from scratch
    fig = sp.make_subplots(
        rows=1, cols=2,
        specs=[[{"type": "surface"}, {"type": "bar"}]],
        subplot_titles=("Planetary Comparison", f"{selected_param} Comparison")
    )

    # Add planets in 3D with procedural textures
    fig.add_trace(create_sphere_with_texture(radius_km[0] / 10000, -1.5, earth_texture), row=1, col=1)  # Earth
    fig.add_trace(create_sphere_with_texture(radius_km[1] / 10000, 1.5, exoplanet_texture), row=1, col=1)  # Exoplanet

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

# Main program loop (for non-Jupyter environments)
while True:
    print("\nSelect a parameter to compare:")
    for i, param in enumerate(parameters.keys()):
        print(f"{i+1}. {param}")

    try:
        selection = int(input("\nEnter number (or 0 to exit): "))
        if selection == 0:
            break
        if 1 <= selection <= len(parameters):
            selected_param = list(parameters.keys())[selection - 1]
            update_figure(selected_param)
        else:
            print("Invalid input, please enter a valid number.")
    except (ValueError, IndexError):
        print("Invalid input, please enter a valid number.")
