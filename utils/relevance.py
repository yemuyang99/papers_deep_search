import re
from openai import OpenAI

class RelevanceChecker:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    def check_relevance(self, title, abstract, topic_description):
        prompt = "You are a research assistant. You are given a paper title and maybe its abstract. You need to check if the paper is relevant to the topic description. If it is relevant, answer 'YES', otherwise return 'NO'."
        prompt += "\nThe topic description will tell you some examples of relevance and irrelevance. Please check the criteria carefully. If any of the criteria is not met, please answer 'NO'. "
        prompt += "\nPlease put your answer in the format of <answer>YES</answer> or <answer>NO</answer>."
        prompt += f"\n\nTitle: {title}."
        if abstract != "":
            prompt += f"\n\nAbstract: {abstract}."
        prompt += f"\n\nTopic Description: {topic_description}."

        response = self.client.chat.completions.create(
            model="deepseek-reasoner",
            messages=[
                {"role": "user", "content": prompt},
            ],
            stream=False
        )
        outputs = response.choices[0].message.content

        idx = outputs.find("</think>")
        if idx != -1:
            outputs = outputs[idx:]
        match = re.search(r"<answer>\s*(YES|NO)\s*</answer>", outputs, re.IGNORECASE)
        if match:
            return match.group(1).upper() == "YES"
        else:
            print("Error: Unexpected output format.")
            return True


