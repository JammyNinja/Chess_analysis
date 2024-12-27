from public.back.api.src.data import load_sample_clean_data


def mvp_analysis():
    clean_data = load_sample_clean_data()

    avg_opponent = clean_data.opp_rating.mean()

    return {
        "avg_opponent" : avg_opponent
    }
