#!/usr/bin/env python3
import os
import sys
import gzip

usage_mesg = '  Usage: %s <faa file> <gff file> <output name>' % sys.argv[0]

# filename_base = 'XENTR_xenTro10.NCBI_104'
# filename_gff = 'raw/GCF_000004195.4_UCB_Xtro_10.0_genomic.gff.gz'
# filename_fa = 'raw/GCF_000004195.4_UCB_Xtro_10.0_protein.faa.gz'

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


f_log = open('%s.prot_all.log' % filename_base, 'w')

prot_info = dict()

f_gff = open(filename_gff, 'r')
if filename_gff.endswith('.gz'):
    f_gff = gzip.open(filename_gff, 'rt')

for line in f_gff:
    if line.startswith('#'):
        continue
    tokens = line.strip().split("\t")
    tmp_type = tokens[2]
    if tmp_type != 'CDS':
        continue

    tx_id = 'NA'
    prot_id = 'NA'
    xb_gene_id = 'NA'
    ncbi_gene_id = 'NA'
    gene_symbol = 'NA'
    for tmp in tokens[8].split(';'):
        if tmp.startswith('Parent='):
            tx_id = tmp.split('=')[1].replace('rna-', '')
        if tmp.startswith('protein_id='):
            prot_id = tmp.split('=')[1]
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

    if gene_symbol == 'prss8l.5.S loc108703873':
        f_log.write("GeneSymbol(%s): %s -> " % (ncbi_gene_id, gene_symbol))
        gene_symbol = 'prss8l.5.S'
        f_log.write(" %s\n" % gene_symbol)

    if prot_id not in prot_info:
        prot_info[prot_id] = {'name': gene_symbol, 'tx_id': tx_id,
                              'xb_gene_id': xb_gene_id,
                              'ncbi_gene_id': ncbi_gene_id}
f_gff.close()

is_log = -1

f_fa = open(filename_fa, 'r')
if filename_fa.endswith('.gz'):
    f_fa = gzip.open(filename_fa, 'rt')

f_out = open('%s.prot_all.fa' % filename_base, 'w')
f_name = open('%s.prot_names.tsv' % filename_base, 'w')
for line in f_fa:
    if line.startswith('>'):
        tmp_id = line.strip().split()[0].lstrip('>')
        tmp_name = " ".join(line.strip().split()[1:])
        tmp_name = tmp_name.replace('[Xenopus laevis]', '').strip()

        # stop if there is no protein_id in the GFF3 file
        if tmp_id not in prot_info:
            sys.stderr.write('No_ID: %s\n' % tmp_id)
            sys.exit(1)
        else:
            tmp_p = prot_info[tmp_id]
            tmp_h = '%s|%s|%s|GeneID:%s xb_gene_id=%s' %\
                    (tmp_p['name'], tmp_id, tmp_p['tx_id'],
                     tmp_p['ncbi_gene_id'], tmp_p['xb_gene_id'])

            f_name.write('%s\tGeneID:%s\t%s\t%s\t%s\n' %
                         (tmp_id, tmp_p['ncbi_gene_id'],
                          tmp_p['xb_gene_id'], tmp_p['name'], tmp_name))

            if tmp_p['tx_id'].find('_') < 0:
                is_log = 1
                sys.stderr.write('tx_id error: %s\n' % tmp_h)
                f_log.write('tx_id error: >%s\n' % tmp_h)
                f_out.write('>%s\n' % tmp_h)
            elif tmp_p['ncbi_gene_id'] == 'NA':
                is_log = 1
                sys.stderr.write('ncbi_gene_id error: %s\n' % tmp_h)
                f_log.write('ncbi_gene_id error: >%s\n' % tmp_h)
                f_out.write('>%s\n' % tmp_h)
            else:
                is_log = -1
                f_out.write('>%s\n' % tmp_h)
    else:
        # if is_log > 0:
        #    f_log.write('%s\n' % line.strip())

        f_out.write('%s\n' % line.strip())
f_fa.close()
f_log.close()
f_out.close()
