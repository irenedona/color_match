import os
import numpy as np
from scipy.spatial import KDTree
from webcolors import (
    css3_hex_to_names,
    hex_to_rgb,
    name_to_rgb
)
import numpy as np
import colorio as cio
from color_match.exceptions import UndefinedSpace
import colorio
from color_match.visualize import EmbeddingVisualiser
import pandas as pd


class ColorSpace:
    def __init__(self, name='lab', to_munsell=False, jnd=2.3):
        """Class implementing a color space. It allows to load standard and Munsell's 
        colors as references. It maps references to a color space (see colorio for
        a detailed list of the available color spaces), CIELAB by default.
        Measures distance between colors, the centroid of list of colors and uses 
        the Just Noticeable Difference (JNB) constant to determine if two colors can 
        be distinguished by a human observer.

        Args:
            name (str, optional): A color space name. Defaults to 'lab'.
            to_munsell (bool, optional): If True load Munsell's colors as reference. 
            Defaults to False.
            jnd (float, optional): The Just Noticeable Distance constant. 
            Defaults to 2.3.
        """
        self.name=name
        self.to_munsell = to_munsell
        self.jnd=jnd
        self.color_names, self.color_rgb, self.color_hex= self.load()
        self.name2rgb = {n: p for n, p in zip(self.color_names, self.color_rgb)}
        self.name2hex = {n: h for n, h in zip(self.color_names, self.color_hex)}
        self.points = self.init_space()
        self.tree = KDTree(self.points)
        self.name2point = {n: p 
            for n, p in zip(self.color_names, self.points)
        }
        if self.to_munsell:
            self.reference_points = self.get_munsell_reference_points()
            self.reference_tree = KDTree(self.reference_points)

    @staticmethod
    def load():
        """Load the standard dictionary of css3 colors and maps them to rgb
        Color names and values are used for both as reference and test.
        """
        css3_db = css3_hex_to_names
        color_names = list(css3_db.values())
        names = []
        values = []    
        for color_hex, color_name in css3_db.items():
            names.append(color_name)
            rgb_value = hex_to_rgb(color_hex)
            values.append(rgb_value)
        return names, values, css3_db.keys()

    def get_munsell_reference_points(self):
        """Get the Munsell colors as reference. 
        This is a way to discretize the CIELAB color space in 10 (L_i, a, b)
        planes, where L_i are constants corresponding to V in the Munsell
        color space.
        """
        d = colorio.data.Munsell()
        points = d.xyy100.T
        return np.array([self.from_xyy_to_lab(p) for p in points])

    @staticmethod
    def from_rgb_to_lab(c):
        """Map a color from RGB255 to CIELAB
        """
        cs = cio.cs.CIELAB()
        return cs.from_rgb255(c)

    @staticmethod
    def from_rgb_to_xyy(c):
        """Map a color from RGB255 to xyY
        """
        cs = cio.cs.XYY()
        return cs.from_rgb255(c)
    
    @staticmethod
    def from_xyy_to_lab(c):
        """Map a color from xyY to LAB
        """
        cs_lab = cio.cs.CIELAB()
        cs_xyy = cio.cs.XYY(Y_scaling=100)
        c_xyz = cs_xyy.to_xyz100(c)
        return cs_lab.from_xyz100(c_xyz)

    def init_space(self):    
        """Given a color space name (see colorio for the list 
        of available color spaces). It maps the reference css3 
        colors to points in the space of choice.
        """
        if self.name == 'lab':
            values = [self.from_rgb_to_lab(v)
                 for v in self.color_rgb]
        elif self.name == 'xyy':
            values = [self.from_rgb_to_xyy(v)
                 for v in self.color_rgb]
        else:
            raise UndefinedSpace(self.name)
        return values

    @staticmethod
    def centroid(points):
        """Computes the centroid of a list of points
        """
        if len(points)==1:
            return points[0]
        return np.mean(points, axis=0)

    def get_points(self, color_names = None):
        """Get points from color names

        Args:
            color_names (list, optional): A list of color names. Defaults to None.

        Returns:
            list: points corresponding to the names listed in color_names
        """
        return [self.name2point[c] for c in color_names]

    def get_centroid(self, color_names = [], 
                    with_name=True):
        """Compute the centroid of a list of color names.c

        Args:
            color_names (list, optional): A list of color names. Defaults to [].
            with_name (bool, optional): If True the name corresponding to the nearest
            reference color is returned. Defaults to True.

        Returns:
            list: centroid of the colors as represented in the color space
            `self.name` 
            str: name of reference color nearest to the centroid in `self.name`
        """
        color_points = self.get_points(color_names = color_names)
        centroid = self.centroid(color_points)
        if with_name:
            centroid_name = self.get_name(centroid)
            return centroid, centroid_name
        return centroid

    def get_name(self, point):
        """Compute the nearest reference color in the color space `self.name`

        Args:
            point (list): a point in the color space `self.name`

        Returns:
            list: the first nearest neighbor to point among the reference colors
        """
        distance, index = self.tree.query(point)
        return self.color_names[index]
    
    @staticmethod
    def not_np(array):
        """True if array is not a numpy ndarray"""
        return isinstance(array, (int, float, list, tuple))
    
    def distance_l2(self, p1, p2):
        """Computes the l2 distance between two points

        Args:
            p1 (list): a point 
            p2 (list): a point 

        Returns:
            [float]: l2 distance between p1 and p2
        """
        if self.not_np(p1):
            p1, p2 = np.array(p1), np.array(p2)
        return np.linalg.norm(p1 - p2)
    
    def project_to_reference(self, p, nearest_L=False, V = None):
        """Get 1-NN of p with respect to Munsell's colors

        Args:
            p (list): a point representing a color in `self.name`
            nearest_L (bool, optional): If True computes the nearest
            Munsell's plane to the inputted point. Defaults to False.
            V (int, optional): Value in Munsell space [0, ..., 9]. 
            Defaults to None. If not None it returns the closest Munsell 
            points to p on the plane (V, a, b)

        Returns:
            list: A point among the Munsell reference points
        """
        
        assert self.hasattr(self, "reference_points"), "Specify a list of reference colors"
        if nearest_L:
            munsell_ls = np.unique(self.reference_points[:,0])
            ind = np.argmin([p[0] - ml for ml in munsell_ls])
            subset_munsell = np.array([mp for mp in self.reference_points 
                                       if mp[0] == munsell_ls[ind]])
            subtree = KDTree(subset_munsell)
            _, index = subtree.query(p)    
        elif V is not None:
            munsell_ls = np.unique(self.reference_points[:,0])
            ind = V
            subset_munsell = np.array([mp for mp in self.reference_points 
                                       if mp[0] == munsell_ls[ind]])
            subtree = KDTree(subset_munsell)
            _, index = subtree.query(p)    
        else:
            _, index = self.reference_tree.query(p)
            
        return self.reference_points[index]
    
    @staticmethod
    def is_rgb(array):
        """If True array is a color in RGB255
        """
        return len(array) == 3 and all(a >= 0 and a < 255 for a in array)
    
    def are_comparable(self, c_1, c_2, coeff = 3):
        """Given two colors as text (according to the dictionary generated
        in self.name2colors.keys()) or RGB255, it returns True if the colors, 
        embedded in CIELAB, are less than three jnd (just noticeable 
        difference) far apart. False otherwise.
        
        """
        if (c_1 in self.name2point and c_2 in self.name2point):
            c_1 = self.name2point[c_1]
            c_2 = self.name2point[c_2]
        elif self.is_rgb(c_1) and self.is_rgb(c_2):
            c_1 = from_rgb_to_lab(c_1)
            c_2 = from_rgb_to_lab(c_2)
        distance = self.distance_CIE76(c_1, c_2)
        return distance, distance < coeff
            
        
    def distance_CIE76(self, p1, p2):
        """distance in CIE76 in unit of jnd
           jnd = just noticeable difference
        Args:
            p1 ([type]): [description]
            p2 ([type]): [description]
        """
        return self.distance_l2(p1,p2)/self.jnd
    
    def visualize(self):
        """Visualize the reference colors and the Munsell reference colors 
        in a 3-dimensional interactive tensorboard.
        After running this method, run in the terminal
        `tensorboard --logdir ./emebddings/test`
        and follow the instructions
        """
        df = pd.DataFrame.from_dict(self.name2point,     
                                    orient = 'index')
        df.reset_index(inplace=True)
        df.columns=["colors", *list(self.name)]
        df["is_reference"] = "0"
        if self.to_munsell:
            df_m = pd.DataFrame(self.reference_points, 
                                columns=list(self.name))
            df_m["is_reference"] = "1"
            df_m["colors"] = [str(i) + "_Munsell" 
                              for i in range(len(self.reference_points))]
            df = pd.concat([df, df_m])
        emb = EmbeddingVisualiser(df, ["colors", "is_reference"], 
                                  list(self.name),
                                  session_name="test_double")
        folder = os.path.join('.', 'embeddings')
        emb.visualize(folder)
        self.df = df        

if __name__ == "__main__":

    color_space = ColorSpace(to_munsell=True)
    color_space.visualize()
    


    

