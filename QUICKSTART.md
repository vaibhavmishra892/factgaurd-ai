- [ ] API keys for all services:
  - [ ] OpenAI API key
  - [ ] Alpha Vantage API key  
  - [ ] NewsAPI key
  - [ ] SerpAPI key

## Setup Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy the template and add your API keys:

```bash
cp .env.template .env
```

Edit `.env`:
```env
OPENAI_API_KEY=sk-...
ALPHA_VANTAGE_KEY=...
NEWS_API_KEY=...
SERP_API_KEY=...
```

### 3. Run the Application

```bash
python app.py
```

The Gradio UI will launch at: **http://localhost:7860**

## Testing the System

Try these example claims:

1. **Financial + Time-sensitive**: "Gold prices increased yesterday"
   - Should invoke: Finance Agent + News Agent
   
2. **Financial Only**: "Tesla stock price"
   - Should invoke: Finance Agent
   
3. **News Only**: "Climate policy announced in Europe"
   - Should invoke: News Agent

4. **General Knowledge**: "Einstein won Nobel Prize"
   - Should invoke: LLM reasoning only

## Docker Deployment

```bash
# Build
docker build -t fact-verifier .

# Run
docker run -p 7860:7860 --env-file .env fact-verifier
```

## Troubleshooting

**Module not found errors:**
```bash
pip install -r requirements.txt
```

**API key errors:**
- Check `.env` file exists
- Verify all keys are set correctly
- Ensure no extra spaces or quotes

**Port already in use:**
```bash
# Windows
netstat -ano | findstr :7860

# Kill the process or change port in app.py
```

## Project Structure

```
P2/
├── app.py              # Gradio UI (START HERE)
├── fact_verifier.py    # Main orchestrator
├── config.py           # Configuration
├── agents/             # Agent definitions
├── tools/              # API wrappers
├── schemas/            # Data models
└── tests/              # Test suite
```

## Need Help?

See [README.md](README.md) for comprehensive documentation.
