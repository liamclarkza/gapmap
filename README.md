# gapmap

# 1. Questions
- What constitutes a gap?
- Can a gap contain more than one missing tree? Flood-fill?
- Do we look at historic surveys to see if there were trees in a certain spot before?
- Probably need to convert lat,lon into utm coordinates.
- What coordinate system are points referenced in?

Possible first approach (geometry approach):
1. Convex hull around the orchard (with padding)
2. Align a grid to the rows and cols in the orchard (such that the points are in the centres of pixels)
3. Fill missing pixels in the grid


https://stackoverflow.com/questions/62946604/fitting-an-orthogonal-grid-to-noisy-coordinates/72854265#72854265


Assuming equal spacing, we can calculate the rotation needed as the difference between the median x and y differences