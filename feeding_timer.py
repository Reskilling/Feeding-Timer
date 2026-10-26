import os
import sys
import tkinter as tk
from datetime import datetime, timedelta
from functools import lru_cache
from tkinter import messagebox
from typing import NamedTuple

from PIL import Image, ImageDraw, ImageFont, ImageTk

INK = "#2a2723"
MUTED = "#4a443e"


class TextStyle(NamedTuple):
    size: int
    weight: int
    color: str
    underline: bool = False


class AppConfig:
    APP_TITLE = "Feeding-Timer"
    PET_NAME = "Jake"
    BACKGROUND_IMAGE_PATH = "assets/background.png"
    BOWL_IMAGE_PATH = "assets/bowl.gif"
    FULLSCREEN_IMAGE_PATH_OPEN = "assets/fullscreen_open.gif"
    FULLSCREEN_IMAGE_PATH_CLOSE = "assets/fullscreen_close.gif"
    FONT_PATH = "assets/fonts/Nunito.ttf"
    WINDOW_SIZE = (800, 480)
    RESET_TIME_MORNING = (6, 0)
    RESET_TIME_EVENING = (16, 30)
    UPDATE_INTERVAL = 1000


class Styles:
    TITLE = TextStyle(36, 800, INK)
    HINT = TextStyle(18, 600, MUTED)
    LABEL = TextStyle(14, 800, MUTED)
    COUNTDOWN = TextStyle(56, 700, INK)
    DETAIL = TextStyle(16, 600, MUTED)
    LINK = TextStyle(16, 800, MUTED, underline=True)


class Layout:
    MARGIN = 32
    TITLE_Y = 32
    HINT_Y = 84
    BOWL_Y = 120
    LABEL_Y = 100
    COUNTDOWN_Y = 116
    DETAIL_Y = 196
    INLINE_GAP = 16


NOT_FED_TITLE = f"Time to feed {AppConfig.PET_NAME}"
FED_TITLE = f"{AppConfig.PET_NAME} has been fed"
BOWL_HINT = "Tap the bowl after feeding"
COUNTDOWN_LABEL = "NEXT MEAL IN"
UNDO_LABEL = "Undo"


def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def exit_with_missing_asset(path, error):
    messagebox.showerror(AppConfig.APP_TITLE, f"Could not load '{path}':\n{error}")
    raise SystemExit(1)


def load_image(relative_path):
    image_path = resource_path(relative_path)
    try:
        return ImageTk.PhotoImage(Image.open(image_path))
    except OSError as e:
        exit_with_missing_asset(image_path, e)


@lru_cache(maxsize=None)
def load_font(size, weight):
    font_path = resource_path(AppConfig.FONT_PATH)
    try:
        font = ImageFont.truetype(font_path, size)
    except OSError as e:
        exit_with_missing_asset(font_path, e)
    font.set_variation_by_axes([weight])
    return font


def render_text(text, style):
    """Render text with the bundled font, so it looks the same whether or not the font is installed."""
    font = load_font(style.size, style.weight)
    ascent, descent = font.getmetrics()
    width = max(1, round(font.getlength(text)))
    image = Image.new("RGBA", (width, ascent + descent))
    draw = ImageDraw.Draw(image)
    draw.text((0, 0), text, font=font, fill=style.color)
    if style.underline:
        underline_y = ascent + 2
        draw.line([(0, underline_y), (width, underline_y)], fill=style.color, width=max(1, style.size // 12))
    return ImageTk.PhotoImage(image)


def next_reset_time(now):
    reset_time_morning = now.replace(hour=AppConfig.RESET_TIME_MORNING[0], minute=AppConfig.RESET_TIME_MORNING[1],
                                     second=0, microsecond=0)
    reset_time_evening = now.replace(hour=AppConfig.RESET_TIME_EVENING[0], minute=AppConfig.RESET_TIME_EVENING[1],
                                     second=0, microsecond=0)

    if now < reset_time_morning:
        return reset_time_morning
    if now < reset_time_evening:
        return reset_time_evening
    return reset_time_morning + timedelta(days=1)


def format_countdown(remaining_time):
    hours, remainder = divmod(int(remaining_time.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}:{minutes:02}:{seconds:02}"


def format_clock_time(moment):
    return f"{moment:%I:%M %p}".lstrip("0")


class MealCountdown:
    def __init__(self, widget, on_tick, on_finished):
        self.widget = widget
        self.on_tick = on_tick
        self.on_finished = on_finished
        self.pending_tick = None

    def start(self, end_time):
        self.tick(end_time)

    def cancel(self):
        if self.pending_tick is not None:
            self.widget.after_cancel(self.pending_tick)
            self.pending_tick = None

    def tick(self, end_time):
        remaining_time = max(end_time - datetime.now(), timedelta(0))
        if remaining_time > timedelta(0):
            self.on_tick(remaining_time)
            self.pending_tick = self.widget.after(AppConfig.UPDATE_INTERVAL, lambda: self.tick(end_time))
        else:
            self.pending_tick = None
            self.on_finished()


class FeedingTimerApp:
    def __init__(self, root):
        self.root = root
        self.text_images = {}
        self.load_images()
        self.setup_gui()
        self.show_not_fed()

    def load_images(self):
        self.bg_image = load_image(AppConfig.BACKGROUND_IMAGE_PATH)
        self.bowl_image = load_image(AppConfig.BOWL_IMAGE_PATH)
        self.fullscreen_open_image = load_image(AppConfig.FULLSCREEN_IMAGE_PATH_OPEN)
        self.fullscreen_close_image = load_image(AppConfig.FULLSCREEN_IMAGE_PATH_CLOSE)

    def setup_gui(self):
        self.root.title(AppConfig.APP_TITLE)
        self.root.resizable(False, False)
        self.root.iconphoto(True, self.bowl_image)

        width, height = AppConfig.WINDOW_SIZE
        self.canvas = tk.Canvas(self.root, width=width, height=height, highlightthickness=0)
        self.canvas.pack()
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.bg_image)

        self.title_text = self.create_text(Layout.TITLE_Y)

        self.bowl_hint = self.create_text(Layout.HINT_Y)
        self.set_text(self.bowl_hint, BOWL_HINT, Styles.HINT)
        self.bowl_button = self.create_button(Layout.MARGIN, Layout.BOWL_Y, self.bowl_image, self.on_bowl_click)

        self.countdown_label = self.create_text(Layout.LABEL_Y)
        self.set_text(self.countdown_label, COUNTDOWN_LABEL, Styles.LABEL)
        self.countdown_text = self.create_text(Layout.COUNTDOWN_Y)
        self.fed_at_text = self.create_text(Layout.DETAIL_Y)
        self.undo_button = self.create_text(Layout.DETAIL_Y)
        self.set_text(self.undo_button, UNDO_LABEL, Styles.LINK)
        self.make_clickable(self.undo_button, self.on_undo_click)

        icon_size = self.fullscreen_open_image.width()
        self.fullscreen_button = self.create_button(width - icon_size - Layout.INLINE_GAP, Layout.INLINE_GAP,
                                                    self.fullscreen_open_image, self.on_fullscreen_click)

        self.not_fed_items = (self.bowl_hint, self.bowl_button)
        self.fed_items = (self.countdown_label, self.countdown_text, self.fed_at_text, self.undo_button)

        self.countdown = MealCountdown(self.canvas, on_tick=self.show_remaining_time, on_finished=self.show_not_fed)
        self.root.bind("<Escape>", self.on_escape)

    def show_not_fed(self):
        self.set_text(self.title_text, NOT_FED_TITLE, Styles.TITLE)
        self.set_visible(self.fed_items, False)
        self.set_visible(self.not_fed_items, True)

    def show_fed(self, fed_at):
        self.set_text(self.title_text, FED_TITLE, Styles.TITLE)
        self.set_text(self.fed_at_text, f"Fed at {format_clock_time(fed_at)}", Styles.DETAIL)
        undo_x = Layout.MARGIN + self.text_images[self.fed_at_text].width() + Layout.INLINE_GAP
        self.canvas.coords(self.undo_button, undo_x, Layout.DETAIL_Y)
        self.set_visible(self.not_fed_items, False)
        self.set_visible(self.fed_items, True)

    def show_remaining_time(self, remaining_time):
        self.set_text(self.countdown_text, format_countdown(remaining_time), Styles.COUNTDOWN)

    def on_bowl_click(self, event):
        fed_at = datetime.now()
        self.show_fed(fed_at)
        self.countdown.start(next_reset_time(fed_at))

    def on_undo_click(self, event):
        self.countdown.cancel()
        self.show_not_fed()

    def on_fullscreen_click(self, event):
        self.set_fullscreen(not self.root.attributes('-fullscreen'))

    def on_escape(self, event):
        self.set_fullscreen(False)

    def set_fullscreen(self, enabled):
        self.root.attributes('-fullscreen', enabled)
        img = self.fullscreen_close_image if enabled else self.fullscreen_open_image
        self.canvas.itemconfig(self.fullscreen_button, image=img)

    def create_text(self, y):
        return self.canvas.create_image(Layout.MARGIN, y, anchor=tk.NW)

    def set_text(self, item, text, style):
        self.text_images[item] = render_text(text, style)
        self.canvas.itemconfig(item, image=self.text_images[item])

    def set_visible(self, items, visible):
        for item in items:
            self.canvas.itemconfig(item, state=tk.NORMAL if visible else tk.HIDDEN)

    def create_button(self, x, y, image, click_handler):
        button = self.canvas.create_image(x, y, anchor=tk.NW, image=image)
        self.make_clickable(button, click_handler)
        return button

    def make_clickable(self, item, click_handler):
        self.canvas.tag_bind(item, "<Button-1>", click_handler)
        self.canvas.tag_bind(item, "<Enter>", lambda event: self.canvas.config(cursor="hand2"))
        self.canvas.tag_bind(item, "<Leave>", lambda event: self.canvas.config(cursor=""))


if __name__ == "__main__":
    root = tk.Tk()
    app = FeedingTimerApp(root)
    root.mainloop()
