from strands import Agent

# Create an agent with a specific model by passing the model ID string
agent = Agent(model="us.anthropic.claude-sonnet-4-6")

response = agent("Tell me about Amazon Bedrock.")