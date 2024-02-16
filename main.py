import pygame
from random import randrange as rnd

WIDTH, HEIGHT = 1200, 800
fps = 60
paddle_w = 330
paddle_h = 35
paddle_speed = 30
paddle = pygame.Rect(WIDTH // 2 - paddle_w // 2, HEIGHT - paddle_h - 10, paddle_w, paddle_h)
ball_radius = 20
ball_speed = 8
ball_rect = int(ball_radius * 2 ** 0.5)
ball = pygame.Rect(rnd(ball_rect, WIDTH - ball_rect), HEIGHT // 2, ball_rect, ball_rect)
dx, dy = 1, -1
block_list = [pygame.Rect(10 + 120 * i, 10 + 70 * j, 100, 50) for i in range(10) for j in range(4)]
color_list = [(rnd(30, 256), rnd(30, 256), rnd(30, 256)) for i in range(10) for j in range(4)]

pygame.init()
pygame.mixer.init()

sc = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
img = pygame.image.load('background/background.jpg').convert()

pygame.mixer.music.load('music/music_game.mp3')
pygame.mixer.music.play(loops=-1)

level = 1

def draw_text(text, font_size, color, x, y):
    font = pygame.font.Font(None, font_size)
    text = font.render(text, True, color)
    text_rect = text.get_rect(center=(x, y))
    sc.blit(text, text_rect)

def start_game():
    sc.blit(img, (0, 0))
    draw_text("Pressione SPACE para iniciar o jogo", 36, pygame.Color('white'), WIDTH // 2, HEIGHT // 2)
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
        if pygame.key.get_pressed()[pygame.K_SPACE]:
            waiting = False

restart_requested = False

def end_game(win):
    global restart_requested, level

    sc.fill(pygame.Color('black'))
    if win:
        level = level + 1
        draw_text("Você Ganhou!", 48, pygame.Color('white'), WIDTH // 2, HEIGHT // 2)
        draw_text(f"Vamos para o nível: {level}", 26, pygame.Color('white'), WIDTH // 2, HEIGHT // 2 + 40)
        draw_text("Pressione R para ir para o próximo ou ESC para sair", 24, pygame.Color('white'), WIDTH // 2, HEIGHT // 2 + 70)
    else:
        pygame.mixer.music.stop()
        pygame.mixer.music.load('music/music_lose.mp3')
        pygame.mixer.music.play(loops=-1)
        level = 1
        draw_text("Você Perdeu!", 48, pygame.Color('white'), WIDTH // 2, HEIGHT // 2)
        draw_text(f"Voltando para o nível: {level}", 26, pygame.Color('white'), WIDTH // 2, HEIGHT // 2 + 40)
        draw_text("Pressione R para reiniciar ou ESC para sair", 24, pygame.Color('white'), WIDTH // 2, HEIGHT // 2 + 70)
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    restart_requested = True
                    return True
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()

        if restart_requested:
            return True

def detect_collision(dx, dy, ball, rect):

    if dx > 0:
        delta_x = ball.right - rect.left
    else:
        delta_x = rect.right - ball.left
    if dy > 0:
        delta_y = ball.bottom - rect.top
    else:
        delta_y = rect.bottom - ball.top

    if abs(delta_x - delta_y) < 10:
        dx, dy = -dx, -dy
    elif delta_x > delta_y:
        dy = -dy
    elif delta_y > delta_x:
        dx = -dx

    return dx, dy

def game_over():
    if ball.bottom > HEIGHT:
        return True
    elif not len(block_list):
        return True
    return False

def setup_game():
    global block_list, color_list, paddle, ball, dx, dy, level, paddle_h

    if(ball_radius/level >= 2):
        ball_radius = ball_radius / level
    else:
        ball_radius = 2

    if(ball_speed*level <= 14):
        ball_speed = ball_speed*level
    else:
        ball_speed = 14

    if(paddle_h/level >= 50):    
        paddle_h = 330 / level
    else:
        paddle_h = 50

    block_list = [pygame.Rect(10 + 120 * i, 10 + 70 * j, 100, 50) for i in range(10) for j in range(4)]
    color_list = [(rnd(30, 256), rnd(30, 256), rnd(30, 256)) for i in range(10) for j in range(4)]
    paddle = pygame.Rect(WIDTH // 2 - paddle_w // 2, HEIGHT - paddle_h - 10, paddle_w, paddle_h)
    ball = pygame.Rect(rnd(ball_rect, WIDTH - ball_rect), HEIGHT // 2, ball_rect, ball_rect)
    dx, dy = 1, -1

def main():
    global restart_requested, level
    dx, dy = 1, -1 
    start_game()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        if restart_requested:
            restart_requested = False
            pygame.mixer.music.stop()
            pygame.mixer.music.load('music/music_game.mp3')
            pygame.mixer.music.play(loops=-1)
            setup_game()
            start_game()
            main()
            continue

        sc.blit(img, (0, 0))

        [pygame.draw.rect(sc, color_list[color], block) for color, block in enumerate(block_list)]
        pygame.draw.rect(sc, pygame.Color('darkorange'), paddle)
        pygame.draw.circle(sc, pygame.Color('white'), ball.center, ball_radius)

        ball.x += ball_speed * dx
        ball.y += ball_speed * dy

        if ball.centerx < ball_radius or ball.centerx > WIDTH - ball_radius:
            dx = -dx

        if ball.centery < ball_radius:
            dy = -dy

        if ball.colliderect(paddle) and dy > 0:
            dx, dy = detect_collision(dx, dy, ball, paddle)

        hit_index = ball.collidelist(block_list)
        if hit_index != -1:
            hit_rect = block_list.pop(hit_index)
            hit_color = color_list.pop(hit_index)
            dx, dy = detect_collision(dx, dy, ball, hit_rect)

            hit_rect.inflate_ip(ball.width * 3, ball.height * 3)
            pygame.draw.rect(sc, hit_color, hit_rect)

        if game_over():
            running = end_game(len(block_list) == 0)

        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT] and paddle.left > 0:
            paddle.left -= paddle_speed
        if key[pygame.K_RIGHT] and paddle.right < WIDTH:
            paddle.right += paddle_speed

        pygame.display.flip()
        clock.tick(fps)

main()
