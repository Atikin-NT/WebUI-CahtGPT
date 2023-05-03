import openai
import tiktoken
import config
import db_functions

openai.api_key = config.DevelopmentConfig.OPENAI_KEY
MAX_TOKENS_RESP = 150
MAX_TOKENS_REQ = 300



def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301"):
  """Returns the number of tokens used by a list of messages."""
  try:
      encoding = tiktoken.encoding_for_model(model)
  except KeyError:
      encoding = tiktoken.get_encoding("cl100k_base")
  if model == "gpt-3.5-turbo-0301":  # note: future models may deviate from this
      num_tokens = 0
      for message in messages:
          num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
          for key, value in message.items():
              num_tokens += len(encoding.encode(value))
              if key == "name":  # if there's a name, the role is omitted
                  num_tokens += -1  # role is always required and always 1 token
      num_tokens += 2  # every reply is primed with <im_start>assistant
      return num_tokens
  else:
      raise NotImplementedError(f"""num_tokens_from_messages() is not presently implemented for model {model}.
  See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")


def generateChatResponse(prompt, ctx_messages, tokens_left):
    model = "gpt-3.5-turbo"

    messages = [{"role": "user", "content": "You are a helpful assistant."}]

    ctx_messages = [{ 'role': msg[0], 'content': msg[1] } for msg in ctx_messages]
    messages.extend(ctx_messages)

    question = { 'role': 'user', 'content': prompt }
    messages.append(question)

    msg_len = num_tokens_from_messages(messages)

    print(messages)
    print('question_len', msg_len)
    print('tokens_left', tokens_left)
    


    if msg_len > MAX_TOKENS_REQ or msg_len > tokens_left:
        return (question, "", 0, "Promt too long")

    # response = openai.ChatCompletion.create(
    #     model=model,
    #     messages=msgs,
    #     max_tokens=MAX_TOKENS_RESP
    # )

    response = {
        "id": "chatcmpl-123",
        "object": "chat.completion",
        "created": 1677652288,
        "choices": [
        {
            "index": 0,
            "message": {
            "role": "assistant",
            "content": "\n\nHello there, how may I assist you today?",
            },
            "finish_reason": "stop"
        }],
        "usage": {
            "prompt_tokens": 9,
            "completion_tokens": 12,
            "total_tokens": 21
        }
    }

    usage = response['usage']
    total_tokens_usage = usage['total_tokens']
    if len(response['choices']) == 0:
        return (question, "", total_tokens_usage, "Oops you beat the AI, try different questions, if the problem persists, come back later.")
    
    answer_msg = response['choices'][0]['message']

    total_tokens_usage = msg_len + usage["completion_tokens"]

    print('actual question_len', usage['prompt_tokens'])
    print('usage', total_tokens_usage)

    print(question)
    print(answer_msg)

    return (question, answer_msg, total_tokens_usage, "ok")


