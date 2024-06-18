
[![Discord](https://img.shields.io/badge/Discord-Join-7289DA?style=flat&logo=discord&logoColor=white)](https://discord.gg/4AfQ2X3Ffc)
[![Substack](https://img.shields.io/badge/Substack-Subscribe-orange?style=flat&logo=substack&logoColor=white)](https://breakintodata.substack.com/about)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Follow-blue.svg?logo=linkedin&logoColor=white)](https://www.linkedin.com/company/break-into-data/) [![Youtube](https://img.shields.io/badge/YouTube-Subscribe-red)](https://www.youtube.com/channel/UCv9TSSXw9SVWdQreJo2ZU_Q)  ![](https://visitor-badge.laobi.icu/badge?page_id=break-into-data.shorts_generator) 
# Youtube Shorts Generator

Shorts Generator is a tool designed to automate the process of generating short videos. It includes functionalities for audio processing, script processing, and video processing.

## Features

- **Audio Processing**: Tools for handling and processing audio files.
- **Script Processing**: Utilities for managing and processing video scripts.
- **Video Processing**: Functions for editing and generating videos from scripts and audio.
- **Integrations**: Includes uploaders for integrating with various platforms.

## Directory Structure

```plaintext
shorts_generator-main/
├── .env.example            # Example environment configuration file
├── .gitignore              # Git ignore file
├── assets/                 # Assets used in the project
├── requirements.txt        # Python dependencies
└── src/
    ├── audio_processing.py # Audio processing functions
    ├── llms/               # Language model scripts
    ├── main.py             # Main entry point for the application
    ├── script_processing.py# Script processing functions
    ├── uploaders/          # Uploader scripts for various platforms
    └── video_processing.py # Video processing functions
```

## Getting Started

### Prerequisites

Ensure you have Python installed on your system. You can download Python from the [official website](https://www.python.org/).

### Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/your-username/shorts_generator.git
    cd shorts_generator
    ```

2. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

3. Create a `.env` file based on the `.env.example`:
    ```sh
    cp .env.example .env
    ```

4. Configure your environment variables in the `.env` file.

    ELEVEN_API_KEY: Your ElevenLabs API key for audio synthesis.
    OPENAI_API_KEY: Your OpenAI API key for text processing.
    YOUTUBE_API_KEY: Your YouTube API key for video uploading.

   
### Setting Up YouTube Client Secret

To upload videos to YouTube, you need to set up a YouTube client secret:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project or select an existing one.
3. Navigate to **APIs & Services** > **Credentials**.
4. Click **Create Credentials** > **OAuth Client ID**.
5. Configure the consent screen and save.
6. Select **Application type** as **Web application**.
7. Set the **Authorized redirect URIs** to `http://localhost:8080`.
8. Download the client secret JSON file.
9. Save the downloaded file as `client_secret.json` in the root directory of the project.


### Usage

Run the main script to start the application:
```sh
python src/main.py
```

### Scripts

- `audio_processing.py`: Contains functions for processing audio files.
- `script_processing.py`: Contains functions for processing video scripts.
- `video_processing.py`: Contains functions for video editing and generation.

## Contributing

Contributions are welcome! Please fork the repository and create a pull request with your changes.




This README provides an overview of the project's purpose, structure, and usage instructions. Feel free to modify it according to your project's specifics.
