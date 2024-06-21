# Bluesky LLM Posting Bot

An automated Bluesky posting bot that generates and posts AI-created images with descriptions.

## Description

This project uses OpenAI's ChatGPT 4o to generate image descriptions, Corcel's Mobius image generation model to create images based on these descriptions, and then posts the result to your Bluesky account. It's designed to run autonomously, creating and sharing unique content regularly.

## Features

- Generates image descriptions using OpenAI's ChatGPT 4o api
- Creates images using Hugging Face's api to run inference on image generation model (Corcelio/mobius)
- Posts generated content to Bluesky
- Handles image resizing and compression to meet Bluesky's upload requirements
- Logs operations for monitoring and debugging
- Includes a shell script for running as a cron job
## Requirements

- Python 3.12.3
- Poetry for dependency management
- OpenAI API key
- Hugging Face API key
- Bluesky account credentials

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/jpotter80/bluesky-llm-posting.git
   cd bluesky-llm-posting
   ```

2. Install dependencies using Poetry:
   ```
   poetry install
   ```

3. Set up environment variables:
   - OPENAI_API_KEY
   - HUGGINGFACE_KEY
   - BSKY_USERNAME
   - BSKY_PASSWORD

## Usage

To run the bot manually:

```
poetry run python post.py
```

To set up automated posting, you can use the provided shell script with a cron job:

1. Edit the `run_post.sh` script to ensure all paths are correct for your system.
2. Make the script executable:
   ```
   chmod +x run_post.sh
   ```
3. Set up a cron job to run the script at your desired frequency.

## Project Structure

- `post.py`: Main script that handles the generation and posting process
- `run_post.sh`: Shell script to run the main Python script
- `pyproject.toml`: Poetry configuration file with project dependencies

## Configuration

Update the following in `post.py`:
- File paths for saving generated content (currently set to `/path/to/project/txt/` and `/path/to/project/images/`)
- Prompt for image description generation
- Any model or API endpoint URLs if they change

## Dependencies

Main dependencies include:
- transformers
- requests
- pillow
- atproto
- torch
- openai
- huggingface-hub

For a full list of dependencies and their versions, refer to the `pyproject.toml` file.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.

## Author

jpotter80 <jpotter80@proton.me>

## Disclaimer

This bot is designed for creative and educational purposes. Ensure you comply with the terms of service of all APIs and platforms used.
