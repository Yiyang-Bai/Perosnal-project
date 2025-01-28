import openai
import os
import logging
import sys
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, PromptTemplate
from llama_index.core.retrievers import VectorIndexRetriever

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger()
logger.addHandler(logging.StreamHandler(stream=sys.stdout))

openai.api_key = "put your api key here"

logger.info("Loading documents")
documents = SimpleDirectoryReader("data").load_data()
logger.info(f"Loaded {len(documents)} documents.")

logger.info("Creating vector store index")
index = VectorStoreIndex.from_documents(documents)
logger.info("Index created successfully.")

logger.info("Setting up query engine")
query_engine = index.as_query_engine(model="gpt-4")
logger.info("Query engine set up successfully.")

template = """You are an assistant for question-answering tasks. 
Use the following pieces of retrieved context to answer the question. 
If you don't know the answer, just say that you don't know. 
Use three sentences maximum and keep the answer concise. Answer in Chinese.
Question: {query_str} 
Context: {context_str} 
Answer:
"""
qa_template = PromptTemplate(template)

logger.info("Creating retriever")
retriever = VectorIndexRetriever(
    index=index,
    similarity_top_k=5,
)

query = "what is bert?"
logger.info(f"Query: {query}")

logger.info("Executing retrieval")
retrieved_context_list = retriever.retrieve(query)
retrieved_context = "\n".join([doc.text for doc in retrieved_context_list])
logger.info(f"Retrieved context: {retrieved_context}")

logger.info("Formatting prompt")
prompt = qa_template.format(context_str=retrieved_context, query_str=query)

logger.info("Executing query")
response = query_engine.query(prompt)

print(response)
