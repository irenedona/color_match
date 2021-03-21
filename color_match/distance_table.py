from itertools import combinations
import matplotlib.pyplot as plt
import pandas as pd
from color_match.colorspace import ColorSpace
import numpy as np
from tqdm import tqdm
from colormath.color_objects import LabColor

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
    df =  pd.DataFrame(np.zeros((len(pairs), 5)), 
                      columns = ["color1", "color2", "match", "distance(in_jnd)", "similarity"])

    for i, (p1, p2) in enumerate(tqdm(pairs, desc="evaluating test color pairs")):
        df.iloc[i, 0] = p1
        df.iloc[i, 1] = p2
        dist, match =colorspace.are_comparable(p1, p2, coeff=9)
        df.iloc[i, 2] = match
        df.iloc[i, 3] = dist
        s = colorspace.similarity(p1, p2)
        df.iloc[i, 4] = s
    return df

def color_centroid(row, colorspace):
    """If the two colors match it returns the centroid
       w.r.t. the reference colors
    """
    if row.match:
        c_point, c_name = colorspace.get_centroid([row.color1,row.color2])
        return colorspace.name2hex[c_name]
    return None

def generate_color_tables(allpairs=True, colorselection=set()):
    """Generate result table having as colomns 
       - color1: reference color name and the corresponding hex color as bkg
       - color2: candidate match and the corresponding hex color as bkg
       - match: True if the two colors match
       - distance: distance in j.n.d. between the two colors 
        and centroid color as background
       
    """
    colorspace = ColorSpace()
    if allpairs:
        pairs = get_pairs(colorspace.color_names)
        output_name = "static/test_match_"
    else:
        pairs = get_pairs(colorselection)
        output_name = "static/test_match_reduced_"
    df = generate_match_table(colorspace, list(pairs)).sort_values(by='similarity', ascending=False)
    df1 = df.copy()
    

    df[df.match==True].style.apply(lambda x: ['background-color: {}'.format(colorspace.name2hex[x.color1]),
                          'background-color: {}'.format(colorspace.name2hex[x.color2]),
                          'background-color: {}'.format(color_centroid(x, colorspace)),
                                       None,
                                       None 
                         ], axis=1).to_excel(output_name+'true2000.xlsx', engine='openpyxl')
    df1[df1.match==False].style.apply(lambda x: ['background-color: {}'.format(colorspace.name2hex[x.color1]),
                          'background-color: {}'.format(colorspace.name2hex[x.color2]),
                          'background-color: {}'.format(color_centroid(x, colorspace)),
                                       None,
                                       None
                         ], axis=1).to_excel(output_name+'false2000.xlsx', engine='openpyxl')


def generate_color_tables_reduced():
    selected_colors = {'darkblue', 'darkgreen', 'darkgrey',
    'darkolivegreen', 'darkorange', 'darkred', 'darkseagreen',
    'darkslategrey', 'darkviolet', 'lightblue',
    'lightgreen', 'lightgrey',
    'lightpink', 'lightseagreen', 'lightskyblue', 'lightslategrey',
    'lightsteelblue', 'lightyellow', 'azure', 'blue',
    'red', 'yellow', 'green', 'grey',
    'pink', 'white', 'violet', 'orange', 'brown'}
    generate_color_tables(allpairs=False, colorselection=selected_colors)


if __name__=="__main__":
    generate_color_tables()
    generate_color_tables_reduced()