#! /usr/bin/env python
#
# Run this, passing the VBO filename as an argument
#

import csv
import re
import sys
from numpy import *
import matplotlib.pyplot as plt

def main():
    # Load each column as an array
    cols = loadtxt(sys.argv[1], delimiter=',', unpack=True)
    plt.plot(cols[0], cols[1])
    plt.show()

if __name__ == '__main__':
    main()