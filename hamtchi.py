import math
import time
import pygame


# 기본 설정
WIDTH, HEIGHT = 720, 540
FPS = 60
NAME = "터리"
DEGRADE_PER_SEC = {
    "hunger": 4,   # 높을수록 배고픔 (0이 포만)
    "energy": 2,
    "fun": 3,
    "hygiene": 2,
}


def clamp(val, lo=0, hi=100):
    return max(lo, min(hi, val))


class Hamtchi:
    def __init__(self):
        # 0~100, 높을수록 좋은 값으로 통일
        self.fullness = 65
        self.energy = 65
        self.fun = 65
        self.hygiene = 65
        self.last_tick = time.time()
        self.last_action = "안녕!"
        self.state = "idle"       # idle / eat / play / sleep / bath
        self.state_until = 0

    def update(self):
        now = time.time()
        dt = now - self.last_tick
        self.last_tick = now

        # 자연 감소
        self.fullness = clamp(self.fullness - DEGRADE_PER_SEC["hunger"] * dt)
        self.energy = clamp(self.energy - DEGRADE_PER_SEC["energy"] * dt)
        self.fun = clamp(self.fun - DEGRADE_PER_SEC["fun"] * dt)
        self.hygiene = clamp(self.hygiene - DEGRADE_PER_SEC["hygiene"] * dt)

        if now > self.state_until:
            self.state = "idle"

    def feed(self):
        self.fullness = clamp(self.fullness + 30)
        self.energy = clamp(self.energy + 5)
        self.last_action = "맛있다!"
        self.state = "eat"
        self.state_until = time.time() + 2.5

    def play(self):
        self.fun = clamp(self.fun + 28)
        self.energy = clamp(self.energy - 10)
        self.hygiene = clamp(self.hygiene - 8)
        self.last_action = "신난다!"
        self.state = "play"
        self.state_until = time.time() + 2.5

    def sleep(self):
        self.energy = clamp(self.energy + 35)
        self.fullness = clamp(self.fullness - 8)
        self.last_action = "잘잤다!"
        self.state = "sleep"
        self.state_until = time.time() + 3

    def clean(self):
        self.hygiene = clamp(self.hygiene + 35)
        self.fun = clamp(self.fun + 4)
        self.last_action = "상쾌해!"
        self.state = "bath"
        self.state_until = time.time() + 2.5

    def mood_score(self):
        return (self.fullness + self.energy + self.fun + self.hygiene) / 4


def draw_button(surface, rect, text, font, hover):
    color = (200, 200, 220) if hover else (180, 180, 200)
    pygame.draw.rect(surface, color, rect, border_radius=10)
    pygame.draw.rect(surface, (90, 90, 110), rect, width=2, border_radius=10)
    txt = font.render(text, True, (20, 20, 30))
    surface.blit(txt, (rect.x + (rect.width - txt.get_width()) // 2,
                       rect.y + (rect.height - txt.get_height()) // 2))


def draw_bar(surface, x, y, label, value, font):
    pygame.draw.rect(surface, (70, 70, 80), (x, y, 180, 22), border_radius=6)
    fill_w = int(180 * (value / 100))
    color = (120, 210, 120) if value >= 60 else (240, 190, 90) if value >= 30 else (240, 120, 120)
    pygame.draw.rect(surface, color, (x, y, fill_w, 22), border_radius=6)
    txt = font.render(f"{label} {int(value)}", True, (240, 240, 240))
    surface.blit(txt, (x + 6, y - 20))


def draw_hamster(surface, center, t, mood, state):
    # mood: 0~100, state drives pose
    cx, cy = center
    bounce = math.sin(t * 3) * 4 if state != "sleep" else 0
    cx += math.sin(t * 3) * (2 if state != "sleep" else 0)
    cy += bounce

    # body
    body_color = (230, 205, 170)
    belly_color = (245, 230, 205)
    ear_color = (210, 180, 150)
    cheek_color = (255, 185, 185)
    outline = (90, 70, 50)

    # ground props per state
    if state == "bath":
        pygame.draw.ellipse(surface, (70, 120, 170), (cx - 80, cy + 70, 160, 40))
    elif state == "sleep":
        pygame.draw.rect(surface, (75, 90, 130), (cx - 90, cy + 55, 180, 50), border_radius=18)  # blanket
        pygame.draw.rect(surface, (190, 205, 230), (cx - 60, cy + 40, 120, 26), border_radius=12)  # pillow
    elif state == "eat":
        pygame.draw.ellipse(surface, (120, 90, 60), (cx - 60, cy + 72, 120, 30))  # seed bowl shadow
        pygame.draw.ellipse(surface, (180, 140, 90), (cx - 55, cy + 70, 110, 26))
    elif state == "play":
        # bouncing ball
        ball_y = cy + 60 + int(math.sin(t * 8) * 12)
        ball_x = cx + 80 + int(math.sin(t * 4) * 10)
        pygame.draw.circle(surface, (250, 200, 90), (ball_x, ball_y), 16)
        pygame.draw.line(surface, (200, 140, 60), (ball_x - 6, ball_y - 6), (ball_x + 6, ball_y + 6), 3)
        pygame.draw.line(surface, (200, 140, 60), (ball_x - 6, ball_y + 6), (ball_x + 6, ball_y - 6), 3)

    pygame.draw.ellipse(surface, body_color, (cx - 70, cy - 60, 140, 160))
    pygame.draw.ellipse(surface, outline, (cx - 70, cy - 60, 140, 160), 3)
    pygame.draw.ellipse(surface, belly_color, (cx - 60, cy + 10, 120, 90))

    # ears
    pygame.draw.circle(surface, ear_color, (cx - 40, cy - 60), 24)
    pygame.draw.circle(surface, ear_color, (cx + 40, cy - 60), 24)
    pygame.draw.circle(surface, outline, (cx - 40, cy - 60), 24, 2)
    pygame.draw.circle(surface, outline, (cx + 40, cy - 60), 24, 2)

    # eyes and mouth change by mood
    happy = mood >= 70
    worried = mood < 35 and state not in ("sleep",)

    eye_y = cy - 10
    eye_dx = 28
    eye_size = 10 if worried else 12
    eye_color = (40, 40, 50)

    if state == "sleep":
        pygame.draw.line(surface, eye_color, (cx - eye_dx - 8, eye_y), (cx - eye_dx + 8, eye_y), 3)
        pygame.draw.line(surface, eye_color, (cx + eye_dx - 8, eye_y), (cx + eye_dx + 8, eye_y), 3)
    else:
        pygame.draw.circle(surface, eye_color, (cx - eye_dx, eye_y), eye_size)
        pygame.draw.circle(surface, eye_color, (cx + eye_dx, eye_y), eye_size)

    # eyebrows
    if state != "sleep":
        if worried:
            pygame.draw.line(surface, outline, (cx - eye_dx - 8, eye_y - 12), (cx - eye_dx + 6, eye_y - 6), 3)
            pygame.draw.line(surface, outline, (cx + eye_dx - 6, eye_y - 6), (cx + eye_dx + 8, eye_y - 12), 3)
        elif happy or state == "eat":
            pygame.draw.line(surface, outline, (cx - eye_dx - 6, eye_y - 12), (cx - eye_dx + 8, eye_y - 14), 3)
            pygame.draw.line(surface, outline, (cx + eye_dx - 8, eye_y - 14), (cx + eye_dx + 6, eye_y - 12), 3)

    # nose
    pygame.draw.circle(surface, (250, 150, 150), (cx, eye_y + 12), 6)

    # mouth + props
    chew_open = (int(t * 6) % 2) == 0
    if state == "sleep":
        pygame.draw.arc(surface, outline, (cx - 10, eye_y + 16, 20, 12), math.pi, math.tau, 2)
        pygame.draw.circle(surface, (220, 230, 255), (cx + 50, eye_y - 10 + int(math.sin(t*3)*3)), 10)
        pygame.draw.circle(surface, (220, 230, 255), (cx + 66, eye_y - 24 + int(math.sin(t*3)*3)), 7)
    elif state == "eat":
        if chew_open:
            pygame.draw.arc(surface, outline, (cx - 16, eye_y + 12, 32, 18), 0, math.pi, 3)
        else:
            pygame.draw.line(surface, outline, (cx - 10, eye_y + 22), (cx + 10, eye_y + 22), 3)
        # paws up with seed
        paw_seed_color = (180, 140, 90)
        pygame.draw.ellipse(surface, paw_seed_color, (cx - 18, cy + 32, 20, 10))
        pygame.draw.ellipse(surface, paw_seed_color, (cx + 0, cy + 34, 20, 10))
        # scattered shells near bowl
        for i in range(6):
            px = cx - 40 + i * 15 + int(math.sin(t*5 + i)*2)
            py = cy + 70 + (i % 2) * 6
            pygame.draw.ellipse(surface, (200, 170, 130), (px, py, 12, 6))
    elif state == "play":
        pygame.draw.arc(surface, outline, (cx - 18, eye_y + 10, 36, 22), 0, math.pi, 3)
        for ang in range(0, 360, 90):
            rad = math.radians(ang + t*180)
            px = cx + int(math.cos(rad)*36)
            py = cy - 20 + int(math.sin(rad)*36)
            pygame.draw.circle(surface, (255, 230, 120), (px, py), 4)
        # little sweat drop for excitement
        pygame.draw.circle(surface, (180, 220, 255), (cx + 36, eye_y - 18), 5)
    elif state == "bath":
        pygame.draw.arc(surface, outline, (cx - 12, eye_y + 14, 24, 14), math.pi, math.tau, 2)
        for i in range(6):
            bub_x = cx - 36 + i*14 + int(math.sin(t*2 + i)*3)
            bub_y = cy - 48 - i*5 + int(math.cos(t*2 + i)*3)
            pygame.draw.circle(surface, (200, 230, 255), (bub_x, bub_y), 8 - i//2)
        # foam on head/body
        pygame.draw.circle(surface, (220, 240, 255), (cx, cy - 50), 18)
        pygame.draw.circle(surface, (220, 240, 255), (cx - 14, cy - 46), 12)
        pygame.draw.circle(surface, (220, 240, 255), (cx + 16, cy - 44), 10)
    else:
        if worried:
            pygame.draw.arc(surface, outline, (cx - 14, eye_y + 18, 28, 18), math.pi, math.tau, 2)
        elif happy:
            pygame.draw.arc(surface, outline, (cx - 16, eye_y + 12, 32, 22), 0, math.pi, 3)
        else:
            pygame.draw.line(surface, outline, (cx - 10, eye_y + 24), (cx + 10, eye_y + 24), 3)

    # whiskers
    for offset in (-1, 1):
        pygame.draw.line(surface, outline, (cx + offset * 16, eye_y + 18), (cx + offset * 42, eye_y + 10), 2)
        pygame.draw.line(surface, outline, (cx + offset * 16, eye_y + 22), (cx + offset * 42, eye_y + 22), 2)

    # cheeks
    pygame.draw.circle(surface, cheek_color, (cx - 34, eye_y + 26), 10)
    pygame.draw.circle(surface, cheek_color, (cx + 34, eye_y + 26), 10)

    # paws (lift when eating)
    paw_y = cy + 60
    if state == "eat":
        paw_y -= 10
    pygame.draw.circle(surface, body_color, (cx - 30, paw_y), 18)
    pygame.draw.circle(surface, body_color, (cx + 30, paw_y), 18)
    pygame.draw.circle(surface, outline, (cx - 30, paw_y), 18, 2)
    pygame.draw.circle(surface, outline, (cx + 30, paw_y), 18, 2)

    # tail wiggle
    tail_angle = math.sin(t * (5 if state != "sleep" else 1)) * 0.3
    tail_len = 30
    tail_x = cx + 70
    tail_y = cy + 20
    tip = (tail_x + math.cos(tail_angle) * tail_len, tail_y + math.sin(tail_angle) * tail_len)
    pygame.draw.line(surface, outline, (tail_x, tail_y), tip, 4)


def run():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("터리 - 다마고치")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("malgungothic", 22)  # Korean-friendly font
    small_font = pygame.font.SysFont("malgungothic", 18)

    ham = Hamtchi()
    buttons = [
        ("먹이주기", pygame.Rect(40, HEIGHT - 100, 120, 44), ham.feed),
        ("놀아주기", pygame.Rect(200, HEIGHT - 100, 120, 44), ham.play),
        ("재우기", pygame.Rect(360, HEIGHT - 100, 120, 44), ham.sleep),
        ("목욕시키기", pygame.Rect(520, HEIGHT - 100, 140, 44), ham.clean),
    ]

    running = True
    start_time = time.time()
    while running:
        dt_ms = clock.tick(FPS)
        ham.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for _, rect, action in buttons:
                    if rect.collidepoint(event.pos):
                        action()

        screen.fill((32, 36, 48))

        # 헤더
        title = font.render(f"{NAME}의 하루", True, (240, 240, 255))
        screen.blit(title, (30, 20))
        status = small_font.render(f"기분: {int(ham.mood_score())} / 100   {ham.last_action}", True, (210, 210, 230))
        screen.blit(status, (30, 50))

        # 바
        draw_bar(screen, 40, 90, "포만감", ham.fullness, small_font)
        draw_bar(screen, 260, 90, "에너지", ham.energy, small_font)
        draw_bar(screen, 480, 90, "즐거움", ham.fun, small_font)
        draw_bar(screen, 40, 140, "청결도", ham.hygiene, small_font)

        # 캐릭터
        t = (time.time() - start_time)
        draw_hamster(screen, (WIDTH // 2, HEIGHT // 2 + 40), t, ham.mood_score(), ham.state)

        # 버튼
        mouse = pygame.mouse.get_pos()
        for text, rect, _ in buttons:
            draw_button(screen, rect, text, small_font, rect.collidepoint(mouse))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    try:
        run()
    except pygame.error as exc:
        print("pygame 실행 중 오류가 발생했습니다. pygame이 설치되어 있는지 확인하세요.")
        raise exc
