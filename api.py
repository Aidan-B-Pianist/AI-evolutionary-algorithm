# ----------------------------------------------
# py -3 -m venv .venv
# .\.venv\Scripts\Activate.ps1
# python -m pip install --upgrade pip
# pip install -r requirements.txt
# -----------------------------------------------------------------------
# To call this manually
# python api.py inFileName.txt NUM_OF_ITERATIONS
# ---------------------------------------------------

from openai import AsyncOpenAI
import yaml
import asyncio
import sys

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

async_client = AsyncOpenAI(
    api_key=config["api-key"],
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"            
    )

# If called from the command line
if len(sys.argv) > 1:
    codeIn = ""
    with open(sys.argv[1], "r") as f:
        codeIn = f.read()
    BASE_CODE = codeIn

    NUM_OF_ITERATIONS = int(sys.argv[2]) # The number of candidates to generate.
    NUM_BEST = int(sys.argv[2])   

API_SEMAPHORE = asyncio.Semaphore(5) # 5 concurrent requests at a time

# user prompts
beginning_user_prompt = "You are an expert in designing and improving code through each iteration. Improve the python code given and only return the code with no explaination or comments"
improvement_user_prompt = "You are an expert in designing and improving python code in regards to effiency. You are given the best python code that performed out of many. Improve the python code even further, only returning the code with no explaination or comments."

#starter example
starter_example = """
Print the Fibonnaci Sequence
n = 10
a = 0
b = 1
next = b  
count = 1

while count <= n:
    print(next, end=" ")
    count += 1
    a, b = b, next
    next = a + b
print()
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


async def main(code_list: list[str] | None = None, NUM_BEST: int | None = None, NUM_OF_ITERATIONS: int | None = None) -> list[str]:
    arr = []
    print("Running API Scripts...\n")
    if code_list is None:
        code_list = [starter_code()] * NUM_BEST
    else:
        code_list = code_list[:NUM_BEST]

    for i in range(NUM_OF_ITERATIONS):
        print(f"\n=== Iteration {i + 1}/{NUM_OF_ITERATIONS} ===")

        prompts = [concatenate_prompt_code(beginning_user_prompt, code) #convert_to_markdown(code) was skipped using human in the loop
                for code in code_list]

       # Use asyncio.create_task so they actually start with stagger
        tasks = []
        for idx, p in enumerate(prompts):
            task = asyncio.create_task(send_to_api(p, task_id=idx + 1))
            tasks.append(task)
            await asyncio.sleep(2)  # Stagger tasks so our RPM isn't too high

        results = await asyncio.gather(*tasks, return_exceptions=True)
        arr.append(results[0])
        for j, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"Result {j + 1} Failed: {result}")
            else:
                print(f"Result {j + 1} Passed")

        # if i < NUM_OF_ITERATIONS - 1:
        #     print("Cooling down between iterations (60s)... [API RPM is only 15 \\(0_0)/]")
        #     await asyncio.sleep(1)

    #Output to files for execution - Blame: Asa
    for i in range(NUM_OF_ITERATIONS):
        with open("candidate"+str(i)+".py", "w") as f:
            f.write(arr[i])
    
    print("\n\n---------------------\nCandidates created in working directory.\n\n")
    return arr


if __name__ == "__main__":
    asyncio.run(main())
    

