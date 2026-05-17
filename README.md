# Quickstart

1. Requirements
    - pip
    - npm
    - Node.js 15.5.12
    - Anthropic API key
    - Python 3.12.x

2. Clone the repo into your desired directory

3. Create & activate your virtual environment
    In project directory, run:
        python -m venv .venv (Ensure you are running the command on python 3.12, alternatively use py -3.12 -m venv .venv)
    and activate with ".venv\Scripts\activate"

4. Install python packages
    With venv activated, run "pip install -r requirements.txt"

5. Install node packages
    Run:
        cd frontend
        npm install

6. Configure .env
    Setup .env and ./frontend/.env.local according to example files
    - Running the following command in the frontend dir. will generate a NEXTAUTH_SECRET key and place it in .env.local:
        npx auth secret

7. Set up database
    To set up the database and populate catalogs run the following command in root directory:
        python data_pipeline/database/database_dev_tools.py --setup --populate_courses courses_data.json --populate_programs programs_data.json --add_students students_data.json --add_advisors advisors_data.json
    To add a term and its course section offerings to the database run the following command from root directory:
        python data_pipeline/database/database_dev_tools.py --add_term term_data.json
    To add events and their dates to the database runt the following command from root directory:
        python data_pipeline/database/database_dev_tools.py --add_events event_data.json

8. Begin hosting
    - In root directory, run:
        npx @langchain/langgraph-cli dev --port 8123 --no-browser 
    - In frontend directory, run:
        npm run dev

    Frontend should appear on http://localhost:3000

# Project Overview

AIDvise is a Next.js based web application that uses the LangGraph framework to orchestrate AI agents. The purpose of this application is to use agents
as a virtual advisor/planner, with capabilities of offering personalized advice to students and student reporting to advisors. The purpose of this project
is to supplement the academic advising process by providing students with a virtual advisor to answer general questions based on a students needs and
give advisors the ability to gather information about the students under their guidance.

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