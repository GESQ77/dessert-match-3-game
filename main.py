import os
import sys
import math
import random
import pygame
from collections import deque


# =========================
# 基础设置
# =========================
ROWS = 8
COLS = 8

DEFAULT_CELL_SIZE = 62
MIN_CELL_SIZE = 44
MAX_CELL_SIZE = 78

TOP_BAR_HEIGHT = 132
BOARD_MARGIN = 22

DEFAULT_WIDTH = 640
DEFAULT_HEIGHT = TOP_BAR_HEIGHT + ROWS * DEFAULT_CELL_SIZE + BOARD_MARGIN * 2

MIN_WINDOW_WIDTH = 560
MIN_WINDOW_HEIGHT = TOP_BAR_HEIGHT + ROWS * MIN_CELL_SIZE + BOARD_MARGIN * 2

FPS = 60
GEM_TYPES = 6

SWAP_DURATION = 160
CLEAR_DURATION = 220
DROP_DURATION = 220
SPAWN_DURATION = 220

HINT_DELAY_MS = 7000

SPECIAL_TRANSPARENT = "transparent"
SPECIAL_RAINBOW = "rainbow"

POPUP_WIDTH = 520
POPUP_HEIGHT = 265


# =========================
# 甜品名称
# =========================
DESSERT_NAMES = {
    0: "小蛋糕",
    1: "冰淇淋",
    2: "橘子汽水",
    3: "曲奇",
    4: "面包",
    5: "甜甜圈",
}


# =========================
# 10 个关卡
# 关卡难度不再只是分数和步数变化，
# 而是加入收集目标、特殊甜品目标、连击目标。
# =========================
LEVELS = [
    {
        "name": "甜品初体验",
        "score": 900,
        "moves": 26,
        "collect": {},
        "transparent": 0,
        "rainbow": 0,
        "combo": 0,
    },
    {
        "name": "草莓蛋糕日",
        "score": 1500,
        "moves": 25,
        "collect": {0: 6},
        "transparent": 0,
        "rainbow": 0,
        "combo": 0,
    },
    {
        "name": "汽水派对",
        "score": 2100,
        "moves": 24,
        "collect": {2: 8},
        "transparent": 0,
        "rainbow": 0,
        "combo": 0,
    },
    {
        "name": "透明甜品",
        "score": 2800,
        "moves": 24,
        "collect": {},
        "transparent": 1,
        "rainbow": 0,
        "combo": 0,
    },
    {
        "name": "曲奇订单",
        "score": 3600,
        "moves": 23,
        "collect": {3: 10},
        "transparent": 1,
        "rainbow": 0,
        "combo": 0,
    },
    {
        "name": "冰淇淋连击",
        "score": 4500,
        "moves": 23,
        "collect": {1: 8},
        "transparent": 0,
        "rainbow": 0,
        "combo": 2,
    },
    {
        "name": "彩虹糖登场",
        "score": 5600,
        "moves": 22,
        "collect": {},
        "transparent": 1,
        "rainbow": 1,
        "combo": 0,
    },
    {
        "name": "面包和甜甜圈",
        "score": 7000,
        "moves": 22,
        "collect": {4: 10, 5: 10},
        "transparent": 1,
        "rainbow": 0,
        "combo": 2,
    },
    {
        "name": "甜品大师",
        "score": 8800,
        "moves": 21,
        "collect": {0: 8, 3: 8},
        "transparent": 2,
        "rainbow": 1,
        "combo": 2,
    },
    {
        "name": "终极甜品宴",
        "score": 10800,
        "moves": 20,
        "collect": {1: 8, 2: 8, 5: 8},
        "transparent": 2,
        "rainbow": 1,
        "combo": 3,
    },
]


# =========================
# 颜色
# =========================
BG_COLOR = (247, 239, 228)
PANEL_COLOR = (244, 220, 193)
GRID_BG = (207, 170, 138)
CELL_BG = (255, 235, 214)
GRID_LINE = (176, 128, 92)

TEXT_COLOR = (96, 62, 42)
WHITE = (255, 255, 255)

TITLE_COLOR = (247, 105, 143)
BUTTON_COLOR = (244, 162, 183)
BUTTON_HOVER = (250, 140, 170)
BUTTON_SELECTED = (255, 196, 212)
BUTTON_TEXT = (106, 49, 66)

HINT_COLOR = (100, 210, 255)
WIN_COLOR = (84, 200, 120)
LOSE_COLOR = (240, 100, 100)
COMBO_COLOR = (255, 140, 40)
SHUFFLE_COLOR = (130, 120, 255)


# =========================
# 图片和音频文件
# =========================
ASSET_FILES = {
    0: "assets/images/Strawberry_cake.png",
    1: "assets/images/Matcha_ice_cream.png",
    2: "assets/images/Orange_soda.png",
    3: "assets/images/Chocolate_Cookie.png",
    4: "assets/images/Pineapple_bun_with_Butter.png",
    5: "assets/images/Dont.png",
}

RAINBOW_FILE = "assets/images/Skittles.png"

MUSIC_ON_IMAGE = "assets/images/Music_on.png"
MUSIC_OFF_IMAGE = "assets/images/Music_off.png"

MUSIC_FILE = "assets/sounds/bgm_piano_healing.flac"

ASSET_OFFSETS = {
    0: (0, 0),
    1: (0, 0),
    2: (0, 0),
    3: (0, 0),
    4: (0, 0),
    5: (0, 0),
}

SOUND_FILES = {
    "swap": "assets/sounds/swap.wav",
    "clear": "assets/sounds/clear.wav",
    "special": "assets/sounds/special.wav",
    "shuffle": "assets/sounds/shuffle.wav",
    "win": "assets/sounds/win.wav",
    "lose": "assets/sounds/lose.wav",
    "hint": "assets/sounds/hint.wav",
}


def get_base(cell):
    if cell is None:
        return None

    if isinstance(cell, tuple):
        if cell[1] == SPECIAL_RAINBOW:
            return "rainbow"
        return cell[0]

    return cell


def get_special(cell):
    if isinstance(cell, tuple):
        return cell[1]
    return None


def make_cell(base, special=None):
    if special is None:
        return base

    if special == SPECIAL_RAINBOW:
        return ("rainbow", SPECIAL_RAINBOW)

    return (base, special)


def is_rainbow(cell):
    return get_special(cell) == SPECIAL_RAINBOW


def is_transparent(cell):
    return get_special(cell) == SPECIAL_TRANSPARENT


class Match3Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()

        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.cache_dir = os.path.join(self.base_dir, "_image_cache")
        os.makedirs(self.cache_dir, exist_ok=True)

        self.width = DEFAULT_WIDTH
        self.height = DEFAULT_HEIGHT

        self.cell_size = DEFAULT_CELL_SIZE
        self.board_x = BOARD_MARGIN
        self.board_y = TOP_BAR_HEIGHT + BOARD_MARGIN
        self.board_w = COLS * self.cell_size
        self.board_h = ROWS * self.cell_size

        self.mixer_ready = self.init_mixer()

        self.screen = pygame.display.set_mode(
            (self.width, self.height),
            pygame.RESIZABLE
        )
        pygame.display.set_caption("甜品消消乐")
        self.clock = pygame.time.Clock()

        self.font_regular_path, self.font_bold_path = self.find_cute_fonts()

        self.font_title = self.make_font(34, bold=True)
        self.font_big = self.make_font(23, bold=True)
        self.font_mid = self.make_font(17, bold=True)
        self.font_small = self.make_font(13)
        self.font_tiny = self.make_font(11)

        self.audio_enabled = True
        self.audio_button = pygame.Rect(0, 0, 58, 42)

        self.selected_start_level = 0
        self.completed_levels = set()

        self.level_buttons = []

        self.start_button = pygame.Rect(0, 0, 200, 50)
        self.level_select_button = pygame.Rect(0, 0, 200, 42)
        self.back_button = pygame.Rect(0, 0, 130, 40)

        self.overlay_primary_button = pygame.Rect(0, 0, 140, 40)
        self.overlay_replay_button = pygame.Rect(0, 0, 140, 40)
        self.overlay_level_button = pygame.Rect(0, 0, 140, 40)

        self.update_layout(self.width, self.height)

        self.draw_loading_screen("正在加载甜品素材...")

        self.scaled_cache = {}

        self.raw_images = self.load_images()
        self.raw_rainbow_image = self.load_rainbow_image()

        self.music_on_image = self.load_music_button_image(MUSIC_ON_IMAGE)
        self.music_off_image = self.load_music_button_image(MUSIC_OFF_IMAGE)

        self.sounds = self.load_sounds()
        self.load_music()

        self.state = "start"

        self.level_index = 0
        self.target_score = 0
        self.moves_left = 0
        self.score = 0

        self.collect_progress = {}
        self.used_transparent = 0
        self.used_rainbow = 0
        self.max_combo = 0

        self.board = []
        self.selected = None
        self.last_swap = []

        self.hint_pair = None
        self.last_input_time = pygame.time.get_ticks()

        self.floating_texts = []
        self.particles = []

    # =========================
    # 自适应窗口
    # =========================
    def update_layout(self, width, height):
        width = max(MIN_WINDOW_WIDTH, int(width))
        height = max(MIN_WINDOW_HEIGHT, int(height))

        self.width = width
        self.height = height

        available_w = max(1, self.width - BOARD_MARGIN * 2)
        available_h = max(1, self.height - TOP_BAR_HEIGHT - BOARD_MARGIN * 2)

        cell_from_w = available_w // COLS
        cell_from_h = available_h // ROWS

        self.cell_size = int(max(MIN_CELL_SIZE, min(MAX_CELL_SIZE, cell_from_w, cell_from_h)))

        self.board_w = COLS * self.cell_size
        self.board_h = ROWS * self.cell_size

        self.board_x = (self.width - self.board_w) // 2

        play_area_h = self.height - TOP_BAR_HEIGHT
        top_bottom_margin = max(BOARD_MARGIN, (play_area_h - self.board_h) // 2)
        self.board_y = TOP_BAR_HEIGHT + top_bottom_margin

        self.audio_button = pygame.Rect(self.width - 74, 10, 58, 42)
        self.update_start_buttons()

    def update_start_buttons(self):
        start_y = min(self.height - 120, 438)

        self.start_button = pygame.Rect(
            self.width // 2 - 100,
            start_y - 25,
            200,
            50
        )

        self.level_select_button = pygame.Rect(
            self.width // 2 - 100,
            start_y + 38,
            200,
            42
        )

        self.back_button = pygame.Rect(22, 18, 130, 40)

    def handle_resize(self, width, height):
        width = max(MIN_WINDOW_WIDTH, int(width))
        height = max(MIN_WINDOW_HEIGHT, int(height))

        self.screen = pygame.display.set_mode(
            (width, height),
            pygame.RESIZABLE
        )

        self.update_layout(width, height)
        self.scaled_cache.clear()

    # =========================
    # 字体：可爱圆润风格
    # =========================
    def find_cute_fonts(self):
        regular_candidates = [
            r"C:\Windows\Fonts\simyou.ttf",
            r"C:\Windows\Fonts\STXINWEI.TTF",
            r"C:\Windows\Fonts\STXINGKA.TTF",
            r"C:\Windows\Fonts\msyh.ttc",
            r"C:\Windows\Fonts\simkai.ttf",
            r"C:\Windows\Fonts\simhei.ttf",
            r"C:\Windows\Fonts\simsun.ttc",
        ]

        bold_candidates = [
            r"C:\Windows\Fonts\simyou.ttf",
            r"C:\Windows\Fonts\msyhbd.ttc",
            r"C:\Windows\Fonts\msyh.ttc",
            r"C:\Windows\Fonts\simhei.ttf",
        ]

        regular = None
        bold = None

        for path in regular_candidates:
            if os.path.exists(path):
                regular = path
                break

        for path in bold_candidates:
            if os.path.exists(path):
                bold = path
                break

        return regular, bold

    def make_font(self, size, bold=False):
        path = self.font_bold_path if bold and self.font_bold_path else self.font_regular_path

        if path:
            font = pygame.font.Font(path, size)
        else:
            font = pygame.font.Font(None, size)

        try:
            font.set_bold(bold)
        except Exception:
            pass

        return font

    def draw_loading_screen(self, text):
        self.screen.fill(BG_COLOR)

        title = self.font_title.render("甜品消消乐", True, TITLE_COLOR)
        tip = self.font_mid.render(text, True, TEXT_COLOR)

        self.screen.blit(title, title.get_rect(center=(self.width // 2, self.height // 2 - 36)))
        self.screen.blit(tip, tip.get_rect(center=(self.width // 2, self.height // 2 + 16)))

        pygame.display.flip()
        pygame.event.pump()

    # =========================
    # 声音
    # =========================
    def init_mixer(self):
        try:
            pygame.mixer.init()
            return True
        except Exception:
            return False

    def load_sounds(self):
        sounds = {}

        if not self.mixer_ready:
            return sounds

        for key, filename in SOUND_FILES.items():
            path = os.path.join(self.base_dir, filename)

            if os.path.exists(path):
                try:
                    sounds[key] = pygame.mixer.Sound(path)
                except Exception:
                    pass

        return sounds

    def load_music(self):
        if not self.mixer_ready:
            return

        path = os.path.join(self.base_dir, MUSIC_FILE)

        if os.path.exists(path):
            try:
                pygame.mixer.music.load(path)
                pygame.mixer.music.set_volume(0.46)

                if self.audio_enabled:
                    pygame.mixer.music.play(-1)

            except Exception as e:
                print(f"背景音乐加载失败：{MUSIC_FILE}，原因：{e}")
        else:
            print(f"没有找到背景音乐文件：{path}")

    def play_sound(self, name):
        if not self.audio_enabled:
            return

        if name in self.sounds:
            try:
                self.sounds[name].play()
            except Exception:
                pass

    def toggle_audio(self):
        self.audio_enabled = not self.audio_enabled

        if not self.mixer_ready:
            return

        try:
            if self.audio_enabled:
                pygame.mixer.music.unpause()

                if not pygame.mixer.music.get_busy():
                    pygame.mixer.music.play(-1)
            else:
                pygame.mixer.music.pause()

        except Exception:
            pass

    def load_music_button_image(self, filename):
        path = self.find_file_case_insensitive(filename)

        try:
            image = pygame.image.load(path).convert_alpha()
            image = self.remove_light_edge_background(image)
            image = self.crop_to_content(image)
            return image
        except Exception as e:
            print(f"音乐按钮图片加载失败：{filename}，原因：{e}")
            return None

    def draw_audio_button(self):
        image = self.music_on_image if self.audio_enabled else self.music_off_image

        if image is not None:
            button_img = self.scale_to_box(
                image,
                self.audio_button.width,
                self.audio_button.height
            )
            self.screen.blit(button_img, self.audio_button.topleft)
            return

        color = (255, 231, 236)
        border = (197, 116, 146)

        pygame.draw.rect(self.screen, color, self.audio_button, border_radius=16)
        pygame.draw.rect(self.screen, border, self.audio_button, 2, border_radius=16)

        cx = self.audio_button.centerx - 3
        cy = self.audio_button.centery
        icon_color = BUTTON_TEXT

        pygame.draw.rect(
            self.screen,
            icon_color,
            pygame.Rect(cx - 17, cy - 7, 8, 14),
            border_radius=3
        )
        pygame.draw.polygon(
            self.screen,
            icon_color,
            [
                (cx - 9, cy - 8),
                (cx - 1, cy - 15),
                (cx - 1, cy + 15),
                (cx - 9, cy + 8),
            ]
        )

        if self.audio_enabled:
            pygame.draw.arc(self.screen, icon_color, (cx + 1, cy - 11, 17, 22), -0.85, 0.85, 2)
            pygame.draw.arc(self.screen, icon_color, (cx + 5, cy - 16, 25, 32), -0.75, 0.75, 2)
        else:
            pygame.draw.line(self.screen, icon_color, (cx + 5, cy - 12), (cx + 24, cy + 12), 3)
            pygame.draw.line(self.screen, icon_color, (cx + 24, cy - 12), (cx + 5, cy + 12), 3)

    # =========================
    # 图片加载
    # =========================
    def find_file_case_insensitive(self, filename):
        direct_path = os.path.join(self.base_dir, filename)

        if os.path.exists(direct_path):
            return direct_path

        target_lower = filename.lower()

        try:
            for name in os.listdir(self.base_dir):
                if name.lower() == target_lower:
                    return os.path.join(self.base_dir, name)
        except Exception:
            pass

        return direct_path

    def load_images(self):
        images = {}

        for gem_type, filename in ASSET_FILES.items():
            path = self.find_file_case_insensitive(filename)

            try:
                image = self.load_one_image(path, gem_type)
            except Exception as e:
                print(f"图片加载失败：{filename}，原因：{e}")
                image = self.create_placeholder_image(gem_type)

            images[gem_type] = image

        return images

    def load_rainbow_image(self):
        path = self.find_file_case_insensitive(RAINBOW_FILE)
        cache_path = os.path.join(self.cache_dir, "clean_rainbow_cute_goal_v1.png")

        try:
            if os.path.exists(cache_path) and os.path.exists(path):
                if os.path.getmtime(cache_path) >= os.path.getmtime(path):
                    return pygame.image.load(cache_path).convert_alpha()

            image = pygame.image.load(path).convert_alpha()
            image = self.remove_light_edge_background(image)
            image = self.crop_to_content(image)

            try:
                pygame.image.save(image, cache_path)
            except Exception:
                pass

            return image

        except Exception as e:
            print(f"彩虹糖图片加载失败：{RAINBOW_FILE}，原因：{e}")
            return None

    def load_one_image(self, path, gem_type):
        cache_name = f"clean_cute_goal_v1_{gem_type}.png"
        cache_path = os.path.join(self.cache_dir, cache_name)

        if os.path.exists(cache_path):
            try:
                cache_time = os.path.getmtime(cache_path)
                source_time = os.path.getmtime(path)

                if cache_time >= source_time:
                    return pygame.image.load(cache_path).convert_alpha()
            except Exception:
                pass

        image = pygame.image.load(path).convert_alpha()
        image = self.remove_light_edge_background(image)
        image = self.crop_to_content(image)

        try:
            pygame.image.save(image, cache_path)
        except Exception:
            pass

        return image

    def is_light_background_pixel(self, color):
        r, g, b, a = color

        if a == 0:
            return True

        if r >= 238 and g >= 238 and b >= 238:
            return True

        if r >= 238 and g >= 228 and b >= 210:
            return True

        if r >= 245 and g >= 230 and b >= 225:
            return True

        if r >= 220 and g >= 220 and b >= 220 and max(r, g, b) - min(r, g, b) <= 20:
            return True

        return False

    def remove_light_edge_background(self, image):
        image = image.copy()
        w, h = image.get_size()

        visited = bytearray(w * h)
        queue = deque()

        for x in range(w):
            queue.append((x, 0))
            queue.append((x, h - 1))

        for y in range(h):
            queue.append((0, y))
            queue.append((w - 1, y))

        while queue:
            x, y = queue.popleft()

            if not (0 <= x < w and 0 <= y < h):
                continue

            index = y * w + x

            if visited[index]:
                continue

            visited[index] = 1

            color = image.get_at((x, y))

            if self.is_light_background_pixel(color):
                image.set_at((x, y), (255, 255, 255, 0))

                queue.append((x + 1, y))
                queue.append((x - 1, y))
                queue.append((x, y + 1))
                queue.append((x, y - 1))

        return image

    def crop_to_content(self, image):
        w, h = image.get_size()

        min_x, min_y = w, h
        max_x, max_y = 0, 0
        found = False

        for y in range(h):
            for x in range(w):
                if image.get_at((x, y)).a > 10:
                    found = True
                    min_x = min(min_x, x)
                    min_y = min(min_y, y)
                    max_x = max(max_x, x)
                    max_y = max(max_y, y)

        if not found:
            return image

        rect = pygame.Rect(min_x, min_y, max_x - min_x + 1, max_y - min_y + 1)
        return image.subsurface(rect).copy()

    def scale_to_box(self, image, max_w, max_h):
        w, h = image.get_size()

        if w == 0 or h == 0:
            return image

        scale = min(max_w / w, max_h / h)
        new_w = max(1, int(w * scale))
        new_h = max(1, int(h * scale))

        scaled = pygame.transform.smoothscale(image, (new_w, new_h))

        canvas = pygame.Surface((max_w, max_h), pygame.SRCALPHA)
        x = (max_w - new_w) // 2
        y = (max_h - new_h) // 2
        canvas.blit(scaled, (x, y))

        return canvas

    def get_scaled_dessert_image(self, gem_type, size):
        size = max(24, int(size))
        key = ("dessert", gem_type, size)

        if key in self.scaled_cache:
            return self.scaled_cache[key]

        raw = self.raw_images[gem_type]
        scaled = self.scale_to_box(raw, size, size)
        self.scaled_cache[key] = scaled

        return scaled

    def get_scaled_rainbow_image(self, size):
        size = max(24, int(size))
        key = ("rainbow", size)

        if key in self.scaled_cache:
            return self.scaled_cache[key]

        if self.raw_rainbow_image is None:
            return None

        scaled = self.scale_to_box(self.raw_rainbow_image, size, size)
        self.scaled_cache[key] = scaled

        return scaled

    def create_placeholder_image(self, gem_type):
        size = 80
        colors = [
            (255, 130, 170),
            (150, 220, 120),
            (255, 190, 80),
            (190, 140, 90),
            (245, 210, 120),
            (255, 150, 200),
        ]

        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        color = colors[gem_type % len(colors)]

        pygame.draw.circle(surf, color, (size // 2, size // 2), size // 2 - 8)
        pygame.draw.circle(surf, WHITE, (size // 2, size // 2), size // 2 - 8, 3)

        return surf

    # =========================
    # 关卡目标
    # =========================
    def reset_goal_progress(self):
        level = LEVELS[self.level_index]
        self.collect_progress = {}

        for dessert_type in level["collect"]:
            self.collect_progress[dessert_type] = 0

        self.used_transparent = 0
        self.used_rainbow = 0
        self.max_combo = 0

    def goal_parts_for_level(self, level_index, include_progress=False):
        level = LEVELS[level_index]
        parts = []

        if include_progress:
            parts.append(f"分数 {self.score}/{level['score']}")
        else:
            parts.append(f"分数 {level['score']}")

        for dessert_type, need in level["collect"].items():
            name = DESSERT_NAMES.get(dessert_type, "甜品")

            if include_progress:
                now = self.collect_progress.get(dessert_type, 0)
                parts.append(f"{name} {now}/{need}")
            else:
                parts.append(f"收集{name}×{need}")

        if level["transparent"] > 0:
            if include_progress:
                parts.append(f"半透明 {self.used_transparent}/{level['transparent']}")
            else:
                parts.append(f"用半透明×{level['transparent']}")

        if level["rainbow"] > 0:
            if include_progress:
                parts.append(f"彩虹糖 {self.used_rainbow}/{level['rainbow']}")
            else:
                parts.append(f"用彩虹糖×{level['rainbow']}")

        if level["combo"] > 0:
            if include_progress:
                parts.append(f"连击 {self.max_combo}/{level['combo']}")
            else:
                parts.append(f"最高连击×{level['combo']}")

        return parts

    def level_goal_finished(self):
        level = LEVELS[self.level_index]

        if self.score < level["score"]:
            return False

        for dessert_type, need in level["collect"].items():
            if self.collect_progress.get(dessert_type, 0) < need:
                return False

        if self.used_transparent < level["transparent"]:
            return False

        if self.used_rainbow < level["rainbow"]:
            return False

        if self.max_combo < level["combo"]:
            return False

        return True

    def add_collect_progress(self, clear_set):
        if not clear_set:
            return

        level = LEVELS[self.level_index]

        if not level["collect"]:
            return

        for r, c in clear_set:
            if not self.in_board(r, c):
                continue

            cell = self.board[r][c]
            base = get_base(cell)

            if base in level["collect"]:
                self.collect_progress[base] = self.collect_progress.get(base, 0) + 1

    # =========================
    # 游戏初始化
    # =========================
    def start_level(self, level_index):
        self.level_index = max(0, min(level_index, len(LEVELS) - 1))

        config = LEVELS[self.level_index]
        self.target_score = config["score"]
        self.moves_left = config["moves"]
        self.score = 0

        self.reset_goal_progress()

        self.selected = None
        self.last_swap = []
        self.hint_pair = None

        self.floating_texts.clear()
        self.particles.clear()

        self.board = self.generate_fresh_board()
        self.state = "playing"
        self.last_input_time = pygame.time.get_ticks()

    def restart_game(self):
        self.start_level(self.level_index)

    def generate_fresh_board(self):
        while True:
            board = [[None for _ in range(COLS)] for _ in range(ROWS)]

            for r in range(ROWS):
                for c in range(COLS):
                    while True:
                        gem = random.randint(0, GEM_TYPES - 1)

                        if c >= 2:
                            if get_base(board[r][c - 1]) == gem and get_base(board[r][c - 2]) == gem:
                                continue

                        if r >= 2:
                            if get_base(board[r - 1][c]) == gem and get_base(board[r - 2][c]) == gem:
                                continue

                        board[r][c] = gem
                        break

            if self.find_possible_moves(board):
                return board

    # =========================
    # 棋盘工具
    # =========================
    def in_board(self, r, c):
        return 0 <= r < ROWS and 0 <= c < COLS

    def swap_cells(self, board, r1, c1, r2, c2):
        board[r1][c1], board[r2][c2] = board[r2][c2], board[r1][c1]

    def is_adjacent(self, r1, c1, r2, c2):
        return abs(r1 - r2) + abs(c1 - c2) == 1

    # =========================
    # 匹配检测
    # =========================
    def find_match_groups(self, board):
        groups = []

        for r in range(ROWS):
            c = 0

            while c < COLS:
                base = get_base(board[r][c])

                if base is None or base == "rainbow":
                    c += 1
                    continue

                start = c
                c += 1

                while c < COLS and get_base(board[r][c]) == base:
                    c += 1

                length = c - start

                if length >= 3:
                    groups.append({
                        "cells": [(r, col) for col in range(start, c)],
                        "base": base,
                        "direction": "row",
                        "length": length
                    })

        for c in range(COLS):
            r = 0

            while r < ROWS:
                base = get_base(board[r][c])

                if base is None or base == "rainbow":
                    r += 1
                    continue

                start = r
                r += 1

                while r < ROWS and get_base(board[r][c]) == base:
                    r += 1

                length = r - start

                if length >= 3:
                    groups.append({
                        "cells": [(row, c) for row in range(start, r)],
                        "base": base,
                        "direction": "col",
                        "length": length
                    })

        return groups

    def find_possible_moves(self, board):
        possible = []

        for r in range(ROWS):
            for c in range(COLS):
                for dr, dc in [(0, 1), (1, 0)]:
                    nr = r + dr
                    nc = c + dc

                    if not self.in_board(nr, nc):
                        continue

                    cell1 = board[r][c]
                    cell2 = board[nr][nc]

                    if (
                        is_rainbow(cell1)
                        or is_rainbow(cell2)
                        or is_transparent(cell1)
                        or is_transparent(cell2)
                    ):
                        possible.append(((r, c), (nr, nc)))
                        continue

                    self.swap_cells(board, r, c, nr, nc)
                    groups = self.find_match_groups(board)
                    self.swap_cells(board, r, c, nr, nc)

                    if groups:
                        possible.append(((r, c), (nr, nc)))

        return possible

    # =========================
    # 提示与洗牌
    # =========================
    def show_hint(self, auto=False):
        moves = self.find_possible_moves(self.board)

        if moves:
            self.hint_pair = random.choice(moves)

            if not auto:
                self.play_sound("hint")
                self.add_floating_text("提示！", HINT_COLOR)
        else:
            self.hint_pair = None

    def auto_shuffle_if_needed(self):
        if self.find_possible_moves(self.board):
            return

        self.add_floating_text("无可移动，自动洗牌！", SHUFFLE_COLOR)
        self.play_sound("shuffle")
        self.shuffle_board()

    def shuffle_board(self):
        cells = []

        for r in range(ROWS):
            for c in range(COLS):
                cells.append(self.board[r][c])

        success = False

        for _ in range(100):
            random.shuffle(cells)

            new_board = [[None for _ in range(COLS)] for _ in range(ROWS)]
            index = 0

            for r in range(ROWS):
                for c in range(COLS):
                    new_board[r][c] = cells[index]
                    index += 1

            if not self.find_match_groups(new_board) and self.find_possible_moves(new_board):
                self.board = new_board
                success = True
                break

        if not success:
            self.board = self.generate_fresh_board()

    # =========================
    # 特殊甜品
    # =========================
    def choose_special_creations(self, groups):
        creations = {}
        sorted_groups = sorted(groups, key=lambda g: g["length"], reverse=True)

        for group in sorted_groups:
            if group["length"] < 4:
                continue

            create_pos = self.choose_create_position(group)
            old = creations.get(create_pos)

            if old is not None and get_special(old) == SPECIAL_RAINBOW:
                continue

            if group["length"] >= 5:
                creations[create_pos] = make_cell(group["base"], SPECIAL_RAINBOW)
            else:
                creations[create_pos] = make_cell(group["base"], SPECIAL_TRANSPARENT)

        return creations

    def choose_create_position(self, group):
        for pos in self.last_swap:
            if pos in group["cells"]:
                return pos

        return group["cells"][len(group["cells"]) // 2]

    def expand_special_effects(self, clear_set, protected):
        expanded = set(clear_set)
        changed = True

        while changed:
            changed = False

            for r, c in list(expanded):
                if not self.in_board(r, c):
                    continue

                cell = self.board[r][c]
                special = get_special(cell)

                if special == SPECIAL_TRANSPARENT:
                    for rr in range(r - 1, r + 2):
                        for cc in range(c - 1, c + 2):
                            if self.in_board(rr, cc) and (rr, cc) not in expanded:
                                expanded.add((rr, cc))
                                changed = True

        return expanded - protected

    # =========================
    # 文字与粒子
    # =========================
    def add_floating_text(self, text, color=WHITE, center=None):
        if center is None:
            center = (self.width // 2, self.board_y + 25)

        self.floating_texts.append({
            "text": text,
            "color": color,
            "x": center[0],
            "y": center[1],
            "life": 75
        })

    def add_combo_text(self, combo_count):
        self.floating_texts.append({
            "text": f"连击 x{combo_count}！",
            "color": COMBO_COLOR,
            "x": self.width // 2,
            "y": self.height // 2 - 25,
            "life": 80
        })

    def spawn_explosion(self, r, c):
        center_x = self.board_x + c * self.cell_size + self.cell_size // 2
        center_y = self.board_y + r * self.cell_size + self.cell_size // 2

        colors = [
            (255, 180, 80),
            (255, 120, 100),
            (255, 240, 150),
            (255, 255, 255),
        ]

        for _ in range(16):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1.5, 4.5)

            self.particles.append({
                "x": center_x,
                "y": center_y,
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "life": random.randint(18, 30),
                "size": random.randint(3, 6),
                "color": random.choice(colors)
            })

    def update_effects(self):
        for item in self.floating_texts[:]:
            item["y"] -= 0.6
            item["life"] -= 1

            if item["life"] <= 0:
                self.floating_texts.remove(item)

        for p in self.particles[:]:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["vy"] += 0.08
            p["life"] -= 1

            if p["life"] <= 0:
                self.particles.remove(p)

    def draw_effects(self):
        for item in self.floating_texts:
            surf = self.font_big.render(item["text"], True, item["color"])
            rect = surf.get_rect(center=(item["x"], item["y"]))
            self.screen.blit(surf, rect)

        for p in self.particles:
            alpha = max(30, min(255, p["life"] * 8))
            surf = pygame.Surface((p["size"] * 2, p["size"] * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*p["color"], alpha), (p["size"], p["size"]), p["size"])
            self.screen.blit(surf, (p["x"] - p["size"], p["y"] - p["size"]))

    # =========================
    # 按钮
    # =========================
    def draw_round_button(self, rect, text, selected=False, faded=False, font=None):
        if font is None:
            font = self.font_mid

        mouse_pos = pygame.mouse.get_pos()
        hover = rect.collidepoint(mouse_pos)

        if selected:
            color = BUTTON_SELECTED
        elif hover:
            color = BUTTON_HOVER
        else:
            color = BUTTON_COLOR

        alpha = 115 if faded else 255

        shadow = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (140, 80, 100, 38), shadow.get_rect(), border_radius=14)
        self.screen.blit(shadow, (rect.x + 2, rect.y + 3))

        button_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(button_surface, (*color, alpha), button_surface.get_rect(), border_radius=14)
        pygame.draw.rect(button_surface, (*WHITE, alpha), button_surface.get_rect(), 3, border_radius=14)
        self.screen.blit(button_surface, rect.topleft)

        surf = font.render(text, True, BUTTON_TEXT)
        if faded:
            surf.set_alpha(150)
        self.screen.blit(surf, surf.get_rect(center=rect.center))

    def draw_text_center(self, text, font, color, center):
        surf = font.render(text, True, color)
        self.screen.blit(surf, surf.get_rect(center=center))

    # =========================
    # 绘制
    # =========================
    def draw(self, hidden=None, moving_items=None):
        if hidden is None:
            hidden = set()

        if moving_items is None:
            moving_items = []

        self.screen.fill(BG_COLOR)

        if self.state == "start":
            self.draw_start_screen()
        elif self.state == "level_select":
            self.draw_level_select_screen()
        else:
            self.draw_top_bar()
            self.draw_board(hidden, moving_items)
            self.draw_effects()

            if self.state == "level_clear":
                self.draw_center_overlay(
                    "关卡完成！",
                    WIN_COLOR,
                    f"第 {self.level_index + 1} 关完成",
                    "下一关" if self.level_index < len(LEVELS) - 1 else "全部通关",
                    mode="level_clear"
                )

            elif self.state == "game_over":
                self.draw_center_overlay(
                    "闯关失败",
                    LOSE_COLOR,
                    "步数用完啦，再试一次吧",
                    "重新开始",
                    mode="game_over"
                )

            elif self.state == "all_clear":
                self.draw_center_overlay(
                    "全部通关！",
                    WIN_COLOR,
                    "恭喜你完成所有关卡！",
                    "重新开始",
                    mode="all_clear"
                )

        pygame.display.flip()

    def draw_start_screen(self):
        self.screen.fill(BG_COLOR)
        self.draw_audio_button()

        self.draw_text_center("甜品消消乐", self.font_title, TITLE_COLOR, (self.width // 2, 58))

        preview_y = 128
        preview_box = max(42, min(58, self.cell_size))
        spacing = preview_box + 14
        start_x = self.width // 2 - (spacing * 5) // 2

        for i in range(GEM_TYPES):
            rect = pygame.Rect(
                start_x + i * spacing - preview_box // 2,
                preview_y - preview_box // 2,
                preview_box,
                preview_box
            )

            pygame.draw.rect(self.screen, CELL_BG, rect, border_radius=10)
            pygame.draw.rect(self.screen, GRID_LINE, rect, 2, border_radius=10)
            self.blit_dessert_image(i, rect, alpha=255)

        cfg = LEVELS[self.selected_start_level]
        self.draw_text_center(
            f"当前关卡：第 {self.selected_start_level + 1} 关《{cfg['name']}》",
            self.font_mid,
            TEXT_COLOR,
            (self.width // 2, 195)
        )

        self.draw_text_center(
            f"步数 {cfg['moves']}    目标分 {cfg['score']}",
            self.font_small,
            TEXT_COLOR,
            (self.width // 2, 222)
        )

        goal_parts = self.goal_parts_for_level(self.selected_start_level, include_progress=False)
        goal_text = "目标：" + "  |  ".join(goal_parts[1:]) if len(goal_parts) > 1 else "目标：达到目标分数即可通关"

        self.draw_text_center(goal_text, self.font_small, TEXT_COLOR, (self.width // 2, 250))

        tips = [
            "3 连：普通消除",
            "4 连：生成半透明甜品，交换后清除 3×3",
            "5 连：生成彩虹糖，交换后清除同类甜品",
        ]

        y = 282
        for tip in tips:
            self.draw_text_center(tip, self.font_small, TEXT_COLOR, (self.width // 2, y))
            y += 23

        self.draw_text_center("H提示  R重开  M音频  ESC退出", self.font_tiny, TEXT_COLOR, (self.width // 2, 360))

        self.update_start_buttons()
        self.draw_round_button(self.start_button, "开始游戏")
        self.draw_round_button(self.level_select_button, "关卡选择")

    def draw_level_select_screen(self):
        self.screen.fill(BG_COLOR)
        self.draw_audio_button()

        self.draw_round_button(self.back_button, "返回首页", font=self.font_small)

        self.draw_text_center("选择关卡", self.font_title, TITLE_COLOR, (self.width // 2, 68))
        self.draw_text_center("每一关都有不同的小目标，越往后挑战越丰富", self.font_small, TEXT_COLOR, (self.width // 2, 106))

        self.level_buttons = []

        button_w = 178
        button_h = 64
        gap_x = 18
        gap_y = 14
        cols = 2

        total_w = cols * button_w + (cols - 1) * gap_x
        start_x = self.width // 2 - total_w // 2
        start_y = 135

        for i, cfg in enumerate(LEVELS):
            row = i // cols
            col = i % cols

            rect = pygame.Rect(
                start_x + col * (button_w + gap_x),
                start_y + row * (button_h + gap_y),
                button_w,
                button_h
            )

            self.level_buttons.append(rect)

            completed = i in self.completed_levels
            selected = i == self.selected_start_level

            mouse_pos = pygame.mouse.get_pos()
            hover = rect.collidepoint(mouse_pos)

            if selected:
                color = BUTTON_SELECTED
            elif hover:
                color = BUTTON_HOVER
            else:
                color = BUTTON_COLOR

            alpha = 115 if completed else 255

            shadow = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            pygame.draw.rect(shadow, (140, 80, 100, 35), shadow.get_rect(), border_radius=14)
            self.screen.blit(shadow, (rect.x + 2, rect.y + 3))

            button_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            pygame.draw.rect(button_surface, (*color, alpha), button_surface.get_rect(), border_radius=14)
            pygame.draw.rect(button_surface, (*WHITE, alpha), button_surface.get_rect(), 3, border_radius=14)
            self.screen.blit(button_surface, rect.topleft)

            line1 = self.font_mid.render(f"第 {i + 1} 关", True, BUTTON_TEXT)
            line2 = self.font_tiny.render(cfg["name"], True, TEXT_COLOR)
            line3 = self.font_tiny.render(f"分数{cfg['score']}  步数{cfg['moves']}", True, TEXT_COLOR)

            if completed:
                line1.set_alpha(150)
                line2.set_alpha(145)
                line3.set_alpha(145)

            self.screen.blit(line1, line1.get_rect(center=(rect.centerx, rect.y + 18)))
            self.screen.blit(line2, line2.get_rect(center=(rect.centerx, rect.y + 38)))
            self.screen.blit(line3, line3.get_rect(center=(rect.centerx, rect.y + 53)))

        self.draw_text_center("已通关的关卡会变淡，点击任意关卡即可开始", self.font_small, TEXT_COLOR, (self.width // 2, self.height - 34))

    def draw_center_overlay(self, title, color, subtitle, primary_text, mode):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        self.screen.blit(overlay, (0, 0))

        popup_w = min(POPUP_WIDTH, self.width - 70)
        popup_h = min(POPUP_HEIGHT, self.height - 110)
        popup_rect = pygame.Rect(0, 0, popup_w, popup_h)
        popup_rect.center = (self.width // 2, self.height // 2)

        pygame.draw.rect(self.screen, (255, 240, 230), popup_rect, border_radius=22)
        pygame.draw.rect(self.screen, (188, 120, 100), popup_rect, 4, border_radius=22)

        self.draw_text_center(title, self.font_title, color, (popup_rect.centerx, popup_rect.y + 48))
        self.draw_text_center(subtitle, self.font_mid, TEXT_COLOR, (popup_rect.centerx, popup_rect.y + 88))

        if mode == "level_clear":
            self.draw_text_center(
                f"得分 {self.score}    剩余步数 {self.moves_left}",
                self.font_small,
                TEXT_COLOR,
                (popup_rect.centerx, popup_rect.y + 118)
            )

        button_w = 132
        button_h = 40
        gap = 10

        if mode == "level_clear":
            total_w = button_w * 3 + gap * 2
            start_x = popup_rect.centerx - total_w // 2
            y = popup_rect.y + popup_rect.height - 64

            self.overlay_primary_button = pygame.Rect(start_x, y, button_w, button_h)
            self.overlay_level_button = pygame.Rect(start_x + button_w + gap, y, button_w, button_h)
            self.overlay_replay_button = pygame.Rect(start_x + (button_w + gap) * 2, y, button_w, button_h)

            self.draw_round_button(self.overlay_primary_button, primary_text, font=self.font_small)
            self.draw_round_button(self.overlay_level_button, "关卡选择", font=self.font_small)
            self.draw_round_button(self.overlay_replay_button, "重玩本关", font=self.font_small)

        else:
            total_w = button_w * 2 + gap
            start_x = popup_rect.centerx - total_w // 2
            y = popup_rect.y + popup_rect.height - 64

            self.overlay_primary_button = pygame.Rect(start_x, y, button_w, button_h)
            self.overlay_level_button = pygame.Rect(start_x + button_w + gap, y, button_w, button_h)
            self.overlay_replay_button = pygame.Rect(0, 0, 0, 0)

            self.draw_round_button(self.overlay_primary_button, primary_text, font=self.font_small)
            self.draw_round_button(self.overlay_level_button, "关卡选择", font=self.font_small)

    def draw_top_bar(self):
        pygame.draw.rect(self.screen, PANEL_COLOR, (0, 0, self.width, TOP_BAR_HEIGHT))

        title = self.font_big.render("甜品消消乐", True, TITLE_COLOR)
        self.screen.blit(title, (18, 8))

        self.draw_audio_button()

        info1 = self.font_mid.render(f"关卡 {self.level_index + 1}", True, TEXT_COLOR)
        info2 = self.font_mid.render(f"分数 {self.score}", True, TEXT_COLOR)
        info3 = self.font_mid.render(f"步数 {self.moves_left}", True, TEXT_COLOR)

        self.screen.blit(info1, (18, 44))
        self.screen.blit(info2, (132, 44))
        self.screen.blit(info3, (270, 44))

        goal_parts = self.goal_parts_for_level(self.level_index, include_progress=True)

        line1 = "目标：" + "  |  ".join(goal_parts[:2])
        line2 = "  |  ".join(goal_parts[2:]) if len(goal_parts) > 2 else "H提示   R重开   M音频   ESC退出"

        goal1 = self.font_tiny.render(line1, True, TEXT_COLOR)
        self.screen.blit(goal1, (18, 76))

        goal2 = self.font_tiny.render(line2, True, TEXT_COLOR)
        self.screen.blit(goal2, (18, 98))

        if len(goal_parts) > 2:
            control_text = self.font_tiny.render("H提示   R重开   M音频   ESC退出", True, TEXT_COLOR)
            self.screen.blit(control_text, (18, 116))

    def draw_board(self, hidden, moving_items):
        board_rect = pygame.Rect(self.board_x, self.board_y, self.board_w, self.board_h)
        pygame.draw.rect(self.screen, GRID_BG, board_rect, border_radius=8)

        for r in range(ROWS):
            for c in range(COLS):
                x = self.board_x + c * self.cell_size
                y = self.board_y + r * self.cell_size
                rect = pygame.Rect(x, y, self.cell_size, self.cell_size)

                pygame.draw.rect(self.screen, CELL_BG, rect)
                pygame.draw.rect(self.screen, GRID_LINE, rect, 2)

                if (r, c) in hidden:
                    continue

                cell = self.board[r][c]

                if cell is not None:
                    self.draw_cell_item(cell, rect)

        if self.selected is not None and self.state == "playing":
            self.draw_selected_effect()

        if self.hint_pair and self.state == "playing":
            tick = pygame.time.get_ticks()
            pulse = 120 + int(100 * (math.sin(tick / 180) + 1) / 2)

            for r, c in self.hint_pair:
                x = self.board_x + c * self.cell_size
                y = self.board_y + r * self.cell_size
                surf = pygame.Surface((self.cell_size - 10, self.cell_size - 10), pygame.SRCALPHA)

                pygame.draw.rect(
                    surf,
                    (*HINT_COLOR, pulse),
                    (0, 0, self.cell_size - 10, self.cell_size - 10),
                    4,
                    border_radius=10
                )

                self.screen.blit(surf, (x + 5, y + 5))

        for item in moving_items:
            rect = pygame.Rect(int(item["x"]), int(item["y"]), self.cell_size, self.cell_size)
            self.draw_cell_item(item["cell"], rect)

    def draw_selected_effect(self):
        r, c = self.selected
        x = self.board_x + c * self.cell_size
        y = self.board_y + r * self.cell_size
        rect = pygame.Rect(x, y, self.cell_size, self.cell_size)

        tick = pygame.time.get_ticks()
        pulse = (math.sin(tick / 130) + 1) / 2
        alpha = int(90 + 90 * pulse)
        border = int(3 + 2 * pulse)

        glow = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)

        pygame.draw.rect(
            glow,
            (255, 255, 255, alpha),
            (4, 4, self.cell_size - 8, self.cell_size - 8),
            border,
            border_radius=12
        )

        pygame.draw.rect(
            glow,
            (255, 170, 200, alpha),
            (8, 8, self.cell_size - 16, self.cell_size - 16),
            2,
            border_radius=10
        )

        center_x, center_y = self.cell_size // 2, self.cell_size // 2
        radius = self.cell_size // 2 - 8

        for i in range(4):
            angle = tick / 320 + i * math.pi / 2
            sx = int(center_x + math.cos(angle) * radius)
            sy = int(center_y + math.sin(angle) * radius)
            pygame.draw.circle(glow, (255, 235, 120, alpha), (sx, sy), max(2, self.cell_size // 20))

        self.screen.blit(glow, rect.topleft)

    def draw_cell_item(self, cell, rect):
        special = get_special(cell)

        if special == SPECIAL_RAINBOW:
            self.draw_rainbow_candy(rect)
            return

        base = get_base(cell)
        alpha = 145 if special == SPECIAL_TRANSPARENT else 255

        self.blit_dessert_image(base, rect, alpha)

        if special == SPECIAL_TRANSPARENT:
            self.draw_transparent_effect(rect)

    def blit_dessert_image(self, gem_type, rect, alpha=255):
        img_size = int(rect.width * 0.82)
        img = self.get_scaled_dessert_image(gem_type, img_size).copy()
        img.set_alpha(alpha)

        offset_x, offset_y = ASSET_OFFSETS.get(gem_type, (0, 0))
        img_rect = img.get_rect(center=(rect.centerx + offset_x, rect.centery + offset_y))

        self.screen.blit(img, img_rect)

    def draw_transparent_effect(self, rect):
        overlay = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)

        pygame.draw.rect(
            overlay,
            (255, 255, 255, 70),
            (5, 5, rect.width - 10, rect.height - 10),
            border_radius=12
        )

        pygame.draw.rect(
            overlay,
            (130, 235, 255, 150),
            (4, 4, rect.width - 8, rect.height - 8),
            3,
            border_radius=12
        )

        tick = pygame.time.get_ticks()
        blink = 150 + int(100 * abs(math.sin(tick / 180)))
        star_color = (255, 255, 255, blink)

        pygame.draw.circle(overlay, star_color, (14, 14), 3)
        pygame.draw.circle(overlay, star_color, (rect.width - 16, 16), 2)
        pygame.draw.circle(overlay, star_color, (18, rect.height - 15), 2)
        pygame.draw.circle(overlay, star_color, (rect.width - 14, rect.height - 14), 3)

        self.screen.blit(overlay, rect.topleft)

    def draw_rainbow_candy(self, rect):
        img_size = int(rect.width * 0.88)
        img = self.get_scaled_rainbow_image(img_size)

        if img is not None:
            img_rect = img.get_rect(center=rect.center)
            self.screen.blit(img, img_rect)
            return

        colors = [
            (255, 70, 95),
            (255, 150, 45),
            (255, 225, 55),
            (70, 220, 110),
            (70, 175, 255),
            (180, 95, 255),
        ]

        size = max(30, int(rect.width * 0.62))
        pixel = max(3, size // 10)
        cols = size // pixel
        center = cols // 2
        radius = cols // 2 - 1
        surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)

        start_x = (rect.width - size) // 2
        start_y = (rect.height - size) // 2

        for y in range(cols):
            for x in range(cols):
                dx = x - center
                dy = y - center

                if dx * dx + dy * dy <= radius * radius:
                    px = start_x + x * pixel
                    py = start_y + y * pixel

                    pygame.draw.rect(surface, (80, 45, 55, 230), (px - 1, py - 1, pixel + 2, pixel + 2))

                    color = colors[(x + y) % len(colors)]
                    pygame.draw.rect(surface, color, (px, py, pixel, pixel))

        self.screen.blit(surface, rect.topleft)

    # =========================
    # 输入
    # =========================
    def handle_click(self, pos):
        if self.audio_button.collidepoint(pos):
            self.toggle_audio()
            return

        if self.state == "start":
            self.update_start_buttons()

            if self.start_button.collidepoint(pos):
                self.start_level(self.selected_start_level)
                return

            if self.level_select_button.collidepoint(pos):
                self.state = "level_select"
                return

        if self.state == "level_select":
            if self.back_button.collidepoint(pos):
                self.state = "start"
                return

            for i, rect in enumerate(self.level_buttons):
                if rect.collidepoint(pos):
                    self.selected_start_level = i
                    self.start_level(i)
                    return

        if self.state == "level_clear":
            if self.overlay_primary_button.collidepoint(pos):
                if self.level_index < len(LEVELS) - 1:
                    self.start_level(self.level_index + 1)
                else:
                    self.state = "all_clear"
                return

            if self.overlay_level_button.collidepoint(pos):
                self.state = "level_select"
                return

            if self.overlay_replay_button.collidepoint(pos):
                self.start_level(self.level_index)
                return

        if self.state in ("game_over", "all_clear"):
            if self.overlay_primary_button.collidepoint(pos):
                self.state = "start"
                self.selected_start_level = 0
                return

            if self.overlay_level_button.collidepoint(pos):
                self.state = "level_select"
                return

        if self.state != "playing":
            return

        x, y = pos

        if not (
            self.board_x <= x < self.board_x + self.board_w
            and self.board_y <= y < self.board_y + self.board_h
        ):
            return

        c = (x - self.board_x) // self.cell_size
        r = (y - self.board_y) // self.cell_size

        if not self.in_board(r, c):
            return

        self.last_input_time = pygame.time.get_ticks()
        self.hint_pair = None

        if self.selected is None:
            self.selected = (r, c)
            return

        r1, c1 = self.selected
        r2, c2 = r, c

        if (r1, c1) == (r2, c2):
            self.selected = None
            return

        if self.is_adjacent(r1, c1, r2, c2):
            self.selected = None
            self.try_swap(r1, c1, r2, c2)
        else:
            self.selected = (r2, c2)

    # =========================
    # 主逻辑
    # =========================
    def try_swap(self, r1, c1, r2, c2):
        if self.state != "playing":
            return

        cell1 = self.board[r1][c1]
        cell2 = self.board[r2][c2]

        if is_rainbow(cell1) or is_rainbow(cell2):
            self.handle_rainbow_swap(r1, c1, r2, c2)
            self.post_move_check()
            return

        if is_transparent(cell1) or is_transparent(cell2):
            self.handle_transparent_swap(r1, c1, r2, c2)
            self.post_move_check()
            return

        self.last_swap = [(r1, c1), (r2, c2)]

        self.animate_swap(r1, c1, r2, c2)
        self.swap_cells(self.board, r1, c1, r2, c2)
        self.play_sound("swap")

        groups = self.find_match_groups(self.board)

        if groups:
            self.moves_left -= 1
            self.resolve_matches(groups)
            self.post_move_check()
        else:
            self.animate_swap(r1, c1, r2, c2)
            self.swap_cells(self.board, r1, c1, r2, c2)

    def handle_transparent_swap(self, r1, c1, r2, c2):
        cell1 = self.board[r1][c1]
        cell2 = self.board[r2][c2]

        self.animate_swap(r1, c1, r2, c2)
        self.swap_cells(self.board, r1, c1, r2, c2)
        self.play_sound("special")

        centers = []

        if is_transparent(cell1):
            centers.append((r2, c2))

        if is_transparent(cell2):
            centers.append((r1, c1))

        clear_set = set()

        for center_r, center_c in centers:
            for rr in range(center_r - 1, center_r + 2):
                for cc in range(center_c - 1, center_c + 2):
                    if self.in_board(rr, cc):
                        clear_set.add((rr, cc))

        clear_set = self.expand_special_effects(clear_set, protected=set())

        self.used_transparent += max(1, len(centers))
        self.moves_left -= 1
        self.score += len(clear_set) * 12

        self.clear_cells_and_drop(clear_set)
        self.resolve_matches()

    def handle_rainbow_swap(self, r1, c1, r2, c2):
        cell1 = self.board[r1][c1]
        cell2 = self.board[r2][c2]

        if is_rainbow(cell1) and is_rainbow(cell2):
            target_base = "ALL"
        elif is_rainbow(cell1):
            target_base = get_base(cell2)
        else:
            target_base = get_base(cell1)

        self.animate_swap(r1, c1, r2, c2)
        self.swap_cells(self.board, r1, c1, r2, c2)
        self.play_sound("special")

        clear_set = set()

        if target_base == "ALL" or target_base is None or target_base == "rainbow":
            for rr in range(ROWS):
                for cc in range(COLS):
                    clear_set.add((rr, cc))
        else:
            for rr in range(ROWS):
                for cc in range(COLS):
                    if get_base(self.board[rr][cc]) == target_base:
                        clear_set.add((rr, cc))

            for rr in range(ROWS):
                for cc in range(COLS):
                    if is_rainbow(self.board[rr][cc]):
                        clear_set.add((rr, cc))

        self.used_rainbow += 1
        self.moves_left -= 1
        self.score += len(clear_set) * 12

        self.clear_cells_and_drop(clear_set)
        self.resolve_matches()

    def post_move_check(self):
        if self.level_goal_finished():
            self.completed_levels.add(self.level_index)
            self.play_sound("win")

            if self.level_index == len(LEVELS) - 1:
                self.state = "all_clear"
            else:
                self.state = "level_clear"

            return

        if self.moves_left <= 0:
            self.play_sound("lose")
            self.state = "game_over"
            return

        self.auto_shuffle_if_needed()

    def resolve_matches(self, groups=None):
        combo_count = 0
        safe_count = 0

        while True:
            safe_count += 1

            if safe_count > 30:
                break

            if groups is None:
                groups = self.find_match_groups(self.board)

            if not groups:
                break

            combo_count += 1
            self.max_combo = max(self.max_combo, combo_count)

            if combo_count >= 2:
                self.add_combo_text(combo_count)

            special_creations = self.choose_special_creations(groups)
            protected = set(special_creations.keys())

            clear_set = set()

            for group in groups:
                for cell in group["cells"]:
                    if cell not in protected:
                        clear_set.add(cell)

            clear_set = self.expand_special_effects(clear_set, protected)

            self.score += len(clear_set) * 10
            self.score += len(special_creations) * 60
            self.score += max(0, combo_count - 1) * 40

            if special_creations:
                self.play_sound("special")
            else:
                self.play_sound("clear")

            self.clear_cells_and_drop(clear_set, special_creations)
            groups = None

    def clear_cells_and_drop(self, clear_set, special_creations=None):
        if special_creations is None:
            special_creations = {}

        self.add_collect_progress(clear_set)

        for r, c in clear_set:
            self.spawn_explosion(r, c)

        if clear_set:
            self.animate_clear(clear_set)

        for r, c in clear_set:
            self.board[r][c] = None

        for (r, c), cell in special_creations.items():
            self.board[r][c] = cell

        self.animate_drop()
        self.animate_spawn()

    # =========================
    # 动画
    # =========================
    def ease_in_out(self, t):
        return t * t * (3 - 2 * t)

    def handle_animation_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.VIDEORESIZE:
                self.handle_resize(event.w, event.h)

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                self.toggle_audio()

    def animate_swap(self, r1, c1, r2, c2):
        cell1 = self.board[r1][c1]
        cell2 = self.board[r2][c2]

        x1 = self.board_x + c1 * self.cell_size
        y1 = self.board_y + r1 * self.cell_size

        x2 = self.board_x + c2 * self.cell_size
        y2 = self.board_y + r2 * self.cell_size

        start_time = pygame.time.get_ticks()

        while True:
            self.handle_animation_events()
            self.update_effects()

            now = pygame.time.get_ticks()
            progress = min(1, (now - start_time) / SWAP_DURATION)
            e = self.ease_in_out(progress)

            item1_x = x1 + (x2 - x1) * e
            item1_y = y1 + (y2 - y1) * e

            item2_x = x2 + (x1 - x2) * e
            item2_y = y2 + (y1 - y2) * e

            moving_items = [
                {"cell": cell1, "x": item1_x, "y": item1_y},
                {"cell": cell2, "x": item2_x, "y": item2_y},
            ]

            self.draw(hidden={(r1, c1), (r2, c2)}, moving_items=moving_items)
            self.clock.tick(FPS)

            if progress >= 1:
                break

    def animate_clear(self, matches):
        start_time = pygame.time.get_ticks()

        while True:
            self.handle_animation_events()
            self.update_effects()

            now = pygame.time.get_ticks()
            progress = min(1, (now - start_time) / CLEAR_DURATION)

            hidden = matches if int(progress * 8) % 2 == 0 else set()

            self.draw(hidden=hidden)
            self.clock.tick(FPS)

            if progress >= 1:
                break

    def animate_drop(self):
        moving_items = []
        hidden = set()
        new_board = [[None for _ in range(COLS)] for _ in range(ROWS)]

        for c in range(COLS):
            target_r = ROWS - 1

            for r in range(ROWS - 1, -1, -1):
                cell = self.board[r][c]

                if cell is not None:
                    start_x = self.board_x + c * self.cell_size
                    start_y = self.board_y + r * self.cell_size

                    end_x = self.board_x + c * self.cell_size
                    end_y = self.board_y + target_r * self.cell_size

                    moving_items.append({
                        "cell": cell,
                        "start_x": start_x,
                        "start_y": start_y,
                        "end_x": end_x,
                        "end_y": end_y,
                    })

                    hidden.add((r, c))
                    new_board[target_r][c] = cell
                    target_r -= 1

        start_time = pygame.time.get_ticks()

        while True:
            self.handle_animation_events()
            self.update_effects()

            now = pygame.time.get_ticks()
            progress = min(1, (now - start_time) / DROP_DURATION)
            e = self.ease_in_out(progress)

            current_items = []

            for item in moving_items:
                x = item["start_x"] + (item["end_x"] - item["start_x"]) * e
                y = item["start_y"] + (item["end_y"] - item["start_y"]) * e

                current_items.append({
                    "cell": item["cell"],
                    "x": x,
                    "y": y
                })

            self.draw(hidden=hidden, moving_items=current_items)
            self.clock.tick(FPS)

            if progress >= 1:
                break

        self.board = new_board

    def animate_spawn(self):
        spawn_items = []
        final_values = []

        for c in range(COLS):
            empty_rows = []

            for r in range(ROWS):
                if self.board[r][c] is None:
                    empty_rows.append(r)

            total = len(empty_rows)

            for index, r in enumerate(empty_rows):
                cell = random.randint(0, GEM_TYPES - 1)

                start_x = self.board_x + c * self.cell_size
                start_y = self.board_y - (total - index) * self.cell_size

                end_x = self.board_x + c * self.cell_size
                end_y = self.board_y + r * self.cell_size

                spawn_items.append({
                    "cell": cell,
                    "start_x": start_x,
                    "start_y": start_y,
                    "end_x": end_x,
                    "end_y": end_y,
                })

                final_values.append((r, c, cell))

        if not spawn_items:
            return

        start_time = pygame.time.get_ticks()

        while True:
            self.handle_animation_events()
            self.update_effects()

            now = pygame.time.get_ticks()
            progress = min(1, (now - start_time) / SPAWN_DURATION)
            e = self.ease_in_out(progress)

            current_items = []

            for item in spawn_items:
                x = item["start_x"] + (item["end_x"] - item["start_x"]) * e
                y = item["start_y"] + (item["end_y"] - item["start_y"]) * e

                current_items.append({
                    "cell": item["cell"],
                    "x": x,
                    "y": y
                })

            self.draw(moving_items=current_items)
            self.clock.tick(FPS)

            if progress >= 1:
                break

        for r, c, cell in final_values:
            self.board[r][c] = cell

    # =========================
    # 主循环
    # =========================
    def run(self):
        while True:
            self.clock.tick(FPS)
            self.update_effects()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.VIDEORESIZE:
                    self.handle_resize(event.w, event.h)

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

                    elif event.key == pygame.K_m:
                        self.toggle_audio()

                    elif self.state == "start":
                        if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                            self.start_level(self.selected_start_level)

                    elif self.state == "playing":
                        if event.key == pygame.K_r:
                            self.start_level(self.level_index)

                        elif event.key == pygame.K_h:
                            self.show_hint(auto=False)
                            self.last_input_time = pygame.time.get_ticks()

                    elif self.state == "level_clear":
                        if event.key == pygame.K_RETURN:
                            if self.level_index < len(LEVELS) - 1:
                                self.start_level(self.level_index + 1)
                            else:
                                self.state = "all_clear"

                        elif event.key == pygame.K_r:
                            self.start_level(self.level_index)

                    elif self.state in ("game_over", "all_clear"):
                        if event.key in (pygame.K_RETURN, pygame.K_r):
                            self.state = "start"

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.handle_click(event.pos)

            if self.state == "playing":
                now = pygame.time.get_ticks()

                if self.hint_pair is None and now - self.last_input_time >= HINT_DELAY_MS:
                    self.show_hint(auto=True)

            self.draw()


if __name__ == "__main__":
    game = Match3Game()
    game.run()
