import pygame
import random
import sys
import time

# Initialize pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 900, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Environmental Protection Game - Waste Sorting")

# Color definitions
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLUE = (0, 120, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
BROWN = (165, 42, 42)
GRAY = (128, 128, 128)
LIGHT_BLUE = (173, 216, 230)
LIGHT_GREEN = (144, 238, 144)

# Waste types and colors
WASTE_TYPES = {
    "Recyclable": {
        "color": BLUE,
        "items": [
            {"name": "Plastic Bottle"},
            {"name": "Newspaper"},
            {"name": "Glass Bottle"},
            {"name": "Can"},
            {"name": "Cardboard"}
        ]
    },
    "Hazardous": {
        "color": RED,
        "items": [
            {"name": "Battery"},
            {"name": "Medicine"},
            {"name": "Light Bulb"},
            {"name": "Paint Can"},
            {"name": "Thermometer"}
        ]
    },
    "Kitchen Waste": {
        "color": BROWN,
        "items": [
            {"name": "Leftover Food"},
            {"name": "Fruit Peel"},
            {"name": "Vegetable Leaves"},
            {"name": "Egg Shell"},
            {"name": "Tea Leaves"}
        ]
    },
    "Other Waste": {
        "color": GRAY,
        "items": [
            {"name": "Tissue"},
            {"name": "Ceramic"},
            {"name": "Diaper"},
            {"name": "Cigarette Butt"},
            {"name": "Broken Bowl"}
        ]
    }
}

# Bin settings
BIN_WIDTH = 160
BIN_HEIGHT = 180
bins = []
bin_spacing = 20
start_x = (WIDTH - (len(WASTE_TYPES) * (BIN_WIDTH + bin_spacing))) // 2

for i, (waste_type, info) in enumerate(WASTE_TYPES.items()):
    bins.append({
        "type": waste_type,
        "rect": pygame.Rect(start_x + i * (BIN_WIDTH + bin_spacing), HEIGHT - 220, BIN_WIDTH, BIN_HEIGHT),
        "color": info["color"]
    })


# Waste item class
class WasteItem:
    def __init__(self):
        self.type = random.choice(list(WASTE_TYPES.keys()))
        item_data = random.choice(WASTE_TYPES[self.type]["items"])
        self.name = item_data["name"]
        self.width = 90
        self.height = 110
        self.x = random.randint(50, WIDTH - 50)
        self.y = -80
        self.speed = random.uniform(2, 4)
        self.dragging = False

    def draw(self):
        # Draw waste item background
        color = WASTE_TYPES[self.type]["color"]
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height), 0, 15)

        # Draw border
        pygame.draw.rect(screen, BLACK, (self.x, self.y, self.width, self.height), 2, 15)

        # Draw waste name
        font_name = pygame.font.SysFont("arial", 16, bold=True)
        name_text = font_name.render(self.name, True, WHITE)
        name_rect = name_text.get_rect(center=(self.x + self.width // 2, self.y + 30))
        screen.blit(name_text, name_rect)

        # Draw waste type
        font_type = pygame.font.SysFont("arial", 14)
        type_text = font_type.render(self.type, True, YELLOW)
        type_rect = type_text.get_rect(center=(self.x + self.width // 2, self.y + 60))
        screen.blit(type_text, type_rect)

        # Draw instruction text
        font_instruction = pygame.font.SysFont("arial", 12)
        instruction_text = font_instruction.render("Drag to bin", True, WHITE)
        instruction_rect = instruction_text.get_rect(center=(self.x + self.width // 2, self.y + 85))
        screen.blit(instruction_text, instruction_rect)

    def update(self):
        if not self.dragging:
            self.y += self.speed

    def check_collision(self, mouse_pos):
        return (self.x <= mouse_pos[0] <= self.x + self.width and
                self.y <= mouse_pos[1] <= self.y + self.height)

    def check_bin_collision(self):
        for bin in bins:
            if (bin["rect"].colliderect(pygame.Rect(self.x, self.y, self.width, self.height)) and
                    bin["type"] == self.type):
                return True
        return False


# Game state
score = 0
lives = 3
waste_items = []
spawn_timer = 0
spawn_delay = 60  # frames
game_over = False
font = pygame.font.SysFont(None, 36)

# Create initial waste items
for _ in range(3):
    waste_items.append(WasteItem())

# Game main loop
clock = pygame.time.Clock()
current_waste = None

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if not game_over:
            if event.type == pygame.MOUSEBUTTONDOWN:
                for waste in waste_items:
                    if waste.check_collision(event.pos):
                        waste.dragging = True
                        current_waste = waste
                        break

            elif event.type == pygame.MOUSEBUTTONUP:
                if current_waste:
                    current_waste.dragging = False
                    if current_waste.check_bin_collision():
                        score += 10
                        waste_items.remove(current_waste)
                        # Add new waste item
                        waste_items.append(WasteItem())
                    else:
                        # Wrong bin, waste goes back to top
                        current_waste.x = random.randint(50, WIDTH - 50)
                        current_waste.y = -80
                        lives -= 1
                        if lives <= 0:
                            game_over = True
                    current_waste = None

            elif event.type == pygame.MOUSEMOTION:
                if current_waste and current_waste.dragging:
                    current_waste.x = event.pos[0] - current_waste.width // 2
                    current_waste.y = event.pos[1] - current_waste.height // 2
        else:
            # Game over, click to restart
            if event.type == pygame.MOUSEBUTTONDOWN:
                score = 0
                lives = 3
                waste_items = []
                for _ in range(3):
                    waste_items.append(WasteItem())
                game_over = False

    # Update game state
    if not game_over:
        # Spawn new waste
        spawn_timer += 1
        if spawn_timer >= spawn_delay and len(waste_items) < 8:
            waste_items.append(WasteItem())
            spawn_timer = 0

        # Update waste positions
        for waste in waste_items[:]:
            if not waste.dragging:
                waste.update()
                # Check if waste reached bottom
                if waste.y > HEIGHT:
                    waste_items.remove(waste)
                    lives -= 1
                    if lives <= 0:
                        game_over = True
                    waste_items.append(WasteItem())

    # Draw background
    screen.fill(LIGHT_GREEN)

    # Draw title
    title_font = pygame.font.SysFont("arial", 48, bold=True)
    title = title_font.render("Waste Sorting Game", True, BLUE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 20))

    subtitle_font = pygame.font.SysFont("arial", 24)
    subtitle = subtitle_font.render("Environmental Protection Challenge", True, GREEN)
    screen.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, 75))

    # Draw bins
    for bin in bins:
        # Draw bin body
        pygame.draw.rect(screen, bin["color"], bin["rect"], 0, 10)

        # Draw bin border
        pygame.draw.rect(screen, BLACK, bin["rect"], 2, 10)

        # Draw bin label
        bin_font = pygame.font.SysFont("arial", 20, bold=True)
        bin_text = bin_font.render(bin["type"], True, WHITE)
        bin_text_rect = bin_text.get_rect(center=(bin["rect"].x + BIN_WIDTH // 2, bin["rect"].y + 40))
        screen.blit(bin_text, bin_text_rect)

        # Draw bin instruction
        bin_instruction_font = pygame.font.SysFont("arial", 14)
        bin_instruction = bin_instruction_font.render("Drop here", True, YELLOW)
        bin_instruction_rect = bin_instruction.get_rect(center=(bin["rect"].x + BIN_WIDTH // 2, bin["rect"].y + 70))
        screen.blit(bin_instruction, bin_instruction_rect)

    # Draw waste items
    for waste in waste_items:
        waste.draw()

    # Draw score and lives
    score_text = font.render(f"Score: {score}", True, BLACK)
    lives_text = font.render(f"Lives: {lives}", True, BLACK)
    screen.blit(score_text, (20, 20))
    screen.blit(lives_text, (WIDTH - 120, 20))

    # Draw game instructions
    instruction_font = pygame.font.SysFont("arial", 24)
    instruction = instruction_font.render("Drag waste items to the correct bins!", True, BLACK)
    screen.blit(instruction, (WIDTH // 2 - instruction.get_width() // 2, 130))

    # Draw scoring info
    info_font = pygame.font.SysFont("arial", 18)
    info_text = info_font.render("Correct: +10 points | Wrong: -1 life | Missed: -1 life", True, RED)
    screen.blit(info_text, (WIDTH // 2 - info_text.get_width() // 2, 160))

    # Game over screen
    if game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))

        game_over_font = pygame.font.SysFont("arial", 72, bold=True)
        game_over_text = game_over_font.render("GAME OVER", True, RED)
        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 50))

        final_score_font = pygame.font.SysFont("arial", 48)
        final_score_text = final_score_font.render(f"Final Score: {score}", True, WHITE)
        screen.blit(final_score_text, (WIDTH // 2 - final_score_text.get_width() // 2, HEIGHT // 2 + 30))

        restart_font = pygame.font.SysFont("arial", 36)
        restart_text = restart_font.render("Click anywhere to restart", True, YELLOW)
        screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 100))

    pygame.display.flip()
    clock.tick(60)
