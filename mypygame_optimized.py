# math_tiles_full.py
import pygame
import random
import json
from pathlib import Path

# Path
SAVE_PATH = Path(__file__).parent / "savegame.json"

SCREEN_W, SCREEN_H = 800, 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
TEAL = (30, 200, 180)
DARK = (20, 20, 20)
GREEN = (60, 200, 60)
RED = (200, 50, 50)
YELLOW = (230, 200, 40)
GRAY = (160, 160, 160)
PANEL_BG = (18, 18, 18)

# Gameplay tuning
BASE_FALL_SPEED = 60
SPEED_PER_SCORE = 3
SPAWN_INTERVAL_BASE = 2.0
SPAWN_INTERVAL_MIN = 0.5
SPAWN_ACCEL_PER_SCORE = 0.03

# Item costs
COST_SKIP = 8
COST_SHIELD = 15

# Save/load
def load_save():
    if not SAVE_PATH.exists():
        return {"high_score": 0, "coins": 0, "items": {"skip": 0, "shield": 0}}
    try:
        with open(SAVE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        data.setdefault("high_score", 0)
        data.setdefault("coins", 0)
        data.setdefault("items", {"skip": 0, "shield": 0})
        return data
    except Exception:
        return {"high_score": 0, "coins": 0, "items": {"skip": 0, "shield": 0}}

def save_game(data):
    try:
        with open(SAVE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print("Save failed:", e)

# Problem generator
def generate_problem():
    op = random.choice(['+', '-', '*', '/'])
    a = random.randint(1, 12)
    b = random.randint(1, 12)
    if op == '/':
        b = random.randint(1, 12)
        a = b * random.randint(1, 6)
        answer = a // b
        display = f"{a} ÷ {b}"
    elif op == '+':
        answer = a + b
        display = f"{a} + {b}"
    elif op == '-':
        answer = a - b
        display = f"{a} - {b}"
    else:
        answer = a * b
        display = f"{a} × {b}"
    return display, answer

def make_choices(correct):
    choices = {correct}
    while len(choices) < 3:
        delta = random.randint(-10, 10)
        candidate = correct + delta
        if candidate != correct and -100 <= candidate <= 100:
            choices.add(candidate)
    choices = list(choices)
    random.shuffle(choices)
    return choices

# tile Classes
class ProblemTile:
    def __init__(self, x, y, problem_str, answer, fall_speed):
        self.x = x
        self.y = y
        self.problem = problem_str
        self.answer = answer
        self.width = 300
        self.height = 70
        self.fall_speed = fall_speed
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.choices = make_choices(answer)

    def update(self, dt):
        self.y += self.fall_speed * dt
        self.rect.y = int(self.y)

    def draw(self, surf, font):
        pygame.draw.rect(surf, TEAL, self.rect, border_radius=8)
        txt = font.render(self.problem, True, DARK)
        surf.blit(txt, (self.rect.x + 12, self.rect.y + (self.height - txt.get_height()) // 2))
        pygame.draw.rect(surf, BLACK, self.rect, 2, border_radius=8)

# Draw fnc
def draw_right_panel(surface, font_big, answer_buttons):
    panel_w = 200
    panel_rect = pygame.Rect(SCREEN_W - panel_w - 20, 60, panel_w, SCREEN_H - 140)
    pygame.draw.rect(surface, PANEL_BG, panel_rect, border_radius=12)
    pygame.draw.rect(surface, (40, 40, 40), panel_rect, 3, border_radius=12)
    for rect, val in answer_buttons:
        pygame.draw.rect(surface, GREEN, rect, border_radius=10)
        txt = font_big.render(str(val), True, DARK)
        surface.blit(txt, (rect.x + (rect.width - txt.get_width()) // 2,
                           rect.y + (rect.height - txt.get_height()) // 2))

def draw_hud(surface, font_small, score, coins, lives, high_score):
    surface.blit(font_small.render(f"Score: {score}", True, WHITE), (20, 10))
    surface.blit(font_small.render(f"Coins: {coins}", True, YELLOW), (20, 40))
    surface.blit(font_small.render(f"Lives: {lives}", True, RED), (180, 10))
    surface.blit(font_small.render(f"High: {high_score}", True, GRAY), (180, 40))

def draw_shop(surface, font_small, player_items, player_coins):
    w, h = 800, 600
    rect = pygame.Rect((SCREEN_W - w) // 2, (SCREEN_H - h) // 2, w, h)
    overlay = pygame.Surface((SCREEN_W, SCREEN_H))
    overlay.fill((0,0,0))
    surface.blit(overlay, (0,0))
    pygame.draw.rect(surface, (30, 30, 30), rect, border_radius=12)
    pygame.draw.rect(surface, (80, 80, 80), rect, 2, border_radius=12)
    y = rect.y + 48
    surface.blit(font_small.render("SHOP - Buy Items", True, WHITE), (rect.x + 18, rect.y + 12))
    surface.blit(font_small.render(f"Skip (cost {COST_SKIP}) - You have: {player_items['skip']}", True, WHITE), (rect.x + 20, y))
    y += 46
    surface.blit(font_small.render(f"Shield (cost {COST_SHIELD}) - You have: {player_items['shield']}", True, WHITE), (rect.x + 20, y))
    y += 60
    surface.blit(font_small.render("Click item text to buy. Press S to close shop.", True, GRAY), (rect.x + 20, y))
    return rect

# Menu and Tutorial
def draw_menu(screen, font_title, font_button):
    screen.fill((100, 100, 100))
    title = font_title.render("Math Tiles", True, WHITE)
    screen.blit(title, (SCREEN_W//2 - title.get_width()//2, 110))

    buttons = {
        "Play": pygame.Rect(SCREEN_W//2 - 100, 300, 200, 60),
        "Tutorial": pygame.Rect(SCREEN_W//2 - 100, 390, 200, 60),
        "Quit": pygame.Rect(SCREEN_W//2 - 100, 480, 200, 60)
    }
    pygame.draw.rect(screen, GREEN, buttons["Play"], border_radius=12)
    pygame.draw.rect(screen, YELLOW, buttons["Tutorial"], border_radius=12)
    pygame.draw.rect(screen, RED, buttons["Quit"], border_radius=12)

    for label, rect in buttons.items():
        txt = font_button.render(label, True, WHITE)
        screen.blit(txt, (rect.centerx - txt.get_width()//2, rect.centery - txt.get_height()//2))

    return buttons

def draw_tutorial(screen, font_title, font_body):
    screen.fill(BLACK)
    title = font_title.render("How to Play Math Tiles", True, WHITE)
    screen.blit(title, (SCREEN_W//2 - title.get_width()//2, 30))

    lines = [
        "Solve falling math problems before they reach the bottom!",
        "Click the correct answer on the right panel.",
        "You start with 3 lives — lose one for each wrong or missed tile.",
        "Earn 1 coin for each correct answer.",
        "Press S to open the shop:",
        "  - Buy 'Skip' to remove the current problem.",
        "  - Buy 'Shield' to block one mistake.",
        "Controls:",
        "  S - Open/close shop",
        "  K - Use Skip item",
        "  ESC - Quit game",
        "Click 'Back' below to return to menu."
    ]
    y = 120
    for line in lines:
        txt = font_body.render(line, True, WHITE)
        screen.blit(txt, (60, y))
        y += 34

    back_btn = pygame.Rect(SCREEN_W//2 - 60, SCREEN_H - 60, 120, 45)
    pygame.draw.rect(screen, TEAL, back_btn, border_radius=10)
    txt = font_body.render("Back", True, BLACK)
    screen.blit(txt, (back_btn.centerx - txt.get_width()//2, back_btn.centery - txt.get_height()//2))
    return back_btn

# Main
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Math Tiles — Math Game")
    clock = pygame.time.Clock()

    font_title = pygame.font.SysFont("Comic Sans MS", 50, bold=True)
    font_menu_btn = pygame.font.SysFont("Comic Sans MS", 36, bold=True)
    font_big = pygame.font.SysFont("Comic Sans MS", 48)
    font_mid = pygame.font.SysFont("Comic Sans MS", 36)
    font_body = pygame.font.SysFont("Comic Sans MS", 22)
    font_small = pygame.font.SysFont("Comic Sans MS", 20)

    # Load save
    save_data = load_save()
    high_score = save_data.get("high_score", 0)
    coins = save_data.get("coins", 0)
    items = save_data.get("items", {"skip": 0, "shield": 0})

    # Game state
    state = "menu"  # "menu", "tutorial", "game"
    running = True

    # Gameplay const
    def make_game_state():
        tiles = []
        score = 0
        lives = 3
        spawn_timer = 0.0
        spawn_interval = SPAWN_INTERVAL_BASE
        game_over = False
        shop_open = False
        return tiles, score, lives, spawn_timer, spawn_interval, game_over, shop_open

    tiles, score, lives, spawn_timer, spawn_interval, game_over, shop_open = make_game_state()

    # answer buttons
    button_w, button_h = 160, 80
    right_x = SCREEN_W - button_w - 40
    btn_y_positions = [140, 260, 380]
    answer_buttons = [(pygame.Rect(right_x, y, button_w, button_h), "-") for y in btn_y_positions]

    def get_active_tile():
        return tiles[0] if tiles else None

    def spawn_tile():
        fall_speed = BASE_FALL_SPEED + score * SPEED_PER_SCORE
        x = 40
        y = -80
        pstr, ans = generate_problem()
        tiles.append(ProblemTile(x, y, pstr, ans, fall_speed))

    # Start with one tile when game begins
    menu_buttons = {}
    tutorial_back = None

    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # save and exit
                save_data["high_score"] = max(high_score, score, save_data.get("high_score", 0))
                save_data["coins"] = coins
                save_data["items"] = items
                save_game(save_data)
                running = False

            elif event.type == pygame.KEYDOWN:
                if state == "game":
                    if event.key == pygame.K_s:
                        shop_open = not shop_open
                    if event.key == pygame.K_ESCAPE:
                        # save and exit from game
                        save_data["high_score"] = max(high_score, score, save_data.get("high_score", 0))
                        save_data["coins"] = coins
                        save_data["items"] = items
                        save_game(save_data)
                        running = False
                else:
                    # global ESC to quit from menu/tutorial
                    if event.key == pygame.K_ESCAPE:
                        save_data["high_score"] = max(high_score, score, save_data.get("high_score", 0))
                        save_data["coins"] = coins
                        save_data["items"] = items
                        save_game(save_data)
                        running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos

                if state == "menu":
                    for name, rect in menu_buttons.items():
                        if rect.collidepoint(mx, my):
                            if name == "Play":
                                state = "game"
                                tiles, score, lives, spawn_timer, spawn_interval, game_over, shop_open = make_game_state()
                                spawn_tile()
                            elif name == "Tutorial":
                                state = "tutorial"
                            elif name == "Quit":
                                save_data["high_score"] = max(high_score, score, save_data.get("high_score", 0))
                                save_data["coins"] = coins
                                save_data["items"] = items
                                save_game(save_data)
                                running = False

                elif state == "tutorial":
                    if tutorial_back and tutorial_back.collidepoint(mx, my):
                        state = "menu"

                elif state == "game":
                    if game_over:
                        # click anywhere to restart
                        tiles, score, lives, spawn_timer, spawn_interval, game_over, shop_open = make_game_state()
                        spawn_tile()
                        continue

                    if shop_open:
                        # shop click areas
                        w, h = 700, 320
                        rect = pygame.Rect((SCREEN_W - w) // 2, (SCREEN_H - h) // 2, w, h)
                        skip_area = pygame.Rect(20, 48, 380, 34)
                        shield_area = pygame.Rect(20, 94, 380, 34)
                        if skip_area.collidepoint(mx, my):
                            if coins >= COST_SKIP:
                                coins -= COST_SKIP
                                items["skip"] = items.get("skip", 0) + 1
                        elif shield_area.collidepoint(mx, my):
                            if coins >= COST_SHIELD:
                                coins -= COST_SHIELD
                                items["shield"] = items.get("shield", 0) + 1
                        continue

                    # check ans buttons
                    for rect, val in answer_buttons:
                        if rect.collidepoint(mx, my):
                            active = get_active_tile()
                            if not active:
                                break
                            if val == active.answer:
                                score += 1
                                coins += 1
                                if tiles:
                                    tiles.pop(0)
                                spawn_interval = max(SPAWN_INTERVAL_MIN,
                                                     SPAWN_INTERVAL_BASE - score * SPAWN_ACCEL_PER_SCORE)
                            else:
                                if items.get("shield", 0) > 0:
                                    items["shield"] -= 1
                                else:
                                    lives -= 1
                                    if lives <= 0:
                                        game_over = True
                                        if score > high_score:
                                            high_score = score
                                        save_data["high_score"] = max(high_score, save_data.get("high_score", 0))
                                        save_data["coins"] = coins
                                        save_data["items"] = items
                                        save_game(save_data)
                            break

                    # skip/shield buttons top-right
                    skip_btn = pygame.Rect(SCREEN_W - 140, 10, 120, 34)
                    shield_btn = pygame.Rect(SCREEN_W - 280, 10, 120, 34)
                    if skip_btn.collidepoint(mx, my):
                        if items.get("skip", 0) > 0 and tiles:
                            items["skip"] -= 1
                            tiles.pop(0)

        # --- Game update ---
        if state == "game" and not game_over and not shop_open:
            spawn_timer += dt
            if spawn_timer >= spawn_interval:
                spawn_timer = 0
                spawn_tile()

            for t in tiles:
                t.fall_speed = BASE_FALL_SPEED + score * SPEED_PER_SCORE
                t.update(dt)

        # Missed tile
        if state == "game" and tiles and tiles[0].y > SCREEN_H:
            tiles.pop(0)
            if items.get("shield", 0) > 0:
                items["shield"] -= 1
            else:
                lives -= 1
                if lives <= 0:
                    game_over = True
                    if score > high_score:
                        high_score = score
                    save_data["high_score"] = max(high_score, save_data.get("high_score", 0))
                    save_data["coins"] = coins
                    save_data["items"] = items
                    save_game(save_data)

        # Update right panel choices
        active = get_active_tile()
        if active:
            for i, (rect, _) in enumerate(answer_buttons):
                answer_buttons[i] = (rect, active.choices[i])
        else:
            for i, (rect, _) in enumerate(answer_buttons):
                answer_buttons[i] = (rect, "-")

        # --- Draw ---
        if state == "menu":
            menu_buttons = draw_menu(screen, font_title, font_menu_btn)

        elif state == "tutorial":
            tutorial_back = draw_tutorial(screen, font_title, font_body)

        elif state == "game":
            screen.fill((12, 12, 20))
            pygame.draw.rect(screen, (63, 63, 80), (20, 80, SCREEN_W - 260, SCREEN_H - 140), border_radius=10)

            # draw tiles
            for t in tiles:
                t.draw(screen, font_mid)

            # draw right panel
            draw_right_panel(screen, font_big, answer_buttons)

            # HUD
            draw_hud(screen, font_small, score, coins, lives, high_score)

            # quick item
            skip_btn = pygame.Rect(SCREEN_W - 140, 10, 120, 34)
            pygame.draw.rect(screen, (70,70,70), skip_btn, border_radius=8)
            skip_label = font_small.render(f"Skip x{items.get('skip',0)}", True, WHITE)
            screen.blit(skip_label, (skip_btn.x + 20, skip_btn.y + 0))

            shield_btn = pygame.Rect(SCREEN_W - 280, 10, 120, 34)
            pygame.draw.rect(screen, (70,70,70), shield_btn, border_radius=8)
            shield_label = font_small.render(f"Shield x{items.get('shield',0)}", True, WHITE)
            screen.blit(shield_label, (shield_btn.x + 10, shield_btn.y + 0))

            shop_hint = font_small.render("Press S to open Shop", True, GRAY)
            screen.blit(shop_hint, (SCREEN_W - 220, 52))

            if shop_open:
                draw_shop(screen, font_small, items, coins)

            if game_over:
                go_rect = pygame.Rect(80, 120, SCREEN_W - 160, SCREEN_H - 240)
                pygame.draw.rect(screen, (20,20,20), go_rect, border_radius=12)
                pygame.draw.rect(screen, (150,150,150), go_rect, 2, border_radius=12)
                title = font_big.render("GAME OVER", True, RED)
                screen.blit(title, (go_rect.x + (go_rect.width - title.get_width()) // 2, go_rect.y + 30))
                sc = font_mid.render(f"Score: {score}", True, WHITE)
                screen.blit(sc, (go_rect.x + (go_rect.width - sc.get_width()) // 2, go_rect.y + 120))
                hi = font_mid.render(f"High Score: {high_score}", True, GRAY)
                screen.blit(hi, (go_rect.x + (go_rect.width - hi.get_width()) // 2, go_rect.y + 160))
                inst = font_small.render("Click anywhere to restart", True, GRAY)
                screen.blit(inst, (go_rect.x + (go_rect.width - inst.get_width()) // 2, go_rect.y + 220))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()

