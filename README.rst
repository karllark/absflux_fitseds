Fitting SEDs of AbsFlux Stars
=============================

Fitting the SEDs of flux calibration stars using the `measure_extinction`
package that has a flexible extinction model (esp. in the UV) and full
Bayesian fitting with MCMC sampling of fit parameters.

In Development!
---------------

Active development.
Data still in changing.
Use at your own risk.

Contributors
------------
Karl Gordon

License
-------

This code is licensed under a 3-clause BSD style license (see the
``LICENSE`` file).

Data
----

STIS and WFC3 grism spectra from Ralph Bohlin reductions.

WFC3 photometry from XXX paper.

Created measure_extinction format STIS/WFC3 spectra using `utils/process_hstdata.py`

Old style merged STIS spectra 
`~/Python/measure_extinction/measure_extinction/utils/merge_stis_spec.py wdfs1055_36 --ralph --inpath ./stis/ --outpath ./ --waveregion UV``

Fits
----

Before fitting, `utils\pic_cont.py` needs to be run to pixel the regular and continuum only WD models.

Fitting is done with `utils/fit_model.py` code.  Example command is `utils/fit_model.py wdfs1514_00 --picmodel --Av_init=0.1`.

Bulk fitting is done using the `fitstars` (wdfs stars) and `fits_stars_med` (wd stars) bash scripts.  These start multiple 
simultaneous fits with log files in the `logs` subdir.

Figures
-------
