import openai
import streamlit as st
import json
import tiktoken
from forex_python.converter import CurrencyRates


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

    # split text into USER and ASSISTANT parts
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
    st.markdown("# GTP Calculator")

    # st.markdown("""
    # For text input, use the following format to separate user and assistant dialogues:

    # * Type "## USER" before the user's dialogue.
    # * Type "## ASSISTANT" before the assistant's dialogue.

    # For example:
    # ```
    # ## USER
    # Text Translated

    # ## ASSISTANT
    # "## USER", "You will be provided with a sentence in English, and your task is to translate it into French."
    # ```
    # """)

    input_type = st.radio("Input Type", ["Text", "File"])

    if input_type == "Text":
        input_text = st.text_area("Input Text")
    else:
        input_file = st.file_uploader("Input File (It must be a .txt file)")

    # model selection
    with open("api_pricing.json", "r") as f:
        data = json.load(f)
    model_names = data.keys()
    selected_model_name = st.selectbox("Select a GPT model", model_names)

    times = st.slider("How many times the tool is used per day?", 1, 100, 10)

    # calculate token count and cost
    if st.button("Calculate"):
        try:
            if input_type == "Text":
                text = input_text
            else:
                text = input_file.read().decode("utf-8")

            api_pricing = APIPricing(selected_model_name)
            cost = api_pricing.calc_cost(text)
            monthly_cost = cost * times * 30
            c = CurrencyRates()
            cost_gbp = c.convert("USD", "GBP", cost)
            monthly_cost_gbp = c.convert("USD", "GBP", monthly_cost)

            st.markdown(f"""
            | Cost | Monthly Cost |
            | --- | --- |
            | {cost} USD | {monthly_cost} USD |
            | {cost_gbp} GBP | {monthly_cost_gbp} GBP |
            """)
        except Exception as e:
            st.error(f"An error occurred: {e}") 

    language_prompts = {
        "German": "Translate the following English text to German.",
        "French": "Translate the following English text to French.",
        "Spanish": "Translate the following English text to Spanish.",
    }  

    with st.sidebar:
        openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")

    st.title("AI Translator Beta")
    # with open("languages_available.json", "r") as f:
    #     lang = json.load(f)
    # languages_available = lang.keys()
    selected_language_to = st.selectbox("Select a Language", language_prompts.keys())

    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    if st.session_state["messages"]:
        # Update the assistant prompt based on the selected language
        st.session_state["messages"][0]["content"] = language_prompts[selected_language_to]
    else:
        initial_prompt = language_prompts[selected_language_to]
        st.session_state["messages"].append({"role": "assistant", "content": initial_prompt})

    if "messages" not in st.session_state:
        initial_prompt = language_prompts[selected_language_to]
        st.session_state["messages"] = [
                {"role": "assistant", "content":initial_prompt},
            ]

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input():
        if not openai_api_key:
            st.info("Please add your OpenAI API key to continue.")
            st.stop()

        try:
            openai.api_key = openai_api_key
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.chat_message("user").write(prompt)
            response = openai.chat.completions.create(model=selected_model_name, messages=st.session_state.messages)
            msg = response.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": msg})
            st.chat_message("assistant").write(msg)
        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
