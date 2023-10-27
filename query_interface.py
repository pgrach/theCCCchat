import os
from dotenv import load_dotenv
import pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
import langchain.vectorstores

# Load environment variables from .env file
load_dotenv()

# Fetch OpenAI and Pinecone API keys from environment variables
openai_api_key = os.getenv('OPENAI_API_KEY')
pinecone_api_key = os.getenv('PINECONE_API_KEY')
pinecone_env = os.getenv('PINECONE_ENVIRONMENT')
namespace = os.getenv('NAMESPACE', default="default_namespace")

# Initialize Pinecone and OpenAIEmbeddings
pinecone.init(api_key=pinecone_api_key, environment=pinecone_env)
embeddings = OpenAIEmbeddings()

index_name = "langchain-demo"
# Use the Pinecone index if it exists, otherwise create a new one.
try:
    docsearch = langchain.vectorstores.Pinecone.from_existing_index(index_name, embeddings, namespace=namespace)
except:
    docsearch = langchain.vectorstores.Pinecone(index_name=index_name)

llm = OpenAI(temperature=0, openai_api_key=openai_api_key)

template = """You are a chatbot having a conversation with a human.
Given the following extracted parts of a long document and a question, create a final answer.
{context}
{chat_history}
Human: {human_input}
Chatbot:"""

prompt = PromptTemplate(
    input_variables=["chat_history", "human_input", "context"], template=template
)

memory = ConversationBufferMemory(memory_key="chat_history", input_key="human_input")

chain = load_qa_chain(
    llm, chain_type="stuff", memory=memory, prompt=prompt
)

def main():
    while True:
        user_query = input("Enter your question or type 'exit' to quit: ")
        if user_query.lower() == 'exit':
            break
        docs = docsearch.similarity_search(user_query, namespace=namespace)
        answer = chain.run(input_documents=docs, question=user_query, human_input=user_query)
        print(f'Answer: {answer}')

if __name__ == "__main__":
    main()