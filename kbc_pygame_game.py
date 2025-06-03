import pygame
import sys
import random
import time
import os

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
DARK_BLUE = (0, 0, 128)
GOLD = (255, 215, 0)
WHITE = (255, 255, 255)
LIGHT_BLUE = (0, 102, 204)
RED = (204, 0, 0)
GREEN = (0, 153, 0)
PURPLE = (128, 0, 128)

# Fonts
TITLE_FONT = pygame.font.SysFont("Arial", 48, bold=True)
LARGE_FONT = pygame.font.SysFont("Arial", 32, bold=True)
MEDIUM_FONT = pygame.font.SysFont("Arial", 24)
SMALL_FONT = pygame.font.SysFont("Arial", 20)

# Paths for assets
ASSETS_DIR = "assets"
if not os.path.exists(ASSETS_DIR):
    os.makedirs(ASSETS_DIR)

# Paths for images
LOGO_PATH = os.path.join(ASSETS_DIR, "logo.png")
BACKGROUND_PATH = os.path.join(ASSETS_DIR, "background.jpg")

# Paths for sounds
MAIN_THEME_PATH = os.path.join(ASSETS_DIR, "main_theme.mp3")
TICK_TOCK_PATH = os.path.join(ASSETS_DIR, "tick_tock.mp3")
CORRECT_ANSWER_PATH = os.path.join(ASSETS_DIR, "correct_answer.mp3")
WRONG_ANSWER_PATH = os.path.join(ASSETS_DIR, "wrong_answer.mp3")
WIN_SOUND_PATH = os.path.join(ASSETS_DIR, "win_sound.mp3")
LOSE_SOUND_PATH = os.path.join(ASSETS_DIR, "lose_sound.mp3")

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, text_color=WHITE, font=MEDIUM_FONT):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font = font
        self.is_hovered = False
        self.pulse = 0
        self.pulse_dir = 1
        
    def draw(self, screen):
        # Base color based on hover state
        color = self.hover_color if self.is_hovered else self.color
        
        # Create a more interesting button shape
        # Draw a rounded rectangle with a gradient effect
        for i in range(5, 0, -1):
            # Create a slightly darker shade for 3D effect
            shade = (max(0, color[0] - i*10), max(0, color[1] - i*10), max(0, color[2] - i*10))
            rect = pygame.Rect(self.rect.x, self.rect.y + i, self.rect.width, self.rect.height - i)
            pygame.draw.rect(screen, shade, rect, border_radius=15)
        
        # Main button surface
        pygame.draw.rect(screen, color, self.rect, border_radius=15)
        
        # Add a glossy highlight effect
        highlight_rect = pygame.Rect(self.rect.x + 5, self.rect.y + 5, 
                                    self.rect.width - 10, self.rect.height // 3)
        highlight_color = (min(255, color[0] + 40), min(255, color[1] + 40), min(255, color[2] + 40), 100)
        pygame.draw.rect(screen, highlight_color, highlight_rect, border_radius=10)
        
        # Add pulsing border effect when hovered
        if self.is_hovered:
            self.pulse += 0.1 * self.pulse_dir
            if self.pulse > 1.0:
                self.pulse = 1.0
                self.pulse_dir = -1
            elif self.pulse < 0.3:
                self.pulse = 0.3
                self.pulse_dir = 1
                
            border_color = (255, 255, 255, int(self.pulse * 255))
            pygame.draw.rect(screen, border_color, self.rect, 3, border_radius=15)
        else:
            # Regular border
            pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=15)
        
        # Text with slight shadow for better readability
        shadow_surface = self.font.render(self.text, True, (0, 0, 0))
        shadow_rect = shadow_surface.get_rect(center=(self.rect.centerx + 2, self.rect.centery + 2))
        screen.blit(shadow_surface, shadow_rect)
        
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        return self.is_hovered
        
    def is_clicked(self, mouse_pos, mouse_click):
        return self.rect.collidepoint(mouse_pos) and mouse_click

class KBCGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Kaun Banega Crorepati")
        
        # Game states
        self.MAIN_MENU = 0
        self.GAME_SCREEN = 1
        self.RESULT_SCREEN = 2
        self.current_state = self.MAIN_MENU
        
        # Game variables
        self.questions = []
        self.current_question = 0
        self.selected_questions = []
        self.prize_money = [1000, 2000, 3000, 5000, 10000, 20000, 40000, 80000, 
                           160000, 320000, 640000, 1250000, 2500000, 5000000, 10000000]
        self.won_amount = 0
        self.game_won = False
        
        # Timer variables
        self.time_left = 30
        self.last_time_update = 0
        
        # Animation variables
        self.logo_scale = 0.1
        self.logo_alpha = 0
        self.logo_animation_done = False
        self.win_particles = []
        self.confetti_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), 
                               (255, 255, 0), (255, 0, 255), (0, 255, 255)]
        
        # Sound effects
        pygame.mixer.init()
        self.correct_sound = None
        self.wrong_sound = None
        self.win_sound = None
        self.lose_sound = None
        self.tick_sound = None
        
        # Try to load sounds
        try:
            if os.path.exists(CORRECT_ANSWER_PATH):
                self.correct_sound = pygame.mixer.Sound(CORRECT_ANSWER_PATH)
            if os.path.exists(WRONG_ANSWER_PATH):
                self.wrong_sound = pygame.mixer.Sound(WRONG_ANSWER_PATH)
            if os.path.exists(WIN_SOUND_PATH):
                self.win_sound = pygame.mixer.Sound(WIN_SOUND_PATH)
            if os.path.exists(LOSE_SOUND_PATH):
                self.lose_sound = pygame.mixer.Sound(LOSE_SOUND_PATH)
        except:
            print("Could not load some sound effects")
        
        # Load questions
        self.load_questions()
        
        # Create buttons for main menu
        self.start_button = Button(SCREEN_WIDTH//2 - 100, 300, 200, 60, "Start Game", LIGHT_BLUE, GREEN)
        self.exit_button = Button(SCREEN_WIDTH//2 - 100, 400, 200, 60, "Exit", RED, (255, 50, 50))
        
        # Create buttons for result screen
        self.play_again_button = Button(SCREEN_WIDTH//2 - 100, 350, 200, 60, "Play Again", LIGHT_BLUE, GREEN)
        self.exit_result_button = Button(SCREEN_WIDTH//2 - 100, 450, 200, 60, "Exit", RED, (255, 50, 50))
        
        # Create option buttons for game screen
        self.option_buttons = []
        option_letters = ['A', 'B', 'C', 'D']
        for i in range(2):
            for j in range(2):
                idx = i * 2 + j
                x = 100 + j * 300
                y = 350 + i * 100
                button = Button(x, y, 250, 70, f"{option_letters[idx]}. Option", LIGHT_BLUE, (100, 150, 255))
                self.option_buttons.append(button)
        
        # Try to load logo (placeholder)
        self.logo = None
        self.original_logo_size = (150, 150)  # Use a square size
        try:
            if os.path.exists(LOGO_PATH):
                self.logo = pygame.image.load(LOGO_PATH)
                self.logo = pygame.transform.smoothscale(self.logo, self.original_logo_size)
        except:
            print(f"Could not load logo from {LOGO_PATH}")
            
    def animate_logo(self):
        """Animate the logo entrance"""
        if not self.logo_animation_done:
            if self.logo_scale < 1.0:
                self.logo_scale += 0.05
            else:
                self.logo_scale = 1.0

            if self.logo_alpha < 255:
                self.logo_alpha += 10
            else:
                self.logo_alpha = 255
                self.logo_animation_done = True

            if self.logo:
                # Always scale to a square
                side = int(self.original_logo_size[0] * self.logo_scale)
                current_size = (side, side)
                scaled_logo = pygame.transform.smoothscale(self.logo, current_size)

                # Create a surface with alpha for fading in
                alpha_surface = pygame.Surface(scaled_logo.get_size(), pygame.SRCALPHA)
                alpha = max(0, min(255, int(self.logo_alpha)))
                alpha_surface.fill((255, 255, 255, alpha))
                scaled_logo.blit(alpha_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

                # Draw the logo
                logo_rect = scaled_logo.get_rect(center=(SCREEN_WIDTH//2, 120))
                self.screen.blit(scaled_logo, logo_rect)
            else:
                # Draw title text if no logo with animation
                title_text = TITLE_FONT.render("KAUN BANEGA CROREPATI", True, GOLD)
                title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 120))
                
                # Apply scaling and alpha
                scaled_text = pygame.transform.scale(title_text, 
                                                   (int(title_text.get_width() * self.logo_scale),
                                                    int(title_text.get_height() * self.logo_scale)))
                alpha_surface = pygame.Surface(scaled_text.get_size(), pygame.SRCALPHA)
                # Use RGBA format for fill
                alpha_surface.fill((255, 255, 255, int(self.logo_alpha)))
                scaled_text.blit(alpha_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                
                scaled_rect = scaled_text.get_rect(center=(SCREEN_WIDTH//2, 120))
                self.screen.blit(scaled_text, scaled_rect)
        else:
            # Draw the normal logo once animation is complete
            if self.logo:
                logo_rect = self.logo.get_rect(center=(SCREEN_WIDTH//2, 120))
                self.screen.blit(self.logo, logo_rect)
            else:
                title_text = TITLE_FONT.render("KAUN BANEGA CROREPATI", True, GOLD)
                title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 120))
                self.screen.blit(title_text, title_rect)
                
    def create_win_animation(self):
        """Create particles for win animation"""
        for _ in range(100):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            size = random.randint(5, 15)
            color = random.choice(self.confetti_colors)
            speed_x = random.uniform(-3, 3)
            speed_y = random.uniform(-8, -4)
            self.win_particles.append({
                'x': x, 'y': y, 'size': size, 'color': color,
                'speed_x': speed_x, 'speed_y': speed_y,
                'rotation': random.uniform(0, 360),
                'rot_speed': random.uniform(-5, 5)
            })
            
    def update_win_animation(self):
        """Update and draw win animation particles"""
        for particle in self.win_particles[:]:
            # Update position
            particle['y'] += particle['speed_y']
            particle['x'] += particle['speed_x']
            particle['speed_y'] += 0.1  # Gravity
            particle['rotation'] += particle['rot_speed']
            
            # Draw the particle (confetti)
            particle_surface = pygame.Surface((particle['size'], particle['size']), pygame.SRCALPHA)
            pygame.draw.rect(particle_surface, particle['color'], 
                           (0, 0, particle['size'], particle['size']))
            
            # Rotate the particle
            rotated_surface = pygame.transform.rotate(particle_surface, particle['rotation'])
            rotated_rect = rotated_surface.get_rect(center=(int(particle['x']), int(particle['y'])))
            self.screen.blit(rotated_surface, rotated_rect)
            
            # Remove particles that are off-screen
            if particle['y'] > SCREEN_HEIGHT + 50:
                self.win_particles.remove(particle)
    
    def load_questions(self):
        """Load questions from the text file."""
        try:
            with open('questions.txt', 'r') as file:
                for line in file:
                    line = line.strip()
                    if line:
                        parts = line.split('|')
                        if len(parts) == 6:
                            question = parts[0]
                            options = parts[1:5]
                            correct_answer = parts[5]
                            self.questions.append({
                                'question': question,
                                'options': options,
                                'correct': correct_answer
                            })
        except FileNotFoundError:
            print("Error: questions.txt file not found!")
            pygame.quit()
            sys.exit()
    
    def draw_text_wrapped(self, text, font, color, x, y, max_width):
        """Draw text that wraps within a given width."""
        words = text.split(' ')
        lines = []
        current_line = words[0]
        
        for word in words[1:]:
            test_line = current_line + ' ' + word
            test_width = font.size(test_line)[0]
            if test_width <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        
        lines.append(current_line)
        
        for i, line in enumerate(lines):
            text_surface = font.render(line, True, color)
            text_rect = text_surface.get_rect(center=(x, y + i * 30))
            self.screen.blit(text_surface, text_rect)
    
    def draw_main_menu(self):
        """Draw the main menu screen."""
        self.screen.fill(PURPLE)
        
        # Draw animated logo
        self.animate_logo()
        
        # Draw subtitle
        subtitle_text = MEDIUM_FONT.render("Test Your Knowledge!", True, WHITE)
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH//2, 200))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Draw buttons
        self.start_button.draw(self.screen)
        self.exit_button.draw(self.screen)
        
        # Draw footer
        footer_text = SMALL_FONT.render("© 2025 KBC Quiz Game", True, WHITE)
        footer_rect = footer_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 30))
        self.screen.blit(footer_text, footer_rect)
    
    def draw_game_screen(self):
        """Draw the game screen."""
        self.screen.fill(DARK_BLUE)
        
        # Draw timer
        timer_text = MEDIUM_FONT.render(f"Time: {self.time_left}", True, WHITE)
        self.screen.blit(timer_text, (20, 20))
        
        # Draw prize
        prize_text = MEDIUM_FONT.render(f"Prize: ₹{self.prize_money[self.current_question]:,}", True, WHITE)
        prize_rect = prize_text.get_rect(topright=(SCREEN_WIDTH - 20, 20))
        self.screen.blit(prize_text, prize_rect)
        
        # Draw question number
        question_num_text = MEDIUM_FONT.render(f"Question {self.current_question + 1}/15", True, GOLD)
        question_num_rect = question_num_text.get_rect(center=(SCREEN_WIDTH//2, 60))
        self.screen.blit(question_num_text, question_num_rect)
        
        # Draw question
        current_q = self.selected_questions[self.current_question]
        self.draw_text_wrapped(current_q['question'], MEDIUM_FONT, WHITE, SCREEN_WIDTH//2, 150, SCREEN_WIDTH - 100)
        
        # Draw option buttons
        option_letters = ['A', 'B', 'C', 'D']
        for i, button in enumerate(self.option_buttons):
            button.text = f"{option_letters[i]}. {current_q['options'][i]}"
            button.draw(self.screen)
    
    def draw_result_screen(self):
        """Draw the result screen."""
        self.screen.fill(DARK_BLUE)
        
        # Draw result title
        if self.game_won:
            title_text = LARGE_FONT.render("Congratulations!", True, GOLD)
            # Update and draw win animation
            if len(self.win_particles) == 0:
                self.create_win_animation()
            self.update_win_animation()
        else:
            title_text = LARGE_FONT.render("Game Over", True, GOLD)
        
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 120))
        self.screen.blit(title_text, title_rect)
        
        # Draw prize amount
        prize_text = MEDIUM_FONT.render(f"You won: ₹{self.won_amount:,}", True, WHITE)
        prize_rect = prize_text.get_rect(center=(SCREEN_WIDTH//2, 200))
        self.screen.blit(prize_text, prize_rect)
        
        # Draw message
        if self.game_won:
            msg_text = MEDIUM_FONT.render("You've reached the top prize!", True, WHITE)
        else:
            if self.won_amount > 0:
                msg_text = MEDIUM_FONT.render("Better luck next time!", True, WHITE)
            else:
                msg_text = MEDIUM_FONT.render("You didn't win any money this time.", True, WHITE)
        
        msg_rect = msg_text.get_rect(center=(SCREEN_WIDTH//2, 260))
        self.screen.blit(msg_text, msg_rect)
        
        # Draw buttons
        self.play_again_button.draw(self.screen)
        self.exit_result_button.draw(self.screen)
    
    def start_game(self):
        """Start a new game."""
        # Reset game variables
        self.current_question = 0
        self.won_amount = 0
        self.game_won = False
        self.time_left = 30
        self.last_time_update = pygame.time.get_ticks()
        self.win_particles = []
        
        # Select 15 random questions
        if len(self.questions) < 15:
            print("Error: Not enough questions in the database!")
            return
        
        self.selected_questions = random.sample(self.questions, 15)
        
        # Change state to game screen
        self.current_state = self.GAME_SCREEN
        
        # Play the tick-tock sound
        if os.path.exists(TICK_TOCK_PATH):
            pygame.mixer.music.load(TICK_TOCK_PATH)
            pygame.mixer.music.play(-1)  # Loop the sound
    
    def check_answer(self, selected_option):
        """Check if the selected answer is correct."""
        correct_option = self.selected_questions[self.current_question]['correct']
        
        if selected_option == correct_option:
            # Correct answer
            if self.correct_sound:
                self.correct_sound.play()
            
            # Update won amount
            self.won_amount = self.prize_money[self.current_question]
            
            # Move to next question
            self.current_question += 1
            
            if self.current_question >= 15:
                # Player won the game
                self.game_won = True
                if self.win_sound:
                    self.win_sound.play()
                pygame.mixer.music.stop()  # Stop the tick-tock sound
                self.current_state = self.RESULT_SCREEN
            else:
                # Reset timer for next question
                self.time_left = 30
                self.last_time_update = pygame.time.get_ticks()
        else:
            # Wrong answer
            if self.wrong_sound:
                self.wrong_sound.play()
            
            if self.lose_sound:
                self.lose_sound.play()
            
            pygame.mixer.music.stop()  # Stop the tick-tock sound
            
            # Game over, move to result screen
            self.current_state = self.RESULT_SCREEN
    
    def update_timer(self):
        """Update the timer."""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_time_update >= 1000:  # 1 second has passed
            self.time_left -= 1
            self.last_time_update = current_time
            
            if self.time_left <= 0:
                # Time's up
                if self.lose_sound:
                    self.lose_sound.play()
                pygame.mixer.music.stop()  # Stop the tick-tock sound
                self.current_state = self.RESULT_SCREEN
    
    def run(self):
        """Main game loop."""
        running = True
        clock = pygame.time.Clock()
        
        # Play the main theme
        if os.path.exists(MAIN_THEME_PATH):
            pygame.mixer.music.load(MAIN_THEME_PATH)
            pygame.mixer.music.play(-1)  # Loop the music
        
        # Reset logo animation
        self.logo_animation_done = False
        self.logo_scale = 0.1
        self.logo_alpha = 0
        
        while running:
            mouse_pos = pygame.mouse.get_pos()
            mouse_click = False
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left mouse button
                        mouse_click = True
            
            # Handle different game states
            if self.current_state == self.MAIN_MENU:
                # Main menu state
                self.draw_main_menu()
                
                # Check button interactions
                self.start_button.check_hover(mouse_pos)
                self.exit_button.check_hover(mouse_pos)
                
                if self.start_button.is_clicked(mouse_pos, mouse_click):
                    pygame.mixer.music.stop()  # Stop main theme
                    self.start_game()
                elif self.exit_button.is_clicked(mouse_pos, mouse_click):
                    running = False
            
            elif self.current_state == self.GAME_SCREEN:
                # Game screen state
                self.update_timer()
                self.draw_game_screen()
                
                # Check option button interactions
                option_letters = ['A', 'B', 'C', 'D']
                for i, button in enumerate(self.option_buttons):
                    button.check_hover(mouse_pos)
                    if button.is_clicked(mouse_pos, mouse_click):
                        self.check_answer(option_letters[i])
            
            elif self.current_state == self.RESULT_SCREEN:
                # Result screen state
                self.draw_result_screen()
                
                # Check button interactions
                self.play_again_button.check_hover(mouse_pos)
                self.exit_result_button.check_hover(mouse_pos)
                
                if self.play_again_button.is_clicked(mouse_pos, mouse_click):
                    # Reset logo animation for main menu
                    self.logo_animation_done = False
                    self.logo_scale = 0.1
                    self.logo_alpha = 0
                    
                    # Play main theme again
                    if os.path.exists(MAIN_THEME_PATH):
                        pygame.mixer.music.load(MAIN_THEME_PATH)
                        pygame.mixer.music.play(-1)
                        
                    self.current_state = self.MAIN_MENU
                elif self.exit_result_button.is_clicked(mouse_pos, mouse_click):
                    running = False
            
            pygame.display.flip()
            clock.tick(60)  # 60 FPS
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = KBCGame()
    game.run()
