import rouge_papier_v2

def write_config(ext):
    path_data = [[path + '_abs.txt', [path + ext]]]
    config_text = rouge_papier_v2.make_simple_config_text(path_data)
        
    of = open(config_path, 'w')
    of.write(config_text)
    of.close()


def compute_rouge(doc_name):
    df, avgfs = rouge_papier_v2.compute_rouge(config_path, lcs=True)
    avg = df.iloc[-1:].to_dict("records")[0]
    
    return "Rouge-1 recall score: %f, Rouge-1 f-score: %f\n"\
    "Rouge-2 recall score:%f, Rouge-2 f-score:%f\n"\
    "Rouge-L recall score:%f, Rouge-L f-score:%f\n\n"%(
        avg['rouge-1-r'],avg['rouge-1-f'], avg['rouge-2-r'],avg['rouge-2-f'], avg['rouge-L-r'],avg['rouge-L-f'])


if __name__ == '__main__':
    docs = ['GAO-01-842', 'GAO-02-1054T', 'GAO-10-297T', 'GAO-10-420', 'GAO-16-36', 'GAO-18-608', 'R42129', 'R43066', 'RCED-98-242', 'RS20598']
    data_path = '../evaluation/distribution/haley/'
    config_path = './hold_config'
    output_path = data_path + 'output_scores.txt'

    out_file = open(output_path, 'w')

    for doc in docs:
        out_file.write("Document " + doc + ":\n")
        path = data_path + doc 
        
        out_file.write("Baseline ROUGE scores: \n")
        write_config('_base.txt')
        out_file.write(compute_rouge(doc))

        out_file.write("Attentive context model ROUGE scores: \n")
        write_config('_model.txt')
        out_file.write(compute_rouge(doc))
        out_file.write('\n')

    out_file.close()
    print("Done! :)")

