from itertools import combinations
import matplotlib.pyplot as plt
import pandas as pd
from color_match.colorspace import ColorSpace
import numpy as np
from tqdm import tqdm

def get_pairs(list):
    """Generate pairs of elements in list without repetitions
    """
    return combinations(list, r=2)

def generate_match_table(colorspace, pairs):
    """Generate  dataframe with all possible combination of hex colors,
       their match (i.e. if they correspond to the same color 
       within a given tolerance level) and their distance.

    Args:
        colorspace (ColorSpace): instance of ColorSpace
        pairs (list): list of pairs of color names

    Returns:
        [pd.DataFrame]
    """
    df =  pd.DataFrame(np.zeros((len(pairs), 4)), 
                      columns = ["color1", "color2", "match", "distance(in_jnd)"])

    for i, (p1, p2) in enumerate(tqdm(pairs, desc="evaluating test color pairs")):
        df.iloc[i, 0] = p1
        df.iloc[i, 1] = p2
        dist, match =colorspace.are_comparable(p1, p2)
        df.iloc[i, 2] = match
        df.iloc[i, 3] = dist
    return df

def color_centroid(row):
    """If the two colors match it returns the centroid
       w.r.t. the reference colors
    """
    if row.match:
        c = colorspace.get_centroid([row.color1,row.color2])
        return colorspace.name2hex[c[1]]
    return None

def generate_color_tables():
    """Generate result table having as colomns 
       - color1: reference color name and the corresponding hex color as bkg
       - color2: candidate match and the corresponding hex color as bkg
       - match: True if the two colors match
       - distance: distance in j.n.d. between the two colors 
        and centroid color as background
       
    """
    colorspace = ColorSpace()
    pairs = get_pairs(colorspace.color_names)
    df = generate_match_table(colorspace, list(pairs))
    df1 = df.copy()
    df[df.match==True].style.apply(lambda x: ['background-color: {}'.format(colorspace.name2hex[x.color1]),
                          'background-color: {}'.format(colorspace.name2hex[x.color2]),
                          'background-color: {}'.format(color_centroid(x)),
                                       None  # x["distance(in_jnd)"]
                         ], axis=1).to_excel('./test_match_true.xlsx', engine='openpyxl')
    df1[df1.match==False].style.apply(lambda x: ['background-color: {}'.format(colorspace.name2hex[x.color1]),
                          'background-color: {}'.format(colorspace.name2hex[x.color2]),
                          'background-color: {}'.format(color_centroid(x)),
                                       None  # x["distance(in_jnd)"]
                         ], axis=1).to_excel('./test_match_false.xlsx', engine='openpyxl')
    return

if __name__=="__main__":
    generate_color_tables()