#!/usr/bin/env python3
import sys
import os

usage_mesg = "    %s <Xenbase GPI>" % sys.argv[0]

if len(sys.argv) != 2:
    sys.stderr.write("\n%s\n\n" % usage_mesg)
    sys.exit(1)

filename_tsv = sys.argv[1]

filename_base = os.path.basename(filename_tsv).replace('.raw.tsv.gz', '').replace('.raw.tsv', '')

filename_log = "%s.XENLA.log" % filename_base
filename_tbl = "%s.XENLA.gene_table.tsv" % filename_base
filename_up = "%s.XENLA.uniprot2gene.tsv" % filename_base

if not os.access(filename_tsv, os.R_OK):
    sys.stderr.write('%s is not available. Exit.\n' % filename_tsv)
    sys.exit(1)

f_tsv = open(filename_tsv, 'r', encoding='latin-1')
if filename_tsv.endswith('.gz'):
    import gzip
    f_tsv = gzip.open(filename_tsv, 'rt', encoding='latin-1')

f_tbl = open(filename_tbl, 'w')
f_up = open(filename_up, 'w')
f_log = open(filename_log, 'w')

uniprot_list = dict()
refseq_list = dict()
xb_id_list = dict()
symbol_list = dict()
gene_list = dict()

for line in f_tsv:
    if line.startswith('!'):
        continue
    tokens = line.split("\t")
    xb_gene_id = tokens[0].replace('Xenbase:', '')
    tmp_symbol = tokens[1]
    tmp_name = tokens[2]
    tmp_taxon = tokens[5]
    tmp_xref = 'NA'
    if tokens[9] != '':
        tmp_xref = tokens[9]

    # Check uniqueness of XB-GENE-ID
    if xb_gene_id in xb_id_list:
        sys.stderr.write("Duplicate XB ID: %s\n" % xb_gene_id)
        sys.exit(1)

    xb_id_list[xb_gene_id] = 1

    # only laevis
    if tmp_taxon == 'NCBITaxon:8355':
        if xb_gene_id not in gene_list:
            gene_list[xb_gene_id] = {'symbols': tmp_symbol, 
                                     'name':  tmp_name, 
                                     'refseq': [], 
                                     'uniprot': []}

        ## Duplicate gene symbols
        if tmp_symbol not in symbol_list:
            symbol_list[tmp_symbol] = [xb_gene_id]
        else:
            symbol_list[tmp_symbol].append(xb_gene_id)

        ncbi_gene_id_list = []
        uniprot_acc_list = []
        for tmp in tmp_xref.split('|'):
            if tmp.startswith('NCBI_Gene:'):
                tmp_ncbi_id = tmp.replace('NCBI_Gene:', 'GeneID:')
                ncbi_gene_id_list.append(tmp_ncbi_id)
                if tmp_ncbi_id not in refseq_list:
                    refseq_list[tmp_ncbi_id] = []
                refseq_list[tmp_ncbi_id].append(xb_gene_id)
                gene_list[xb_gene_id]['refseq'].append(tmp_ncbi_id)

            if tmp.startswith('UniProtKB:'):
                tmp_uniprot_id = tmp.split(':')[1]
                uniprot_acc_list.append(tmp_uniprot_id)
                if tmp_uniprot_id not in uniprot_list:
                    uniprot_list[tmp_uniprot_id] = []
                uniprot_list[tmp_uniprot_id].append(xb_gene_id)
                gene_list[xb_gene_id]['uniprot'].append(tmp_ncbi_id)
        
        tmp_refseq_str = 'NA'
        count_ncbi_ids = len(ncbi_gene_id_list)

        if count_ncbi_ids == 1:
            tmp_refseq_str = ncbi_gene_id_list[0]

            if tmp_name == '':
                tmp_name = 'NotAvailable'
                f_log.write("NoGeneName\t%s\t%s\t%s\n" % (xb_gene_id, tmp_symbol, tmp_xref))

        elif count_ncbi_ids == 0:
            f_log.write("NoRefSeqID\t%s\t%s\t%s\n" % (xb_gene_id, tmp_symbol, tmp_xref))

        else:
            f_log.write("MultiRefSeqID\t%s\t%s\t%s\n" % (xb_gene_id, tmp_symbol, tmp_xref))
            tmp_refseq_str = ','.join(sorted(ncbi_gene_id_list))

        tmp_uniprot_str = 'NA'
        if len(uniprot_acc_list) == 0:
            f_log.write("NoUniProtAcc\t%s\t%s\t%s\n" % (xb_gene_id, tmp_symbol, tmp_xref))
        else:
            tmp_uniprot_str = ','.join(sorted(uniprot_acc_list))
            for tmp_acc in uniprot_acc_list:
                f_up.write("%s\t%s\t%s\t%s\n" % (tmp_acc, tmp_refseq_str, xb_gene_id, tmp_symbol))

        f_tbl.write('%s\t%s\t%s\t%s\n' % \
                     (tmp_refseq_str, xb_gene_id, tmp_symbol, tmp_name))
f_tsv.close()

for tmp_ncbi_id, tmp_list in refseq_list.items():
    if len(tmp_list) > 1:
        f_log.write("RefSeqWithMultiXB\t%s\t%s\n" % (tmp_ncbi_id, ';'.join(sorted(tmp_list))))

for tmp_uniprot_id, tmp_list in uniprot_list.items():
    if len(tmp_list) > 1:
        f_log.write("UniProtWithMultiXB\t%s\t%s\n" % (tmp_uniprot_id, ';'.join(sorted(tmp_list))))

f_log.close()
f_tbl.close()
f_up.close()
