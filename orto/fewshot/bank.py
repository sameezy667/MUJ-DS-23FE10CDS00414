"""
@file bank.py
@description Curated bank of diverse linguistic minimal pair exemplars across ERRANT taxonomy categories
@module orto/fewshot
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class Exemplar:
    """Represents an annotated linguistic exemplar for few-shot prompt injection."""

    id: str
    errant_type: str
    input_text: str
    target_text: str
    start_char: int
    end_char: int
    original_text: str
    replacement: str
    linguistic_rule: str
    explanation: str
    counterfactual_example: str
    key_pos_tags: List[str]
    syntactic_pattern: str


FEW_SHOT_EXEMPLAR_BANK: List[Exemplar] = [
    # 1. Subject-Verb Agreement (SVA) with Intervening Prepositional Phrase
    Exemplar(
        id="sva-prep-01",
        errant_type="R:VERB:SVA",
        input_text="The box of old vintage vinyl records were dropped by the movers.",
        target_text="The box of old vintage vinyl records was dropped by the movers.",
        start_char=37,
        end_char=41,
        original_text="were",
        replacement="was",
        linguistic_rule="Subject-Verb Agreement with Intervening Prepositional Phrase",
        explanation="The grammatical subject head is singular ('box'); the verb must agree with 'box', not the plural object of preposition 'records'.",
        counterfactual_example="The vinyl records were dropped by the movers.",
        key_pos_tags=["NOUN", "ADP", "NOUN", "AUX", "VERB"],
        syntactic_pattern="nsubj(Sing) -> prep(Plur) -> aux(Plur->Sing)",
    ),
    # 2. SVA with Plural Subject and Singular Verb
    Exemplar(
        id="sva-plur-02",
        errant_type="R:VERB:SVA",
        input_text="The results of the preliminary investigation was inconclusive.",
        target_text="The results of the preliminary investigation were inconclusive.",
        start_char=45,
        end_char=48,
        original_text="was",
        replacement="were",
        linguistic_rule="Plural Subject-Verb Agreement",
        explanation="The subject head 'results' is plural; the predicate auxiliary must be plural ('were').",
        counterfactual_example="The result of the preliminary investigation was inconclusive.",
        key_pos_tags=["NOUN", "ADP", "NOUN", "AUX", "ADJ"],
        syntactic_pattern="nsubj(Plur) -> prep(Sing) -> aux(Sing->Plur)",
    ),
    # 3. Orthographic / Spelling Confusion
    Exemplar(
        id="spell-vowel-01",
        errant_type="R:SPELL",
        input_text="She will definately recieve the package untill Friday.",
        target_text="She will definitely receive the package until Friday.",
        start_char=9,
        end_char=19,
        original_text="definately",
        replacement="definitely",
        linguistic_rule="Standard Orthographic Spelling",
        explanation="'definately' is an orthographic vowel substitution error for 'definitely'.",
        counterfactual_example="We will definitely confirm the reservation.",
        key_pos_tags=["PRON", "AUX", "ADV", "VERB"],
        syntactic_pattern="advmod(SpellError)",
    ),
    # 4. Homophone Confusion (Existential 'There' vs Possessive 'Their')
    Exemplar(
        id="spell-homophone-02",
        errant_type="R:SPELL",
        input_text="Their is no doubt that the committee will approve the budget.",
        target_text="There is no doubt that the committee will approve the budget.",
        start_char=0,
        end_char=5,
        original_text="Their",
        replacement="There",
        linguistic_rule="Homophone Distinction (Existential Pronoun)",
        explanation="'Their' is a possessive pronoun. The existential dummy pronoun 'There' is required before 'is'.",
        counterfactual_example="Their house is located on the corner of the avenue.",
        key_pos_tags=["PRON", "VERB", "DET", "NOUN"],
        syntactic_pattern="expl(PronounHomophone)",
    ),
    # 5. Indefinite Article Phonetic Agreement
    Exemplar(
        id="det-phonetic-01",
        errant_type="M:DET",
        input_text="A unexpected error occured during the file upload process.",
        target_text="An unexpected error occurred during the file upload process.",
        start_char=0,
        end_char=1,
        original_text="A",
        replacement="An",
        linguistic_rule="Indefinite Article Phonetic Agreement",
        explanation="The indefinite article 'an' precedes words beginning with a vowel sound ('unexpected').",
        counterfactual_example="A sudden error occurred during the process.",
        key_pos_tags=["DET", "ADJ", "NOUN"],
        syntactic_pattern="det(A->An)",
    ),
    # 6. Mass / Uncountable Noun Countability
    Exemplar(
        id="noun-num-01",
        errant_type="R:NOUN:NUM",
        input_text="The goverment provides many informations to the public.",
        target_text="The government provides much information to the public.",
        start_char=28,
        end_char=40,
        original_text="informations",
        replacement="information",
        linguistic_rule="Uncountable Mass Noun Morphology",
        explanation="'Information' is an uncountable mass noun in English and cannot take a plural '-s' suffix.",
        counterfactual_example="The government provides many reports to the public.",
        key_pos_tags=["DET", "NOUN", "VERB", "ADJ", "NOUN"],
        syntactic_pattern="dobj(MassNounPlural)",
    ),
    # 7. Prepositional Collocation Error
    Exemplar(
        id="prep-colloc-01",
        errant_type="R:PREP",
        input_text="We are very interested for participating in this project.",
        target_text="We are very interested in participating in this project.",
        start_char=23,
        end_char=26,
        original_text="for",
        replacement="in",
        linguistic_rule="Adjectival Preposition Collocation",
        explanation="The participial adjective 'interested' standardly collocates with 'in', not 'for'.",
        counterfactual_example="This funding is intended for participating organizations.",
        key_pos_tags=["PRON", "AUX", "ADV", "ADJ", "ADP", "VERB"],
        syntactic_pattern="prep(AdjCollocation)",
    ),
    # 8. Transitive Verb Extraneous Preposition
    Exemplar(
        id="prep-trans-02",
        errant_type="R:PREP",
        input_text="A increase in temperature affect on the final chemical reaction.",
        target_text="An increase in temperature affects the final chemical reaction.",
        start_char=33,
        end_char=35,
        original_text="on",
        replacement="",
        linguistic_rule="Extraneous Preposition on Transitive Verb",
        explanation="'Affect' is a transitive verb taking a direct object; the extraneous preposition 'on' must be omitted.",
        counterfactual_example="The temperature had a strong effect on the final chemical reaction.",
        key_pos_tags=["VERB", "ADP", "DET", "ADJ", "NOUN"],
        syntactic_pattern="prep(ExtraneousPreposition)",
    ),
    # 9. Temporal Adverbial / Verb Tense Discordance
    Exemplar(
        id="tense-adverb-01",
        errant_type="R:OTHER",
        input_text="Tomorrow I went to the store and bought groceries.",
        target_text="Yesterday I went to the store and bought groceries.",
        start_char=0,
        end_char=8,
        original_text="Tomorrow",
        replacement="Yesterday",
        linguistic_rule="Temporal Adverbial Agreement",
        explanation="The future temporal adverbial 'Tomorrow' contradicts the past tense verbs 'went' and 'bought'. Minimal editing aligns the temporal adverbial to 'Yesterday'.",
        counterfactual_example="Tomorrow I will go to the store and buy groceries.",
        key_pos_tags=["NOUN", "PRON", "VERB", "ADP", "DET", "NOUN"],
        syntactic_pattern="npadvmod(Future) -> ROOT(PastVerb)",
    ),
]

