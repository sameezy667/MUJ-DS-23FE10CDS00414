/**
 * @file engine.ts
 * @description Local linguistic heuristic rule engine & dependency prior parser for Orto client-side workbench
 * @module frontend/src/utils
 */

import type { DepToken, DiagnosticEdit, ErrantType } from '../types';

export const CATS: Record<ErrantType, { c: string; label: string; desc: string; bad: string; good: string }> = {
  'R:SPELL': {
    c: '#b07614',
    label: 'Spelling · Typographic',
    desc: 'Phonetic and orthographic misspellings, ranked against confusion sets.',
    bad: 'recieve',
    good: 'receive',
  },
  'R:VERB:SVA': {
    c: '#d92c35',
    label: 'Subject–Verb Agreement',
    desc: 'Finite verb disagrees with the subject head — including across prepositional phrases.',
    bad: 'box … were',
    good: 'was',
  },
  'R:VERB:TENSE': {
    c: '#c25a1e',
    label: 'Tense · Aspect',
    desc: 'Wrong tense or aspect, checked against temporal adverbials and perfect constructions.',
    bad: 'I go',
    good: 'I went',
  },
  'R:NOUN:NUM': {
    c: '#1a6f8a',
    label: 'Noun Number',
    desc: 'Countability violations and irregular plural paradigms.',
    bad: 'three informations',
    good: 'information',
  },
  'R:PREP': {
    c: '#3a5fa8',
    label: 'Preposition Selection',
    desc: 'Substitution or deletion of a wrongly-selected preposition.',
    bad: 'married with',
    good: 'married to',
  },
  'M:DET': {
    c: '#6a4fa3',
    label: 'Missing Determiner',
    desc: 'Absent or phonologically wrong article / determiner.',
    bad: 'a old',
    good: 'an old',
  },
  'R:WO': {
    c: '#a83a8a',
    label: 'Word Order',
    desc: 'Permuted constituents — typically wh-inversion and compound subjects.',
    bad: 'what means this?',
    good: 'what does this mean?',
  },
  'R:OTHER': {
    c: '#5c5850',
    label: 'Idiomatic · Lexical',
    desc: 'Collocational and idiomatic violations outside the other classes.',
    bad: 'I am agree',
    good: 'I agree',
  },
};

export const softColor = (hex: string): string => {
  const n = parseInt(hex.slice(1), 16);
  return `rgba(${(n >> 16) & 255},${(n >> 8) & 255},${n & 255},.12)`;
};

export const cap = (s: string): string => (s ? s[0].toUpperCase() + s.slice(1) : s);

export const matchCase = (src: string, repl: string): string => {
  if (!src || !repl) return repl;
  if (src[0] !== src[0].toLowerCase() && src[0] !== src[0].toUpperCase()) return repl;
  return src[0] === src[0].toUpperCase() ? repl[0].toUpperCase() + repl.slice(1) : repl;
};

// Lexicons
export const IRREG: Record<string, string> = {
  go: 'went', eat: 'ate', see: 'saw', take: 'took', make: 'made', come: 'came', buy: 'bought',
  write: 'wrote', drink: 'drank', drive: 'drove', run: 'ran', give: 'gave', find: 'found',
  know: 'knew', think: 'thought', break: 'broke', speak: 'spoke', meet: 'met', pay: 'paid',
  say: 'said', tell: 'told', get: 'got', read: 'read', teach: 'taught', catch: 'caught',
  build: 'built', feel: 'felt', keep: 'kept', leave: 'left', lose: 'lost', swim: 'swam',
  understand: 'understood', send: 'sent',
};

export const REV: Record<string, string> = {};
for (const b in IRREG) REV[IRREG[b]] = b;
export const PAST = new Set(Object.values(IRREG));

export const PART: Record<string, string> = {
  went: 'gone', ate: 'eaten', saw: 'seen', took: 'taken', wrote: 'written', spoke: 'spoken',
  broke: 'broken', did: 'done', came: 'come', drove: 'driven', gave: 'given', knew: 'known',
  grew: 'grown', flew: 'flown', was: 'been', were: 'been', forgot: 'forgotten', chose: 'chosen',
  fell: 'fallen',
};

export const LEX = {
  PREP: new Set('of in on at to by for with from into over after before between during without about under near above below against along among around behind beside despite except inside outside toward upon within'.split(' ')),
  DET: new Set('the a an this that these those my your his her its our their each every some any both such'.split(' ')),
  PRON: new Set('i you he she it we they me him her us them who whom what'.split(' ')),
  AUX: new Set("is are was were be been being am has have had do does did will would can could should may might must don't doesn't didn't isn't wasn't aren't".split(' ')),
  CONJ: new Set('and or but so yet nor'.split(' ')),
  ADV: new Set('very much more most always often never sometimes usually really quite too also just only still even again well maybe perhaps'.split(' ')),
  ADJ: new Set('good bad big small new old young beautiful happy sad quick slow long short high low important different same next last few many great little whole major final strong weak early late modern vintage'.split(' ')),
  VERB: new Set('go eat see take make come buy write drive run give find know think speak meet pay say tell get read teach catch drink swim understand study work play walk arrive visit call send lose leave keep feel live like love hate want need seem look watch show open close start finish help move stop build create explain discuss marry mean drop believe hold bring win'.split(' ')),
};

export function pastOf(base: string): string {
  if (IRREG[base]) return IRREG[base];
  return /e$/.test(base) ? base + 'd' : base + 'ed';
}

export function toBase(v: string): string {
  if (/(ch|sh|ss|x|z|o)es$/i.test(v)) return v.slice(0, -2);
  if (/s$/i.test(v)) return v.slice(0, -1);
  return v;
}

export const SPELLMAP: Record<string, { f: string; cf: string }> = {
  teh: { f: 'the', cf: 'Go to the store.' },
  libary: { f: 'library', cf: 'The library closes at nine.' },
  recieve: { f: 'receive', cf: 'We receive your message every Friday.' },
  seperate: { f: 'separate', cf: 'Keep the two files separate.' },
  definately: { f: 'definitely', cf: 'That is definitely the right answer.' },
  explaination: { f: 'explanation', cf: 'Your explanation was very clear.' },
  occured: { f: 'occurred', cf: 'The error occurred twice.' },
  untill: { f: 'until', cf: 'Wait until Friday.' },
  becuase: { f: 'because', cf: 'Because I said so.' },
  thier: { f: 'their', cf: 'They left their keys inside.' },
  beleive: { f: 'believe', cf: 'I believe you.' },
  wich: { f: 'which', cf: 'Which option do you prefer?' },
  tommorow: { f: 'tomorrow', cf: 'See you tomorrow.' },
  wierd: { f: 'weird', cf: 'That was weird.' },
  goverment: { f: 'government', cf: 'The government responded.' },
  enviroment: { f: 'environment', cf: 'Protect the environment.' },
  neccessary: { f: 'necessary', cf: 'Bring the necessary forms.' },
  accomodate: { f: 'accommodate', cf: 'We can accommodate you.' },
  embarass: { f: 'embarrassed', cf: "Don't be embarrassed." },
  calender: { f: 'calendar', cf: 'Mark the calendar.' },
  arguement: { f: 'argument', cf: 'That is a weak argument.' },
  alot: { f: 'a lot', cf: 'I have a lot of work today.' },
  writting: { f: 'writing', cf: 'She is writing a novel.' },
  freind: { f: 'friend', cf: 'She is my best friend.' },
  freinds: { f: 'friends', cf: 'I met my friends at noon.' },
  begining: { f: 'beginning', cf: 'From the beginning.' },
  acheive: { f: 'achieve', cf: 'You can achieve it.' },
  adress: { f: 'address', cf: 'Check the address.' },
  lenght: { f: 'length', cf: 'Measure the length.' },
};

export const spellRe = new RegExp('\\b(' + Object.keys(SPELLMAP).sort((a, b) => b.length - a.length).join('|') + ')\\b', 'gid');

export function spanFor(m: any, g?: number): [number, number] | null {
  g = g == null ? 0 : g;
  if (m.indices && m.indices[g]) return [m.indices[g][0], m.indices[g][1]];
  if (g === 0) return [m.index, m.index + m[0].length];
  const sub = m[g];
  if (sub == null) return null;
  const rel = m[0].indexOf(sub);
  return rel < 0 ? null : [m.index + rel, m.index + rel + sub.length];
}

interface RuleDef {
  re?: RegExp | null;
  target: number;
  build?: (m: any) => any;
  list?: Array<[RegExp, string, string, string, string]>;
}

export const RULES: RuleDef[] = [
  {
    re: /\b(the|a|an|this|that|each|every|either|neither|one)\s+([a-z]+)\s+of\s+((?:[a-z]+\s+){0,4}[a-z]+)\s+(were|are|have|do)\b((?:\s+[a-z']+){0,7})/gid,
    target: 4,
    build(m) {
      const [, , head, pp, verb, tail] = m;
      if (/s$/.test(head.toLowerCase())) return null;
      const map: Record<string, string> = { were: 'was', are: 'is', have: 'has', do: 'does' };
      const repl = map[verb];
      const ppLast = pp.trim().split(/\s+/).pop();
      return {
        type: 'R:VERB:SVA' as ErrantType,
        replacement: repl,
        subject: head,
        subjNum: 'Sing',
        rule: 'Subject–Verb Agreement with Intervening Prepositional Phrase',
        exp: `The grammatical subject head is “${head}” (singular), separated from the verb by the prepositional phrase “of ${pp.trim()}”. The verb must agree with “${head}” — not with the adjacent plural “${ppLast}” — so the finite verb takes the singular form “${repl}”.`,
        cf: `The ${pp.trim()} ${verb}${(tail || '').replace(/[.!?]$/, '')}.`,
        conf: 0.98,
      };
    },
  },
  {
    re: /\b(he|she|it)\s+(don't|dont|do not|are|were|have)\b/gid,
    target: 2,
    build(m) {
      const [s, v] = m.slice(1);
      const map: Record<string, string> = { "don't": "doesn't", dont: "doesn't", "do not": "does not", are: 'is', were: 'was', have: 'has' };
      const tails: Record<string, string> = { are: 'late', were: 'there', have: 'time', "don't": 'like it', dont: 'like it', 'do not': 'agree' };
      return {
        type: 'R:VERB:SVA' as ErrantType,
        replacement: map[v],
        subject: s,
        subjNum: 'Sing',
        rule: 'Third-Person Singular Agreement',
        exp: `“${s}” is a third-person singular subject, so the finite verb must take its third-person form: “${v}” → “${map[v]}”.`,
        cf: `We ${v} ${tails[v] || ''} — plural subjects take the plural form.`,
        conf: 0.97,
      };
    },
  },
  {
    re: /\b(they|we|you|these|those)\s+(was|is|has|doesn't|lives|likes|wants|goes|knows|makes|takes|asks|seems)\b/gid,
    target: 2,
    build(m) {
      const [s, v] = m.slice(1);
      const map: Record<string, string> = { was: 'were', is: 'are', has: 'have', "doesn't": "don't" };
      const repl = map[v] || v.replace(/s$/, '');
      const cfMap: Record<string, string> = {
        was: 'The parcel was delivered today.',
        is: 'The book is on the shelf.',
        has: 'The parcel has a label.',
        "doesn't": 'She does not smoke.',
        lives: 'My aunt lives in Lisbon.',
        likes: 'My aunt likes jazz.',
        wants: 'My aunt wants a coffee.',
        goes: 'The train goes at nine.',
        knows: 'My aunt knows the answer.',
        makes: 'She makes ceramics.',
        takes: 'She takes the bus.',
        asks: 'She asks good questions.',
        seems: 'It seems fine.',
      };
      return {
        type: 'R:VERB:SVA' as ErrantType,
        replacement: repl,
        subject: s,
        subjNum: 'Plur',
        rule: 'Plural Subject Agreement',
        exp: `“${s}” is a plural subject, so the finite verb takes its plural / base form: “${v}” → “${repl}”.`,
        cf: cfMap[v] || 'They were present.',
        conf: 0.96,
      };
    },
  },
  {
    re: /\b(he|she|it)\s+(ask|make|take|want|need|like|know|think|say|go|come|have|do|play|watch|study|work|live|look|seem|write|read|call|talk|walk|run|drive|speak)\b(?=\s)/gid,
    target: 2,
    build(m) {
      const [s, v] = m.slice(1);
      const map: Record<string, string> = { have: 'has', do: 'does', go: 'goes' };
      const repl = map[v] || v + 's';
      return {
        type: 'R:VERB:SVA' as ErrantType,
        replacement: repl,
        subject: s,
        subjNum: 'Sing',
        rule: 'Third-Person Singular ‑s Inflection',
        exp: `A singular third-person subject (“${s}”) in the present simple requires the ‑s form of the lexical verb: “${v}” → “${repl}”.`,
        cf: `They ${v} every weekend.`,
        conf: 0.95,
      };
    },
  },
  {
    re: /\b(yesterday|last night|last week|last month|last year|last weekend)\s+(?:(i|we|they|he|she|you)\s+)?(goes|go|eats|eat|sees|see|takes|take|makes|make|comes|come|buys|buy|writes|write|drives|drive|runs|run|gives|give|finds|find|knows|know|thinks|think|speaks|speak|meets|meet|pays|pay|says|say|tells|tell|gets|get|reads|read|teaches|teach|catches|catch|drinks|drink|swims|swim|understands|understand|studies|study|works|work|plays|play|walks|walk|arrives|arrive|visits|visit|calls|call|sends|send|loses|lose|leaves|leave|keeps|keep|feels|feel)\b/gid,
    target: 3,
    build(m) {
      const [marker, , v] = m.slice(1);
      if (PAST.has(v.toLowerCase()) || /ed$/i.test(v)) return null;
      const base = toBase(v);
      const past = pastOf(base);
      return {
        type: 'R:VERB:TENSE' as ErrantType,
        replacement: past,
        rule: 'Past-Tense Concordance with Temporal Adverbials',
        exp: `The past-time adverbial “${marker}” anchors the clause to a finished time frame, so the lexical verb must appear in the past tense: “${v}” → “${past}”.`,
        cf: `I ${v} there every week — habitual present is fine without past time.`,
        conf: 0.93,
      };
    },
  },
  {
    re: /\b(can|could|should|would|will|shall|might|may|must|did|does|do|didn't|did\s+not|doesn't|don't)\s+(?:(i|you|he|she|it|we|they|[a-z]+)\s+)?(went|saw|ate|came|took|wrote|bought|found|made|said|told|gave|knew|thought|brought|left|felt|began|ran|broke|chose|drove|fell|forgot|grew|heard|kept|paid|read|sent|slept|spoke|spent|stood|swam|taught|threw|understood|wore|won)\b/gid,
    target: 3,
    build(m) {
      const [aux, subj, v] = m.slice(1);
      const targetVerb = v || subj;
      const base = REV[targetVerb.toLowerCase()] || toBase(targetVerb);
      return {
        type: 'R:VERB:TENSE' as ErrantType,
        replacement: base,
        rule: 'Modal Auxiliary Verb Form (Bare Infinitive)',
        exp: `Modal auxiliary verbs such as “${aux}” require the bare infinitive / base form of the lexical verb (“${base}”), rather than past tense “${targetVerb}”.`,
        cf: `I can ${base} tomorrow.`,
        conf: 0.98,
      };
    },
  },
  {
    re: /\b(tomorrow|next\s+week|next\s+month|next\s+year)\s+(?:(i|we|they|he|she|you|[a-z]+)\s+)?(went|saw|ate|came|took|wrote|bought|found|made|said|told|gave|knew|thought|brought|left|felt|began|ran|broke|chose|drove|fell|forgot|grew|heard|kept|paid|read|sent|slept|spoke|spent|stood|swam|taught|threw|understood|wore|won|was|were|had|did|[a-z]+ed)\b/gid,
    target: 1,
    build(m) {
      const [marker, , verb] = m.slice(1);
      const isCap = marker[0] === marker[0].toUpperCase();
      let repl = isCap ? 'Yesterday' : 'yesterday';
      if (/week/i.test(marker)) repl = isCap ? 'Last week' : 'last week';
      else if (/month/i.test(marker)) repl = isCap ? 'Last month' : 'last month';
      else if (/year/i.test(marker)) repl = isCap ? 'Last year' : 'last year';
      return {
        type: 'R:OTHER' as ErrantType,
        replacement: repl,
        rule: 'Temporal Adverbial Agreement (Tense Concordance)',
        exp: `The future temporal adverbial “${marker}” contradicts the past tense verb “${verb}”. In minimal-edit GEC, reconciling the time adverbial to “${repl}” aligns the clause’s temporal frame with the past narrative.`,
        cf: `Tomorrow I will ${toBase(verb)} there.`,
        conf: 0.97,
      };
    },
  },
  {
    re: /\b(yesterday|last\s+night|last\s+week|last\s+month|last\s+year)\s+(?:(i|we|they|he|she|you|[a-z]+)\s+)?(will|shall)\b/gid,
    target: 1,
    build(m) {
      const [marker, , aux] = m.slice(1);
      const isCap = marker[0] === marker[0].toUpperCase();
      const repl = isCap ? 'Tomorrow' : 'tomorrow';
      return {
        type: 'R:OTHER' as ErrantType,
        replacement: repl,
        rule: 'Temporal Adverbial Agreement (Tense Concordance)',
        exp: `The past temporal adverbial “${marker}” contradicts the future auxiliary “${aux}”. Reconciling the adverbial to “${repl}” restores temporal agreement.`,
        cf: `Yesterday I went there.`,
        conf: 0.97,
      };
    },
  },
  {
    re: /\b(i)\b/gd,

    target: 1,
    build(_m) {
      return {
        type: 'R:SPELL' as ErrantType,
        replacement: 'I',
        rule: 'First-Person Pronoun Capitalization',
        exp: 'The first-person singular pronoun “I” is always capitalized in standard English orthography.',
        cf: 'I am ready.',
        conf: 0.99,
      };
    },
  },
  {
    re: /^([a-z]+)\b/gd,
    target: 1,
    build(m) {
      const w = m[1];
      if (!w || w[0] === w[0].toUpperCase()) return null;
      return {
        type: 'R:SPELL' as ErrantType,
        replacement: cap(w),
        rule: 'Sentence-Initial Capitalization',
        exp: `Sentences must begin with a capital letter: “${w}” → “${cap(w)}”.`,
        cf: `${cap(w)} you please check this?`,
        conf: 0.95,
      };
    },
  },
  {
    re: /\b(didn't|did\s+not)\s+([a-z]+ed|went|saw|took|ate|made|got|came|bought|wrote|spoke|knew|thought|found|told|said|paid|drove|left|kept|understood|taught|caught|read|gave|sent|met)\b/gid,
    target: 2,
    build(m) {
      const [aux, v] = m.slice(1);
      let base = REV[v.toLowerCase()];
      if (!base) {
        if (/ied$/.test(v)) base = v.replace(/ied$/, 'y');
        else if (/ed$/.test(v)) {
          base = v.slice(0, -2);
          if (/([^aeiou])\1$/.test(base)) base = base.slice(0, -1);
        }
      }
      if (!base) return null;
      return {
        type: 'R:VERB:TENSE' as ErrantType,
        replacement: base,
        rule: 'Bare Stem after Dummy Auxiliary do',
        exp: `“${aux}” is the past-tense auxiliary do, which already carries tense for the whole predicate. The lexical verb must therefore stay in its bare stem form: “${v}” → “${base}”.`,
        cf: `She ${v} the report yesterday — with no auxiliary, the past form is correct.`,
        conf: 0.99,
      };
    },
  },
  {
    re: /\b(has|have)\s+(went|ate|saw|took|wrote|spoke|broke|did|came|drove|gave|knew|grew|flew|was|were|forgot|chose|fell)\b/gid,
    target: 2,
    build(m) {
      const [aux, v] = m.slice(1);
      return {
        type: 'R:VERB:TENSE' as ErrantType,
        replacement: PART[v.toLowerCase()],
        rule: 'Perfect Aspect Requires the Past Participle',
        exp: `The perfect construction “${aux} + …” selects the past participle, not the simple past: “${v}” → “${PART[v.toLowerCase()]}”.`,
        cf: `She ${v} home yesterday — simple past with no auxiliary.`,
        conf: 0.97,
      };
    },
  },
  {
    re: spellRe,
    target: 1,
    build(m) {
      const o = m[1];
      const e = SPELLMAP[o.toLowerCase()];
      return {
        type: 'R:SPELL' as ErrantType,
        replacement: e.f,
        rule: 'Orthographic Correction (Confusion Set)',
        exp: `“${o}” is a high-frequency misspelling of “${e.f}” — a ranked confusion pair (data/confusion_sets.json).`,
        cf: e.cf,
        conf: 0.99,
      };
    },
  },
  {
    re: null,
    target: 0,
    list: [
      [/\bdifferent\s+than\b/gi, 'different from', 'Adjective Complement Selection: different + from', '“Different” selects “from” for standard-of-comparison complements; “than” is licensed by comparative adjectives.', 'This approach is easier than the old one.'],
      [/\bmarried\s+with\b/gi, 'married to', 'Selectional Restriction: marry + to', 'The verb “marry” selects “to” for its spouse complement; “with” attaches modifiers instead.', 'She is married with two children — “with” correctly attaches the children here.'],
      [/\bgood\s+in\b/gi, 'good at', 'Skill Predicate Complementation: good + at', 'Predicate adjectives of skill (“good”, “brilliant”, “terrible”) select “at” + gerund or NP.', 'It looks good in print — “in” marks a medium, not a skill.'],
      [/\bnear\s+of\b/gi, 'near', 'P-Comp Reduction: near', '“Near” is a locative preposition and takes its complement directly; “of” is unlicensed here.', 'The roof of the house — “of” is licensed by “roof”.'],
      [/\binterested\s+about\b/gi, 'interested in', 'Psych-Predicate Complementation: interested + in', 'Stative psych predicates of the interested-class select “in” for their stimulus.', 'She told me about the delay — “tell” selects “about”.'],
      [/\bcapable\s+to\b/gi, 'capable of', 'Adjective Complementation: capable + of', '“Capable” selects “of” + gerund; “to” is licensed by adjectives like “able”.', 'He is able to help — “able” licenses “to”.'],
      [/\bdiscuss\s+about\b/gi, 'discuss', 'Transitive Verb without About-Complement', '“Discuss” is transitive and takes its object directly; the redundant “about” is deleted.', 'We talked about the plan — “talk” requires “about”.'],
      [/\bdepends\s+of\b/gi, 'depends on', 'Verb Complement Selection: depend + on', '“Depend” selects “on” for its complement.', 'The cover of the book — “of” is licensed by “cover”.'],
      [/\barrived\s+to\b/gi, 'arrived at', 'Goal Preposition Selection: arrive + at', '“Arrive” takes punctual goals with “at” (buildings, events) and “in” (regions); “to” marks direction with motion verbs.', 'She drove to the airport — the motion verb “drive” licenses “to”.'],
      [/\bsuperior\s+than\b/gi, 'superior to', 'Latinate Comparative Complementation', 'Latinate comparatives (superior, inferior, prior, senior) select “to”, not analytic “than”.', 'This one is cheaper than that — the analytic comparative licenses “than”.'],
    ],
  },
  {
    re: /\b(an)\s+(european|university|universities|unique|user|users|uniform|unit|united|utensil|one|once|usual)\b/gid,
    target: 1,
    build(m) {
      const w = m[2];
      return {
        type: 'M:DET' as ErrantType,
        replacement: 'a',
        rule: 'Indefinite Article Allomorphy (Phonological Onset)',
        exp: `“${w}” begins with the consonant glide /j/ (“y-” sound), so the article allomorph is “a”, not “an”.`,
        cf: 'An hour passed in silence — /aʊ/ onset takes “an”.',
        conf: 0.96,
      };
    },
  },
  {
    re: /\b(a)\s+(?!(?:one|once|uni\w*|use\w*|usu\w*|euro\w*|euph\w*|utop\w*|utens\w*))([aeiou]\w*)/gid,
    target: 1,
    build(m) {
      const w = m[2];
      return {
        type: 'M:DET' as ErrantType,
        replacement: 'an',
        rule: 'Indefinite Article Allomorphy (Phonological Onset)',
        exp: `“${w}” begins with a vowel sound, so the article allomorph is “an”.`,
        cf: 'A university degree takes three years — /juː/ onset keeps “a”.',
        conf: 0.97,
      };
    },
  },
  {
    re: /\b(informations|advices|equipments|knowledges|feedbacks|softwares|homeworks|luggages|furnitures|researches|trainings)\b/gid,
    target: 1,
    build(m) {
      const v = m[1];
      const fix = v.replace(/s$/, '');
      return {
        type: 'R:NOUN:NUM' as ErrantType,
        replacement: fix,
        rule: 'Mass Noun Non-Pluralization',
        exp: `“${fix}” is a mass (uncountable) noun in standard English — it does not inflect for plural; quantity is expressed with a measure phrase (“three pieces of ${fix}”).`,
        cf: `I need some ${fix} before Friday.`,
        conf: 0.99,
      };
    },
  },
  {
    re: /\b(childs|womans|mans|peoples|fishes|tooths|feets|mouses|gooses|sheeps|deers)\b/gid,
    target: 1,
    build(m) {
      const v = m[1];
      const fixMap: Record<string, string> = {
        childs: 'children', womans: 'women', mans: 'men', peoples: 'people', fishes: 'fish',
        tooths: 'teeth', feets: 'feet', mouses: 'mice', gooses: 'geese', sheeps: 'sheep', deers: 'deer',
      };
      const fix = fixMap[v.toLowerCase()] || v;
      return {
        type: 'R:NOUN:NUM' as ErrantType,
        replacement: fix,
        rule: 'Irregular Plural Paradigm',
        exp: `Irregular plural: the plural of this noun is “${fix}”, not a regular ‑s inflection.`,
        cf: `Many ${fix} attended the ceremony.`,
        conf: 0.98,
      };
    },
  },
  {
    re: /\bme and\b((?:\s+(?:my|the|our|his|her|their|a))?(?:\s+[a-z]+){1,2})(?=\s+(?:go|goes|went|are|is|was|were|like|likes|will|can|do|does|did|live|lives))/gid,
    target: 0,
    build(m) {
      const rest = m[1].trim();
      return {
        type: 'R:WO' as ErrantType,
        replacement: cap(rest) + ' and I',
        rule: 'Politeness-Ordered Compound Subject with Nominative Case',
        exp: `In a compound subject, the standard register places the first-person pronoun last (“X and I”) and in the nominative case, since the whole phrase functions as the grammatical subject.`,
        cf: 'The teacher praised my sister and me — “me” is correct as an object.',
        conf: 0.88,
      };
    },
  },
  {
    re: /\b(what)\s+(means)\s+(this|that|the)\s+(\w+)\b/gid,
    target: 0,
    build(m) {
      const [w1, , det, noun] = m;
      return {
        type: 'R:WO' as ErrantType,
        replacement: `${cap(w1)} does ${det} ${noun} mean`,
        rule: 'Subject–Auxiliary Inversion in Wh-Interrogatives',
        exp: `Wh-questions require do-support: the auxiliary “does” carries tense and inverts with the wh-word, while the lexical verb stays in base form after the subject.`,
        cf: `It means a lot to me — declarative order uses “means” correctly.`,
        conf: 0.86,
      };
    },
  },
  {
    re: /\bexplain\s+me\b/gi,
    target: 0,
    build() {
      return {
        type: 'R:OTHER' as ErrantType,
        replacement: 'explain to me',
        rule: 'Dative Preposition Selection with explain',
        exp: '“Explain” does not license a dative object; the recipient appears in a “to”-phrase.',
        cf: 'She told me the answer — “tell” licenses the dative directly.',
        conf: 0.9,
      };
    },
  },
  {
    re: /\b(i|we|they|he|she)\s+(am|is|are)\s+agree\b/gid,
    target: 0,
    build(m) {
      return {
        type: 'R:OTHER' as ErrantType,
        replacement: `${cap(m[1])} agree`,
        rule: 'Verbal Predicate without Copula',
        exp: '“Agree” is a verb, not an adjective — it takes no copula.',
        cf: 'I am in agreement with you — the nominal takes the copula.',
        conf: 0.92,
      };
    },
  },
  {
    re: /\bdo\s+a\s+mistake\b/gi,
    target: 0,
    build() {
      return {
        type: 'R:OTHER' as ErrantType,
        replacement: 'make a mistake',
        rule: 'Light-Verb Collocation: make + mistake',
        exp: 'The light verb for “mistake” is “make”, not “do”.',
        cf: 'They did the right thing — “do” collocates with task nouns.',
        conf: 0.93,
      };
    },
  },
  {
    re: /\bsay\s+the\s+truth\b/gi,
    target: 0,
    build() {
      return {
        type: 'R:OTHER' as ErrantType,
        replacement: 'tell the truth',
        rule: 'Verbal Collocation: tell + truth',
        exp: 'The truth is “told”, not “said” — a fixed collocation.',
        cf: 'She said her name aloud — “say” takes direct speech.',
        conf: 0.93,
      };
    },
  },
];

export function runLocalRules(text: string): DiagnosticEdit[] {
  const found: any[] = [];
  const flat: any[] = [];

  for (const r of RULES) {
    if (r.list) {
      for (const [re, to, rule, exp, cf] of r.list) {
        re.lastIndex = 0;
        let m: RegExpExecArray | null;
        while ((m = re.exec(text))) {
          flat.push({
            start: m.index,
            end: m.index + m[0].length,
            original: text.slice(m.index, m.index + m[0].length),
            type: 'R:PREP' as ErrantType,
            replacement: matchCase(m[0], to),
            rule,
            exp,
            cf,
            conf: 0.9,
          });
          if (re.lastIndex === m.index) re.lastIndex++;
        }
      }
      continue;
    }

    const rx = r.re;
    if (!rx || !r.build) continue;
    rx.lastIndex = 0;
    let m: RegExpExecArray | null;
    let guard = 0;
    while ((m = rx.exec(text)) && guard++ < 60) {
      const b = r.build(m);
      if (!b) continue;
      const sp = spanFor(m, r.target);
      if (!sp) continue;
      found.push({
        ...b,
        start: sp[0],
        end: sp[1],
        original: text.slice(sp[0], sp[1]),
      });
      if (rx.lastIndex === m.index) rx.lastIndex++;
    }
  }

  const all = found.concat(flat);
  all.sort((a, b) => a.start - b.start || (b.end - b.start) - (a.end - a.start));
  const edits: DiagnosticEdit[] = [];
  let lastEnd = -1;

  for (const e of all) {
    if (e.start >= lastEnd) {
      edits.push({
        id: edits.length,
        span: {
          start_char: e.start,
          end_char: e.end,
          original_text: e.original,
        },
        replacement: matchCase(e.original, e.replacement),
        errant_type: e.type,
        linguistic_rule: e.rule,
        explanation: e.exp,
        counterfactual_example: e.cf,
        confidence: Math.min(0.99, e.conf + Math.random() * 0.008),
        critic_verified: true,
        accepted: true,
      });
      lastEnd = e.end;
    }
  }

  return edits;
}

// Dependency parsing helpers
export function tokenizeDeps(text: string): DepToken[] {
  const toks: DepToken[] = [];
  const rx = /[A-Za-z]+(?:'[a-z]+)?|[.,!?;:]/g;
  let m: RegExpExecArray | null;
  while ((m = rx.exec(text))) {
    toks.push({
      w: m[0],
      i: m.index,
      l: m[0].toLowerCase(),
      pos: 'NOUN',
      head: -1,
      label: '',
    });
  }
  return toks;
}

export function tagAll(toks: DepToken[]): DepToken[] {
  for (const t of toks) {
    const w = t.l;
    if (/^[.,!?;:]$/.test(t.w)) t.pos = 'PUNCT';
    else if (LEX.PREP.has(w)) t.pos = 'PREP';
    else if (LEX.CONJ.has(w)) t.pos = 'CONJ';
    else if (LEX.AUX.has(w)) t.pos = 'AUX';
    else if (LEX.DET.has(w)) t.pos = 'DET';
    else if (LEX.PRON.has(w)) t.pos = 'PRON';
    else if (LEX.ADV.has(w)) t.pos = 'ADV';
    else if (LEX.ADJ.has(w)) t.pos = 'ADJ';
    else if (LEX.VERB.has(w) || /(ed|ing)$/.test(w)) t.pos = 'VERB';
    else t.pos = 'NOUN';
  }

  toks.forEach((t, i) => {
    if (t.pos === 'NOUN' && !/s$/.test(t.l) && toks[i + 1] && toks[i + 1].pos === 'NOUN') {
      t.pos = 'ADJ';
    }
  });

  let root = toks.findIndex((t) => t.pos === 'VERB');
  if (root < 0) root = toks.findIndex((t) => t.pos === 'AUX');
  if (root < 0) root = 0;

  const nextNoun = (i: number) => {
    for (let j = i + 1; j < toks.length; j++) {
      if (toks[j].pos === 'NOUN') return j;
    }
    return null;
  };

  const lastPrep = (i: number) => {
    for (let j = i - 1; j >= 0; j--) {
      const p = toks[j].pos;
      if (p === 'VERB' || p === 'AUX' || p === 'NOUN') return null;
      if (p === 'PREP') return j;
    }
    return null;
  };

  toks.forEach((t, i) => {
    if (i === root) {
      t.head = -1;
      t.label = 'ROOT';
      return;
    }
    switch (t.pos) {
      case 'DET': {
        const n = nextNoun(i);
        t.head = n == null ? root : n;
        t.label = 'det';
        break;
      }
      case 'ADJ': {
        const n = nextNoun(i);
        t.head = n == null ? root : n;
        t.label = 'amod';
        break;
      }
      case 'PRON':
        t.head = root;
        t.label = i < root ? 'nsubj' : 'obj';
        break;
      case 'AUX':
        t.head = root;
        t.label = 'aux';
        break;
      case 'ADV':
        t.head = root;
        t.label = 'advmod';
        break;
      case 'PREP':
        t.head = root;
        t.label = t.l === 'by' ? 'agent' : 'prep';
        break;
      case 'CONJ': {
        const n = nextNoun(i);
        t.head = n == null ? root : n;
        t.label = 'cc';
        break;
      }
      case 'PUNCT':
        t.head = root;
        t.label = 'punct';
        break;
      case 'VERB':
        t.head = root;
        t.label = 'conj';
        break;
      default: {
        const p = toks[i - 1];
        if (p && p.pos === 'CONJ') {
          let q: number | null = null;
          for (let j = i - 2; j >= 0; j--) {
            if (toks[j].pos === 'NOUN') {
              q = j;
              break;
            }
          }
          if (q != null) {
            t.head = q;
            t.label = 'conj';
            break;
          }
        }
        const prep = lastPrep(i);
        if (prep != null) {
          t.head = prep;
          t.label = 'pobj';
        } else {
          t.head = root;
          t.label = i < root ? 'nsubj' : 'obj';
        }
      }
    }
  });

  return toks;
}

export const ARCC: Record<string, string> = {
  nsubj: '#1a6f8a', obj: '#177a4e', iobj: '#1a6f8a', prep: '#6a4fa3', pobj: '#6a4fa3', agent: '#6a4fa3',
  det: '#a19b8e', amod: '#8a857a', aux: '#c25a1e', neg: '#d92c35', advmod: '#6a4fa3', punct: '#c9c3b4',
  cc: '#a19b8e', conj: '#8a857a', ROOT: '#191813', dep: '#a19b8e',
};

export function morphNum(t: DepToken): string {
  return /s$/.test(t.l) && !/(ss|us|is)$/.test(t.l) ? 'Plur' : 'Sing';
}

export function morphOf(t: DepToken): string | null {
  if (t.pos === 'NOUN') return `Number=${morphNum(t)}`;
  if (t.pos === 'AUX') {
    const n = ['is', 'was', 'has', 'does', 'am', "isn't", "wasn't", "doesn't"].includes(t.l) ? 'Sing' : 'Plur';
    return `Number=${n} · Tense=${PAST.has(t.l) ? 'Past' : 'Pres'}`;
  }
  if (t.pos === 'VERB') {
    return PAST.has(t.l) || /ed$/.test(t.l)
      ? 'Tense=Past · VerbForm=Part'
      : `Number=${/s$/.test(t.l) ? 'Sing' : 'Plur'} · Tense=Pres`;
  }
  return null;
}

export function checkAgreement(toks: DepToken[]): { subj: string; sNum: string; verb: string; vNum: string; ok: boolean } | null {
  const root = toks.findIndex((t) => t.label === 'ROOT');
  if (root < 0) return null;
  const subj = toks.find((t, i) => t.label === 'nsubj' && i < root);
  if (!subj) return null;
  const sNum = subj.pos === 'PRON'
    ? (['i', 'you', 'he', 'she', 'it'].includes(subj.l) ? 'Sing' : 'Plur')
    : morphNum(subj);
  const auxes = toks.filter((t) => t.pos === 'AUX');
  const verb = auxes.length ? auxes[auxes.length - 1] : toks[root];
  if (!verb) return null;
  const vNum = verb.pos === 'AUX'
    ? (['is', 'was', 'has', 'does', 'am', "isn't", "wasn't", "doesn't"].includes(verb.l) ? 'Sing' : 'Plur')
    : (/s$/.test(verb.l) && !/(ss|us|is)$/.test(verb.l) ? 'Sing' : 'Plur');
  if (verb.pos !== 'AUX' && verb.pos !== 'VERB') return null;
  return { subj: subj.w, sNum, verb: verb.w, vNum, ok: sNum === vNum };
}
