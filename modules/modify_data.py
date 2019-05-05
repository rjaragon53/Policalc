from googletrans import Translator
import preprocessor as pr
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


class modify_data:

    def clean_tweet(self, tweet):

        pr.set_options(pr.OPT.URL, pr.OPT.MENTION, pr.OPT.HASHTAG,
                       pr.OPT.EMOJI, pr.OPT.SMILEY, pr.OPT.RESERVED)

        tweet = pr.clean(tweet).replace('&amp', "").strip().encode(
            'ascii', 'ignore').decode('utf-8')

        return tweet

    def translate(self, text):

        trans = Translator()
        temp = trans.translate(text)
        new_text = temp.text

        return new_text

    def remove_stopwords(self, text):

        text = re.sub(r'[^\w]', ' ', text)
        stop_words = set(stopwords.words('english'))
        word_tokens = word_tokenize(text)
        filtered_sentence = [word for word in word_tokens if word not in stop_words]
        filtered_sentence = []

        for w in word_tokens:
            if w not in stop_words:
                filtered_sentence.append(w)

        text = ' '.join(filtered_sentence)

        return text
