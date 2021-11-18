import json
import argparse
from nltk.tokenize import sent_tokenize, word_tokenize
from rouge_score import rouge_scorer
import re
import os
from progressbar import ProgressBar

scorer = rouge_scorer.RougeScorer(['rouge1'], use_stemmer=True)
missing_data = []

def parse_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                            description=__doc__,
                            epilog='Example Usage: python label_generation.py -src crs -i 500 --punkt')

    parser.add_argument("-src", "--source", type=str, nargs=1, required=True, help="Pass 'crs' or 'gao' for extractive label generation")

    parser.add_argument("-i", "--index", type=int, nargs='+', default=0, help="Pass index number to start generating labels at")

    parser.add_argument("--punkt", default=False, action="store_true", help="Set if have not downloaded 'punkt' from nltk")

    args = parser.parse_args()

    return args

def readFile(file):
    f = open(file)
    contents = json.load(f)
    f.close()

    return contents

def getSummary(contents):
    summary = ' '.join([summary.lower() for summary in contents['summary']])
    sentences = sent_tokenize(summary)
    sentences_clean = []

    for sentence in sentences:
        sentence_clean = re.sub('([!?(–)—;-<->/])', r' \1 ', sentence)  # pad basic punctuation with whitespace
        sentence_clean = re.sub('.$', ' .', sentence_clean)  # pad ending period with whitespace
        sentence_clean = re.sub(' - - ', ' -- ', sentence_clean)  # cleaning up instances of --
        sentence_clean = re.sub(r'([0-9]) - ', r'\1-', sentence_clean)  # keeping number-word instances together
        sentence_clean = re.sub(', ', ' , ', sentence_clean)  # padding commas in sentences but not in numbers
        sentence_clean = re.sub('’', '\'', sentence_clean)  # replacing apostrophe font
        sentence_clean = re.sub(' +', ' ', sentence_clean).rstrip()  # remove double white spice and space at end
        sentences_clean.append(sentence_clean)

    tokens = word_tokenize(' '.join(sentences_clean))
    summary = ' '.join(tokens)
    summary = re.sub(' - - ', ' -- ', summary)

    return summary

def getHighlight(contents):
    #summary = ' '.join(contents['highlight'][1]['paragraphs'])
    summary = ' '.join([' '.join(summary['paragraphs']).lower() for summary in contents['highlight']])
    sentences = sent_tokenize(summary)
    sentences_clean = []

    for sentence in sentences:
        sentence_clean = re.sub('\(\d+\)', '', sentence)
        sentence_clean = re.sub('\(\w\)', '', sentence_clean)
        sentence_clean = re.sub('([!?(–)—;-<->/])', r' \1 ', sentence_clean)  # pad basic punctuation with whitespace
        sentence_clean = re.sub('.$', ' .', sentence_clean)  # pad ending period with whitespace
        sentence_clean = re.sub(' - - ', ' -- ', sentence_clean)  # cleaning up instances of --
        sentence_clean = re.sub(r'([0-9]) - ', r'\1-', sentence_clean)  # keeping number-word instances together
        sentence_clean = re.sub(', ', ' , ', sentence_clean)  # padding commas in sentences but not in numbers
        sentence_clean = re.sub('’', '\'', sentence_clean)  # replacing apostrophe font
        sentence_clean = re.sub(' +', ' ', sentence_clean).rstrip()  # remove double white spice and space at end
        sentences_clean.append(sentence_clean)

    tokens = word_tokenize(' '.join(sentences_clean))
    summary = ' '.join(tokens)
    summary = re.sub(' - - ', ' -- ', summary)

    return summary

def getSentences(contents):
    sentences = [' '.join(word_tokenize(sentence['text'])) for sentence in contents['inputs']]
    total_length = sum([len(sent) for sent in sentences])
    budget = 0.1*total_length

    return sentences,budget

def getNumSentences(contents):
    num_sentences = contents['inputs'][-1]['sentence_id']
    return num_sentences

def wordCount(sentence):
    return len(word_tokenize(sentence))

def labelGeneration(ref,sentences,budget):
    hyp = ''
    wc = 0
    picked = []
    highest_r1 = 0
    sid = -1

    while wc <= budget:
        for i in range(len(sentences)):
            score = scorer.score(hyp+sentences[i],ref)['rouge1'][2] ##fmeasure of ROUGE1
            if score > highest_r1:
                highest_r1 = score
                sid = i

        if (len(picked) > 5) and (picked[-1] == sid) and (picked[-2] == sid):
            break
        elif sid != -1:
            picked.append(sid)
            hyp = hyp+sentences[sid]
            wc += wordCount(sentences[sid])
        else:
            break

    picked = list(set(picked))
    #picked = list(dict.fromkeys(picked))

    return picked

def write_labelFile(out_path, doc_id, picked, num_sentences):
    labels = [0]*num_sentences
    for sid in picked:
        labels[sid] = 1

    output_file = {'id':doc_id, 'labels':labels}

    with open(out_path, 'w') as f:
        json.dump(output_file, f)

def getLabels(file, clean_file, out_path, source='crs'):
    raw_file = readFile(file)

    if source == 'crs':
        summary = getSummary(raw_file)
    else:
        summary = getHighlight(raw_file)

    contents = readFile(clean_file)
    sentences,budget = getSentences(contents)

    picked = labelGeneration(summary,sentences,budget)

    try:
        num_sentences = contents['inputs'][-1]['sentence_id']
        doc_id = contents['id']

        write_labelFile(out_path, doc_id, picked, num_sentences)
    except:
        missing_data.append(clean_file)

def main():
    args = parse_args()
    index = args.index
    source = args.source[0]

    if args.punkt:
        import nltk
        nltk.download('punkt')

    if source == 'crs':
        path_to_json = 'gov-report/crs'
        json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]
        json_files.sort()

        label_path = 'labels/crs'
        label_files = [jsonf for jsonf in os.listdir(label_path) if jsonf.endswith('.json')]

        if len(index) > 1:
            json_files = json_files[index[0]:index[1]]
        else:
            ## start labeling files beginning at index
            json_files = json_files[index[0]:]

        pbar = ProgressBar()
        for d in pbar(json_files):
            file = path_to_json + '/' + d
            clean_file = f'formatted-data-and-code/formatted-data/crs/{d}'
            out_path = f'labels/crs/{d}'

            if d in label_files:
                continue

            getLabels(file, clean_file, out_path, source='crs')
    else:
        path_to_json = 'gov-report/gao'
        json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]
        json_files.sort()

        label_path = 'labels/gao'
        label_files = [jsonf for jsonf in os.listdir(label_path) if jsonf.endswith('.json')]

        if len(index) > 1:
            json_files = json_files[index[0]:index[1]]
        else:
            json_files = json_files[index[0]:]

        pbar = ProgressBar()
        for d in pbar(json_files):
            file = path_to_json + '/' + d
            clean_file = f'formatted-data-and-code/formatted-data/gao/{d}'
            out_path = f'labels/gao/{d}'

            if d in label_files:
                continue

            getLabels(file, clean_file, out_path, source='gao')


if __name__ == "__main__":
    main()
