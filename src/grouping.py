from group_mapping import get_group, EXCLUDED, UNCLASSIFIED_KEY


def apply_grouping(merged_df):
    df = merged_df.copy()
    groups = df.apply(lambda row: get_group(row['ItemNumber'], row['ProductConfigurationId']), axis=1)
    df['group_key'] = groups.apply(lambda g: g[0])
    df['group_name'] = groups.apply(lambda g: g[1])

    df = df[df['group_key'] != EXCLUDED]

    unclassified_df = df[df['group_key'] == UNCLASSIFIED_KEY]
    unclassified_items = sorted(zip(unclassified_df['ItemNumber'], unclassified_df['ProductConfigurationId']))

    classified_df = df[df['group_key'] != UNCLASSIFIED_KEY]

    grouped = classified_df.groupby('group_key').agg(
        group_name=('group_name', 'first'),
        AvailableOnHandQuantity=('AvailableOnHandQuantity', 'sum'),
        avg_daily_consumption_7d=('avg_daily_consumption_7d', 'sum'),
        avg_daily_consumption_30d=('avg_daily_consumption_30d', 'sum'),
        Configuracion=('ProductConfigurationId', lambda values: ', '.join(sorted(set(v for v in values if v is not None)))),
    ).reset_index()

    grouped = grouped.sort_values('group_key').drop(columns=['group_key']).reset_index(drop=True)

    return grouped, unclassified_items
