# GPT Translator Tool & Tokens Calculator

## Run te Application

`streamlit run app.py`

## Models

Here's a reference pricing for the available GPT models:

| Model | Prompt Price (USD / 1K tokens) | Completion Price (USD / 1K tokens) |
| :--- | :---: | :---: |
| gpt-3.5-turbo | 0.002 | 0.002 |
| gpt-4-8k | 0.03 | 0.06 |
| gpt-4-32k | 0.06 | 0.12 |

The application will output a table that shows the cost and monthly cost of using the selected GPT model based on the input text and usage frequency.

The cost will be shown in USD and GBP. The currency conversion rate is based on the current exchange rate from USD to GBP using the `forex-python` package.

## Tokens
The project uses [tiktoken](https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb), fast open-source tokenizer by Open AI.