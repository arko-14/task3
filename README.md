# FastAPI Gemini Proxy

A lightweight FastAPI proxy service that forwards prompts to Google's Gemini 2.0 Flash API and returns the generated text.

## Features

- Simple REST API for text generation via Gemini
- Optional debug mode to inspect raw API responses
- Health check endpoint

## Requirements

- Python 3.8+
- Google API Key with Gemini access

## Installation

1. Clone the repository and navigate to the project folder

2. Create and activate a virtual environment:
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set your Google API key as an environment variable:
   ```bash
   export GOOGLE_API_KEY="your-api-key"  # On Windows: set GOOGLE_API_KEY=your-api-key
   ```

## Usage

Start the server:
```bash
uvicorn main:app --reload
```

### Endpoints

#### POST `/generate`
Generate text from a prompt.

**Request body:**
```json
{
  "prompt": "Your prompt here",
  "debug": false
}
```

**Response:**
```json
{
  "text": "Generated response text"
}
```

Set `debug: true` to include the raw Gemini API response.

#### GET `/health`
Health check endpoint. Returns `{"status": "ok"}`.

## License

MIT
