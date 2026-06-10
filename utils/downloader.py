"""
YouTube Downloader Utility
Uses yt-dlp for downloading videos and audio
"""

import os
import re


class YouTubeDownloader:
    def __init__(self):
        self._ydl = None

    def download(self, url, save_path, fmt="video", quality="720",
                 progress_hook=None, status_hook=None):
        try:
            import yt_dlp
        except ImportError:
            if status_hook:
                status_hook("❌ yt-dlp ইনস্টল করা নেই!", None)
            return

        os.makedirs(save_path, exist_ok=True)
        ydl_opts = self._build_options(save_path, fmt, quality, progress_hook, status_hook)

        try:
            if status_hook:
                status_hook("🔍 Video তথ্য লোড হচ্ছে...")

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                title = info.get("title", "video")
                duration = info.get("duration", 0)
                mins = duration // 60
                secs = duration % 60

                if status_hook:
                    status_hook(f"📥 ডাউনলোড হচ্ছে: {title[:30]}... ({mins}:{secs:02d})")

                ydl.download([url])

                ext = "mp3" if fmt == "audio" else "mp4"
                safe_title = self._safe_filename(title)
                filename = f"{safe_title}.{ext}"

                if status_hook:
                    status_hook("✅ সম্পন্ন!", filename)

        except Exception as e:
            err = str(e)
            if "Sign in" in err or "age" in err.lower():
                msg = "❌ এই video age-restricted।"
            elif "Private" in err or "private" in err:
                msg = "❌ Private video ডাউনলোড করা যাবে না।"
            elif "unavailable" in err.lower():
                msg = "❌ Video পাওয়া যাচ্ছে না।"
            elif "network" in err.lower() or "connection" in err.lower():
                msg = "❌ ইন্টারনেট সংযোগ সমস্যা।"
            elif "copyright" in err.lower():
                msg = "❌ Copyright সমস্যা।"
            else:
                msg = f"❌ Error: {err[:80]}"
            if status_hook:
                status_hook(msg, None)
            raise Exception(msg)

    def _build_options(self, save_path, fmt, quality, progress_hook, status_hook):
        def _progress_callback(d):
            if d["status"] == "downloading":
                total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
                downloaded = d.get("downloaded_bytes", 0)
                percent = (downloaded / total * 100) if total > 0 else 0
                speed = d.get("speed", 0) or 0
                eta = d.get("eta", 0) or 0
                if progress_hook:
                    progress_hook(percent, self._format_speed(speed), self._format_eta(eta))
            elif d["status"] == "finished":
                if status_hook:
                    status_hook("⚙️ Processing হচ্ছে...")

        opts = {
            "outtmpl": os.path.join(save_path, "%(title)s.%(ext)s"),
            "progress_hooks": [_progress_callback],
            "quiet": True,
            "no_warnings": True,
            "nocheckcertificate": True,
            "ignoreerrors": False,
            "retries": 3,
        }

        if fmt == "audio":
            opts.update({
                "format": "bestaudio/best",
                "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}],
                "prefer_ffmpeg": True,
            })
        else:
            quality_map = {
                "360": "bestvideo[height<=360]+bestaudio/best[height<=360]/best",
                "720": "bestvideo[height<=720]+bestaudio/best[height<=720]/best",
                "1080": "bestvideo[height<=1080]+bestaudio/best[height<=1080]/best",
            }
            opts.update({
                "format": quality_map.get(quality, quality_map["720"]),
                "merge_output_format": "mp4",
                "prefer_ffmpeg": True,
            })
        return opts

    @staticmethod
    def _safe_filename(name):
        name = re.sub(r'[\\/*?:"<>|]', "", name).strip()
        return name[:80]

    @staticmethod
    def _format_speed(speed_bps):
        if speed_bps <= 0: return "-- KB/s"
        if speed_bps > 1_000_000: return f"{speed_bps/1_000_000:.1f} MB/s"
        return f"{speed_bps/1_000:.0f} KB/s"

    @staticmethod
    def _format_eta(seconds):
        if seconds <= 0: return "--:--"
        return f"{seconds//60}:{seconds%60:02d}"
