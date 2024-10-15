# CodeLM project

## Run Backend

```bash
git clone https://github.com/t-montes/codelm-back
cd codelm-back
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

### Seting API Keys

You might set the following environment variables in your `.env` file:

```bash
nano .env
```

```bash
OPENAI_API_KEY=...
SERPAPI_KEY=...
```

If they are **not set** on the backend as environment variables, they must be passed through the API calls Authorization header (e.g. `Bearer ${OPENAI_API_KEY};${SERPAPI_KEY}`).

## Run Testing Frontend

```bash
git clone https://github.com/t-montes/codelm-testing-front
cd codelm-testing-front
npm install
npm start
```
