### Input Product Reader Structure ###
# The nisarqa input product readers leverage class inheritance to avoid
# code duplication.
# The base class for all of the product readers is NisarProduct.
# From there, we create diamond inheritance patterns to specialize.
# For example, each product type is either a L1 RadarProduct or an L2 GeoProduct,
# and it is also either a NonInsarProduct or an InsarProduct. Some examples:
#   RSLC is a RadarProduct and a NonInsarProduct
#   GSLC is a GeoProduct and a NonInsarProduct
#   RUNW is a RadarProduct and an InsarProduct
#   GUNW is a GeoProduct and an InsarProduct
# The diamond-pattern of the class inheritance hierarchy becomes more and more
# specialized, until we finally get to the instantiable product readers.

# Note: Private utility functions
# Because all functions in ._utils.py are private (i.e. prefixed with an
# underscore) then `from ._utils.py import *` does nothing.
# Otherwise, importing these functions in the __init__.py would make them
# public, which we don't want to do.

# Abstract base class for all NISAR product readers
from .nisar_base import *

# Abstract base class for L1 vs. L2
from .l1_radar_base import *
from .l2_geo_base import *

# Abstract base classes for Non-Insar (RSLC, GSLC, GCOV)
from .non_insar_base import *
from .slc_base import *  # for RSLC and GSLC
from .non_insar_geo_base import *  # for GSLC and GCOV

# Instantiable Non-Insar (RSLC, GSLC, GCOV) classes
from .rslc_product import *
from .gslc_product import *
from .gcov_product import *

# Abstract base classes for Interferometry (RIFG, RUNW, GUNW, ROFF, GOFF)
from .insar_base import *

# Abstract base classes for the groupings of related Datasets in Interferogram
# (RIFG, RUNW, GUNW) products.
from .igram_base_groups import *

# Instantiable RIFG, RUNW, GUNW product readers
from .igram_products import *

# Abstract base class for Offsets (ROFF, GOFF)
from .offsets_base import *

# Instantiable ROFF and GOFF product readers
from .offsets_products import *
