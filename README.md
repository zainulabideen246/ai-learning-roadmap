# PathPilot — AI Learning Roadmap Generator

PathPilot is a beginner-friendly Streamlit app that uses Google's Gemini model to create a personalized week-by-week learning roadmap.

## Features
- Learning goal, skill level, interests, and schedule inputs
- Week-by-week topics, practice, mini-projects, resources, and checkpoints
- Milestones, study tips, and next steps
- Download the generated roadmap as JSON
- Streamlit Secrets support for keeping the API key out of source code

## Files
- `app.py` — Streamlit application
- `requirements.txt` — Python dependencies

## Run locally

1. Install Python 3.10 or newer.
2. Download or clone this repository and open a terminal in its folder.
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.streamlit` folder, then inside it create a file named `secrets.toml`.
5. Add your Gemini API key to `.streamlit/secrets.toml`:

   ```toml
   GEMINI_API_KEY = "paste-your-api-key-here"
   ```

6. Start the app:

   ```bash
   streamlit run app.py
   ```

Never commit `secrets.toml` or share your API key. Add `.streamlit/secrets.toml` to `.gitignore` if using Git locally.

## Get a Gemini API key
Create/manage a key through Google AI Studio. Use a model name that is currently available to your account. The app's model field defaults to `gemini-2.5-flash`; change it in the sidebar if your account uses another supported Gemini Flash model.

## Push to GitHub using the website UI (no Git commands)

1. Sign in at https://github.com and click **New repository**.
2. Give the repository a name such as `pathpilot-learning-roadmap`; choose Public or Private, then click **Create repository**.
3. In the new repository, select **Add file → Create new file**.
4. Name the file `app.py`; paste the full contents of `app.py` from this project and commit the file.
5. Repeat **Add file → Create new file** for `requirements.txt` and `README.md`.
6. Do **not** upload your API key or `.streamlit/secrets.toml`.

## Deploy on Streamlit Community Cloud

1. Visit https://share.streamlit.io/ and sign in with GitHub.
2. Click **Create app** (or **New app**) and select the repository, branch (usually `main`), and main file path `app.py`.
3. Open the app's **Advanced settings / Secrets** section before deploying.
4. Add this TOML secret:

   ```toml
   GEMINI_API_KEY = "paste-your-api-key-here"
   ```

5. Click **Deploy**. Streamlit Cloud installs packages from `requirements.txt`.
6. If you update the code in GitHub, Streamlit Cloud generally redeploys from the selected branch.

## Requirements and testing notes

- Python 3.10+
- A valid Gemini API key with access to the selected model
- Internet access for API calls

The app was reviewed for Python syntax and key application flows. A live Gemini API test requires your own API key and account quota; without those credentials, generation cannot be verified end-to-end. AI outputs and resource links should be checked by the user.
