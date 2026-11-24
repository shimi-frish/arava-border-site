import os,sys
R=sys.argv[1]
for l in reversed(open(os.path.join(os.path.dirname(__file__),'moves.tsv'),encoding='utf-8').read().splitlines()):
    k,o,n=l.split('\t'); os.makedirs(os.path.dirname(os.path.join(R,o)),exist_ok=True); os.rename(os.path.join(R,n),os.path.join(R,o))
print('undone; restore MASTER from 99_Archive/qgz_backups/*BEFORE_hist_folders_reorg*')
