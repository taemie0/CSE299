#@title Query expansion
import requests
from langchain.prompts import ChatPromptTemplate
from langchain_community.llms import Ollama
import re

PROMPT_TEMPLATE = """
    You are creating questions for 9-10 grade students. Given the following prompt: '{prompt}', rewrite it into 5 more refined and specific questions. Provide only the questions, without any additional information or context.
    """

def query_enhancement(question):
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(prompt=question)

    print("\n\n\n------------prompt----------------\n")
    print(prompt)

    try:
        # Assuming Ollama is a model interface you have imported or defined elsewhere. Update accordingly if it has a different method.
        # Import or define the Ollama class
        # from ollama import Ollama  # Uncomment this line if Ollama is defined in another module

        model = Ollama(model="qwen2.5:1.5b")
        response = model.invoke(prompt)

        # Debugging: Print the raw response to understand what is being returned
        print("\n\n\n------------Raw Response----------------\n")
        print(response)

        # Assuming 'response' is a dictionary containing a 'response' key
        if isinstance(response, dict) and 'response' in response:
            questions = re.split(r'\n\d+\.\s', response['response'].strip())
            # Remove any empty strings from the list
            questions = [q for q in questions if q]
            print("\n\n\n------------5 Questions----------------\n")
            print(questions)
            return questions
        else:
            print("Oops! Something went wrong in retrieving questions!")
            return ["Unable to generate questions. Please try again later."]

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return ["Error occurred while processing the request."]

