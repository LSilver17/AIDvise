# Project Overview

AIDvise is a Next.js based web application that uses the LangGraph framework to orchestrate AI agents designed around providing academic support/advise to students and advisors. Users ask questions through a chat interface, invoking the backend agent which gathers data from a locally-hosted SQLite database and web tools in order to inform and deliver its response.

## Features

- Two account types, students and advisors
- ### Students:
    - Integrated chat agent that can give academic advice based on academic data and personal details
    - Ability to remember user interests and generate a list of events relevant to that user based on their interests
    - Ability to track courses user is interested in to notify them of sections opening, closing, and reopening
    - Alert view displaying events and course changes relevant to the user
- ### Advisors:
    - Chat agent that can report the status of students under their guidance
    - List view of students managed by their advisor
    - Academic data overview for each student

---

# Quickstart

## Requirements

The following need to be installed for this quickstart guide:

- pip (Comes with Python)
- npm (Comes with Node.js)
- Node.js 20.9+ (Developed with 24.14.0) (https://nodejs.org/en/download)
- Python 3.12.x (https://www.python.org/downloads/release/python-31210/)

To verify installation, run:
```bash
node --version
npm --version
python --version
pip --version
```

Expected output:
```bash
v20.9+
(npm version number)
Python 3.12.x
(pip version number)
```

In addition, the user must gather these API keys:

### Required
- #### Anthropic
    - Go to https://platform.claude.com and create an account
    - Navigate to `Profile` (Bottom Left) -> `Organization Settings`
    - Navigate to `Billing` via the sidebar
    - Click the pencil icon next to `Buy Credits` to update your billing info
    - Click `Buy Credits` and select an amount to purchase
    - Navigate to `API Keys` via the sidebar
    - Click `Create Key` to generate an API Key
    - Copy the generated key to use in your `.env` file

### Optional
- #### OpenAI
    - Go to https://platform.openai.com/home and create an account
    - Navigate to `Billing` via the sidebar
    - Click `Add Payment Details` and fill out the form with billing information
    - Select an ammount for your initial credit purchase
    - Navigate to `API Keys` via the sidebar
    - Click `Create New Secret Key` to generate an API key
    - Copy the generated key to use in your `.env` file
Use this only if you switch one or more model slots in `config.json` (`model_select`) to an OpenAI-backed model.

- #### OpenRouter
    - Go to https://openrouter.ai/ and create an account
    - Click `Get API Key`
    - Click `New Key` to generate your API Key
    - Copy the generated key to use in your `.env` file
    - If you plan to use a paid model:
        - Navigate to `Credits` via the sidebar
        - Click `Add Credits`
        - Fill out the form with a billing method
        - Select an amount to purchase
Use this only if you switch one or more model slots in `config.json` (`model_select`) to an OpenRouter-backed model.

- #### LangChain
    - Go to https://smith.langchain.com/ and create an account
    - Navigate to settings via the sidebar
    - Click `API Key` to generate your key
    - Copy the generated key to use in your `.env` file
Needed only if you want LangSmith tracing/observability.

## Setup

### 1. Clone the repo into your desired directory

```bash
git clone https://github.com/LSilver17/AIDvise
cd AIDvise
```

### 2. Create & activate your virtual environment

Windows (PowerShell):
```powershell
py -3.12 -m venv .venv
.venv\Scripts\activate
```

macOS / Linux:
```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

### 3. Install python packages

```bash
pip install -r requirements.txt
```

### 4. Install node packages

```bash
cd frontend
npm install
```     

### 5. Configure environment

AIDvise depends on values in the files `.env` and `.env.local` to run

#### .env creation & setup

Windows (PowerShell):
```powershell
cd ..
Copy-Item .env.example .env
```

macOS / Linux:
```bash
cd ..
cp .env.example .env
```


Next, open `.env`. The following keys are required:

```.env
# AI API keys
ANTHROPIC_API_KEY=your_key
```

* Note: Make sure `model_select:mode` in `config.json` is set to "all-claude" if using Anthropic chat model (assumed for this guide)

#### .env.local creation & setup

Windows (PowerShell):
```powershell
cd frontend
Copy-Item .env.local.example .env.local
npx auth secret
```

macOS / Linux:
```bash
cd frontend
cp .env.local.example .env.local
npx auth secret
```

Open `.env.local`. The following keys are required (NEXTAUTH_SECRET is automatically generated after running npx auth secret):

```.env.local
NEXTAUTH_SECRET=YOUR_SECRET
NEXTAUTH_URL=http://localhost:3000/
```


Finally, switch back to root:

```bash
cd ..
```

### 6. Set up database (Skip this step if you want to use preinitialized database)

```bash
- python data_pipeline/database/database_dev_tools.py --setup --populate_courses courses_data.json --populate_programs programs_data.json --add_students students_data.json --add_advisors advisors_data.json --add_term term_data.json --add_events event_data.json
```
This command creates a database with the name configured in `config.json` under `database_config:db_name`. Each flag populates their respective table with the contents of the json file provided in the flag argument.

To adapt this project for your institution, the json files in `data_pipeline/jsons` can be referenced as an example of how to create your own of each type (whether manually or using a data scraping program).

### 7. Begin hosting

Open two new terminals and run the following in each terminal:

#### Terminal 1

Windows (PowerShell):
```powershell
.venv/Scripts/activate
npx @langchain/langgraph-cli dev --port 8123 --no-browser 
```

macOS / Linux:
```bash
source .venv/bin/activate
npx @langchain/langgraph-cli dev --port 8123 --no-browser 
```

#### Terminal 2

Windows (PowerShell):
```powershell
.venv/Scripts/activate
cd frontend
npm run dev
```

macOS / Linux:
```bash
source .venv/bin/activate
cd frontend
npm run dev
```

### 8. Test application

The application can be accessed at http://localhost:3000

Navigate to the registration section to test with a new account. AIDvise handles account registration by connecting new users to pre-existing database entries. If using the pre-initialized database, you can register an account with IDs 1,2,3 or 1,2,3,4 for students and advisors, respectively. Otherwise, refer to the IDs listed in `data_pipeline/jsons/students_data.json` and `data_pipeline/jsons/advisors_data.json` to see what IDs are available for account creation. After logging in, test asking a question in the Chat section of the dashboard to confirm that the backend agent is connected. 

## Users

The application supports the creation of two types of user accounts, students and advisors. Users interact with the software via a dashboard interface.

### Students

Students have access to a chat agent that is capable of listening to a students goals and interests and providing relevant advice based on their personal 
goals and preferences. Based on conversations, the AI can record information in the database, such as a student's interests, to supplement 
Based on a student's interests, the AI is capable of generating alerts for events and courses relevant to the student, which is accessible from the alerts page.
Alerts are organized as seen and unseen and listed in order of recency. Updates to a section status (Opening, Closing, Reopening) for courses a student has expressed
interest in creates an alert. The "Generate new alerts" button invokes a seperate agent for generating alerts based on the interests of the student.

### Advisors

Advisors have access to a list view of all the students under their guidance as well as their own chat agent. Asking the chat agent about a student will have them
summarize details about a student like academic information as well as their interests expressed within conversations.

# Database

AIDvise uses a local SQLite database to store user and academic information, including college catalogs, term offerings, user accounts, student/advisor profiles, events, and alert tracking metadata.

## Schema & Catalogs

The database is organized into several key catalog tables:

- **Courses**: Master list of college courses with department, code, title, description, credits, prerequisite notes, and semesters typically offered.
- **Programs of Study**: Degree and certificate programs with their required courses and alternative requirement options.
- **Terms**: Semester/year schedule data, including which courses are offered, specific class sections (instructors, dates, capacity, delivery method, status), and meeting times.
- **Events**: Campus events (workshops, orientations, deadlines) with their scheduled dates and times.
- **Students & Advisors**: User profiles linked to login accounts, including academic history, interests, and advising relationships.

## Accounts

Student and advisor accounts are created from preexisting entries in the Student and Advisor tables, the data of which persist even when an account is deleted. 
Registering an account involves creation of an entry in the User database which is then connected to a student/advisor entry depending on account type and ID selected in the registration form.

## Database CLI

A command-line helper script is provided to manage the local SQLite database used by the project. The script is `data_pipeline/database/database_dev_tools.py` and supports creating the schema, populating tables from JSON files, and destructive reset operations. Run it from the project root inside your Python virtual environment.

Basic usage examples:

```bash
# Create the schema and populate core tables
python data_pipeline/database/database_dev_tools.py --setup \
    --populate_courses jsons/courses_data.json \
    --populate_programs jsons/programs_data.json \
    --add_students jsons/students_data.json \
    --add_advisors jsons/advisors_data.json \
    --add_term jsons/term_data.json \
    --add_events jsons/event_data.json

# Add only events from a JSON file
python data_pipeline/database/database_dev_tools.py --add_events jsons/event_data.json

# Reset and re-create only the course catalog
python data_pipeline/database/database_dev_tools.py --reset course_catalog --populate_courses jsons/courses_data.json
```

Available flags:

- `--setup`: create the full database schema and triggers.
- `--populate_courses <file>`: load courses from a JSON file in `data_pipeline/jsons`.
- `--populate_programs <file>`: load programs of study from a JSON file.
- `--add_students <file>`: add student records and histories from a JSON file.
- `--add_advisors <file>`: add advisor records from a JSON file.
- `--add_term <file>`: add a single term and its offerings from a JSON file.
- `--add_events <file>`: add events and their dates from a JSON file.
- `--reset <group>`: drop tables for a group. Valid groups: `course_catalog`, `programs_catalog`, `terms_and_courses`, `events`, `users`, `all`.

Important notes:

- The script reads the database filename from `config.json` (`database_config.db_name`). Ensure that value is correct before running destructive `--reset` operations.
- Reset options are destructive and permanently delete data. Use with caution and backups if necessary.

# Data Scraping
The data pipeline uses QCC(Quinsigamond Community College) as a proof of concept but can be adapted for other institutions. The scraper URLs and field parsing logic can be updated to target any college or university, while the JSON output schema and backend integration remain unchanged. See data_pipeline/README.md for full adaptation instructions.

## Adapting for Other Institutions
To adapt it for a different institution:

### 1. Registration Data (The Q Portal / Jenzabar)
If the institution uses Jenzabar, the scraper may work with minimal changes.
Update the search URL in `refresh_registration.py`:
```python
SEARCH_URL = "https://[institution-portal-url]/..."
TERM       = "Fall 2026"  # Update each semester accordingly
```
### 2. Public Course & Program Pages
If the institution has a different website structure, update the URLs and adjust the field parsing logic in `scrape_classes_page.py` and `scrape_programs.py`:
```python
CLASSES_URL  = "https://[institution].edu/classes"
PROGRAMS_URL = "https://[institution].edu/programs"
```
The line-scanning extraction approach is flexible — update the label patterns
(e.g. "Credits", "Prerequisites") to match whatever labels the target site uses.

### 3. JSON Output Schema
The JSON output schema and backend integration do not need to change.
Only the scraper URLs and parsing logic need to be updated per institution.

# Working With Agents

AIDvise comes with two agent graphs, chat_graph and alert_graph, defined in constr.py and alert_constr.py, respectively. Agents are specified within the "graphs" property in `langgraph.json`, located in the root directory. Graphs are defined with the following syntax: `"graph_identifier": "./graph_directory:imported_graph_name"`. These agents can then be used on the frontend by defining them within the runtime constant in `frontend\app\api\copilotkit\route.ts`. The agents are given a name and connected by using the graph ID specified in `langgraph.json`. An agent with the name "default" is the one called by CopilotKit's frontend components. Other agents can be programatically controlled using React hooks, detailed in this CopilotKit documentation: https://docs.copilotkit.ai/langgraph/programmatic-control

Graphs are compiled and exported within constr.py files, located in `./lg_agent`. Nodes and other graph utilities can be defined in the _utilities_ subfolder.

## Chat Graph

The Chat Graph powers the chat assistant you use in the dashboard. When you ask a question, the system decides how to find the answer by consulting a small set of helpers:

- **Database helper:** looks up official campus data (courses, programs, student records) stored locally.
- **Web helper:** searches public web pages when the database doesn't contain the needed information.
- **Insertion helper (students only):** saves things you tell the assistant (for example, interests or course sections you want to track) into your profile.

For students, the assistant can only read or write the student's own data. Advisors can access information for the students they advise. The system includes safety limits so helpers only run a few times per question—this keeps responses fast and predictable. You can change high-level behavior (which AI model is used, how many attempts helpers get, etc.) by editing `config.json`.

## Alert Graph

The Alert Graph is the background process that creates personalized alerts for students (event reminders, section status changes, etc.). In plain terms it:

- Collects recent campus events and the student's saved interests.
- Uses the assistant to decide which events are relevant to that student.
- Saves the matching events so they appear on the Alerts page.

Alert generation runs when you press "Generate new alerts" in the UI. The module is designed to surface useful items without flooding the student with irrelevant results. Like the chat assistant, the alert process can be configured from `config.json` to use different AI profiles.

## Configuration (config.json)

The `config.json` file controls important runtime settings for the application. Editing it lets you change behavior without touching source code.

### End-User Settings

- **database_config.db_name:** the filename of the local SQLite database the app uses. Change this if you want to switch between different database instances.
- **loop_limits:** how many times helper components (planning, database, web search, insertion) may run during a single request. Lower values make responses faster; higher values allow more thorough searches but may be slower.
- **model_select:** groups named AI model profiles. The `mode` field picks which profile to use. Each profile specifies which AI model powers planning, database queries, web searches, insertions, and alerts. Use this to switch between different AI providers or cost-optimization strategies without restarting.

After editing `config.json`, restart the backend service (see Quickstart step 7) so changes take effect.

#### Adding a New Model Profile

To add a new profile (for example, a budget-friendly or experimental setup), edit the `model_select` object in `config.json`:

```json
"model_select": {
  "mode": "my_new_profile",
  "all_claude": { /* existing profile */ },
  "my_new_profile": {
    "planning": "gpt-4",
    "db": "gpt-4-turbo",
    "web": "gpt-3.5-turbo",
    "insertion": "gpt-3.5-turbo",
    "alerts": "gpt-3.5-turbo"
  }
}
```

Then change the `mode` field to point to your new profile name. Each field must reference a model that is defined in `lg_agent/utilities/model_inits.py`.

### Developer Settings

These options control internal behavior and are intended for testing and debugging, not production use.

- **context_config:** controls what information and helper tools the chat assistant has available. Options like `full` (all helpers: database, web, insertion), `some-db` (limited database access), `no-db` (only web and insertion), and `no-tools` (planning only, no external helpers). **Important:** changing this doesn't just adjust the AI prompt, it actually enables or disables which helper nodes are available. Most modes work standalone, but `some-db` requires manual tool restrictions via `tool_select` to actually enforce limited access. This is useful for testing specific components but not recommended for end users.
- **tool_select:** turn specific tools on or off. Used for isolated testing of individual features.

### Adding a New AI Model

To add support for a new AI model provider or configuration, edit `lg_agent/utilities/model_inits.py` and add a case to the `_create_model` function:

```python
def _create_model(model_name: str, node_type: str):
    normalized = _normalize_model_name(model_name)
    
    match normalized:
        case "sonnet_4_6":
            if env := os.getenv("ANTHROPIC_API_KEY"):
                return ChatAnthropic(model="claude-sonnet-4-6", temperature=0.2)
            else:
                raise ValueError("ANTHROPIC_API_KEY not found in environment variables.")
        # ...
        case "claude_3_5_sonnet":
            if env := os.getenv("ANTHROPIC_API_KEY"):
                return ChatAnthropic(model="claude-3-5-sonnet-20241022", temperature=0)
            else:
                raise ValueError("ANTHROPIC_API_KEY not found in environment variables.")
        case "gpt_4":
            if env := os.getenv("OPENAI_API_KEY"):
                return ChatOpenAI(model="gpt-4", temperature=0.2)
            else:
                raise ValueError("OPENAI_API_KEY not found in environment variables.")
        case "my_custom_model":
            if env := os.getenv("OPENROUTER_API_KEY"):
                return ChatOpenRouter(model="custom-model-id", temperature=0)
            else:
                raise ValueError("OPENROUTER_API_KEY not found in environment variables.")
        # ...
        case _:
            raise ValueError(f"Unknown model: {model_name}")
```

Once added, you can reference the new model name in your `model_select` profiles in `config.json` (e.g., `"planning": "my_custom_model"`). Make sure the corresponding API key is available in your `.env` file.

#### Provider-specific `.env` setup

If you stay with the default Anthropic setup, you only need `ANTHROPIC_API_KEY` in `.env`.

If you switch any model slots in `config.json` to a different provider, also add the matching key in `.env`:

- OpenAI models use `OPENAI_API_KEY`
- OpenRouter models use `OPENROUTER_API_KEY`

#### LangSmith tracing setup

If you want to utylize LangSmith features like ein-depth graph tracing or testing datasets, add these values to `.env`:

- `LANGCHAIN_API_KEY`: your LangSmith API key
- `LANGCHAIN_TRACING_V2=true`: turns tracing on
- `LANGCHAIN_PROJECT`: the project name you want to group traces under

This setup is optional and mainly intended for developers who want to debug or inspect agent behavior. If you do not need tracing, you can leave these values out.

### Developer: Testing with `model_inits.py`

Use `lg_agent/utilities/model_inits.py` to add new test profiles and `FakeChatModel` variants for the chat and alert graphs.

- Add a new profile under `model_select` in `config.json`.
- Add a matching case in `_create_model()` inside `model_inits.py`.
- Create one or more helper functions that return `FakeChatModel(...)` instances with the message sequence you want to test.
- Set `model_select.mode` to your new profile before importing the graphs.

Adding a new test profile:

```json
"model_select": {
  "mode": "student_tool_test",
  "student_tool_test": {
    "planning": "student_planning_test_v2",
    "db": "student_db_test_v2",
    "web": "tool_test",
    "insertion": "tool_test",
    "alerts": "test"
  }
}
```

Then add the matching cases in `model_inits.py`:

```python
case "student_planning_test_v2":
    return _my_new_student_planner_test_model()
case "student_db_test_v2":
    return _my_new_student_db_test_model()
```

Creating a new `FakeChatModel` instance:

```python
from langchain_core.messages import AIMessage, ToolCall
from utilities.TestModel import FakeChatModel

def _my_new_student_planner_test_model() -> FakeChatModel:
    return FakeChatModel(
        messages=iter([
            AIMessage(
                content='{"requires_database": true, "info_needed_db": "Test the new profile."}',
                tool_calls=[
                    ToolCall(
                        name="get_current_time",
                        args={},
                        id="time-1"
                    )
                ]
            ),
            AIMessage(content='{"answer": "Done."}'),
        ])
    )
```

Use these fake models to drive specific graph behavior, such as forcing tool calls, testing loop limits, or checking fallback paths.

Simple test example:

```python
import asyncio
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool

import lg_agent.utilities.model_inits as model_inits

@tool
def fixed_current_time() -> str:
    return "2026-05-18 12:00 PM"


model_inits.planning_llm = model_inits.planning_llm.bind_tools(
    tools=[fixed_current_time],
    runtime_state={},
)

from lg_agent.s_chat_graph import s_chat_graph

async def main():
    state = {
        "messages": [HumanMessage(content="Run tool tests")],
        "plan": {},
        "loop_count": 0,
        "user_id": 1,
    }
    result = await s_chat_graph.ainvoke(state)
    assert "messages" in result
    assert result["messages"]

    final_message = result["messages"][-1]
    executed_calls = final_message.additional_kwargs.get("executed_tool_calls", [])
    assert executed_calls
    assert executed_calls[0]["name"] == "fixed_current_time"
    assert executed_calls[0]["output"] == "2026-05-18 12:00 PM"

asyncio.run(main())
```

# Frontend Components

Advise uses React components to build the frontend. App components are defined in `./frontend/app/components`. The dashboard is rendered using the Aside component in `./navigation/aside.tsx`. Page links are made with the DefaultButton component, taking the page's HREF as a prop. Dashboard pages are defined in `./app/dashboard`. If defining a page that is meant to be accessed by only an advisor/student, it is important to enforce redirection of unauthorized users in a page's `layout.tsx` file.

## Session Data

Developers are provided the `authSession()` hook, defined in `@/app/lib/account/authSession`. This hook returns a session object which can be used for user authorization.

## User Context

Upon loading the dashboard, a user context is created by pulling user information by the database based on the user's ID. This user context allows for easy access of user-specific data. This includes user data & metadata as well as account-type specific data like alerts and students for students & advisors, respectively. 

### Modifying User Context

The `get_curr_context` function and its related helper functions in `@/app/lib/account/account_db_utils` are used for context creation & retrieval, while the context itself is defined in `@/app/lib/account/user_context`. These two files must be modified for any modifications to user context.

### Accessing User Context

Context data can be accessed from components within the UserContextProvider wrapper by using the `useUserData()` hook defined in `@/app/lib/account/user_context`. This hook is typically used to define component state. For example, `const { userData } : {userData: StudentData} = useUserData();` allows for userData to be accessed within a component.

# Developer Documentation Links

- [Frontend Documentation](https://crystalclear1080p.github.io/Frontend-Documentation/)
- [Backend Documentation](https://lsilver17.github.io/AIDvise---Backend-Docs/html/index.html)
- [DataPipeline Documentation](https://noe-qpromecode.github.io/AIdvise-data-pipeline-docs/docs/index.html)

# Credits
Luca Silver | Agent & Database Design | [Profile](https://github.com/LSilver17)
Sean Collins | Frontend Design & User Management| [Profile](https://github.com/crystalclear1080p)
Noel Mensah | Data Management | [Profile](https://github.com/noe-Qpromecode)
