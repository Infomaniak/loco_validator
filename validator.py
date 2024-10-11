from .rules import ExistenceRule, FrenchEmailRule, NoSpaceBeforeRule, SpaceBeforeRule, SpaceBeforeColonRule

global_rules = [
    ExistenceRule("'", exception_ids=[
        "allDeletedFilePattern",  # kDrive
        "allLastModifiedFilePattern",  # kDrive
    ]),
    ExistenceRule("..."),
    ExistenceRule(r" \n", "No space before a new line")
]

language_rules = {
    "en": [
        ExistenceRule("e-mail", "Remove the hyphen"),
        NoSpaceBeforeRule(":"),
        NoSpaceBeforeRule("?"),
        NoSpaceBeforeRule("!"),
    ],
    "fr": [
        FrenchEmailRule(exception_ids=[
            "faqUrl"  # kMail
        ]),
        # As two spellings are possible, we choose to use "évènement" arbitrarily
        ExistenceRule("événement", "Use 'évènement' instead"),
        SpaceBeforeColonRule(),
        SpaceBeforeRule("?"),
        SpaceBeforeRule("!"),
    ],
    "de": [
        ExistenceRule("ẞ"),
        ExistenceRule("gespräch", "Use 'Unterhaltung' instead"),
        ExistenceRule(  # Won't detect conjugated usages of Aufnehmen because it's a particle verb
            "aufnehmen",
            "'Aufnehmen' means to shoot/take a video/picture where as 'Speichern' means to save a file, to save settings, etc.",
            ["buttonTakePhotoOrVideo"]  # kDrive
        ),
        NoSpaceBeforeRule(":"),
        NoSpaceBeforeRule("?"),
        NoSpaceBeforeRule("!"),
    ],
    "it": [
        ExistenceRule("oscuro", "In the context of a dark and light theme, use 'scuro'"),
        ExistenceRule("claro", "In the context of a dark and light theme, use 'chiaro'"),
        ExistenceRule("luce", "In the context of a dark and light theme, use 'chiaro'"),
        ExistenceRule("thema", "In the context of a dark and light theme, use 'tema'"),
        NoSpaceBeforeRule(":"),
        NoSpaceBeforeRule("?"),
        NoSpaceBeforeRule("!"),
    ],
    "es": [
        NoSpaceBeforeRule(":"),
        NoSpaceBeforeRule("?"),
        NoSpaceBeforeRule("!"),
    ]
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
