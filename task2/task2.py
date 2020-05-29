# https://stepik.org/lesson/37845/step/1?unit=18887
# https://github.com/dialogue-evaluation/morphoRuEval-2017

import xmltodict
from collections import Counter
import operator


def opcorpora_dict_builder(data):

    tags_opcorpora = {
                      'ADVB': 'ADV', 
                      'UNKN': 'NI', 
                      'GRND': 'V', 
                      'PRCL': 'ADV', 
                      'PREP': 'PR', 
                      'ADJS': 'A', 
                      'PRTS': 'V', 
                      'INFN': 'V', 
                      'VERB': 'V', 
                      'LATN': 'NI',
                      'ADJF': 'A', 
                      'PNCT': 'NI', 
                      'PRTF': 'V', 
                      'NOUN': 'S', 
                      'INTJ': 'ADV', 
                      'SYMB': 'NI',
                      'PRED': 'NI', 
                      'COMP': 'A', # A or NI
                      'NUMB': 'NI',
                      'CONJ': 'CONJ', 
                      'ROMN': 'NI',
                      'NUMR': 'NI', 
                      'NPRO': 'NI' # NI or S
                     }

    tokens_out = {}
    data_in = xmltodict.parse(data)
    for text in data_in['annotation']['text']:

        if text['paragraphs'] is None:
            continue
        text_paragraph = text['paragraphs']['paragraph']
        if not isinstance(text_paragraph, list):
            text_paragraph = [text_paragraph]

        for paragraph in text_paragraph:

            paragraph_sentence = paragraph['sentence']
            if not isinstance(paragraph_sentence, list):
                paragraph_sentence = [paragraph_sentence]

            for sentence in paragraph_sentence:

                sentence_token = sentence['tokens']['token']
                if not isinstance(sentence_token, list):
                    sentence_token = [sentence_token]

                for token in sentence_token:

                    lemma = token['tfr']['v']['l']['@t']
                    tag = token['tfr']['v']['l']['g']
                    tag = tag[0]['@v'] if isinstance(tag, list) else tag['@v']

                    if tag not in tags_opcorpora:
                        continue
                    tag = tags_opcorpora[tag]

                    if tag == 'NI':
                        continue

                    token_value = token['@text'].lower().replace(u'ё', u'е')
                    if token_value not in tokens_out:
                        tokens_out[token_value] = []
                    tokens_out[token_value].append([lemma, tag])

    return tokens_out


def gikrya_dict_builder(data):

    tags_gikrya = {
                   'ADV': 'ADV', 
                   'H': 'ADV', 
                   'NUM': 'NI', 
                   'INTJ': 'ADV', 
                   'ADP': 'PR', 
                   'PUNCT': 'NI', 
                   'NOUN': 'S', 
                   'PRON': 'NI', 
                   'VERB': 'V', 
                   'CONJ': 'CONJ', 
                   'PART': 'ADV', 
                   'ADJ': 'A', 
                   'DET': 'NI'
                  }

    tokens_out = {}
    texts = data.split('\n\n')
    for text in texts:
        text_line = text.split('\n')
        for line in text_line:
            line_info = line.split('\t')
            if len(line_info) < 4:
                continue
                    
            lemma = line_info[2]
            tag = tags_gikrya[line_info[3]]
            if tag == 'NI':
                continue

            token_value = line_info[1].lower().replace(u'ё', u'е')
            if token_value not in tokens_out:
                tokens_out[token_value] = []
            tokens_out[token_value].append([lemma, tag])

    return tokens_out



# with open('train/annot.opcorpora.no_ambig.nonmod.xml', 'r', encoding="utf-8") as myfile:
#     data = myfile.read()
# tokens = opcorpora_dict_builder(data)

# with open('train/annot.opcorpora.no_ambig.xml', 'r', encoding="utf-8") as myfile:
#     data = myfile.read()
# tokens = opcorpora_dict_builder(data)

with open('train/gikrya_fixed.txt', 'r', encoding="utf-8") as myfile:
    data = myfile.read()
tokens = gikrya_dict_builder(data)


for i in tokens.keys():
    if len(tokens[i]) == 1:
        continue
    buf = [f"{i[0]} {i[1]}" for i in tokens[i]]
    buf = Counter(buf)
    if len(buf) == 1:
        tokens[i] = [tokens[i][0]]
        continue
    buf = sorted(buf.items(), key=operator.itemgetter(1))
    buf.reverse()
    tokens[i] = [i[0].split(' ') for i in buf]

# print("Count tokens:", len(tokens))


with open('test/dataset_37845_1.txt', 'r', encoding="utf-8") as myfile:
    data = myfile.read()

data = data.replace('.', '').replace(',', '').replace('!', '').replace('?', '')
data = data.split('\n')

texts = []
for i in range(len(data)):
    buf = [j for j in data[i].split(" ") if j]
    if not buf:
        continue
    texts.append(buf)



for text in texts:
    out = ""
    for token in text:
        token_norm = token.lower().replace(u'ё', u'е')

        lemma = token_norm
        tag = "NI"
        if token_norm in tokens:
            lemma = tokens[token_norm][0][0]
            tag = tokens[token_norm][0][1]
        out += f"{token}{{{lemma}={tag}}} "

    print(out[0:len(out)-1])
