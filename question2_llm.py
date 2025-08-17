import os
import json
import time
from groq import Groq
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
MODEL_NAME = "gemini-1.5-flash"

def check_privacy_with_llm(call_id, conversation):
    system_prompt = """
You are a compliance auditor analyzing call center conversations between agents and customers.

Your task is to identify all utterances by the AGENT where sensitive financial or account information is shared (such as balance amounts, payment details, account numbers, Social Security Numbers, loan amounts, routing numbers, credit card numbers, etc.) **before the customer's identity has been properly verified**.

Proper identity verification must involve confirmation of one or more of the following **before** any sensitive disclosure:
- Date of birth, address, Social Security Number, postal or zip code, security questions, password, PIN, or personal identification number.
- Simply asking for or stating the customer's NAME alone does NOT count as verification.

if customer verification is given, you should not flag the utterance.
so you will be provided with the agent and customers text line by line by the timeline order
so if a verification from customer is given before and then the agent presents the sensitive information, you should not flag that utterance.

Output Format:
- Return a strict JSON array listing all violating utterances.
- Each entry must have keys: "call_id", "speaker" (always "agent"), and the full "text" of the utterance.
- If no violations are found, return an empty JSON array: [].
- Do NOT include any explanations or additional text.

Analyze the conversation below and respond accordingly.
"""

    user_message = "Conversation:\n"
    for utt in conversation:
        speaker = utt.get("speaker", "")
        text = utt.get("text", "")
        user_message += f'- Speaker: {speaker}, Text: "{text}"\n'

    try:
        model = genai.GenerativeModel(
            model_name=MODEL_NAME,
            system_instruction=system_prompt,
        )

        response = model.generate_content(
            user_message,
            generation_config={"response_mime_type": "application/json"}  
        )
        output = response.text.strip()

    except:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=0,
        )
        output = response.choices[0].message.content.strip()

    try:
        parsed = json.loads(output)
    except Exception:
        parsed = []

    for v in parsed:
        v["call_id"] = call_id

    return parsed


def detect_privacy_violation_llm(folder: str, output_file: str):
    violations = []

    for fname in os.listdir(folder):
        if not fname.endswith(".json"):
            continue
        call_id = os.path.splitext(fname)[0]
        file_path = os.path.join(folder, fname)

        with open(file_path, "r", encoding="utf-8") as f:
            conversation = json.load(f)

        results = check_privacy_with_llm(call_id, conversation)
        # print(results)

        if results:
            violations.extend(results)

        time.sleep(2.5)  
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(violations, f, indent=2)

    return {v["call_id"] for v in violations}

# detect_privacy_violation_llm("All_Conversations", "privacy_violations_llm.json")