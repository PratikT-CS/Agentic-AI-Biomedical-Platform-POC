# Gemini API Setup Instructions

This document provides instructions for setting up Google Gemini API for the biomedical research platform.

## Prerequisites

1. A Google account
2. Access to Google AI Studio

## Getting Your Gemini API Key

1. **Visit Google AI Studio**

   - Go to [https://aistudio.google.com/](https://aistudio.google.com/)

2. **Sign in with your Google account**

3. **Create a new API key**
   - Click on "Get API key" in the left sidebar
   - Click "Create API key"
   - Choose your Google Cloud project (or create a new one)
   - Copy the generated API key

## Setting Up Environment Variables

1. **Create a `.env` file** in the backend directory:

   ```bash
   cd agentic-ai-biomedical-platform/backend
   touch .env
   ```

2. **Add your API key to the `.env` file**:

   ```
   GEMINI_API_KEY=your_actual_api_key_here
   DATABASE_URL=sqlite:///./biomedical_platform.db
   DEBUG=True
   LOG_LEVEL=INFO
   HOST=0.0.0.0
   PORT=8000
   ```

3. **Replace `your_actual_api_key_here`** with the API key you copied from Google AI Studio

## Installing Dependencies

1. **Install the required packages**:

   ```bash
   pip install -r requirements.txt
   ```

2. **Verify the installation**:
   ```bash
   python -c "import google.generativeai; print('Gemini API package installed successfully')"
   ```

## Testing the Setup

1. **Start the backend server**:

   ```bash
   python main.py
   ```

2. **Check the health endpoint**:

   ```bash
   curl http://localhost:8000/health
   ```

3. **Test a query**:
   ```bash
   curl -X POST "http://localhost:8000/api/query" \
        -H "Content-Type: application/json" \
        -d '{"query": "cancer treatment", "sources": ["pubmed"], "max_results": 5}'
   ```

## Troubleshooting

### Common Issues

1. **"GEMINI_API_KEY environment variable is required"**

   - Make sure your `.env` file is in the correct location
   - Verify the API key is correctly set in the `.env` file
   - Restart the application after adding the environment variable

2. **"Invalid API key"**

   - Double-check that you copied the API key correctly
   - Ensure there are no extra spaces or characters
   - Verify the API key is active in Google AI Studio

3. **"Module not found" errors**
   - Run `pip install -r requirements.txt` to install all dependencies
   - Make sure you're using the correct Python environment

### API Limits

- Gemini API has usage limits based on your Google Cloud billing
- Free tier has limited requests per minute
- Monitor your usage in Google AI Studio

## Security Notes

- **Never commit your `.env` file** to version control
- **Keep your API key secure** and don't share it publicly
- **Use environment variables** in production deployments
- **Consider using Google Cloud Secret Manager** for production environments

## Support

For issues related to:

- **Gemini API**: Check [Google AI Studio documentation](https://ai.google.dev/docs)
- **This application**: Check the main README.md file
- **LangChain integration**: Check [LangChain Google GenAI documentation](https://python.langchain.com/docs/integrations/llms/google_vertex_ai_palm)
