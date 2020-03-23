import pandas as pd
import csv
from collections import defaultdict
import numpy as np
import argparse


def select_fields(d, keys):
    return {key: d[key] for key in keys}


def parse_tapes_info(info):
    result = {}
    for pair in info.split(";"):
        key_value = pair.split("=")
        if len(key_value) == 2:
            key, value = key_value
            if value == ".":
                value = np.nan
            result[key] = value
    return result


def read_tapes(tapes_file):
    if tapes_file == "-":
        return pd.DataFrame()

    tapes = []

    with open(tapes_file) as f:
        while True:
            line = f.readline()
            if line.startswith("##"):
                continue
            elif line.startswith("#"):
                header = line.lstrip("#").split("\t")
                break
            else:
                raise Exception("Can't parse file")

        csv_reader = csv.reader(f, delimiter="\t")
        for row in csv_reader:
            row = dict(zip(header, row))
            row = {
                **select_fields(row, ("CHROM", "POS", "REF", "ALT", "QUAL")),
                **parse_tapes_info(row["INFO"])
            }
            tapes.append(row)

    tapes = pd.DataFrame.from_dict(tapes)
    tapes["POS"] = pd.to_numeric(tapes["POS"])
    tapes.sort_values("POS", inplace=True)

    return tapes


def rename_header_duplicates(header):
    col_count = defaultdict(lambda: 0)
    new_header = []
    for col in header:
        if col_count[col] == 0:
            col_count[col] = 1
        else:
            new_col_name = "{}_{}".format(col, col_count[col])
            col_count[col] += 1
            col = new_col_name

        new_header.append(col)

    return new_header


def read_inter_var(inter_var_file):
    if inter_var_file == "-":
        return pd.DataFrame()

    with open(inter_var_file) as f:
        header = f.readline().split("\t")
        header = [col.strip() for col in header]

    inter_var = pd.read_csv(inter_var_file,
                            sep="\t",
                            index_col=False,
                            usecols=list(range(len(header))),
                            names=rename_header_duplicates(header),
                            skiprows=1)

    inter_var.replace('.', np.nan, inplace=True)
    inter_var["Start"] = pd.to_numeric(inter_var["Start"])
    inter_var["End"] = pd.to_numeric(inter_var["End"])
    inter_var.sort_values("Start", inplace=True)

    return inter_var


def get_value(*dict_col_pairs):
    for d, col in dict_col_pairs:
        if d is not None:
            if col in d:
                value = d[col]
                if not (value != value):
                    return value

    return np.nan


def merge(tapes_row, inter_var_row):
    return {
        "chr": get_value((inter_var_row, "Chr"), (tapes_row, "CHROM")),
        "start": get_value((inter_var_row, "Start"), (tapes_row, "POS")),
        "end": get_value((inter_var_row, "End"), (tapes_row, "POS")),
        "ref": get_value((inter_var_row, "Ref"), (tapes_row, "REF")),
        "alt": get_value((inter_var_row, "Alt"), (tapes_row, "ALT")),
        "localization_variant": get_value((inter_var_row, "Func.refGene"), (tapes_row, "Func.refGene")),
        "gene_refgene": get_value((inter_var_row, "Gene.refGene"), (tapes_row, "Gene.refGene")),
        "exon_replacement_type": get_value((inter_var_row, "ExonicFunc.refGene"), (tapes_row, "ExonicFunc.refGene")),
        "zygosity": get_value((inter_var_row, "Otherinfo")),
        "clinical_signature": get_value((tapes_row, "CLNSIG"), (inter_var_row, "CLNSIG")),
        "read_depth": get_value((tapes_row, "DP")),
        "Max-likelihood estimate of the first ALT allele frequency": get_value((tapes_row, "AF1")),
        "Allele frequency in gnomAD genome set": get_value((tapes_row, "gnomAD_genome_ALL"),
                                                           (inter_var_row, "gnomAD_genome_ALL")),
        "ID_in_db_hereditary_diseases": get_value((tapes_row, "CLNDISDB"), (inter_var_row, "CLNDISDB")),
        "associated_disease": get_value((tapes_row, "CLNDN"), (inter_var_row, "CLNDN")),
        "Review_status_in_ClinVar": get_value((tapes_row, "CLNREVSTAT"), (inter_var_row, "CLNREVSTAT")),
        "gene_associated_disease": get_value((tapes_row, "Disease_description.refGene"),
                                             (inter_var_row, "Disease_description.refGene")),
        "where_gene_expressed": get_value((tapes_row, "Expression(egenetics).refGene"),
                                          (inter_var_row, "Expression(egenetics).refGene")),
        "gnomad.genome.AFR(African/African American)": get_value((tapes_row, "gnomAD_genome_AFR"),
                                                                 (inter_var_row, "gnomAD_genome_AFR")),
        "gnomad.genome.EAS(East Asian)": get_value((tapes_row, "gnomAD_genome_EAS"),
                                                   (inter_var_row, "gnomAD_genome_EAS")),
        "gnomad.genome.NFE(Non-Finnish European)": get_value((tapes_row, "gnomAD_genome_NFE"),
                                                             (inter_var_row, "gnomAD_genome_NFE")),
        "gnomAD_genome_AMR(Admixed American)": get_value((tapes_row, "gnomAD_genome_AMR"),
                                                         (inter_var_row, "gnomAD_genome_AMR")),
        "gnomAD_genome_ASJ(Ashkenazi Jewish)": get_value((tapes_row, "gnomAD_genome_ASJ"),
                                                         (inter_var_row, "gnomAD_genome_ASJ")),
        "gnomAD_genome_FIN(Finnish)": get_value((tapes_row, "gnomAD_genome_FIN"), (inter_var_row, "gnomAD_genome_FIN")),
        "gnomAD_genome_OTH": get_value((tapes_row, "gnomAD_genome_OTH"), (inter_var_row, "gnomAD_genome_OTH")),

        **{
            key: get_value((tapes_row, key), (inter_var_row, key)) for key in
            [
                "Function_description.refGene",
                "Tissue_specificity(Uniprot).refGene",
                "Gene_full_name.refGene",
                "Function_description.refGene",
                "Disease_description.refGene",
                "Tissue_specificity(Uniprot).refGene",
                "Expression(egenetics).refGene",
                "P(HI).refGene",
                "P(rec).refGene",
                "SIFT_score",
                "SIFT_converted_rankscore",
                "SIFT_pred",
                "gnomAD_genome_AFR",
                "gnomAD_genome_AMR",
                "gnomAD_genome_ASJ",
                "gnomAD_genome_EAS",
                "gnomAD_genome_FIN",
                "gnomAD_genome_NFE",
                "gnomAD_genome_OTH",
                "dbscSNV_ADA_SCORE",
                "dbscSNV_RF_SCORE"
            ]
        },
        **{
            key: get_value((inter_var_row, key), (tapes_row, key)) for key in
            [
                "CLNALLELEID",
                "AAChange.refGene",
                "Polyphen2_HDIV_score",
                "Polyphen2_HDIV_rankscore",
                "Polyphen2_HDIV_pred",
                "Polyphen2_HVAR_score",
                "Polyphen2_HVAR_rankscore",
                "Polyphen2_HVAR_pred",
                "LRT_score",
                "LRT_pred",
                "LRT_converted_rankscore",
                "MutationTaster_score",
                "MutationTaster_converted_rankscore",
                "MutationTaster_pred    MutationAssessor_score",
                "MutationAssessor_score_rankscore",
                "MutationAssessor_pred",
                "FATHMM_score",
                "FATHMM_converted_rankscore",
                "FATHMM_pred",
                "PROVEAN_score",
                "PROVEAN_converted_rankscore",
                "PROVEAN_pred"

            ]
        }
    }


def iterdicts(d):
    it = d.itertuples(index=False, name=None)
    columns = tuple(d.columns)
    return map(lambda row: dict(zip(columns, row)), it)


def next_or_none(it):
    try:
        return next(it)
    except StopIteration:
        return None


def join_tables(tapes, inter_var):
    if len(tapes) == 0 and len(inter_var) == 0:
        columns = list(merge(None, None).keys())
        return pd.DataFrame(columns=columns)

    tapes_it = iter(iterdicts(tapes))
    inter_var_it = iter(iterdicts(inter_var))

    tapes_row = next_or_none(tapes_it)
    inter_var_row = next_or_none(inter_var_it)

    inter_var_row_matched = False

    result_rows = []

    matched = 0
    non_matched_tapes = 0
    non_matched_inter_var = 0

    while not (tapes_row is None and inter_var_row is None):
        if tapes_row is None or tapes_row["POS"] > inter_var_row["End"]:
            if inter_var_row_matched:
                inter_var_row = next_or_none(inter_var_it)
                inter_var_row_matched = False
            else:
                result_rows.append(merge(None, inter_var_row))
                inter_var_row = next_or_none(inter_var_it)
                non_matched_inter_var += 1
        elif inter_var_row is None or tapes_row["POS"] < inter_var_row["Start"]:
            result_rows.append(merge(tapes_row, None))
            tapes_row = next_or_none(tapes_it)
            non_matched_tapes += 1
        elif inter_var_row["Start"] <= tapes_row["POS"] <= inter_var_row["End"]:
            result_rows.append(merge(tapes_row, inter_var_row))
            inter_var_row_matched = True
            tapes_row = next_or_none(tapes_it)
            matched += 1
        else:
            raise Exception("InterVar Start is larger then End")

    print("{} matched; {} non matched tapes; {} non matched inter vars".format(matched, non_matched_tapes,
                                                                               non_matched_inter_var))

    return pd.DataFrame.from_dict(result_rows)


def place_cols_to_front(df, front_cols):
    columns = list(df.columns)
    front_cols_set = set(front_cols)
    columns = front_cols + [col for col in columns if col not in front_cols_set]
    return df[columns]


def get_chr_key(chr_value):
    chr_type = chr_value[3:]
    if chr_type == "X":
        return 100000
    elif chr_type == "Y":
        return 110000
    else:
        return int(chr_type)


def df_sort(df, col, key):
    keys = [key(x) for x in df[col]]
    argsort_inds = np.argsort(keys)
    return result.iloc[argsort_inds]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("tapes", help="Path to tapes table. Set path to '-' if you don't have tapes table")
    parser.add_argument("inter_var", help="Path to InterVar table. Set path to '-' if you don't have InterVar table")
    parser.add_argument("out", help="Output table path")

    args = parser.parse_args()

    tapes = read_tapes(args.tapes)
    inter_var = read_inter_var(args.inter_var)

    result = join_tables(tapes, inter_var)

    result = place_cols_to_front(result, [
        "chr",
        "start",
        "end",
        "ref",
        "alt",
        "read_depth",
        "Max-likelihood estimate of the first ALT allele frequency",
        "Allele frequency in gnomAD genome set",
        "gnomad.genome.AFR(African/African American)",
        "gnomad.genome.EAS(East Asian)",
        "gnomad.genome.NFE(Non-Finnish European)",
        "gnomAD_genome_AMR(Admixed American)",
        "gnomAD_genome_ASJ(Ashkenazi Jewish)",
        "gnomAD_genome_FIN(Finnish)",
        "gnomAD_genome_OTH",
        "localization_variant",
        "gene_refgene",
        "exon_replacement_type",
        "zygosity",
        "clinical_signature"

    ])

    result = result[~result["clinical_signature"].isnull()]
    result = df_sort(result, "chr", get_chr_key)

    result.to_csv(args.out, sep="\t", na_rep='.', index=False)
