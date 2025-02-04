# Color match

Perception is, by its very nature, subjective. The `color_match` Python package tackles the problem of estimating color similarity based on color names (i.e., text).

As a practical case, if two observers describe potentially different shirts by their color, often, it is desirable to compute a perceptual distance between the two descriptions.

Although `color_match` is colorspace agnostic, it uses by default the CIELAB space and computes distances between points in CIELAB with an adjusted metric (CIEDE2000). This metric makes CIELAB as uniform as possible for human color perception (details and references below).

The collection of 136 named hex colors (from the webcolor package) served as a test set. Matches between the 9180 pairs are computed with the adjusted perceptual distance CIEDE2000.

### Similarity

A measure of similarity among colors is calculated from the distance as 

1 - *relative distance* 

where *relative distance* is the ratio between the distance between two given colors and the maximum estimated distance among the set of reference colors in CIELAB (CIEDE2000).

### Match

Match between two colors (i.e. if they can be confused or not) is established by thresholding the pairwise color distance. The threshold can vary depending on the application and inputted in the following method:
```python
from color_match.colorspace import Colorspace
c = ColorSpace()
c.are_comparable(self, c_1, c_2, coeff = 3, year= "2000")
```
The `are_comparable` method returns the distance between the colors `c_1` and `c_2`, and a boolean stating if they match (can be confused) or not (the colors are perceptually distant).


### Application

The aim is to claim if two colors described from memory could be variation of the same color as perceived by different people, in different situations. 

For this reason, the threshold mentioned before has to be set to a high enough value. In this case, the threshold is computed by estimating 1/4 arc-length at fixed luminosity and saturation (average luminosity and high saturation) in the CIELAB space and using the CIEDE2000 distance. This means that colors lying in the same a* b* plane in LAB can be distinguished only if they are at least one quarter of the circle centered on the L-axis apart. This threshold corresponds to 9 times the just-noticeable-difference in CIEDE2000.

Results are listed in the following tables.

**Table 1: Matching colors**. We list here pairs of most common colors that, according to the model just described, could be referred to as the same color (i.e. they match).

*Table structure:* 
- columns **color1** and **color2** report the name of the color and use the same color as a background. 
- The **match** column is always True for only matching (confusable) pairs are considered in this table. The background color is the mean color between the considered color pairs.
- The **similarity** column gives the similarity value between the colors, it is 1 if the two colors are perceptually indistinguishable and 0 if they are at opposite extreme of the CIELAB space equipped with CIEDE2000 metrics. This value can be interpreted as the probability of two colors being swapped in describing an object by memory. 

<img src="/static/true.png" width = "45%"> 

**Table 2: Mismatching colors**. Here are listed colors that lie far enough in the color space to be considered not confusable even when recalling them from memory.

The column `match` this time has not background color, indeed the mean color would make no perceptual sense, being `color1` and `color2` so perceptually far. 

<img src="/static/false.png" width = "45%">

#### How to install

Clone this repository and run

```bash
pip install pathlib
cd color_match
pip install ./
```

#### Usage

###### Create a color space

```python
from color_match.colorspace import ColorSpace

c = ColorSpace(name='lab', include_munsell=False, jnd=2.3)
```

At this stage the package manages CIELAB (name = "lab"), xyY and RGB255. However, it is easily extendable to all the colorspaces supported by the `colorio` package.


###### Compute distance and match between two colors

```
from color_match.colorspace import ColorSpace

c = ColorSpace(name='lab', include_munsell=False, jnd=2.3)
match, distance = c.are_comparable(color1, color2, coeff=6 year=2000)
```

`c1` and `c2` can be either text (included in the css3 color dataset) or RGB values.
`match` is a boolean stating if the two colors lie in CIELAB space at a distance less than `coeff`. The distance is automatically computed in `jnd` units (just noticeable difference) estimated in CIELAB as jnd = 2.3. `color_match` uses the CIEDE2000 distance by default, or depending on the value of the kwarg `year`, the 1976 CIELAB distance or the Euclidean distance, as discussed below.

###### Visualization
To generate a three-dimensional, interactive visualization of the color space.


```python
from color_match.colorspace import ColorSpace

c = ColorSpace(name='lab', include_munsell=True)
c.visualize()
```
and, from the color_match folder launch in the terminal
```bash
tensorboard --logdir ./embeddings/test
```
follow the instruction to the localhost webpage (optimized and tested on Chrome). See figure below.


#### CIELAB
Although no color space is a perfect representation of color, to my best knowledge, CIELAB is the most suitable continuous color space to perform perceptual matching between colors. Indeed, CIELAB was intended to be a perceptually uniform space, and, unlike the RGB color models, CIELAB is designed to approximate human vision. See the [Wiki CIELAB page](https://en.wikipedia.org/wiki/CIELAB_color_space) for details.

In 1931, it was shown that CIELAB lacks uniformity in some regions,  e.g., blue hue or highly saturated colors.

In uniform color spaces, Euclidean distance should reflect perceptual changes in color. As a consequence, this was the distance used until the non-uniformity of this space was discovered. The metrics CIE94 and CIEDE2000 aim to correct this behavior. In color_match, the euclidean distance and these later adjusted metrics are implemented and calculated in units of j.n.d (just notable difference). CIEDE2000 is used by default. See [Wiki Color difference page](https://en.wikipedia.org/wiki/Color_difference#) for the precise formulas.

Another advantage of CIELAB space is that it allows for specifying a white reference, which provides information about the light available in the scene. The standard white references correspond to the most common lighting settings, including direct and indirect sunlight (“D50” and “D65” white references, respectively), incandescent lamps (“A” series), and a theoretical equal-energy light source (“E”).


#### Munsell color system

Munsell was the first to separate hue, value, and chroma into perceptually uniform and independent dimensions, and he was the first to illustrate the colors systematically in three-dimensional space.
The modern Munsell Book of Color (the 1940s) resulted from an extensive series of experiments. Though several replacements for the Munsell system have been invented, building on Munsell's foundational ideas, the Munsell system is still widely used.
Color_match performs an embedding of Munsell colors in the CIELAB space.

On the right, there is the Munsell color chart data (with V=5) embedded in the CIELAB color spaces. If a color space has a chroma prediction that matches that of the Munsell data, the rings formed by the data should appear as perfect circles. Although the projection at V=5 does not display perfect circles, the adjusted CIEDE2000 distance corrects this distortion.

| CIELAB top view | CIELAB sampling Munsell colors |CIELAB sampling Munsell colors projected V = 5 |
|---|---|---|
| image credit Wikipedia | genate through color_match.visualize() |genate through color_match.visualize() and filtered in tensorboard|
|<img src="/static/CIELAB_color_space_top_view.png" width = "300" height="200">|<img src="/static/Munsell_sampling_in_LAB.png" width = "300" height="200">|<img src="/static/Munsell_sampling_in_LAB_V5.png" width = "200" height="200" >

## References

[1] Paul Centore. An Open-source inversion algorithm for the Munsell renotation. Color Research and Application. 2011

[2] Douglas A. Kerr. The CIE XYZ and xyY Color Spaces. Stanford Computer Graphics Laboratory. 2010
