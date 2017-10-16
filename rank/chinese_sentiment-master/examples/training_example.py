import sys
sys.path.append('../src')
from training import training
training('../dict/ntusd-positive.txt','../dict/ntusd-negative.txt','../model/','../dict/ntusd-full.dic')
