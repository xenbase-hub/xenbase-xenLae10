#!/usr/bin/env python3
import os
import sys
import gzip

usage_mesg = '  Usage: %s <fna file> <gff file> <output name>' % sys.argv[0]

if len(sys.argv) != 4:
    sys.stderr.write('\n%s\n\n' % usage_mesg)
    sys.exit(1)


def check_file(tmp_filename):
    if not os.access(tmp_filename, os.R_OK):
        sys.stderr.write('%s is not available. Stop.\n' % tmp_filename)
        sys.exit(1)

filename_fa = sys.argv[1]
filename_gff = sys.argv[2]
filename_base = sys.argv[3]

check_file(filename_fa)
check_file(filename_gff)


f_log = open('%s.tx_all.log' % filename_base, 'w')

tx_info = dict()

f_gff = open(filename_gff, 'r')
if filename_gff.endswith('.gz'):
    f_gff = gzip.open(filename_gff, 'rt')

target_types = ['mRNA', 'rRNA', 'snRNA', 'lnc_RNA', 'transcript', 'scRNA',
                'primary_transcript', 'snoRNA', 'guide_RNA', 'telomerase_RNA']

for line in f_gff:
    if line.startswith('#'):
        continue
    tokens = line.strip().split("\t")
    tmp_type = tokens[2]

    if tmp_type not in target_types:
        continue

    tx_id = 'NA'
    xb_gene_id = 'NA'
    ncbi_gene_id = 'NA'
    gene_symbol = 'NA'
    for tmp in tokens[8].split(';'):
        if tmp.startswith('transcript_id='):
            tx_id = tmp.split('=')[1]
        if tmp.startswith('gene='):
            gene_symbol = tmp.split('=')[1]
        if tmp.startswith('Dbxref='):
            for tmp2 in tmp.split('=')[1].split(','):
                if tmp2.startswith('GeneID:'):
                    ncbi_gene_id = tmp2.split(':')[1]
                if tmp2.startswith('Xenbase:'):
                    xb_gene_id = tmp2.split(':')[1]
    
    if gene_symbol.find('provis') >= 0:
        f_log.write("GeneSymbol(%s): %s -> " % (ncbi_gene_id, gene_symbol))
        gene_symbol = gene_symbol.replace(' [provisonal]', '')
        gene_symbol = gene_symbol.replace('-provisional', '')
        gene_symbol = gene_symbol.replace('provisional', '')
        f_log.write(" %s\n" % gene_symbol)

    if gene_symbol == 'XFG 5-1':
        # https://www.xenbase.org/xenbase/gene/showgene.do?method=display&geneId=5723273
        f_log.write("GeneSymbol(%s): %s -> " % (ncbi_gene_id, gene_symbol))
        gene_symbol = 'znf568.L'
        f_log.write(" %s\n" % gene_symbol)

    if tx_id not in tx_info:
        tx_info[tx_id] = {'name': gene_symbol, 'xb_gene_id': xb_gene_id, 'ncbi_gene_id': ncbi_gene_id, 'type': tmp_type}
f_gff.close()

is_log = -1

f_fa = open(filename_fa, 'r')
if filename_fa.endswith('.gz'):
    f_fa = gzip.open(filename_fa, 'rt')

is_print = 1
f_out = open('%s.tx_all.fa' % filename_base, 'w')
for line in f_fa:
    if line.startswith('>'):
        tmp_id = line.strip().split()[0].lstrip('>')

        # stop if there is no transcript_id in the GFF3 file
        if tmp_id not in tx_info:
            sys.stderr.write('No_ID: %s\n' % tmp_id)
            sys.exit(1)
        else:
            tmp_tx = tx_info[tmp_id]
            tmp_h = '%s|%s|GeneID:%s xb_gene_id=%s type=%s' %\
                    (tmp_tx['name'], tmp_id, tmp_tx['ncbi_gene_id'], 
                     tmp_tx['xb_gene_id'], tmp_tx['type'])

            if tmp_tx['ncbi_gene_id'] == 'NA':
                is_log = 1
                is_print = 1
                sys.stderr.write('ncbi_gene_id error: %s\n' % tmp_h)
                f_log.write('ncbi_gene_id error: >%s\n' % tmp_h)
                f_out.write('>%s\n' % tmp_h)
            elif tmp_tx['type'] == 'guide_RNA':
                sys.stderr.write('Guide RNA: %s\n' % tmp_h)
                f_log.write('>%s\n' % tmp_h)
                is_print = -1
            else:
                is_log = -1
                is_print = 1
                f_out.write('>%s\n' % tmp_h)
    else:
        # if is_log > 0:
        #    f_log.write('%s\n' % line.strip())
        if is_print > 0:
            f_out.write('%s\n' % line.strip())
        else:
            f_log.write('%s\n' % line.strip())
f_fa.close()
f_log.close()
f_out.close()
