import openai
import streamlit as st
import json

class APIPricing:
    def __init__(self, model_name):
        self.model_name = model_name
        with open("api_pricing.json", "r") as f:
            data = json.load(f)
        self.prompt_price = float(data[model_name]["prompt_price"])
        self.completion_price = float(data[model_name]["completion_price"])

    def calc_cost(self, text):
        self.text = text
        user_text, assistant_text = self.split_text()
        user_token_count = self.get_token_count(user_text)
        assistant_token_count = self.get_token_count(assistant_text)
        user_cost = user_token_count * self.prompt_price / 1000
        assistant_cost = assistant_token_count * self.completion_price / 1000
        total_cost = user_cost + assistant_cost
        return total_cost

    def split_text(self):
        lines = self.text.split("\n")
        user_text = [""]
        assistant_text = ["## ASSISTANT", "You will be provided with a text in English, and your task is to translate it into French."]
        is_user = True

        for line in lines:
            if line == "## USER":
                is_user = True
                continue
            elif line == "## ASSISTANT":
                is_user = False
                continue
            elif line == "":
                continue

            if is_user:
                user_text.append(line)
            else:
                assistant_text.append(line)

        return " ".join(user_text), " ".join(assistant_text)

    def get_token_count(self, text):
        encoding = tiktoken.encoding_for_model(self.model_name)
        tokens = encoding.encode(text)
        return len(tokens)

def main():
    # Commented Ferrari-themed sidebar
    """
    st.sidebar.markdown(
        '''
        <style>
            [data-testid="stSidebar"] {{
                background-image: url('https://upload.wikimedia.org/wikipedia/commons/4/44/Ferrari-Logo.svg');
                background-repeat: no-repeat;
                padding-top: 80px;
                background-position: center;
                background-size: 60%;
            }}
        </style>
        ''', unsafe_allow_html=True)
    st.sidebar.title("Enzo")
    """

    # Title with Formula 1 race car icon
    st.title("🏎️ Enzo")

    # Commented markdown instructions
    st.markdown("""
    ### Instructions:
    - **Language Selection**: Choose the language you want to translate your text into.
    - **Tone Selection**: Set the tone for translation such as 'Documentation', 'Product Page', 'Email Marketing', etc.
    """)

    # Model selection
    with open("api_pricing.json", "r") as f:
        data = json.load(f)
    model_names = data.keys()
    selected_model_name = st.selectbox("Select a GPT model", model_names)

    # Language selection with Czech and Dutch added
    language_prompts = {
        "German": "Please translate the following text from English to German, ensuring accuracy and cultural relevance.",
        "French": "Translate this English passage into French, considering regional linguistic variations where applicable.",
        "Spanish Mexico": "Convert the below English text into Mexican Spanish, paying close attention to local expressions and idiomatic usage.",
        "Spanish Neutral": "Translate the following English text into a neutral Spanish that is universally understood, while being mindful of idiomatic expressions.",
        "Spanish Spain": "Please adapt the English content into Castilian Spanish, incorporating cultural and regional nuances specific to Spain.",
        "Portuguese": "Translate the following English text into Portuguese, ensuring that regional differences are respected.",
        "Italian": "Please render the following English passage into Italian, taking care to reflect the linguistic richness and regional variations of Italy.",
        "Japanese": "Convert the English text below into Japanese, being mindful of the cultural context and nuances.",
        "English Australia": "Translate the following English text into Australian English, incorporating local slang and expressions where appropriate.",
        "English US": "Adapt the following English content into American English, considering regional variations and idiomatic usage."
    }
    selected_language_to = st.selectbox("Select a Language", language_prompts.keys())

    # Tone selection for translations
    tone_options = ["Documentation/Instructions", "Product Page", "Email Marketing", "General Translation"]
    selected_tone = st.selectbox("Select Translation Tone", tone_options)

    # Modify the prompt based on the selected tone
    tone_prompts = {
        "Documentation/Instructions": "Translate the text with a formal and instructional tone.",
        "Product Page": "Translate the text with a persuasive and customer-centric tone.",
        "Email Marketing": "Translate the text with an engaging and informal tone.",
        "General Translation": "Translate the text with a neutral tone."
    }
    selected_tone_prompt = tone_prompts[selected_tone]

    # Translation rules
    st.markdown("#### Translation Rules")
    st.markdown("Define specific rules to override translation logic, such as terms to avoid or prefer.")
    translation_rules = st.text_area("Translation Rules (Optional)", help="Specify rules to override the translation output.")

    # Prepare initial messages
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    # Construct the final prompt including tone and rules
    final_prompt = f"{language_prompts[selected_language_to]} {selected_tone_prompt}"
    if translation_rules:
        final_prompt += f"\n\nPlease follow these translation rules: {translation_rules}."

    if st.session_state["messages"]:
        st.session_state["messages"][0]["content"] = final_prompt
    else:
        st.session_state["messages"].append({"role": "assistant", "content": final_prompt})

    # Handle user input and generate translation
    if prompt := st.chat_input("Enter text to translate or provide instructions"):
        openai_api_key = st.secrets["OPENAI_TOKEN"]
        if not openai_api_key:
            st.info("Please add your OpenAI API key to continue.")
            st.stop()

        try:
            openai.api_key = openai_api_key
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.chat_message("user").write(prompt)

            # Make the OpenAI API call with hyperparameters for optimal translation
            response = openai.chat.completions.create(
                model=selected_model_name,
                messages=st.session_state.messages,
                max_tokens=2000,  # Set high token limit for larger translations
                temperature=0.7,  # Adjust temperature for creativity balance
                top_p=1,  # Use top-p sampling
                frequency_penalty=0.0,  # Reduce repeating words
                presence_penalty=0.0  # Encourage new topics
            )

            # Access the response content
            msg = response.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": msg})
            st.chat_message("assistant").write(msg)

        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()