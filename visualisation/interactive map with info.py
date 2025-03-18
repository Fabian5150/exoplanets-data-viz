# -*- coding: utf-8 -*-
"""
Created on Tue Mar 18 10:27:20 2025

@author: lalka
"""

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Load dataset
file_path = "C:/Users/lalka/Downloads/nasa_classified.csv"
data = pd.read_csv(file_path)

# Classification function
def classify_planet(row):
    radius, mass, temp = row["pl_rade"], row["pl_bmasse"], row["pl_eqt"]
    
    if pd.isna(radius) or pd.isna(mass) or pd.isna(temp):
        return "Unknown"
    elif 0.5 <= radius <= 1.5 and 0.5 <= mass <= 5 and 180 <= temp <= 370:
        return "Earth-like"
    else:
        return "Other"

# Apply classification
data["Planet_Type"] = data.apply(classify_planet, axis=1)
earth_like_planets = data[data["Planet_Type"] == "Earth-like"].copy()

# Normalize planet sizes
min_radius = earth_like_planets["pl_rade"].min()
max_radius = earth_like_planets["pl_rade"].max()
earth_like_planets["scaled_size"] = (earth_like_planets["pl_rade"] - min_radius) / (max_radius - min_radius) * 15 + 10

# Arrange planets in solar rings
num_planets = len(earth_like_planets)
angles = np.linspace(0, 2 * np.pi, num_planets, endpoint=False)
radii = np.linspace(70, 300, num_planets)  # Spread planets in solar rings

earth_like_planets["x"] = radii * np.cos(angles)
earth_like_planets["y"] = radii * np.sin(angles)
earth_like_planets["z"] = np.zeros(num_planets)  # Keep planets on a flat plane

# Function to generate orbit rings
def create_orbit(radius):
    theta = np.linspace(0, 2 * np.pi, 100)
    x = radius * np.cos(theta)
    y = radius * np.sin(theta)
    z = np.zeros_like(x)  # Keep rings on the same plane
    return go.Scatter3d(x=x, y=y, z=z, mode="lines",
                        line=dict(color="white", width=1.2, dash="dot"),
                        opacity=0.6, showlegend=False)

# Dash App
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Earth-like Exoplanet Explorer 🌍", style={"textAlign": "center", "color": "#FFFFFF"}),

    dcc.Graph(id="exoplanet-3D"),
    html.Div(
    id="planet-info",
    style={
        "color": "white",
        "backgroundColor": "#121212",
        "padding": "20px",
        "borderRadius": "10px",
        "textAlign": "center",
        "fontSize": "16px",
        "marginTop": "20px",
        "width": "80%",
        "marginLeft": "auto",
        "marginRight": "auto",
        "height": "80%"
    },
    children="Select a planet to see details here!"
),


    dcc.Dropdown(
        id="planet-select",
        options=[{"label": name, "value": name} for name in earth_like_planets["pl_name"]],
        value=earth_like_planets["pl_name"].iloc[0] if not earth_like_planets.empty else None,
        style={"width": "50%", "margin": "auto"}
    )
    
], style={"backgroundColor": "#1E1E1E", "padding": "20px"})  # Dark theme

# Callback for updating the visualization
@app.callback(
    [Output("exoplanet-3D", "figure"), Output("planet-info", "children")],
    Input("planet-select", "value")
)
def update_visual(selected_planet):
    fig = go.Figure()

    # Add orbit rings
    for r in np.linspace(70, 300, 10):  
        fig.add_trace(create_orbit(r))

    planet_info = "Select a planet to see details here!"
    
    fig.add_trace(go.Scatter3d(
    x=[0], y=[0], z=[0],  # Center of the solar system
    mode="markers+text",
    marker=dict(
        size=30,  # Big bright star
        color="yellow",
        opacity=1,
        line=dict(width=4, color="white")  # Glowing effect
    ),
    text="🌞 Host Star",
    textposition="middle center",
    textfont=dict(
        color="pink",
        size=20,
        family="Arial Black"
    )
))
    
    # Add all Earth-like planets, updating color if selected
    for _, row in earth_like_planets.iterrows():
        is_selected = row["pl_name"] == selected_planet

        fig.add_trace(go.Scatter3d(
            x=[row["x"]], y=[row["y"]], z=[row["z"]],
            mode="markers+text",
            marker=dict(
                size=row["scaled_size"] * (1.3 if is_selected else 1),
                color="red" if is_selected else "blue",
                opacity=1 if is_selected else 0.9,
                line=dict(width=3 if is_selected else 2, color="yellow" if is_selected else "white")
            ),
            text=row["pl_name"],
            textposition="middle center",
            textfont=dict(
                color="yellow" if is_selected else "cyan",
                size=16 if is_selected else 14,
                family="Arial Black"
            )
        ))

        # Update planet info when selected
        if is_selected:
            planet_info = html.Div([
                html.H3(f"🌍 {row['pl_name']}"),
                html.P(f"🌡️ Temperature: {row['pl_eqt']} K"),
                html.P(f"🪐 Radius: {row['pl_rade']} Earth radii"),
                html.P(f"⚖️ Mass: {row['pl_bmasse']} Earth masses"),
                html.P(f"🌟 Host Star: {row['hostname']}"),
                html.P(f"🪐 Orbit Period: {row['pl_orbper']} days"),
                html.P(f"🔘 Semi-Major Axis: {row['pl_orbsmax']} AU"),
                html.P(f"📏 Eccentricity: {row['pl_orbeccen']}")
            ])

    # Layout enhancements
    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            aspectmode="cube",
            bgcolor="black",
            camera=dict(
                eye=dict(x=0.3, y=0.4, z=0.6)  # Adjust zoom level (lower z = more zoomed in)
                )
        ),
        title="🌌 Interactive 3D Map of Earth-like Exoplanets",
        paper_bgcolor="black",
        font=dict(color="white"),
        margin=dict(l=0, r=0, b=0, t=30)
    )

    return fig, planet_info



# Run the app
if __name__ == "__main__":
    app.run_server(debug=True, port=8020)