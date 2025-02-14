from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random
import time
import sys


# Window dimensions
WIDTH, HEIGHT = 800, 600

# Global variables initialization
misfires = 0  # Initialize the misfires counter
consecutive_misses = 0  # Consecutive misses counter
score = 0  # Score counter
falling_circles = []  # List of falling circles
bullets = []  # List of bullets
power_up_active = False  # Whether the power-up is active or not
power_up_circle = None  # The current power-up circle
power_up_timer = 0  # Timer for power-up duration
power_up_duration = 500  # Duration for the power-up
shooter_x = WIDTH // 2  # X position of the shooter (spaceship)
shooter_y = 50  # Y position of the shooter
shooter_width = 50  # Width of the shooter (spaceship)
shooter_height = 10  # Height of the shooter
paused = False  # Game paused state

# Circle generation settings
circle_radius = 20
circle_speed = 2

# Bullet settings
bullet_speed = 5

#Power-up settings
power_up_active = False
power_up_timer = 0
power_up_circle = None
power_up_duration = 600

# Variable to store the last time for flame flicker effect
last_time = time.time()

# Midpoint circle drawing algorithm
def draw_circle(xc, yc, r):
    x = 0
    y = r
    d = 1 - r

    def draw_symmetric_points(xc, yc, x, y):
        glVertex2f(xc + x, yc + y)
        glVertex2f(xc - x, yc + y)
        glVertex2f(xc + x, yc - y)
        glVertex2f(xc - x, yc - y)
        glVertex2f(xc + y, yc + x)
        glVertex2f(xc - y, yc + x)
        glVertex2f(xc + y, yc - x)
        glVertex2f(xc - y, yc - x)

    glBegin(GL_POINTS)
    while x <= y:
        draw_symmetric_points(xc, yc, x, y)
        if d < 0:
            d += 2 * x + 3
        else:
            d += 2 * (x - y) + 5
            y -= 1
        x += 1
    glEnd()


# Axis-Aligned Bounding Box (AABB) collision detection
def has_collided(aabb1, aabb2):
    return (
            aabb1["x"] < aabb2["x"] + aabb2["width"] and
            aabb1["x"] + aabb1["width"] > aabb2["x"] and
            aabb1["y"] < aabb2["y"] + aabb2["height"] and
            aabb1["y"] + aabb1["height"] > aabb2["y"]
    )


# Draw rocket-shaped shooter
def draw_shooter(x, y, width, height):
    glColor3f(1.0, 0.5, 0.0)  # Orange color for the rocket

    # Draw the rocket body (rectangle)
    glBegin(GL_LINE_LOOP)
    glVertex2f(x, y)
    glVertex2f(x + width, y)
    glVertex2f(x + width, y + height - 20)
    glVertex2f(x, y + height - 20)
    glEnd()

    # Draw the rocket tip (triangle)
    glBegin(GL_LINE_LOOP)
    glVertex2f(x, y + height - 20)
    glVertex2f(x + width / 2, y + height)
    glVertex2f(x + width, y + height - 20)
    glEnd()

    # Draw the rocket fins (triangles on the sides)
    glBegin(GL_LINE_LOOP)
    glVertex2f(x, y)
    glVertex2f(x - width / 2, y + height / 2 - 10)
    glVertex2f(x, y + height / 2)
    glEnd()

    glBegin(GL_LINE_LOOP)
    glVertex2f(x + width, y)
    glVertex2f(x + width + width / 2, y + height / 2 - 10)
    glVertex2f(x + width, y + height / 2)
    glEnd()

    # Draw the rocket exhaust pipes (three small rectangles)
    exhaust_width = width / 5
    exhaust_spacing = exhaust_width / 2
    for i in range(3):
        exhaust_x = x + exhaust_spacing + i * (exhaust_width + exhaust_spacing)
        glBegin(GL_LINE_LOOP)
        glVertex2f(exhaust_x, y)
        glVertex2f(exhaust_x + exhaust_width, y)
        glVertex2f(exhaust_x + exhaust_width, y - height / 3)
        glVertex2f(exhaust_x, y - height / 3)
        glEnd()

    # Add dynamic exhaust flame
    draw_flame(x + width / 2, y - height / 3, width / 2)

# Draw dynamic flame for exhaust
def draw_flame(x, y, width):
    global last_time
    current_time = time.time()
    flicker = 10 * ((current_time - last_time) % 0.1)

    glColor3f(1.0, 0.6, 0.0)  # Flame orange
    glBegin(GL_TRIANGLES)
    glVertex2f(x, y)
    glVertex2f(x - width / 2, y - flicker)
    glVertex2f(x + width / 2, y - flicker)
    glEnd()

    last_time = current_time



def draw_power_up(x, y, r):
    glColor3f(1.0, 1.0, 0.0)  
    draw_circle(x, y, r)



def draw_left_arrow(x, y):
    glColor3f(1.0, 1.0, 1.0)
    glBegin(GL_POINTS)
    for i in range(5):
        glVertex2f(x + i, y + i)
        glVertex2f(x + i, y - i)
    glEnd()


def draw_pause_play_icon(x, y):
    glColor3f(1.0, 0.6, 0.0)  # Amber color for Play/Pause icon
    glBegin(GL_POINTS)
    for i in range(5):
        glVertex2f(x, y + i)
        glVertex2f(x, y - i)
    for i in range(5):
        glVertex2f(x + 10, y + i)
        glVertex2f(x + 10, y - i)
    glEnd()


def draw_close_icon(x, y):
    glColor3f(1.0, 0.0, 0.0)  # Red color for Close icon
    glBegin(GL_POINTS)
    for i in range(5):
        glVertex2f(x + i, y + i)
        glVertex2f(x + i, y - i)
        glVertex2f(x - i, y + i)
        glVertex2f(x - i, y - i)
    glEnd()



def display():
    glClear(GL_COLOR_BUFFER_BIT)

    draw_shooter(shooter_x, shooter_y, shooter_width, shooter_height)

    glColor3f(1.0, 0.0, 0.0)
    for bullet in bullets:
        draw_circle(bullet["x"], bullet["y"], 5)

    glColor3f(0.0, 1.0, 0.0)
    for circle in falling_circles:
        draw_circle(circle["x"], circle["y"], circle_radius)

    if power_up_circle:
        draw_power_up(power_up_circle["x"], power_up_circle["y"], circle_radius)

    draw_left_arrow(20, HEIGHT - 40)
    draw_pause_play_icon(WIDTH // 2 - 5, HEIGHT - 40)
    draw_close_icon(WIDTH - 40, HEIGHT - 40)

    glutSwapBuffers()



def exit_game():
    print("Exiting game...")
    glutLeaveMainLoop()
    #sys.exit(0)



def mouse(button, state, x, y):
    global paused
    y = HEIGHT - y

    if state == GLUT_DOWN:
        if HEIGHT - 40 <= y <= HEIGHT:
            if x <= 60:
                print("Restarting Game!")
                restart_game()
            elif WIDTH // 2 - 20 <= x <= WIDTH // 2 + 20:
                paused = not paused
                print("Game Paused" if paused else "Game Resumed")
            elif x >= WIDTH - 60:
                print("Khatam tata bye bye!")
                exit_game()


# Restart game
def restart_game():
    global bullets, falling_circles, score, misses, consecutive_misses, paused, power_up_active, power_up_timer, power_up_circle
    bullets = []
    falling_circles = []
    score = 0
    misses = 0
    consecutive_misses = 0
    paused = False
    power_up_active = False
    power_up_timer = 0
    power_up_circle = None


def keyboard(key, x, y):
    global shooter_x, bullets

    if key == b'a' and shooter_x > 0:
        shooter_x -= 10
    elif key == b'd' and shooter_x + shooter_width < WIDTH:
        shooter_x += 10
    elif key == b' ':

        bullets.append({"x": shooter_x + shooter_width // 2, "y": shooter_y + shooter_height})
        print("Bullet fired!")

def update(value):
    global bullets, falling_circles, score, misses, consecutive_misses, power_up_active, power_up_timer, power_up_circle, paused

    if paused:
        glutTimerFunc(16, update, 0)
        return

    # Move bullets
    for bullet in bullets:
        bullet["y"] += bullet_speed
    bullets = [bullet for bullet in bullets if bullet["y"] < HEIGHT]

    # Move falling circles
    for circle in falling_circles:
        circle["y"] -= circle_speed
    falling_circles = [circle for circle in falling_circles if circle["y"] > 0]  # Remove off-screen circles

    # Add new falling circle
    if random.random() < 0.02:  # Probability of a new circle appearing
        falling_circles.append({
            "x": random.randint(circle_radius, WIDTH - circle_radius),
            "y": HEIGHT - circle_radius
        })

    # Check for collisions
    global_collided = False
    for bullet in bullets[:]:
        for circle in falling_circles[:]:
            bullet_aabb = {"x": bullet["x"] - 5, "y": bullet["y"] - 5, "width": 10, "height": 10}
            circle_aabb = {"x": circle["x"] - circle_radius, "y": circle["y"] - circle_radius, "width": 2 * circle_radius, "height": 2 * circle_radius}
            if has_collided(bullet_aabb, circle_aabb):
                bullets.remove(bullet)
                falling_circles.remove(circle)
                score += 1
                consecutive_misses = 0
                print(f"Score: {score}")
                break

    # Check for missed circles
    for circle in falling_circles[:]:
        if circle["y"] - circle_radius <= shooter_y:
            global_collided = True
            falling_circles.remove(circle)
            consecutive_misses += 1
            print(f"Missed! Consecutive misses: {consecutive_misses} \n Score: {score}")
            break

    # Check for game over if a circle collides with the shooter
    for circle in falling_circles[:]:
        circle_aabb = {"x": circle["x"] - circle_radius, "y": circle["y"] - circle_radius, "width": 2 * circle_radius, "height": 2 * circle_radius}
        shooter_aabb = {"x": shooter_x, "y": shooter_y, "width": shooter_width, "height": shooter_height}
        if has_collided(circle_aabb, shooter_aabb):
            print(f"Game Over! A circle collided with the rocket. \n Score: {score}")
            restart_game()
            return

    # Check for game over condition (consecutive misses)
    if consecutive_misses >= 3:
        print(f"Game Over! Too many missed circles. \n Score: {score}")
        restart_game()
        return

    # Power-up logic
    if power_up_active:
        power_up_timer += 1
        if power_up_timer >= power_up_duration:
            power_up_active = False
            power_up_circle = None
            print("Power-up expired!")

    # Move the power-up circle if it exists
    if power_up_circle:
        power_up_circle["y"] -= circle_speed
        if power_up_circle["y"] < 0:  # Remove off-screen power-up
            power_up_circle = None

    # Generate a new power-up circle
    if not power_up_active and not power_up_circle and random.random() < 0.005:
        power_up_circle = {
            "x": random.randint(circle_radius, WIDTH - circle_radius),
            "y": HEIGHT - circle_radius
        }

    # Check for power-up collision
    if power_up_circle:
        power_up_aabb = {"x": power_up_circle["x"] - circle_radius, "y": power_up_circle["y"] - circle_radius, "width": 2 * circle_radius, "height": 2 * circle_radius}
        shooter_aabb = {"x": shooter_x, "y": shooter_y, "width": shooter_width, "height": shooter_height}
        if has_collided(power_up_aabb, shooter_aabb):
            power_up_active = True
            power_up_timer = 0
            score += 5  # Increase score by 5
            power_up_circle = None
            print("Power-up collected! +5 points")

    glutPostRedisplay()  # Trigger a display callback
    glutTimerFunc(16, update, 0)  # Continue updating at ~60 FPS


# Initialize game window
def init():
    glClearColor(0.0, 0.0, 0.0, 0.0)  # Black background
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, WIDTH, 0, HEIGHT)

# Main function
def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(WIDTH, HEIGHT)
    glutCreateWindow(b"Rocket Shooter Game")
    init()
    glutDisplayFunc(display)
    glutKeyboardFunc(keyboard)
    glutMouseFunc(mouse)
    glutTimerFunc(16, update, 0)
    glutMainLoop()

if __name__ == "__main__":
    main()
