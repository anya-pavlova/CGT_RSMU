import pandas as pd
import csv
from collections import defaultdict
import numpy as np
import argparse
import urllib.parse


def select_fields(d, keys):
    return {key: d[key] for key in keys}


def is_nan(x):
    return x != x


def parse_vcf_info(info):
    result = {}
    for pair in info.split(";"):
        key_value = pair.split("=")
        if len(key_value) == 2:
            key, value = key_value
            if value == ".":
                value = np.nan
            result[key] = value
    return result


def read_vcf(vcf_file):
    with open(vcf_file) as f:
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
                **parse_vcf_info(row["INFO"])
            }
            yield row


def read_tapes(tapes_file):
    if tapes_file == "-":
        return pd.DataFrame()

    tapes = []

    for row in read_vcf(tapes_file):
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


def read_read_depth(depth_read_file):
    read_depth_map = {}
    for row in read_vcf(depth_read_file):
        read_depth_map[int(row["POS"])] = int(row["DP"])
    return read_depth_map


def get_value(*dict_col_pairs):
    for d, col in dict_col_pairs:
        if d is not None:
            if col in d:
                value = d[col]
                if not is_nan(value):
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
        "Gene.ensGene": get_value((tapes_row, "Gene.ensGene"), (inter_var_row, "Gene.ensGene")),

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
                # "gnomAD_genome_AFR",
                # "gnomAD_genome_AMR",
                # "gnomAD_genome_ASJ",
                # "gnomAD_genome_EAS",
                # "gnomAD_genome_FIN",
                # "gnomAD_genome_NFE",
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


def fill_read_depth(result, read_depth_map):
    read_depth = []
    n_filled_values = 0
    n_missing = 0
    for row in result.itertuples(index=False):
        if is_nan(row.read_depth):
            read_depth_value = read_depth_map.get(row.start)
            if read_depth_value is None:
                read_depth.append(np.nan)
                n_missing += 1
            else:
                read_depth.append(read_depth_value)
                n_filled_values += 1
        else:
            read_depth.append(row.read_depth)

    result["read_depth"] = read_depth

    
    return result


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
    elif chr_type == "M":
        return 120000
    else:
        return int(chr_type)


def df_sort(df, col, key):
    keys = [key(x) for x in df[col]]
    argsort_inds = np.argsort(keys)
    return df.iloc[argsort_inds]


def generate_varsome_url(row):
    # https://varsome.com/variant/hg19/chr1:247588858:C:A
    return "https://varsome.com/variant/hg19/" + urllib.parse.quote("{chr}:{start}:{ref}:{alt}".format(**row))


def split_by_condition(arr, predicate):
    true_array = []
    false_array = []

    for x in arr:
        if predicate(x):
            true_array.append(x)
        else:
            false_array.append(x)

    return true_array, false_array


def collect_sheets(result):
    sheets = [("All", result)]

    groups_pool = list(result.groupby('clinical_signature', as_index=False))

    def key_in_string(key):
        return lambda s: key in s

    def key_in_string_ignore_case(key):
        key = key.lower()
        return lambda s: key in s.lower()

    names_with_predicates = [
        ("Benign", key_in_string_ignore_case("Benign")),
        ("Pathogenic", key_in_string("Pathogenic")),
        ("Likely pathogenic", key_in_string("Likely_pathogenic")),
        ("Uncertain significance", key_in_string("Uncertain_significance"))
    ]

    def add_sheet(name, groups):
        if len(groups) > 0:
            dfs = [df for key, df in groups]
            sheets.append((name, pd.concat(dfs, ignore_index=True)))

    for name, predicate in names_with_predicates:
        key_groups, groups_pool = split_by_condition(groups_pool, lambda name_df: predicate(name_df[0]))
        add_sheet(name, key_groups)

    add_sheet("Other", groups_pool)

    sheets = [(name, df_sort(df, "chr", get_chr_key)) for name, df in sheets]
    return sheets


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("tapes", help="Path to tapes table. Set path to '-' if you don't have tapes table")
    parser.add_argument("inter_var", help="Path to InterVar table. Set path to '-' if you don't have InterVar table")
    parser.add_argument("read_depth",
                        help="Path to read depth table. Set path to '-' if you don't have read depth table")
    parser.add_argument("out", help="Output table path")

    args = parser.parse_args()

    tapes = read_tapes(args.tapes)
    inter_var = read_inter_var(args.inter_var)

    result = join_tables(tapes, inter_var)

    result = result[result["chr"] != 'chrM']

    if args.read_depth != "-":
        result = fill_read_depth(result, read_read_depth(args.read_depth))
    result = result[~result["read_depth"].isnull()]
    result["read_depth"] = pd.to_numeric(result["read_depth"])
    result = result[result["read_depth"] > 2]

    result["varsome"] = ['=HYPERLINK("{url}")'.format(url=generate_varsome_url(row)) for row in iterdicts(result)]

    result = place_cols_to_front(result, [
        "chr",
        "start",
        "end",
        "ref",
        "alt",
        "varsome",
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
        "clinical_signature",
        "Gene.ensGene",
        "AAChange.refGene",
        "CLNALLELEID",
        "Disease_description.refGene",
        "Expression(egenetics).refGene",
        "FATHMM_converted_rankscore",
        "FATHMM_pred",
        "FATHMM_score",
        "Function_description.refGene",
        "Gene_full_name.refGene",
        "ID_in_db_hereditary_diseases",
        "LRT_converted_rankscore",
        "LRT_pred",
        "LRT_score",
        "MutationAssessor_pred",
        "MutationAssessor_score_rankscore",
        "MutationTaster_converted_rankscore",
        "MutationTaster_pred    MutationAssessor_score",
        "MutationTaster_score",
        "P(HI).refGene",
        "P(rec).refGene",
        "PROVEAN_converted_rankscore",
        "PROVEAN_pred",
        "PROVEAN_score",
        "Polyphen2_HDIV_pred",
        "Polyphen2_HDIV_rankscore",
        "Polyphen2_HDIV_score",
        "Polyphen2_HVAR_pred",
        "Polyphen2_HVAR_rankscore",
        "Polyphen2_HVAR_score",
        "Review_status_in_ClinVar",
        "SIFT_converted_rankscore",
        "SIFT_pred",
        "SIFT_score",
        "Tissue_specificity(Uniprot).refGene",
        "associated_disease",
        "dbscSNV_ADA_SCORE",
        "dbscSNV_RF_SCORE",
        "gene_associated_disease",
        "gnomad.genome.AFR(African/African American)",
        "gnomAD_genome_AMR(Admixed American)",
        "gnomAD_genome_ASJ(Ashkenazi Jewish)",
        "gnomad.genome.EAS(East Asian)",
        "gnomAD_genome_FIN(Finnish)",
        "gnomad.genome.NFE(Non-Finnish European)",
        "where_gene_expressed"
    ])

    with pd.ExcelWriter(args.out) as writer:
        for sheet_name, df in collect_sheets(result):
            df.to_excel(writer, na_rep='.', index=False, sheet_name=sheet_name)
