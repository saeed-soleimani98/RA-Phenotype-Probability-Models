import os
import nbformat as nbf
from pathlib import Path

out=Path(os.environ.get('RA_OUTPUT_DIR','./outputs'))/'05_directional_oof_shap_check.ipynb'
out.parent.mkdir(parents=True, exist_ok=True)
nb=nbf.v4.new_notebook()
nb['metadata']={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python','version':'3'}}

nb.cells=[
nbf.v4.new_markdown_cell("""# Directional out-of-fold SHAP check and HTML report

This notebook answers two questions:

1. **Do the saved patient-level signed out-of-fold SHAP files still exist?**
2. **If they exist, do higher or present feature values generally move predictions toward or away from each positive outcome?**

The original modeling notebook was designed to save files named:

`<outcome>__<model>__patient_oof_shap.csv`

Each file should contain `VisitID`, `y`, and one **signed** SHAP column per original clinical variable. Positive SHAP values move a patient's prediction toward the positive outcome; negative values move it away. The notebook joins those values to the original data when possible, generates directional summaries, exports CSV tables, and writes a self-contained HTML report.

**Important:** direction is predictive, not causal. For correlated variables, SHAP credit can be redistributed. Mean absolute SHAP charts alone cannot provide direction."""),

nbf.v4.new_code_cell("""# Configuration and imports
from pathlib import Path
import re, io, base64, html, warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

warnings.filterwarnings('ignore')
pd.set_option('display.max_columns', 100)
pd.set_option('display.max_rows', 100)

# Add or change roots if your Stage 3B result folder is elsewhere.
SEARCH_ROOTS = [
    Path.cwd(),
    Path.cwd(),
    Path('/content'),
    Path.cwd(),
]
SEARCH_ROOTS = [p for i,p in enumerate(SEARCH_ROOTS) if p.exists() and p not in SEARCH_ROOTS[:i]]

# Optional manual overrides. Leave as None for automatic discovery.
MANUAL_SHAP_DIR = None  # Example: ENV_PROJECT/'RA/modeling_results_stage3b/tables'
MANUAL_SOURCE_CSV = None # Example: ENV_PROJECT/'RA/Atypical_presentations_RA_predictors_valid_c_exclusions_final_population.csv'

OUTPUT_DIR = Path.cwd() / 'directional_shap_output'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
HTML_PATH = OUTPUT_DIR / 'directional_oof_shap_report.html'
print('Search roots:', [str(x) for x in SEARCH_ROOTS])
print('Output:', OUTPUT_DIR.resolve())"""),

nbf.v4.new_markdown_cell("""## Interpretation rules used here

For each original feature and outcome/model pair:

- **Contribution sign:** positive SHAP increases the model's log-odds for the positive outcome; negative SHAP decreases it.
- **Numeric direction:** Spearman correlation between the raw feature value and signed SHAP. Positive means higher values generally push toward the outcome; negative means higher values push away.
- **Binary direction:** difference in mean signed SHAP between value 1 and value 0.
- **Categorical direction:** mean signed SHAP is reported separately for each observed category.
- **Strength:** mean absolute SHAP. This ranks influence, not direction.

A relationship is labelled “mixed/weak” when its direction is small or inconsistent. This avoids forcing a single direction onto nonlinear or unstable patterns."""),

nbf.v4.new_code_cell("""# Discovery and directional-analysis functions
OUTCOMES = ['NegRFandACCP','NoHandJointInvolvement','AsymmetricArthritis']
MODEL_ORDER = ['core_ridge','broad_ridge','broad_elastic_net']
SHAP_RE = re.compile(r'(?P<outcome>.+)__(?P<model>.+)__patient_oof_shap\\.csv$', re.I)

def discover_files():
    found=[]
    if MANUAL_SHAP_DIR is not None:
        found += list(Path(MANUAL_SHAP_DIR).glob('*__patient_oof_shap.csv'))
    for root in SEARCH_ROOTS:
        try:
            found += list(root.rglob('*__patient_oof_shap.csv'))
        except (PermissionError,OSError):
            pass
    # Resolve and de-duplicate.
    uniq=[]; seen=set()
    for p in found:
        try: k=str(p.resolve())
        except Exception: k=str(p)
        if k not in seen: seen.add(k); uniq.append(p)
    rows=[]
    for p in uniq:
        m=SHAP_RE.match(p.name)
        if m:
            rows.append({'outcome':m.group('outcome'),'model':m.group('model'),'path':p})
    return pd.DataFrame(rows)

def discover_source_csv():
    if MANUAL_SOURCE_CSV is not None and Path(MANUAL_SOURCE_CSV).exists():
        return Path(MANUAL_SOURCE_CSV)
    preferred='Atypical_presentations_RA_predictors_valid_c_exclusions_final_population.csv'
    candidates=[]
    for root in SEARCH_ROOTS:
        try:
            candidates += list(root.rglob(preferred))
        except (PermissionError,OSError):
            pass
    return candidates[0] if candidates else None

def signed_file_audit(inventory):
    rows=[]
    for r in inventory.itertuples(index=False):
        try:
            df=pd.read_csv(r.path)
            feats=[c for c in df.columns if c not in {'VisitID','y'}]
            arr=df[feats].apply(pd.to_numeric,errors='coerce').to_numpy(float) if feats else np.empty((len(df),0))
            finite=arr[np.isfinite(arr)]
            rows.append({'outcome':r.outcome,'model':r.model,'path':str(r.path),'n':len(df),
                         'feature_count':len(feats),'has_negative':bool((finite<0).any()) if finite.size else False,
                         'has_positive':bool((finite>0).any()) if finite.size else False,
                         'signed_values_confirmed':bool((finite<0).any() and (finite>0).any()) if finite.size else False,
                         'status':'OK' if {'VisitID','y'}.issubset(df.columns) and len(feats)>0 else 'INVALID'})
        except Exception as e:
            rows.append({'outcome':r.outcome,'model':r.model,'path':str(r.path),'n':np.nan,'feature_count':np.nan,
                         'has_negative':False,'has_positive':False,'signed_values_confirmed':False,'status':f'ERROR: {e}'})
    return pd.DataFrame(rows)

def classify_feature(s):
    non=s.dropna()
    if non.empty: return 'unavailable'
    u=pd.unique(non)
    if len(u)<=2 and set(pd.Series(u).astype(str)).issubset({'0','1','0.0','1.0','False','True'}): return 'binary'
    if pd.api.types.is_numeric_dtype(non) and len(u)>5: return 'numeric'
    return 'categorical'

def direction_label(effect, threshold=0.10):
    if pd.isna(effect): return 'unavailable'
    if effect>=threshold: return 'higher/present value pushes toward outcome'
    if effect<=-threshold: return 'higher/present value pushes away from outcome'
    return 'mixed or weak directional pattern'

def analyze_one(shap_path, outcome, model, raw):
    sw=pd.read_csv(shap_path)
    feat_cols=[c for c in sw.columns if c not in {'VisitID','y'}]
    for c in feat_cols: sw[c]=pd.to_numeric(sw[c],errors='coerce')
    merged=None
    if raw is not None and 'VisitID' in raw.columns and 'VisitID' in sw.columns:
        # Convert IDs to strings to avoid numeric/string mismatch.
        a=sw.copy(); b=raw.copy(); a['_id']=a['VisitID'].astype(str); b['_id']=b['VisitID'].astype(str)
        raw_keep=['_id']+[c for c in feat_cols if c in b.columns]
        merged=a.merge(b[raw_keep],on='_id',how='left',suffixes=('_shap','_raw'))
    rows=[]; category_rows=[]
    for f in feat_cols:
        sv=sw[f]
        base={'outcome':outcome,'model':model,'feature':f,'n_shap':int(sv.notna().sum()),
              'mean_abs_shap':float(sv.abs().mean()),'mean_signed_shap':float(sv.mean()),
              'median_signed_shap':float(sv.median()),'positive_fraction':float((sv>0).mean()),
              'negative_fraction':float((sv<0).mean()),'raw_available':False,
              'feature_type':'unavailable','direction_effect':np.nan,'direction':'raw values unavailable'}
        if merged is not None and f+'_raw' in merged.columns and f+'_shap' in merged.columns:
            x=merged[f+'_raw']; z=merged[f+'_shap']; typ=classify_feature(x); base['raw_available']=x.notna().any(); base['feature_type']=typ
            temp=pd.DataFrame({'x':x,'z':z}).dropna()
            if typ=='numeric' and len(temp)>=10:
                rho=temp['x'].rank().corr(temp['z'].rank())
                q1,q3=temp['x'].quantile([.25,.75])
                low=temp.loc[temp.x<=q1,'z'].mean(); high=temp.loc[temp.x>=q3,'z'].mean()
                base.update(direction_effect=float(rho),direction=direction_label(rho,.10),
                            low_value_mean_shap=float(low),high_value_mean_shap=float(high),high_minus_low=float(high-low))
            elif typ=='binary' and len(temp)>=10:
                xn=pd.to_numeric(temp.x,errors='coerce')
                m0=temp.loc[xn==0,'z'].mean(); m1=temp.loc[xn==1,'z'].mean(); diff=m1-m0
                base.update(direction_effect=float(diff),direction=direction_label(diff,.005),
                            value0_mean_shap=float(m0),value1_mean_shap=float(m1),high_minus_low=float(diff))
            elif typ=='categorical' and len(temp)>=10:
                gm=temp.assign(group=temp.x.astype(str)).groupby('group').z.agg(['count','mean']).reset_index()
                gm=gm[gm['count']>=3].sort_values('mean')
                if len(gm):
                    effect=float(gm['mean'].max()-gm['mean'].min())
                    base.update(direction_effect=effect,direction='category-specific; inspect category table')
                    for rr in gm.itertuples(index=False):
                        category_rows.append({'outcome':outcome,'model':model,'feature':f,'category':rr.group,
                                              'n':int(rr.count),'mean_signed_shap':float(rr.mean)})
        rows.append(base)
    return pd.DataFrame(rows),pd.DataFrame(category_rows),sw,merged

def fig_to_b64(fig):
    buf=io.BytesIO(); fig.savefig(buf,format='png',dpi=170,bbox_inches='tight',facecolor='white'); plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode('ascii')

def directional_plot(summary, title):
    d=summary.sort_values('mean_abs_shap',ascending=False).head(15).copy().sort_values('mean_abs_shap')
    fig,ax=plt.subplots(figsize=(9,6.5))
    effects=d['direction_effect'].fillna(0)
    colors=np.where(effects>0.10,'#2a8f62',np.where(effects<-0.10,'#b33b3b','#88939d'))
    ax.barh(d.feature,d.mean_abs_shap,color=colors)
    ax.set_xlabel('Mean absolute out-of-fold SHAP value (log-odds scale)')
    ax.set_title(title+'\\nGreen: higher values tend toward outcome; red: higher values tend away; grey: mixed/unavailable')
    ax.grid(axis='x',alpha=.25); fig.tight_layout(); return fig
"""),

nbf.v4.new_code_cell("""# Quick inventory check
inventory=discover_files()
source_path=discover_source_csv()
print(f'Found {len(inventory)} patient-level OOF SHAP file(s).')
if len(inventory): display(inventory.assign(path=inventory.path.astype(str)).sort_values(['outcome','model']))
else:
    print('No signed patient-level OOF SHAP CSV files were found in the configured roots.')
    print('Expected filename example: NegRFandACCP__core_ridge__patient_oof_shap.csv')
print('Source data:', source_path if source_path else 'not found')
"""),

nbf.v4.new_markdown_cell("""## HTML-generating cell

Run the next cell after setting the paths above. It will not fail if the signed files are missing. Instead, it produces an audit report explaining what was found and which files are needed. If files are available, it produces directional tables, plots, and CSV exports."""),

nbf.v4.new_code_cell("""# GENERATE THE SELF-CONTAINED HTML REPORT
inventory=discover_files()
audit=signed_file_audit(inventory) if len(inventory) else pd.DataFrame()
source_path=discover_source_csv()
raw=pd.read_csv(source_path,low_memory=False) if source_path else None

all_summary=[]; all_categories=[]; plot_sections=[]; errors=[]
if len(inventory):
    for r in inventory.sort_values(['outcome','model']).itertuples(index=False):
        try:
            summary,cats,sw,merged=analyze_one(r.path,r.outcome,r.model,raw)
            all_summary.append(summary)
            if len(cats): all_categories.append(cats)
            fig=directional_plot(summary,f'{r.outcome} — {r.model}')
            plot_sections.append((r.outcome,r.model,fig_to_b64(fig),summary.sort_values('mean_abs_shap',ascending=False).head(20)))
        except Exception as e:
            errors.append(f'{r.path}: {e}')
summary=pd.concat(all_summary,ignore_index=True) if all_summary else pd.DataFrame()
categories=pd.concat(all_categories,ignore_index=True) if all_categories else pd.DataFrame()

if len(summary):
    summary.to_csv(OUTPUT_DIR/'directional_oof_shap_summary.csv',index=False,encoding='utf-8-sig')
if len(categories):
    categories.to_csv(OUTPUT_DIR/'directional_oof_shap_category_means.csv',index=False,encoding='utf-8-sig')
if len(audit): audit.to_csv(OUTPUT_DIR/'signed_shap_file_audit.csv',index=False,encoding='utf-8-sig')

css='''
body{font-family:Arial,sans-serif;max-width:1180px;margin:0 auto;padding:28px;color:#1b2633;line-height:1.48}
h1,h2,h3{color:#10243b} h1{border-bottom:5px solid #167b80;padding-bottom:12px}
.card{background:#f4f7fa;border-left:5px solid #167b80;padding:16px 20px;margin:18px 0;border-radius:5px}
.warn{border-left-color:#d95f02;background:#fff6ed}.ok{border-left-color:#2a8f62;background:#effaf4}
table{border-collapse:collapse;width:100%;font-size:13px;margin:12px 0 24px}th{background:#10243b;color:white;position:sticky;top:0}th,td{border:1px solid #d8e0e6;padding:7px;text-align:left}tr:nth-child(even){background:#f7f9fb}
img{max-width:100%;height:auto;border:1px solid #d8e0e6}.small{color:#5f6b76;font-size:13px}code{background:#edf1f4;padding:2px 5px}
'''
parts=[f'<!doctype html><html><head><meta charset="utf-8"><title>Directional OOF SHAP audit</title><style>{css}</style></head><body>',
       '<h1>Directional out-of-fold SHAP audit</h1>',
       '<div class="card"><b>Purpose.</b> Verify that signed patient-level OOF SHAP values exist and, when raw feature values are available, estimate whether higher or present feature values tend to move predictions toward or away from each positive outcome.</div>']

if not len(inventory):
    parts += ['<div class="card warn"><h2>Signed OOF SHAP files were not found</h2>',
              '<p>The existing mean-absolute SHAP PNG files are not sufficient for direction. The original Stage 3B notebook was designed to save the required signed files with names such as:</p>',
              '<p><code>NegRFandACCP__core_ridge__patient_oof_shap.csv</code></p>',
              '<p>Search the original Stage 3B results folder, checkpoint/output drive, or rerun the full scientific Stage 3B notebook. Do not use quick-mode software-test output for scientific interpretation.</p></div>']
else:
    parts += [f'<div class="card ok"><b>{len(inventory)} candidate file(s) found.</b> Source data: {html.escape(str(source_path)) if source_path else "not found; only contribution signs can be summarized"}.</div>',
              '<h2>File audit</h2>',audit.to_html(index=False,escape=True)]
    if errors: parts += ['<div class="card warn"><b>Errors</b><br>'+ '<br>'.join(html.escape(x) for x in errors)+'</div>']
    parts += ['<h2>How to interpret direction</h2><ul><li>Positive SHAP: contribution toward the positive outcome.</li><li>Negative SHAP: contribution away from the positive outcome.</li><li>Green/red labels require raw-value linkage; grey means mixed, weak, or unavailable.</li><li>Direction is predictive association, not causation.</li></ul>']
    for outcome,model,b64,top in plot_sections:
        cols=[c for c in ['feature','mean_abs_shap','mean_signed_shap','positive_fraction','feature_type','direction_effect','direction','high_minus_low'] if c in top.columns]
        parts += [f'<h2>{html.escape(outcome)} — {html.escape(model)}</h2>',
                  f'<img alt="Directional SHAP summary" src="data:image/png;base64,{b64}">',
                  top[cols].round(4).to_html(index=False,escape=True)]
    if len(categories):
        parts += ['<h2>Categorical feature details</h2>',categories.round(4).to_html(index=False,escape=True)]

parts += ['<h2>Required cautions</h2><div class="card warn"><ul><li>Mean signed SHAP can be near zero even for an important feature because positive and negative contributions cancel.</li><li>Use raw-value versus signed-SHAP direction, not mean signed SHAP alone.</li><li>Correlated predictors can share or exchange attribution.</li><li>For ridge models, coefficient sign and SHAP direction should be checked together.</li><li>These results remain internally validated and non-causal.</li></ul></div>',
          f'<p class="small">Generated by 05_directional_oof_shap_check.ipynb. Output folder: {html.escape(str(OUTPUT_DIR.resolve()))}</p></body></html>']
HTML_PATH.write_text(''.join(parts),encoding='utf-8')
print('Wrote:',HTML_PATH.resolve())
if len(summary):
    display(summary.sort_values(['outcome','model','mean_abs_shap'],ascending=[True,True,False]).groupby(['outcome','model']).head(15))
else:
    print('No directional table generated because signed patient-level files were unavailable.')
""")
]

nbf.write(nb,out)
print(out)
