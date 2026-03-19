Quickstart

1. Requirements
    - pip
    - npm
    - Node.js 15.5.12
    - Anthropic API key
    - Python 3.13

2. Clone the repo into your desired directory

3. Create & activate your virtual environment
    In project directory, run:
        python -m venv .venv (Ensure you are running the command on python 3.13, alternatively use py -3.13 -m venv .venv)
    and activate with .venv\Scripts\activate

4. Install python packages
    With venv activated, run pip install -r requirements.txt

5. Install node packages
    Run:
        cd frontend
        npm install

6. Configure .env
    Setup .env and .env.local according to example files

7. Begin hosting
    - In root directory, run:
        npx @langchain/langgraph-cli dev --port 8123 --no-browser 
    - In frontend directory, run:
        npm run dev

    Frontend should appear on http://localhost:3000