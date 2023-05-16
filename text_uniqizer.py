import spacy
import random
from nltk.corpus import wordnet
from textblob import TextBlob
from transformers import T5ForConditionalGeneration, T5Tokenizer

nlp = spacy.load('en_core_web_sm')  # загружаем модель для английского языка

class TextUniqizer:
    def __init__(self, synonymize_percent=0, paraphrase_percent=0):
        self.synonymize_percent = synonymize_percent
        self.paraphrase_percent = paraphrase_percent
        self.model = T5ForConditionalGeneration.from_pretrained("t5-base")
        self.tokenizer = T5Tokenizer.from_pretrained("t5-base")
        # TODO: Добавить поддержку различных языков
        # TODO: Добавить поддержку различных алгоритмов уникализации
        # TODO: Добавить обработку исключений и валидацию входных данных

    def uniqize(self, text, category=None):
        doc = nlp(text)  # создаем объект Doc spaCy
        uniq_words = []
        for token in doc:
            # только для слов, являющихся существительными, глаголами, прилагательными или наречиями
            if token.pos_ in ['NOUN', 'VERB', 'ADJ', 'ADV']:
                if random.randint(0, 100) < self.synonymize_percent:
                    synonyms = wordnet.synsets(token.text)
                    if synonyms:
                        # выбираем случайный синоним из списка
                        synonym = random.choice(synonyms).lemmas()[0].name()
                        uniq_words.append(synonym)
                    else:
                        uniq_words.append(token.text)
                else:
                    uniq_words.append(token.text)
            else:
                uniq_words.append(token.text)
        uniq_text = ' '.join(uniq_words)

        # использование TextBlob для дополнительной перефразировки предложений
        blob = TextBlob(uniq_text)
        uniq_sentences = []
        for sentence in blob.sentences:
            if random.randint(0, 100) < self.paraphrase_percent:
                sentence = str(sentence)
                paraphrases = self.paraphrase(sentence)
                uniq_sentences.append(random.choice(paraphrases)) # выбираем один случайный вариант перефразирования
            else:
                uniq_sentences.append(str(sentence))
        uniq_text = ' '.join(uniq_sentences)

        return uniq_text

    def set_synonymize_percent(self, percent):
        self.synonymize_percent = percent

    def set_paraphrase_percent(self, percent):
        self.paraphrase_percent = percent

    def paraphrase(self, sentence: str) -> str:
        text =  "paraphrase: " + sentence
        max_len = 256

        encoding = self.tokenizer.encode_plus(text, pad_to_max_length=True, return_tensors="pt")
        input_ids, attention_masks = encoding["        input_ids"].to("cuda"), encoding["attention_mask"].to("cuda")

        outputs = self.model.generate(
            input_ids=input_ids, attention_mask=attention_masks,
            max_length=max_len,
            do_sample=True,
            top_k=120,
            top_p=0.95,
            early_stopping=True,
            num_return_sequences=5
        )

        paraphrases = []
        for output in outputs:
            sequence = self.tokenizer.decode(output, skip_special_tokens=True)
            paraphrases.append(sequence)

        return paraphrases
