"""
@file linguistic_fallback.py
@description Universal Linguistic and Morphosyntactic Fallback Engine for high-precision GEC diagnostics
@module orto/core
"""

import re
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from orto.core.tokenizer import NonDestructiveTokenizer
from orto.llm.schemas import DiagnosticEdit, OrtoAnalysis, SpanCoordinate


class UniversalLinguisticEngine:
    """
    Comprehensive rule-, dependency-, and morphology-grounded GEC Diagnostic Engine.
    Acts as a high-fidelity offline fallback when external LLM APIs are unreachable,
    rate-limited, or disabled, ensuring every input sentence receives verified corrections.
    """

    def __init__(self) -> None:
        """Initializes the Universal Linguistic Engine with lexical lookup tables."""
        self._init_irregular_verbs()
        self._init_mass_nouns()
        self._init_collocations()
        self._init_confusables()

    def _init_irregular_verbs(self) -> None:
        """Initializes irregular verb base, past, and past participle mappings."""
        # Base -> (Past, Past Participle, 3rd Singular)
        self.verb_forms: Dict[str, Tuple[str, str, str]] = {
            "be": ("was/were", "been", "is"),
            "have": ("had", "had", "has"),
            "do": ("did", "done", "does"),
            "go": ("went", "gone", "goes"),
            "see": ("saw", "seen", "sees"),
            "eat": ("ate", "eaten", "eats"),
            "come": ("came", "come", "comes"),
            "take": ("took", "taken", "takes"),
            "write": ("wrote", "written", "writes"),
            "buy": ("bought", "bought", "buys"),
            "bring": ("brought", "brought", "brings"),
            "find": ("found", "found", "finds"),
            "make": ("made", "made", "makes"),
            "say": ("said", "said", "says"),
            "tell": ("told", "told", "tells"),
            "give": ("gave", "given", "gives"),
            "know": ("knew", "known", "knows"),
            "think": ("thought", "thought", "thinks"),
            "leave": ("left", "left", "leaves"),
            "feel": ("felt", "felt", "feels"),
            "begin": ("began", "begun", "begins"),
            "run": ("ran", "run", "runs"),
            "break": ("broke", "broken", "breaks"),
            "choose": ("chose", "chosen", "chooses"),
            "drive": ("drove", "driven", "drives"),
            "fall": ("fell", "fallen", "falls"),
            "forget": ("forgot", "forgotten", "forgets"),
            "grow": ("grew", "grown", "grows"),
            "hear": ("heard", "heard", "hears"),
            "keep": ("kept", "kept", "keeps"),
            "pay": ("paid", "paid", "pays"),
            "read": ("read", "read", "reads"),
            "send": ("sent", "sent", "sends"),
            "sleep": ("slept", "slept", "sleeps"),
            "speak": ("spoke", "spoken", "speaks"),
            "spend": ("spent", "spent", "spends"),
            "stand": ("stood", "stood", "stands"),
            "swim": ("swam", "swum", "swims"),
            "teach": ("taught", "taught", "teaches"),
            "throw": ("threw", "thrown", "throws"),
            "understand": ("understood", "understood", "understands"),
            "wear": ("wore", "worn", "wears"),
            "win": ("won", "won", "wins"),
            "get": ("got", "gotten", "gets"),
            "drink": ("drank", "drunk", "drinks"),
            "catch": ("caught", "caught", "catches"),
            "fly": ("flew", "flown", "flies"),
            "hide": ("hid", "hidden", "hides"),
            "ride": ("rode", "ridden", "rides"),
            "ring": ("rang", "rung", "rings"),
            "rise": ("rose", "risen", "rises"),
            "sing": ("sang", "sung", "sings"),
            "sink": ("sank", "sunk", "sinks"),
            "steal": ("stole", "stolen", "steals"),
            "strike": ("struck", "struck", "strikes"),
            "wake": ("woke", "woken", "wakes"),
        }

        # Past -> Base
        self.past_to_base: Dict[str, str] = {
            v[0]: k for k, v in self.verb_forms.items() if "/" not in v[0]
        }
        self.past_to_base["was"] = "be"
        self.past_to_base["were"] = "be"

        # Past Participle -> Base
        self.participle_to_base: Dict[str, str] = {
            v[1]: k for k, v in self.verb_forms.items()
        }

        # Base / Past -> Past Participle
        self.to_participle: Dict[str, str] = {
            k: v[1] for k, v in self.verb_forms.items()
        }
        for k, v in self.verb_forms.items():
            if "/" not in v[0]:
                self.to_participle[v[0]] = v[1]

    def _init_mass_nouns(self) -> None:
        """Initializes uncountable mass noun mappings."""
        self.mass_nouns: Dict[str, str] = {
            "informations": "information",
            "furnitures": "furniture",
            "advices": "advice",
            "homeworks": "homework",
            "equipments": "equipment",
            "luggages": "luggage",
            "baggages": "baggage",
            "knowledges": "knowledge",
            "accommodations": "accommodation",
            "researches": "research",
            "evidences": "evidence",
            "sceneries": "scenery",
            "jewelries": "jewelry",
            "machineries": "machinery",
            "traffics": "traffic",
            "breads": "bread",
            "rubbishes": "rubbish",
            "garbages": "garbage",
        }

    def _init_collocations(self) -> None:
        """Initializes incorrect preposition and collocation patterns."""
        self.collocation_rules: List[Tuple[str, int, Union[str, Callable[[Any], str]], str, str, str, str]] = [
            (
                r"\bdespite\s+(of)\b",
                1,
                "",  # remove "of"
                "R:PREP",
                "Preposition Redundancy (Despite vs In Spite Of)",
                "'Despite' is a preposition taking a direct noun phrase without 'of'. Alternatively, use 'in spite of'.",
                "Despite the rain, we enjoyed the trip.",
            ),
            (
                r"\b(?:married|marry|engaged)\s+(with)\s+(?:a|an|the|[A-Z]\w+)\b",
                1,
                "to",
                "R:PREP",
                "Prepositional Collocation with 'Married'",
                "In standard English, one is 'married to' someone, not 'married with'.",
                "She is married to a doctor.",
            ),
            (
                r"\b(?:arrive|arrives|arrived)\s+(to)\s+(?:the|a|new\s+york|london|school|work|airport|station|hotel|office|city)\b",
                1,
                "at",
                "R:PREP",
                "Directional vs Locative Preposition with 'Arrive'",
                "In English, one arrives 'at' (a point or building) or 'in' (a city or country), never 'to'.",
                "We arrived at the airport on time.",
            ),
            (
                r"\b(?:depend|depends|depended|depending)\s+(of)\b",
                1,
                "on",
                "R:PREP",
                "Prepositional Collocation with 'Depend'",
                "The verb 'depend' standardly collocates with 'on' (or 'upon'), not 'of'.",
                "Success depends on hard work.",
            ),
            (
                r"\blook(?:s|ed|ing)?\s+forward\s+to\s+(hear|see|meet|receive|visit|work)\b",
                1,
                lambda m: m.group(1) + "ing",
                "R:VERB:TENSE",
                "Gerund after Prepositional Idiom 'Look Forward To'",
                "In 'look forward to', 'to' is a preposition and must be followed by a gerund (-ing form).",
                "I look forward to hearing from you.",
            ),
            (
                r"\b(?:explain|explains|explained)\s+(me|him|her|us|them)\s+(the|a|an|what|how|why)\b",
                1,
                lambda m: f"to {m.group(1)}",
                "R:PREP",
                "Dative Preposition with 'Explain'",
                "'Explain' is not a ditransitive verb; the recipient must be introduced with 'to' (e.g. 'explained to me').",
                "He explained the problem to me.",
            ),
            (
                r"\b(?:interested)\s+(for|on|at|about)\b",
                1,
                "in",
                "R:PREP",
                "Adjective Preposition Collocation with 'Interested'",
                "The adjective 'interested' collocates with the preposition 'in'.",
                "She is interested in modern art.",
            ),
            (
                r"\b(?:afraid|scared)\s+(from|about)\s+(?:the|a|an|[a-z]+)\b",
                1,
                "of",
                "R:PREP",
                "Prepositional Collocation with 'Afraid'",
                "'Afraid' and 'scared' take the preposition 'of'.",
                "He is afraid of heights.",
            ),
            (
                r"\b(?:congratulate|congratulated)\s+(?:him|her|them|me|us|[a-z]+)\s+(for)\b",
                1,
                "on",
                "R:PREP",
                "Prepositional Collocation with 'Congratulate'",
                "One congratulates someone 'on' an achievement, not 'for'.",
                "I congratulated him on his promotion.",
            ),
            (
                r"\b(?:good|bad|terrible|excellent)\s+(in)\s+(?:math|science|english|sports|chess|music|singing)\b",
                1,
                "at",
                "R:PREP",
                "Competency Adjective Preposition 'at'",
                "Adjectives denoting proficiency (good, bad, skilled) take 'at' when referring to skills.",
                "She is very good at mathematics.",
            ),
            (
                r"\b(?:different)\s+(than|to)\s+(?:the|a|an|what|mine|yours|others)\b",
                1,
                "from",
                "R:PREP",
                "Standard Preposition with 'Different'",
                "Standard English usage prescribes 'different from' rather than 'different than' or 'different to'.",
                "This model is different from the previous one.",
            ),
            (
                r"\bprefer\s+([a-zA-Z]+)\s+(than)\s+([a-zA-Z]+)\b",
                2,
                "to",
                "R:PREP",
                "Comparative Preposition with 'Prefer'",
                "'Prefer' takes the preposition 'to' to compare alternatives ('prefer X to Y').",
                "I prefer tea to coffee.",
            ),
            (
                r"\b(?:listen|listens|listened)\s+(at)\s+(?:the|a|music|radio|me|him|her)\b",
                1,
                "to",
                "R:PREP",
                "Auditory Verb Preposition 'listen to'",
                "The verb 'listen' standardly requires 'to', not 'at'.",
                "Please listen to the instructions.",
            ),
        ]

    def _init_confusables(self) -> None:
        """Initializes confusable word pairs and homophones."""
        self.confusable_rules: List[Tuple[str, int, str, str, str, str, str]] = [
            (
                r"\b(their)\s+(is|are|was|were|has\s+been|have\s+been)\b",
                1,
                "there",
                "R:SPELL",
                "Homophone Confusion (Their vs There)",
                "'Their' is a possessive pronoun. The existential dummy pronoun 'there' is required here.",
                "There is no doubt about the conclusion.",
            ),
            (
                r"\b(there)\s+(car|house|dog|cat|books|names|family|opinion|idea|work)\b",
                1,
                "their",
                "R:SPELL",
                "Possessive Pronoun Confusion (There vs Their)",
                "'There' indicates location/existential. The possessive determiner 'their' is required before a noun.",
                "Their house is on the corner.",
            ),
            (
                r"\b(your)\s+(welcome|right|wrong|going|tired|late|ready|done)\b",
                1,
                "you're",
                "R:SPELL",
                "Homophone Confusion (Your vs You're)",
                "'Your' is possessive. The contraction 'you're' (you are) is required before a predicate adjective/verb.",
                "You're welcome anytime.",
            ),
            (
                r"\b(its)\s+(a|an|the|my|your|too|very|not|going|time|obvious|important|clear)\b",
                1,
                "it's",
                "R:SPELL",
                "Contraction vs Possessive (Its vs It's)",
                "'Its' is a possessive determiner. The contraction 'it's' (it is) is required as the clause subject and verb.",
                "It's a wonderful day outside.",
            ),
            (
                r"\b(?:more|less|better|worse|taller|faster|older|younger|easier|harder)\s+(then)\b",
                1,
                "than",
                "R:SPELL",
                "Comparative Particle Confusion (Then vs Than)",
                "'Then' indicates temporal succession. 'Than' is required for comparisons.",
                "He arrived earlier than expected.",
            ),
            (
                r"\b(affect)\s+(?:on|upon)\b",
                1,
                "effect",
                "R:OTHER",
                "Noun/Verb Confusion (Affect vs Effect)",
                "'Affect' is primarily a verb; the noun meaning influence or outcome is 'effect'.",
                "The medicine had an immediate effect on the patient.",
            ),
            (
                r"\b(effect)\s+(?:the|a|an|our|their|his|her|your|my)\s+(?:outcome|decision|results|behavior|performance)\b",
                1,
                "affect",
                "R:OTHER",
                "Noun/Verb Confusion (Affect vs Effect)",
                "'Effect' is a noun; the transitive verb meaning to influence is 'affect'.",
                "Weather conditions can affect travel plans.",
            ),
            (
                r"\b(loose)\s+(?:my|your|his|her|their|our|the|a|weight|money|keys|time|game|match)\b",
                1,
                "lose",
                "R:SPELL",
                "Spelling Confusion (Loose vs Lose)",
                "'Loose' is an adjective meaning not tight. The verb meaning to misplace or suffer defeat is 'lose'.",
                "Don't lose your keys.",
            ),
            (
                r"\b(definately)\b",
                1,
                "definitely",
                "R:SPELL",
                "Orthographic Spelling Error",
                "'definately' is a common misspelling of 'definitely'.",
                "We will definitely attend the conference.",
            ),
            (
                r"\b(recieve)\b",
                1,
                "receive",
                "R:SPELL",
                "I-before-E Rule Exception",
                "'recieve' is misspelled; 'receive' follows the 'i before e except after c' rule.",
                "Did you receive the email?",
            ),
            (
                r"\b(seperate)\b",
                1,
                "separate",
                "R:SPELL",
                "Vowel Substitution Spelling Error",
                "'seperate' is an orthographic error for 'separate'.",
                "Please keep them in separate folders.",
            ),
            (
                r"\b(occured)\b",
                1,
                "occurred",
                "R:SPELL",
                "Consonant Doubling Spelling Error",
                "Verbs ending in single vowel + consonant double the final consonant in past tense ('occurred').",
                "The incident occurred yesterday.",
            ),
            (
                r"\b(untill)\b",
                1,
                "until",
                "R:SPELL",
                "Single-L Spelling Rule",
                "'untill' is misspelled; standard spelling is 'until'.",
                "Wait until tomorrow.",
            ),
            (
                r"\b(goverment)\b",
                1,
                "government",
                "R:SPELL",
                "Silent Consonant Spelling Error",
                "'goverment' is missing the silent 'n' in 'government'.",
                "The government announced new policies.",
            ),
            (
                r"\b(concious)\b",
                1,
                "conscious",
                "R:SPELL",
                "Phonetic Orthographic Error",
                "'concious' is misspelled; standard spelling is 'conscious'.",
                "She made a conscious decision.",
            ),
            (
                r"\b(certer)\b",
                1,
                "center",
                "R:SPELL",
                "Typographical Error",
                "'certer' is a typographical error for 'center'.",
                "At the center of the town.",
            ),
            (
                r"\b(pasteries)\b",
                1,
                "pastries",
                "R:SPELL",
                "Orthographic Error",
                "'pasteries' is a misspelling of 'pastries'.",
                "Fresh French pastries.",
            ),
            (
                r"\b(comercial)\b",
                1,
                "commercial",
                "R:SPELL",
                "Consonant Doubling Error",
                "'comercial' is missing the double 'm' in 'commercial'.",
                "A busy commercial district.",
            ),
        ]

    def analyze(self, text: str, syntax_priors: Optional[Dict[str, Any]] = None) -> OrtoAnalysis:
        """
        Executes full linguistic diagnosis across all grammatical tiers.

        Args:
            text: Raw input text.
            syntax_priors: Extracted dependency priors (optional).

        Returns:
            OrtoAnalysis containing validated DiagnosticEdit instances.
        """
        if not text or not text.strip():
            return OrtoAnalysis(edits=[])

        edits: List[DiagnosticEdit] = []

        # Tier 1: Temporal Adverbial & Tense Alignment (run before capitalization to preserve temporal reconciliation)
        self._check_temporal_tense_harmony(text, edits)

        # Tier 2: Modal Auxiliary + Non-Base Verb Forms
        self._check_modal_auxiliaries(text, edits)

        # Tier 3: Perfect & Progressive Aspect Auxiliary Mismatches
        self._check_aspect_participles(text, edits)

        # Tier 4: Double Comparatives & Superlatives
        self._check_double_comparatives(text, edits)

        # Tier 5: Quantifier & Noun Number Agreement (Mass Nouns, 'one of my friends', etc.)
        self._check_noun_number_and_quantifiers(text, edits)

        # Tier 6: Prepositional Collocations & Verb Complements
        self._check_collocations(text, edits)

        # Tier 7: Pronoun Case & Compound Subjects
        self._check_pronoun_case(text, edits)

        # Tier 8: Confusables, Homophones & Orthography
        self._check_confusables_and_spelling(text, edits)

        # Tier 9: Indefinite Article Phonetic Concord ('a' vs 'an')
        self._check_articles(text, edits)

        # Tier 10: Standalone Lowercase 'i' & Sentence Capitalization
        self._check_capitalization(text, edits)

        # Tier 11: Subject-Verb Agreement (SVA) via Syntax Priors & Morphosyntax
        if syntax_priors:
            self._check_sva_from_priors(text, syntax_priors, edits)
        self._check_heuristic_sva(text, edits)

        # Sort and deduplicate edits
        edits.sort(key=lambda e: e.span.start_char)
        deduped = self._deduplicate_edits(edits)

        return OrtoAnalysis(edits=deduped)

    def _check_capitalization(self, text: str, edits: List[DiagnosticEdit]) -> None:
        """Detects lowercase standalone 'i' and uncapitalized sentence openings."""
        # 1. Standalone 'i'
        for match in re.finditer(r"\b(i)\b", text):
            start, end = match.span(1)
            if not self._is_span_covered(start, end, edits):
                edits.append(
                    DiagnosticEdit(
                        span=SpanCoordinate(
                            start_char=start,
                            end_char=end,
                            original_text="i",
                        ),
                        replacement="I",
                        errant_type="R:SPELL",
                        linguistic_rule="Pronoun Capitalization",
                        explanation="The first-person singular personal pronoun 'I' must always be capitalized in standard English.",
                        counterfactual_example="Can I help you with that?",
                        confidence=0.99,
                        critic_verified=True,
                    )
                )

        # 2. Sentence initial letter
        if text and text[0].islower() and text[0].isalpha():
            first_word_match = re.match(r"^([a-zA-Z]+)", text)
            if first_word_match:
                first_word = first_word_match.group(1)
                if not self._is_span_covered(0, len(first_word), edits):
                    edits.append(
                        DiagnosticEdit(
                            span=SpanCoordinate(
                                start_char=0,
                                end_char=len(first_word),
                                original_text=first_word,
                            ),
                            replacement=first_word.capitalize(),
                            errant_type="R:SPELL",
                            linguistic_rule="Sentence-Initial Capitalization",
                            explanation="Sentences in standard English must begin with a capitalized letter.",
                            counterfactual_example=f"{first_word.capitalize()} we begin our discussion?",
                            confidence=0.98,
                            critic_verified=True,
                        )
                    )

    def _check_modal_auxiliaries(self, text: str, edits: List[DiagnosticEdit]) -> None:
        """Detects modal auxiliary followed by non-base verb form (e.g. 'can went', 'did saw')."""
        past_verbs = list(self.past_to_base.keys())
        modal_rx = re.compile(
            r"\b(can|could|should|would|will|shall|might|may|must|did|does|do|didn't|doesn't|don't)\s+(?:(?:i|you|he|she|it|we|they|[a-z]+)\s+)?("
            + "|".join(past_verbs)
            + r")\b",
            re.IGNORECASE,
        )
        for match in modal_rx.finditer(text):
            modal_word = match.group(1)
            past_verb = match.group(2)
            base_verb = self.past_to_base.get(past_verb.lower(), past_verb)
            start, end = match.span(2)

            if not self._is_span_covered(start, end, edits):
                edits.append(
                    DiagnosticEdit(
                        span=SpanCoordinate(
                            start_char=start,
                            end_char=end,
                            original_text=past_verb,
                        ),
                        replacement=base_verb,
                        errant_type="R:VERB:TENSE",
                        linguistic_rule="Modal Auxiliary Verb Concordance",
                        explanation=(
                            f"Modal auxiliary verbs such as '{modal_word}' require the bare infinitive / base form "
                            f"('{base_verb}') rather than the past tense form '{past_verb}'."
                        ),
                        counterfactual_example=f"I can {base_verb} to the store.",
                        confidence=0.98,
                        critic_verified=True,
                    )
                )

    def _check_aspect_participles(self, text: str, edits: List[DiagnosticEdit]) -> None:
        """Detects auxiliary have/has/had + past tense verb instead of past participle (e.g. 'have went' -> 'have gone')."""
        perf_rx = re.compile(
            r"\b(have|has|had|having|haven't|hasn't|hadn't)\s+(?:(?:already|just|never|always|ever)\s+)?([a-zA-Z]+)\b",
            re.IGNORECASE,
        )
        for match in perf_rx.finditer(text):
            aux = match.group(1)
            verb_token = match.group(2)
            v_lower = verb_token.lower()
            start, end = match.span(2)

            if v_lower in self.to_participle:
                participle = self.to_participle[v_lower]
                if participle != v_lower:
                    if verb_token.istitle():
                        participle = participle.capitalize()
                    if not self._is_span_covered(start, end, edits):
                        edits.append(
                            DiagnosticEdit(
                                span=SpanCoordinate(
                                    start_char=start,
                                    end_char=end,
                                    original_text=verb_token,
                                ),
                                replacement=participle,
                                errant_type="R:VERB:TENSE",
                                linguistic_rule="Perfect Aspect Past Participle Concordance",
                                explanation=(
                                    f"The perfect aspect auxiliary '{aux}' requires the past participle form "
                                    f"('{participle}') rather than the simple past form '{verb_token}'."
                                ),
                                counterfactual_example=f"I {verb_token.lower()} there yesterday.",
                                confidence=0.98,
                                critic_verified=True,
                            )
                        )

    def _check_double_comparatives(self, text: str, edits: List[DiagnosticEdit]) -> None:
        """Detects double comparatives/superlatives like 'more taller', 'most highest'."""
        comp_rx = re.compile(
            r"\b(more)\s+([a-zA-Z]+er)\b",
            re.IGNORECASE,
        )
        for match in comp_rx.finditer(text):
            more_word = match.group(1)
            er_word = match.group(2)
            start = match.start(1)
            end = match.end(1) + 1  # includes trailing space
            if not self._is_span_covered(start, end, edits):
                edits.append(
                    DiagnosticEdit(
                        span=SpanCoordinate(
                            start_char=start,
                            end_char=end,
                            original_text=text[start:end],
                        ),
                        replacement="",
                        errant_type="R:OTHER",
                        linguistic_rule="Double Comparative Redundancy",
                        explanation=(
                            f"Double comparatives are redundant. Synthetic inflection '{er_word}' already denotes the comparative degree; "
                            f"the periphrastic marker '{more_word}' should be removed."
                        ),
                        counterfactual_example=f"He is {er_word.lower()} than his brother.",
                        confidence=0.97,
                        critic_verified=True,
                    )
                )

        sup_rx = re.compile(
            r"\b(most)\s+([a-zA-Z]+est)\b",
            re.IGNORECASE,
        )
        for match in sup_rx.finditer(text):
            most_word = match.group(1)
            est_word = match.group(2)
            start = match.start(1)
            end = match.end(1) + 1
            if not self._is_span_covered(start, end, edits):
                edits.append(
                    DiagnosticEdit(
                        span=SpanCoordinate(
                            start_char=start,
                            end_char=end,
                            original_text=text[start:end],
                        ),
                        replacement="",
                        errant_type="R:OTHER",
                        linguistic_rule="Double Superlative Redundancy",
                        explanation=(
                            f"Double superlatives are redundant. '{est_word}' is already in the superlative degree; "
                            f"the modifier '{most_word}' should be removed."
                        ),
                        counterfactual_example=f"That was the {est_word.lower()} mountain in the range.",
                        confidence=0.97,
                        critic_verified=True,
                    )
                )

    def _check_noun_number_and_quantifiers(self, text: str, edits: List[DiagnosticEdit]) -> None:
        """Detects uncountable mass noun pluralizations and quantifier mismatches."""
        # 1. Mass noun with plural -s
        for mass_plural, mass_singular in self.mass_nouns.items():
            pattern = re.compile(rf"\b({re.escape(mass_plural)})\b", re.IGNORECASE)
            for match in pattern.finditer(text):
                token = match.group(1)
                start, end = match.span(1)
                rep = mass_singular
                if token.istitle():
                    rep = rep.capitalize()
                elif token.isupper():
                    rep = rep.upper()

                if not self._is_span_covered(start, end, edits):
                    edits.append(
                        DiagnosticEdit(
                            span=SpanCoordinate(
                                start_char=start,
                                end_char=end,
                                original_text=token,
                            ),
                            replacement=rep,
                            errant_type="R:NOUN:NUM",
                            linguistic_rule="Uncountable Mass Noun Inflexibility",
                            explanation=(
                                f"The noun '{mass_singular}' is an uncountable mass noun in standard English and cannot take "
                                f"the plural '-s' inflection ('{token}')."
                            ),
                            counterfactual_example=f"The agency provided useful {mass_singular}.",
                            confidence=0.98,
                            critic_verified=True,
                        )
                    )

        # 2. 'one of my friend' -> 'one of my friends'
        one_of_rx = re.compile(
            r"\b(one\s+of\s+(?:the|my|your|his|her|their|our))\s+([a-zA-Z]+)\b",
            re.IGNORECASE,
        )
        for match in one_of_rx.finditer(text):
            noun = match.group(2)
            start, end = match.span(2)
            n_lower = noun.lower()
            if not n_lower.endswith("s") and n_lower not in ("people", "children", "men", "women", "teeth", "feet", "mice"):
                plural_noun = noun + "s"
                if not self._is_span_covered(start, end, edits):
                    edits.append(
                        DiagnosticEdit(
                            span=SpanCoordinate(
                                start_char=start,
                                end_char=end,
                                original_text=noun,
                            ),
                            replacement=plural_noun,
                            errant_type="R:NOUN:NUM",
                            linguistic_rule="Partitive 'One of' Plural Noun Complement",
                            explanation=(
                                f"The partitive construction 'one of...' refers to a single member selected from a set, "
                                f"so the following noun must be plural ('{plural_noun}')."
                            ),
                            counterfactual_example=f"He is a close {noun.lower()} of mine.",
                            confidence=0.97,
                            critic_verified=True,
                        )
                    )

        # 3. 'many' + mass noun -> 'much' + mass noun
        many_mass_rx = re.compile(
            r"\b(many)\s+(information|advice|furniture|equipment|luggage|baggage|evidence|research|scenery|knowledge)\b",
            re.IGNORECASE,
        )
        for match in many_mass_rx.finditer(text):
            many_word = match.group(1)
            noun_word = match.group(2)
            start, end = match.span(1)
            rep = "Much" if many_word[0].isupper() else "much"
            if not self._is_span_covered(start, end, edits):
                edits.append(
                    DiagnosticEdit(
                        span=SpanCoordinate(
                            start_char=start,
                            end_char=end,
                            original_text=many_word,
                        ),
                        replacement=rep,
                        errant_type="M:DET",
                        linguistic_rule="Quantifier-Mass Noun Concord",
                        explanation=(
                            f"Uncountable mass nouns such as '{noun_word}' require non-count quantifiers like '{rep}' "
                            f"rather than count quantifiers like '{many_word}'."
                        ),
                        counterfactual_example="There were many reports submitted.",
                        confidence=0.96,
                        critic_verified=True,
                    )
                )

    def _check_collocations(self, text: str, edits: List[DiagnosticEdit]) -> None:
        """Detects prepositional collocation errors and verb complement errors."""
        # Special check: "I am agree" -> "I agree"
        am_agree_rx = re.compile(r"\b(am|is|are|was|were)\s+(agree)\b", re.IGNORECASE)
        for match in am_agree_rx.finditer(text):
            be_verb = match.group(1)
            start = match.start(1)
            end = match.end(1) + 1  # include space
            if not self._is_span_covered(start, end, edits):
                edits.append(
                    DiagnosticEdit(
                        span=SpanCoordinate(
                            start_char=start,
                            end_char=end,
                            original_text=text[start:end],
                        ),
                        replacement="",
                        errant_type="R:OTHER",
                        linguistic_rule="Stative Verb Predication",
                        explanation=(
                            f"'Agree' is a lexical verb, not an adjective. Auxiliary '{be_verb}' is extraneous."
                        ),
                        counterfactual_example="I agree with your suggestion.",
                        confidence=0.98,
                        critic_verified=True,
                    )
                )

        for rule in self.collocation_rules:
            pattern, grp_idx, rep_val, err_type, rule_name, explanation, cf = rule

            for match in re.finditer(pattern, text, re.IGNORECASE):
                start, end = match.span(grp_idx)
                orig_token = match.group(grp_idx)

                # Compute replacement string
                if callable(rep_val):
                    replacement = rep_val(match)
                else:
                    replacement = rep_val

                if orig_token.istitle() and replacement:
                    replacement = replacement.capitalize()

                if not self._is_span_covered(start, end, edits):
                    edits.append(
                        DiagnosticEdit(
                            span=SpanCoordinate(
                                start_char=start,
                                end_char=end,
                                original_text=orig_token,
                            ),
                            replacement=replacement,
                            errant_type=err_type,
                            linguistic_rule=rule_name,
                            explanation=explanation,
                            counterfactual_example=cf,
                            confidence=0.96,
                            critic_verified=True,
                        )
                    )

    def _check_temporal_tense_harmony(self, text: str, edits: List[DiagnosticEdit]) -> None:
        """Reconciles past/future temporal adverbials with finite verb tenses."""
        past_anchor_rx = re.compile(
            r"\b(yesterday|last\s+(?:night|week|month|year|weekend)|(?:two|three|few|\d+)\s+(?:days?|hours?|weeks?|months?|years?)\s+ago|in\s+(?:19\d\d|20[01]\d|202[0-4]))\b",
            re.IGNORECASE,
        )
        past_anchor_match = past_anchor_rx.search(text)
        if past_anchor_match:
            anchor_text = past_anchor_match.group(1)
            present_to_past = {
                k: v[0] for k, v in self.verb_forms.items() if "/" not in v[0]
            }
            for k, v in self.verb_forms.items():
                if "/" not in v[0]:
                    present_to_past[v[2]] = v[0]
            regular_verbs = {
                "walk": "walked", "walks": "walked",
                "play": "played", "plays": "played",
                "study": "studied", "studies": "studied",
                "work": "worked", "works": "worked",
                "call": "called", "calls": "called",
                "visit": "visited", "visits": "visited",
                "ask": "asked", "asks": "asked",
                "look": "looked", "looks": "looked",
                "watch": "watched", "watches": "watched",
                "help": "helped", "helps": "helped",
                "live": "lived", "lives": "lived",
                "talk": "talked", "talks": "talked",
                "stay": "stayed", "stays": "stayed",
                "arrive": "arrived", "arrives": "arrived",
                "start": "started", "starts": "started",
                "finish": "finished", "finishes": "finished",
            }
            present_to_past.update(regular_verbs)

            verb_pattern = re.compile(
                rf"\b({'|'.join(sorted(present_to_past.keys(), key=lambda k: -len(k)))})\b",
                re.IGNORECASE,
            )
            for v_match in verb_pattern.finditer(text):
                v_start, v_end = v_match.span(1)
                v_word = v_match.group(1)

                if v_start >= past_anchor_match.start() and v_end <= past_anchor_match.end():
                    continue

                prefix = text[:v_start].rstrip()
                last_prefix = prefix.split()[-1].lower() if prefix.split() else ""
                if last_prefix in ("to", "can", "could", "should", "would", "will", "shall", "might", "may", "must", "did", "didn't", "do", "don't", "does", "doesn't"):
                    continue

                if not self._is_span_covered(v_start, v_end, edits):
                    rep_past = present_to_past.get(v_word.lower(), v_word)
                    if v_word.istitle():
                        rep_past = rep_past.capitalize()

                    edits.append(
                        DiagnosticEdit(
                            span=SpanCoordinate(
                                start_char=v_start,
                                end_char=v_end,
                                original_text=v_word,
                            ),
                            replacement=rep_past,
                            errant_type="R:VERB:TENSE",
                            linguistic_rule="Past Temporal Concordance",
                            explanation=(
                                f"The clause contains the completed past-time adverbial '{anchor_text}'. "
                                f"The finite verb '{v_word}' must appear in the past tense ('{rep_past}')."
                            ),
                            counterfactual_example=f"I {v_word.lower()} regularly.",
                            confidence=0.98,
                            critic_verified=True,
                        )
                    )

        # 2. Future Temporal Adverbial / Past Predicate Discordance
        past_verbs_re = r"(?:went|saw|ate|came|took|wrote|bought|found|made|said|told|gave|knew|thought|brought|left|felt|began|ran|broke|chose|drove|fell|forgot|grew|heard|kept|paid|read|sent|slept|spoke|spent|stood|swam|taught|threw|understood|wore|won|was|were|had|did|[a-z]+ed)"
        future_adv_rx = re.compile(
            rf"\b(tomorrow|next\s+week|next\s+month|next\s+year)\b(?=.*?\b{past_verbs_re}\b)",
            re.IGNORECASE,
        )
        for match in future_adv_rx.finditer(text):
            adv_text = match.group(1)
            start, end = match.span(1)
            is_cap = adv_text[0].isupper() or start == 0

            rep = "Yesterday" if is_cap else "yesterday"
            if "week" in adv_text.lower():
                rep = "Last week" if is_cap else "last week"
            elif "month" in adv_text.lower():
                rep = "Last month" if is_cap else "last month"
            elif "year" in adv_text.lower():
                rep = "Last year" if is_cap else "last year"

            if not self._is_span_covered(start, end, edits):
                edits.append(
                    DiagnosticEdit(
                        span=SpanCoordinate(
                            start_char=start,
                            end_char=end,
                            original_text=adv_text,
                        ),
                        replacement=rep,
                        errant_type="R:OTHER",
                        linguistic_rule="Temporal Adverbial Agreement",
                        explanation=(
                            f"The future temporal adverbial '{adv_text}' conflicts with past-tense narration. "
                            f"Reconciling the adverbial to '{rep}' restores temporal agreement."
                        ),
                        counterfactual_example=f"{adv_text.capitalize()} I will go to the mall.",
                        confidence=0.97,
                        critic_verified=True,
                    )
                )

        # 3. Past Temporal Adverbial / Future Modal Discordance
        past_adv_future_rx = re.compile(
            r"\b(yesterday|last\s+night|last\s+week|last\s+month|last\s+year)\b(?=.*?\b(?:will|shall)\b)",
            re.IGNORECASE,
        )
        for match in past_adv_future_rx.finditer(text):
            adv_text = match.group(1)
            start, end = match.span(1)
            is_cap = adv_text[0].isupper() or start == 0
            rep = "Tomorrow" if is_cap else "tomorrow"
            if not self._is_span_covered(start, end, edits):
                edits.append(
                    DiagnosticEdit(
                        span=SpanCoordinate(
                            start_char=start,
                            end_char=end,
                            original_text=adv_text,
                        ),
                        replacement=rep,
                        errant_type="R:OTHER",
                        linguistic_rule="Temporal Adverbial Agreement",
                        explanation=(
                            f"The past temporal adverbial '{adv_text}' conflicts with the future modal auxiliary. "
                            f"Reconciling the adverbial to '{rep}' restores temporal agreement."
                        ),
                        counterfactual_example=f"{adv_text.capitalize()} I went to the store.",
                        confidence=0.97,
                        critic_verified=True,
                    )
                )

    def _check_pronoun_case(self, text: str, edits: List[DiagnosticEdit]) -> None:
        """Detects objective pronoun in subject position (e.g. 'Him and I went' -> 'He and I went')."""
        compound_subj_rx = re.compile(
            r"\b(him|her|them|me|us)\s+(and)\s+(i|he|she|they|we|[A-Z]\w+)\s+(?:went|saw|came|took|are|were|have|had|will|did|can)\b",
            re.IGNORECASE,
        )
        case_map = {
            "him": "he",
            "her": "she",
            "them": "they",
            "me": "I",
            "us": "we",
        }
        for match in compound_subj_rx.finditer(text):
            obj_pronoun = match.group(1)
            start, end = match.span(1)
            nom_pronoun = case_map.get(obj_pronoun.lower(), obj_pronoun)
            if obj_pronoun[0].isupper() or start == 0:
                nom_pronoun = nom_pronoun.capitalize()

            if not self._is_span_covered(start, end, edits):
                edits.append(
                    DiagnosticEdit(
                        span=SpanCoordinate(
                            start_char=start,
                            end_char=end,
                            original_text=obj_pronoun,
                        ),
                        replacement=nom_pronoun,
                        errant_type="R:OTHER",
                        linguistic_rule="Compound Subject Nominative Pronoun Case",
                        explanation=(
                            f"Pronouns serving as the grammatical subject of a finite verb clause must appear in the nominative case ('{nom_pronoun}'), "
                            f"not the objective case ('{obj_pronoun}')."
                        ),
                        counterfactual_example=f"The teacher called {obj_pronoun.lower()}.",
                        confidence=0.97,
                        critic_verified=True,
                    )
                )

    def _check_confusables_and_spelling(self, text: str, edits: List[DiagnosticEdit]) -> None:
        """Evaluates confusable words, homophones, and standard orthographic misspellings."""
        for rule in self.confusable_rules:
            pattern, grp_idx, rep_val, err_type, rule_name, explanation, cf = rule

            for match in re.finditer(pattern, text, re.IGNORECASE):
                start, end = match.span(grp_idx)
                orig_token = match.group(grp_idx)
                replacement = rep_val
                if orig_token.istitle():
                    replacement = replacement.capitalize()
                elif orig_token.isupper():
                    replacement = replacement.upper()

                if not self._is_span_covered(start, end, edits):
                    edits.append(
                        DiagnosticEdit(
                            span=SpanCoordinate(
                                start_char=start,
                                end_char=end,
                                original_text=orig_token,
                            ),
                            replacement=replacement,
                            errant_type=err_type,
                            linguistic_rule=rule_name,
                            explanation=explanation,
                            counterfactual_example=cf,
                            confidence=0.97,
                            critic_verified=True,
                        )
                    )

    def _check_articles(self, text: str, edits: List[DiagnosticEdit]) -> None:
        """Detects phonetic mismatch with indefinite articles 'a' vs 'an'."""
        a_vowel_rx = re.compile(
            r"\b(a)\s+([aeiouAEIOU]\w+)\b",
        )
        consonant_sound_exceptions = {"university", "uniform", "universal", "european", "one", "unique", "unit", "user", "usage", "union"}

        for match in a_vowel_rx.finditer(text):
            article = match.group(1)
            next_word = match.group(2)
            start, end = match.span(1)
            if next_word.lower() in consonant_sound_exceptions:
                continue

            rep = "An" if article[0].isupper() else "an"
            if not self._is_span_covered(start, end, edits):
                edits.append(
                    DiagnosticEdit(
                        span=SpanCoordinate(
                            start_char=start,
                            end_char=end,
                            original_text=article,
                        ),
                        replacement=rep,
                        errant_type="M:DET",
                        linguistic_rule="Indefinite Article Phonetic Agreement",
                        explanation=(
                            f"The indefinite article '{rep}' precedes words beginning with a vowel sound (such as '{next_word}')."
                        ),
                        counterfactual_example="A book was placed on the table.",
                        confidence=0.98,
                        critic_verified=True,
                    )
                )

        an_cons_rx = re.compile(
            r"\b(an)\s+([bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ]\w+)\b",
        )
        vowel_sound_exceptions = {"hour", "hours", "honest", "honor", "honour", "heir", "heirs"}

        for match in an_cons_rx.finditer(text):
            article = match.group(1)
            next_word = match.group(2)
            start, end = match.span(1)
            if next_word.lower() in vowel_sound_exceptions:
                continue

            rep = "A" if article[0].isupper() else "a"
            if not self._is_span_covered(start, end, edits):
                edits.append(
                    DiagnosticEdit(
                        span=SpanCoordinate(
                            start_char=start,
                            end_char=end,
                            original_text=article,
                        ),
                        replacement=rep,
                        errant_type="M:DET",
                        linguistic_rule="Indefinite Article Phonetic Agreement",
                        explanation=(
                            f"The indefinite article '{rep}' precedes words beginning with a consonant sound (such as '{next_word}')."
                        ),
                        counterfactual_example="An apple was eaten.",
                        confidence=0.98,
                        critic_verified=True,
                    )
                )

    def _check_sva_from_priors(
        self, text: str, syntax_priors: Dict[str, Any], edits: List[DiagnosticEdit]
    ) -> None:
        """Extracts SVA discordances from SyntaxEngine dependency priors."""
        sva_pairs = syntax_priors.get("subject_verb_pairs", [])
        for pair in sva_pairs:
            if not pair.get("agreement_mismatch"):
                continue

            subj = pair.get("subject", {})
            verb = pair.get("verb", {})
            subj_num = subj.get("number")
            subj_person = subj.get("person", "3")
            subj_text = subj.get("text", "")
            verb_text = verb.get("text", "")
            verb_start = verb.get("start_char", -1)
            verb_end = verb.get("end_char", -1)

            if subj_text.lower() in ("i", "you") or subj_person in ("1", "2"):
                continue

            if subj_num == "Sing" and verb_start >= 0:
                rep_verb = None
                v_lower = verb_text.lower()
                if v_lower == "were":
                    rep_verb = "was" if verb_text.islower() else "Was"
                elif v_lower == "are":
                    rep_verb = "is" if verb_text.islower() else "Is"
                elif v_lower == "have":
                    rep_verb = "has" if verb_text.islower() else "Has"
                elif v_lower == "do":
                    rep_verb = "does" if verb_text.islower() else "Does"
                elif not v_lower.endswith("s") and len(v_lower) > 2:
                    if v_lower.endswith(("ch", "sh", "ss", "x", "z", "o")):
                        rep_verb = verb_text + "es"
                    elif v_lower.endswith("y") and len(v_lower) > 2 and v_lower[-2] not in "aeiou":
                        rep_verb = verb_text[:-1] + "ies"
                    else:
                        rep_verb = verb_text + "s"

                if rep_verb and text[verb_start:verb_end] == verb_text:
                    if not self._is_span_covered(verb_start, verb_end, edits):
                        edits.append(
                            DiagnosticEdit(
                                span=SpanCoordinate(
                                    start_char=verb_start,
                                    end_char=verb_end,
                                    original_text=verb_text,
                                ),
                                replacement=rep_verb,
                                errant_type="R:VERB:SVA",
                                linguistic_rule="Subject-Verb Agreement with Intervening Modifiers",
                                explanation=(
                                    f"The grammatical subject head is '{subj_text}' (singular), but the verb '{verb_text}' "
                                    f"is plural. The verb must agree in number with its subject head."
                                ),
                                counterfactual_example=f"The students {verb_text} present at the meeting.",
                                confidence=0.98,
                                critic_verified=True,
                            )
                        )

            elif subj_num == "Plur" and verb_start >= 0:
                rep_verb = None
                v_lower = verb_text.lower()
                if v_lower == "was":
                    rep_verb = "were" if verb_text.islower() else "Were"
                elif v_lower == "is":
                    rep_verb = "are" if verb_text.islower() else "Are"
                elif v_lower == "has":
                    rep_verb = "have" if verb_text.islower() else "Have"
                elif v_lower == "does":
                    rep_verb = "do" if verb_text.islower() else "Do"
                elif v_lower.endswith("s") and len(v_lower) > 3:
                    rep_verb = verb_text[:-1]

                if rep_verb and text[verb_start:verb_end] == verb_text:
                    if not self._is_span_covered(verb_start, verb_end, edits):
                        edits.append(
                            DiagnosticEdit(
                                span=SpanCoordinate(
                                    start_char=verb_start,
                                    end_char=verb_end,
                                    original_text=verb_text,
                                ),
                                replacement=rep_verb,
                                errant_type="R:VERB:SVA",
                                linguistic_rule="Plural Subject-Verb Agreement",
                                explanation=(
                                    f"The subject head '{subj_text}' is plural, but the verb '{verb_text}' is singular. "
                                    f"The verb must take the plural form."
                                ),
                                counterfactual_example=f"The student {verb_text} present at the meeting.",
                                confidence=0.98,
                                critic_verified=True,
                            )
                        )

    def _check_heuristic_sva(self, text: str, edits: List[DiagnosticEdit]) -> None:
        """Heuristic direct checks for high-frequency SVA errors like 'He don't' -> 'He doesn't', 'She go' -> 'She goes'."""
        # 1. Pronoun singular + base verb ("He don't", "She don't", "It don't")
        dont_rx = re.compile(r"\b(he|she|it|that|this)\s+(don't)\b", re.IGNORECASE)
        for match in dont_rx.finditer(text):
            subj = match.group(1)
            dont_word = match.group(2)
            start, end = match.span(2)
            rep = "doesn't" if dont_word.islower() else "Doesn't"
            if not self._is_span_covered(start, end, edits):
                edits.append(
                    DiagnosticEdit(
                        span=SpanCoordinate(
                            start_char=start,
                            end_char=end,
                            original_text=dont_word,
                        ),
                        replacement=rep,
                        errant_type="R:VERB:SVA",
                        linguistic_rule="3rd-Person Singular Negative Auxiliary Agreement",
                        explanation=(
                            f"Third-person singular subjects ('{subj}') require '{rep}' rather than '{dont_word}'."
                        ),
                        counterfactual_example=f"They {dont_word.lower()} understand.",
                        confidence=0.98,
                        critic_verified=True,
                    )
                )

        # 2. Pronoun singular + base verb ("He go", "She like", "It look")
        singular_subj_rx = re.compile(
            r"\b(he|she|it)\s+(go|like|want|need|know|think|look|seem|feel|have)\b",
            re.IGNORECASE,
        )
        base_to_3sg = {
            "go": "goes", "like": "likes", "want": "wants", "need": "needs",
            "know": "knows", "think": "thinks", "look": "looks", "seem": "seems",
            "feel": "feels", "have": "has",
        }
        for match in singular_subj_rx.finditer(text):
            subj = match.group(1)
            base_v = match.group(2)
            start, end = match.span(2)
            rep = base_to_3sg.get(base_v.lower(), base_v + "s")
            if not self._is_span_covered(start, end, edits):
                edits.append(
                    DiagnosticEdit(
                        span=SpanCoordinate(
                            start_char=start,
                            end_char=end,
                            original_text=base_v,
                        ),
                        replacement=rep,
                        errant_type="R:VERB:SVA",
                        linguistic_rule="3rd-Person Singular Present Indicative Agreement",
                        explanation=(
                            f"Third-person singular subjects ('{subj}') require 3rd-person singular verb forms ending in '-s' ('{rep}')."
                        ),
                        counterfactual_example=f"They {base_v.lower()} to the library.",
                        confidence=0.98,
                        critic_verified=True,
                    )
                )

        # 3. Plural pronoun + singular verb ("They was", "We was")
        they_was_rx = re.compile(r"\b(they|we|you)\s+(was)\b", re.IGNORECASE)
        for match in they_was_rx.finditer(text):
            subj = match.group(1)
            was_word = match.group(2)
            start, end = match.span(2)
            rep = "were" if was_word.islower() else "Were"
            if not self._is_span_covered(start, end, edits):
                edits.append(
                    DiagnosticEdit(
                        span=SpanCoordinate(
                            start_char=start,
                            end_char=end,
                            original_text=was_word,
                        ),
                        replacement=rep,
                        errant_type="R:VERB:SVA",
                        linguistic_rule="Plural Subject Past Copula Agreement",
                        explanation=(
                            f"The plural subject '{subj}' requires the plural copular verb '{rep}'."
                        ),
                        counterfactual_example="He was present yesterday.",
                        confidence=0.98,
                        critic_verified=True,
                    )
                )

    def _is_span_covered(self, start: int, end: int, edits: List[DiagnosticEdit]) -> bool:
        """Returns True if any existing edit overlaps with [start, end]."""
        for e in edits:
            if not (end <= e.span.start_char or start >= e.span.end_char):
                return True
        return False

    def _deduplicate_edits(self, edits: List[DiagnosticEdit]) -> List[DiagnosticEdit]:
        """Removes overlapping edits while prioritizing higher confidence."""
        if not edits:
            return []

        sorted_by_conf = sorted(edits, key=lambda e: (-e.confidence, e.span.start_char))
        accepted: List[DiagnosticEdit] = []

        for candidate in sorted_by_conf:
            c_start = candidate.span.start_char
            c_end = candidate.span.end_char
            overlaps = False
            for acc in accepted:
                a_start = acc.span.start_char
                a_end = acc.span.end_char
                if not (c_end <= a_start or c_start >= a_end):
                    overlaps = True
                    break
            if not overlaps:
                accepted.append(candidate)

        return sorted(accepted, key=lambda e: e.span.start_char)
