import json
import re
from pathlib import Path
import requests
import click
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from yt_dlp import YoutubeDL

# Ensure NLTK resources are downloaded and initialized
import nltk

# Absolute path to the NLTK data directory
nltk_data_dir = Path(__file__).parent / "nltk_data"
nltk.data.path.append(str(nltk_data_dir))

# Force download of required resources
nltk.download("punkt", download_dir=str(nltk_data_dir), force=True)
nltk.download("stopwords", download_dir=str(nltk_data_dir), force=True)

# Verify resource availability
try:
    nltk.data.find("tokenizers/punkt")
    print("Punkt tokenizer is correctly loaded.")
except LookupError:
    print("Punkt tokenizer not found!")

try:
    nltk.data.find("corpora/stopwords")
    print("Stopwords are correctly loaded.")
except LookupError:
    print("Stopwords not found!")


def clean_transcript(raw_transcript):
    """
    Cleans up a raw transcript by removing timestamps, formatting artifacts, and stopwords.
    """
    # Remove WEBVTT headers, timestamps, and formatting
    transcript = re.sub(r"WEBVTT.*?\nKind:.*?\nLanguage:.*?\n",
                        "", raw_transcript, flags=re.DOTALL)
    transcript = re.sub(r"\d{2}:\d{2}:\d{2}\.\d{3}.*?\n",
                        "", transcript)  # Remove timestamps
    # Remove inline tags like <c>
    transcript = re.sub(r"<.*?>", "", transcript)
    # Remove [Music], [Applause], etc.
    transcript = re.sub(r"\[.*?\]", "", transcript)
    transcript = re.sub(r"\s{2,}", " ", transcript)  # Remove extra spaces
    transcript = transcript.strip()

    # Tokenize the text
    words = word_tokenize(transcript)

    # Remove stopwords
    stop_words = set(stopwords.words("english"))
    filtered_words = [word for word in words if word.lower() not in stop_words]

    # Rejoin the words into cleaned text
    cleaned_text = " ".join(filtered_words)

    return cleaned_text


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
    """Fetch metadata (title, description, transcript) for a YouTube video or playlist."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    ydl_opts = {
        "quiet": True,  # Suppress yt-dlp logs
        "skip_download": True,  # Do not download the video
        "subtitleslangs": ["en"],  # Only English subtitles
        "writesubtitles": True,  # Enable subtitle download
        # Include auto-generated subtitles if no manual subtitles are available
        "writeautomaticsub": True,
    }

    with YoutubeDL(ydl_opts) as ydl:
        try:
            # Extract video/playlist metadata
            info = ydl.extract_info(url, download=False)

            metadata = {
                "title": info.get("title"),
                "description": info.get("description"),
                "transcript": None,
            }

            # Extract English subtitles (manual or automatic)
            subtitles = info.get("subtitles") or info.get("automatic_captions")
            if subtitles and "en" in subtitles:
                subtitle_formats = subtitles["en"]
                vtt_url = next(
                    (f["url"] for f in subtitle_formats if f["ext"] == "vtt"), None)
                if vtt_url:
                    raw_transcript = fetch_transcript(vtt_url)
                    metadata["transcript"] = clean_transcript(raw_transcript)
                else:
                    metadata["transcript"] = "Transcript not available in VTT format."
            else:
                metadata["transcript"] = "No English subtitles available."

            # Save metadata to the specified format
            if format.lower() == "json":
                output_file = output_path / f"{info['id']}.json"
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(metadata, f, indent=4)
            else:
                output_file = output_path / f"{info['id']}.txt"
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(f"Title: {metadata['title']}\n")
                    f.write(f"Description: {metadata['description']}\n")
                    f.write(f"Transcript:\n{metadata['transcript']}\n")

            click.echo(f"Metadata saved to: {output_file}")

        except Exception as e:
            click.echo(f"Error fetching metadata: {e}")


def fetch_transcript(vtt_url):
    """
    Fetch the transcript from the VTT URL.
    """
    try:
        response = requests.get(vtt_url)
        response.raise_for_status()
        return response.text  # Return the raw VTT content
    except Exception as e:
        return f"Error fetching transcript: {e}"


if __name__ == "__main__":
    fetch_metadata()
