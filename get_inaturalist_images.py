#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 11 15:02:59 2019

@author: Bruno A. S. de Medeiros
"""

import requests, argparse, sys, math, random, numpy as np, os, shutil

inaturalist_url = 'https://api.inaturalist.org/v1/'

def retrieve_taxon_id(taxon_name):
    res = requests.get(inaturalist_url + 'taxa/',
                 headers = {'Accept': 'application/json'},
                 params = {'q':taxon_name}).json()['results'][0]
    
    print('Matched taxon: ' + res['name'] + ' (' + res['preferred_common_name'] + ')', file=sys.stderr)
    return res['id']

def retrieve_photos_for_id(taxon_id, max_obs, max_photos, image_size):
    
    #first, let's see how many results
    n_res = requests.get(inaturalist_url + 'observations/',
                 headers = {'Accept': 'application/json'},
                 params = {'taxon_id': taxon_id,
                           'photos': 'true',
                           'verifiable': 'true',
                           'only_id': 'true',
                           'per_page':0}).json()['total_results']
    #message
    print(str(int(n_res)) + ' observations with images found.', file=sys.stderr)
    if n_res > 10000:
        print('Limiting search to the most recent 10000 observations because of API limitations.', file=sys.stderr)
        n_res = 10000
        
    if n_res <= max_obs:
        print('Downloading up to ' + 
              str(max_photos) + 
              ' image urls for ' + 
              str(n_res) +  
              ' observations.', file=sys.stderr)
    else:
        print('Downloading up to ' + 
              str(max_photos) + 
              ' image urls for ' + 
              str(max_obs) +  
              ' randomly chosen observations.', file=sys.stderr)
    
    #let's create an array to store results
    all_obs_ids = np.zeros(n_res, dtype=int)
    
    #now, let's download id numbers, 200 at a time
    #inaturalist api won't let more than that
    i = 0
    for page in range(1, math.ceil(n_res / 200)+1):
        res = requests.get(inaturalist_url + 'observations/',
                 headers = {'Accept': 'application/json'},
                 params = {'taxon_id': taxon_id,
                           'photos': 'true',
                           'verifiable': 'true',
                           'only_id': 'true',
                           'per_page': 200,
                           'page': page}).json()['results']
        for r in res:
            all_obs_ids[i] = r['id']
            i+=1
            
    #now let's randomly subsample observations if needed
    if n_res > max_obs:
        all_obs_ids = tuple(np.random.choice(all_obs_ids, size = max_obs, replace = False))
        
    #finally, let's retrieve image urls
    all_img_urls = np.empty(len(all_obs_ids) * max_photos, dtype=object)
    all_img_attribution = np.empty(len(all_obs_ids) * max_photos, dtype=object)
    i = 0
    
    for page in range(1, math.ceil(len(all_obs_ids) / 200)+1):
        res = requests.get(inaturalist_url + 'observations/',
                 headers = {'Accept': 'application/json'},
                 params = {'id': all_obs_ids,
                           'per_page': 200,
                           'page': page}).json()['results']
        for r in res:
            n_photos = len(r['observation_photos'])
            photos = random.sample(r['observation_photos'], min(n_photos,max_photos))
            for p in photos:
                if p['photo']['url'] is None:
                    print('Observation ' + 
                          str(r['id']) + 
                          ' has invalid photo URL, skipping',
                          file=sys.stderr)
                    i += 1
                else:                    
                    all_img_urls[i] = p['photo']['url'].replace('square',image_size)
                    all_img_attribution[i] = p['photo']['attribution']
                    i+=1
    
    idx_to_keep = [i for i in range(len(all_img_urls)) if all_img_urls[i] is not None]
    
    return (tuple([all_img_attribution[i] for i in idx_to_keep]),
            tuple([all_img_urls[i] for i in idx_to_keep]))
    

if __name__ == "__main__":
    
    #Let's start defining arguments
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('name', help = 'Name of the organism to search')
    parser.add_argument('-o','--observations', type = int, help = 'Maximum number of observations to download. Observations are randomly chosen if more than the maximum', default = 100)
    parser.add_argument('-i', '--images', type= int, help = 'Maximum number of images per observation. Images are randomly chosen if more than the maximum', default = 1)
    parser.add_argument('-s', '--size', help = 'Image size', choices=['original','medium','square'], default = 'medium')
    parser.add_argument('-d', '--download', help = 'Whether to download images (by default, only writes URLs to output file). Images will be downloaded to a folder with the same name as output file', action = 'store_true')
    parser.add_argument('output', help = 'Output file path', default = 'output.txt')
    
    args = parser.parse_args()
    #args = parser.parse_args(['caranguejo','crab']) #this is here for testing
    
    taxon_id = retrieve_taxon_id(args.name)
    attribution, photo_urls = retrieve_photos_for_id(taxon_id, 
                                        max_obs = args.observations, 
                                        max_photos = args.images, 
                                        image_size = args.size)
    with open(args.output,'w') as outfile:
        outfile.write('\n'.join(photo_urls))
        
    if args.download:
        out_dir = os.path.splitext(os.path.basename(args.output))[0]
        print('Now downloading image files to ' + out_dir, file=sys.stderr)
        os.makedirs(out_dir, exist_ok = True)
        ndigits = len(str(len(attribution)))
        
        with open(os.path.join(out_dir, 'attribution.txt'),'w') as outfile:
            for i, x in enumerate(attribution):
                print(str(i).zfill(ndigits) +
                      '.jpg' + '\t' + x, file = outfile)
        
        for i, url in enumerate(photo_urls):
            res = requests.get(url, stream = True)
            with open(os.path.join(out_dir,str(i).zfill(ndigits) + '.jpg'), 'wb') as outfile:
                shutil.copyfileobj(res.raw, outfile)
            del res
        
    
    
    
