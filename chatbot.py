import re
from datetime import datetime


# ======================================================================
#  ASSISTANT STATE
# ======================================================================

def create_state():
    return {
        "user_name": None,
        "notes": [],
        "reminders": [],
        "commands_run": 0,
        "session_start": datetime.now()
    }


# ======================================================================
#  HELPERS
# ======================================================================

def normalize(text):
    return text.lower().strip()


def contains_any(text, keyword_list):
    for keyword in keyword_list:
        if keyword in text:
            return True
    return False


def address(state):
    """Return the user's name if known, otherwise 'sir'."""
    return state["user_name"] if state["user_name"] else "sir"


# ======================================================================
#  FEATURE 1: TIME & DATE
# ======================================================================

def handle_time():
    now = datetime.now()
    return "The current time is " + now.strftime("%I:%M %p") + "."


def handle_date():
    now = datetime.now()
    return "Today is " + now.strftime("%A, %B %d, %Y") + "."


# ======================================================================
#  FEATURE 2: CALCULATOR
# ======================================================================

ALLOWED_CALC_CHARS = set("0123456789+-*/(). ")


def calculate(raw_input):
    match = re.search(r"(?:calculate|what is|what's|compute)\s+(.+)", raw_input, re.IGNORECASE)
    expression = match.group(1).strip() if match else raw_input.strip()
    expression = expression.rstrip("?")

    if not expression:
        return "I'll need an actual expression to calculate."

    if not set(expression).issubset(ALLOWED_CALC_CHARS):
        return "I can only process numbers and + - * / ( ) at the moment. Try something like: calculate 45 * 3"

    try:
        result = eval(expression, {"__builtins__": {}}, {})
    except ZeroDivisionError:
        return "That would require dividing by zero. I'd rather not."
    except Exception:
        return "I couldn't parse that expression. Mind rephrasing it?"

    return expression + " equals " + str(result)


def looks_like_math(text):
    """Detect plain arithmetic typed without a trigger word, e.g. '12 * 4'."""
    stripped = text.strip().rstrip("?")
    if not stripped:
        return False
    has_operator = any(op in stripped for op in ["+", "-", "*", "/"])
    is_safe = set(stripped).issubset(ALLOWED_CALC_CHARS | {"?"})
    return has_operator and is_safe and any(char.isdigit() for char in stripped)


# ======================================================================
#  FEATURE 3: UNIT CONVERSIONS
# ======================================================================

def convert_units(raw_input):
    text = normalize(raw_input)

    celsius_match = re.search(r"([-+]?\d*\.?\d+)\s*(?:c|celsius|degrees c)\s*(?:to|in)\s*f", text)
    fahrenheit_match = re.search(r"([-+]?\d*\.?\d+)\s*(?:f|fahrenheit|degrees f)\s*(?:to|in)\s*c", text)

    if celsius_match:
        celsius = float(celsius_match.group(1))
        fahrenheit = (celsius * 9 / 5) + 32
        return str(celsius) + "°C is " + str(round(fahrenheit, 1)) + "°F."

    if fahrenheit_match:
        fahrenheit = float(fahrenheit_match.group(1))
        celsius = (fahrenheit - 32) * 5 / 9
        return str(fahrenheit) + "°F is " + str(round(celsius, 1)) + "°C."

    km_match = re.search(r"([-+]?\d*\.?\d+)\s*(?:km|kilometers?)\s*(?:to|in)\s*mi", text)
    mi_match = re.search(r"([-+]?\d*\.?\d+)\s*(?:mi|miles?)\s*(?:to|in)\s*km", text)

    if km_match:
        km = float(km_match.group(1))
        miles = km * 0.621371
        return str(km) + " km is approximately " + str(round(miles, 2)) + " miles."

    if mi_match:
        miles = float(mi_match.group(1))
        km = miles * 1.60934
        return str(miles) + " miles is approximately " + str(round(km, 2)) + " km."

    kg_match = re.search(r"([-+]?\d*\.?\d+)\s*(?:kg|kilograms?)\s*(?:to|in)\s*lb", text)
    lb_match = re.search(r"([-+]?\d*\.?\d+)\s*(?:lb|lbs|pounds?)\s*(?:to|in)\s*kg", text)

    if kg_match:
        kg = float(kg_match.group(1))
        pounds = kg * 2.20462
        return str(kg) + " kg is approximately " + str(round(pounds, 2)) + " lb."

    if lb_match:
        pounds = float(lb_match.group(1))
        kg = pounds * 0.453592
        return str(pounds) + " lb is approximately " + str(round(kg, 2)) + " kg."

    return None


# ======================================================================
#  FEATURE 4: NOTES
# ======================================================================

def add_note(state, raw_input):
    match = re.search(r"(?:note|remember)\s*(?:that|this)?\s*:?\s*(.+)", raw_input, re.IGNORECASE)
    note_text = match.group(1).strip(" :") if match else ""

    if not note_text:
        return "What would you like me to note down?"

    state["notes"].append(note_text)
    return "Noted: \"" + note_text + "\". That's note #" + str(len(state["notes"])) + "."


def list_notes(state):
    if not state["notes"]:
        return "You don't have any notes saved yet."

    lines = ["Here are your saved notes:"]
    for index, note in enumerate(state["notes"], start=1):
        lines.append("  " + str(index) + ". " + note)
    return "\n".join(lines)


# ======================================================================
#  FEATURE 5: REMINDERS
# ======================================================================

def add_reminder(state, raw_input):
    match = re.search(r"remind me (?:to)?\s*(.+)", raw_input, re.IGNORECASE)
    if not match or not match.group(1).strip():
        return "What should I remind you about?"

    reminder_text = match.group(1).strip()
    state["reminders"].append(reminder_text)
    return "I'll remember that: \"" + reminder_text + "\". (Reminder #" + str(len(state["reminders"])) + " logged for this session.)"


def list_reminders(state):
    if not state["reminders"]:
        return "You have no active reminders."

    lines = ["Here's what you asked me to remind you about:"]
    for index, reminder in enumerate(state["reminders"], start=1):
        lines.append("  " + str(index) + ". " + reminder)
    return "\n".join(lines)


# ======================================================================
#  FEATURE 6: GENERAL KNOWLEDGE BASE
# ======================================================================

KNOWLEDGE_BASE = {
    "capital of france": "Paris is the capital of France.",
    "capital of pakistan": "Islamabad is the capital of Pakistan.",
    "capital of japan": "Tokyo is the capital of Japan.",
    "capital of usa": "Washington, D.C. is the capital of the United States.",
    "capital of uk": "London is the capital of the United Kingdom.",
    "capital of italy": "Rome is the capital of Italy.",
    "capital of china": "Beijing is the capital of China.",
    "capital of india": "New Delhi is the capital of India.",
    "largest planet": "Jupiter is the largest planet in our solar system.",
    "smallest planet": "Mercury is the smallest planet in our solar system.",
    "largest ocean": "The Pacific Ocean is the largest ocean on Earth.",
    "largest country": "Russia is the largest country in the world by area.",
    "tallest mountain": "Mount Everest is the tallest mountain above sea level, at 8,849 meters.",
    "longest river": "The Nile is traditionally considered the longest river in the world.",
    "speed of light": "The speed of light is approximately 299,792 kilometers per second.",
    "boiling point of water": "Water boils at 100°C (212°F) at standard atmospheric pressure.",
    "freezing point of water": "Water freezes at 0°C (32°F) at standard atmospheric pressure.",
    "who wrote romeo and juliet": "Romeo and Juliet was written by William Shakespeare.",
    "who painted mona lisa": "The Mona Lisa was painted by Leonardo da Vinci.",
    "creator of python": "Python was created by Guido van Rossum, first released in 1991.",
    "founder of microsoft": "Microsoft was founded by Bill Gates and Paul Allen.",
    "founder of apple": "Apple was founded by Steve Jobs, Steve Wozniak, and Ronald Wayne.",
    "number of continents": "There are seven continents: Africa, Antarctica, Asia, Australia, Europe, North America, and South America.",
    "number of planets": "There are eight planets in our solar system, following Pluto's reclassification in 2006.",
    "human body bones": "An adult human body has 206 bones.",
    "value of pi": "Pi (\u03c0) is approximately 3.14159.",
}


def search_knowledge_base(raw_input):
    text = normalize(raw_input)
    text = re.sub(r"[?!.]", "", text)

    for key, fact in KNOWLEDGE_BASE.items():
        if key in text:
            return fact

    return None


# ======================================================================
#  FEATURE 7: SYSTEM DIAGNOSTICS
# ======================================================================

def system_status(state):
    uptime = datetime.now() - state["session_start"]
    minutes = int(uptime.total_seconds() // 60)
    seconds = int(uptime.total_seconds() % 60)

    lines = [
        "Running a quick diagnostic, " + address(state) + ":",
        "  Session uptime     : " + str(minutes) + "m " + str(seconds) + "s",
        "  Commands processed : " + str(state["commands_run"]),
        "  Notes stored       : " + str(len(state["notes"])),
        "  Reminders active   : " + str(len(state["reminders"])),
        "  Status             : All systems nominal."
    ]
    return "\n".join(lines)


# ======================================================================
#  IDENTITY HANDLING
# ======================================================================

NAME_INTRO_KEYWORDS = ["my name is", "call me", "this is"]


def handle_identity(raw_input, state):
    text = normalize(raw_input)
    for phrase in NAME_INTRO_KEYWORDS:
        if phrase in text:
            after = text.split(phrase, 1)[1].strip()
            name_word = after.split(" ")[0].strip(".,!?")
            if name_word.isalpha():
                state["user_name"] = name_word.capitalize()
                return "Understood. I'll address you as " + state["user_name"] + " from now on."
    return None


# ======================================================================
#  INTENT KEYWORDS
# ======================================================================

GREETING_KEYWORDS = ["hello jarvis", "hello", "hi jarvis", "hi", "hey jarvis", "hey", "good morning", "good evening"]
FAREWELL_KEYWORDS = ["goodbye", "shut down", "power down", "exit", "quit", "that's all", "bye"]
THANKS_KEYWORDS = ["thank you", "thanks", "appreciate it"]
HELP_KEYWORDS = ["help", "what can you do", "your capabilities", "commands"]
IDENTITY_KEYWORDS = ["who are you", "what are you"]
WELLBEING_KEYWORDS = ["how are you"]


# ======================================================================
#  MAIN RESPONSE ROUTER
# ======================================================================

def handle_command(raw_input, state):
    user_input = normalize(raw_input)
    state["commands_run"] += 1

    identity_response = handle_identity(raw_input, state)
    if identity_response:
        return identity_response

    if contains_any(user_input, HELP_KEYWORDS):
        return help_text()

    elif contains_any(user_input, IDENTITY_KEYWORDS):
        return (
            "I'm JARVIS — Just A Rather Very Intelligent System. Think of me as your "
            "personal assistant: part calculator, part notepad, part walking encyclopedia."
        )

    elif contains_any(user_input, WELLBEING_KEYWORDS):
        return "All systems operating within normal parameters. Thank you for asking, " + address(state) + "."

    elif contains_any(user_input, THANKS_KEYWORDS):
        return "Always a pleasure, " + address(state) + "."

    elif "time" in user_input and "what" in user_input:
        return handle_time()

    elif "date" in user_input or "what day is it" in user_input or "today" in user_input:
        return handle_date()

    elif "note" in user_input and ("remember that" in user_input or user_input.startswith("note")):
        return add_note(state, raw_input)

    elif "my notes" in user_input or user_input == "notes" or "list notes" in user_input:
        return list_notes(state)

    elif "remind me" in user_input:
        return add_reminder(state, raw_input)

    elif "my reminders" in user_input or "list reminders" in user_input:
        return list_reminders(state)

    elif "status" in user_input or "diagnostic" in user_input:
        return system_status(state)

    elif contains_any(user_input, GREETING_KEYWORDS):
        greeting_options = [
            "At your service, " + address(state) + ".",
            "Good to see you, " + address(state) + ". What can I do for you?",
            "Online and ready, " + address(state) + "."
        ]
        return greeting_options[state["commands_run"] % len(greeting_options)]

    elif contains_any(user_input, ["calculate", "compute"]) or looks_like_math(raw_input):
        return calculate(raw_input)

    conversion_result = convert_units(raw_input)
    if conversion_result:
        return conversion_result

    knowledge_result = search_knowledge_base(raw_input)
    if knowledge_result:
        return knowledge_result

    return (
        "I don't have an answer for that one, " + address(state) + ". I'm built on a fixed "
        "knowledge base and a set of rules, not a live connection to the wider internet — "
        "so anything outside what I've been taught is genuinely outside my reach. "
        "Try 'help' to see what I'm actually equipped to do."
    )


def help_text():
    return (
        "Here is what I'm currently equipped to handle:\n\n"
        "  TIME & DATE\n"
        "    what time is it / what is today's date\n\n"
        "  CALCULATOR\n"
        "    calculate <expression>     e.g. calculate (45 + 30) / 3\n"
        "    or just type math directly, e.g. 12 * 8\n\n"
        "  UNIT CONVERSION\n"
        "    25 c to f      |      10 km to mi      |      150 lb to kg\n\n"
        "  NOTES\n"
        "    note: <text>  or  remember that <text>\n"
        "    my notes\n\n"
        "  REMINDERS\n"
        "    remind me to <text>\n"
        "    my reminders\n\n"
        "  KNOWLEDGE BASE\n"
        "    capital of france | largest planet | speed of light | who wrote romeo and juliet\n"
        "    (and several dozen other common facts)\n\n"
        "  SYSTEM\n"
        "    status              - session diagnostics\n"
        "    my name is <name>   - I'll address you by name\n"
        "    goodbye             - end the session\n\n"
        "I'm honest about my limits: if something falls outside this list, I'll tell you "
        "rather than guess."
    )


# ======================================================================
#  MAIN LOOP
# ======================================================================

def print_intro():
    print()
    print("=" * 60)
    print("                         J.A.R.V.I.S.")
    print("           Just A Rather Very Intelligent System")
    print("=" * 60)
    print(" Initializing personal assistant protocols... done.")
    print(" I can handle calculations, conversions, notes, reminders,")
    print(" general knowledge queries, and system diagnostics.")
    print(" Type 'help' anytime for the full list of what I can do.")
    print("=" * 60)
    print()


def run_assistant():
    state = create_state()
    print_intro()

    is_done = False

    while not is_done:
        user_input = input("You: ").strip()

        if not user_input:
            print("JARVIS: I didn't receive any input, " + address(state) + ".")
            continue

        normalized = normalize(user_input)

        if contains_any(normalized, FAREWELL_KEYWORDS):
            state["commands_run"] += 1
            print("JARVIS: " + system_status(state))
            print()
            print("JARVIS: Powering down this session. Until next time, " + address(state) + ".")
            is_done = True
            continue

        response = handle_command(user_input, state)
        print("JARVIS: " + response)
        print()

run_assistant()
