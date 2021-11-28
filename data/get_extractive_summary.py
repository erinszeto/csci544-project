import json
#from nltk.tokenize import sent_tokenize, word_tokenize
#import re
import os
from progressbar import ProgressBar

def readFile(file):
    f = open(file)
    contents = json.load(f)
    f.close()

    return contents

def getSummary(input_file, label_file):
    summary = []
    for i in range(len(input_file['inputs'])):
        if label_file['labels'][i] == 1:
            summary.append(input_file['inputs'][i]['text'])
            
    summary = ' '.join(summary)
    return summary

def writeFile(out_path, summary):
    with open(out_path, 'w') as f:
        f.write(summary)
    f.close()

def main():
    input_path = 'input/test'
    input_files = [pos_json for pos_json in os.listdir(input_path) if pos_json.endswith('.json')]
    
    label_path = 'labels/test'
    #label_files = [pos_json for pos_json in os.listdir(label_path) if pos_json.endswith('.json')]

    pbar = ProgressBar()

    for d in pbar(input_files):
        input_file = f'{input_path}/{d}'
        label_file = f'{label_path}/{d}'
        
        input_file = readFile(input_file)
        label_file = readFile(label_file)

        doc_id = input_file['id']
        out_path = f'extractive-summaries/test/{doc_id}.txt'
        
        summary = getSummary(input_file, label_file)
        writeFile(out_path, summary)

if __name__ == "__main__":
    main()