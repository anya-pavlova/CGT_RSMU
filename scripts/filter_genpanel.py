import argparse
import pandas as pd

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("table", help="Path to table to be filtered")
    parser.add_argument("genpanel", help="Path to genpanel table")
    parser.add_argument("out", help="Output table path")

    args = parser.parse_args()

    table = pd.read_excel(args.table, sheet_name="All")
    genpanel = pd.read_csv(args.genpanel, sep="\t", index_col=False)

    gene_id_filter = table["gene_refgene"].isin(genpanel["Gene ID"])
    ensembl_filter = table["Gene.ensGene"].isin(genpanel["Ensembl"])
    combined_filter = gene_id_filter | ensembl_filter

    result = table[combined_filter]
    with pd.ExcelWriter(args.out) as writer:
        result.to_excel(writer, na_rep='.', index=False, sheet_name="All")
