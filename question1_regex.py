import os
import re
import json

PROFANITY_PATTERN = re.compile(
    r"("
    r"\b(?:fuck|f\*+ck|f\*\*k|f\*\*\*|fuk|fuking|fukin|fucker|fucking|motherfuck(?:er|a)|mf)\b|"
    r"\b(?:shit|shitty|bullshit|b/s|sh!t|sh\*t)\b|"
    r"\b(?:ass|a[$]+|arse|asshole|asswipe|assclown|dumbass|jackass|asshat|assface|asslicker|assmuncher)\b|"
    r"\b(?:bitch|b[*]+tch|b!tch|biatch|beeotch|sonofabitch|whore|hoe|ho|skank|slut|slag|tramp)\b|"
    r"\b(?:bastard|bloody|bollocks|bugger)\b|"
    r"\b(?:damn|dick|d[*]+ck|d1ck|dickhead|cock|c0ck|cawk|cocksucker|dildo|blowjob|handjob|wanker|fag|faggot)\b|"
    r"\b(?:cunt|kike|spic|chingchong|nigger|nigga|n1gga|beaner|coon|gook|yid|dyke|tranny|shemale|wetback)\b|"
    r"\b(?:cum|jizz|spunk|jism|orgasm|sex|blowjob|handjob|rimjob)\b|"
    r"\bjerk\s?off\b|\bwank(?:er)?\b|"
    r"\b(?:goddamn|godd\*mn|hell|christ)\b|\bjesus\s?christ\b|"
    r"\bcrap\b|\bscrew\s?you\b|\bpiss\s?off\b|\bsuck\s?it\b|\beat\s?shit\b|\bdrop\s?dead\b|\bbite\s?me\b|"
    r"\b(?:retard|moron|idiot|stupid|dumb|jerk|loser|sucker)\b|"
    r"\b(?:chink|wop|raghead|paki|queer)\b|"
    r"wasting\s+my\s+time|"
    r"stop\s+wasting\s+my\s+time"
    r")",
    re.IGNORECASE
)

def detect_profanity_regex(folder: str):
    agent_profanity_calls = set()
    borrower_profanity_calls = set()
    profane_records = []

    for file in os.listdir(folder):
        if file.endswith(".json"):
            call_id = os.path.splitext(file)[0]  
            file_path = os.path.join(folder, file)

            with open(file_path, "r", encoding="utf-8") as f:
                conversation = json.load(f)

            for responses in conversation:
                speaker = responses.get("speaker", "").lower()
                text = responses.get("text", "")

                if PROFANITY_PATTERN.search(text):
                    profane_records.append({
                        "call_id": call_id,
                        "speaker": speaker,
                        "text": text
                    })
                    if speaker == "agent":
                        agent_profanity_calls.add(call_id)
                    elif speaker == "customer":
                        borrower_profanity_calls.add(call_id)

    with open("profane_regex_texts.json", "w", encoding="utf-8") as out_f:
        json.dump(profane_records, out_f, ensure_ascii=False, indent=2)

    return agent_profanity_calls, borrower_profanity_calls

# detect_profanity_regex("All_Conversations")