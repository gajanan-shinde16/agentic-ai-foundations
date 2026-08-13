from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
client = OpenAI()


# response1 = client.responses.create(
#     model='gpt-4o',
#     input="Explain GenAI roadmap in single paragraph"
# )
# print(response1.output_text)

# response2 = client.responses.create(
#     model='gpt-4o',
#     input="in one line tell me estimate time for beginner to learn GenAI with roadmap given in previous response",
#     previous_response_id=response1.id
# )

response1 = client.responses.create(
    model='gpt-4o',
    input="Hi! My name is Gajanan, and i am a Software Developer"
)
print(response1.output_text)

response2 = client.responses.create(
    model='gpt-4o',
    input="What is my name, and what do I do?",
    previous_response_id=response1.id
)

print(response2.output_text)


'''
(.venv) PS C:\Users\gajan\Desktop\Agentic AI Foundations\04_OpenAIAgentStack> python conversation_chaining_with_response_api.py       
A Generative AI (GenAI) roadmap outlines the strategic implementation and evolution of AI systems that create content such as text, images, and audio. It typically begins with foundational research and the selection of robust models, followed by the development of training datasets tailored to specific applications. The roadmap includes phases for fine-tuning models, ensuring ethical guidelines and biases are addressed, and incorporating user feedback for iterative improvement. Deployment stages emphasize scalability and integration with existing technologies, while long-term goals focus on innovation, expanding capabilities, and exploring new use cases to maximize impact and efficiency in various industries.
It typically takes 6-12 months for a beginner to learn Generative AI following a comprehensive roadmap.
(.venv) PS C:\Users\gajan\Desktop\Agentic AI Foundations\04_OpenAIAgentStack> python conversation_chaining_with_response_api.py
Hi Gajanan! It's great to meet you. As a software developer, what projects or technologies are you currently working on?
Your name is Gajanan, and you are a Software Developer.
(.venv) PS C:\Users\gajan\Desktop\Agentic AI Foundations\04_OpenAIAgentStack> 
'''