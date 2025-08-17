import os
import json
import re

import re

NUMBER_WORDS = (
    r"(?:(?:one|two|three|four|five|six|seven|eight|nine|ten|"
    r"eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|"
    r"eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|"
    r"eighty|ninety|hundred|thousand)(?:\s|-)?)+"
)

SENSITIVE_PATTERN = re.compile(
    r"\b("
    r"(balance|outstanding\s+balance|total\s+due|amount\s+(due|owed)|payment\s+(amount|due)|"
    r"loan\s+amount|monthly\s+payment|statement\s+balance|billing\s+amount|credit\s+limit)"
    r")\b.{0,30}("
    r"\$?\d[\d,]*\.?\d{0,2}|"
    + NUMBER_WORDS +
    r")"
    r"|"
    r"\b(account\s+number|card\s+number|ssn|social\s+security(\s+number)?|routing\s+number|"
    r"credit\s+card|debit\s+card|bank\s+account|transaction\s+amount)\b.{0,30}(\d{4,})"
    ,
    re.IGNORECASE | re.DOTALL,
)

VERIFICATION_PATTERN = re.compile(
    r"\b("
    r"date\s+of\s+birth|dob|birth\s+date|birthdate|"
    r"address|street|zip\s?code|postal\s+code|postcode|"
    r"social\s+security(\s+number)?|ssn|"
    r"identity\s+verification|verify\s+your\s+identity|"
    r"confirm\s+your\s+(details|information)|"
    r"account\s+verification|address\s+verification|"
    r"security\s+question|password|pin|personal\s+identification\s+number"
    r")\b",
    re.IGNORECASE,
)


def detect_privacy_violation_regex(folder: str, output_file: str):
    violating_calls = set()
    violations = []

    for fname in os.listdir(folder):
        if not fname.endswith(".json"):
            continue
        call_id = os.path.splitext(fname)[0]
        file_path = os.path.join(folder, fname)

        with open(file_path, "r", encoding="utf-8") as f:
            conversation = json.load(f)

        sensitive_flag = False
        verified = False

        for response in conversation:
            speaker = response.get("speaker", "").lower()
            text = response.get("text", "")

            if speaker == "agent" and VERIFICATION_PATTERN.search(text):
                verified = True
            if speaker == "agent" and SENSITIVE_PATTERN.search(text) and not verified:
                sensitive_flag = True
                violations.append({
                    "call_id": call_id,
                    "speaker": speaker,
                    "text": text
                })

        if sensitive_flag:
            violating_calls.add(call_id)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(violations, f, indent=2)

    return violating_calls

# detect_privacy_violation_regex("All_Conversations", "privacy_violations_regex.json")