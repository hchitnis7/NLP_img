import os
import base64
import streamlit as st
from mistralai import Mistral

# Function to encode image to base64
def encode_image(image_file):
    """Encode the image to base64."""
    try:
        return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        st.error(f"Error encoding image: {e}")
        return None

# API Key and client setup
api_key = 'uH96MMtPOqN0kJNYSGKUqH173NF8EBV9'
client = Mistral(api_key=api_key)

# Function to call the API with multiple prompt options
def get_api_responses(image_base64, detailed=False):
    """Make an API call with the encoded image."""
    try:
        if detailed:
            prompt = "Provide a detailed description of this image."
        else:
            prompt = (
                "Provide 4 short, one-line captions for this image. "
                "Each caption should be distinct, creative, and accurate."
            )

        chat_response = client.agents.complete(
            agent_id="ag:4849df2f:20241103:sfrpixtral:0f95a7d8",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": f"data:image/jpeg;base64,{image_base64}"}
                ]
            }]
        )
        return chat_response.choices[0].message.content
    except Exception as e:
        st.error(f"Error during API call: {e}")
        return None

# Streamlit UI components
st.title("Enhanced Image Captioning")
st.markdown("Upload an image, and explore multiple captions, detailed descriptions, or chat with the model about the image.")

# Upload image file
uploaded_image = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

# Tabs for different functionalities
tab1, tab2, tab3 = st.tabs(["Short Captions", "Detailed Description", "Chat with Model"])



if uploaded_image:
    base64_image = encode_image(uploaded_image)

    # Tab 1: Short captions
    with tab1:
        st.image(uploaded_image, caption="Uploaded Image", use_column_width=True)
        if st.button("Generate Short Captions"):
            if base64_image:
                st.write("Generating short captions...")
                captions_response = get_api_responses(base64_image)
                if captions_response:
                    captions = captions_response.split("\n")  # Assuming the API returns captions as a newline-separated list
                    st.subheader("Caption Options:")
                    for i, caption in enumerate(captions, start=1):
                        st.write(f"{caption}")
                else:
                    st.error("Failed to generate captions.")

    # Tab 2: Detailed description
    with tab2:
        st.image(uploaded_image, caption="Uploaded Image", use_column_width=True)
        if st.button("Generate Detailed Description"):
            if base64_image:
                st.write("Generating a detailed description...")
                description_response = get_api_responses(base64_image, detailed=True)
                if description_response:
                    st.subheader("Detailed Description:")
                    st.write(description_response)
                else:
                    st.error("Failed to generate a description.")

    # Tab 3: Chat with model
    with tab3:
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        
        st.image(uploaded_image, caption="Uploaded Image", use_column_width=True)
        user_input = st.text_input("Ask a question about the image:")
        if st.button("Send"):
            if base64_image and user_input:
                st.session_state.chat_history.append({"role": "user", "content": user_input})
                try:
                    chat_response = client.agents.complete(
                        agent_id="ag:4849df2f:20241103:sfrpixtral:0f95a7d8",
                        messages=[
                            {"role": "user", "content": [
                                {"type": "text", "text": user_input},
                                {"type": "image_url", "image_url": f"data:image/jpeg;base64,{base64_image}"}
                            ]}
                        ]
                    )
                    model_reply = chat_response.choices[0].message.content
                    st.session_state.chat_history.append({"role": "assistant", "content": model_reply})
                except Exception as e:
                    st.error(f"Error during chat: {e}")
            
        # Display chat history
        for chat in st.session_state.chat_history:
            role = "You" if chat["role"] == "user" else "Model"
            st.write(f"**{role}:** {chat['content']}")
        # Reset chat
        if st.button("Reset Chat"):
            st.session_state.chat_history = []    

else:
    st.info("Please upload an image to begin.")
