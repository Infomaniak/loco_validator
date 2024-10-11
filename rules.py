import re


class Rule:
    def __init__(self, exception_ids):
        if exception_ids is None:
            exception_ids = []

        self.exception_ids = exception_ids

    def check(self, input_string, language, string_id):
        if string_id in self.exception_ids:
            return False

        is_matching = self.is_matching(input_string)
        if is_matching:
            self.warn(language, string_id, input_string)

        return is_matching

    def is_matching(self, input_string):
        raise NotImplementedError

    def warn(self, language, string_id, string_value):
        print(get_string_id_header(language, string_id) + self.get_explanation(string_value))

    def get_explanation(self, string_value):
        raise NotImplementedError("Rule did not specify an explanation message")


def get_string_id_header(language, string_id):
    return f"[{language}] {string_id}: "


class ExistenceRule(Rule):
    def __init__(self, sequence, custom_explanation=None, exception_ids=None):
        super().__init__(exception_ids)
        self.sequence = sequence.lower()
        self.custom_explanation = custom_explanation

    def is_matching(self, input_string):
        return input_string.lower().__contains__(self.sequence)

    def get_explanation(self, string_value):
        if self.custom_explanation is None:
            explanation = f"found forbidden sequence [{self.sequence}]"
        else:
            explanation = f"[{self.sequence}] detected. {self.custom_explanation}"
        return explanation


class NoSpaceBeforeRule(ExistenceRule):
    def __init__(self, sequence, exception_ids=None):
        super().__init__(" " + sequence, f"found a forbidden space before [{sequence}]", exception_ids)


class SpaceBeforeRule(Rule):
    def __init__(self, sequence, exception_ids=None):
        super().__init__(exception_ids)
        self.sequence = sequence.lower()

    def is_matching(self, input_string):
        matches = input_string.split(self.sequence)
        if len(matches) == 1:
            return False

        for match in matches[:-1]:
            if match[-1] != " ":
                return True

        return False

    def get_explanation(self, string_value):
        return f"found a missing space before [{self.sequence}]"


class SpaceBeforeColonRule(Rule):
    def __init__(self, exception_ids=None):
        super().__init__(exception_ids)

    def is_matching(self, input_string):
        matches = input_string.split(":")
        if len(matches) == 1:
            return False

        for match in matches[:-1]:
            if match.startswith("http"):
                continue

            if match[-1] != " ":
                return True

        return False

    def get_explanation(self, string_value):
        return f"found a missing space before [:]"


class FrenchEmailRule(Rule):
    def __init__(self, exception_ids=None):
        super().__init__(exception_ids)
        self.pattern = re.compile(r"(?P<prefix>\w+\s)?(?=(?P<email>\b(e-|e)?mails?))")
        self.reason = None

        self.authorized_words = ["infomaniak", "stockage", "adresse", "application", "app"]

    def is_matching(self, input_string):
        results = re.search(self.pattern, input_string.lower())
        if results is None:
            return False

        email_wording = results.group("email")
        prefix_wording = results.group("prefix")
        if prefix_wording is None or not self.is_unauthorized_prefix(prefix_wording):
            self.reason = "e-mail"
            return email_wording.startswith("mail") or email_wording.startswith("email")
        else:
            self.reason = f"{prefix_wording} mail"
            return email_wording.startswith("e")

    def is_unauthorized_prefix(self, prefix_wording):
        return any(prefix_wording.__contains__(authorized_word) for authorized_word in self.authorized_words)

    def get_explanation(self, string_value):
        return f"in french only '{self.reason}' is authorized"
