from langchain_openai import AzureChatOpenAI
from dotenv import load_dotenv
load_dotenv()
llm = AzureChatOpenAI(   # or your api version
    timeout=None,
    max_retries=2,
    model="gpt-5-mini",  # or your deployment  # or your api version
    api_version='2025-03-01-preview'
    # other params...
)
print(llm.invoke( "What is the airspeed of a laden swallow?"))