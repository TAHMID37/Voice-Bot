from dotenv import dotenv_values
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

config = dotenv_values(".env")
Groq_API_KEY=config['GROQ_API_KEY']
openai_api_key=config['OPENAI_API_KEY']

model_gpt_4o_mini = ChatOpenAI(
    model="gpt-4o-mini-2024-07-18",
    streaming=True,
    temperature=0.05, 
    api_key=openai_api_key
)

llm = ChatGroq(
    model="mixtral-8x7b-32768",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key=Groq_API_KEY
)
