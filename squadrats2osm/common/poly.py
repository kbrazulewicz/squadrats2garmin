import re

class Poly:
    def __init__(self, filename):
        self.coords = []
        with open(filename) as f:
            filetype = f.readline().rstrip('\n')
            if (filetype != 'polygon'):
                raise Exception('Expecting polygon filetype, got "{}" instead'.format(filetype))

            for l1 in f:
                l1 = l1.strip()
                if (l1 == 'END'): break
                for l2 in f:
                    l2 = l2.strip()
                    if (l2 == 'END'): break
                    self.coords.append([float(s) for s in re.split('\s+', l2)])