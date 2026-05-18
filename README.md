# Project Overview

AIDvise is a Next.js based web application that uses the LangGraph framework to orchestrate AI agents designed around providing academic support/advise to students and advisors. Users ask questions through a chat interface, invoking the backend agent which gathers data from a locally-hosted SQLite database and web tools in order to inform its response.

---

# Quickstart

## Requirements

    - pip
    - npm
    - Node.js 24.14.0
    - Next.js 16.1.6
    - Anthropic API key
    - Python 3.12.x

## Setup (Windows) (PowerShell)

### 1. Clone the repo into your desired directory

Windows PowerShell:
```powershell
git clone https://github.com/LSilver17/AIDvise
cd AIDvise
```

macOS / Linux
```bash
git clone https://github.com/LSilver17/AIDvise
cd AIDvise
```

### 2. Create & activate your virtual environment

```powershell
py -3.12 -m venv .venv
.venv\Scripts\activate
```

### 3. Install python packages

```powershell
pip install -r requirements.txt
```

### 4. Install node packages

```powershell
cd frontend
npm install
```     

### 5. Configure environment

AIDvise depends on values the files .env and .env.local to run

#### .env creation & setup

```powershell
cd ..
Copy-Item .env.example .env
```

Next, open .env. The following keys are required:

```.env
# AI API keys
ANTHROPIC_API_KEY=your_key

# Langchain configuration
LANGCHAIN_API_KEY=your-api-key-here
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT="AIDvise"
```

* Note: Make sure model_select:mode is set to all-claude in config.json if using Anthropic chat model

#### .env.local creation & setup

```powershell
cd frontend
Copy-Item .env.local.example .env.local
npx auth secret
```

Open .env.local. The following keys are required (NEXTAUTH_SECRET is automatically generated after running npx auth secret):

```.env.local
NEXTAUTH_SECRET=YOUR_SECRET
NEXTAUTH_URL=http://localhost:3000/
```

### 6. Set up database (Skip this step if you want to use preinitialized database)

To set up the database and populate catalogs run the following command in root directory: 
- python data_pipeline/database/database_dev_tools.py --setup --populate_courses courses_data.json --populate_programs programs_data.json --add_students students_data.json --add_advisors advisors_data.json
Explanation:
--setup: initializes the database structure by creating all required tables and triggers
--populate_courses courses_data.json: populates the database’s course catalog based on a provided json file (in this case courses_data.json), which should contain all courses offered by the college (this is distinct from courses offered in a given semester or course sections)
--populate_programs programs_data.json: populates the database’s programs of study catalog based on a provided json file (in this case programs_data.json), which should contain all degree and certificate programs, and their requirements, offered by the college
--add_students students_data.json: populates the database’s student catalog based on the provided json file (in this case students_data.json), which should contain a list of all students attending the college
--add_advisors advisors_data.json: populates the database’s advisor catalog based on the provided json file (in this case advisors_data.json), which should contain a list of all academic advisors at the college

To add a term and its course section offerings to the database run the following command in root directory: 
- python data_pipeline/database/database_dev_tools.py --add_term term_data.json 
Explanation:
--add_term term_data.json: populates the database with a new term entry, as well as all course sections offered for that term, based on a provided json file (in this case term_data.json)

To add events and their dates to the database run the following command in root directory: - python data_pipeline/database/database_dev_tools.py --add_events event_data.json
Explanation:
--add_events event_data.json: populates the database with events, and any dates on which they occur, based on a provided json file (in this case event_data.json)

To adapt this project for your institution these json files can be referenced as an example of how to create your own of each type (whether manually or using a data scraping program)

### 7. Begin hosting

Open a new terminal and run the following:

```powershell
.venv/Scripts/activate
npx @langchain/langgraph-cli dev --port 8123 --no-browser 
```

Open a new terminal (without closing the previous one) and run the following:

```powershell
.venv/Scripts/activate
cd frontend
npm run dev
```

### 8. Test application

The application can be accessed at http://localhost:3000

Navigate to the registration section to test with a new account. If using the pre-initialized database, you can register an account with IDs 1,2,3 or 1,2,3,4 for students and advisors, respectively. Otherwise, refer to the IDs listed in students_data/json and advisors_data.json to see what IDs are available for account creation. After logging in, test asking a question in the Chat section of the dashboard to confirm that the backend agent is connected.

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

AIDvise uses a local SQLite database to store user and academic information. 

## Accounts

Student and advisor accounts are created from preexisting entries in the Student and Advisor tables, the data of which persist even when an account is deleted. 
Registering an account involves creation of an entry in the User database which is then connected to an student/advisor entry depending on account type and ID selected in the registration form.

# Working With Agents

AIDvise comes with two agent graphs, chat_graph and alert_graph, defined in constr.py and alert_constr.py, respectively. Agents are specified within the "graphs" property in langgraph.json, located in the root directory. Graphs are defined with the following syntax: *"graph_identifier": "./graph_directory:imported_graph_name"*. These agents can then be used on the frontend by defining them within the runtime constant in _frontend\app\api\copilotkit\route.ts_. The agents are given a name and connected by using the graph ID specified in langgraph.json. An agent with the name "default" is the one called by CopilotKit's frontend components. Other agents can be programatically controlled using React hooks, detailed in this CopilotKit documentation: https://docs.copilotkit.ai/langgraph/programmatic-control

Graphs are compiled and exported within constr.py files, located in *./lg_agent*. Nodes and other graph utilities can be defined in the _utilities_ subfolder.

## Chat Graph

The chatbot routes between two versions based on the user's account types. For students it has access to 3 sub-agents - one for getting info from the database, one for getting info from the web, and one for adding info about the user's interests and course sections they would like to track to the database. For advisors the insertion sub-agent is not needed. For student accounts restrictions are put in place to prevent the database helper from accessing information about other students. For advisors it is instead allowed to access information about any student assigned to them, though not students assigned to other advisors. Each agents can be configered with loop limits (via the config.json file) that restrict the number of times they can run per call. config.json also allows for easily switching between several test modes and AI models. To add additional models the model_inits.py file can be modified with additional cases.

## Alert Graph

The alert graph is used for event filtering to determine what upcoming events are relivent to a user. It first gather info about upcoming events and user interests from the database, then uses an AI node to perfrom the filtering, and finally updates the database to reflect the result. This is the used by the frontend for alert generation. Like with the chatbot system, the config.json file allows for easy swithcing between AI models for the event filtering node.

# Frontend Components

Advise uses React components to build the frontend. App components are defined in *./frontend/app/components*. The dashboard is rendered using the Aside component in *./navigation/aside.tsx*. Page links are made with the DefaultButton component, taking the page's HREF as a prop. Dashboard pages are defined in *./app/dashboard*. If defining a page that is meant to be accessed by only an advisor/student, it is important to enforce redirection of unauthorized users in a page's *layout.tsx* file.

## Session Data

Developers are provided the *authSession()* hook, defined in *@/app/lib/account/authSession*. This hook returns a session object which can be used for user authorization.

## User Context

Upon loading the dashboard, a user context is created by pulling user information by the database based on the user's ID. This user context allows for easy access of user-specific data. This includes user data & metadata as well as account-type specific data like alerts and students for students & advisors, respectively. 

### Modifying User Context

The *get_curr_context* function and its related helper functions in *@/app/lib/account/account_db_utils* are used for context creation & retrieval, while the context itself is defined in *@/app/lib/account/user_context*. These two files must be modified for any modifications to user context.

### Accessing User Context

Context data can be accessed from components within the UserContextProvider wrapper by using the *useUserData()* hook defined in *@/app/lib/account/user_context*. This hook is typically used to define component state. For example, *const { userData } : {userData: StudentData} = useUserData();* allows for userData to be accessed within a component.

# Documentation Links

- [Frontend Documentation](https://crystalclear1080p.github.io/Frontend-Documentation/)
- [Backend Documentation](https://lsilver17.github.io/AIDvise---Backend-Docs/html/index.html)
- [DataPipeline Documentation](https://noe-qpromecode.github.io/AIdvise-data-pipeline-docs/docs/index.html)
