import json
from nltk.tokenize import sent_tokenize, word_tokenize
import re
import os
from progressbar import ProgressBar

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

def writeFile(out_path, summary):
    with open(out_path, 'w') as f:
        f.write(summary)
    f.close()

def writeSummary(file, out_path, source='crs'):
    raw_file = readFile(file)
    doc_id = raw_file['id']
    out_path = out_path + f'{doc_id}.txt'

    if source == 'crs':
        summary = getSummary(raw_file)
    else:
        summary = getHighlight(raw_file)

    writeFile(out_path, summary)

def main():
    crs_path = 'gov-report/crs'
    crs_files = [pos_json for pos_json in os.listdir(crs_path) if pos_json.endswith('.json')]

    gao_path = 'gov-report/gao'
    gao_files = [pos_json for pos_json in os.listdir(gao_path) if pos_json.endswith('.json')]

    valid_files = [jsonf for jsonf in os.listdir('labels/valid') if jsonf.endswith('.json')]
    test_files = [jsonf for jsonf in os.listdir('labels/test') if jsonf.endswith('.json')]

    pbar = ProgressBar()
    for d in pbar(valid_files):
        out_path = 'abstraction/valid/'
        if d in crs_files:
            file = f'{crs_path}/{d}'

            writeSummary(file, out_path, 'crs')
        else:
            file = f'{gao_path}/{d}'

            writeSummary(file, out_path, 'gao')

    for d in pbar(test_files):
        out_path = 'abstraction/test/'
        if d in crs_files:
            file = f'{crs_path}/{d}'

            writeSummary(file, out_path, 'crs')
        else:
            file = f'{gao_path}/{d}'

            writeSummary(file, out_path, 'gao')

if __name__ == "__main__":
    main()
