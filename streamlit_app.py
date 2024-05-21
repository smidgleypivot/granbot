from openai import OpenAI
import time
import streamlit as st
import asyncio
from openai.types.beta.assistant_stream_event import ThreadMessageDelta
from openai.types.beta.threads.text_delta_block import TextDeltaBlock 

def main():
    st.set_page_config(
        page_title="Dougbot",
        page_icon="📚",
    )

    api_key = st.secrets["OPENAI_API_KEY"]
    assistant_id = st.secrets["ASSISTANT_ID"]
    letters_id = st.secrets['LETTERSID'] 
    # Initiate st.session_state
    st.session_state.client = OpenAI(api_key=api_key)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "start_chat" not in st.session_state:
        st.session_state.start_chat = False

    if st.session_state.client:
       st.session_state.start_chat = True

    if st.session_state.start_chat:
        # Display existing messages in the chat
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

                # Accept user input
        if prompt := st.chat_input(f"I fondly await news from you, Doug."):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            # Display user message in chat message container
            with st.chat_message("user"):
                st.markdown(prompt)

            if "thread_id" not in st.session_state:
                thread = st.session_state.client.beta.threads.create()
                st.session_state.thread_id = thread.id
            
            # Add a Message to the thread
            st.session_state.client.beta.threads.messages.create(
                thread_id=st.session_state.thread_id,
                role="user",
                content=prompt,
                attachments=[
                    {
                    "file_id":letters_id, 
                        "tools":[{"type":"file_search"}]
                    }
                ],
                
                
            )

            # As of now, assistant and thread are not associated to eash other
            # You need to create a run in order to tell the assistant at which thread to look at
            run = st.session_state.client.beta.threads.runs.create(
                thread_id=st.session_state.thread_id,
                assistant_id=assistant_id,
                stream=True,
                additional_instructions="You are Doug, use the referenced letters to respond in they style of the letters. Please keep responses to upto 2 paragraphs."
            )

            assistant_reply_box = st.empty()
            assistant_reply = ""

            for event in run:
            # There are various types of streaming events
            # See here: https://platform.openai.com/docs/api-reference/assistants-streaming/events

            # Here, we only consider if there's a delta text
                if isinstance(event, ThreadMessageDelta):
                    if isinstance(event.data.delta.content[0], TextDeltaBlock):
                        # empty the container
                        assistant_reply_box.empty()
                        # add the new text
                        assistant_reply += event.data.delta.content[0].text.value
                        # display the new text
                        assistant_reply_box.markdown(assistant_reply)
        
            # Once the stream is over, update chat history
            st.session_state.messages.append({"role": "assistant",
                                                "content": assistant_reply})
            

if __name__ == "__main__":
    main()