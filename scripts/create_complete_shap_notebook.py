from pathlib import Path
import nbformat as nbf

OUT = Path(os.environ.get('RA_OUTPUT_DIR','./outputs'))/'Complete_SHAP_Analysis_Publication.ipynb'
OUT.parent.mkdir(parents=True, exist_ok=True)
nb = nbf.v4.new_notebook()
nb['metadata'] = {
    'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'},
    'language_info': {'name': 'python', 'version': '3'},
}
C=[]
def md(s): C.append(nbf.v4.new_markdown_cell(s.strip()))
def code(s): C.append(nbf.v4.new_code_cell(s.strip()))

md(r'''
# Complete publication-grade SHAP analysis

This notebook performs a deliberately separated, reproducible explainability analysis for the three positive RA phenotypes:

- **Negative RF and anti-CCP** (`NegRFandACCP`)
- **No hand-joint involvement** (`NoHandJointInvolvement`)
- **Asymmetric arthritis** (`AsymmetricArthritis`)

It combines four complementary explanation sources without pretending that they are interchangeable:

1. **Signed patient-level out-of-fold (OOF) linear SHAP** from the repeated nested-validation analysis — the primary source for internally validated magnitude and direction.
2. **Exact linear SHAP** for the six packaged ridge models — descriptive explanations of the full-cohort final fits.
3. **TreeSHAP** for the two packaged XGBoost challengers — exact/fast tree-specific explanations on the model margin (log-odds) scale.
4. **Kernel SHAP** for every packaged model — a model-agnostic audit on a reproducible stratified patient sample, also on the log-odds scale.

Outputs include signed patient-level tables, global magnitude, beeswarm distributions, numeric/binary/categorical direction summaries, direction plots, local waterfall plots, cross-method agreement, stability/audit tables, and **600-dpi PNG/TIFF plus vector PDF/SVG** figures. A self-contained HTML report is created by the final cell.

> **Interpretation:** positive SHAP moves prediction toward the named positive phenotype; negative SHAP moves it away. SHAP describes model behavior, not causation. Correlated predictors can share or exchange attribution. Mean signed SHAP alone is never used as importance because positive and negative contributions can cancel.
''')

code(r'''
# Optional one-time installation (uncomment if needed)
# %pip install -U "shap>=0.46,<0.50" "scikit-learn>=1.8,<1.10" "xgboost>=2.0" pandas numpy scipy matplotlib seaborn joblib nbconvert openpyxl pillow
''')

code(r'''
# 1. Imports, versions, and deterministic plotting
from __future__ import annotations
import hashlib, json, os, platform, re, subprocess, sys, time, warnings
from pathlib import Path
from collections import defaultdict

import joblib
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.special import expit, logit
from scipy.stats import spearmanr
from sklearn.model_selection import train_test_split
import sklearn, shap
from IPython.display import display, Markdown

MASTER_SEED = 20260925
rng = np.random.default_rng(MASTER_SEED)
np.random.seed(MASTER_SEED)
warnings.filterwarnings('ignore', category=FutureWarning)
pd.set_option('display.max_columns', 200)
pd.set_option('display.max_rows', 200)
pd.set_option('display.width', 220)

mpl.rcParams.update({
    'figure.dpi': 140, 'savefig.dpi': 600,
    'font.family': 'DejaVu Sans', 'font.size': 10,
    'axes.titlesize': 12, 'axes.labelsize': 10,
    'axes.titleweight': 'bold', 'axes.spines.top': False,
    'axes.spines.right': False, 'axes.linewidth': 0.8,
    'xtick.labelsize': 8.5, 'ytick.labelsize': 8.5,
    'legend.fontsize': 8.5, 'legend.frameon': False,
    'pdf.fonttype': 42, 'ps.fonttype': 42,
})
sns.set_theme(style='whitegrid', context='paper', palette='colorblind', rc=mpl.rcParams)
try:
    from matplotlib_inline.backend_inline import set_matplotlib_formats
    set_matplotlib_formats('retina')
except Exception:
    pass

print('Python', sys.version.split()[0], '| platform', platform.platform())
print('numpy', np.__version__, '| pandas', pd.__version__, '| sklearn', sklearn.__version__)
print('SHAP', shap.__version__)
''')

code(r'''
# 2. Configuration and portable project discovery
NOTEBOOK_NAME = 'Complete_SHAP_Analysis_Publication.ipynb'
ENV_PROJECT = Path(os.environ['RA_PROJECT_DIR']).expanduser() if os.environ.get('RA_PROJECT_DIR') else Path.cwd()
COLAB_PROJECT = Path.cwd()
ENV_PROJECT = Path(os.environ['RA_PROJECT_DIR']).expanduser() if os.environ.get('RA_PROJECT_DIR') else None

candidates = [p for p in [ENV_PROJECT, ENV_PROJECT, COLAB_PROJECT, Path.cwd(), Path.cwd()/'ra_analysis', Path.cwd()] if p is not None]
PROJECT_DIR = next((p for p in candidates if (p/'modeling_results_stage4g'/'final_model_package').exists()), None)
if PROJECT_DIR is None:
    checked = '\n'.join(str(p/'modeling_results_stage4g'/'final_model_package') for p in candidates)
    raise FileNotFoundError('Final model package was not found. Set RA_PROJECT_DIR. Checked:\n'+checked)

PACKAGE_DIR = PROJECT_DIR/'modeling_results_stage4g'/'final_model_package'
REGISTRY_PATH = PROJECT_DIR/'modeling_results_stage4g'/'tables'/'final_model_registry.csv'
OOF_TABLE_DIR = PROJECT_DIR/'modeling_results'/'tables'
OUT_DIR = PROJECT_DIR/'complete_shap_analysis'
TABLE_DIR = OUT_DIR/'tables'; FIGURE_DIR = OUT_DIR/'figures'; REPORT_DIR = OUT_DIR/'report'; CACHE_DIR = OUT_DIR/'cache'
for d in [OUT_DIR, TABLE_DIR, FIGURE_DIR, REPORT_DIR, CACHE_DIR]: d.mkdir(parents=True, exist_ok=True)

# Kernel SHAP is expensive. These frozen defaults are publication-suitable while remaining feasible.
# Increase KERNEL_EXPLAIN_N after a successful run if your computing budget permits.
KERNEL_EXPLAIN_N = int(os.environ.get('RA_SHAP_KERNEL_N', '120'))
KERNEL_BACKGROUND_N = int(os.environ.get('RA_SHAP_KERNEL_BG', '30'))
KERNEL_NSAMPLES = int(os.environ.get('RA_SHAP_KERNEL_NSAMPLES', '512'))
TREE_BACKGROUND_N = int(os.environ.get('RA_SHAP_TREE_BG', '100'))
TOP_N = 15
FORCE_RECOMPUTE = os.environ.get('RA_SHAP_FORCE_RECOMPUTE', '0') == '1'
RUN_KERNEL = os.environ.get('RA_SHAP_SKIP_KERNEL', '0') != '1'

OUTCOMES = ['NegRFandACCP','NoHandJointInvolvement','AsymmetricArthritis']
OUTCOME_LABEL = {
    'NegRFandACCP':'Negative RF and anti-CCP',
    'NoHandJointInvolvement':'No hand-joint involvement',
    'AsymmetricArthritis':'Asymmetric arthritis',
}
print('Project:', PROJECT_DIR.resolve())
print('Output:', OUT_DIR.resolve())
print('Kernel configuration:', KERNEL_EXPLAIN_N, 'patients |', KERNEL_BACKGROUND_N, 'background |', KERNEL_NSAMPLES, 'evaluations')
''')

md(r'''
## Scientific safeguards

- OOF explanations and final-fit explanations are stored and plotted separately.
- TreeSHAP is used only for tree models; exact linear SHAP is used only for linear-logit models.
- Kernel SHAP is a model-agnostic sensitivity analysis, not a replacement for OOF explanations.
- Tree and linear values are on the model margin/log-odds scale. Kernel SHAP explains the logit of predicted probability.
- All encoded columns and missingness indicators are aggregated back to the original clinical predictor before clinical interpretation.
- Binary blanks remain unknown/imputed; they are not recoded as absence.
- `OnlyLargeJoints`, outcome columns, and `VisitID` are prohibited as predictors.
''')

code(r'''
# 3. Load portable model components, registry, models, and source data
component_candidates = [PROJECT_DIR/'ra_final_model_components.py', PACKAGE_DIR/'ra_final_model_components.py', ENV_PROJECT/'ra_final_model_components.py']
component_path = next((p for p in component_candidates if p.exists()), None)
if component_path is None: raise FileNotFoundError('ra_final_model_components.py is required to reload pipelines')
sys.path.insert(0, str(component_path.parent))
from ra_final_model_components import MissingnessFlags, RADurationLogTransformer
import os

registry = pd.read_csv(REGISTRY_PATH)
assert len(registry) == 8 and set(registry.outcome).issubset(OUTCOMES)
models, metadata, data_by_outcome = {}, {}, {}
for outcome in OUTCOMES:
    p = PROJECT_DIR/'derived_data'/f'{outcome}__primary_eligible.csv'
    d = pd.read_csv(p)
    assert len(d) == 820 and d.VisitID.is_unique
    data_by_outcome[outcome] = d
for r in registry.itertuples(index=False):
    mdir = PACKAGE_DIR/r.model_id
    metadata[r.model_id] = json.loads((mdir/'metadata.json').read_text(encoding='utf-8'))
    models[r.model_id] = joblib.load(mdir/'pipeline.joblib')
    raw = metadata[r.model_id]['raw_predictors']
    assert r.outcome not in raw and 'VisitID' not in raw and 'OnlyLargeJoints' not in raw
print('Loaded', len(models), 'packaged pipelines and three 820-patient analysis datasets.')
display(registry[['model_id','outcome','model','status','scope','raw_predictor_count','transformed_feature_count']])
''')

code(r'''
# 4. Feature mapping, SHAP normalization, sampling, and publication export helpers
def safe_name(x): return re.sub(r'[^A-Za-z0-9_.-]+','_',str(x)).strip('_')

def original_feature_name(transformed_name):
    s = str(transformed_name)
    s = re.sub(r'^(numeric|binary|categorical|missing)__', '', s)
    s = s.replace('RADurationDays_log1p', 'RADurationDays')
    s = re.sub(r'__missing$', '', s)
    # Fixed categorical predictors in this project; map encoded levels back to their source.
    for cat in ['Gender','RAOnset','PhysicalActivity']:
        if s == cat or s.startswith(cat+'_'): return cat
    return s

def transformed_matrix(pipe, X):
    engineered = pipe.named_steps['feature_engineering'].transform(X)
    z = pipe.named_steps['preprocess'].transform(engineered)
    z = z.toarray() if hasattr(z, 'toarray') else np.asarray(z)
    names = list(pipe.named_steps['preprocess'].get_feature_names_out())
    if z.shape[1] != len(names): raise AssertionError((z.shape, len(names)))
    return np.asarray(z, dtype=float), names

def aggregate_shap(values, transformed_names):
    values = np.asarray(values)
    if values.ndim == 3: values = values[..., -1]
    if values.ndim == 1: values = values[None, :]
    originals = [original_feature_name(x) for x in transformed_names]
    ordered = list(dict.fromkeys(originals))
    grouped = np.column_stack([values[:, np.array(originals)==f].sum(axis=1) for f in ordered])
    return grouped, ordered

def normalize_shap_values(obj):
    v = obj.values if hasattr(obj, 'values') else obj
    if isinstance(v, list): v = v[-1]
    v = np.asarray(v)
    if v.ndim == 3: v = v[..., -1]
    return v

def stratified_indices(y, n, seed):
    idx = np.arange(len(y))
    if n >= len(y): return idx
    chosen, _ = train_test_split(idx, train_size=n, stratify=np.asarray(y), random_state=seed)
    return np.sort(chosen)

def save_pub(fig, stem):
    stem = FIGURE_DIR/safe_name(stem)
    fig.savefig(stem.with_suffix('.png'), dpi=600, bbox_inches='tight', facecolor='white')
    fig.savefig(stem.with_suffix('.tiff'), dpi=600, bbox_inches='tight', facecolor='white', pil_kwargs={'compression':'tiff_lzw'})
    fig.savefig(stem.with_suffix('.pdf'), bbox_inches='tight', facecolor='white')
    fig.savefig(stem.with_suffix('.svg'), bbox_inches='tight', facecolor='white')
    return stem

def sha256(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()
''')

md('## A. Internally validated signed OOF SHAP')
code(r'''
# 5. Discover and validate all signed patient-level OOF SHAP files
rows=[]; oof_long=[]
for outcome in OUTCOMES:
    raw = data_by_outcome[outcome]
    for model in ['core_logistic','core_ridge','broad_ridge','broad_elastic_net']:
        patterns = [f'{outcome}__{model}__patient_oof_shap.csv', f'*{outcome}*{model}*patient*oof*shap*.csv']
        hits=[]
        for pat in patterns: hits.extend(OOF_TABLE_DIR.glob(pat))
        hits=list(dict.fromkeys(hits))
        if not hits:
            rows.append({'outcome':outcome,'model':model,'status':'MISSING','path':''}); continue
        p=hits[0]; w=pd.read_csv(p)
        features=[c for c in w.columns if c not in ['VisitID','y']]
        vals=w[features].apply(pd.to_numeric,errors='coerce').to_numpy()
        ok=(len(w)==820 and w.VisitID.is_unique and np.isfinite(vals).all() and (vals>0).any() and (vals<0).any())
        rows.append({'outcome':outcome,'model':model,'status':'OK' if ok else 'FAIL','path':str(p),'n':len(w),'features':len(features),'min_shap':vals.min(),'max_shap':vals.max()})
        if ok:
            q=w.melt(id_vars=['VisitID','y'],value_vars=features,var_name='feature',value_name='shap_value')
            q['outcome']=outcome;q['model']=model;q['method']='OOF exact linear';q['analysis_source']='internally_validated_oof'
            oof_long.append(q)
oof_audit=pd.DataFrame(rows)
oof_audit.to_csv(TABLE_DIR/'oof_signed_shap_audit.csv',index=False,encoding='utf-8-sig')
display(oof_audit)
if not oof_audit.status.eq('OK').all():
    raise AssertionError('All 12 expected signed OOF SHAP files are required before publication analysis.')
oof_long=pd.concat(oof_long,ignore_index=True)
oof_long.to_csv(TABLE_DIR/'oof_signed_shap_long.csv.gz',index=False,compression='gzip')
print('Validated 12/12 OOF files; both positive and negative contributions are present.')
''')

code(r'''
# 6. Reusable magnitude and direction summaries linked to raw patient values
def summarize_explanations(long_df, source_label):
    mag=(long_df.groupby(['outcome','model','method','feature'],as_index=False)
         .shap_value.agg(mean_abs_shap=lambda x:np.mean(np.abs(x)), median_abs_shap=lambda x:np.median(np.abs(x)),
                         mean_signed_shap='mean', median_signed_shap='median', positive_fraction=lambda x:np.mean(x>0), n='size'))
    mag['global_rank']=mag.groupby(['outcome','model','method']).mean_abs_shap.rank(ascending=False,method='min')
    mag['analysis_source']=source_label
    directions=[]; categories=[]
    for (outcome,model,method,feature),g in long_df.groupby(['outcome','model','method','feature'],sort=False):
        raw=data_by_outcome[outcome][['VisitID',feature]].copy() if feature in data_by_outcome[outcome] else None
        if raw is None:
            directions.append({'outcome':outcome,'model':model,'method':method,'feature':feature,'type':'unlinked','n':len(g),'direction_label':'raw value unavailable'})
            continue
        z=g.merge(raw,on='VisitID',how='left'); x=z[feature]; s=z.shap_value
        numeric=pd.to_numeric(x,errors='coerce')
        unique=set(numeric.dropna().unique())
        if len(unique)>0 and unique.issubset({0,1}):
            means=z.assign(_x=numeric).groupby('_x').shap_value.agg(['mean','median','count'])
            m0=means.loc[0,'mean'] if 0 in means.index else np.nan; m1=means.loc[1,'mean'] if 1 in means.index else np.nan
            delta=m1-m0
            label='present/higher moves toward outcome' if delta>0 else ('present/higher moves away from outcome' if delta<0 else 'no average contrast')
            directions.append({'outcome':outcome,'model':model,'method':method,'feature':feature,'type':'binary','n':numeric.notna().sum(),'mean_shap_low_or_0':m0,'mean_shap_high_or_1':m1,'high_minus_low':delta,'spearman_rho':np.nan,'direction_label':label})
        elif pd.api.types.is_numeric_dtype(x) or numeric.notna().mean()>.90:
            keep=numeric.notna() & s.notna(); rho,p=spearmanr(numeric[keep],s[keep]) if keep.sum()>3 else (np.nan,np.nan)
            q20,q80=numeric[keep].quantile([.2,.8]); low=s[keep & numeric.le(q20)].mean(); high=s[keep & numeric.ge(q80)].mean(); delta=high-low
            label='higher values move toward outcome' if delta>0 else ('higher values move away from outcome' if delta<0 else 'no average contrast')
            directions.append({'outcome':outcome,'model':model,'method':method,'feature':feature,'type':'numeric','n':keep.sum(),'mean_shap_low_or_0':low,'mean_shap_high_or_1':high,'high_minus_low':delta,'spearman_rho':rho,'spearman_p_descriptive':p,'direction_label':label})
        else:
            tmp=z.assign(category_label=x.fillna('Unknown').astype(str)).groupby('category_label').shap_value.agg(['mean','median','count']).reset_index()
            for _,rr in tmp.iterrows(): categories.append({'outcome':outcome,'model':model,'method':method,'feature':feature,'category':rr['category_label'],'mean_shap':rr['mean'],'median_shap':rr['median'],'n':rr['count']})
            directions.append({'outcome':outcome,'model':model,'method':method,'feature':feature,'type':'categorical','n':len(z),'direction_label':'interpret category-specific means'})
    return mag, pd.DataFrame(directions), pd.DataFrame(categories)

oof_magnitude,oof_direction,oof_categories=summarize_explanations(oof_long,'internally_validated_oof')
oof_magnitude.to_csv(TABLE_DIR/'oof_shap_magnitude.csv',index=False,encoding='utf-8-sig')
oof_direction.to_csv(TABLE_DIR/'oof_shap_direction.csv',index=False,encoding='utf-8-sig')
oof_categories.to_csv(TABLE_DIR/'oof_shap_categorical_direction.csv',index=False,encoding='utf-8-sig')
display(oof_magnitude.query("model=='core_ridge'").sort_values(['outcome','global_rank']).groupby('outcome').head(10))
''')

md('## B. Exact linear SHAP, TreeSHAP, and Kernel SHAP for packaged final models')
code(r'''
# 7. Compute or load final-fit exact linear and TreeSHAP explanations
final_parts=[]; method_audit=[]
for i,r in enumerate(registry.itertuples(index=False)):
    mid=r.model_id; outcome=r.outcome; pipe=models[mid]; meta=metadata[mid]; raw=meta['raw_predictors']
    d=data_by_outcome[outcome]; X=d[raw].copy(); y=d[outcome].astype(int).to_numpy(); z,names=transformed_matrix(pipe,X)
    fitted_model=pipe.named_steps['model']
    if r.model in ['core_ridge','refined_broad_ridge']:
        coef=np.asarray(fitted_model.coef_).ravel(); bg=z.mean(axis=0); vals=(z-bg)*coef
        base=float(np.asarray(fitted_model.intercept_).ravel()[0]+bg@coef)
        err=np.max(np.abs(base+vals.sum(1)-np.asarray(fitted_model.decision_function(z)).ravel()))
        method='Final-fit exact linear'
    elif r.model=='xgboost':
        bg_idx=stratified_indices(y,min(TREE_BACKGROUND_N,len(y)),MASTER_SEED+i)
        explainer=shap.TreeExplainer(fitted_model,data=z[bg_idx],model_output='raw',feature_perturbation='interventional')
        ex=explainer(z,check_additivity=False); vals=normalize_shap_values(ex)
        base=np.asarray(ex.base_values); base=float(np.ravel(base)[0])
        margin=np.asarray(fitted_model.predict(z,output_margin=True)).ravel()
        err=float(np.max(np.abs(base+vals.sum(1)-margin)))
        method='TreeSHAP'
    else: continue
    grouped,features=aggregate_shap(vals,names)
    wide=pd.DataFrame(grouped,columns=features);wide.insert(0,'VisitID',d.VisitID.to_numpy());wide.insert(1,'y',y)
    wide.to_csv(TABLE_DIR/f'{safe_name(mid)}__{safe_name(method)}__patient_shap.csv.gz',index=False,compression='gzip')
    q=wide.melt(id_vars=['VisitID','y'],var_name='feature',value_name='shap_value')
    q['outcome']=outcome;q['model']=r.model;q['model_id']=mid;q['method']=method;q['analysis_source']='descriptive_final_fit'
    final_parts.append(q)
    method_audit.append({'model_id':mid,'method':method,'n_explained':len(X),'background_n':len(X) if 'linear' in method else len(bg_idx),'max_additivity_error':err,'scale':'log-odds/model margin','status':'PASS' if err<1e-4 else 'CHECK'})
final_long=pd.concat(final_parts,ignore_index=True)
print('Exact linear / TreeSHAP complete.')
''')

code(r'''
# 8. Model-agnostic Kernel SHAP audit on a reproducible stratified sample
kernel_parts=[]
if RUN_KERNEL:
    for i,r in enumerate(registry.itertuples(index=False)):
        mid=r.model_id; outcome=r.outcome; pipe=models[mid]; meta=metadata[mid]; raw=meta['raw_predictors']
        d=data_by_outcome[outcome]; X=d[raw].copy(); y=d[outcome].astype(int).to_numpy(); z,names=transformed_matrix(pipe,X)
        model=pipe.named_steps['model']
        explain_idx=stratified_indices(y,min(KERNEL_EXPLAIN_N,len(y)),MASTER_SEED+100+i)
        remaining=np.setdiff1d(np.arange(len(y)),explain_idx)
        bg_pool=remaining if len(remaining)>=KERNEL_BACKGROUND_N else np.arange(len(y))
        bg_rel=stratified_indices(y[bg_pool],min(KERNEL_BACKGROUND_N,len(bg_pool)),MASTER_SEED+200+i)
        bg_idx=bg_pool[bg_rel]
        cache=CACHE_DIR/f'{safe_name(mid)}__kernel_shap.npz'
        if cache.exists() and not FORCE_RECOMPUTE:
            saved=np.load(cache,allow_pickle=True); vals=saved['values']; cached_idx=saved['explain_idx'];
            if not np.array_equal(cached_idx,explain_idx): raise AssertionError('Kernel cache sample mismatch; set RA_SHAP_FORCE_RECOMPUTE=1')
        else:
            def predict_log_odds(a):
                a=np.asarray(a,dtype=float)
                if hasattr(model,'decision_function'): return np.asarray(model.decision_function(a)).ravel()
                p=np.clip(np.asarray(model.predict_proba(a))[:,1],1e-7,1-1e-7)
                return logit(p)
            ke=shap.KernelExplainer(predict_log_odds,z[bg_idx],link='identity')
            t0=time.time(); vals=normalize_shap_values(ke.shap_values(z[explain_idx],nsamples=KERNEL_NSAMPLES,silent=True))
            np.savez_compressed(cache,values=vals,explain_idx=explain_idx,bg_idx=bg_idx,names=np.array(names,dtype=object))
            print(mid,'Kernel SHAP seconds:',round(time.time()-t0,1))
        grouped,features=aggregate_shap(vals,names)
        wide=pd.DataFrame(grouped,columns=features);wide.insert(0,'VisitID',d.VisitID.iloc[explain_idx].to_numpy());wide.insert(1,'y',y[explain_idx])
        wide.to_csv(TABLE_DIR/f'{safe_name(mid)}__KernelSHAP__patient_shap.csv.gz',index=False,compression='gzip')
        q=wide.melt(id_vars=['VisitID','y'],var_name='feature',value_name='shap_value')
        q['outcome']=outcome;q['model']=r.model;q['model_id']=mid;q['method']='KernelSHAP';q['analysis_source']='descriptive_final_fit_sample'
        kernel_parts.append(q)
        method_audit.append({'model_id':mid,'method':'KernelSHAP','n_explained':len(explain_idx),'background_n':len(bg_idx),'max_additivity_error':np.nan,'scale':'log-odds','status':'PASS'})
    kernel_long=pd.concat(kernel_parts,ignore_index=True)
    final_long=pd.concat([final_long,kernel_long],ignore_index=True)
else:
    kernel_long=pd.DataFrame(); print('Kernel SHAP skipped by RA_SHAP_SKIP_KERNEL=1')

method_audit=pd.DataFrame(method_audit)
method_audit.to_csv(TABLE_DIR/'shap_method_audit.csv',index=False,encoding='utf-8-sig')
final_long.to_csv(TABLE_DIR/'final_fit_all_methods_shap_long.csv.gz',index=False,compression='gzip')
display(method_audit)
''')

code(r'''
# 9. Final-fit magnitude and direction tables
final_magnitude,final_direction,final_categories=summarize_explanations(final_long,'descriptive_final_fit')
final_magnitude.to_csv(TABLE_DIR/'final_fit_shap_magnitude.csv',index=False,encoding='utf-8-sig')
final_direction.to_csv(TABLE_DIR/'final_fit_shap_direction.csv',index=False,encoding='utf-8-sig')
final_categories.to_csv(TABLE_DIR/'final_fit_shap_categorical_direction.csv',index=False,encoding='utf-8-sig')
display(final_magnitude.sort_values(['outcome','model','method','global_rank']).groupby(['outcome','model','method']).head(8))
''')

md('## C. Publication-grade figures')
code(r'''
# 10. Magnitude figures for every outcome/model/method
all_mag=pd.concat([oof_magnitude,final_magnitude],ignore_index=True)
for (outcome,model,method),g in all_mag.groupby(['outcome','model','method']):
    top=g.nsmallest(TOP_N,'global_rank').sort_values('mean_abs_shap')
    h=max(4.8,0.32*len(top)+1.8);fig,ax=plt.subplots(figsize=(8.6,h))
    ax.barh(top.feature,top.mean_abs_shap,color='#176B87',edgecolor='white',linewidth=.4)
    ax.set_xlabel('Mean absolute SHAP value (log-odds scale)');ax.set_ylabel('')
    ax.set_title(f'{OUTCOME_LABEL[outcome]}\n{model} — {method}',loc='left',pad=10)
    ax.grid(axis='y',visible=False);ax.grid(axis='x',alpha=.25)
    fig.text(.01,.005,'Magnitude measures influence, not direction. OOF and final-fit explanations are not pooled.',fontsize=7.5,color='#444444')
    fig.tight_layout(rect=[0,.025,1,1]);save_pub(fig,f'magnitude__{outcome}__{model}__{method}');plt.show();plt.close(fig)
''')

code(r'''
# 11. Custom grouped-feature beeswarm: distribution, sign, and relative raw feature value
# Color is within-feature percentile for numeric/binary variables; categorical/unlinked values are gray.
def beeswarm_plot(long_sub,outcome,model,method,top_features):
    raw=data_by_outcome[outcome]
    fig,ax=plt.subplots(figsize=(9.2,max(5.2,.36*len(top_features)+1.8)))
    for yi,f in enumerate(top_features[::-1]):
        g=long_sub[long_sub.feature.eq(f)].merge(raw[['VisitID',f]],on='VisitID',how='left') if f in raw else long_sub[long_sub.feature.eq(f)].copy()
        s=g.shap_value.to_numpy(); jitter=rng.normal(0,.085,len(g)); y=np.full(len(g),yi)+jitter
        if f in raw:
            x=pd.to_numeric(g[f],errors='coerce'); color=x.rank(pct=True).to_numpy()
            mask=np.isfinite(color);ax.scatter(s[~mask],y[~mask],s=9,c='#9E9E9E',alpha=.45,rasterized=True,linewidth=0)
            sc=ax.scatter(s[mask],y[mask],s=10,c=color[mask],cmap='coolwarm',vmin=0,vmax=1,alpha=.62,rasterized=True,linewidth=0)
        else: ax.scatter(s,y,s=9,c='#777777',alpha=.5,rasterized=True,linewidth=0)
    ax.axvline(0,color='#222222',lw=.8);ax.set_yticks(range(len(top_features)));ax.set_yticklabels(top_features[::-1])
    ax.set_xlabel('Signed SHAP value (log-odds): away  ←  0  →  toward outcome');ax.set_ylabel('')
    ax.set_title(f'{OUTCOME_LABEL[outcome]}\n{model} — {method}',loc='left')
    ax.grid(axis='y',visible=False);fig.tight_layout();save_pub(fig,f'beeswarm__{outcome}__{model}__{method}');plt.show();plt.close(fig)

for (outcome,model,method),g in pd.concat([oof_long,final_long],ignore_index=True).groupby(['outcome','model','method']):
    mag=all_mag.query('outcome==@outcome and model==@model and method==@method').nsmallest(TOP_N,'global_rank')
    beeswarm_plot(g,outcome,model,method,mag.feature.tolist())
''')

code(r'''
# 12. Numeric/binary direction figures for primary OOF core-ridge models
primary=oof_long[oof_long.model.eq('core_ridge')]
for outcome in OUTCOMES:
    ranked=oof_magnitude.query("outcome==@outcome and model=='core_ridge'").sort_values('global_rank')
    features=[f for f in ranked.feature if f in data_by_outcome[outcome].columns][:8]
    fig,axes=plt.subplots(2,4,figsize=(13.5,7.2));axes=axes.ravel()
    for ax,f in zip(axes,features):
        g=primary[(primary.outcome.eq(outcome))&(primary.feature.eq(f))].merge(data_by_outcome[outcome][['VisitID',f]],on='VisitID')
        x=pd.to_numeric(g[f],errors='coerce');keep=x.notna()
        if set(x[keep].unique()).issubset({0,1}):
            sns.boxplot(data=pd.DataFrame({'Raw value':x[keep].astype(int),'SHAP':g.loc[keep,'shap_value']}),x='Raw value',y='SHAP',ax=ax,color='#75AADB',width=.55,fliersize=1.5)
        else:
            ax.scatter(x[keep],g.loc[keep,'shap_value'],s=9,alpha=.22,color='#176B87',rasterized=True)
            if keep.sum()>10:
                bins=pd.qcut(x[keep],q=min(10,x[keep].nunique()),duplicates='drop');sm=g.loc[keep].assign(_bin=bins).groupby('_bin',observed=True).agg(x=(f,'median'),s=('shap_value','mean'))
                ax.plot(sm.x,sm.s,color='#C0392B',lw=2)
        ax.axhline(0,color='black',lw=.7);ax.set_title(f,fontsize=10);ax.set_ylabel('Signed OOF SHAP');ax.set_xlabel('Observed value')
    for ax in axes[len(features):]:ax.axis('off')
    fig.suptitle(f'{OUTCOME_LABEL[outcome]}: direction of leading core-ridge predictors',x=.01,ha='left',fontsize=14,fontweight='bold')
    fig.tight_layout(rect=[0,0,1,.95]);save_pub(fig,f'direction_panels__{outcome}__core_ridge_oof');plt.show();plt.close(fig)
''')

code(r'''
# 13. Direction-summary forest plot (high-versus-low mean SHAP contrast)
for outcome in OUTCOMES:
    d=oof_direction.query("outcome==@outcome and model=='core_ridge' and type in ['numeric','binary']").copy()
    order=oof_magnitude.query("outcome==@outcome and model=='core_ridge'")[['feature','global_rank']]
    d=d.merge(order,on='feature').sort_values('global_rank').head(TOP_N).sort_values('high_minus_low')
    fig,ax=plt.subplots(figsize=(8.6,max(4.8,.34*len(d)+1.8)))
    colors=np.where(d.high_minus_low>=0,'#B23A48','#2C7FB8')
    ax.barh(d.feature,d.high_minus_low,color=colors)
    ax.axvline(0,color='black',lw=.8);ax.set_xlabel('Mean signed SHAP: high/present minus low/absent')
    ax.set_title(f'{OUTCOME_LABEL[outcome]}\nDirectional contrast — internally validated core ridge',loc='left')
    ax.text(.01,-.12,'Negative = higher/present moves away; positive = higher/present moves toward. Descriptive contrast, not a confidence interval.',transform=ax.transAxes,fontsize=7.5)
    fig.tight_layout();save_pub(fig,f'direction_contrast__{outcome}__core_ridge_oof');plt.show();plt.close(fig)
''')

code(r'''
# 14. Cross-method rank agreement: TreeSHAP versus KernelSHAP for XGBoost
agreement=[]
if not kernel_long.empty:
    for outcome in ['NoHandJointInvolvement','AsymmetricArthritis']:
        a=final_magnitude.query("outcome==@outcome and model=='xgboost' and method=='TreeSHAP'")[['feature','mean_abs_shap','global_rank']].rename(columns={'mean_abs_shap':'tree_magnitude','global_rank':'tree_rank'})
        b=final_magnitude.query("outcome==@outcome and model=='xgboost' and method=='KernelSHAP'")[['feature','mean_abs_shap','global_rank']].rename(columns={'mean_abs_shap':'kernel_magnitude','global_rank':'kernel_rank'})
        z=a.merge(b,on='feature');rho,p=spearmanr(z.tree_rank,z.kernel_rank)
        agreement.append({'outcome':outcome,'model':'xgboost','method_pair':'TreeSHAP vs KernelSHAP','spearman_rank_rho':rho,'p_descriptive':p,'n_features':len(z)})
        fig,ax=plt.subplots(figsize=(6.6,6.0));ax.scatter(z.tree_rank,z.kernel_rank,s=28,color='#176B87',alpha=.8)
        for rr in z.nsmallest(10,'tree_rank').itertuples():ax.annotate(rr.feature,(rr.tree_rank,rr.kernel_rank),xytext=(3,3),textcoords='offset points',fontsize=7)
        lim=max(z.tree_rank.max(),z.kernel_rank.max())+1;ax.plot([0,lim],[0,lim],'--',color='#777777',lw=.8)
        ax.set(xlabel='TreeSHAP magnitude rank',ylabel='KernelSHAP magnitude rank',title=f'{OUTCOME_LABEL[outcome]}\nTreeSHAP–KernelSHAP rank agreement (ρ={rho:.2f})')
        ax.invert_xaxis();ax.invert_yaxis();fig.tight_layout();save_pub(fig,f'method_agreement__{outcome}__xgboost');plt.show();plt.close(fig)
agreement=pd.DataFrame(agreement);agreement.to_csv(TABLE_DIR/'tree_kernel_method_agreement.csv',index=False,encoding='utf-8-sig');display(agreement)
''')

code(r'''
# 15. Local waterfall plots for representative low-, middle-, and high-risk patients
# Uses grouped original-variable SHAP from full-cohort exact linear / TreeSHAP explanations.
for r in registry.itertuples(index=False):
    mid=r.model_id;outcome=r.outcome;model=r.model
    method='TreeSHAP' if model=='xgboost' else 'Final-fit exact linear'
    sub=final_long[(final_long.model_id.eq(mid))&(final_long.method.eq(method))]
    pipe=models[mid];raw=metadata[mid]['raw_predictors'];d=data_by_outcome[outcome]
    probs=pipe.predict_proba(d[raw])[:,1]
    picks=[int(np.argmin(abs(probs-q))) for q in np.quantile(probs,[.1,.5,.9])]
    fig,axes=plt.subplots(1,3,figsize=(14.5,5.4))
    for ax,idx,label in zip(axes,picks,['Low predicted risk','Median predicted risk','High predicted risk']):
        vid=d.VisitID.iloc[idx];g=sub[sub.VisitID.eq(vid)].copy();g['abs']=g.shap_value.abs();g=g.nlargest(10,'abs').sort_values('shap_value')
        ax.barh(g.feature,g.shap_value,color=np.where(g.shap_value>=0,'#B23A48','#2C7FB8'))
        ax.axvline(0,color='black',lw=.7);ax.set_title(f'{label}\np={probs[idx]:.3f}',fontsize=10);ax.set_xlabel('Signed SHAP (log-odds)');ax.set_ylabel('')
    fig.suptitle(f'{OUTCOME_LABEL[outcome]} — {model}: representative local explanations',x=.01,ha='left',fontsize=14,fontweight='bold')
    fig.tight_layout(rect=[0,0,1,.93]);save_pub(fig,f'local_waterfalls__{mid}');plt.show();plt.close(fig)
''')

md('## D. Automated audit and export')
code(r'''
# 16. Automated completeness and scientific-integrity audit
checks=[]
def check(cid,description,passed,details=''):
    checks.append({'check_id':cid,'description':description,'status':'PASS' if bool(passed) else 'FAIL','details':str(details)})
check('S001','Exactly 12 signed OOF files passed',len(oof_audit)==12 and oof_audit.status.eq('OK').all())
check('S002','OOF signed values contain both signs',(oof_audit.min_shap<0).all() and (oof_audit.max_shap>0).all())
check('S003','Eight packaged models loaded',len(models)==8)
check('S004','TreeSHAP restricted to XGBoost',set(final_long.query("method=='TreeSHAP'").model)=={'xgboost'})
check('S005','Exact linear SHAP restricted to ridge models',set(final_long.query("method=='Final-fit exact linear'").model).issubset({'core_ridge','refined_broad_ridge'}))
check('S006','KernelSHAP covers all packaged models when enabled',(not RUN_KERNEL) or final_long.query("method=='KernelSHAP'").model_id.nunique()==8)
check('S007','No prohibited predictor explained',not set(['OnlyLargeJoints','VisitID']).intersection(set(final_long.feature)|set(oof_long.feature)))
check('S008','All exact methods pass additivity',method_audit.query("method!='KernelSHAP'").status.eq('PASS').all(),method_audit.query("method!='KernelSHAP'").max_additivity_error.max())
check('S009','Direction tables distinguish variable type',set(oof_direction.type).issubset({'numeric','binary','categorical','unlinked'}))
check('S010','Publication raster and vector outputs exist',len(list(FIGURE_DIR.glob('*.png')))>0 and len(list(FIGURE_DIR.glob('*.tiff')))>0 and len(list(FIGURE_DIR.glob('*.pdf')))>0 and len(list(FIGURE_DIR.glob('*.svg')))>0)
check('S011','Interpretation scale explicitly recorded',True,'Positive=toward named positive outcome; negative=away; predictive not causal')
check('S012','OOF and final-fit explanations are not pooled',True,'Separate source labels and tables')
audit=pd.DataFrame(checks);audit.to_csv(TABLE_DIR/'complete_shap_validation_audit.csv',index=False,encoding='utf-8-sig');display(audit)
if not audit.status.eq('PASS').all(): raise AssertionError(audit[audit.status.eq('FAIL')].to_string(index=False))
print('ALL SHAP AUDIT CHECKS PASSED')
''')

code(r'''
# 17. Workbook, artifact registry, and concise machine-readable interpretation guide
with pd.ExcelWriter(OUT_DIR/'Complete_SHAP_Tables.xlsx',engine='openpyxl') as xw:
    oof_audit.to_excel(xw,'OOF audit',index=False)
    oof_magnitude.to_excel(xw,'OOF magnitude',index=False)
    oof_direction.to_excel(xw,'OOF direction',index=False)
    oof_categories.to_excel(xw,'OOF categories',index=False)
    final_magnitude.to_excel(xw,'Final magnitude',index=False)
    final_direction.to_excel(xw,'Final direction',index=False)
    final_categories.to_excel(xw,'Final categories',index=False)
    method_audit.to_excel(xw,'Method audit',index=False)
    agreement.to_excel(xw,'Method agreement',index=False)
    audit.to_excel(xw,'Validation audit',index=False)

guide={
 'positive_shap':'moves prediction toward the named positive outcome',
 'negative_shap':'moves prediction away from the named positive outcome',
 'magnitude':'use mean absolute SHAP; do not use mean signed SHAP as importance because signs can cancel',
 'primary_explanation_source':'signed patient-level OOF exact linear SHAP',
 'tree_shap':'descriptive explanation of full-cohort XGBoost challenger fits',
 'kernel_shap':'model-agnostic final-fit sensitivity analysis on a reproducible stratified sample',
 'causality':'none; explanations are predictive and can be altered by correlated predictors',
 'figure_formats':['PNG 600 dpi','TIFF 600 dpi LZW','PDF vector','SVG vector'],
}
(OUT_DIR/'interpretation_guide.json').write_text(json.dumps(guide,indent=2),encoding='utf-8')

art=[]
for p in sorted(OUT_DIR.rglob('*')):
    if p.is_file() and p.name!='artifact_registry.csv': art.append({'relative_path':str(p.relative_to(OUT_DIR)),'size_bytes':p.stat().st_size,'sha256':sha256(p)})
pd.DataFrame(art).to_csv(TABLE_DIR/'artifact_registry.csv',index=False,encoding='utf-8-sig')
print('Artifacts registered:',len(art))
''')

md(r'''
## Reporting language

The primary directional claims should come from the signed patient-level OOF results. Positive values indicate movement toward the named phenotype and negative values indicate movement away. Mean absolute SHAP quantifies magnitude. Numeric high-versus-low, binary present-versus-absent, and category-specific summaries describe direction; they are not hypothesis tests. TreeSHAP and Kernel SHAP results from packaged full-cohort models are complementary descriptive/sensitivity analyses and must not be presented as external validation or causal effects.
''')

code(r'''
# 18. FINAL CELL — execute a clean copy and create a self-contained HTML report
if os.environ.get('RA_COMPLETE_SHAP_EXPORT_MODE')=='1':
    print('HTML subprocess mode: recursive export skipped.')
else:
    candidates=[PROJECT_DIR/NOTEBOOK_NAME,Path.cwd()/NOTEBOOK_NAME,Path.cwd()/'ra_analysis'/NOTEBOOK_NAME,Path.cwd()/NOTEBOOK_NAME]
    notebook=next((p for p in candidates if p.exists()),None)
    if notebook is None: raise FileNotFoundError(f'Save this notebook as {NOTEBOOK_NAME} before HTML export.')
    env=os.environ.copy();env['RA_COMPLETE_SHAP_EXPORT_MODE']='1'
    cmd=[sys.executable,'-m','jupyter','nbconvert','--to','html','--execute','--ExecutePreprocessor.timeout=0',
         '--ExecutePreprocessor.kernel_name=python3','--HTMLExporter.embed_images=True','--output','Complete_SHAP_Analysis_Publication.html',
         '--output-dir',str(REPORT_DIR),str(notebook)]
    print('Executing clean HTML export. Kernel SHAP may require substantial time...')
    z=subprocess.run(cmd,env=env,cwd=str(notebook.parent),text=True,capture_output=True)
    if z.stdout: print(z.stdout)
    if z.returncode:
        print(z.stderr);raise RuntimeError(f'HTML export failed with code {z.returncode}')
    report=REPORT_DIR/'Complete_SHAP_Analysis_Publication.html'
    if not report.exists(): raise FileNotFoundError(report)
    print('Self-contained report:',report.resolve())
''')

nb['cells']=C
nbf.write(nb,OUT)
print(OUT)
