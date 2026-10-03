"""
@file syntax_engine.py
@description spaCy Universal Dependency and morphological feature extractor
@module orto/core
"""

from typing import Any, Dict, List, Optional, Tuple
import spacy
from spacy.tokens import Doc, Token


class SyntaxEngine:
    """
    Extracts Universal Dependencies, morphological feature sets, and structural
    dependency priors using spaCy.
    """

    _nlp_instance: Optional[spacy.language.Language] = None

    def __init__(self, model_name: str = "en_core_web_sm") -> None:
        """
        Initializes the SyntaxEngine with a spaCy pipeline.

        Args:
            model_name: spaCy model name to load.
        """
        self.model_name = model_name
        self.nlp = self._get_or_load_nlp(model_name)

    @classmethod
    def _get_or_load_nlp(cls, model_name: str = "en_core_web_sm") -> spacy.language.Language:
        """Cached singleton loader for spaCy pipeline."""
        if cls._nlp_instance is None:
            try:
                cls._nlp_instance = spacy.load(model_name)
            except OSError:
                # Fallback to downloading or loading blank English if needed
                from spacy.cli import download

                download(model_name)
                cls._nlp_instance = spacy.load(model_name)
        return cls._nlp_instance

    def parse(self, text: str) -> Doc:
        """
        Runs spaCy linguistic parsing over raw text.

        Args:
            text: Input string.

        Returns:
            spaCy Doc instance with syntactic tree and morphology.
        """
        return self.nlp(text)

    def extract_dependency_triples(self, doc: Doc) -> List[Dict[str, Any]]:
        """
        Extracts directed Universal Dependency edges: (head, dep, child).

        Args:
            doc: Parsed spaCy Doc.

        Returns:
            List of dependency relation dictionaries with token text, POS, dep, and char offsets.
        """
        triples: List[Dict[str, Any]] = []
        for token in doc:
            morph_dict = token.morph.to_dict()
            triples.append(
                {
                    "child_idx": token.i,
                    "child_text": token.text,
                    "child_pos": token.pos_,
                    "child_tag": token.tag_,
                    "dep": token.dep_,
                    "head_idx": token.head.i,
                    "head_text": token.head.text,
                    "head_pos": token.head.pos_,
                    "start_char": token.idx,
                    "end_char": token.idx + len(token.text),
                    "morph": morph_dict,
                }
            )
        return triples

    def extract_sva_pairs(self, doc: Doc) -> List[Dict[str, Any]]:
        """
        Finds Subject-Verb Agreement candidate pairs in the dependency parse,
        associating subjects with the finite verb or auxiliary that carries number inflection.

        Args:
            doc: Parsed spaCy Doc.

        Returns:
            List of dictionaries containing subject head and finite verb/auxiliary details.
        """
        sva_pairs: List[Dict[str, Any]] = []

        for token in doc:
            # Check if token is a predicate (VERB or AUX)
            if token.pos_ in ("VERB", "AUX"):
                # Look for nominal subjects
                subj_tokens = [
                    child
                    for child in token.children
                    if child.dep_ in ("nsubj", "nsubjpass", "csubj", "csubjpass")
                ]
                if not subj_tokens:
                    continue

                # Check if there is an auxiliary verb child carrying finiteness (e.g. 'was dropped', 'were built')
                aux_children = [
                    c for c in token.children if c.dep_ in ("aux", "auxpass") and c.pos_ in ("AUX", "VERB")
                ]
                # Target verb carrying the agreement inflection
                target_verbs = aux_children if aux_children else [token]

                for subj in subj_tokens:
                    subj_morph = subj.morph.to_dict()
                    subj_num = subj_morph.get("Number")
                    subj_person = subj_morph.get("Person", "3")
                    if subj.text.lower() == "i":
                        subj_num = "Sing"
                        subj_person = "1"
                    elif subj.text.lower() == "you":
                        subj_num = "Plur"  # Grammatically takes plural verb forms in English
                        subj_person = "2"
                    elif not subj_num:
                        if subj.tag_ in ("NN", "NNP"):
                            subj_num = "Sing"
                            subj_person = "3"
                        elif subj.tag_ in ("NNS", "NNPS"):
                            subj_num = "Plur"
                            subj_person = "3"
                        else:
                            subj_num = "Unspecified"

                    for v in target_verbs:
                        verb_morph = v.morph.to_dict()
                        verb_num = verb_morph.get("Number")
                        verb_person = verb_morph.get("Person", "Unspecified")

                        # Infer number & person for English verbs/auxiliaries if missing in morph
                        v_lower = v.text.lower()
                        if not verb_num:
                            if v_lower in ("is", "was", "has", "does") or v.tag_ == "VBZ":
                                verb_num = "Sing"
                                verb_person = "3"
                            elif v_lower in ("are", "were", "have", "do") or v.tag_ == "VBP":
                                verb_num = "Plur"
                            else:
                                verb_num = "Unspecified"

                        verb_tense = verb_morph.get("Tense", "Unspecified")
                        verb_form = verb_morph.get("VerbForm", "Unspecified")

                        # Determine if this pair has a genuine grammatical agreement mismatch
                        has_mismatch = False
                        if subj_person == "1":
                            # "I" allows am, was, do, have, base forms (VBP). Rejects VBZ (is, does, has, eats).
                            if v.tag_ == "VBZ" or v_lower in ("is", "does", "has"):
                                has_mismatch = True
                        elif subj_person == "2":
                            # "You" allows are, were, do, have, base forms (VBP). Rejects VBZ and 'was'.
                            if v.tag_ == "VBZ" or v_lower in ("is", "was", "does", "has"):
                                has_mismatch = True
                        elif subj_person == "3":
                            if subj_num == "Sing" and (v.tag_ == "VBP" or v_lower in ("are", "were")):
                                has_mismatch = True
                            elif subj_num == "Plur" and (v.tag_ == "VBZ" or v_lower in ("is", "was", "does", "has")):
                                has_mismatch = True

                        sva_pairs.append(
                            {
                                "subject": {
                                    "text": subj.text,
                                    "pos": subj.pos_,
                                    "dep": subj.dep_,
                                    "number": subj_num,
                                    "person": subj_person,
                                    "start_char": subj.idx,
                                    "end_char": subj.idx + len(subj.text),
                                },
                                "verb": {
                                    "text": v.text,
                                    "pos": v.pos_,
                                    "tag": v.tag_,
                                    "number": verb_num,
                                    "person": verb_person,
                                    "tense": verb_tense,
                                    "verb_form": verb_form,
                                    "start_char": v.idx,
                                    "end_char": v.idx + len(v.text),
                                },
                                "agreement_mismatch": has_mismatch,
                            }
                        )
        return sva_pairs

    def extract_priors(self, text: str) -> Dict[str, Any]:
        """
        Extracts a compact, linguistically grounded structural summary
        suitable for LLM prompt injection.

        Args:
            text: Raw input string.

        Returns:
            Dictionary with dependency edges, SVA pairs, and syntactic anomalies.
        """
        doc = self.parse(text)
        triples = self.extract_dependency_triples(doc)
        sva_pairs = self.extract_sva_pairs(doc)

        # Highlight key relations
        key_relations: List[str] = []
        for t in triples:
            if t["dep"] in ("ROOT", "nsubj", "nsubjpass", "dobj", "pobj", "prep", "attr", "advmod", "npadvmod"):
                key_relations.append(
                    f"{t['head_text']} --[{t['dep']}]--> {t['child_text']} (POS: {t['child_pos']}, Morph: {t['morph']})"
                )

        # Detect anomalous dependency labels (e.g., 'dep' unclassified)
        anomalies = [
            f"Unresolved token '{t['child_text']}' at index {t['child_idx']} with dep='dep'"
            for t in triples
            if t["dep"] == "dep"
        ]

        # Add any detected SVA agreement mismatches to anomalies
        for pair in sva_pairs:
            if pair.get("agreement_mismatch"):
                s_txt = pair["subject"]["text"]
                v_txt = pair["verb"]["text"]
                anomalies.append(f"Potential Subject-Verb Agreement mismatch between '{s_txt}' and '{v_txt}'")

        # Detect temporal adverbial vs verb tense discordance
        past_verbs = [
            t for t in doc
            if t.pos_ in ("VERB", "AUX") and (t.tag_ == "VBD" or t.morph.get("Tense") == ["Past"])
        ]
        future_aux = [
            t for t in doc
            if t.text.lower() in ("will", "shall") or (t.text.lower() == "going" and any(c.text.lower() == "to" for c in t.children))
        ]
        future_adverbs = {"tomorrow", "next week", "next month", "next year"}
        past_adverbs = {"yesterday", "last night", "last week", "last month", "last year", "ago"}

        for t in doc:
            t_low = t.text.lower()
            if t_low in future_adverbs and past_verbs:
                anomalies.append(
                    f"Temporal discordance: Future adverbial '{t.text}' conflicts with past tense verb(s) {[v.text for v in past_verbs]}"
                )
            elif t_low in past_adverbs and future_aux:
                anomalies.append(
                    f"Temporal discordance: Past adverbial '{t.text}' conflicts with future auxiliary {[v.text for v in future_aux]}"
                )

        return {
            "sentence_length": len(doc),
            "key_dependencies": key_relations,
            "subject_verb_pairs": sva_pairs,
            "anomalies": anomalies,
        }

