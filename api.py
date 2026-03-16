# In search.py modify the AStarAlgorithm Class
# Must use an environment to run this

# ----------------------------------------------
# py -3 -m venv .venv
# .\.venv\Scripts\Activate.ps1
# python -m pip install --upgrade pip
# pip install -r requirements.txt
# -----------------------------------------------------------------------

from openai import AsyncOpenAI
import yaml
import asyncio

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

async_client = AsyncOpenAI(
    api_key=config["api-key"],
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"            
    )


NUM_OF_ITERATIONS = 3 # However many iterations we want
NUM_BEST = 10   # best 10 highest scored python codes
MAX_NUM = 100   # array index of results

API_SEMAPHORE = asyncio.Semaphore(5) # 5 concurrent requests at a time

# user prompts
beginning_user_prompt = "You are an expert in designing and improving code through each iteration. Improve the python code given and only return the code with no explaination or comments"
improvement_user_prompt = "You are an expert in designing and improving python code in regards to pacman search agents. You are given the " + str(NUM_BEST) + " best python code that performed out of " + str(MAX_NUM) + ". Improve the python code even further"
"only returning the code with no explaination or comments."

#starter example
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
# Concurrent API sending using semaphores to not hit RPM (RPM = 15 for gemini-3.1-flash-lite-preview)
async def send_to_api(prompt, task_id: int = 0) -> str:
    async with API_SEMAPHORE:
        for attempt in range(5):
            try:
                response = await asyncio.wait_for(
                    async_client.chat.completions.create(
                        model="gemini-3.1-flash-lite-preview",
                        messages=[{"role": "user", "content": prompt}]
                    ),
                    timeout=60 # 1 minute
                )
                print(f"[Task {task_id}] Success on attempt {attempt + 1}")
                return response.choices[0].message.content

            except asyncio.TimeoutError:
                print(f"[Task {task_id}] Timed out on attempt {attempt + 1}")
                continue

            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg:
                    wait = 15 * (2 ** attempt) # exponential backoff for error handling just in case
                    print(f"[Task {task_id}] Rate limited (attempt {attempt + 1}/5). "
                          f"Waiting {wait}s...")
                    await asyncio.sleep(wait)
                else:
                    print(f"[Task {task_id}] Non-retryable error: {error_msg}")
                    raise

        raise Exception(f"Task {task_id}: Max retries exceeded")

def concatenate_prompt_code(user_prompt, code) -> str:
    return user_prompt + '\n\n' + code


async def main(code_list: list[str] | None = None) -> list[str]:
    arr = []
    print("Running API Scripts...\n")
    if code_list is None:
        code_list = [starter_code()] * 10
    else:
        code_list = code_list[:10]

    for i in range(NUM_OF_ITERATIONS):
        print(f"\n=== Iteration {i + 1}/{NUM_OF_ITERATIONS} ===")

        prompts = [concatenate_prompt_code(beginning_user_prompt, convert_to_markdown(code))
                for code in code_list]

        # Use asyncio.create_task so they actually start with stagger
        tasks = []
        for idx, p in enumerate(prompts):
            task = asyncio.create_task(send_to_api(p, task_id=idx + 1))
            tasks.append(task)
            await asyncio.sleep(2)  # Stagger tasks so our RPM isn't too high

        results = await asyncio.gather(*tasks, return_exceptions=True)
        arr.append(results)
        for j, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"Result {j + 1} Failed: {result}")
            else:
                print(f"Result {j + 1} Passed")

        if i < NUM_OF_ITERATIONS - 1:
            print("Cooling down between iterations (60s)... [API RPM is only 15 \(0_0)/]")
            await asyncio.sleep(60)

    return arr

if __name__ == "__main__":
    asyncio.run(main())