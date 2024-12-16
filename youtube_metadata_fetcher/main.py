import re
from pathlib import Path
import requests
import click
from yt_dlp import YoutubeDL
from pydantic import BaseModel


def clean_text(text):
    if not text:
        return "N/A"

    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()


def clean_transcript(raw_transcript):
    # Remove WEBVTT headers and metadata
    transcript = re.sub(r"WEBVTT.*?\nKind:.*?\nLanguage:.*?\n",
                        "", raw_transcript, flags=re.DOTALL)

    # Remove timestamps
    transcript = re.sub(r"\d{2}:\d{2}:\d{2}\.\d{3}.*?\n", "", transcript)

    # Remove inline tags like <c> and artifacts like [Music]
    transcript = re.sub(r"<.*?>", "", transcript)
    transcript = re.sub(r"\[.*?\]", "", transcript)

    # Remove unwanted characters like '<' and replace newlines with spaces
    transcript = re.sub(r"<", "", transcript)
    transcript = re.sub(r"\n", " ", transcript)

    # Replace multiple spaces with a single space
    transcript = re.sub(r"\s{2,}", " ", transcript)
    transcript = transcript.strip()

    return transcript


class VideoMetadata(BaseModel):
    title: str
    description: str
    transcript: str


@click.command()
@click.argument("url")
@click.option(
    "--output-dir",
    default="output",
    help="Directory where metadata files will be saved.",
)
@click.option(
    "--format",
    type=click.Choice(["json", "text"], case_sensitive=False),
    default="json",
    help="Output format for the metadata (json or text).",
)
def fetch_metadata(url, output_dir, format):
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "extract_flat": True,  # Fetch playlist metadata without downloading videos
    }

    with YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)

            if "entries" in info:  # Playlist detected
                click.echo(f"Processing playlist: {info['title']}")

                for entry in info["entries"]:
                    if entry is None:  # Skip unavailable videos
                        click.echo("Skipping unavailable video.")
                        continue

                    video_url = f"https://www.youtube.com/watch?v={
                        entry['id']}"
                    process_video(video_url, output_path, format)

            else:  # Single video
                process_video(url, output_path, format)

        except Exception as e:
            click.echo(f"Error fetching metadata: {e}")


def process_video(video_url, output_path, format):
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "subtitleslangs": ["en"],
        "writesubtitles": True,
        "writeautomaticsub": True,
    }

    with YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(video_url, download=False)

            # Clean metadata fields
            title = clean_text(info.get("title"))
            description = clean_text(info.get("description"))
            transcript = None

            # Extract English subtitles (manual or automatic)
            subtitles = info.get("subtitles") or info.get("automatic_captions")
            if subtitles and "en" in subtitles:
                subtitle_formats = subtitles["en"]
                vtt_url = next(
                    (f["url"] for f in subtitle_formats if f["ext"] == "vtt"), None)
                if vtt_url:
                    raw_transcript = fetch_transcript(vtt_url)
                    transcript = clean_transcript(raw_transcript)
                else:
                    transcript = "Transcript not available in VTT format."
            else:
                transcript = "No English subtitles available."

            metadata = VideoMetadata(
                title=title,
                description=description,
                transcript=transcript
            )

            if format.lower() == "json":
                output_file = output_path / f"{info['id']}.json"
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(metadata.model_dump_json(indent=4))
            else:
                output_file = output_path / f"{info['id']}.txt"
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(f"Title: {metadata.title}\n")
                    f.write(f"Description: {metadata.description}\n")
                    f.write(f"Transcript:\n{metadata.transcript}\n")

            click.echo(f"Metadata saved to: {output_file}")

        except Exception as e:
            click.echo(f"Error processing video {video_url}: {e}")


def fetch_transcript(vtt_url):
    try:
        response = requests.get(vtt_url)
        response.raise_for_status()
        return response.text  # Return the raw VTT content
    except Exception as e:
        return f"Error fetching transcript: {e}"


if __name__ == "__main__":
    fetch_metadata()
