import re
from collections import Counter

STOP = {'the','a','an','is','are','was','were','be','of','to','in','on','at','by','for','from','with','our','their','this','that','and','or','but','it','we','they','i','near'}
IRREG = {'noises':'noise','residents':'resident','disturbing':'disturb','disturbed':'disturb','playing':'play','played':'play','drilling':'drill','honking':'honk','elderly':'elderly'}

def tokenize(text): return re.findall(r"[a-z]+(?:'[a-z]+)?", text.lower())
def lemma(w):
    if w in IRREG: return IRREG[w]
    for suffix in ('ies','ing','ed','es','s'):
        if w.endswith(suffix) and len(w)>len(suffix)+2: return w[:-len(suffix)]+('y' if suffix=='ies' else '')
    return w
def preprocess(text): return ' '.join(lemma(w) for w in tokenize(text) if w not in STOP)
def sentiment(text):
    words=set(tokenize(text)); neg={'unbearable','disturbing','disturbance','impossible','loud','excessive','problem','suffering','angry','continuous','unable'}; pos={'acceptable','improved','quiet','resolved','better','pleasant'}
    n,p=len(words&neg),len(words&pos)
    return ('Negative',min(.98,.65+.05*n)) if n>p else ('Positive',min(.95,.65+.05*p)) if p>n else ('Neutral',.62)
def severity(text):
    t=text.lower(); score=2*any(w in t for w in ('extremely','unbearable','impossible to sleep','dangerous','emergency'))+any(w in t for w in ('every night','all night','continuous','midnight','1 am','2 am','sleep','hospital','school','elderly','unable to sleep','very loud'))
    return ('CRITICAL' if score>=3 else 'HIGH' if score>=2 else 'MEDIUM' if score else 'LOW',min(.96,.58+score*.1))
def analyze(text, model=None, vectorizer=None):
    clean=preprocess(text); source,confidence=('Other',.5)
    if model is not None and vectorizer is not None:
        probs=model.predict_proba(vectorizer.transform([clean or text.lower()]))[0]; idx=probs.argmax();source=str(model.classes_[idx]);confidence=float(probs[idx])
    else:
        t=text.lower()
        rules=[('Vehicle Horn',('horn','honking','honk')),('Loud Music',('music','dj','speaker','band','song')),('Construction',('construction','drilling','drill','hammer','building site')),('Industrial',('factory','industrial','generator','plant machinery')),('Religious/Event',('temple','mosque','prayer','wedding','festival')),('Animals',('dog','barking','bark','kennel')),('Traffic',('traffic','vehicles','cars','buses','road noise')),('Neighbourhood',('neighbour','neighbor','party','society','restaurant'))]
        for label,terms in rules:
            if any(w in t for w in terms): source,confidence=label,.65;break
    sent,sc=sentiment(text); sev,sv=severity(text); t=text.lower()
    urgent=sev=='CRITICAL' or any(w in t for w in ('hospital','emergency','every night','all night','midnight','unable to sleep','extremely loud'))
    words=Counter(w for w in clean.split() if len(w)>2); keys=[w for w,_ in words.most_common(6)]
    vocab={'Traffic':'traffic road vehicle engine bus truck','Construction':'construction drill hammer building machinery','Loud Music':'music dj speaker band song','Industrial':'factory industrial machine generator plant','Religious/Event':'temple mosque prayer wedding festival event','Neighbourhood':'neighbour neighbor party society restaurant','Animals':'dog bark animal bird kennel','Vehicle Horn':'horn honk'}
    hits=[w for w in vocab.get(source,'').split() if w in t]
    explanation='Detected terms: '+', '.join(hits[:4])+'.' if hits else 'Wording most closely matches training examples for this source.'
    if model is None: explanation='Local keyword fallback (model artifact unavailable); '+explanation
    return {'processed_text':clean,'noise_source':source,'source_confidence':round(confidence,3),'sentiment':sent,'sentiment_score':round(sc,3),'severity':sev,'severity_score':round(sv,3),'is_urgent':bool(urgent),'keywords':keys,'explanation':explanation}
