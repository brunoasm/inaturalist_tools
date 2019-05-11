#iNaturalist tools

This repository contains some code to interact with iNaturalist via the API using python programs:

* get_inaturalist_images.py [-h] [-o OBSERVATIONS] [-i IMAGES]
                                 [-s {original,medium,square}] [-d]
                                 name output

positional arguments:

  name                  Name of the organism to search

  output                Output file path

optional arguments:

  -h, --help            show this help message and exit

  -o OBSERVATIONS, --observations OBSERVATIONS
                        Maximum number of observations to download.
                        Observations are randomly chosen if more than the
                        maximum

  -i IMAGES, --images IMAGES
                        Maximum number of images per observation. Images are
                        randomly chosen if more than the maximum

  -s {original,medium,square}, --size {original,medium,square}
                        Image size

  -d, --download        Whether to download images (by default, only writes
                        URLs to output file). Images will be downloaded to a
                        folder with the same name as output file
