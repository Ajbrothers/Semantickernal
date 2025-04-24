# Semantic Kernel Exercise Plugin

This plugin provides exercise management functionality using the Semantic Kernel framework with Azure OpenAI integration.

## Setup

1. Copy `.env.example` to `.env` and fill in your Azure OpenAI credentials:
```
AZURE_DEPLOYMENT_NAME=your-deployment-name
AZURE_OPENAI_ENDPOINT=your-endpoint
AZURE_OPENAI_KEY=your-api-key
AZURE_OPENAI_API_VERSION=2024-02-01
```

2. Install dependencies:
```bash
pip install semantic-kernel python-dotenv
```

## Features

- View list of exercises with their completion status
- Toggle exercise completion status
- Add new exercises
- Built-in prompt templates for exercise suggestions
- Comprehensive logging
- Error handling

## Usage

1. Run the main plugin:
```bash
python Plugin.py
```

2. Run tests:
```bash
python test_plugin.py
```

## Plugin Structure

```
Semantic/
├── Plugin.py           # Main plugin implementation
├── test_plugin.py     # Unit tests
├── .env.example       # Environment variables template
└── Prompts/           # Prompt templates
    └── ExercisePlugins/Config.json/skprompt.txt
        ├── GetExercise/Config.json/skprompt.txt
        └── SuggestExercise/Config.json/skprompt.txt
```

## Error Handling

The plugin includes comprehensive error handling for:
- Invalid exercise IDs
- API connection issues
- Environment configuration problems
- Invalid input validation

## Logging

Logs are available at INFO level by default, showing:
- Plugin initialization
- Exercise status changes
- API connection status
- Error messages

## Testing

The test suite covers:
- Plugin initialization
- Exercise data structure
- CRUD operations
- Error cases
- Async functionality