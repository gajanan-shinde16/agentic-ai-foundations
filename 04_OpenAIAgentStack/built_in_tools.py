from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI

client = OpenAI()
# basic web search

# response1 = client.responses.create(
#     model='gpt-4o',
#     tools=[{"type": "web_search"}],
#     input="What happend in world in tech in last 24 hrs tell me in 10 bullet points"
# )

# print(response1.output_text)


# MODEL decides when to search web (if it can answer from its knowledge it won't search web)

res2 = response1 = client.responses.create(
    model='gpt-4o',
    tools=[{"type": "web_search"}],
    input="What is Maharashtra's second capital?"
)

print(res2.output_text)