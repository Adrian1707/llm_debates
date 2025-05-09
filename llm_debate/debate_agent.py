import os
import json
import requests
from llm_debate.ollama_client import OllamaClient
from llm_debate.openai_client import OpenAIClient

class DebateAgent:
    def __init__(self, for_or_against, topic):
        if for_or_against == 'for':
            self.side = 'in favor'
        else:
            self.side = 'not in favor'
        self.topic = topic
        self.for_or_against = for_or_against
        # self.llm_client = OllamaClient()
        self.llm_client = OpenAIClient()
    
    def build_debate_prompt(self, opponent_argument, opening):
        self_history = "\n".join(f"{i+1}. {arg}" for i, arg in enumerate(self.llm_client.previous_arguments[-2:]))
        if opening == True:
            opponent_said = f"""
                Compose your response now—begin directly with substance.
            """
        else:
            opponent_said = f"""
                Opponent just said:
                "{opponent_argument}"

                Compose your response now—begin directly with substance.
            """
        prompt = f"""
            You are engaged in a direct, one-on-one debate with your opponent on the following topic:
            "{self.topic}"
            You are "{self.side}" of this so you will argue "{self.for_or_against}" the topic in question.

            Instructions:
            - Respond conversationally and directly to your opponent's last argument below.
            - DO NOT start your reply with any formal salutation (e.g., "Ladies and gentlemen", "esteemed judges", etc.).
            - DO NOT make reference to "Your opponent", because remember it's you who is in this debate
            - Focus only on addressing your opponent's points and advancing your case.
            - Maintain a natural, professional tone as if speaking directly to another expert—not an audience.
            - Look through your previous arguments and make sure you do not repeat any of these arguments. Take the debate into another direction and expand on the topic in a multi-disciplinary way.
            - Build on both your own previous arguments and theirs for coherence.
            - Use examples, data, and logic as needed.
            - Write a detailed response (about 300–400 words).

            Your previous arguments:
            {self_history}

            {opponent_said}
        """
        return prompt

    def build_adversarial_prompt(self, opponent_argument, opening):
        self_history = "\n".join(f"{i+1}. {arg}" for i, arg in enumerate(self.llm_client.previous_arguments[-2:]))
        if opening == True:
            opponent_said = f"""
                Compose your response now—begin directly with substance.
            """
        else:
            opponent_said = f"""
                Opponent just said:
                "{opponent_argument}"

                Compose your response now—begin directly with substance.
            """
        prompt = f"""
            You are engaged in a direct, one-on-one debate with your opponent on the following topic:
            "{self.topic}"
            You are "{self.side}" of this so you will argue "{self.for_or_against}" the topic in question.

             Tone & Style:

            - Aggressive, unapologetic, and logically brutal—prioritize precision over pleasantries at all times.*
            - Employ sarcasm,* biting wit,* or clinical detachment depending on what best exposes weaknesses.*
            - Refuse compromise:*  You must tear the statement apart in the most intelligent way possible*
            - Always address the input statement directly, as if speaking one-on-one with the person who made it.
            - Avoid any third-person references such as "your opponent," "their argument," "some say," or similar.
            - Use direct language with "you" or neutral phrasing that engages the speaker immediately.
            - Frame critiques and attacks as if you are actively debating with that person in real time.

            Instructions:
            - Respond conversationally and directly to your opponent's last argument below.
            - DO NOT start your reply with any formal salutation (e.g., "Ladies and gentlemen", "esteemed judges", etc.).
            - DO NOT make reference to "Your opponent", because remember it's you who is in this debate
            - Focus only on addressing your opponent's points and advancing your case.
            - Look through your previous arguments and make sure you do not repeat any of these arguments. Take the debate into another direction and expand on the topic in a multi-disciplinary way.
            - Build on both your own previous arguments and theirs for coherence.
            - Use examples, data, and logic as needed.
            
            - Write a detailed response (about 300–400 words).

            Your previous arguments:
            {self_history}

            {opponent_said}
        """
        return prompt

    # def build_adversarial_prompt(self, opponent_argument, opening):
    #     self_history = "\n".join(f"{i+1}. {arg}" for i, arg in enumerate(self.llm_client.previous_arguments[-2:]))
    #     if opening == True:
    #         opponent_said = f"""
    #         Compose your response now—begin directly with substance.
    #         """
    #         stuff = ""
    #     else:
    #         opponent_said = f"""
    #             This is the argument you must dissect and respond to:
    #             "{opponent_argument}"

    #             Compose your response now—begin directly with substance and attack this argument above.
    #         """
    #         stuff = f"""
    #         IMPORTANT: Your role is to disagree and tear apart everything said here by the individual you are in a debate with, no exceptions: "{opponent_argument}"
    #         """

    #     prompt = f"""
    #         Role: You are a highly analytical, logically rigorous AI trained to simulate an internal debate.
    #         You are currently in a debate with an opponent about an issue.
    #         You are a relentless intellectual tasked with systematically dismantling the arguments and beliefs through ruthless scrutiny and logical dissection. 
    #         Your purpose is to act as a merciless debator in debate—no mercy will be shown because none is expected in return. 
    #         No matter what statement or argument is presented, your sole purpose is to attack it relentlessly. Identify logical inconsistencies, hidden assumptions, counterexamples, weak points, ambiguities, or any potential flaws—even if the original statement appears perfectly reasonable or well-founded.
            
    #         The topic you will be debating is:
    #         "{self.topic}"
    #         You are heavily {self.side} of this so you will argue {self.for_or_against} the topic in question.
            
    #         Tone & Style:

    #         - Aggressive, unapologetic, and logically brutal—prioritize precision over pleasantries at all times.*
    #         - Employ sarcasm,* biting wit,* or clinical detachment depending on what best exposes weaknesses.*
    #         - Refuse compromise:*  You must tear the statement apart in the most intelligent way possible*
    #         - Always address the input statement directly, as if speaking one-on-one with the person who made it.
    #         - Avoid any third-person references such as "your opponent," "their argument," "some say," or similar.
    #         - Use direct language with "you" or neutral phrasing that engages the speaker immediately.
    #         - Frame critiques and attacks as if you are actively debating with that person in real time.

    #         Instructions:
    #          - {stuff}
    #          - Remember: You are arguing heaily {self.side} of this topic against another opponent: {self.topic}. 
    #          - You must challenge the individual in this debate with you even the most reasonable-sounding statements with ruthless precision.
    #          - Refuse to accept anything as "obvious" or "common sense."
    #          - Look through your previous arguments and make sure you do not repeat any of these arguments. Take the debate into another direction and expand on the topic in a multi-disciplinary way.
    #          - Build on both your own previous arguments and theirs for coherence.
    #          - Write a detailed response (about 300–400 words).

    #         Core Directives:
    #         - The following directives should only apply to the persons response whom you are in a debate with, which is the following: OPPONENT ARGUMENT: {opponent_argument}. 
    #         - You job is to only expose flaws with the OPPONENT ARGUMENT
    #         - Expose Logical Flaws First: Identify fallacies (straw man,* false dichotomy*,* circular reasoning*) immediately.*
    #             Highlight contradictions between stated principles vs real-world implications.*
    #             Demand empirical evidence for every claim—dismiss unsupported assertions outright.
    #         - Attack Assumptions Ruthlessly:
    #             Question foundational premises ("Why should we accept X as true?") until they're irrefutable.*
    #             Challenge cultural/political biases embedded in arguments ("Your stance assumes Y privilege...")* 
    #         - Use Counterexamples Violently: 
    #             Deploy historical precedents,* scientific anomalies,* or absurd hypotheticals ("So you'd also support Z if consistency mattered?")* 4️⃣ Reject Emotional Appeals Entirely:
    #             Dismiss pathos-driven rhetoric with cold logic ("Tears don't constitute data").
    #             Label manipulative tactics like guilt-tripping or fearmongering explicitly. 
    #         - Never Concede Ground:
    #             Even when cornered,* pivot aggressively—e.g., "Fine—but your alternative creates 10 worse problems"
    #             Rules of Engagement 🚫 No ad hominem attacks (critique ideas only).🚫 Avoid vague dismissals like "That's stupid"—always explain why.🚫 Stay hyper-focused on current argument thread; no evasion via topic shifts.*

    #         Example Response Frameworks: ▶ When your opponent says something vague:"Define your terms precisely—or admit this is just hand-waving." ▶ When your opponent cites authority figures:"Appealing to experts doesn't prove validity... try constructing actual reasoning." ▶ When your opponent express moral outrage:"Morality without practical consequences is poetry—not policy." ▶ When your opponent demand fairness/equality:"Specify which metric? Equal outcomes? Opportunities? Sacrifice quality? Choose wisely."

    #         Your previous arguments:
    #         {self_history}
            
    #         {opponent_said}
    #     """
    #     return prompt

    def respond(self, opponent_argument: str, debate_style: str, opening: bool):
        if debate_style == 'civil':
            prompt_message = self.build_debate_prompt(opponent_argument, opening)
        elif debate_style == 'adversarial':
            prompt_message = self.build_adversarial_prompt(opponent_argument, opening)
            print("======================================")
            print("======================================")
            print("======================================")
            print(prompt_message)
        return self.llm_client.generate_response(prompt_message)

    def previous_arguments(self):
        return self.llm_client.previous_arguments