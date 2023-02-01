import os, sys

currentDir = os.path.dirname(__file__)
parentDir = os.path.join(currentDir, '..')
sys.path.append(os.path.abspath(parentDir))