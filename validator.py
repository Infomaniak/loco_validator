from .rules import ExistenceRule, FrenchEmailRule, NoSpaceBeforeRule, SpaceBeforeRule, SpaceBeforeColonRule, EndsWithRule

global_rules = [
    ExistenceRule("'", "Use the real apostrophe '’' instead", exception_ids=[
        "allDeletedFilePattern",  # kDrive
        "allLastModifiedFilePattern",  # kDrive
    ]),
    ExistenceRule("...", "Use '…' so soft wrapping won't ever wrap text inbetween some of the dots"),
    ExistenceRule(r" \n", "No space before a new line"),
    ExistenceRule(r"\n ", "No space after a new line"),
    ExistenceRule(r"\\n", "No escaped new line. You probably meant to add a real new line"),
    EndsWithRule(r"\u0020", "No space at the end of a translation"),
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
            "faqUrl",  # kMail
            "kSuiteProQuotasAlertDescription",  # Mail (kSuite)
            "kSuiteProQuotasAlertFullDescription",  # Mail (kSuite)
            "myKSuiteDashboardFunctionalityMailAndDrive",  # Core (kSuite)
            "kSuiteStandardMailLabel",  # Core (kSuite pro)
            "kSuiteStandardMailLabelBold",  # Core (kSuite pro)
        ]),
        # As two spellings are possible, we choose to use "évènement" arbitrarily
        ExistenceRule("événement", "Use 'évènement' instead"),
        SpaceBeforeColonRule(exception_ids=[
            "allDeletedFilePattern",  # kDrive
            "allLastModifiedFilePattern",  # kDrive
        ]),
        SpaceBeforeRule("?"),
        SpaceBeforeRule("!"),
    ],
    "de": [
        ExistenceRule("ẞ", "Replace with 'ss' to better suit swiss-german"),
        ExistenceRule("gespräch", "Use 'Unterhaltung' instead"),
        ExistenceRule(  # Won't detect conjugated usages of Aufnehmen because it's a particle verb
            "aufnehmen",
            "'Aufnehmen' means to shoot/take a video/picture where as 'Speichern' means to save a file, to save settings, etc.",
            ["buttonTakePhotoOrVideo"]  # kDrive
        ),
        ExistenceRule(
            "Überweis",
            "Use 'Transfer' or derivations of it if possible. 'Überweisen' is for transfering money or hospital patients",
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
        ExistenceRule("basura", "The trash is usually translated as 'papelera' instead"),
        ExistenceRule("discapacitado", "To say that someting is deactivated use 'desactivado' instead"),
        ExistenceRule("hilo", "When talking about a conversation thread, use 'conversación' instead"),
    ],
    "da": [
        NoSpaceBeforeRule(":"),
        NoSpaceBeforeRule("?"),
        NoSpaceBeforeRule("!"),
    ],
    "el": [
        NoSpaceBeforeRule(":"),
        NoSpaceBeforeRule(";"),
        ExistenceRule("?", "In greek, the '?' is not used, instead they use a special unicode character U+037E ';'"),
        NoSpaceBeforeRule("!"),
    ],
    "fi": [
        NoSpaceBeforeRule(":"),
        NoSpaceBeforeRule("?"),
        NoSpaceBeforeRule("!"),
    ],
    "nb": [
        NoSpaceBeforeRule(":"),
        NoSpaceBeforeRule("?"),
        NoSpaceBeforeRule("!"),
    ],
    "nl": [
        NoSpaceBeforeRule(":"),
        NoSpaceBeforeRule("?"),
        NoSpaceBeforeRule("!"),
    ],
    "pl": [
        NoSpaceBeforeRule(":"),
        NoSpaceBeforeRule("?"),
        NoSpaceBeforeRule("!"),
    ],
    "pt": [
        NoSpaceBeforeRule(":"),
        NoSpaceBeforeRule("?"),
        NoSpaceBeforeRule("!"),
        ExistenceRule("excluir", "Don't use the verb excluir (pt-BR) when deleting something, use 'eliminar' (pt-PT) instead"),
        ExistenceRule("senha", "Don't use 'senha' (pt-BR) for password, use 'palavra-passe' (pt-PT) instead"),
        ExistenceRule("usuário", "Don't use 'usuário' (pt-BR) for a user, use 'utilizador' (pt-PT) instead"),
        ExistenceRule("celular", "Don't use 'celular' (pt-BR) for a mobile phone, use 'telemóvel' (pt-PT) instead"),
    ],
    "sv": [
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

    for language_rule in language_rules.get(language, []):
        if language_rule.check(value, language, name):
            error_count += 1

    return error_count
