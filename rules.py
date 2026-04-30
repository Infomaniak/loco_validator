import re


class Rule:
    def __init__(self, exception_ids):
        if exception_ids is None:
            exception_ids = []

        self.exception_ids = exception_ids

    def check(self, input_string, language, string_id):
        if string_id in self.exception_ids:
            return False

        if input_string == "" or input_string is None:
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


class EndsWithRule(Rule):
    def __init__(self, sequence, custom_explanation=None, exception_ids=None):
        super().__init__(exception_ids)
        self.sequence = sequence.lower()
        self.custom_explanation = custom_explanation

    def is_matching(self, input_string):
        return input_string.lower().endswith(self.sequence)

    def get_explanation(self, string_value):
        if self.custom_explanation is None:
            explanation = f"ends with forbidden sequence [{self.sequence}]"
        else:
            explanation = f"ending [{self.sequence}] detected. {self.custom_explanation}"
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


class CrossLocaleRule:
    """Base class for rules that validate a key across all its locale translations at once."""

    def __init__(self, exception_ids=None):
        if exception_ids is None:
            exception_ids = []

        self.exception_ids = exception_ids

    def check(self, string_id, translations):
        """Check a key across all its translations.

        Args:
            string_id: The key identifier.
            translations: A dict of {locale: value} for this key.

        Returns:
            True if the rule detected an error, False otherwise.
        """
        if string_id in self.exception_ids:
            return False

        is_matching = self.is_matching(translations)
        if is_matching:
            self.warn(string_id, translations)

        return is_matching

    def is_matching(self, translations):
        """Return True if the translations violate the rule."""
        raise NotImplementedError

    def warn(self, string_id, translations):
        header = get_string_id_header("all", string_id)
        print(f"{header}{self.get_explanation(translations)}")

    def get_explanation(self, translations):
        raise NotImplementedError("CrossLocaleRule did not specify an explanation message")


class PlaceholderConsistencyRule(CrossLocaleRule):
    """Ensures that all translations of a key use the same placeholders (e.g. %s, %d, %1$s, %@).

    Plurals (when the value is a dict keyed by plural form like 'one', 'other', ...) are checked
    per form across locales: different forms of the same plural may legitimately use different
    placeholders, but a given form must be consistent across locales.
    """

    # Matches printf-style and Objective-C/Swift placeholders, e.g. %s, %d, %i, %f, %x, %c, %@,
    # %1$s, %2$d, %ld, %lld, %-3.2f, % d, %#x. Components, in order:
    #   %                          literal percent sign
    #   (?:\d+\$)?                 optional positional index, e.g. 1$ in %1$s
    #   [+\-# 0]*                  optional flags (sign, alt form, padding, ...)
    #   \d*                        optional minimum width
    #   (?:\.\d+)?                 optional precision, e.g. .2 in %.2f
    #   [hlLzjt]*                  optional length modifiers, e.g. l in %ld
    #   [a-zA-Z@]                  conversion specifier (s, d, f, @, ...)
    # The leading `%%` alternative captures escaped percents so they aren't mistaken for placeholders.
    PLACEHOLDER_PATTERN = re.compile(
        r"%%|%(?:\d+\$)?[+\-# 0]*\d*(?:\.\d+)?[hlLzjt]*[a-zA-Z@]"
    )

    def is_matching(self, translations):
        plural_locales, plain_locales = self._split_plurals_and_plain_strings(translations)

        # Mixed: some locales declare the key as a plural and others as a plain string.
        if plural_locales and plain_locales:
            return True

        if plural_locales:
            for form in self._collect_plural_forms(plural_locales):
                form_translations = self._get_form_translations(plural_locales, form)
                if len({self._extract_placeholders(v) for v in form_translations.values()}) > 1:
                    return True
            return False
        else:
            return len({self._extract_placeholders(v) for v in plain_locales.values()}) > 1

    def get_explanation(self, translations):
        plural_locales, plain_locales = self._split_plurals_and_plain_strings(translations)

        if plural_locales and plain_locales:
            plural = sorted(plural_locales.keys())
            plain = sorted(plain_locales.keys())
            return (
                "inconsistent placeholders: key declared as a plural in "
                f"[{', '.join(plural)}] but as a plain string in [{', '.join(plain)}]"
            )

        if plural_locales:
            messages = []
            for form in sorted(self._collect_plural_forms(plural_locales)):
                form_translations = self._get_form_translations(plural_locales, form)
                if len({self._extract_placeholders(v) for v in form_translations.values()}) > 1:
                    messages.append(f"plural form '{form}': {self._format_groups(form_translations)}")
            return "inconsistent placeholders across locales for " + "; ".join(messages)
        else:
            return f"inconsistent placeholders across locales: {self._format_groups(plain_locales)}"

    @classmethod
    def _iter_placeholders(cls, value):
        for match in cls.PLACEHOLDER_PATTERN.finditer(value or ""):
            text = match.group(0)
            if text == "%%":
                continue
            yield text

    @classmethod
    def _extract_placeholders(cls, value):
        extracted_placeholders = sorted(cls._iter_placeholders(value))
        return tuple(extracted_placeholders)

    @staticmethod
    def _is_plural(value):
        return isinstance(value, dict)

    @classmethod
    def _split_plurals_and_plain_strings(cls, translations):
        """Split translations into (plural_locales, plain_locales) in a single pass."""
        plural_locales, plain_locales = {}, {}
        for locale, value in translations.items():
            target = plural_locales if cls._is_plural(value) else plain_locales
            target[locale] = value
        return plural_locales, plain_locales

    @staticmethod
    def _collect_plural_forms(plural_locales):
        forms = set()
        for value in plural_locales.values():
            forms.update(value.keys())
        return forms

    @staticmethod
    def _get_form_translations(plural_locales, form):
        return {locale: value[form] for locale, value in plural_locales.items() if form in value}

    @classmethod
    def _format_groups(cls, translations):
        groups = {}
        for locale, value in translations.items():
            groups.setdefault(cls._extract_placeholders(value), []).append(locale)
        parts = []
        for placeholders, locales in sorted(groups.items(), key=lambda item: sorted(item[1])):
            display = f"[{', '.join(placeholders)}]" if placeholders else "[]"
            parts.append(f"{display} in [{', '.join(sorted(locales))}]")
        return ", ".join(parts)


class ConsistentEndingRule(CrossLocaleRule):
    """Ensures all translations of a key either all end with a given suffix or none do."""

    def __init__(self, suffix, exception_ids=None):
        super().__init__(exception_ids)
        self.suffix = suffix

    def is_matching(self, translations):
        ends_with = {locale for locale, value in translations.items() if (value or "").endswith(self.suffix)}
        does_not = set(translations.keys()) - ends_with

        return len(ends_with) > 0 and len(does_not) > 0

    def get_explanation(self, translations):
        ends_with = sorted(locale for locale, value in translations.items() if (value or "").endswith(self.suffix))
        does_not = sorted(locale for locale, value in translations.items() if not (value or "").endswith(self.suffix))

        if len(ends_with) == 1:
            return f"inconsistent ending '{self.suffix}' only present in '{ends_with[0]}'"
        elif len(does_not) == 1:
            return f"inconsistent ending '{self.suffix}' only missing in '{does_not[0]}'"
        else:
            return f"inconsistent ending '{self.suffix}' present in [{', '.join(ends_with)}] and missing in [{', '.join(does_not)}]"
