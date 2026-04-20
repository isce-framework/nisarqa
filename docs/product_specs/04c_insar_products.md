
## InSAR and Offsets Products (RIFG, RUNW, GUNW, ROFF, GOFF)


### Unwrapped Phase (RUNW, GUNW)

Example Unwrapped Phase plots and histogram in the PDF 
(generated from ALOS/PALSAR data): 

![Example Unwrapped Phase Plots in the PDF](images/report_unw_igram.jpg)

![Example Unwrapped Phase Histogram in the PDF](images/report_unw_igram_hist.jpg)


### Connected Components (RUNW, GUNW)

Example Connected Components plot and bar chart in the PDF 
(generated from ALOS/PALSAR data): 

![Example Connected Components Plot in the PDF](images/report_cc.jpg)

### Unwrapped Coherence Magnitude (RUNW, GUNW)

Example Unwrapped Coherence Magnitude plot and histogram in the PDF 
(generated from ALOS/PALSAR data): 

![Example Unwrapped Coherence Magnitude Plot in the PDF](images/report_unw_coh.jpg)

![Example Unwrapped Coherence Magnitude Histogram in the PDF](images/report_unw_coh_hist.jpg)


### Wrapped Phase and Wrapped Coherence Magnitude (RIFG, GUNW)

Note: GUNW products contain individual coherence magnitude 
layers for the unwrapped phase image and for the wrapped phase image, 
at postings matching the corresponding phase image. 
Both coherence magnitude layers are plotted in the GUNW QA report PDF.

Example Wrapped Phase and Wrapped Coherence Magnitude plots and 
histograms in the PDF (generated from ALOS/PALSAR data): 

![Example Wrapped Phase and Wrapped Coherence Magnitude Plots in the PDF](images/report_wrapped_igram_coh.jpg)

![Example Wrapped Phase and Wrapped Coherence Magnitude Histograms in the PDF](images/report_wrapped_igram_coh_hist.jpg)



### Ionosphere Phase Screen and Phase Screen Uncertainty (RUNW, GUNW)

Example Ionosphere Phase Screen and Phase Screen Uncertainty plots and 
histograms in the PDF (generated from ALOS/PALSAR data): 

![Example Ionosphere Phase Screen and Phase Screen Uncertainty Plots in the PDF](images/report_iono_phs_screen.jpg)

![Example Ionosphere Phase Screen and Phase Screen Uncertainty Histograms in the PDF](images/report_iono_phs_screen_hist.jpg)



### Along Track Offsets and Slant Range Offsets (RIFG, RUNW, GUNW, ROFF, GOFF)

Example Along Track Offsets and Slant Range Offsets plots and 
histograms in the PDF (generated from ALOS-2/PALSAR-2 data): 

![Example Along Track Offsets and Slant Range Offsets Plots in the PDF](images/report_az_rng_offsets.jpg)

![Example Along Track Offsets and Slant Range Offsets Histograms in the PDF](images/report_az_rng_offsets_hist.jpg)



### Combined Azimuth and Slant Range Displacement (Quiver Plots) (ROFF, GOFF)

ROFF: Example Combined Azimuth and Slant Range Displacement plot in the PDF 
(generated from ALOS-2/PALSAR-2 data):

![Example Combined Pixel Offsets Plot in the ROFF PDF](images/report_offsets_quiver_roff.jpg)


GOFF: Example Combined Azimuth and Slant Range Displacement plot in the PDF 
(generated from ALOS-2/PALSAR-2 data): 

![Example Geocoded Combined Pixel Offsets Plot in the GOFF PDF](images/report_offsets_quiver_goff.jpg)


In both ROFF and GOFF products, the Along-Track Offset and Slant-Range 
Offset layers represent displacement in the satellite’s along-track and 
slant range directions, respectively.

For GOFF products, although these layers are geocoded onto a projected 
coordinate grid, their pixel values still represent offsets from the 
satellite’s perspective — that is, in the range-Doppler coordinate system. 
These pixel values do not represent displacements in the projected (map) 
coordinate grid.

Because of this distinction, the quiver plots in the GOFF Browse Image PNG 
and QA PDF products undergo additional processing. Similar to ROFF 
products, the quiver plot background image (and associated colorbar) 
displays the combined displacement magnitude in radar coordinates to 
accurately reflect the underlying offsets layers.

However, for visualization purposes, the GOFF QA SAS applies an additional 
transformation to the quiver arrows so that they indicate the direction 
and relative magnitude of the combined X and Y displacements in projected 
coordinates (i.e., on the geocoded grid).


### Cross Offset Variance and Correlation Surface Peak (RIFG, RUNW, GUNW, ROFF, GOFF)

Cross Offset Variance is only available in ROFF and GOFF products. 
Correlation Surface Peak is available in all RIFG, RUNW, GUNW, ROFF, 
GOFF products.

Example Cross Offset Variance and Correlation Surface Peak plots and 
histograms in the PDF (generated from ALOS-2/PALSAR-2 data): 

![Example Cross Offset Variance and Correlation Surface Peak Plots in the PDF](images/report_offsets_cov_and_surf_peak.jpg)

![Example Cross Offset Variance and Correlation Surface Peak Histograms in the PDF](images/report_offsets_cov_and_surf_peak_hist.jpg)



### Along Track and Slant Range Offset Variance (ROFF, GOFF)

Example Along Track and Slant Range Offset Variance plots and 
histograms in the PDF (generated from ALOS-2/PALSAR-2 data): 

![Example Along Track and Slant Range Offset Variance Plots in the PDF](images/report_offsets_variance.jpg)

![Example Along Track and Slant Range Offset Variance Histograms in the PDF](images/report_offsets_variance_hist.jpg)



