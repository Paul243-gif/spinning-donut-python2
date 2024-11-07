import numpy as np
import time

screen_size = 40
theta_spacing = 0.07
phi_spacing = 0.02
illumination = np.fromiter(".,-~:;=!*#$@", dtype="<U1")

A = 1
B = 1
R1 = 1
R2 = 2
K2 = 5
K1 = screen_size * K2 * 3 / (8.0 * (R1 + R2))  # Ensuring float division

def render_frame(A, B):
    """
    Returns a frame of the spinning 3D donut.
    Based on the pseudocode from: https://www.a1k0n.net/2011/07/20/donut-math.html
    """

    time.sleep(0.02)

    cos_A = np.cos(A)
    sin_A = np.sin(A)
    cos_B = np.cos(B)
    sin_B = np.sin(B)

    output = np.full((screen_size, screen_size), " ")  # (40, 40)
    zbuffer = np.zeros((screen_size, screen_size))  # (40, 40)

    # Generate angle arrays for phi and theta
    cos_phi = np.cos(np.arange(0, 2 * np.pi, phi_spacing))  # (315,)
    sin_phi = np.sin(np.arange(0, 2 * np.pi, phi_spacing))  # (315,)
    cos_theta = np.cos(np.arange(0, 2 * np.pi, theta_spacing))  # (90,)
    sin_theta = np.sin(np.arange(0, 2 * np.pi, theta_spacing))  # (90,)

    # Precompute x and y coordinates on the circle
    circle_x = R2 + R1 * cos_theta  # (90,)
    circle_y = R1 * sin_theta  # (90,)

    # Compute 3D positions of the points on the torus
    x = (np.outer(cos_B * cos_phi + sin_A * sin_B * sin_phi, circle_x) - circle_y * cos_A * sin_B).T  # (90, 315)
    y = (np.outer(sin_B * cos_phi - sin_A * cos_B * sin_phi, circle_x) + circle_y * cos_A * cos_B).T  # (90, 315)
    z = ((K2 + cos_A * np.outer(sin_phi, circle_x)) + circle_y * sin_A).T  # (90, 315)

    # Calculate projected screen coordinates and luminance
    ooz = 1 / z  # Avoid division by zero; numpy will handle it by setting inf to very large
    xp = (screen_size / 2 + K1 * ooz * x).astype(int)  # (90, 315)
    yp = (screen_size / 2 - K1 * ooz * y).astype(int)  # (90, 315)

    L1 = ((np.outer(cos_phi, cos_theta) * sin_B) - cos_A * np.outer(sin_phi, cos_theta) - sin_A * sin_theta)  # (315, 90)
    L2 = cos_B * (cos_A * sin_theta - np.outer(sin_phi, cos_theta * sin_A))  # (315, 90)
    L = np.around((L1 + L2) * 8).astype(int).T  # (90, 315)
    
    mask_L = L >= 0  # Mask where luminance values are valid
    chars = illumination[L]  # Select characters based on luminance

    # Populate the output array and zbuffer for the current frame
    for i in range(90):
        mask = mask_L[i] & (ooz[i] > zbuffer[xp[i], yp[i]])  # Check for valid luminance and depth

        zbuffer[xp[i], yp[i]] = np.where(mask, ooz[i], zbuffer[xp[i], yp[i]])
        output[xp[i], yp[i]] = np.where(mask, chars[i], output[xp[i], yp[i]])

    return output

def pprint(array):
    """Pretty print the frame."""
    for row in array:
        print " ".join(row)

if __name__ == "__main__":
    for _ in range(screen_size * screen_size):
        A += theta_spacing
        B += phi_spacing
        print "\x1b[H"  # Clears the screen and moves the cursor to the top-left
        pprint(render_frame(A, B))
