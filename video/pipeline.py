from __future__ import annotations

from pathlib import Path
import subprocess


class VideoPipeline:
    """Video-processing boundary.

    Generated source videos can be normalized to a Reel-friendly format with
    FFmpeg. AI generation itself is delegated to a configured provider.
    """

    def normalize_for_reel(self, source: str, destination: str) -> str:
        Path(destination).parent.mkdir(parents=True, exist_ok=True)
        command = [
            "ffmpeg", "-y", "-i", source,
            "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2",
            "-r", "30", "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-movflags", "+faststart", destination,
        ]
        subprocess.run(command, check=True)
        return destination
