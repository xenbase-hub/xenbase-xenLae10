#!/usr/bin/python3
import sys

filename_fa = sys.argv[1]

seq_list = dict()
seq_h = ''
f_seq = open(filename_fa, 'r')
if filename_fa.endswith('.gz'):
    import gzip
    f_seq = gzip.open(filename_fa, 'rt')

for line in f_seq:
    if line.startswith('>'):
        seq_h = line.strip().lstrip('>')
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
filename_base = '.'.join(filename_fa.split('.')[:-1])

f_nr = open('%s_NR.fa' % filename_base, 'w')
f_nr_log = open('%s_NR.log' % filename_base, 'w')
for tmp_seq in seq2h.keys():
    rep_h = ''
    h_list = sorted(seq2h[tmp_seq])

    tmp_name_list = []
    for tmp_h in h_list:
        if rep_h == '':
            rep_h = tmp_h

        tmp_name = tmp_h.split()[0].split('|')[0]
        tmp_type = tmp_h.split()[1]
        tmp_name_list.append(tmp_name)

        # Xenopus_laevis specific criteria
        if tmp_name.endswith('.L') or tmp_name.endswith('.S'):
            rep_h = tmp_h
        if tmp_name != 'NA':
            if tmp_type.find('main') >= 0:
                rep_h = tmp_h

    f_nr.write('>%s\n%s\n' % (rep_h, "\n".join(seq_list[rep_h])))
    if len(seq2h[tmp_seq]) > 1:
        if len(set(tmp_name_list)) == 1:
            f_nr_log.write('Duplicate\t%s\t%s\n' %
                           (rep_h, ';;'.join(h_list)))
        else:
            f_nr_log.write('MultiName\t%s\t%s\n' %
                           (rep_h, ';;'.join(h_list)))
        count_multi += 1
    else:
        count_unique += 1

f_nr_log.write('#total seq: %d\n' % len(seq_list))
f_nr_log.write('#total nr seq: %d\n' % len(seq2h))
f_nr_log.write('#unique seq: %d, redundant seq:%d\n' %
               (count_unique, count_multi))
f_nr_log.close()
f_nr.close()
