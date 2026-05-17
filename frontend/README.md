# Frontend Overview

AIDvise uses the Next.js framework to construct the application, with the CopilotKit SDK being used to connect
frontend components with the backend. Authorization is handled with the NextAuth library.

AIDvise uses React components to build the frontend. App components are defined in *./frontend/app/components*. The dashboard is rendered using the Aside component in *./navigation/aside.tsx*. Page links are made with the DefaultButton component, taking the page's HREF as a prop. Dashboard pages are defined in *./app/dashboard*. If defining a page that is meant to be accessed by only an advisor/student, it is important to enforce redirection of unauthorized users in a page's *layout.tsx* file.

Integration of agents within the CopilotKit framework is detailed in the root directory's README file.

## Session Data

Developers are provided the *authSession()* hook, defined in *@/app/lib/account/authSession*. This hook returns a session object which can be used for user authorization.

## User Context

Upon loading the dashboard, a user context is created by pulling user information by the database based on the user's ID. This user context allows for easy access of user-specific data. This includes user data & metadata as well as account-type specific data like alerts and students for students & advisors, respectively.

### Modifying User Context

The *get_curr_context* function and its related helper functions in *@/app/lib/account/account_db_utils* are used for context creation & retrieval, while the context itself is defined in *@/app/lib/account/user_context*. These two files must be modified for any modifications to user context. Refer to the documentation files for more details on implementation.

### Accessing User Context

Context data can be accessed from components within the UserContextProvider wrapper by using the *useUserData()* hook defined in *@/app/lib/account/user_context*. This hook is typically used to define component state. For example, *const { userData } : {userData: StudentData} = useUserData();* allows for userData to be accessed within a component.

## API Endpoints

AIDvise uses three api endpoints in the *@/app/api directory* for account creation, account registration, and CopilotKit integration. The first two use functions defined in *@/app/lib/account/account_db_utils.tsx* to integrate user accounts with the database. Refer to the documentation on these endpoints to integrate your own CopilotKit functionality and user creation logic.