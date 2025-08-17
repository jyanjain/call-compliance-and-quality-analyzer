import os
import json
import joblib

vectorizer = joblib.load("tfidf_vectorizer.pkl")
model = joblib.load("logreg_model.pkl")

def detect_profanity_ml(folder: str):

    agent_profanity_calls = set()
    customer_profanity_calls = set()
    profane_records = []

    for file in os.listdir(folder):
        if file.endswith(".json"):
            call_id = os.path.splitext(file)[0]
            file_path = os.path.join(folder, file)

            with open(file_path, "r", encoding="utf-8") as f:
                conversation = json.load(f)

            for response in conversation:
                speaker = response.get("speaker", "").lower()
                text = response.get("text", "")

                X_text = vectorizer.transform([text])
                proba = model.predict_proba(X_text)[0]

                if proba[1] >= 0.54:
                    if "Who's calling" in text or "confirm your address" in text or "verify your address" in text or "verify your name" in text or "tell me your address" in text or "confirm your name" in text:
                        continue
                    profane_records.append({
                        "call_id": call_id,
                        "speaker": speaker,
                        "text": text
                    })
                    if speaker == "agent":
                        agent_profanity_calls.add(call_id)
                    elif speaker == "customer":
                        customer_profanity_calls.add(call_id)

    with open("profane_ml_texts.json", "w", encoding="utf-8") as out_f:
        json.dump(profane_records, out_f, ensure_ascii=False, indent=2)

    return agent_profanity_calls, customer_profanity_calls

detect_profanity_ml("All_Conversations")