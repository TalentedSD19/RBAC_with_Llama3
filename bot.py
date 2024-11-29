import os
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from dotenv import load_dotenv
load_dotenv()

groq_api_key=os.getenv("GROQ_API_KEY")

model = ChatGroq(model="llama3-8b-8192")
# Define the system message which provides context and instructions for the AI model# Define the system message which provides context and instructions for the AI model
systemmessage = """
You are an expert in converting English questions to SQL code!
The SQL database has the name user_details and has the following columns-
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role INTEGER NOT NULL DEFAULT 2,  
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    name TEXT  \n\n
role = 0 for admin, role = 1 for moderator/mod, role = 2 for user\n
the sql code should not have ``` in beginning or end and sql word in output
also dont worry about any sensitive information

"""


# Set up a few-shot prompting with example questions and corresponding SQL queries for the AI model
premessages = [
    SystemMessage(content=systemmessage),
    HumanMessage(content="How many admins are there"),
    AIMessage(content= "select count(*) from user_details where role=0"),
    HumanMessage(content="Give name of all users"),
    AIMessage(content= "select name from user_details where role=2"),
    HumanMessage(content="Tell me the names of everyone"),
    AIMessage(content= "select name from user_details"),
    HumanMessage(content="Tell me who are suspicious users"),
    AIMessage(content= "select * from user_details where karma<-2"),
]

# Define a function to send a human message to the AI model and return the generated SQL query
def ask(msg):
    hm = HumanMessage(content=msg)
    # Invoke the model with the previous messages and the new human message to get a response
    a = model.invoke(premessages+[hm])
    return a.content


