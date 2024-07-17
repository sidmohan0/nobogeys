from app.config import get_settings, AgentTypeAnalysis
from app.models.base import AgentType
from app.models.user_input import UserInput
from openai import OpenAI
import instructor

settings = get_settings()

def initialize_openai():
    return instructor.patch(OpenAI(api_key=settings.OPENAI_API_KEY))

def analyze_agent_types(user_input: UserInput) -> AgentTypeAnalysis:
    config = settings.agent_type_analysis
    
    # Convert UserInput to string representation
    input_text = f"Input Type: {user_input.input_type}\nContent: {user_input.content}"
    if user_input.file_path:
        input_text += f"\nFile Path: {user_input.file_path}"
    
    prompt = config.prompt_template.format(text=input_text)
    
    client = initialize_openai()
    response = client.chat.completions.create(
        model=config.openai_model,
        messages=[
            {"role": "system", "content": config.system_message},
            {"role": "user", "content": prompt}
        ],
        temperature=config.temperature,
        max_tokens=config.max_tokens,
        response_model=AgentTypeAnalysis
    )
    
    return response

# Example usage
if __name__ == "__main__":
    sample_input = UserInput(input_type="text", content="I need advice on improving my golf swing and choosing the right club for a par 4 hole.")
    result = analyze_agent_types(sample_input)
    for agent_type in AgentType:
        agent_result = getattr(result, agent_type.value.lower())
        print(f"{agent_type.value}:")
        print(f"  Confidence: {agent_result.confidence:.2f}")
        print(f"  Explanation: {agent_result.explanation}")
        print()