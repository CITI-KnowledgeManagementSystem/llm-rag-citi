

def format_conversation_history(history:list):
    new_hist = []

    for message in history:
        if message["type"] == "request":
            new_hist.append(
                {
                    "role": "user",
                    "content": message["message"]
                }
            )
        else:
            new_hist.append(
                {
                    "role": "assistant",
                    "content": message["message"]
                }
            )
    return new_hist