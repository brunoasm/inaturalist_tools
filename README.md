# iNaturalist tools

This repository contains some code to interact with iNaturalist via the API using Python:

## get_inaturalist_images.py 

### Positional arguments:

  `name`                  Name of the organism to search

  `output`                Output file path

### Optional arguments:

  `-h`, `--help`            show this help message and exit

  `-o OBSERVATIONS`, `--observations OBSERVATIONS`
                        Maximum number of observations to download.
                        Observations are randomly chosen if more than the
                        maximum

  `-i IMAGES`, `--images IMAGES`
                        Maximum number of images per observation. Images are
                        randomly chosen if more than the maximum

  `-s {original,medium,square}`, `--size {original,medium,square}`
                        Image size

  `-d`, `--download`        Whether to download images (by default, only writes
                        URLs to output file). Images will be downloaded to a
                        folder with the same name as output file
                        
### Example

All of these do the same:

`python get_inaturalist_images.py --download "gorgulhos" weevils.txt`
`python get_inaturalist_images.py --download "weevils" weevils.txt`
`python get_inaturalist_images.py --download "Curculionoidea" weevils.txt`

The result is a file named `weevils.txt` containing URLs for 100 weevil images and a folder named `weevils` containing the downloaded images.
