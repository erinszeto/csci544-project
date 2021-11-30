import rouge_papier_v2
import rouge_papier_v2.wrapper as wrapper
import os
import numpy as np
import pandas as pd


def get_rouge(paths, config_path):
    config_text = rouge_papier_v2.make_simple_config_text(paths)
    of = open(config_path,'w')
    of.write(config_text)
    of.close()

    df, avgfs, conf = rouge_papier_v2.compute_rouge(config_path, max_ngram=2, lcs=True)
    df['data_ids'] = pd.Series(np.array(uttnames),index=df.index)
    
    return df, avgfs, conf


if __name__ == '__main__':
    model_summ_path = '../data/model-summaries/attentive-context-summaries/test-summaries/'
    abs_summ_path = '../data/extractive-summaries/test/'
    ext_summ_path = '../data/abstraction/test/'

    abs_paths = []
    ext_paths = []
    uttnames = []

    directory = os.fsencode(model_summ_path)
    
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        uttnames.append(filename)
        abs_paths.append([abs_summ_path + filename, [model_summ_path + filename]])
        ext_paths.append([ext_summ_path + filename, [model_summ_path + filename]])

    uttnames.append('Average')
    df, avgfs, output = get_rouge(abs_paths, './abs-config')
    of = open('../data/model-summaries/attentive-context-summaries/Rouge12L_attentive_context_abstractive.txt', 'w')
    of.write(output)
    of.close()

    df, avgfs, output = get_rouge(abs_paths, './ext-config')
    of = open('../data/model-summaries/attentive-context-summaries/Rouge12L_attentive_context_extractive.txt', 'w')
    of.write(output)
    of.close()


    
