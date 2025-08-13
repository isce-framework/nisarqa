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

# Abstract base class for all NISAR products
from .nisar_product import *

# Abstract base class for L1 range-Doppler vs. L2 Geocoded products
from .radar_product import *
from .geo_product import *

# Abstract base classes for Non-Insar products (RSLC, GSLC, GCOV)
from .non_insar_product import *
from .slc_product import *  # for RSLC and GSLC
from .non_insar_geo_product import *  # for GSLC and GCOV

# Instantiable Non-Insar (RSLC, GSLC, GCOV) product readers
from .rslc_reader import *
from .gslc_reader import *
from .gcov_reader import *

# Abstract base class for Interferometry products (RIFG, RUNW, GUNW, ROFF, GOFF)
from .insar_product import *

# Abstract base classes for the groupings of related Datasets in Interferogram
# products (RIFG, RUNW, GUNW).
from .igram_groups import *

# Instantiable RIFG, RUNW, GUNW product readers
from .rifg_runw_gunw_readers import *

# Abstract base class for Offset products (ROFF, GOFF)
from .offset_product import *

# Instantiable ROFF and GOFF product readers
from .roff_goff_readers import *
