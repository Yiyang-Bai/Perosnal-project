import time
import openai
import logging
import sys
import os
from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain_community.chat_models import ChatOpenAI
from langchain.evaluation import load_evaluator
from langchain_community.cache import InMemoryCache
from langchain.callbacks import StdOutCallbackHandler
from langchain.chains import LLMChain, MapReduceDocumentsChain, StuffDocumentsChain, ReduceDocumentsChain
from langchain.schema.runnable import RunnableSequence, RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger()
logger.addHandler(logging.StreamHandler(stream=sys.stdout))

api_key = "put your api key here"
os.environ["OPENAI_API_KEY"] = api_key

logger.info("Logging configured successfully, API key set.")

loader = TextLoader('C:/Users/AAA/Desktop/llama-index and langchain/data/book.txt', encoding='utf-8')
documents = loader.load()
logger.info(f"Loaded {len(documents)} documents.")

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
chunks = text_splitter.split_documents(documents)
logger.info(f"Split documents into {len(chunks)} chunks.")

embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")

vectorstore = Chroma.from_documents(documents=chunks, embedding=embeddings)
logger.info("Vector database initialized and documents embedded.")

retriever = vectorstore.as_retriever()
logger.info("Retriever configured.")

llm = ChatOpenAI(model="gpt-4", temperature=0.1)

map_prompt = PromptTemplate.from_template("Summarize this text: {page_content}")
reduce_prompt = PromptTemplate.from_template("Combine these summaries: {context}")

map_llm_chain = LLMChain(llm=llm, prompt=map_prompt)
reduce_llm_chain = LLMChain(llm=llm, prompt=reduce_prompt)

combine_documents_chain = StuffDocumentsChain(
    llm_chain=reduce_llm_chain,
    document_prompt=PromptTemplate.from_template("{page_content}"),
    document_variable_name="context"
)

reduce_documents_chain = ReduceDocumentsChain(
    combine_documents_chain=combine_documents_chain,
)

map_reduce_chain = MapReduceDocumentsChain(
    llm_chain=map_llm_chain,
    reduce_documents_chain=reduce_documents_chain,
)

logger.info("MapReduceDocumentsChain created.")

batch_size = 10
delay = 1
all_summaries = []
for i in range(0, len(chunks), batch_size):
    batch = chunks[i:i + batch_size]
    summary = map_reduce_chain.run(batch)
    all_summaries.append(summary)
    time.sleep(delay)
combined_context = " ".join(all_summaries)

rag_prompt_template = """You are an assistant for question-answering tasks. 
Use the following pieces of retrieved context to answer the question. 
If you don't know the answer, just say that you don't know. 
Use three sentences maximum and keep the answer concise.
Question: {question} 
Context: {context} 
Answer:
"""
rag_prompt = ChatPromptTemplate.from_template(rag_prompt_template)

rag_chain = RunnableSequence(
    {"context": combined_context, "question": RunnablePassthrough()},
    rag_prompt,
    llm,
    StrOutputParser()
)

query = "what is this book"
response = rag_chain.invoke(query)
print("RAG Chain Response: ", response)

logger.info("RAG Chain execution completed.")
