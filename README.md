# Chatbot

A simple chatbot was developed based on OpenAI's GPT3 model. APIs were called by AWS Lambda, supporting both `requests` and `boto3` library calls. Web app was writen in Streamlit and hosted on custom EC2 instance. CI/CD was done using GitHub Actions. Repo details at [GitHub link](https://github.com/nesaboz/chatbot/).

Try it yourself at <a href="https://nesaboz-chatbot-mygpt-cfgwpf.streamlit.app" target="_blank">MyGPT</a>.

# Demo 

![demo](demo_2x.mov)

# Notable technical points

1. OpenAI interface is via client and API key (pip library is [`openai`](https://pypi.org/project/openai/))

2. Chat is a list of messages, each message is a dictionary with `role` (user or bot) and `content` (text). For example this is how we assign a system role, i.e. a type of assistant you want to have:

```python
chat = [{"role": "system", "content": 'You are software engineer'}]
```

3. To get a reply from the assistant, we use `client.chat.completions.create` method. The model is `gpt-3`:

```python
def question(chat_history, some_question, client=client):
        """We take a chat_history, append a question as a user, then get a reply from the assistant, and append that too

        Args:
            chat_history (list): A list of dictionaries, with each dictionary containing a role and content key
            some_question (string): 
        """
        chat_history.append({"role": "user", "content": some_question})
        reply = client.chat.completions.create(
                model="gpt-3",
                messages=chat
                )
        reply_message = reply.choices[0].message
        chat_history.append({'role': reply_message.role, 'content':reply_message.content})
        display(Markdown(reply_message.content))
```

4. I am using AWS Lambda to make API calls, for that I:
    - create a layer with the dependencies (I had to use 1.10.12 version of `pydantic` as new one is having issues). Also note that Lambda has issues with some native libraries per [this](https://docs.aws.amazon.com/lambda/latest/dg/python-package.html#python-package-native-libraries), so make sure to install packages using this command:
    ```bash
    pip install --platform manylinux2014_x86_64 --target=package --implementation cp --python-version 3.x --only-binary=:all: --upgrade <package_name> -t ./theEnvFolder/python
    ```
    - create an IAM role
    - finally create Lambda function (I am handling both options of using `requests` and `boto3` since they have different event)

```python
import json
from openai import OpenAI
import os

def lambda_handler(event, context):
    """
    event is a same as chat i.e. list of dictionaries with role and content (in a case when called via URL it is slightly different since it is embedded in the extra layer so we extract body first)
    """
    
    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)
        
    if 'body' in event:  # this is needed when calling Lambda via URL, since URL call and boto3 have different events
        event = json.loads(json.loads(event.get('body')))
        
    chat_history = event
        
    reply = client.chat.completions.create(
        model="gpt-4",
        messages=chat_history,
        max_tokens=500
        )
    
    reply_message = reply.choices[0].message
    chat_history.append({'role': reply_message.role, 'content':reply_message.content})

    return {
        'statusCode': 200,
        'body': event
    }
```

# Conclusion

We have shown two approaches to call OpenAI API hosted on AWS Lambda using `requests` and `boto3` python libraries. I've hosted the app on both `streamlit.app` web platform and my own EC2 instance, however, it is not worth using the resources just for the demo. If this is to scale the proper way I would use AWS Beanstalk that takes care of load balancers and autoscaling web servers.

For details see [myGPT.ipynb](https://github.com/nesaboz/chatbot/blob/main/myGPT.ipynb) notebook.