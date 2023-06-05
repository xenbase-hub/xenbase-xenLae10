#!/usr/bin/env python3
import os
import sys
import gzip

usage_mesg = '  Usage: %s <cds fna file> <protein faa file (processed .prot_all.fa)>' % sys.argv[0]

if len(sys.argv) != 3:
    sys.stderr.write('\n%s\n\n' % usage_mesg)
    sys.exit(1)


def check_file(tmp_filename):
    if not os.access(tmp_filename, os.R_OK):
        sys.stderr.write('%s is not available. Stop.\n' % tmp_filename)
        sys.exit(1)


filename_cds_fa = sys.argv[1]
filename_prot_fa = sys.argv[2]

check_file(filename_cds_fa)
check_file(filename_prot_fa)


prot_info = dict()

f_prot = open(filename_prot_fa, 'r')
for line in f_prot:
    if line.startswith('>'):
        tmp_h = line.strip().lstrip('>')
        tmp_tokens = tmp_h.split('|')
        tmp_prot_id = tmp_tokens[1]
        prot_info[tmp_prot_id] = tmp_h
f_prot.close()

filename_base = filename_prot_fa.replace('.prot_all.fa', '')

f_out = open('%s.cds_all.fa' % filename_base, 'w')
f_log = open('%s.cds_all.log' % filename_base, 'w')

f_cds = open(filename_cds_fa, 'r')
if filename_cds_fa.endswith('.gz'):
    f_cds = gzip.open(filename_cds_fa, 'rt')

cds_list = dict()
is_print = 0
for line in f_cds:
    if line.startswith('>'):
        tmp_prot_id = 'NA'
        for tmp in line.strip().split():
            if tmp.startswith('[protein_id='):
                tmp_prot_id = tmp.split('=')[1].replace(']', '')

        if tmp_prot_id == 'NA':
            sys.stderr.write('NoID: %s\n' % line.strip())
            f_log.write('NoID: %s\n' % line.strip())
            is_print = -1
        else:
            is_print = 1
            if tmp_prot_id not in cds_list:
                cds_list[tmp_prot_id] = 1
                tmp_cds_id = 'cds-%s' % tmp_prot_id
                new_h = prot_info[tmp_prot_id]
                new_h = new_h.replace(tmp_prot_id, tmp_cds_id)
                f_out.write('>%s\n' % new_h)
            else:
                cds_list[tmp_prot_id] += 1
                f_log.write('MultiID: %s\n' % line.strip())

                tmp_cds_id = 'cds%d-%s' % (cds_list[tmp_prot_id], tmp_prot_id)
                new_h = prot_info[tmp_prot_id]
                new_h = new_h.replace(tmp_prot_id, tmp_cds_id)
                f_out.write('>%s\n' % new_h)
    elif is_print > 0:
        f_out.write("%s\n" % line.strip())
f_cds.close()
