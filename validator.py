from .rules import ExistenceRule, FrenchEmailRule

forbidden_sequences = ["'", "..."]
forbidden_rules = [ExistenceRule(sequence) for sequence in forbidden_sequences]
global_rules = [*forbidden_rules, ExistenceRule(r" \n", "No space before a new line")]

language_rules = {
    "en": [ExistenceRule("e-mail", "Remove the hyphen")],
    "fr": [
        FrenchEmailRule(),
        ExistenceRule("événement", "Use 'évènement' instead") # As two spellings are possible, we choose to use "évènement" arbitrarily
    ],
    "de": [
        ExistenceRule("ẞ"),
        ExistenceRule("gespräch", "Use 'Unterhaltung' instead"),
    ],
    "it": [
        ExistenceRule("oscuro", "In the context of a dark and light theme, use 'scuro'"),
        ExistenceRule("claro", "In the context of a dark and light theme, use 'chiaro'"),
        ExistenceRule("luce", "In the context of a dark and light theme, use 'chiaro'"),
        ExistenceRule("thema", "In the context of a dark and light theme, use 'tema'"),
    ],
    "es": []
}


def validate_string(language, name, value):
    error_count = 0

    for global_rule in global_rules:
        if global_rule.check(value, language, name):
            error_count += 1

    for language_rule in language_rules[language]:
        if language_rule.check(value, language, name):
            error_count += 1

    return error_count
