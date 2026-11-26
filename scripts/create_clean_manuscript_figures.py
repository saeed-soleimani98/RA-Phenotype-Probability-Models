import os
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import pandas as pd, numpy as np

OUT=Path(os.environ.get('RA_OUTPUT_DIR','./outputs'))/'manuscript_figure_renders';OUT.mkdir(parents=True,exist_ok=True)
if not os.environ.get('RA_ARTIFACT_DIR'):
    raise RuntimeError('Set RA_ARTIFACT_DIR to the authorized local artifact directory.')
ARTIFACT=Path(os.environ['RA_ARTIFACT_DIR']).expanduser()

# Remove the internal super-title from the calibration graphic. Panel titles and
# all axes are retained; the manuscript caption supplies the figure title.
from PIL import Image
cal=Image.open(ARTIFACT/'locked_models_flexible_calibration.png')
cal.crop((0,105,cal.width,cal.height)).save(OUT/'CLEAN_locked_models_flexible_calibration.png',quality=95)

NAVY='#17365D';TEAL='#167C80';BLUE='#365F91';ORANGE='#C77900';LIGHT='#F4F7FA';GRID='#D5DBE1'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.titlesize':11,'axes.labelsize':10,'pdf.fonttype':42})

def box(ax,xy,w,h,title,lines,color=NAVY,title_fs=11,body_fs=9.5):
    x,y=xy
    p=FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.012,rounding_size=0.012',fc=color,ec='white',lw=1.5)
    ax.add_patch(p)
    ax.text(x+w/2,y+h*.69,title,ha='center',va='center',color='white',weight='bold',fontsize=title_fs)
    ax.text(x+w/2,y+h*.30,lines,ha='center',va='center',color='white',fontsize=body_fs,linespacing=1.28)
    return p

def arrow(ax,a,b):
    ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=15,lw=1.8,color='#52616F',shrinkA=3,shrinkB=3,connectionstyle='arc3,rad=0'))

# Clean workflow without an internal title. The Word caption supplies the figure title.
fig,ax=plt.subplots(figsize=(8.3,9.5));ax.set_xlim(0,1);ax.set_ylim(0,1);ax.axis('off')
box(ax,(.15,.88),.70,.09,'Source cohort','820 patients; one completed rheumatology assessment',NAVY,12,10)
box(ax,(.12,.73),.76,.10,'Three outcomes modeled separately','Negative RF and anti-CCP: 164 events\nNo hand-joint involvement: 191 events | Asymmetric arthritis: 190 events',NAVY,12,9.5)
arrow(ax,(.50,.88),(.50,.83));arrow(ax,(.50,.73),(.27,.65));arrow(ax,(.50,.73),(.73,.65))
box(ax,(.06,.52),.41,.13,'Prespecified primary analysis','Seven-variable common core\nRidge logistic regression\nRepeated nested 5-fold CV × 10 repeats',TEAL,11,9.2)
box(ax,(.53,.52),.41,.13,'Secondary and exploratory analyses','Outcome-specific broad penalized models\nSVC, random forest, AdaBoost, and XGBoost\nTuning confined to training data',BLUE,11,8.9)
arrow(ax,(.265,.52),(.265,.45));arrow(ax,(.735,.52),(.735,.45))
box(ax,(.06,.31),.41,.13,'Validation and robustness','Patient-averaged OOF predictions\nCalibration and paired bootstrap intervals\nDomain removal, missingness, and stability',TEAL,11,9)
box(ax,(.53,.31),.41,.13,'Explainability','Signed patient-level OOF linear SHAP\nOuter-test permutation importance\nTreeSHAP and Kernel SHAP method audit',BLUE,11,9)
arrow(ax,(.265,.31),(.42,.23));arrow(ax,(.735,.31),(.58,.23))
box(ax,(.15,.08),.70,.12,'Frozen research package','Eight pipelines refitted to all 820 patients\nNo apparent full-cohort performance reported\nExternal validation required before clinical evaluation',NAVY,12,9.6)
fig.tight_layout(pad=.25);fig.savefig(OUT/'CLEAN_analysis_workflow.png',dpi=400,bbox_inches='tight',facecolor='white');plt.close(fig)

# Clean directional contrasts from the audited summary.
d=pd.read_csv(ARTIFACT/'directional_oof_shap_summary.csv')
labels={'RADurationDays':'RA duration','DASJointCountTEN28':'Tender 28-joint count','DASJointCountSW':'Swollen 28-joint count','PatientGlobalAssessment':'Patient global assessment','AbnormalCRPorESR':'Abnormal CRP or ESR','Age':'Age'}
outcomes=[('NegRFandACCP','Negative RF and anti-CCP'),('NoHandJointInvolvement','No hand-joint involvement'),('AsymmetricArthritis','Asymmetric arthritis')]
paths=[]
for outcome,title in outcomes:
    z=d[(d.outcome==outcome)&(d.model=='core_ridge')&d.feature.isin(labels)].copy()
    z=z.sort_values('high_minus_low')
    y=np.arange(len(z));colors=np.where(z.high_minus_low>=0,'#B43B4D','#2F80B7')
    fig,ax=plt.subplots(figsize=(8.2,4.7))
    ax.barh(y,z.high_minus_low,color=colors,height=.68)
    ax.set_yticks(y,labels=[labels[x] for x in z.feature]);ax.axvline(0,color='#222222',lw=.9)
    ax.set_xlabel('Mean signed OOF SHAP contrast: high/present minus low/absent',labelpad=8)
    ax.set_title(title,loc='left',fontweight='bold',pad=10)
    ax.grid(axis='x',color=GRID,lw=.7);ax.grid(axis='y',visible=False)
    for s in ['top','right']:ax.spines[s].set_visible(False)
    fig.subplots_adjust(left=.29,right=.98,top=.88,bottom=.20)
    p=OUT/f'CLEAN_direction_contrast__{outcome}.png';fig.savefig(p,dpi=400,facecolor='white');plt.close(fig);paths.append(p)

# Stack clean contrasts with ample separation and no repeated subtitles.
from PIL import Image
ims=[Image.open(p).convert('RGB') for p in paths];w=max(i.width for i in ims);gap=80
res=[]
for i in ims:
    if i.width!=w:i=i.resize((w,round(i.height*w/i.width)),Image.Resampling.LANCZOS)
    res.append(i)
canvas=Image.new('RGB',(w,sum(i.height for i in res)+gap*2),'white');y=0
for i in res:canvas.paste(i,(0,y));y+=i.height+gap
canvas.save(OUT/'CLEAN_MAIN_direction_contrasts.png',dpi=(300,300),optimize=True)
print('created clean manuscript figures')
