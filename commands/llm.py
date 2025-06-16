import discord
import ollama
import asyncio

async def run_command(message: discord.Message, history: list[discord.Message]):
    """
    Handles the $llm command to interact with the Ollama language model.
    """
    user_prompt = message.content
    if not user_prompt:
        await message.channel.send("Please provide a prompt for the LLM. Example: `$llm Tell me a short story.`")
        return

    # Construct the history string
    history_str = ""
    if history:
        for msg in history:
            history_str += f"message from {msg.author.display_name}: {msg.content}\n"

    # Combine current prompt and history into the desired format
    combined_prompt = f"""
		<user_request>
		{user_prompt}
		</user_request>
		<message_history>
		{history_str}
		</message_history>
	"""

    # Construct the messages for Ollama API call
    # The system message guides Gemma's behavior
    messages = [
        {'role': 'system', 'content': 'You are a helpful and concise assistant. Directly answer the user\'s request presented in the <user_request> tag. Keep your response brief.'},
        {'role': 'user', 'content': combined_prompt},
    ]

    try:
        # Call Ollama API in a separate thread to avoid blocking the Discord bot's event loop
        response = await asyncio.to_thread(
            ollama.chat,
            model='gemma:2b',
            messages=messages
        )
        llm_response = response['message']['content']

        # Truncate if response is still too long for Discord (Discord has a 2000 character limit)
        if len(llm_response) > 1990: # Leave some room for "..."
            llm_response = llm_response[:1990] + "..."

        await message.channel.send(llm_response)
    except ollama.ResponseError as e:
        await message.channel.send(f"Error communicating with the LLM: {e}")
    except Exception as e:
        await message.channel.send(f"An unexpected error occurred while processing your request: {e}")
