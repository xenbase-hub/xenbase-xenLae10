#!/usr/bin/python3
import sys

filename_fa = sys.argv[1]
filename_base = '.'.join(filename_fa.split('.')[:-1])

seq_list = dict()
seq_h = ''
f_seq = open(filename_fa, 'r')
if filename_fa.endswith('.gz'):
    import gzip
    f_seq = gzip.open(filename_fa, 'rt')
    filename_base = '.'.join(filename_fa.replace('.gz', '').split('.')[:-1])

for line in f_seq:
    if line.startswith('>'):
        seq_h = line.strip().lstrip('>')
        # seq_h = line.strip().lstrip('>').split()[0]
        seq_list[seq_h] = []
    else:
        seq_list[seq_h].append(line.strip())
f_seq.close()

seq2h = dict()
for tmp_h in seq_list.keys():
    tmp_seq = ''.join(seq_list[tmp_h])
    if tmp_seq not in seq2h:
        seq2h[tmp_seq] = []
    seq2h[tmp_seq].append(tmp_h)

count_unique = 0
count_multi = 0

f_nr = open('%s_NR.fa' % filename_base, 'w')
f_nr_log = open('%s_NR.log' % filename_base, 'w')
for tmp_seq in seq2h.keys():
    name_list = [x.split('|')[0] for x in seq2h[tmp_seq]]
    gene_list = [x.split('|')[-1] for x in seq2h[tmp_seq]]
    h_list = sorted(seq2h[tmp_seq])

    name_count = dict()
    for tmp_name in name_list:
        if tmp_name != 'NA':
            if tmp_name not in name_count:
                name_count[tmp_name] = 0
            name_count[tmp_name] += 1

            # Xenopus_laevis specific criteria
            if tmp_name.endswith('.L') or tmp_name.endswith('.S'):
                name_count[tmp_name] += 5

    rep_name = h_list[0].split('|')[0]
    if len(name_count) > 0:
        rep_name = sorted(name_count.keys(), key=name_count.get)[-1]
    
    rep_h = ''
    for tmp_h in h_list:
        if rep_h == '':
            rep_h = tmp_h
        
        if tmp_h.startswith(rep_name):
            rep_h = tmp_h

    tmp_remark = 'NA'
    if len(set(gene_list)) == 1:
        tmp_remark = 'SameGene'
    else:
        tmp_remark = 'DiffGene'
    
    if len(set(name_list)) == 1:
        tmp_remark += ';SameName'
    else:
        tmp_remark += ';DiffName'
    
    f_nr.write('>%s\n%s\n' % (rep_h, "\n".join(seq_list[rep_h])))
    if len(h_list) > 1:
        f_nr_log.write('%s\t%s\t%s\n' % (tmp_remark, rep_h, ";;".join(h_list)))


f_nr_log.write('#total seq: %d\n' % len(seq_list))
f_nr_log.write('#total nr seq: %d\n' % len(seq2h))

f_nr_log.close()
f_nr.close()
