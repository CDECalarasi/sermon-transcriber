from mixins.openai import OpenAIMixin
import logging

_sum = """The Sermon MAIN POINT (only one), Sermon applications (what could be applied from the sermon into one's day 
to day life), main ideas (no less than 3, no more than 5), a summary (intro, main content and conclusion; sparing no 
details, but as you would explain the sermon to a friend) of the sermon (AVOID using words like 'The sermon begins', 
'The preacher' or similar)""".replace("\n", " ")

system_content = f"""You are a proficient AI with a specialty in understanding information. Based on the following 
text, identify and list the following PREACHED or brought up: {_sum}. These should be the most important ideas, 
findings, or topics that are crucial to the essence of the PREACH. Your goal is to provide {_sum} that someone could 
read to quickly understand what was talked about. This text is Romanian and you need to extract the key points from 
it and list them in Romanian. THIS IS A SERMON or a PREACH. The text should be in markdown format.""".replace("\n", " ")


class Summarizer(OpenAIMixin):  # Mixin included
    def __init__(self):
        # Initialize mixin
        self.initialize_openai()
        self.logger = logging.getLogger(__name__)

    def summarize(self, content):
        try:
            self.logger.info(f"Trying to summarize: {content}")

            completion = self.client.chat.completions.create(
                # model="gpt-4",
                model="gpt-4-turbo-preview",
                temperature=0,
                messages=[
                    {
                        "role": "system",
                        "content": system_content
                    },
                    {
                        "role": "user",
                        "content": content
                    }
                ]
            )

            return completion.choices[0].message.content
        except Exception as e:
            return str(e)
