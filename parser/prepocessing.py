from pandas import DataFrame


def preprocess(data: dict) -> DataFrame:
    # make df
    df = DataFrame([data])

    # rename columns
    df.columns = [col.replace('_ _', '_').replace(' ', '_') for col in df.columns]

    # change type of hs% columns
    hs_cols = [col for col in df.columns if 'headshot_%' in col]
    for col in hs_cols:
        df[col] = df[col].apply(lambda x: x.replace('%', ''))

    # removing columns
    data = df.drop(columns=['url', 't1_name', 't2_name', 'date',])

    return df
