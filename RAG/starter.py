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


logger.info("加载文档")
documents = SimpleDirectoryReader("data").load_data()
logger.info(f"加载了 {len(documents)} 个文档")

logger.info("创建向量存储索引")
index = VectorStoreIndex.from_documents(documents)
logger.info("索引创建成功")


logger.info("设置查询引擎")
query_engine = index.as_query_engine(model="gpt-4")
logger.info("查询引擎设置成功")


template = """You are an assistant for question-answering tasks. 
Use the following pieces of retrieved context to answer the question. 
If you don't know the answer, just say that you don't know. 
Use three sentences maximum and keep the answer concise 用中文回答问题.
Question: {query_str} 
Context: {context_str} 
Answer:
"""
qa_template = PromptTemplate(template)


logger.info("创建检索器")
retriever = VectorIndexRetriever(
    index=index,
    similarity_top_k=5,
)


query = "what is bert？"
logger.info(f"查询: {query}")


logger.info("执行检索")
retrieved_context_list = retriever.retrieve(query)
retrieved_context = "\n".join([doc.text for doc in retrieved_context_list])
logger.info(f"检索到的上下文: {retrieved_context}")


logger.info("格式化提示")
prompt = qa_template.format(context_str=retrieved_context, query_str=query)


logger.info("执行查询")
response = query_engine.query(prompt)


print(response)

