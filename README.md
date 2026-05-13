# Otter Meeting Digest Helper

Small CLI app to turn daily Otter transcript text into:
- action items
- decisions
- open questions
- key highlights

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py --input sample_transcript.txt --output digest.md --json-output digest.json
```

## Input format

Use plain text export from Otter (or copy/paste transcript text). Speaker labels are fine.

## Optional AI enrichment

By default, it uses rule-based extraction.
If `OPENAI_API_KEY` is set, it attempts enrichment via OpenAI Responses API.

```bash
export OPENAI_API_KEY=... 
export OPENAI_MODEL=gpt-4.1-mini
python app.py --input today.txt --output today_digest.md --json-output today_digest.json
```

## Automation idea

You can schedule this daily:

```bash
0 18 * * 1-5 cd /path/to/project && /path/to/python app.py --input /path/to/today.txt --output /path/to/digest.md
```
