def evaluate(df):

    valid = df[df["VALID"]]

    total = len(valid)

    top1 = valid["TOP1_HIT"].sum()
    top3 = valid["TOP3_HIT"].sum()
    top5 = valid["TOP5_HIT"].sum()

    return {
        "matches": total,
        "top1": top1 / total,
        "top3": top3 / total,
        "top5": top5 / total,
    }