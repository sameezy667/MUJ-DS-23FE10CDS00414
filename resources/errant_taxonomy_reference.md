# ERRANT Taxonomy Reference & Classification Rules

## Overview
ERRANT (Enhanced Reference Alignment and Error Annotation Toolkit) categorizes grammatical errors using a 3-part schema:
`Operation:Main_Category:Sub_Category`

Operations:
- **`R:`** Replacement (substitution of erroneous token with correct token)
- **`M:`** Missing (insertion of omitted token)
- **`U:`** Unnecessary (deletion of redundant token)

---

## Complete Category Table

| Category | Description | Examples | Target Linguistic Rule |
|---|---|---|---|
| **`R:VERB:SVA`** | Subject-Verb Agreement error | *"he know"* $\rightarrow$ *"he knows"*, *"records were"* $\rightarrow$ *"records was"* | Morphosyntactic Concord |
| **`R:SPELL`** | Spelling, typo, or orthographic mistake | *"definately"* $\rightarrow$ *"definitely"*, *"recieve"* $\rightarrow$ *"receive"* | Standard Lexical Orthography |
| **`R:VERB:TENSE`** | Verb tense, aspect, or modal mismatch | *"can went"* $\rightarrow$ *"can go"*, *"have went"* $\rightarrow$ *"have gone"* | Auxiliary & Aspect Harmony |
| **`R:NOUN:NUM`** | Noun number or mass noun error | *"many informations"* $\rightarrow$ *"much information"*, *"two child"* $\rightarrow$ *"two children"* | Countability & Nominal Plural |
| **`R:PREP`** | Incorrect preposition collocation | *"despite of"* $\rightarrow$ *"despite"*, *"married with"* $\rightarrow$ *"married to"* | Prepositional Collocation |
| **`M:DET`** | Missing or incorrect determiner/article | *"a apple"* $\rightarrow$ *"an apple"*, *"an book"* $\rightarrow$ *"a book"* | Indefinite Article Phonetic Agreement |
| **`R:WO`** | Word order permutation | *"always I go"* $\rightarrow$ *"I always go"* | Clause Syntax & Adverbial Placement |
| **`R:OTHER`** | Confusables, homophones, or idioms | *"their is"* $\rightarrow$ *"there is"*, *"affect on"* $\rightarrow$ *"effect on"* | Lexical & Homophone Distinction |
