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

- pip
- Node.js 20.9+ (tested on 24.14.0)
- Python 3.12.x

In addition, the user must gather these API keys:

### Required
- #### Anthropic
    - Go to https://platform.claude.com and create an account
    - Buy token credits under Profile (Bottom Left) -> Organization Settings -> Billing
    - Generate and copy a key in API keys
 
### Optional

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

AIDvise depends on values in the files *.env* and *.env.local* to run

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

Next, open *.env*. The following keys are required:

```.env
# AI API keys
ANTHROPIC_API_KEY=your_key

# Langchain configuration
LANGCHAIN_API_KEY=your-api-key-here
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT="AIDvise"
```

* Note: Make sure *model_select:mode* in *config.json* is set to "all-claude" if using Anthropic chat model (assumed for this guide)

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

Open *.env.local*. The following keys are required (NEXTAUTH_SECRET is automatically generated after running npx auth secret):

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
This command creates a database with the name configured in *config.json* under *database_config:db_name*. Each flag populates their respective table with the contents of the json file provided in the flag argument.

To adapt this project for your institution, the json files in *data_pipeline/jsons* can be referenced as an example of how to create your own of each type (whether manually or using a data scraping program).

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

Navigate to the registration section to test with a new account. AIDvise handles account registration by connecting new users to pre-existing database entries. If using the pre-initialized database, you can register an account with IDs 1,2,3 or 1,2,3,4 for students and advisors, respectively. Otherwise, refer to the IDs listed in *data_pipeline/jsons/students_data.json* and *data_pipeline/jsons/advisors_data.json* to see what IDs are available for account creation. After logging in, test asking a question in the Chat section of the dashboard to confirm that the backend agent is connected. 

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

# Working With Agents

AIDvise comes with two agent graphs, chat_graph and alert_graph, defined in constr.py and alert_constr.py, respectively. Agents are specified within the "graphs" property in langgraph.json, located in the root directory. Graphs are defined with the following syntax: *"graph_identifier": "./graph_directory:imported_graph_name"*. These agents can then be used on the frontend by defining them within the runtime constant in _frontend\app\api\copilotkit\route.ts_. The agents are given a name and connected by using the graph ID specified in langgraph.json. An agent with the name "default" is the one called by CopilotKit's frontend components. Other agents can be programatically controlled using React hooks, detailed in this CopilotKit documentation: https://docs.copilotkit.ai/langgraph/programmatic-control

Graphs are compiled and exported within constr.py files, located in *./lg_agent*. Nodes and other graph utilities can be defined in the _utilities_ subfolder.

## Chat Graph

The chatbot routes between two versions based on the user's account types. For students it has access to 3 sub-agents - one for getting info from the database, one for getting info from the web, and one for adding info about the user's interests and course sections they would like to track to the database. For advisors the insertion sub-agent is not needed. For student accounts restrictions are put in place to prevent the database helper from accessing information about other students. For advisors it is instead allowed to access information about any student assigned to them, though not students assigned to other advisors. Each agents can be configered with loop limits (via the config.json file) that restrict the number of times they can run per call. config.json also allows for easily switching between several test modes and AI models. To add additional models the model_inits.py file can be modified with additional cases.

## Alert Graph

The alert graph is used for event filtering to determine what upcoming events are relivent to a user. It first gather info about upcoming events and user interests from the database, then uses an AI node to perfrom the filtering, and finally updates the database to reflect the result. This is the used by the frontend for alert generation. Like with the chatbot system, the config.json file allows for easy swithcing between AI models for the event filtering node.

# Developer Documentation Links

- [Frontend Documentation](https://crystalclear1080p.github.io/Frontend-Documentation/)
- [Backend Documentation](https://lsilver17.github.io/AIDvise---Backend-Docs/html/index.html)
- [DataPipeline Documentation](https://noe-qpromecode.github.io/AIdvise-data-pipeline-docs/docs/index.html)
