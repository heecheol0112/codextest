"""
Streamlit-based web Tamagotchi for sharing via a link.
Run locally:  streamlit run hamtchi_streamlit.py
Deploy: push this file to a public repo and use Streamlit Community Cloud.
"""
import math
import time
from io import BytesIO

import streamlit as st
from PIL import Image, ImageDraw


WIDTH, HEIGHT = 640, 480  # smaller canvas so it fits mobile viewports better
DEGRADE_PER_SEC = {"hunger": 4, "energy": 2, "fun": 3, "hygiene": 2}
NAME = "터리"


def clamp(val, lo=0, hi=100):
    return max(lo, min(hi, val))


def init_state():
    if "fullness" not in st.session_state:
        st.session_state.fullness = 65
        st.session_state.energy = 65
        st.session_state.fun = 65
        st.session_state.hygiene = 65
        st.session_state.last_tick = time.time()
        st.session_state.state = "idle"
        st.session_state.state_until = 0
        st.session_state.last_action = "안녕!"


def degrade():
    now = time.time()
    dt = now - st.session_state.last_tick
    st.session_state.last_tick = now
    st.session_state.fullness = clamp(st.session_state.fullness - DEGRADE_PER_SEC["hunger"] * dt)
    st.session_state.energy = clamp(st.session_state.energy - DEGRADE_PER_SEC["energy"] * dt)
    st.session_state.fun = clamp(st.session_state.fun - DEGRADE_PER_SEC["fun"] * dt)
    st.session_state.hygiene = clamp(st.session_state.hygiene - DEGRADE_PER_SEC["hygiene"] * dt)
    if now > st.session_state.state_until:
        st.session_state.state = "idle"


def set_action(action, state, dur, deltas):
    for k, v in deltas.items():
        setattr(st.session_state, k, clamp(getattr(st.session_state, k) + v))
    st.session_state.last_action = action
    st.session_state.state = state
    st.session_state.state_until = time.time() + dur


def mood_score():
    return (
        st.session_state.fullness
        + st.session_state.energy
        + st.session_state.fun
        + st.session_state.hygiene
    ) / 4


def draw_hamster(state, mood, t):
    img = Image.new("RGB", (WIDTH, HEIGHT), (32, 36, 48))
    d = ImageDraw.Draw(img)
    # Move character higher on the canvas for mobile viewports
    cx, cy = WIDTH // 2, HEIGHT // 2
    bounce = math.sin(t * 3) * (3 if state != "sleep" else 0)
    cx += int(math.sin(t * 3) * (2 if state != "sleep" else 0))
    cy += int(bounce)

    body_color = (230, 205, 170)
    belly_color = (245, 230, 205)
    ear_color = (210, 180, 150)
    cheek_color = (255, 185, 185)
    outline = (90, 70, 50)

    if state == "bath":
        d.ellipse((cx - 80, cy + 60, cx + 80, cy + 100), fill=(70, 120, 170))
    elif state == "sleep":
        d.rounded_rectangle((cx - 90, cy + 45, cx + 90, cy + 95), 18, fill=(75, 90, 130))
        d.rounded_rectangle((cx - 60, cy + 32, cx + 60, cy + 58), 12, fill=(190, 205, 230))
    elif state == "eat":
        d.ellipse((cx - 60, cy + 62, cx + 60, cy + 92), fill=(120, 90, 60))
        d.ellipse((cx - 55, cy + 60, cx + 55, cy + 86), fill=(180, 140, 90))
    elif state == "play":
        ball_y = cy + 52 + int(math.sin(t * 8) * 10)
        ball_x = cx + 76 + int(math.sin(t * 4) * 10)
        d.ellipse((ball_x - 16, ball_y - 16, ball_x + 16, ball_y + 16), fill=(250, 200, 90))
        d.line((ball_x - 6, ball_y - 6, ball_x + 6, ball_y + 6), fill=(200, 140, 60), width=3)
        d.line((ball_x - 6, ball_y + 6, ball_x + 6, ball_y - 6), fill=(200, 140, 60), width=3)

    d.ellipse((cx - 70, cy - 60, cx + 70, cy + 100), fill=body_color, outline=outline, width=3)
    d.ellipse((cx - 60, cy + 10, cx + 60, cy + 100), fill=belly_color)

    d.ellipse((cx - 64, cy - 84, cx - 16, cy - 36), fill=ear_color, outline=outline, width=2)
    d.ellipse((cx + 16, cy - 84, cx + 64, cy - 36), fill=ear_color, outline=outline, width=2)

    happy = mood >= 70
    worried = mood < 35 and state != "sleep"
    eye_y = cy - 10
    eye_dx = 28
    eye_size = 10 if worried else 12
    eye_color = (40, 40, 50)

    if state == "sleep":
        d.line((cx - eye_dx - 8, eye_y, cx - eye_dx + 8, eye_y), fill=eye_color, width=3)
        d.line((cx + eye_dx - 8, eye_y, cx + eye_dx + 8, eye_y), fill=eye_color, width=3)
    else:
        d.ellipse((cx - eye_dx - eye_size, eye_y - eye_size, cx - eye_dx + eye_size, eye_y + eye_size), fill=eye_color)
        d.ellipse((cx + eye_dx - eye_size, eye_y - eye_size, cx + eye_dx + eye_size, eye_y + eye_size), fill=eye_color)

    if state != "sleep":
        if worried:
            d.line((cx - eye_dx - 8, eye_y - 12, cx - eye_dx + 6, eye_y - 6), fill=outline, width=3)
            d.line((cx + eye_dx - 6, eye_y - 6, cx + eye_dx + 8, eye_y - 12), fill=outline, width=3)
        elif happy or state == "eat":
            d.line((cx - eye_dx - 6, eye_y - 12, cx - eye_dx + 8, eye_y - 14), fill=outline, width=3)
            d.line((cx + eye_dx - 8, eye_y - 14, cx + eye_dx + 6, eye_y - 12), fill=outline, width=3)

    d.ellipse((cx - 6, eye_y + 6, cx + 6, eye_y + 18), fill=(250, 150, 150))

    chew_open = int(t * 6) % 2 == 0
    if state == "sleep":
        d.arc((cx - 10, eye_y + 16, cx + 10, eye_y + 28), 180, 360, fill=outline, width=2)
        d.ellipse((cx + 45, eye_y - 20 + int(math.sin(t * 3) * 3), cx + 55, eye_y - 10 + int(math.sin(t * 3) * 3)), fill=(220, 230, 255))
    elif state == "eat":
        if chew_open:
            d.arc((cx - 16, eye_y + 12, cx + 16, eye_y + 30), 0, 180, fill=outline, width=3)
        else:
            d.line((cx - 10, eye_y + 22, cx + 10, eye_y + 22), fill=outline, width=3)
        paw_seed = (180, 140, 90)
        d.ellipse((cx - 18, cy + 32, cx + 2, cy + 42), fill=paw_seed)
        d.ellipse((cx + 0, cy + 34, cx + 20, cy + 44), fill=paw_seed)
        for i in range(6):
            px = cx - 40 + i * 15 + int(math.sin(t * 5 + i) * 2)
            py = cy + 70 + (i % 2) * 6
            d.ellipse((px, py, px + 12, py + 6), fill=(200, 170, 130))
    elif state == "play":
        d.arc((cx - 18, eye_y + 10, cx + 18, eye_y + 32), 0, 180, fill=outline, width=3)
        for ang in range(0, 360, 90):
            rad = math.radians(ang + t * 180)
            px = cx + int(math.cos(rad) * 36)
            py = cy - 20 + int(math.sin(rad) * 36)
            d.ellipse((px - 4, py - 4, px + 4, py + 4), fill=(255, 230, 120))
    elif state == "bath":
        d.arc((cx - 12, eye_y + 14, cx + 12, eye_y + 28), 180, 360, fill=outline, width=2)
        for i in range(6):
            bub_x = cx - 36 + i * 14 + int(math.sin(t * 2 + i) * 3)
            bub_y = cy - 48 - i * 5 + int(math.cos(t * 2 + i) * 3)
            d.ellipse((bub_x - 8 + i // 2, bub_y - 8 + i // 2, bub_x + 8 - i // 2, bub_y + 8 - i // 2), fill=(200, 230, 255))
        d.ellipse((cx - 18, cy - 68, cx + 18, cy - 32), fill=(220, 240, 255))
        d.ellipse((cx - 30, cy - 62, cx - 10, cy - 38), fill=(220, 240, 255))
        d.ellipse((cx + 10, cy - 60, cx + 30, cy - 40), fill=(220, 240, 255))
    else:
        if worried:
            d.arc((cx - 14, eye_y + 18, cx + 14, eye_y + 36), 180, 360, fill=outline, width=2)
        elif happy:
            d.arc((cx - 16, eye_y + 12, cx + 16, eye_y + 34), 0, 180, fill=outline, width=3)
        else:
            d.line((cx - 10, eye_y + 24, cx + 10, eye_y + 24), fill=outline, width=3)

    for off in (-1, 1):
        d.line((cx + off * 16, eye_y + 18, cx + off * 42, eye_y + 10), fill=outline, width=2)
        d.line((cx + off * 16, eye_y + 22, cx + off * 42, eye_y + 22), fill=outline, width=2)

    d.ellipse((cx - 34, eye_y + 16, cx - 24, eye_y + 26), fill=cheek_color)
    d.ellipse((cx + 24, eye_y + 16, cx + 34, eye_y + 26), fill=cheek_color)

    paw_y = cy + 60 if state != "eat" else cy + 50
    d.ellipse((cx - 48, paw_y - 18, cx - 12, paw_y + 18), fill=body_color, outline=outline, width=2)
    d.ellipse((cx + 12, paw_y - 18, cx + 48, paw_y + 18), fill=body_color, outline=outline, width=2)

    tail_angle = math.sin(t * (5 if state != "sleep" else 1)) * 0.3
    tail_len = 30
    tail_x = cx + 70
    tail_y = cy + 20
    tip = (tail_x + math.cos(tail_angle) * tail_len, tail_y + math.sin(tail_angle) * tail_len)
    d.line((tail_x, tail_y, *tip), fill=outline, width=4)
    return img


def main():
    st.set_page_config(page_title="터리 다마고치", page_icon="🐹", layout="centered")
    init_state()
    degrade()

    st.title("터리 다마고치")
    st.caption("배포용 웹 버전 (Streamlit)")
    cols = st.columns(4)
    if cols[0].button("🥜 먹이주기"):
        set_action("맛있다!", "eat", 2.5, {"fullness": 30, "energy": 5})
    if cols[1].button("🎾 놀아주기"):
        set_action("신난다!", "play", 2.5, {"fun": 28, "energy": -10, "hygiene": -8})
    if cols[2].button("😴 재우기"):
        set_action("잘잤다!", "sleep", 3.0, {"energy": 35, "fullness": -8})
    if cols[3].button("🫧 목욕시키기"):
        set_action("상쾌해!", "bath", 2.5, {"hygiene": 35, "fun": 4})

    mood = mood_score()
    st.write(f"기분 점수: **{int(mood)} / 100**   |   마지막 행동: {st.session_state.last_action}")

    bar_cols = st.columns(4)
    stats = [
        ("포만감", st.session_state.fullness),
        ("에너지", st.session_state.energy),
        ("즐거움", st.session_state.fun),
        ("청결도", st.session_state.hygiene),
    ]
    for (label, val), c in zip(stats, bar_cols):
        c.progress(val / 100, text=f"{label} {int(val)}")

    img = draw_hamster(st.session_state.state, mood, time.time())
    buf = BytesIO()
    img.save(buf, format="PNG")
    st.image(buf.getvalue(), use_column_width=True)

    st.info("다른 사람과 공유하려면 이 파일을 GitHub에 올린 뒤 Streamlit Community Cloud에서 배포하세요.")
    st.caption("로컬 실행: `streamlit run hamtchi_streamlit.py`")


if __name__ == "__main__":
    main()
