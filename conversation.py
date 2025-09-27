from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

load_dotenv()
LIARA_API_KEY = os.getenv("LIARA_API_KEY")
if not LIARA_API_KEY:
    raise ValueError("LIARA_API_KEY is not set in environment variables.")
OPENAI_API_BASE=os.getenv('OPENAI_API_BASE')
if not OPENAI_API_BASE:
    raise ValueError("OPENAI_API_BASE is not set in envirement variables")
# Configure for Liara
os.environ["OPENAI_API_KEY"] = LIARA_API_KEY
os.environ["OPENAI_API_BASE"] = OPENAI_API_BASE

# Memory (shared)
memory = ConversationBufferMemory(memory_key="history", return_messages=True)

def get_conversation(model_name: str):
    """Return a ConversationChain with the selected model."""
    chat_model = ChatOpenAI(
        model=model_name,
        temperature=0,
        streaming=True,
    )
    return ConversationChain(llm=chat_model, memory=memory, verbose=True)
