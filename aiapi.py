import openai
import tiktoken
import config
import db_functions
import markdown as md

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


def markdown(value):
    return md.markdown(value, extensions=[
        'markdown.extensions.footnotes',
        'markdown.extensions.footnotes',
        'markdown.extensions.attr_list',
        'markdown.extensions.def_list',
        'markdown.extensions.tables',
        'markdown.extensions.abbr',
        'markdown.extensions.md_in_html',
        'pymdownx.highlight',
        'pymdownx.superfences',
        'pymdownx.mark',
        'pymdownx.arithmatex',
    ],
                       extension_configs={
        "pymdownx.arithmatex": {
            'generic': True,
        },
       "pymdownx.tasklist": {
           "custom_checkbox": True,
       },
       "pymdownx.highlight": {
           'use_pygments': True,
           'guess_lang': True,
           'noclasses': False,
           'pygments_style': 'friendly',
       },
    })


def close_blocks_check(msg: str) -> str:
    """
    Функция, которая проверяет на закрытие блоков в html. Например, бот мог отослать сообщение,
    но он его обрезал по середине блока кода. В этом случае плывет вся разметка

    msg: - сообщение
    return: -отформатированное сообщение
    """
    msg = msg.replace("\\n", "\n").replace('\\"', '\"')
    if msg.count("```") % 2 != 0:
        msg += "\n...\n```"

    return msg

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

    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        max_tokens=MAX_TOKENS_RESP
    )

    usage = response['usage']
    total_tokens_usage = usage['total_tokens']
    if len(response['choices']) == 0:
        return (question, "", total_tokens_usage, "Oops you beat the AI, try different questions, if the problem persists, come back later.")
    
    answer_msg = response['choices'][0]['message']

    total_tokens_usage = msg_len + usage["completion_tokens"]

    print('actual question_len', usage['prompt_tokens'])
    print('usage', total_tokens_usage)

    answer_msg["content"] = close_blocks_check(answer_msg["content"])
    answer_msg["content"] = markdown(answer_msg["content"])
    print(question)
    print(answer_msg)

    return (question, answer_msg, total_tokens_usage, "ok")


