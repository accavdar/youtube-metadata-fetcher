# YouTube Metadata Fetcher

A command-line tool to fetch metadata (title, description, and transcript) from YouTube videos or playlists using `yt-dlp`. The tool processes the video metadata and saves it in either JSON or plain text format.

## Features

- Fetch metadata for individual YouTube videos or entire playlists.
- Extract English transcripts from subtitles (manual or automatic).
- Clean and format titles, descriptions, and transcripts.
- Save metadata in JSON or plain text format.

## Installation

### Install with `pip`

You can install the tool directly from the GitHub repository using `pip`:

```bash
pip install git+https://github.com/accavdar/youtube-metadata-fetcher.git
```

After installation, the CLI tool `youtube-fetch` will be available for use.

### Install with Poetry (Optional for Development)

1. Clone the repository:

   ```bash
   git clone https://github.com/accavdar/youtube-metadata-fetcher.git
   ```

2. Navigate to the project directory and install dependencies:

   ```bash
   cd youtube-metadata-fetcher
   poetry install
   ```

3. Add the CLI tool to your system path:

   ```bash
   poetry run youtube-fetch --help
   ```

## Usage

### Fetch Metadata for a Video or Playlist

Run the CLI tool with the required URL argument and optional parameters:

```bash
youtube-fetch [OPTIONS] URL
```

### Options

| Option        | Description                                                                                     | Default       |
|---------------|-------------------------------------------------------------------------------------------------|---------------|
| `--output-dir`| Directory where metadata files will be saved.                                                   | `output`      |
| `--format`    | Output format for metadata files (`json` or `text`).                                            | `json`        |

### Examples

#### Fetch Metadata for a Single Video

```bash
youtube-fetch --output-dir my_videos --format json "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

#### Fetch Metadata for a Playlist

```bash
youtube-fetch --output-dir playlists --format text "https://www.youtube.com/playlist?list=PLFgquLnL59amGJ6jDFmTa8sqpQjKYjRBl"
```

## Output

The fetched metadata will be saved in the specified directory as JSON or text files, depending on the selected format.

### JSON Format

```json
{
    "title": "Video Title",
    "description": "Video Description",
    "transcript": "Transcript content..."
}
```

### Text Format

```
Title: Video Title
Description: Video Description
Transcript:
Transcript content...
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
