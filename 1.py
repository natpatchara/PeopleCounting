import pstats
from pstats import SortKey
p1 = pstats.Stats('resultVideo')
p1.sort_stats('tottime').print_stats(20)
