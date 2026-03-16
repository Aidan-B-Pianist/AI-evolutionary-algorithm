# In search.py modify the AStarAlgorithm Class
# Doing this in python for integration purposes : Using FastAPI

# Must use an environment to run this
# ----------------------------------------------
# py -3 -m venv .venv
# .\.venv\Scripts\Activate.ps1
# python -m pip install --upgrade pip
# pip install -r requirements.txt
# -----------------------------------------------------------------------


# from fastapi import FastAPI
# from pydantic.v1 import BaseModel
from markdown_strings import *
from openai import OpenAI
import yaml

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

client = OpenAI(
    api_key=config["api-key"],
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"            
    )

# user prompts
user_prompt = "You are an expert in designing and improving code through each iteration. Improve the python code given and only return the code with no explaination or comments"


# app = FastAPI()
NUM_OF_ITERATIONS = 1

# Sequential processing first (may take a while)

starter_example = """
def aStarSearch(problem, heuristic=nullHeuristic):
    queue = PriorityQueue()

    # get current state of Pacman
    # State of current problem, parent, direction and cost of node -> parameters of Node constructor
    current_node = Node(problem.getStartState(), 'none', 'none', 0)
    queue.update(current_node, 0)

    path = []
    visited = []
    while not queue.isEmpty():
        current_node = queue.pop()
        # returns path if Pacman has reached final destination state
        if problem.isGoalState(current_node.state):
            path = current_node.getPath()
            return path

        # Search the node that has the lowest combined cost and heuristic first.
        if current_node.state not in visited:
            visited.append(current_node.state)
            for successor in problem.getSuccessors(current_node.state):
                # successor[0] = state of new node
                # succesor[1] = direction of new node
                # successor[2] = cost of new node
                total_cost = current_node.priority + successor[2]
                next_node = Node(successor[0], current_node, successor[1], total_cost)
                queue.update(next_node, total_cost + heuristic(successor[0], problem))
    return path
"""

# Grab starter code
def starter_code() -> str:
    return starter_example

# Turn it into a markdown string
def convert_to_markdown(code: str) -> str:
    return f"""## Improve this Python code
````python
{code.strip()}
```"""

def send_to_api(prompt) -> str:
    response = client.chat.completions.create(
        model = "gemini-2.5-flash",
        messages=[
        {"role": "user", "content": prompt}
        ]   
    )
    return response.choices[0].message.content

def concatenate_prompt_code(user_prompt, code) -> str:
    return user_prompt + '\n\n' + code


results = []
code = starter_code()
markdown = convert_to_markdown(code)
full_prompt = concatenate_prompt_code(user_prompt, markdown)

res = send_to_api(full_prompt)
print(res)
print("Appending res to list")
results.append(res)