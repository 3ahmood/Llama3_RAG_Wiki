import warnings
warnings.filterwarnings('ignore')

from wikipediaapi import Wikipedia
import ollama
from sentence_transformers import SentenceTransformer
import numpy as np
import sys

print('\nApplication is starting...')

model = SentenceTransformer('Alibaba-NLP/gte-base-en-v1.5', trust_remote_code=True)
state = False
embeddings_state = False

def exit():
    '''
        Function to Exit the application
    '''
    sys.exit("\n\nSee you later!")

def llama(query):
    '''
        Function to chat with Llama3 
    '''
    state = True
    response = ollama.chat(model='llama3',messages=[
    {
        'role':'user',
        'content':query,
        },
    ])
    answer = response['message']['content']
    print(f'\nUser Question : {query}\n')
    print(f"\nLlama's Response : {answer}\n")
    while (True):
        try:        
            re = int(input("\n\n1.Ask Llamma another question\n2.Return to main menu\n3.EXIT\n\n"))
        except BaseException as e:
            print("\nplease enter a valid input")
            continue
        if re == 1:
            query = str(input("\nPlease enter your query :"))
            llama(query)
        elif re == 2 :
            initiate()
        elif re == 3:
            exit()
        else:
            print("\nplease enter a valid input")
            continue

def get_embeddings(page):
    '''
        Function to generate embeddings for Wikipidea page's chunks
    '''
    try:
        wiki = Wikipedia('RAGBot/0.0','en')
        doc = wiki.page(page).text
        global paragraphs, embeddings
        paragraphs = doc.split('\n\n')
        embeddings = model.encode(paragraphs, normalize_embeddings=True)
        return paragraphs, embeddings
    except Exception as e:
        return e.value()

    
def initiate_rag():
    '''
        Function to validate and fetch Wikipedia page entered by the user
    '''
    wiki_html = str(input("\nPlease enter a valid Wikipedia page: "))
    if(len(wiki_html)<31 and 'https://en.wikipedia.org/wiki/' not in wiki_html):
        print('\nWikipedia page not found. Please enter a valid Wikipedia page\n')
        initiate_rag()
    else:
        page = wiki_html.split('/')[-1]
        paragraphs, embeddings = get_embeddings(page)
        global embeddings_state
        embeddings_state = True
        query = str(input("\nPlease enter your query: "))
        print(RAG(query))

def RAG(query):
    '''
        Function to implement the RAG functionality
    '''
    state = True
    embedded_query = model.encode(query, normalize_embeddings=True)
    similarities = np.dot(embeddings,embedded_query.T)
    top_3_indexes = np.argsort(similarities, axis=0)[-3:][::-1].tolist()
    similar_docs = [paragraphs[i] for i in top_3_indexes]
    DOCUMENT = ""
    for doc in similar_docs:
        DOCUMENT += doc+'\n\n'
    prompt = f"""
    use the following DOCUMENT to answer the QUESTION.
    If you don't know the answer, just say you don't know, don't try to make up an answer.
    
    DOCUMENT: {DOCUMENT}
    QUESTION: {query}
    """
    response = ollama.chat(model='llama3',messages=[
        {
            'role':'user',
            'content':prompt,
            },
    ])
    answer = response['message']['content']
    print(f'\nUser Question : {query}\n')
    print(f"\nLlama + RAG Response : {answer}\n")
    while (True):
        try:        
            re = int(input("\n\n1.Ask another question with RAG\n2.Return to main menu\n3.EXIT\n\n"))
        except BaseException as e:
            print("\nplease enter a valid input")
            continue
        if re == 1:
            query = str(input("Please enter your query :"))
            RAG(query)
        elif re == 2 :
            initiate()
        elif re == 3:
            exit()
        else:
            print("\nplease enter a valid input")
            continue

def initiate():
    '''
        Function to initiate the application and also present its abililties to the user
    '''
    global state
    if state is False:
        print("""\n\nHi, I am Llama. \n\nI can help you with my pre-trained knowledge or 
        \nI can go through a specific Wikipedia page and answer your related questions using it. \n\nLet me know how would you like to proceed?
        \n\nChoose anyone of the following options:""")
        state = True
    while (True):
        try:
            response = int(input("\n\n1.Llama\n2.RAG\n3.EXIT\n\n"))
        except BaseException as e:
            print("\nplease enter a valid input")
            continue
        if response == 1:
            query = str(input("\nPlease enter your query :"))
            llama(query)
        elif response == 2 and embeddings_state == False:
            initiate_rag()
        elif response == 2 and embeddings_state == True:
            query = str(input("\nPlease enter your query :"))
            RAG(query)
        elif response == 3:
            exit()
        else:
            print("\nPlease enter a valid input")
            continue

initiate()