import discord
import ollama
import asyncio

async def run_command(message: discord.Message):
    """
    Handles the $llm command to interact with the Ollama language model.
    """
    prompt = message.content[len('$llm'):].strip()
    if not prompt:
        await message.channel.send("Please provide a prompt for the LLM. Example: `$llm Tell me a short story.`")
        return

    # Construct the messages for Ollama API call
    # The system message guides Gemma's behavior
    messages = [
        {'role': 'system', 'content': 'You are ekimbot, a helpful discord bot written by legendary programmer Ekim Karabey. When a user asks you for help, try to fulfill their request to the best of your ability. Keep your responses short and concise for a general audience. Keep your response up to 5 sentences.'},
        {'role': 'user', 'content': prompt},
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
