import pygame
import pygame.gfxdraw
import secrets
import sys
import hashlib
import numpy as np
import pygame.surfarray
import pyperclip
import threading
import time

# Password generation thread
# This function runs in the background and updates the password every second
def password_updater(get_surface, update_password):
    time.sleep(2)  # Wait 2 seconds before starting
    while True:
        screenshot = get_surface()
        pixels = pygame.surfarray.array3d(screenshot)
        flat_pixels = pixels.flatten()
        np.random.shuffle(flat_pixels)
        hash_object = hashlib.sha256()
        hash_object.update(flat_pixels.tobytes())
        update_password(hash_object.hexdigest())
        time.sleep(1)  # Update every second

# Creates a new circle with random properties
def create_circle(screen_width, screen_height):
    x = secrets.randbelow(screen_width - 200) + 100
    y = secrets.randbelow(screen_height - 200) + 100
    radius = secrets.randbelow(71) + 80
    color = [secrets.randbelow(255) + 1 for _ in range(3)]
    lifetime = secrets.randbelow(400) + 1000
    return {
        'x': x,
        'y': y,
        'radius': radius,
        'color': color,
        'created_at': pygame.time.get_ticks(),
        'lifetime': lifetime
    }

def main():
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    screen_width, screen_height = screen.get_size()
    clock = pygame.time.Clock()

    font = pygame.font.SysFont(None, 28)
    password = ""
    copy_message = ""
    copy_message_time = 0
    button_clicked = False

    # Button settings
    copy_button_rect = pygame.Rect(screen_width - 180, screen_height - 150, 150, 40)
    default_button_color = (255, 255, 255)
    clicked_button_color = (0, 200, 0)

    # Circle settings (based on screen resolution)
    circle_interval = 3  # Time between new circle generation (in ms)
    max_circles = max(100, (screen_width * screen_height) // 3000)  # Max circles allowed at once
    circles = []
    last_circle_time = pygame.time.get_ticks()

    # Functions for password updating
    def get_surface():
        return screen.copy()

    def update_password(new_pass):
        nonlocal password
        password = new_pass

    # Start the password update thread
    threading.Thread(target=password_updater, args=(get_surface, update_password), daemon=True).start()

    # Create the "Press ESC to quit" message once
    quit_message = "Press ESC to quit"
    quit_text = font.render(quit_message, True, (255, 255, 255))
    
    running = True
    while running:
        now = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if copy_button_rect.collidepoint(event.pos):
                    pyperclip.copy(password)
                    copy_message = "Password copied to clipboard!"
                    copy_message_time = now
                    button_clicked = True

        # Generate a new circle if enough time has passed and limit not reached
        if now - last_circle_time >= circle_interval and len(circles) < max_circles:
            circles.append(create_circle(screen_width, screen_height))
            last_circle_time = now

        # Draw background
        screen.fill((0, 0, 0))

        # Draw all existing circles
        for circle in circles[:]:
            age = now - circle['created_at']
            if age >= circle['lifetime']:
                circles.remove(circle)  # Remove expired circle
                continue
            fade = age / circle['lifetime']
            faded_color = [max(0, int(c * (1 - fade))) for c in circle['color']]
            pygame.gfxdraw.aacircle(screen, circle['x'], circle['y'], circle['radius'], faded_color)

        # Display password in bottom-right corner
        if password:
            text = font.render(password, True, (255, 255, 255))
            screen.blit(text, (screen_width - text.get_width() - 10, screen_height - text.get_height() - 60))

        # Show copy confirmation message in center (visible for 1 second)
        if copy_message and now - copy_message_time <= 1000:
            msg_text = font.render(copy_message, True, (0, 255, 0))
            msg_x = (screen_width - msg_text.get_width()) // 2
            msg_y = screen_height // 2 + 100
            screen.blit(msg_text, (msg_x, msg_y))
        else:
            button_clicked = False

        # Draw the "Copy" button
        pygame.draw.rect(
            screen,
            clicked_button_color if button_clicked else default_button_color,
            copy_button_rect,
            border_radius=8
        )
        screen.blit(font.render("Copy", True, (0, 0, 0)), (copy_button_rect.x + 30, copy_button_rect.y + 8))

        # Always draw the "Press ESC to quit" message in the bottom-left corner
        screen.blit(quit_text, (10, screen_height - quit_text.get_height() - 10))  # Bottom-left corner

        pygame.display.flip()
        clock.tick(120)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
