import ctypes
import os
import sys
import tkinter as tk
from datetime import datetime, timedelta
from tkinter import messagebox

from PIL import Image, ImageTk


class AppConfig:
    APP_TITLE = "AnimalTimer"
    PET_NAME = "Jake"
    BACKGROUND_IMAGE_PATH = "background.png"
    BOWL_IMAGE_PATH = "bowl.gif"
    FULLSCREEN_IMAGE_PATH_OPEN = "fullscreen_open.gif"
    FULLSCREEN_IMAGE_PATH_CLOSE = "fullscreen_close.gif"
    WINDOW_SIZE = (800, 480)
    RESET_TIME_MORNING = (6, 0)
    RESET_TIME_EVENING = (16, 30)
    UPDATE_INTERVAL = 1000
    FONT_STYLE = ("Cooper Black", 24)
    COUNTDOWN_FONT_STYLE = ("Cooper Black", 20)
    HINT_FONT_STYLE = ("Cooper Black", 14)
    LINK_FONT_STYLE = ("Cooper Black", 14, "underline")
    TEXT_COLOR = "black"


NOT_FED_MESSAGE = f"{AppConfig.PET_NAME} has not eaten. 😢"
FED_MESSAGE = f"{AppConfig.PET_NAME} has been fed! 😀"
BOWL_HINT = "Tap the bowl after feeding"
UNDO_LABEL = "Undo"
TEXT_CENTER_X = 200
BOWL_POSITION = (100, 75)


def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def load_image(relative_path):
    image_path = resource_path(relative_path)
    try:
        return ImageTk.PhotoImage(Image.open(image_path))
    except OSError as e:
        messagebox.showerror(AppConfig.APP_TITLE, f"Could not load image '{image_path}':\n{e}")
        raise SystemExit(1)


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
    return f"Next meal in {hours:02}:{minutes:02}:{seconds:02}"


class FeedingTimer:
    def __init__(self, canvas, status_text, bowl_button, bowl_hint, countdown_text, undo_button):
        self.canvas = canvas
        self.status_text = status_text
        self.bowl_button = bowl_button
        self.bowl_hint = bowl_hint
        self.countdown_text = countdown_text
        self.undo_button = undo_button
        self.pending_tick = None

    def start(self):
        self.tick(next_reset_time(datetime.now()))

    def cancel(self):
        if self.pending_tick is not None:
            self.canvas.after_cancel(self.pending_tick)
            self.pending_tick = None
        self.reset_display()

    def tick(self, end_time):
        remaining_time = max(end_time - datetime.now(), timedelta(0))
        self.canvas.itemconfig(self.countdown_text, text=format_countdown(remaining_time))

        if remaining_time > timedelta(0):
            self.pending_tick = self.canvas.after(AppConfig.UPDATE_INTERVAL, lambda: self.tick(end_time))
        else:
            self.pending_tick = None
            self.reset_display()

    def reset_display(self):
        self.canvas.itemconfig(self.status_text, text=NOT_FED_MESSAGE)
        self.canvas.itemconfig(self.countdown_text, text="")
        self.canvas.itemconfig(self.undo_button, state=tk.HIDDEN)
        self.canvas.itemconfig(self.bowl_button, state=tk.NORMAL)
        self.canvas.itemconfig(self.bowl_hint, state=tk.NORMAL)


class AnimalTimerApp:
    def __init__(self, root):
        self.root = root
        self.load_images()
        self.setup_gui()

    def load_images(self):
        self.bg_image = load_image(AppConfig.BACKGROUND_IMAGE_PATH)
        self.bowl_image = load_image(AppConfig.BOWL_IMAGE_PATH)
        self.fullscreen_open_image = load_image(AppConfig.FULLSCREEN_IMAGE_PATH_OPEN)
        self.fullscreen_close_image = load_image(AppConfig.FULLSCREEN_IMAGE_PATH_CLOSE)

    def setup_gui(self):
        self.root.title(AppConfig.APP_TITLE)

        width, height = AppConfig.WINDOW_SIZE
        self.canvas = tk.Canvas(self.root, width=width, height=height, highlightthickness=0)
        self.canvas.pack()
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.bg_image)

        self.status_text = self.create_text(TEXT_CENTER_X, 50, NOT_FED_MESSAGE)
        bowl_x, bowl_y = BOWL_POSITION
        self.bowl_button = self.create_button(bowl_x, bowl_y, self.bowl_image, self.on_bowl_click)
        bowl_center_x = bowl_x + self.bowl_image.width() // 2
        self.bowl_hint = self.create_text(bowl_center_x, bowl_y + 115, BOWL_HINT, font=AppConfig.HINT_FONT_STYLE)
        self.fullscreen_button = self.create_button(width - 32, 0, self.fullscreen_open_image, self.on_fullscreen_click)
        self.countdown_text = self.create_text(TEXT_CENTER_X, 100, "", font=AppConfig.COUNTDOWN_FONT_STYLE)
        self.undo_button = self.create_text(TEXT_CENTER_X, 150, UNDO_LABEL, font=AppConfig.LINK_FONT_STYLE)
        self.canvas.itemconfig(self.undo_button, state=tk.HIDDEN)
        self.make_clickable(self.undo_button, self.on_undo_click)

        self.feeding_timer = FeedingTimer(self.canvas, self.status_text, self.bowl_button, self.bowl_hint,
                                          self.countdown_text, self.undo_button)
        self.root.bind("<Escape>", self.on_escape)

    def on_bowl_click(self, event):
        self.canvas.itemconfig(self.status_text, text=FED_MESSAGE)
        self.canvas.itemconfig(self.bowl_button, state=tk.HIDDEN)
        self.canvas.itemconfig(self.bowl_hint, state=tk.HIDDEN)
        self.canvas.itemconfig(self.undo_button, state=tk.NORMAL)
        self.feeding_timer.start()

    def on_undo_click(self, event):
        self.feeding_timer.cancel()

    def on_fullscreen_click(self, event):
        self.set_fullscreen(not self.root.attributes('-fullscreen'))

    def on_escape(self, event):
        self.set_fullscreen(False)

    def set_fullscreen(self, enabled):
        self.root.attributes('-fullscreen', enabled)
        img = self.fullscreen_close_image if enabled else self.fullscreen_open_image
        self.canvas.itemconfig(self.fullscreen_button, image=img)

    def create_text(self, x, y, text, font=AppConfig.FONT_STYLE):
        return self.canvas.create_text(x, y, text=text, font=font, fill=AppConfig.TEXT_COLOR)

    def create_button(self, x, y, image, click_handler):
        button = self.canvas.create_image(x, y, anchor=tk.NW, image=image)
        self.make_clickable(button, click_handler)
        return button

    def make_clickable(self, item, click_handler):
        self.canvas.tag_bind(item, "<Button-1>", click_handler)
        self.canvas.tag_bind(item, "<Enter>", lambda event: self.canvas.config(cursor="hand2"))
        self.canvas.tag_bind(item, "<Leave>", lambda event: self.canvas.config(cursor=""))


def hide_frozen_console():
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    ctypes.windll.kernel32.SetConsoleTitleW(AppConfig.APP_TITLE)


if __name__ == "__main__":
    if hasattr(sys, 'frozen'):
        hide_frozen_console()
    root = tk.Tk()
    app = AnimalTimerApp(root)
    root.mainloop()
