from bs4 import BeautifulSoup
from pathlib import Path
import base64
import os
if not os.environ.get('RA_ARTIFACT_DIR'):
    raise RuntimeError('Set RA_ARTIFACT_DIR to the authorized local artifact directory.')
src=Path(os.environ['RA_ARTIFACT_DIR']).expanduser()/'Complete_SHAP_Analysis_Publication.html'
out=Path(os.environ.get('RA_OUTPUT_DIR','./outputs'))/'manuscript_figure_renders';out.mkdir(parents=True,exist_ok=True)
soup=BeautifulSoup(src.read_text(encoding='utf8',errors='ignore'),'html.parser')
imgs=[]
for img in soup.find_all('img'):
    s=img.get('src','')
    if s.startswith('data:image'):
        imgs.append(base64.b64decode(s.split(',',1)[1]))
assert len(imgs)==72,len(imgs)
mag=sorted(Path(os.environ.get('RA_DATA_PATH', 'uploads')).glob('magnitude__*.pdf'))
bee=sorted(Path(os.environ.get('RA_DATA_PATH', 'uploads')).glob('beeswarm__*.pdf'))
assert len(mag)==28 and len(bee)==28
for i,p in enumerate(mag):(out/(p.stem+'.png')).write_bytes(imgs[i])
for i,p in enumerate(bee):(out/(p.stem+'.png')).write_bytes(imgs[28+i])
panels=['NegRFandACCP','NoHandJointInvolvement','AsymmetricArthritis']
for j,o in enumerate(panels):(out/f'direction_panels__{o}__core_ridge_oof.png').write_bytes(imgs[56+j])
for j,o in enumerate(panels):(out/f'direction_contrast__{o}__core_ridge_oof.png').write_bytes(imgs[59+j])
for j,o in enumerate(['NoHandJointInvolvement','AsymmetricArthritis']):(out/f'method_agreement__{o}__xgboost.png').write_bytes(imgs[62+j])
water=['NegRFandACCP__core_ridge__primary','NegRFandACCP__refined_broad_ridge__secondary','NoHandJointInvolvement__core_ridge__primary','NoHandJointInvolvement__refined_broad_ridge__secondary','NoHandJointInvolvement__xgboost__exploratory_challenger','AsymmetricArthritis__core_ridge__primary','AsymmetricArthritis__refined_broad_ridge__secondary','AsymmetricArthritis__xgboost__exploratory_challenger']
for j,x in enumerate(water):(out/f'local_waterfalls__{x}.png').write_bytes(imgs[64+j])
print('extracted',len(list(out.glob('*.png'))),'figures')
