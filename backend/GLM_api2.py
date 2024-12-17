import json

from openai import OpenAI
from colorama import init, Fore
from loguru import logger

from tool_register import get_tools, dispatch_tool

init(autoreset=True)
client = OpenAI(
  base_url="http://127.0.0.1:6006/v1",
  api_key = "xxx"
)

functions = get_tools()


def run_conversation(query: str, stream=False, functions=None,messages = [], max_retry=5):
    params = dict(model="chatglm3", messages=[*messages,{"role": "user", "content": query}], stream=stream)
    if functions:
        params["functions"] = functions
    response = client.chat.completions.create(**params)

    for _ in range(max_retry):
        if not stream:
            if response.choices[0].message.function_call:
                function_call = response.choices[0].message.function_call
                logger.info(f"Function Call Response: {function_call.model_dump()}")

                function_args = json.loads(function_call.arguments)
                tool_response = dispatch_tool(function_call.name, function_args)
                logger.info(f"Tool Call Response: {tool_response}")

                params["messages"].append(response.choices[0].message)
                params["messages"].append(
                    {
                        "role": "function",
                        "name": function_call.name,
                        "content": tool_response,  # 调用函数返回结果
                    }
                )
            else:
                reply = response.choices[0].message.content
                logger.info(f"Final Reply: \n{reply}")
                params["messages"].append(response.choices[0].message)
                return params["messages"]
        #流式对话
        else:
            output = ""
            for chunk in response:
                content = chunk.choices[0].delta.content or ""
                print(Fore.BLUE + content, end="", flush=True)
                output += content

                if chunk.choices[0].finish_reason == "stop":
                    params["messages"].append({'content': output,'role':'assistant'})
                    return params["messages"]

                elif chunk.choices[0].finish_reason == "function_call":
                    print("\n")

                    function_call = chunk.choices[0].delta.function_call
                    logger.info(f"Function Call Response: {function_call.model_dump()}")

                    function_args = json.loads(function_call.arguments)
                    tool_response = dispatch_tool(function_call.name, function_args)
                    logger.info(f"Tool Call Response: {tool_response}")

                    params["messages"].append(
                        {
                            "role": "assistant",
                            "content": output
                        }
                    )
                    params["messages"].append(
                        {
                            "role": "function",
                            "name": function_call.name,
                            "content": tool_response,
                        }
                    )
                    print(messages)
                    break
        response = client.chat.completions.create(**params)
        return response

if __name__ == "__main__":
    # while True:
        # user_input = input("请输入您的问题: ")
        # chat_messages.append({"role": "user", "content": user_input})
        # response = create_chat_completion("chatglm3-6b", chat_messages, use_stream=False)
        # print("回复:", response)
        chat_messages = [
        {
            "role": "system",
            "content": "从现在起请你扮演一位水利专家与我对话",
        }
        ]

        while 1:
            try:
                logger.info("\n=========== next conversation ===========")
                query = input("Enter a query: ")
                chat_messages.append({"role": "user", "content": query})
                messages = run_conversation(chat_messages, functions=functions, stream=True)
                print(messages)
            except:
                messages.pop()
                print('ChatGLM3：error\n')
    #加多轮对话
    #页数，以及一页的数量
    #找清楚每一个api必须要的参数