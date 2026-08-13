from openai import OpenAI

from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

response = client.responses.create(
    model='gpt-5.5',
    input="Explain different ways to use openai's response apis"
)


print(response.output_text)

# OUTPUT BELOW

'''
OpenAI’s **Responses API** is the newer general-purpose API for generating model outputs. It can handle normal chat, structured JSON, tool use, multimodal input, streaming, and longer-running tasks.

Endpoint:

```http
POST /v1/responses
```

Python SDK:

```bash
pip install openai
```

```python
from openai import OpenAI

client = OpenAI()
```

JavaScript SDK:

```bash
npm install openai
```

```js
import OpenAI from "openai";

const client = new OpenAI();
```

---

## 1. Simple text generation

Use the Responses API like a normal chat/completion endpoint.

### Python

```python
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-4.1-mini",
    input="Explain quantum computing in simple terms."
)

print(response.output_text)
```

### JavaScript

```js
import OpenAI from "openai";

const client = new OpenAI();

const response = await client.responses.create({
  model: "gpt-4.1-mini",
  input: "Explain quantum computing in simple terms."
});

console.log(response.output_text);
```

### cURL

```bash
curl https://api.openai.com/v1/responses \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4.1-mini",
    "input": "Explain quantum computing in simple terms."
  }'
```

---

## 2. Using system/developer instructions

You can separate high-level behavior from user input.

```python
response = client.responses.create(
    model="gpt-4.1-mini",
    instructions="You are a concise technical tutor.",
    input="Explain how DNS works."
)

print(response.output_text)
```

Use `instructions` for things like:

- Tone
- Role
- Formatting preferences
- Domain-specific constraints
- Safety or business rules

---

## 3. Multi-turn conversations

There are two common approaches.

### Option A: Use `previous_response_id`

This lets OpenAI connect the new response to a previous one.

```python
first = client.responses.create(
    model="gpt-4.1-mini",
    input="My name is Maya. Give me a workout plan."
)

second = client.responses.create(
    model="gpt-4.1-mini",
    previous_response_id=first.id,
    input="Make it suitable for beginners."
)

print(second.output_text)
```

### Option B: Send the whole conversation yourself

```python
response = client.responses.create(
    model="gpt-4.1-mini",
    input=[
        {
            "role": "user",
            "content": "My name is Maya. Give me a workout plan."
        },
        {
            "role": "assistant",
            "content": "Sure, here is a basic workout plan..."
        },
        {
            "role": "user",
            "content": "Make it suitable for beginners."
        }
    ]
)

print(response.output_text)
```

Use this if you want full control over conversation history.

---

## 4. Streaming responses

Streaming lets you show tokens as they are generated.

### Python

```python
with client.responses.stream(
    model="gpt-4.1-mini",
    input="Write a short story about a robot learning music."
) as stream:
    for event in stream:
        if event.type == "response.output_text.delta":
            print(event.delta, end="")

    final_response = stream.get_final_response()
```

### JavaScript

```js
const stream = await client.responses.stream({
  model: "gpt-4.1-mini",
  input: "Write a short story about a robot learning music."
});

for await (const event of stream) {
  if (event.type === "response.output_text.delta") {
    process.stdout.write(event.delta);
  }
}
```

Streaming is useful for:

- Chat UIs
- Long answers
- Better perceived latency
- Voice or live interfaces

---

## 5. Structured JSON outputs

You can force the model to return data matching a JSON schema.

```python
response = client.responses.create(
    model="gpt-4.1-mini",
    input="Extract the event details: Alice and Bob are meeting Friday at 3pm.",
    text={
        "format": {
            "type": "json_schema",
            "name": "calendar_event",
            "schema": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "participants": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "day": {"type": "string"},
                    "time": {"type": "string"}
                },
                "required": ["title", "participants", "day", "time"],
                "additionalProperties": False
            },
            "strict": True
        }
    }
)

print(response.output_text)
```

Example output:

```json
{
  "title": "Meeting",
  "participants": ["Alice", "Bob"],
  "day": "Friday",
  "time": "3pm"
}
```

Useful for:

- Data extraction
- API payload generation
- Classification
- Form filling
- Workflow automation

---

## 6. Function calling

You can let the model decide when to call your own functions.

Example: define a weather function.

```python
tools = [
    {
        "type": "function",
        "name": "get_weather",
        "description": "Get the current weather for a city.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string"}
            },
            "required": ["city"],
            "additionalProperties": False
        }
    }
]

response = client.responses.create(
    model="gpt-4.1-mini",
    input="What's the weather in Tokyo?",
    tools=tools
)
```

The response may contain a function call like:

```json
{
  "type": "function_call",
  "name": "get_weather",
  "arguments": "{\"city\":\"Tokyo\"}"
}
```

You then run the function in your own code and send the result back.

```python
import json

function_call = None

for item in response.output:
    if item.type == "function_call":
        function_call = item

args = json.loads(function_call.arguments)

# Your actual function
weather_result = {
    "city": args["city"],
    "temperature": "27°C",
    "condition": "Sunny"
}

final = client.responses.create(
    model="gpt-4.1-mini",
    previous_response_id=response.id,
    input=[
        {
            "type": "function_call_output",
            "call_id": function_call.call_id,
            "output": json.dumps(weather_result)
        }
    ]
)

print(final.output_text)
```

Function calling is useful for:

- Database lookups
- External APIs
- Booking systems
- User account operations
- Internal business logic

---

## 7. Web search tool

Some models can use OpenAI-hosted tools such as web search.

```python
response = client.responses.create(
    model="gpt-4.1-mini",
    input="What are the latest updates on OpenAI's APIs?",
    tools=[
        {
            "type": "web_search_preview"
        }
    ]
)

print(response.output_text)
```

Useful for questions that require current information.

Tool names may vary depending on the model and API version, so check the current OpenAI docs for the exact supported tool type.

---

## 8. File search / retrieval

You can connect the model to your own uploaded documents using file search/vector stores.

Conceptually:

```python
response = client.responses.create(
    model="gpt-4.1-mini",
    input="Summarize the refund policy from our company docs.",
    tools=[
        {
            "type": "file_search",
            "vector_store_ids": ["vs_abc123"]
        }
    ]
)

print(response.output_text)
```

Useful for:

- Internal knowledge bases
- Customer support
- Legal or policy search
- Technical documentation Q&A

---

## 9. Multimodal input: text + images

You can send images along with text.

```python
response = client.responses.create(
    model="gpt-4.1-mini",
    input=[
        {
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": "What is shown in this image?"
                },
                {
                    "type": "input_image",
                    "image_url": "https://example.com/image.jpg"
                }
            ]
        }
    ]
)

print(response.output_text)
```

Useful for:

- Image understanding
- Chart interpretation
- Screenshot analysis
- Visual QA
- UI debugging

---

## 10. Uploading and using files

You can upload files and refer to them in a response.

```python
file = client.files.create(
    file=open("report.pdf", "rb"),
    purpose="assistants"
)

response = client.responses.create(
    model="gpt-4.1-mini",
    input=[
        {
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": "Summarize this PDF."
                },
                {
                    "type": "input_file",
                    "file_id": file.id
                }
            ]
        }
    ]
)

print(response.output_text)
```

This is useful for one-off document analysis. For large document collections, use file search/vector stores instead.

---

## 11. Background or asynchronous processing

For longer jobs, you can create a response in the background and retrieve it later.

```python
response = client.responses.create(
    model="gpt-4.1-mini",
    input="Write a detailed 20-page market analysis.",
    background=True
)

print(response.id)
```

Later:

```python
result = client.responses.retrieve(response.id)

print(result.status)
print(result.output_text)
```

Useful for:

- Long reports
- Large document processing
- Agents with many tool calls
- Expensive workflows

---

## 12. Batch usage

If you need to run many responses offline, use the Batch API with `/v1/responses`.

This is useful for:

- Classifying thousands of records
- Summarizing many documents
- Extracting structured fields from large datasets
- Running cheaper asynchronous jobs at scale

A batch request usually references a `.jsonl` file containing many individual API calls.

---

## 13. Reasoning models

Some models support deeper reasoning. You can often control reasoning effort.

```python
response = client.responses.create(
    model="o4-mini",
    input="Solve this logic puzzle step by step.",
    reasoning={
        "effort": "medium"
    }
)

print(response.output_text)
```

Use reasoning models for:

- Math
- Coding
- Planning
- Complex analysis
- Multi-step decision making

---

## 14. Building agents

The Responses API can be used as the core loop for an agent:

1. User asks something.
2. Model decides whether it needs a tool.
3. Your app executes the tool.
4. Tool result is sent back.
5. Model continues until it gives a final answer.

Basic pattern:

```python
response = client.responses.create(
    model="gpt-4.1-mini",
    input="Find the status of order 123 and email the customer.",
    tools=[
        {
            "type": "function",
            "name": "get_order_status",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string"}
                },
                "required": ["order_id"]
            }
        },
        {
            "type": "function",
            "name": "send_email",
            "parameters": {
                "type": "object",
                "properties": {
                    "email": {"type": "string"},
                    "body": {"type": "string"}
                },
                "required": ["email", "body"]
            }
        }
    ]
)
```

Your code then handles any function calls returned by the model.

---

## 15. Migrating from Chat Completions

Old style:

```python
client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are helpful."},
        {"role": "user", "content": "Hello!"}
    ]
)
```

Responses API style:

```python
client.responses.create(
    model="gpt-4.1-mini",
    instructions="You are helpful.",
    input="Hello!"
)
```

Or with message objects:

```python
client.responses.create(
    model="gpt-4.1-mini",
    input=[
        {"role": "user", "content": "Hello!"}
    ]
)
```

---

# Summary

Common ways to use the Responses API:

| Use case | Feature |
|---|---|
| Basic chatbot | `input` + `output_text` |
| System behavior | `instructions` |
| Multi-turn chat | `previous_response_id` or message history |
| Live UI | Streaming |
| JSON output | `text.format` with JSON schema |
| External actions | Function calling |
| Current information | Web search tool |
| Your documents | File search or uploaded files |
| Images/screenshots | Multimodal input |
| Long tasks | `background=True` |
| Bulk jobs | Batch API |
| Complex problem solving | Reasoning models |

For most new applications, use the **Responses API** instead of the older Chat Completions API.
'''