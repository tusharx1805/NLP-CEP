from app.services.nlp import preprocess,severity,sentiment,analyze
def test_preprocess_retains_intensifiers_and_negation():
    assert 'not' in preprocess('not extremely loud') and 'extremely' in preprocess('not extremely loud')
def test_severity_and_urgency_cues():
    assert severity('Extremely loud noise every night makes sleep impossible')[0] in ('HIGH','CRITICAL')
    assert analyze('Extremely loud music every night') ['is_urgent']
def test_sentiment():assert sentiment('Unbearable noise is disturbing residents')[0]=='Negative'
