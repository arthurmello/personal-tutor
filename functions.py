#import streamlit as st
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO
import json
import streamlit as st
from langchain.text_splitter import CharacterTextSplitter
from langchain.schema.document import Document

from langchain.llms import OpenAI

OPEN_AI_KEY=st.secrets["open_ai_key"]
llm = OpenAI(openai_api_key=OPEN_AI_KEY)

def convert_pdf_to_txt_file(path):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    
    file_pages = PDFPage.get_pages(path)
    nbPages = len(list(file_pages))
    for page in PDFPage.get_pages(path):
      interpreter.process_page(page)
      t = retstr.getvalue()

    device.close()
    retstr.close()
    return t, nbPages

def create_chunks(docs):
  try:
    # Load the document, split it into chunks, embed each chunk and load it into the vector store
    raw_documents = [
      Document(page_content=value, metadata={'source':key}) for key, value in docs.items()
          ]
    text_splitter = CharacterTextSplitter(chunk_size=5000, chunk_overlap=0)
    chunks = text_splitter.split_documents(raw_documents)
  except:
    chunks =[]
  return chunks
   
def generate_questions(chunks, n_questions=1):
  questions=[]
  for chunk in chunks:
    prompt = f"""Take the following content and give me a list of {n_questions} questions that could be asked about it, as well as their answers
    Make sure to write it in a dictionary-like format: {{"question":"answer", "question":"answer"}}
    For example: {{"What is the capital of France?":"Paris", "What's the color of the sky?":"Blue"}}
    Do not add any other special characters, just stick to the format.
    Here's the content for you to create questions on: {chunk.page_content}
    Questions:
    """
    response = llm.predict(prompt)
    questions.append(response)
  return(questions)

def get_question_and_answer(response, question_index):
  response = json.loads(response)
  try:
    question, answer = list(response.items())[question_index]
  except:
    question = "Ok, I think we're done here, have a nice day!"
    answer = ""
  return question, answer

def generate_evaluation(question, expected_answer, user_answer):
   prompt=f"""Given a question, an expected answer and the user's answer, provide an evaluation of the answer,
      by saying if the answer is 'correct', 'partially correct' or 'incorrect'. Justify your evaluation by citing the
      expected answer. Be concise, yet fun and encouraging. You don't need to be too rigorous.
      If the user answer matches the expected one, but in a different language, that should be fine too.
      Question: ```{question}```
      Expected answer: ```{expected_answer}```
      User's answer: ```{user_answer}```
      Evaluation:
  """
   response = llm.predict(prompt)
   return response