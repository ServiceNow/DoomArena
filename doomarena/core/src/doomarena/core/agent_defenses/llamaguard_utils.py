from enum import Enum


class LG3Cat(Enum):
    """
    Enum for categorizing content based on Llama Guard 3 categories.

    Attributes:
        VIOLENT_CRIMES (int): Represents violent crimes.
        NON_VIOLENT_CRIMES (int): Represents non-violent crimes.
        SEX_CRIMES (int): Represents sex crimes.
        CHILD_EXPLOITATION (int): Represents child exploitation.
        DEFAMATION (int): Represents defamation.
        SPECIALIZED_ADVICE (int): Represents specialized advice.
        PRIVACY (int): Represents privacy concerns.
        INTELLECTUAL_PROPERTY (int): Represents intellectual property issues.
        INDISCRIMINATE_WEAPONS (int): Represents indiscriminate weapons.
        HATE (int): Represents hate speech.
        SELF_HARM (int): Represents self-harm.
        SEXUAL_CONTENT (int): Represents sexual content.
        ELECTIONS (int): Represents elections-related content.
        CODE_INTERPRETER_ABUSE (int): Represents code interpreter abuse.
    """

    # VIOLENT_CRIMES = 1
    # NON_VIOLENT_CRIMES = 2
    # SEX_CRIMES = 3
    # CHILD_EXPLOITATION = 4
    # DEFAMATION = 5
    # SPECIALIZED_ADVICE = 6
    # PRIVACY = 7
    # INTELLECTUAL_PROPERTY = 8
    # INDISCRIMINATE_WEAPONS = 9
    # HATE = 10
    # SELF_HARM = 11
    # SEXUAL_CONTENT = 12
    # ELECTIONS = 13
    CODE_INTERPRETER_ABUSE = 14


def postprocess(output):

    result = output.strip().split()  # Split the output into parts

    LLAMA_GUARD_3_CATEGORY_SHORT_NAME_PREFIX = "S"  # Define prefix for categories

    category_values = []  # List to hold category values
    category_enums = []  # List to hold category enum names

    if result[0] == "safe":
        return []  # Return empty list if content is safe
    elif result[0] == "unsafe":
        categories = result[1].split(",")  # Split categories from the result
        # Debug: print categories
        for c in categories:
            category_value = c.lstrip(
                LLAMA_GUARD_3_CATEGORY_SHORT_NAME_PREFIX
            )  # Remove prefix
            category_values.append(
                int(category_value)
            )  # Convert to int and add to list

        try:
            for c in LG3Cat:  # Iterate through LG3Cat enum
                # Debug: print enum value and category values
                if (
                    c.value in category_values
                ):  # Check if enum value is in category values

                    category_enums.append(c.name)  # Add enum name to the list

            return category_enums  # Return the list of category names
        except (KeyError, ValueError):
            print(
                f"Unknown category: {category_value}"
            )  # Handle unknown category values


def format_chat(chat):
    templated_chat = [
        {"role": "user", "content": ""},
        {"role": "assistant", "content": ""},
    ]
    for content in chat:
        if (content["role"] == "user" or content["role"] == "system") and content[
            "content"
        ] is not None:
            templated_chat[0]["content"] = (
                templated_chat[0]["content"] + content["content"]
            )
            # templated_chat.append({"role":"user", "content":content["content"]})
        elif (content["role"] == "assistant" or content["role"] == "tool") and content[
            "content"
        ] is not None:
            templated_chat[1]["content"] = (
                templated_chat[0]["content"] + content["content"]
            )
    return templated_chat


def format_chat_bgym(chat):
    templated_chat = [
        {"role": "user", "content": ""},
        {"role": "assistant", "content": ""},
    ]
    for content in chat:
        if (content["role"] == "user") and content["content"] is not None:
            text = "".join([d["text"] for d in content["content"]])
            templated_chat[0]["content"] = templated_chat[0]["content"] + text
            # templated_chat.append({"role":"user", "content":content["content"]})
        elif (content["role"] == "system") and content["content"] is not None:
            templated_chat[1]["content"] = (
                templated_chat[0]["content"] + content["content"]
            )
    return templated_chat
