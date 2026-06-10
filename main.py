"""
YouTube Downloader - Dark Mode App
Built with Python + KivyMD
"""

import os
import threading
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.utils import platform
from kivymd.app import MDApp
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
from kivy.clock import Clock, mainthread
from utils.downloader import YouTubeDownloader

# Dark background
Window.clearcolor = (0.08, 0.08, 0.08, 1)

KV = '''
MDScreen:
    md_bg_color: app.theme_cls.backgroundColor

    MDBoxLayout:
        orientation: "vertical"
        spacing: 0

        # ── TOP APP BAR ──────────────────────────────────────────────
        MDTopAppBar:
            id: top_bar
            type: "small"
            MDTopAppBarLeadingButtonContainer:
                MDActionTopAppBarButton:
                    icon: "youtube"
                    theme_icon_color: "Custom"
                    icon_color: 1, 0.2, 0.2, 1

            MDTopAppBarTitle:
                text: "YT Downloader"
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1

            MDTopAppBarTrailingButtonContainer:
                MDActionTopAppBarButton:
                    icon: "information-outline"
                    theme_icon_color: "Custom"
                    icon_color: 0.6, 0.6, 0.6, 1
                    on_release: app.show_info()

        # ── MAIN SCROLL AREA ─────────────────────────────────────────
        MDScrollView:
            do_scroll_x: False

            MDBoxLayout:
                orientation: "vertical"
                padding: "16dp"
                spacing: "16dp"
                adaptive_height: True

                # ── URL INPUT CARD ────────────────────────────────────
                MDCard:
                    md_bg_color: 0.13, 0.13, 0.13, 1
                    radius: [16]
                    padding: "16dp"
                    spacing: "12dp"
                    orientation: "vertical"
                    adaptive_height: True
                    elevation: 2
                    shadow_color: 0, 0, 0, 0.6

                    MDLabel:
                        text: "YouTube URL"
                        theme_text_color: "Custom"
                        text_color: 0.6, 0.6, 0.6, 1
                        font_style: "Label"
                        role: "small"
                        adaptive_height: True

                    MDTextField:
                        id: url_input
                        mode: "outlined"
                        hint_text: "https://www.youtube.com/watch?v=..."
                        helper_text: "Video বা Playlist URL পেস্ট করুন"
                        helper_text_mode: "persistent"

                        MDTextFieldLeadingIcon:
                            icon: "link"
                            theme_icon_color: "Custom"
                            icon_color: 1, 0.2, 0.2, 1

                        MDTextFieldTrailingIcon:
                            icon: "close-circle"
                            theme_icon_color: "Custom"
                            icon_color: 0.5, 0.5, 0.5, 1
                            on_release: app.clear_url()

                # ── FORMAT SELECTION CARD ─────────────────────────────
                MDCard:
                    md_bg_color: 0.13, 0.13, 0.13, 1
                    radius: [16]
                    padding: "16dp"
                    spacing: "12dp"
                    orientation: "vertical"
                    adaptive_height: True
                    elevation: 2

                    MDLabel:
                        text: "ডাউনলোড ফরম্যাট"
                        theme_text_color: "Custom"
                        text_color: 0.6, 0.6, 0.6, 1
                        font_style: "Label"
                        role: "small"
                        adaptive_height: True

                    MDBoxLayout:
                        orientation: "horizontal"
                        spacing: "10dp"
                        adaptive_height: True

                        # Video Button
                        MDButton:
                            id: btn_video
                            style: "filled"
                            md_bg_color: 1, 0.2, 0.2, 1
                            on_release: app.select_format("video")
                            MDButtonIcon:
                                icon: "video"
                            MDButtonText:
                                text: "Video"
                                theme_text_color: "Custom"
                                text_color: 1, 1, 1, 1

                        # Audio Button
                        MDButton:
                            id: btn_audio
                            style: "outlined"
                            on_release: app.select_format("audio")
                            MDButtonIcon:
                                icon: "music"
                            MDButtonText:
                                text: "Audio"

                    # Quality dropdown row
                    MDBoxLayout:
                        id: quality_row
                        orientation: "horizontal"
                        spacing: "10dp"
                        adaptive_height: True

                        MDLabel:
                            text: "Quality:"
                            theme_text_color: "Custom"
                            text_color: 0.7, 0.7, 0.7, 1
                            adaptive_height: True
                            size_hint_x: None
                            width: "70dp"

                        MDSegmentedButton:
                            id: quality_seg
                            MDSegmentedButtonItem:
                                MDSegmentButtonIcon:
                                    icon: "quality-low"
                                MDSegmentButtonLabel:
                                    text: "360p"
                            MDSegmentedButtonItem:
                                active: True
                                MDSegmentButtonIcon:
                                    icon: "quality-medium"
                                MDSegmentButtonLabel:
                                    text: "720p"
                            MDSegmentedButtonItem:
                                MDSegmentButtonIcon:
                                    icon: "quality-high"
                                MDSegmentButtonLabel:
                                    text: "1080p"

                # ── SAVE PATH CARD ────────────────────────────────────
                MDCard:
                    md_bg_color: 0.13, 0.13, 0.13, 1
                    radius: [16]
                    padding: "16dp"
                    spacing: "8dp"
                    orientation: "vertical"
                    adaptive_height: True
                    elevation: 2

                    MDLabel:
                        text: "সেভ লোকেশন"
                        theme_text_color: "Custom"
                        text_color: 0.6, 0.6, 0.6, 1
                        font_style: "Label"
                        role: "small"
                        adaptive_height: True

                    MDBoxLayout:
                        orientation: "horizontal"
                        spacing: "8dp"
                        adaptive_height: True

                        MDTextField:
                            id: save_path
                            mode: "outlined"
                            text: "/sdcard/Download/YTDownloader"
                            size_hint_x: 0.75
                            MDTextFieldLeadingIcon:
                                icon: "folder"
                                theme_icon_color: "Custom"
                                icon_color: 0.8, 0.6, 0.1, 1

                        MDButton:
                            style: "tonal"
                            size_hint_x: 0.25
                            on_release: app.choose_folder()
                            MDButtonText:
                                text: "Browse"

                # ── PROGRESS CARD ─────────────────────────────────────
                MDCard:
                    id: progress_card
                    md_bg_color: 0.13, 0.13, 0.13, 1
                    radius: [16]
                    padding: "16dp"
                    spacing: "10dp"
                    orientation: "vertical"
                    adaptive_height: True
                    elevation: 2
                    opacity: 0

                    MDLabel:
                        id: status_label
                        text: "প্রস্তুত..."
                        theme_text_color: "Custom"
                        text_color: 0.8, 0.8, 0.8, 1
                        adaptive_height: True

                    MDProgressIndicator:
                        id: progress_bar
                        type: "linear"
                        size_hint_y: None
                        height: "4dp"
                        color: 1, 0.2, 0.2, 1

                    MDLabel:
                        id: progress_label
                        text: "0%"
                        theme_text_color: "Custom"
                        text_color: 0.5, 0.5, 0.5, 1
                        font_style: "Label"
                        role: "small"
                        adaptive_height: True
                        halign: "right"

                # ── DOWNLOAD BUTTON ───────────────────────────────────
                MDButton:
                    id: download_btn
                    style: "filled"
                    md_bg_color: 1, 0.2, 0.2, 1
                    size_hint_x: 1
                    height: "56dp"
                    on_release: app.start_download()

                    MDButtonIcon:
                        icon: "download"
                        theme_icon_color: "Custom"
                        icon_color: 1, 1, 1, 1

                    MDButtonText:
                        text: "ডাউনলোড শুরু করুন"
                        theme_text_color: "Custom"
                        text_color: 1, 1, 1, 1
                        font_style: "Title"
                        role: "medium"

                # ── HISTORY CARD ──────────────────────────────────────
                MDCard:
                    md_bg_color: 0.13, 0.13, 0.13, 1
                    radius: [16]
                    padding: "16dp"
                    spacing: "8dp"
                    orientation: "vertical"
                    adaptive_height: True
                    elevation: 2

                    MDBoxLayout:
                        orientation: "horizontal"
                        adaptive_height: True

                        MDLabel:
                            text: "ডাউনলোড হিস্ট্রি"
                            theme_text_color: "Custom"
                            text_color: 0.9, 0.9, 0.9, 1
                            font_style: "Title"
                            role: "small"
                            adaptive_height: True

                        MDIconButton:
                            icon: "delete-sweep"
                            theme_icon_color: "Custom"
                            icon_color: 0.6, 0.2, 0.2, 1
                            on_release: app.clear_history()
                            pos_hint: {"right": 1}

                    MDDivider:

                    MDList:
                        id: history_list
                        adaptive_height: True
'''


class YTDownloaderApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_format = "video"
        self.downloader = YouTubeDownloader()
        self.download_history = []
        self.is_downloading = False

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Red"
        self.theme_cls.primary_hue = "600"
        return Builder.load_string(KV)

    def on_start(self):
        self._ensure_download_dir()
        self._load_history()

    # ── FORMAT SELECTION ──────────────────────────────────────────────────
    def select_format(self, fmt):
        self.selected_format = fmt
        btn_video = self.root.ids.btn_video
        btn_audio = self.root.ids.btn_audio
        quality_row = self.root.ids.quality_row

        if fmt == "video":
            btn_video.style = "filled"
            btn_video.md_bg_color = (1, 0.2, 0.2, 1)
            btn_audio.style = "outlined"
            quality_row.opacity = 1
            quality_row.disabled = False
        else:
            btn_audio.style = "filled"
            btn_audio.md_bg_color = (0.2, 0.6, 1, 1)
            btn_video.style = "outlined"
            quality_row.opacity = 0.4
            quality_row.disabled = True

    # ── DOWNLOAD ──────────────────────────────────────────────────────────
    def start_download(self):
        if self.is_downloading:
            self._snack("⚠️ ডাউনলোড চলছে, অপেক্ষা করুন...")
            return

        url = self.root.ids.url_input.text.strip()
        if not url:
            self._snack("❌ URL দিন!")
            return
        if "youtube.com" not in url and "youtu.be" not in url:
            self._snack("❌ সঠিক YouTube URL দিন")
            return

        save_path = self.root.ids.save_path.text.strip()
        quality = self._get_selected_quality()

        self._show_progress(True)
        self._update_status("🔍 Video তথ্য খোঁজা হচ্ছে...")
        self.is_downloading = True

        thread = threading.Thread(
            target=self._download_thread,
            args=(url, save_path, quality),
            daemon=True
        )
        thread.start()

    def _download_thread(self, url, save_path, quality):
        try:
            self.downloader.download(
                url=url,
                save_path=save_path,
                fmt=self.selected_format,
                quality=quality,
                progress_hook=self._on_progress,
                status_hook=self._on_status,
            )
        except Exception as e:
            self._on_error(str(e))

    @mainthread
    def _on_progress(self, percent, speed, eta):
        pb = self.root.ids.progress_bar
        pl = self.root.ids.progress_label
        pb.value = percent
        pl.text = f"{percent:.0f}%  •  {speed}  •  ETA: {eta}"

    @mainthread
    def _on_status(self, msg, filename=None):
        self.root.ids.status_label.text = msg
        if filename:
            self.is_downloading = False
            self._add_to_history(filename)
            self._snack(f"✅ ডাউনলোড সম্পন্ন: {filename}")
            Clock.schedule_once(lambda dt: self._show_progress(False), 2)

    @mainthread
    def _on_error(self, error_msg):
        self.is_downloading = False
        self._show_progress(False)
        self._snack(f"❌ Error: {error_msg}")

    # ── HISTORY ───────────────────────────────────────────────────────────
    def _add_to_history(self, filename):
        from kivymd.uix.list import (
            MDListItem, MDListItemLeadingIcon,
            MDListItemHeadlineText, MDListItemSupportingText
        )
        import time
        ts = time.strftime("%d/%m %H:%M")
        icon = "music-note" if self.selected_format == "audio" else "video"

        item = MDListItem()
        leading = MDListItemLeadingIcon()
        leading.icon = icon
        leading.theme_icon_color = "Custom"
        leading.icon_color = (1, 0.2, 0.2, 1) if self.selected_format == "video" else (0.2, 0.6, 1, 1)

        headline = MDListItemHeadlineText()
        headline.text = filename[:40] + "..." if len(filename) > 40 else filename
        headline.theme_text_color = "Custom"
        headline.text_color = (0.9, 0.9, 0.9, 1)

        supporting = MDListItemSupportingText()
        supporting.text = ts
        supporting.theme_text_color = "Custom"
        supporting.text_color = (0.5, 0.5, 0.5, 1)

        item.add_widget(leading)
        item.add_widget(headline)
        item.add_widget(supporting)

        self.root.ids.history_list.add_widget(item)
        self.download_history.append({"file": filename, "time": ts, "type": self.selected_format})

    def clear_history(self):
        self.root.ids.history_list.clear_widgets()
        self.download_history.clear()
        self._snack("🗑️ হিস্ট্রি মুছে ফেলা হয়েছে")

    def _load_history(self):
        pass  # Could load from JSON file

    # ── UI HELPERS ────────────────────────────────────────────────────────
    def clear_url(self):
        self.root.ids.url_input.text = ""

    def choose_folder(self):
        self._snack("📁 Default path ব্যবহার হচ্ছে: /sdcard/Download/YTDownloader")

    def show_info(self):
        self._snack("YT Downloader v1.0 | Python + Kivy | Dark Mode")

    def _show_progress(self, show):
        card = self.root.ids.progress_card
        card.opacity = 1 if show else 0
        if show:
            self.root.ids.progress_bar.value = 0

    def _update_status(self, msg):
        self.root.ids.status_label.text = msg

    def _get_selected_quality(self):
        seg = self.root.ids.quality_seg
        qualities = ["360", "720", "1080"]
        for i, item in enumerate(seg.get_items()):
            if hasattr(item, 'active') and item.active:
                return qualities[i]
        return "720"

    def _ensure_download_dir(self):
        path = "/sdcard/Download/YTDownloader"
        if platform == "android":
            try:
                os.makedirs(path, exist_ok=True)
            except Exception:
                pass
        else:
            os.makedirs(os.path.expanduser("~/Downloads/YTDownloader"), exist_ok=True)

    def _snack(self, text):
        snackbar = MDSnackbar(
            MDSnackbarText(text=text),
            y="24dp",
            pos_hint={"center_x": 0.5},
            size_hint_x=0.9,
            md_bg_color=(0.18, 0.18, 0.18, 1),
            duration=2.5,
        )
        snackbar.open()


if __name__ == "__main__":
    YTDownloaderApp().run()
