"""
naca_math.py
Module for generating NACA 4-digit airfoil coordinates.
"""
import numpy as np

def generate_naca_airfoil(m, p, t, c, n_points=100):
    """
    Calculates the 2D coordinates for a NACA 4-digit airfoil, using Cosine Spacing for CFD mesh stability.

    Args:
        m (float): Maximum camber as a percentage of the chord (e.g., 2.0 for 2%).
        p (float): Position of maximum camber in tens of percent of chord (e.g., 4.0 for 40%).
        t (float): Maximum thickness as a percentage of the chord (e.g., 12.0 for 12%).
        c (float): Chord length in metric units.
        n_points (int, optional): Number of coordinate points along the chord. Defaults to 100.

    Returns:
        tuple: Four 1D numpy arrays containing (X_upper, Y_upper, X_lower, Y_lower).
    """
    # Convert percentages to decimal fractions for calculation
    m_val = m / 100.0
    p_val = p / 10.0
    t_val = t / 100.0
    
    # Cosine spacing for better leading/trailing edge resolution
    theta = np.linspace(0, np.pi, n_points)
    x = (c / 2) * (1 - np.cos(theta))
    
    x_norm = x / c
    
    # Calculate half-thickness distribution (yt) across the chord length
    yt = 5 * t_val * c * (0.2969 * np.sqrt(x_norm) - 0.1260 * x_norm - 0.3516 * x_norm**2 + 0.2843 * x_norm**3 - 0.1015 * x_norm**4)
    
    # Initialize arrays for Mean Camber Line (yc) and its gradient (dyc_dx)
    yc = np.zeros_like(x)
    dyc_dx = np.zeros_like(x)

    # Piecewise calculation of the camber line based on position 'p'
    for i in range(len(x)):
        xi = x_norm[i]
        if xi <= p_val:
            yc[i] = (m_val * c / p_val**2) * (2 * p_val * xi - xi**2)
            dyc_dx[i] = (2 * m_val / p_val**2) * (p_val - xi)
        else:
            yc[i] = (m_val * c / (1 - p_val)**2) * ((1 - 2 * p_val) + 2 * p_val * xi - xi**2)
            dyc_dx[i] = (2 * m_val / (1 - p_val)**2) * (p_val - xi)

    # Calculate the angle of the camber line to apply thickness perpendicularly
    angle = np.arctan(dyc_dx)
    xu = x - yt * np.sin(angle)
    yu = yc + yt * np.cos(angle)
    xl = x + yt * np.sin(angle)
    yl = yc - yt * np.cos(angle)

    return xu, yu, xl, yl