import spacy 
nlp=spacy.load("en_core_web_sm")
def summarize_text(text,num_sentences=3):
  doc=nlp(text)
  #extract the most important text
  top_sentences = [str(sent) for sent in sorted(doc.sents, key=lambda s: s.score_,reverse=True)[:num_sentences]]
  summary = " ".join(top_sentences)
  return summary