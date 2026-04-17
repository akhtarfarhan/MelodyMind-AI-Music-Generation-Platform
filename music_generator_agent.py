import os
from uuid import uuid4
import requests
import streamlit as st

from agno.agent import Agent
from agno.run.agent import RunOutput
from agno.models.openai import OpenAIChat
from agno.tools.models_labs import FileType, ModelsLabTools
from agno.utils.log import logger

# Sidebar: User enters the API keys
st.sidebar.title("API Key Configuration")

openai_api_key = st.sidebar.text_input("Enter your OpenAI API Key", type="password")
models_lab_api_key = st.sidebar.text_input("Enter your ModelsLab API Key", type="password")

# Streamlit App UI
st.title("🎶 MelodyMind-AI-Music-Generation-Platform")

prompt = st.text_area(
    "Enter a music generation prompt:",
    "Generate a 30 second classical music piece",
    height=100
)

# Initialize agent only if both API keys are provided
if openai_api_key and models_lab_api_key:

    agent = Agent(
        name="ModelsLab Music Agent",
        model=OpenAIChat(
            id="gpt-4o",
            api_key=openai_api_key
        ),
        tools=[
            ModelsLabTools(
                api_key=models_lab_api_key,
                wait_for_completion=True,
                file_type=FileType.MP3
            )
        ],
        description="You are an AI agent that can generate music using the ModelsLabs API.",
        instructions=[
            "When generating music, use the `generate_media` tool with detailed prompts that specify:",
            "- Genre and style (classical, jazz, etc.)",
            "- Instruments",
            "- Tempo and mood",
            "- Structure (intro, chorus, etc.)",
        ],
        markdown=True,
        debug_mode=True,
    )

    if st.button("Generate Music"):
        if not prompt.strip():
            st.warning("Please enter a prompt first.")
        else:
            with st.spinner("Generating music... 🎵"):
                try:
                    tool = ModelsLabTools(
                        api_key=models_lab_api_key,
                        wait_for_completion=True,
                        file_type=FileType.MP3
                    )

                    result = tool.generate_media(prompt=prompt)

                    st.write(result)  # DEBUG

                    if result and hasattr(result, "url"):
                        url = result.url
                    elif result and isinstance(result, dict):
                        url = result.get("url")
                    else:
                        st.error("No URL returned from ModelsLab")
                        st.stop()

                    audio = requests.get(url)

                    if not audio.ok:
                        st.error("Failed to download audio")
                        st.stop()

                    st.audio(audio.content, format="audio/mp3")

                except Exception as e:
                    st.error(f"Error: {e}")
else:
    st.sidebar.warning("Please enter both API keys.")