from public.back.api.src.data import load_sample_clean_data
import pandas as pd
import matplotlib.pyplot as plt

def mvp_analysis():
    clean_data = load_sample_clean_data()

    avg_opponent = clean_data.opp_rating.mean()

    return {
        "avg_opponent" : avg_opponent
    }

def get_results_by_rating_fig():
    """returns fig for streamlit to plot"""
    rating_df = load_sample_clean_data()
    cols = ["user_rating", "user_result", "opp_result", "opp_rating"]
    rating_df = rating_df[cols]

    game_endings_mapping = {
        'abandoned' : "lose",
        'checkmated' : "lose",
        'resigned' : "lose",
        'timeout' : "lose",
        'agreed' : "draw",
        'insufficient': "draw",
        'repetition' : "draw",
        'stalemate' : "draw",
        'timevsinsufficient' : "draw",
        'win' : "win"
    }

    rating_df['user_result_map'] = rating_df.user_result.map(game_endings_mapping)

    def get_bins(bin_width = 50):
        min_bin = rating_df.opp_rating.min() // bin_width * bin_width #round down to nearest 50
        max_bin = rating_df.opp_rating.max() // bin_width * bin_width + bin_width #round up to nearst 50

        bin_ranges, bin_edges = pd.cut(x=rating_df["opp_rating"],
            bins =range(min_bin, max_bin+1, bin_width),
                retbins=True)
        return bin_ranges, bin_edges

    bin_ranges, bin_edges = get_bins()
    rating_df.loc[:,"opp_rating_range"] = bin_ranges#.values

    results_by_rating_df = rating_df.groupby(by="opp_rating_range", observed=False)["user_result_map"].value_counts(normalize=True).unstack()
    results_by_rating_df = results_by_rating_df.reindex(labels=["win", "draw", "lose"], axis=1)

    
    print("plotting!")
    # fig, ax = plt.subplots()
    # plot = results_by_rating_df.plot(kind="barh",
    #                    stacked=True,
    #                   ax=ax,
    #                    color = ["green", "orange", "red"],
    #                   ylabel="opponent rating range",
    #                   xlabel="share of games")
    #
    #
    ax = plt.bar([1,2,3],[4,5,6])
    print("done plotting")
    return ax

# get_results_by_rating_fig()
