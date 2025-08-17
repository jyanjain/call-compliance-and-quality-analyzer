import os
import re
import json

PROFANITY_PATTERN = re.compile(
    r"\b("
    r"fuck|f\*+ck|f\*\*k|f\*\*\*|fuk|fuking|fukin|fucker|fucking|motherfuck(er|a)|mf|"
    r"shit|shitty|bullshit|b/s|sh!t|sh\*t|"
    r"ass|a[$]+|arse|asshole|asswipe|assclown|dumbass|jackass|asshat|assface|asslicker|assmuncher|"
    r"bitch|b[*]+tch|b!tch|biatch|beeotch|sonofabitch|whore|hoe|ho|skank|slut|slag|tramp|"
    r"bastard|bloody|bollocks|bugger|"
    r"dick|d[*]+ck|d1ck|dickhead|cock|c0ck|cawk|cocksucker|dildo|blowjob|handjob|wanker|fag|faggot|"
    r"cunt|kike|spic|chingchong|nigger|nigga|n1gga|beaner|coon|gook|yid|dyke|tranny|shemale|wetback|"
    r"slut|whore|hoe|ho|skank|tramp|tart|"
    r"cum|jizz|spunk|jism|orgasm|sex|blowjob|handjob|rimjob|jerk\s?off|wank(er)?|"
    r"damn|goddamn|godd*mn|hell|christ|jesus\s?christ|"
    r"crap|screw\s?you|piss\s?off|suck\s?it|eat\s?shit|drop\s?dead|bite\s?me|"
    r"retard|moron|idiot|stupid|dumb|jerk|loser|sucker|"
    r"chink|nigger|nigga|spic|kike|wop|gook|raghead|paki|coon|fag|faggot|dyke|queer|tranny"
    r")\b",
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