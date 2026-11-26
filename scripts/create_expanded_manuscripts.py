from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.section import WD_SECTION
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import pandas as pd, re, json

ROOT=Path.cwd()
SRC_MAIN=ROOT/'Manuscript_Files/RA_models_Revised_Academic_Main_Methods_Results.docx'
SRC_SUPP=ROOT/'Manuscript_Files/RA_models_Revised_Academic_Supplementary_Methods_Results.docx'
HTML=ROOT/'uploads/Complete_SHAP_Analysis_Publication.html'
OUT=ROOT/'Manuscript_Files'
OUT.mkdir(exist_ok=True)

# Existing validated tables are used as the numerical source of truth.
main_src=Document(SRC_MAIN); supp_src=Document(SRC_SUPP)
def table_matrix(t): return [[c.text for c in r.cells] for r in t.rows]
MAIN_TABLES=[table_matrix(t) for t in main_src.tables]
SUPP_TABLES=[table_matrix(t) for t in supp_src.tables]
html_tables=pd.read_html(HTML)
SHAP_TOP=html_tables[2].drop(columns=[c for c in html_tables[2].columns if str(c).startswith('Unnamed')])
METHOD_AUDIT=html_tables[3].drop(columns=[c for c in html_tables[3].columns if str(c).startswith('Unnamed')])
AGREEMENT=html_tables[5].drop(columns=[c for c in html_tables[5].columns if str(c).startswith('Unnamed')])
FINAL_AUDIT=html_tables[6].drop(columns=[c for c in html_tables[6].columns if str(c).startswith('Unnamed')])

REFS=[
"Collins GS, Moons KGM, Dhiman P, et al. TRIPOD+AI statement: updated guidance for reporting clinical prediction models that use regression or machine learning methods. BMJ. 2024;385:e078378. doi:10.1136/bmj-2023-078378.",
"Moons KGM, et al. PROBAST+AI: an updated quality, risk-of-bias and applicability assessment tool for prediction models using regression or artificial intelligence methods. BMJ. 2025;388:e082505. doi:10.1136/bmj-2024-082505.",
"Riley RD, Ensor J, Snell KIE, et al. Calculating the sample size required for developing a clinical prediction model. BMJ. 2020;368:m441. doi:10.1136/bmj.m441.",
"Riley RD, Snell KIE, Ensor J, et al. Minimum sample size for developing a multivariable prediction model: Part II, binary and time-to-event outcomes. Stat Med. 2019;38:1276-1296. doi:10.1002/sim.7992.",
"Varma S, Simon R. Bias in error estimation when using cross-validation for model selection. BMC Bioinformatics. 2006;7:91. doi:10.1186/1471-2105-7-91.",
"Steyerberg EW, Harrell FE Jr, Borsboom GJJM, et al. Internal validation of predictive models: efficiency of some procedures for logistic regression analysis. J Clin Epidemiol. 2001;54:774-781. doi:10.1016/S0895-4356(01)00341-9.",
"Van Calster B, Nieboer D, Vergouwe Y, et al. A calibration hierarchy for risk models was defined: from utopia to empirical data. J Clin Epidemiol. 2016;74:167-176. doi:10.1016/j.jclinepi.2015.12.005.",
"Van Calster B, McLernon DJ, van Smeden M, et al. Calibration: the Achilles heel of predictive analytics. BMC Med. 2019;17:230. doi:10.1186/s12916-019-1466-7.",
"Riley RD, Debray TPA, Collins GS, et al. Minimum sample size for external validation of a clinical prediction model with a binary outcome. Stat Med. 2021;40:4230-4251. doi:10.1002/sim.9025.",
"Saito T, Rehmsmeier M. The precision-recall plot is more informative than the ROC plot when evaluating binary classifiers on imbalanced datasets. PLoS One. 2015;10:e0118432. doi:10.1371/journal.pone.0118432.",
"Lundberg SM, Lee SI. A unified approach to interpreting model predictions. Adv Neural Inf Process Syst. 2017;30:4765-4774.",
"Lundberg SM, Erion G, Chen H, et al. From local explanations to global understanding with explainable AI for trees. Nat Mach Intell. 2020;2:56-67. doi:10.1038/s42256-019-0138-9.",
"Janzing D, Minorics L, Blöbaum P. Feature relevance quantification in explainable AI: a causal problem. Proc AISTATS. 2020;108:2907-2916.",
"Pedregosa F, Varoquaux G, Gramfort A, et al. Scikit-learn: machine learning in Python. J Mach Learn Res. 2011;12:2825-2830.",
"Chen T, Guestrin C. XGBoost: a scalable tree boosting system. Proc 22nd ACM SIGKDD. 2016:785-794. doi:10.1145/2939672.2939785.",
"Aletaha D, Neogi T, Silman AJ, et al. 2010 rheumatoid arthritis classification criteria: an ACR/EULAR collaborative initiative. Ann Rheum Dis. 2010;69:1580-1588. doi:10.1136/ard.2010.138461.",
"Coffey CM, Crowson CS, Myasoedova E, Matteson EL, Davis JM III. Evidence of diagnostic and treatment delay in seronegative rheumatoid arthritis: missing the window of opportunity. Mayo Clin Proc. 2019;94:2241-2248. doi:10.1016/j.mayocp.2019.05.023.",
"Nordberg LB, Lillegraven S, Lie E, et al. Patients with seronegative RA have more inflammatory activity compared with patients with seropositive RA in an inception cohort of DMARD-naive patients classified according to the 2010 ACR/EULAR criteria. Ann Rheum Dis. 2017;76:341-345. doi:10.1136/annrheumdis-2015-208873.",
"Rauniyar R, Möttönen T, Hannonen P, et al. Initial presentation of early rheumatoid arthritis. PLoS One. 2023;18:e0287707. doi:10.1371/journal.pone.0287707.",
"Bricman N, Ospelt C, Raza K, et al. Analysis of synovitis patterns in early rheumatoid arthritis supports the importance of joint-specific factors. Semin Arthritis Rheum. 2024;68:152524. doi:10.1016/j.semarthrit.2024.152524.",
"Zangger P, Keystone EC, Bogoch ER. Asymmetry of small joint involvement in rheumatoid arthritis: prevalence and tendency towards symmetry over time. Joint Bone Spine. 2005;72:241-247. doi:10.1016/j.jbspin.2004.08.013.",
"Scherer HU, van der Woude D, Toes REM. From risk to chronicity: evolution of autoreactive B cell and antibody responses in rheumatoid arthritis. Nat Rev Rheumatol. 2017;13:589-600. doi:10.1038/nrrheum.2017.111.",
"Żelnio E, Taljanovic M, Mańczak M, Sudoł-Szopińska I. Hand and wrist involvement in seropositive rheumatoid arthritis, seronegative rheumatoid arthritis, and psoriatic arthritis: the value of classic radiography. J Clin Med. 2023;12:2622. doi:10.3390/jcm12072622.",
"Mendoza-Pinto C, Sanchez-Tecuatl M, Berra-Romani R, et al. Machine learning in the prediction of treatment response in rheumatoid arthritis: a systematic review. Semin Arthritis Rheum. 2024;68:152501. doi:10.1016/j.semarthrit.2024.152501.",
"Shi Y, Zhou M, Chang C, et al. Advancing precision rheumatology: applications of machine learning for rheumatoid arthritis management. Front Immunol. 2024;15:1409555. doi:10.3389/fimmu.2024.1409555.",
"Bilgin E, et al. Current application, possibilities, and challenges of artificial intelligence in the management of rheumatoid arthritis, axial spondyloarthritis, and psoriatic arthritis. Ther Adv Musculoskelet Dis. 2025. doi:10.1177/1759720X251343579.",
"van Smeden M, Moons KGM, de Groot JAH, et al. Sample size for binary logistic prediction models: beyond events per variable criteria. Stat Methods Med Res. 2019;28:2455-2474. doi:10.1177/0962280218784726.",
"Harrell FE Jr, Lee KL, Mark DB. Multivariable prognostic models: issues in developing models, evaluating assumptions and adequacy, and measuring and reducing errors. Stat Med. 1996;15:361-387. doi:10.1002/(SICI)1097-0258(19960229)15:4<361::AID-SIM168>3.0.CO;2-4.",
"Collins GS, Reitsma JB, Altman DG, Moons KGM. Transparent reporting of a multivariable prediction model for individual prognosis or diagnosis: the TRIPOD statement. Ann Intern Med. 2015;162:55-63. doi:10.7326/M14-0697.",
"Wolff RF, Moons KGM, Riley RD, et al. PROBAST: a tool to assess risk of bias and applicability of prediction model studies. Ann Intern Med. 2019;170:51-58. doi:10.7326/M18-1376.",
"Maarseveen TD, Maurits MP, Coletto LA, et al. Location and amount of joint involvement differentiates rheumatoid arthritis into different clinical subsets. NPJ Digit Med. 2025;8:623. doi:10.1038/s41746-025-01997-1.",
"Vickers AJ, Elkin EB. Decision curve analysis: a novel method for evaluating prediction models. Med Decis Making. 2006;26:565-574. doi:10.1177/0272989X06295361.",
"Davis J, Goadrich M. The relationship between precision-recall and ROC curves. Proc 23rd International Conference on Machine Learning. 2006:233-240. doi:10.1145/1143844.1143874.",
"Rudin C. Stop explaining black box machine learning models for high stakes decisions and use interpretable models instead. Nat Mach Intell. 2019;1:206-215. doi:10.1038/s42256-019-0048-x.",
"Sundararajan M, Najmi A. The many Shapley values for model explanation. Proc 37th International Conference on Machine Learning. 2020;119:9269-9278.",
"Hooker G, Mentch L. Please stop permuting features: an explanation and alternatives. arXiv. 2019;1905.03151. doi:10.48550/arXiv.1905.03151.",
"Efron B, Tibshirani RJ. An Introduction to the Bootstrap. New York: Chapman and Hall/CRC; 1993. doi:10.1201/9780429246593.",
"Steyerberg EW. Clinical Prediction Models. 2nd ed. Cham: Springer; 2019. doi:10.1007/978-3-030-16399-0."
]

COLORS={'navy':'17365D','blue':'D9EAF7','gray':'F2F2F2','dark':'1F1F1F','white':'FFFFFF'}
def shade(cell,fill):
    tcPr=cell._tc.get_or_add_tcPr(); shd=tcPr.find(qn('w:shd'))
    if shd is None: shd=OxmlElement('w:shd');tcPr.append(shd)
    shd.set(qn('w:fill'),fill)
def borders(table,top='17365D',bottom='17365D'):
    tblPr=table._tbl.tblPr; old=tblPr.find(qn('w:tblBorders'))
    if old is not None: tblPr.remove(old)
    b=OxmlElement('w:tblBorders')
    for edge,val,size in [('top',top,'10'),('bottom',bottom,'10'),('insideH','B7B7B7','4')]:
        x=OxmlElement('w:'+edge);x.set(qn('w:val'),'single');x.set(qn('w:sz'),size);x.set(qn('w:color'),val);b.append(x)
    for edge in ['left','right','insideV']:
        x=OxmlElement('w:'+edge);x.set(qn('w:val'),'nil');b.append(x)
    tblPr.append(b)
def set_repeat_header(row):
    trPr=row._tr.get_or_add_trPr(); el=OxmlElement('w:tblHeader');el.set(qn('w:val'),'true');trPr.append(el)
def set_cell_margin(cell,top=60,start=80,bottom=60,end=80):
    tc=cell._tc;tcPr=tc.get_or_add_tcPr();m=tcPr.first_child_found_in('w:tcMar')
    if m is None:m=OxmlElement('w:tcMar');tcPr.append(m)
    for tag,val in [('top',top),('start',start),('bottom',bottom),('end',end)]:
        node=m.find(qn('w:'+tag))
        if node is None:node=OxmlElement('w:'+tag);m.append(node)
        node.set(qn('w:w'),str(val));node.set(qn('w:type'),'dxa')
def setup(doc,title,subtitle):
    sec=doc.sections[0];sec.top_margin=Inches(.75);sec.bottom_margin=Inches(.7);sec.left_margin=Inches(.78);sec.right_margin=Inches(.78)
    styles=doc.styles
    styles['Normal'].font.name='Arial';styles['Normal'].font.size=Pt(10);styles['Normal'].paragraph_format.space_after=Pt(5);styles['Normal'].paragraph_format.line_spacing=1.08
    for s,size,col in [('Title',20,'17365D'),('Heading 1',15,'17365D'),('Heading 2',12,'244A6B'),('Heading 3',10.5,'244A6B')]:
        styles[s].font.name='Arial';styles[s].font.size=Pt(size);styles[s].font.color.rgb=RGBColor.from_string(col);styles[s].font.bold=True
    p=doc.add_paragraph();p.style='Title';p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.add_run(title)
    p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER;r=p.add_run(subtitle);r.bold=True;r.font.size=Pt(12);r.font.color.rgb=RGBColor.from_string('244A6B')
    p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER;r=p.add_run('Expanded academic manuscript | 25 September 2026');r.italic=True;r.font.size=Pt(9)
    doc.add_paragraph('Intended use. These models estimate contemporaneously recorded phenotype probabilities at a completed rheumatology assessment. They are research models. They have not been externally validated and must not be used as diagnostic, prognostic, causal, treatment-selection, or autonomous clinical decision tools.',style='Intense Quote')
def add_heading(doc,text,level=1):doc.add_heading(text,level=level)
def add_paras(doc,text):
    for x in [z.strip() for z in text.strip().split('\n\n') if z.strip()]: doc.add_paragraph(x)
def add_caption(doc,text):
    p=doc.add_paragraph();p.paragraph_format.space_before=Pt(8);p.paragraph_format.space_after=Pt(3);r=p.add_run(text);r.bold=True;r.font.size=Pt(9.5);r.font.color.rgb=RGBColor.from_string('17365D')
def add_table(doc,data,widths=None,font=8.3):
    rows=len(data);cols=max(len(r) for r in data);t=doc.add_table(rows=rows,cols=cols);t.alignment=WD_TABLE_ALIGNMENT.CENTER;t.autofit=True
    for i,row in enumerate(data):
        for j in range(cols):
            cell=t.cell(i,j);cell.text=(str(row[j]).replace('—','Not applicable') if j<len(row) else '');cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER;set_cell_margin(cell)
            for p in cell.paragraphs:
                p.paragraph_format.space_after=Pt(0);p.paragraph_format.space_before=Pt(0)
                for run in p.runs:run.font.name='Arial';run.font.size=Pt(font);run.font.color.rgb=RGBColor.from_string('FFFFFF' if i==0 else '1F1F1F');run.bold=(i==0)
            if i==0:shade(cell,COLORS['navy'])
            elif i%2==0:shade(cell,COLORS['gray'])
    # Journal-style vertical merging for repeated outcome labels.
    if rows>2 and str(data[0][0]).strip().lower()=='outcome':
        start=1
        while start<rows:
            value=str(data[start][0]).replace('—','Not applicable')
            end=start
            while end+1<rows and str(data[end+1][0]).replace('—','Not applicable')==value:end+=1
            if end>start:
                for rr in range(start+1,end+1):t.cell(rr,0).text=''
                merged=t.cell(start,0).merge(t.cell(end,0));merged.text=value;merged.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
                for p in merged.paragraphs:
                    p.alignment=WD_ALIGN_PARAGRAPH.LEFT;p.paragraph_format.space_after=Pt(0)
                    for run in p.runs:run.font.name='Arial';run.font.size=Pt(font);run.font.color.rgb=RGBColor.from_string('1F1F1F')
            start=end+1
    set_repeat_header(t.rows[0]);borders(t)
    if widths:
        for row in t.rows:
            for j,w in enumerate(widths[:cols]):row.cells[j].width=Inches(w)
    return t
def add_note(doc,text):
    p=doc.add_paragraph();p.paragraph_format.space_before=Pt(2);p.paragraph_format.space_after=Pt(8);r=p.add_run('Note. '+text);r.font.size=Pt(8);r.italic=True;r.font.color.rgb=RGBColor.from_string('555555')
def add_figure(doc,path,caption,interpretation='',width=6.75,page_break=False):
    path=Path(path)
    if not path.exists(): raise FileNotFoundError(path)
    if page_break: doc.add_page_break()
    p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.keep_with_next=True
    p.add_run().add_picture(str(path),width=Inches(width))
    c=doc.add_paragraph();c.paragraph_format.space_before=Pt(3);c.paragraph_format.space_after=Pt(3)
    r=c.add_run(caption);r.bold=True;r.font.size=Pt(9);r.font.color.rgb=RGBColor.from_string('17365D')
    if interpretation:
        q=doc.add_paragraph();q.paragraph_format.space_after=Pt(9);rr=q.add_run(interpretation);rr.font.size=Pt(8.5);rr.italic=True;rr.font.color.rgb=RGBColor.from_string('444444')
def add_refs(doc):
    add_heading(doc,'References',1)
    for i,r in enumerate(REFS,1):
        p=doc.add_paragraph(style='Normal');p.paragraph_format.left_indent=Inches(.22);p.paragraph_format.first_line_indent=Inches(-.22);p.paragraph_format.space_after=Pt(3);p.add_run(f'{i}. {r}')
def footer(doc):
    for sec in doc.sections:
        p=sec.footer.paragraphs[0];p.alignment=WD_ALIGN_PARAGRAPH.CENTER
        run=p.add_run();fld=OxmlElement('w:fldSimple');fld.set(qn('w:instr'),'PAGE');run._r.addnext(fld)

def direction_rows():
    label={'RADurationDays':'RA duration','DASJointCountTEN28':'Tender 28-joint count','DASJointCountSW':'Swollen-joint count','PatientGlobalAssessment':'Patient global assessment','Age':'Age','Gender':'Sex','AbnormalCRPorESR':'Abnormal CRP or ESR'}
    dirs={
      'NegRFandACCP':{'RADurationDays':'Toward','DASJointCountTEN28':'Toward','DASJointCountSW':'Away','PatientGlobalAssessment':'Away','Age':'Away','Gender':'Female toward; male away','AbnormalCRPorESR':'Small contribution'},
      'NoHandJointInvolvement':{'RADurationDays':'Toward','DASJointCountTEN28':'Away','DASJointCountSW':'Away','PatientGlobalAssessment':'Away','Age':'Toward','Gender':'Minimal','AbnormalCRPorESR':'Present toward'},
      'AsymmetricArthritis':{'RADurationDays':'Away','DASJointCountTEN28':'Away','DASJointCountSW':'Away','PatientGlobalAssessment':'Away','Age':'Away','Gender':'Male toward; female away','AbnormalCRPorESR':'Present away'}}
    out=[['Outcome','Core predictor','Mean |OOF SHAP|','Directional interpretation']]
    for outcome in ['NegRFandACCP','NoHandJointInvolvement','AsymmetricArthritis']:
        g=SHAP_TOP[SHAP_TOP.outcome.eq(outcome)].sort_values('global_rank')
        for _,r in g.iterrows():out.append([outcome,label.get(r.feature,r.feature),f"{r.mean_abs_shap:.4f}",dirs[outcome].get(r.feature,'See category-specific table')])
    return out

# ---------------- Main manuscript ----------------
main=Document();setup(main,'Cross-sectional phenotype probability modeling in rheumatoid arthritis','Expanded Methods, Results, and Discussion')
add_heading(main,'Methods',1)
add_heading(main,'Study design, estimand, and reporting framework',2)
add_paras(main,"""
We conducted a cross-sectional model-development and internal-validation study in 820 patients who had completed a rheumatology assessment. Three binary phenotypes were modeled separately: concurrent negativity for rheumatoid factor (RF) and anti-cyclic citrullinated peptide antibody (anti-CCP), absence of hand-joint involvement, and asymmetric arthritis. The estimand was the probability of each recorded phenotype conditional on information available at the same completed assessment. It was not the probability of future RA, subsequent damage, remission, or treatment response. This distinction governed predictor eligibility and interpretation.

The patient was the unit of analysis. Each patient contributed once to the analytical cohort. All three outcomes were observed for every patient. Outcome-specific predictor restrictions were applied before modeling because direct components and close semantic proxies differed by endpoint. Reporting was structured around TRIPOD+AI, and design choices were checked against domains addressed by PROBAST+AI.[1,2] The earlier TRIPOD and PROBAST publications were also consulted where they supplied background for model-development and risk-of-bias decisions.[29,30]
""")
add_heading(main,'Participants, outcomes, and candidate predictors',2)
add_paras(main,"""
The source population comprised patients with RA assessed in the contributing clinical dataset. Eligibility produced 820 unique records with complete outcome ascertainment. Concurrent RF and anti-CCP negativity was coded as the positive event for the serology model. No hand-joint involvement and asymmetric arthritis were retained as recorded in the verified source data. The outcomes were not combined into a multiclass variable. A patient could meet more than one phenotype, and the phenotypes represent different clinical dimensions.

The prespecified core contained seven variables: age, sex, RA duration in days, 28-joint tender count, 28-joint swollen count, patient global assessment, and an indicator for abnormal C-reactive protein or erythrocyte sedimentation rate. RA duration was transformed as log(1 + days) inside each fitted pipeline. The core was chosen before examination of full-cohort outcome associations. It was intended to test whether a compact set of routinely available clinical measures could produce stable probability estimates.

Broader outcome-specific sets included eligible demographic measures, disease manifestations, joint-location variables, symptoms, comorbidities, treatment-related fields, and laboratory-derived measures. VisitID was used only to align folds and predictions. It was never supplied to a model. OnlyLargeJoints was excluded from all model development and sensitivity analyses. NowPregnant, Cancer, and NotCurrentlyClassifiableasRA2010 were excluded because they had no usable variation. Reproductive variables were omitted from all-patient primary models. Outcome components and direct proxies were removed separately for each endpoint. The final broad sets contained 68, 66, and 70 raw predictors for negative serology, no hand-joint involvement, and asymmetric arthritis.
""")
add_heading(main,'Missing data and preprocessing',2)
add_paras(main,"""
Blank binary and comorbidity entries were treated as unknown or not assessed. They were not recoded to zero. Numerical predictors underwent training-fold median imputation. Variables entering scale-sensitive algorithms were standardized with parameters estimated in the same training fold. Categorical predictors used an explicit unknown category and fixed one-hot encoding. Missingness indicators were created only for variables with missing values and were estimated within the resampling pipeline.

Every data-dependent step was placed inside the fitted pipeline. This included imputation, scaling, transformation, encoding, feature selection where applicable, probability calibration, and hyperparameter tuning. No full-cohort imputation or global feature screening preceded validation. Synthetic oversampling, undersampling, class weighting, and selection of a favorable random seed were not used.
""")
add_heading(main,'Complexity assessment and model hierarchy',2)
add_paras(main,"""
Model complexity was examined before broad modeling using sample-size methods for binary prediction models rather than a fixed events-per-variable rule.[3,4,27] After reference coding and missingness indicators, broad sets generated 95 to 99 independent parameters. Under the conservative design assumptions used in the prespecified calculation, the available cohort supported about nine parameters. Required sample sizes for the unpenalized broad parameterizations exceeded 8,000. Penalization can reduce variance, but it does not manufacture information that is absent from the sample.

The seven-variable ridge logistic model was therefore designated the primary model for each outcome. Ordinary logistic regression with the same core was a benchmark. Broad ridge and elastic-net logistic regression were secondary models. Lasso regression, linear and radial-basis-function support vector classifiers, random forest, AdaBoost, and XGBoost were examined after the primary plan as expanded candidate families. A fully nested selector tested what would happen if model family itself were selected inside each training sample. Results from broader and nonlinear models were not allowed to redefine the primary analysis.
""")
add_heading(main,'Model fitting, tuning, and repeated nested validation',2)
add_paras(main,"""
The outer validation procedure used stratified five-fold cross-validation repeated ten times. Fifty outer test evaluations were therefore obtained for each model and outcome. All model fitting and tuning occurred in the other four folds. Inner stratified cross-validation optimized log loss. A prespecified one-standard-error rule selected a simpler or more strongly regularized configuration when its inner-validation loss was statistically compatible with the minimum. This rule reduced the chance that a trivial inner-validation difference would select an unstable model.

Each patient was held out once in every outer repeat and received ten out-of-fold probabilities. Those probabilities were averaged at patient level before performance estimation. Repeated predictions were not treated as independent records. This arrangement evaluates the complete procedure and limits the selection bias that occurs when tuning and evaluation use the same observations.[5,6]

Probability calibration for model families that required it was fitted inside the training process. Software versions and seeds were locked in the analysis record. Logistic models were implemented in scikit-learn, and gradient boosting used XGBoost.[14,15]
""")
add_heading(main,'Performance measures and uncertainty',2)
add_paras(main,"""
Log loss and the Brier score were the main measures of probability accuracy. AUROC described ranking discrimination. Average precision was reported because event prevalence was near 20% to 23% and AUROC can conceal poor positive-class retrieval in imbalanced settings.[10] Calibration-in-the-large and calibration slope were calculated from patient-level OOF probabilities. Flexible calibration curves were used to inspect departures that cannot be summarized by two coefficients.[7,8]

Uncertainty intervals used 2,000 nonparametric bootstrap resamples of patients. Each resample retained the outcome and all paired predictions for that patient. Model comparisons were paired. Positive differences in AUROC and average precision favored the comparator. Positive log-loss and Brier improvements represented lower error than the reference model. Threshold accuracy and decision-curve analysis were not primary analyses because no clinical action, intended user, threshold range, or relative cost of errors had been prespecified.
""")
add_heading(main,'Robustness, missingness, and prediction stability',2)
add_paras(main,"""
The robustness plan addressed semantic proximity and missing-data structure. Joint-related domains were removed from models of the two joint-pattern outcomes. Separate models used missingness indicators alone, restricted predictors to near-complete variables, or omitted explicit missingness flags. Missingness subgroups were corrected to preserve ties and were defined as complete, greater than 0% to 5%, and greater than 5% missing eligible fields. An earlier row-order-dependent grouping was invalid and was discarded.

For each patient, variation across the ten OOF probabilities was summarized by the standard deviation. This patient-level quantity was then summarized by model. It measures sensitivity to training-sample perturbation. It is distinct from calibration and discrimination.
""")
add_heading(main,'SHAP analysis',2)
add_paras(main,"""
Signed patient-level OOF SHAP values were calculated for every outer-test patient in each repeat for the four prespecified regression specifications. For a fitted linear model, the contribution of transformed feature j was calculated as the difference between the test value and the outer-training background mean, multiplied by the fitted coefficient. Encoded columns and explicit missingness flags were summed back to their original clinical variable. Contributions were checked against the model decision function, then averaged across the ten OOF appearances for each patient. This produced 12 signed OOF files, one for every outcome and prespecified model. Each file contained 820 patients and both positive and negative values.

Magnitude was summarized by mean absolute SHAP, median absolute SHAP, the fraction of positive contributions, and fold-rank stability. Mean signed SHAP was retained for audit but was not used as an importance measure because opposite patient-level contributions cancel. Direction was linked to observed raw values by VisitID. Numerical predictors were interpreted from high-versus-low contrasts and rank association; binary predictors were contrasted as present versus absent; categories were summarized separately. Positive SHAP moved the model toward the named positive phenotype. Negative SHAP moved it away.

The packaged final models received a separate descriptive analysis. Exact linear SHAP was computed for six ridge pipelines in all 820 patients. Interventional TreeSHAP was computed for the two XGBoost models in all 820 patients using 100 background observations.[11,12] Kernel SHAP supplied a model-agnostic audit for all eight final models using a reproducible stratified sample of 120 patients and 30 background observations per model, with 512 evaluations. These final-fit explanations were not merged with OOF explanations. Tree, linear, and Kernel values were placed on the model-margin or log-odds scale. Attributions from correlated predictors can shift among variables, and none of these analyses identifies a causal effect.[13]
""")
add_heading(main,'Final model fitting and computational verification',2)
add_paras(main,"""
After the hierarchy, candidate families, and tuning rules had been frozen, eight pipelines were fitted to all 820 patients: core ridge and refined broad ridge for each outcome, plus XGBoost for no hand-joint involvement and asymmetric arthritis. Full-cohort refitting created portable research objects. It did not provide a new estimate of performance, so apparent fit-cohort metrics were withheld. Serialized objects were tested after reload and in fresh command-line processes. External validation remains necessary before any clinical evaluation.[9]
""")
add_figure(main,ROOT/'manuscript_figure_renders/CLEAN_analysis_workflow.png','Figure 1. Analysis workflow and model hierarchy.','The diagram distinguishes the prespecified compact analysis, broader sensitivity models, expanded algorithm benchmark, robustness analyses, and final full-cohort packaging. Performance was estimated before final refitting.',6.6)

add_heading(main,'Results',1)
add_heading(main,'Cohort',2)
add_paras(main,"""
The cohort included 820 patients. Women accounted for 700 patients (85.4%). Median age was 59 years (IQR 49 to 67). Median RA duration was 730 days (IQR 300 to 2,190); 16 duration values were missing. Median tender and swollen 28-joint counts were 6 and 2. Abnormal CRP or ESR was recorded in 563 of 816 patients with an observed value (69.0%). Concurrent RF and anti-CCP negativity occurred in 164 patients (20.0%). No hand-joint involvement occurred in 191 (23.3%), and asymmetric arthritis in 190 (23.2%).
""")
add_caption(main,'Table 1. Cohort characteristics and outcome frequencies')
add_table(main,MAIN_TABLES[0]);add_note(main,'Continuous variables are median (IQR); categorical variables are n (%). Blank binary fields were not assumed to be negative.')
add_heading(main,'Primary core models',2)
add_paras(main,"""
The primary core ridge model had limited discrimination for negative RF and anti-CCP: AUROC 0.613 (95% CI 0.571 to 0.657). Average precision was 0.244 against a prevalence of 0.200. Log loss was 0.488 and the Brier score was 0.157. The calibration intercept was 0.024 and the slope was 1.019, with broad uncertainty around both quantities.

Performance was stronger for no hand-joint involvement. AUROC reached 0.718 (95% CI 0.677 to 0.757), average precision was 0.383, log loss was 0.492, and the Brier score was 0.162. Calibration point estimates were close to the ideal values, with intercept -0.015 and slope 0.988.

The asymmetric-arthritis core model discriminated weakly. AUROC was 0.566 (95% CI 0.518 to 0.613); average precision was 0.287 against a prevalence of 0.232. Log loss was 0.539 and the Brier score was 0.177. The slope estimate of 0.913 was poorly determined. Ordinary logistic regression did not produce a convincing improvement and was unstable for asymmetric arthritis, supporting shrinkage in the primary specification.
""")
add_caption(main,'Table 2. Performance of prespecified primary core ridge models')
add_table(main,MAIN_TABLES[1]);add_note(main,'Patient-level probabilities were averaged across ten repeated nested OOF predictions. Intervals are 95% patient-bootstrap confidence intervals.')
add_heading(main,'Broad penalized and exploratory models',2)
add_paras(main,"""
Refined broad ridge improved each endpoint relative to core ridge. For negative serology, AUROC increased by 0.078 (95% CI 0.036 to 0.121), average precision by 0.065 (0.026 to 0.113), and log loss decreased by 0.025 (0.012 to 0.037). For no hand-joint involvement, the paired AUROC gain was 0.057 (0.027 to 0.089), with a 0.035 (0.018 to 0.052) reduction in log loss. For asymmetric arthritis, AUROC increased by 0.090 (0.044 to 0.138) and log loss decreased by 0.025 (0.011 to 0.038). Broad elastic net and broad ridge were close across outcomes.

XGBoost was retained as an exploratory final model for the two joint-pattern endpoints. For no hand-joint involvement, its AUROC was 0.796, average precision 0.523, log loss 0.440, and Brier score 0.143. The corresponding refined broad ridge values were 0.774, 0.484, 0.457, and 0.149. For asymmetric arthritis, XGBoost yielded AUROC 0.675 and log loss 0.506, compared with 0.657 and 0.514 for refined broad ridge. Random forest was competitive for both endpoints and had the highest AUROC for no hand-joint involvement, 0.799, but it did not offer a clear probability-accuracy advantage over XGBoost. No complex family won consistently across outcomes or metrics.
""")
add_caption(main,'Table 3. Internally validated performance attached to final model specifications')
add_table(main,MAIN_TABLES[2],font=7.7);add_note(main,'Roles preserve the analytical hierarchy. These OOF estimates precede and are distinct from final all-data refitting.')
add_figure(main,ROOT/'ra_analysis/stage4h_manuscript/figures/Figure_2_oof_performance_forest.png','Figure 2. Repeated nested OOF performance of the model specifications retained for final refitting.','The broad models improved discrimination and proper scoring rules relative to core ridge. XGBoost gains were largest for no hand-joint involvement. Confidence intervals describe patient-level bootstrap uncertainty.',6.65)
add_heading(main,'Calibration, model-family selection, and robustness',2)
add_paras(main,"""
Calibration slopes for refined broad ridge were near one: 1.107 for negative serology, 1.099 for no hand-joint involvement, and 0.999 for asymmetric arthritis. Smoothed curves became uncertain at the edges of the prediction range, where few observations were available. These tails should not be read as precise evidence of calibration.

The fully nested family selector produced AUROCs of 0.688, 0.799, and 0.671 for negative serology, no hand-joint involvement, and asymmetric arthritis. Random forest was chosen in 80% of outer fits for negative serology. XGBoost was chosen in 66% for no hand-joint involvement. Selection for asymmetric arthritis split between random forest (50%) and XGBoost (42%). The selector did not supply a stable reason to abandon the prespecified hierarchy.

Removal of the joint domain reduced no-hand discrimination sharply. Refined broad ridge AUROC fell from 0.774 to 0.673; XGBoost fell from 0.796 to 0.663. The decreases were 0.101 and 0.133. For asymmetry, removal of the same domain produced smaller ridge deterioration and a clearer XGBoost decrease. These results show that much of the signal for contemporaneous joint-pattern labels came from other joint-location variables recorded at the same examination. They do not establish pre-examination prediction.

Missingness-only models performed poorly, with AUROCs of 0.629, 0.559, and 0.535. Near-complete-predictor models and models without explicit flags were much closer to the full broad models. Outcome prevalence differed across corrected missingness categories. The >5% missing category had 4.8% negative serology, 9.0% no hand involvement, and 36.2% asymmetric arthritis. These patterns may reflect assessment processes, case mix, or both. Subgroup estimates were descriptive.
""")
add_figure(main,ROOT/'manuscript_figure_renders/CLEAN_locked_models_flexible_calibration.png','Figure 3. Flexible calibration of locked repeated OOF predictions.','Calibration was most regular for no hand-joint involvement. Curves at the edges are supported by fewer patients and have broad bootstrap bands. The figure is descriptive and does not support threshold selection.',6.65)
add_heading(main,'Prediction stability',2)
add_paras(main,"""
Patient-specific probabilities varied more across repeated training samples for XGBoost than for refined broad ridge. Mean OOF probability standard deviations for XGBoost were 0.038 for negative serology, 0.050 for no hand involvement, and 0.047 for asymmetry. Broad ridge values were 0.023, 0.028, and 0.030. The maximum XGBoost standard deviation reached 0.155 for no hand involvement. Small aggregate gains therefore coexisted with less stable estimates for some patients.
""")
add_figure(main,ROOT/'uploads/patient_level_prediction_instability.png','Figure 4. Mean patient-level variation in predicted probability across ten outer repeats.','XGBoost was less stable than refined broad ridge for every outcome. This comparison concerns sensitivity to training-sample perturbation, not discrimination or calibration.',6.55)
add_heading(main,'OOF SHAP magnitude and direction',2)
add_paras(main,"""
All 12 signed OOF SHAP datasets passed audit. Each contained 820 unique VisitIDs and contributions of both signs. The files covered three outcomes and four prespecified regression specifications. Exact linear additivity held by construction within outer folds.

For negative RF and anti-CCP in the core ridge model, RA duration had the largest mean absolute OOF SHAP value, 0.2903. Longer duration moved predictions toward negative serology. Tender-joint count ranked second at 0.1184 and higher values moved toward the event. Higher swollen-joint count, patient global assessment, and age moved away, with mean absolute values of 0.1033, 0.0855, and 0.0785. Sex contributed less, 0.0485; female category contributions were toward negative serology and male contributions away. Abnormal CRP or ESR had limited magnitude, 0.0223.

For no hand-joint involvement, tender-joint count dominated the core model, with mean absolute OOF SHAP 0.5651. Higher counts moved predictions away from absence of hand involvement. Abnormal CRP or ESR ranked second at 0.2001 and its presence moved predictions toward the event. Longer RA duration and older age also moved toward, with mean absolute values of 0.1611 and 0.0615. Higher swollen-joint count and patient global assessment moved away, at 0.1002 and 0.0789. Sex contributed little.

For asymmetric arthritis, all six non-sex core predictors moved away from the positive phenotype as their values increased. RA duration and tender-joint count had the largest magnitudes, 0.0791 and 0.0785. Age, abnormal inflammatory markers, swollen-joint count, and patient global assessment followed. Male sex moved predictions toward asymmetry and female sex away, but the magnitude was small, 0.0063. The direction of RA duration changed in some broad specifications, so it should not be treated as a stable independent relationship after broad adjustment.

Broad models generated additional signals. Longer duration, higher triglyceride-glucose index, vitamin D deficiency, and higher tender count tended to move negative-serology predictions toward the event. Constitutional symptoms excluding fatigue and higher swollen count moved them away. For no hand involvement, sacroiliac, knee, and ankle involvement moved predictions toward the event, whereas tender-joint count and constitutional symptoms moved away. For asymmetry, elbow involvement and RF positivity moved predictions toward the event; tender count, initial soft-tissue presentation, and vitamin D deficiency moved away. Correlation and attribution sharing are credible explanations for sign changes across specifications.
""")
add_caption(main,'Table 4. Magnitude and direction of core-ridge signed OOF SHAP contributions')
add_table(main,direction_rows(),font=7.8);add_note(main,'Mean |OOF SHAP| is on the log-odds scale. “Toward” and “away” refer to the named positive outcome. Direction is predictive, conditional on the fitted model, and not causal.')
add_figure(main,ROOT/'manuscript_figure_renders/MAIN_core_oof_shap_magnitude.png','Figure 5. Mean absolute signed OOF SHAP magnitude for the primary core-ridge models.','RA duration dominated the negative-serology model. Tender-joint count dominated no hand-joint involvement. The asymmetry model had smaller, more diffuse contributions. Magnitude alone does not indicate direction.',6.35)
add_figure(main,ROOT/'manuscript_figure_renders/CLEAN_MAIN_direction_contrasts.png','Figure 6. Directional high-versus-low or present-versus-absent SHAP contrasts for the primary models.','Positive contrasts move predictions toward the named phenotype; negative contrasts move them away. These contrasts describe fitted predictive functions and are not causal estimates or confidence intervals.',6.35)
add_heading(main,'TreeSHAP and Kernel SHAP audit',2)
add_paras(main,"""
Exact SHAP additivity errors for the six final ridge models were at machine precision, 2.22×10^-16 to 8.88×10^-16. TreeSHAP explained all 820 patients for both XGBoost models. Maximum additivity error was 3.66×10^-6 for no hand involvement and 4.17×10^-6 for asymmetry. Kernel SHAP ran for all eight packaged models using 120 stratified explanation patients and 30 background patients per model.

Magnitude ranks from TreeSHAP and Kernel SHAP agreed closely. Spearman rank correlation was 0.966 across 66 predictors for no hand-joint involvement and 0.989 across 70 predictors for asymmetric arthritis. Agreement between two attribution algorithms reduces concern that the leading XGBoost rankings arose solely from one explainer. It does not resolve dependence among predictors, background-sample sensitivity, or the descriptive status of full-cohort explanations.
""")
add_figure(main,ROOT/'manuscript_figure_renders/MAIN_method_agreement.png','Figure 7. Agreement of TreeSHAP and KernelSHAP magnitude rankings for the XGBoost models.','Rank concordance was high for both joint-pattern endpoints. Agreement is a method-sensitivity check and does not validate the models in new patients.',6.6)
add_heading(main,'Final fitting and technical audit',2)
add_paras(main,"""
Eight frozen pipelines were refitted with all 820 patients. The tuning record contained all 202 expected candidates. Thirty execution checks and 22 independent checks passed. Predictions after serialized reload were identical for all eight models. Fresh-process command-line predictions also passed; the largest absolute difference was 9.12×10^-10. The complete SHAP run passed 12 further checks and registered 326 artifacts. These checks support computational reproducibility. They do not address transportability or patient benefit.
""")

add_heading(main,'Discussion',1)
add_heading(main,'Principal findings',2)
add_paras(main,"""
Three results deserve separate attention. First, the seven-variable core carried useful but uneven information. It worked best for no hand-joint involvement, less well for negative serology, and poorly for asymmetry. Second, broad contemporaneous assessment data improved every outcome. The improvement was largest where anatomic variables described other parts of the same joint examination. Third, nonlinear models added only modest aggregate gains over broad ridge and produced less stable patient-level probabilities.

The analytical hierarchy prevents a common error in small clinical machine-learning studies: interpreting the numerically best algorithm as the best-supported model. The broad sets contained far more candidate parameters than the cohort could support without strong shrinkage and careful validation. The XGBoost findings are useful as exploratory evidence of nonlinear structure. They are not a license to ignore effective sample size, calibration, or external validation.
""")
add_heading(main,'Negative RF and anti-CCP phenotype',2)
add_paras(main,"""
The weak core discrimination for negative serology is clinically plausible. Serostatus is an immunological phenotype, and a short list of age, duration, joint counts, inflammatory status, and patient global assessment cannot be expected to recover all determinants of RF and ACPA expression. The broad ridge improvement indicates that additional contemporaneous features carried information, but AUROC remained 0.691. This is insufficient for stand-alone classification.

Longer RA duration produced the largest core SHAP magnitude and moved predictions toward concurrent RF and anti-CCP negativity. This association may reflect referral patterns, survivor or treatment-related selection, cohort composition, or delayed recognition of seronegative disease. It should not be read as evidence that time causes autoantibody loss. Coffey and colleagues reported longer delays to clinical diagnosis and DMARD treatment among seronegative patients, and other inception cohorts have shown that seronegative RA can present with substantial inflammatory activity.[17,18] The present cross-sectional result fits a setting in which duration and ascertainment are connected; it cannot identify the pathway.

Higher tender count moved the core prediction toward negative serology, whereas swollen count and patient global assessment moved it away. Seronegative early RA has sometimes shown higher clinical disease activity than seropositive RA, including greater joint burden in early cohorts.[18,19] Differences among tender counts, swollen counts, and patient-reported assessment can also arise from pain mechanisms and examination variability. The model has found a conditional pattern in this dataset. It has not separated inflammation from measurement or treatment effects.
""")
add_heading(main,'No hand-joint involvement phenotype',2)
add_paras(main,"""
No hand-joint involvement was the most learnable endpoint. A higher tender 28-joint count strongly moved core predictions away from the event, and broad joint-location variables added substantial information. The removal analysis makes the source of this performance plain: XGBoost AUROC fell by 0.133 when the joint domain was removed. Much of the prediction came from the distribution of articular findings recorded during the same assessment.

This does not make the result circular, because direct hand-outcome components and proxies were excluded. It does make the use case narrow. The models describe a completed examination. They are not validated triage tools before joint assessment. Studies of early RA report meaningful diversity in joint location. In a national cohort of 1,816 patients, symmetrical swelling was present in 75%, not all patients.[19] Joint-specific clustering has identified hand, metatarsophalangeal, and large-joint groupings, and newer replication work has separated foot-predominant, seropositive oligoarticular, seronegative hand, and polyarticular patterns.[20,31] The present result belongs to that descriptive phenotype literature rather than to diagnosis.

Abnormal CRP or ESR moved core predictions toward no hand involvement. Sacroiliac, knee, and ankle involvement were positive broad-model contributors. Such findings may identify patients whose current inflammatory burden is located outside the hands. Differential diagnosis remains relevant because axial or sacroiliac findings can also point away from classical RA. A SHAP contribution is not confirmation that the label is correct.
""")
add_heading(main,'Asymmetric arthritis phenotype',2)
add_paras(main,"""
Asymmetry was difficult to estimate from the core variables. The primary AUROC of 0.566 was close to chance ranking. Broad ridge and XGBoost improved discrimination to 0.657 and 0.675. The ceiling remained modest, which may reflect label heterogeneity, examination noise, temporal variation in joint patterns, and limited information about laterality in the candidate set.

RA is often described as symmetric, but asymmetry is not rare and symmetry is not part of the 2010 classification score.[16] Zangger and colleagues reported asymmetric small-joint damage and studied its change over time.[21] Early-presentation data likewise show that about one quarter of patients lacked symmetrical swelling.[19] The present core SHAP pattern, in which greater duration and higher joint counts moved away from asymmetry, is compatible with increasing bilateral involvement as disease becomes more extensive. That interpretation remains tentative. Duration changed sign in some broad models, and correlated joint variables can redistribute attribution.

Elbow involvement and RF positivity moved broad-model predictions toward asymmetry, whereas tender count and initial soft-tissue presentation moved them away. These are conditional model explanations. They are best used to formulate hypotheses for longitudinal, joint-level studies with explicit laterality, imaging, and repeated examinations.
""")
add_heading(main,'What the comparison of model families adds',2)
add_paras(main,"""
Random forest and XGBoost often ranked well, but model-family superiority was not stable. The nested selector chose random forest for most negative-serology folds, XGBoost for most no-hand folds, and split its choices for asymmetry. This instability is scientifically informative. Several families can approximate similar signal in a dataset of this size, and small changes in training observations alter which family appears best.

Probability stability strengthens this point. XGBoost varied more across repeats for the same patient. An AUROC gain at cohort level can coexist with clinically relevant movement in an individual's estimated probability. A model intended for patient-facing use would need external calibration, stability assessment under data shift, and evaluation of consequences at a specified decision threshold. None has been completed here.
""")
add_heading(main,'Interpretation of SHAP results',2)
add_paras(main,"""
The OOF SHAP design is stronger than calculating explanations after fitting once to the full cohort. Each OOF contribution came from a model that had not seen the explained patient. Direction was recovered from signed values linked to raw predictors, not inferred from mean-absolute bar charts. The analysis also used exact linear, TreeSHAP, and Kernel SHAP methods for their appropriate model classes.[11,12]

These safeguards do not convert SHAP into causal analysis. Shapley allocations depend on the fitted function, the background distribution, the feature representation, and the handling of dependence. Correlated predictors can divide or exchange credit.[13] A feature can be important because it is a proxy, because it participates in an interaction, or because it records a clinical process. Near-zero mean signed SHAP can coexist with high importance when positive and negative patient contributions cancel. For these reasons, the manuscript reports mean absolute magnitude and direct high-versus-low or category-specific direction.

The close TreeSHAP and Kernel SHAP rank correlations support the robustness of leading XGBoost rankings to explainer choice. Kernel SHAP used only 120 patients and 30 background observations per model, so weaker ranks remain subject to Monte Carlo and background-sample variation. The result is a method audit, not independent clinical validation.
""")
add_heading(main,'Relation to RA machine-learning literature',2)
add_paras(main,"""
Recent reviews document rapid growth of machine learning in RA for diagnosis, imaging, prognosis, and treatment response.[24-26] Reported discrimination is often high, but evaluation design and reporting remain uneven. A 2024 systematic review of treatment-response models found frequent concerns about risk of bias and transparency.[24] The present study addresses several recurrent problems by nesting all data-dependent operations, reporting calibration and proper scoring rules, preserving a primary low-complexity model, and withholding apparent full-cohort performance.

Direct numerical comparison with treatment-response or diagnostic models would be misleading. The endpoints here are contemporaneous phenotype labels in a known RA cohort. Case mix, target definition, and intended use differ. Even a higher AUROC would not establish clinical value without a decision context.
""")
add_heading(main,'Strengths',2)
add_paras(main,"""
The study used the same 820-patient cohort for three separately defined outcomes and retained outcome-specific leakage controls. Validation covered the entire preprocessing and tuning procedure. Patient-level repeated OOF predictions prevented duplicated weighting. Performance reporting included discrimination, average precision, calibration, log loss, and Brier score. Paired bootstrap comparisons retained dependence between models.

The work also recorded failures and constraints. OnlyLargeJoints was removed after the analytical decision. The invalid missingness-tertile analysis was superseded rather than defended. Blank binary values were retained as unknown. The final packages were tested after serialization and in new processes. Signed OOF SHAP files were audited for both signs and linked to raw predictors before direction was reported.
""")
add_heading(main,'Limitations',2)
add_paras(main,"""
This is a single-cohort internal-validation study. Geographic, temporal, and health-system transportability are unknown. The sample contained 820 patients and 164 to 191 events per outcome. That was adequate for the compact primary model but small relative to broad parameter counts and nonlinear search spaces. Penalization and nested validation reduce overfitting; they do not remove it.

The analysis is cross-sectional. Several predictors were measured at the same visit as the phenotype, and joint-location variables were clinically close to the two articular outcomes. The models may describe how clinicians recorded a completed examination rather than how to recognize a phenotype before examination. Treatment before assessment, referral, disease duration, and measurement practice could influence predictors and labels.

Outcome definitions came from the verified clinical dataset. Inter-rater agreement, repeated examination reliability, and imaging confirmation were unavailable. Asymmetry is especially sensitive to timing and the number of joints examined. Grip-strength direction could not be linked under the derived MeanGripStrength name in the raw dataset, so no directional claim is made for that variable.

Missingness was informative. Prevalence varied sharply across corrected missingness groups. Models that omit or alter missing-data processes may transport poorly to another setting. Missingness-only models performed poorly, which argues against a purely administrative classifier, but it does not eliminate bias from assessment patterns.

No external validation, prospective evaluation, fairness analysis, decision-curve analysis, or impact study was performed. Sex was examined as recorded; broader gender and sociodemographic structure was not available. The study does not supply a clinical threshold. Full-cohort final-fit SHAP values are descriptive. Kernel SHAP used a limited reproducible sample for computational feasibility.
""")
add_heading(main,'Implications and next studies',2)
add_paras(main,"""
The core models quantify how much can be learned from seven routine variables. For negative serology and asymmetry, that amount is limited. For no hand involvement, a broader completed joint examination adds clear signal. This may help characterize cohort heterogeneity, but it does not justify clinical deployment.

External evaluation should preserve the exact outcome definitions and preprocessing objects, recruit a sufficiently large number of events, and report calibration before discrimination claims.[9] A useful next design would include joint-level laterality, imaging, treatment timing, referral pathway, and repeated assessments. Temporal data could test whether asymmetry becomes more symmetric and whether the observed duration-serology association persists after accounting for diagnostic delay. Clinical utility should be examined only after a real decision and threshold range are specified.
""")
add_refs(main);footer(main)
main_path=OUT/'RA_Phenotype_Models_Expanded_Main_Manuscript.docx';main.save(main_path)

# ---------------- Supplement ----------------
supp=Document();setup(supp,'Cross-sectional phenotype probability modeling in rheumatoid arthritis','Expanded Supplementary Methods and Results')
add_heading(supp,'Supplementary Methods',1)
add_heading(supp,'Cohort assembly and endpoint handling',2)
add_paras(supp,"""
The verified analytical cohort contained 820 unique VisitIDs. Each record represented one patient at a completed rheumatology assessment. All three endpoints were observed. Endpoint variables were never imputed. Separate binary analyses were required because serostatus, hand involvement, and symmetry are neither mutually exclusive nor alternative levels of a single outcome.

The source dataset, derived outcome-specific files, predictor manifests, split assignments, OOF predictions, fitted checkpoints, and audit tables were connected through VisitID. The identifier was used for bookkeeping only. Assertions checked cohort size, uniqueness, row alignment, outcome coding, and the absence of prohibited predictors before model fitting.

Concurrent RF and anti-CCP negativity was the positive serology event. The other positive events were no hand-joint involvement and asymmetric arthritis. Prevalences were 20.0%, 23.3%, and 23.2%. The 2010 ACR/EULAR criteria provide clinical context for serology and joint involvement, but the present endpoints were phenotype descriptors rather than reimplementations of classification criteria.[16]
""")
add_caption(supp,'Supplementary Table S1. Outcome-specific analysis sets and restrictions');add_table(supp,SUPP_TABLES[0]);add_note(supp,'Raw broad predictor counts refer to final refined sets. Direct outcome components and semantic proxies were excluded separately.')
add_heading(supp,'Core and broad predictor representation',2)
add_paras(supp,"""
The core was fixed before model comparison. Continuous variables remained continuous; arbitrary categorization was avoided. RA duration received log1p transformation because its distribution was right-skewed. The transformation was fitted within the pipeline and mapped back to RA duration for explanation. Sex was categorical. Abnormal CRP or ESR was binary with an allowed unknown state.

Broad manifests classified each eligible variable as numerical, binary, or categorical. Fixed category levels were used where required for portable refitting. Reference coding, explicit unknown categories, and missingness indicators increased transformed dimension to 96, 95, and 99 columns for the final broad models.
""")
add_caption(supp,'Supplementary Table S2. Core predictor processing');add_table(supp,SUPP_TABLES[1]);add_note(supp,'All stated operations were fitted using training data only.')
add_heading(supp,'Complexity calculations',2)
add_paras(supp,"""
Formal calculations used the observed event count, anticipated model fit, target shrinkage, and optimism control described by Riley and colleagues.[3,4] The aim was to assess whether the initial broad parameterization could be regarded as a conventional low-dimensional model. It could not. Required sample sizes were 8,123 to 8,620 under the conservative assumptions. About nine parameters were supported at N=820. The calculation informed the hierarchy rather than acting as a mechanical prohibition against penalized exploratory models.
""")
add_caption(supp,'Supplementary Table S3. Model-complexity assessment');add_table(supp,SUPP_TABLES[2]);add_note(supp,'Events per parameter is shown descriptively; model planning did not rely on a fixed threshold.')
add_heading(supp,'Candidate algorithms and tuning',2)
add_paras(supp,"""
Core ridge and ordinary logistic regression used the same seven raw predictors. Broad ridge and elastic net used outcome-specific manifests. Expanded families comprised lasso, linear SVC, RBF SVC, random forest, AdaBoost, and XGBoost. Hyperparameter grids or distributions were frozen before outer test predictions. SVC probabilities were calibrated within training data. Natural event prevalence was retained.

Inner validation minimized log loss. The one-standard-error rule selected stronger regularization for ridge and structurally simpler configurations for nonlinear models when eligible. The expanded benchmark compared fixed families on common outer splits. A separate nested selector chose the family using inner data in each outer training set. This distinction prevents test-fold performance from choosing the algorithm.
""")
add_heading(supp,'Repeated nested cross-validation and bootstrap inference',2)
add_paras(supp,"""
Outer stratified five-fold cross-validation was repeated ten times. Within every outer training set, inner five-fold validation fitted preprocessing and selected hyperparameters. Held-out patients were transformed with training-derived objects and predicted once. The resulting ten OOF probabilities per patient were averaged. Fold-level rows remained available for stability and explanation audits but were not treated as 8,200 independent patients.

Two thousand patient-level bootstrap resamples produced percentile confidence intervals. Paired comparisons resampled the same patient indices for both models. Calibration curves were restricted to regions supported by predictions. Intercept and slope estimates were supplemented by curves because neither coefficient captures local miscalibration.[7,8]
""")
add_heading(supp,'Robustness and missingness analyses',2)
add_paras(supp,"""
Semantic-domain removal targeted clinically proximate joint variables for no hand involvement and asymmetry. Missingness sensitivity included three designs: missingness indicators alone, predictors selected for near-complete observation, and substantive predictors without explicit missingness flags. The corrected missingness grouping preserved tied fractions. Complete records formed one group; nonzero fractions up to 5% formed the second; fractions greater than 5% formed the third. The obsolete row-order-dependent grouping was removed from every inferential claim.
""")
add_heading(supp,'Explainability procedures',2)
add_paras(supp,"""
OOF linear SHAP values were generated inside the outer loop. For each transformed test matrix, the outer-training transformed mean defined the background. The centered test value was multiplied by the fitted coefficient. Contributions were summed across one-hot columns and missingness flags belonging to the same raw variable. The base value plus grouped contributions reproduced the model decision score. Ten OOF contributions were averaged by VisitID.

Direction analysis joined contributions to raw values. A numerical high-versus-low contrast compared mean contribution in the upper and lower quintiles, supplemented by Spearman rank association. Binary variables compared observed 1 and 0 values. Categorical variables retained category-specific means. These summaries are descriptive. Fixed thresholds used for automated labels were not treated as inferential significance tests.

Final-fit exact linear SHAP used all 820 patients for six ridge packages. Interventional TreeSHAP used all patients and 100 background records for the two XGBoost packages. Kernel SHAP used 120 stratified explanation records, 30 background records, and 512 evaluations for each of eight packages. Explanations were aggregated to raw predictors and saved at patient level. Figures were exported as 600-dpi PNG and LZW-compressed TIFF, plus vector PDF and SVG.
""")

add_heading(supp,'Supplementary Results',1)
# Existing S4-S16 tables with concise expanded commentary
comments=[
('Complete prespecified performance','The broad penalized models improved probability accuracy and discrimination for each endpoint. Ridge and elastic net were close, which indicates that the results did not depend on one penalty mixture.'),
('Expanded candidate-family benchmark','Random forest had the lowest log loss for negative serology, and XGBoost had the lowest for the two joint-pattern outcomes. Differences among leading broad families were small. Linear SVC calibrated poorly for negative serology and asymmetry.'),
('Paired comparisons with the primary core model','All reported broad-ridge paired improvements had confidence intervals excluding zero. XGBoost improvements over core ridge also excluded zero for both retained joint-pattern endpoints.'),
('Fully nested family selection','The selector reproduced the approximate performance of the best fixed exploratory families. It did not produce an endpoint-independent winning family.'),
('Model-family selection frequencies','Selection varied across outer samples. Negative serology favored random forest; no hand involvement favored XGBoost; asymmetry divided between random forest and XGBoost.'),
('Semantic-domain removal','Removing joint variables caused the largest deterioration for no hand involvement. The same removal had a smaller effect for asymmetry.'),
('Paired semantic-domain changes','Negative changes denote worse performance after removal. The no-hand losses were large across AUROC, log loss, and Brier score.'),
('Missingness sensitivity','Near-complete and no-flag models remained close to full broad models. Missingness-only models were substantially weaker.'),
('Corrected missingness-category prevalence','Prevalence differed across missingness categories. Tied missingness fractions were kept together.'),
('Performance by corrected missingness category','Subgroup intervals were wide. Differences combine prevalence, case mix, and missing-data processes; no subgroup result selected a model.'),
('Prediction stability','XGBoost had higher patient-level OOF variability for every outcome. The largest maximum SD was 0.155 for no hand involvement.'),
('Final-model registry','All eight pipelines were refitted after freezing specifications. No apparent full-cohort performance was calculated.'),
('Reproducibility audit','All execution, independent, reload, and fresh-process checks passed.')]
for idx,(title,comment) in enumerate(comments,start=3):
    sn=idx+1
    add_heading(supp,title,2);add_paras(supp,comment)
    add_caption(supp,f'Supplementary Table S{sn}. {title}')
    add_table(supp,SUPP_TABLES[idx],font=7.2 if idx in [4,12,14] else 7.8)
    add_note(supp,'All performance values are internally validated OOF estimates unless the table explicitly describes final refitting or audit status.')

add_heading(supp,'Signed OOF SHAP findings',2)
add_paras(supp,"""
Every expected OOF SHAP file was present and valid. Each file contained 820 patients, finite values, and contributions on both sides of zero. Mean absolute contribution ranked variables. Direction was determined from linked raw values.

The negative-serology core model concentrated attribution in RA duration, tender count, and swollen count. The no-hand model was dominated by tender count. The asymmetry core model had smaller contributions spread across duration, tender count, and age. Mean signed contributions were near zero for many variables because patient-level signs differed; this cancellation did not indicate absence of importance.
""")
add_caption(supp,'Supplementary Table S17. Core-ridge OOF SHAP magnitude and direction');add_table(supp,direction_rows(),font=7.6);add_note(supp,'Positive means movement toward the named positive phenotype. Direction is conditional and predictive.')
add_heading(supp,'Final-fit SHAP method audit',2)
ma=[list(METHOD_AUDIT.columns)]+[[str(x) for x in row] for row in METHOD_AUDIT.fillna('').itertuples(index=False,name=None)]
add_caption(supp,'Supplementary Table S18. Exact linear, TreeSHAP, and Kernel SHAP audit');add_table(supp,ma,font=7.2);add_note(supp,'Kernel SHAP used a stratified 120-patient explanation sample and 30 background patients per model. Additivity error is not shown for the sampling approximation.')
add_heading(supp,'TreeSHAP and Kernel SHAP agreement',2)
add_paras(supp,"""
The XGBoost magnitude rankings were highly concordant between TreeSHAP and Kernel SHAP. This result supports method robustness for leading ranks. It does not make the attributions causal and does not remove uncertainty due to correlated inputs.
""")
ag=[list(AGREEMENT.columns)]+[[str(x) for x in row] for row in AGREEMENT.fillna('').itertuples(index=False,name=None)]
add_caption(supp,'Supplementary Table S19. Cross-method rank agreement');add_table(supp,ag);add_note(supp,'Spearman correlations compare mean-absolute SHAP ranks across raw predictors.')
add_heading(supp,'Complete SHAP execution audit',2)
fa=[list(FINAL_AUDIT.columns)]+[[str(x) for x in row] for row in FINAL_AUDIT.fillna('').itertuples(index=False,name=None)]
add_caption(supp,'Supplementary Table S20. SHAP completeness and integrity checks');add_table(supp,fa,font=7.5);add_note(supp,'All 12 checks passed. A pass confirms execution of the specified analysis, not external clinical validity.')
add_heading(supp,'Interpretive limits',2)
add_paras(supp,"""
The validated performance estimates apply to repeated resampling of this development cohort. They do not estimate performance in a different hospital, calendar period, referral pathway, or measurement system. Full-cohort final models inherit these limits. The predictor manifests must be reproduced exactly during external evaluation.

No threshold is recommended. Net benefit was not estimated because a clinical action and error-cost ratio had not been defined. SHAP values describe the fitted prediction functions. A positive contribution moves a prediction toward the outcome relative to the specified background. It does not mean the predictor causes the phenotype or that changing the predictor would alter the outcome.
""")

# Complete figure appendix. Every supplied analysis figure is retained, with obsolete
# or EDA-only outputs explicitly identified rather than silently discarded.
add_heading(supp,'Supplementary Figure Appendix',1)
add_paras(supp,"""
The appendix preserves the complete graphical analysis record. Closely related plots are retained because they answer different questions: magnitude, patient-level direction, calibration, discrimination, model stability, missingness, and explainer agreement. Figures based on final full-cohort fits are descriptive and are separated from OOF validation figures. The old row-order missingness-tertile display is shown only as a superseded audit artifact; all scientific interpretation uses the corrected tie-preserving groups.
""")

def pretty_token(s):
    repl={'NegRFandACCP':'negative RF and anti-CCP','NoHandJointInvolvement':'no hand-joint involvement','AsymmetricArthritis':'asymmetric arthritis','OOF_exact_linear':'OOF exact linear SHAP','Final-fit_exact_linear':'final-fit exact linear SHAP','KernelSHAP':'Kernel SHAP','TreeSHAP':'TreeSHAP','core_ridge':'core ridge','core_logistic':'ordinary core logistic','broad_ridge':'broad ridge','broad_elastic_net':'broad elastic net','refined_broad_ridge':'refined broad ridge','xgboost':'XGBoost'}
    for a,b in repl.items():s=s.replace(a,b)
    return s.replace('__','; ').replace('_',' ')
def fig_text(name):
    stem=Path(name).stem
    if stem.startswith('CLEAN_'):stem=stem[len('CLEAN_'):]
    if stem.startswith('magnitude__'):
        desc=pretty_token(stem[len('magnitude__'):]);return f'SHAP magnitude: {desc}.','Bars rank predictors by mean absolute contribution. This display measures influence but cannot establish whether higher values move predictions toward or away from the outcome.'
    if stem.startswith('beeswarm__'):
        desc=pretty_token(stem[len('beeswarm__'):]);return f'Signed SHAP distribution: {desc}.','Each point is a patient-level contribution. Horizontal position gives direction and magnitude relative to zero; color represents relative raw value where a numerical link was available. Correlated variables may share attribution.'
    if stem.startswith('direction_panels__'):
        desc=pretty_token(stem[len('direction_panels__'):]);return f'Directional SHAP panels: {desc}.','Observed raw values are plotted against signed OOF contributions. The red summaries describe the fitted relationship. Categorical direction is interpreted from separate category-specific results.'
    if stem.startswith('direction_contrast__'):
        desc=pretty_token(stem[len('direction_contrast__'):]);return f'Directional SHAP contrasts: {desc}.','Positive contrasts move the fitted prediction toward the named event; negative contrasts move it away. The contrasts are descriptive, not causal effects or significance tests.'
    if stem.startswith('local_waterfalls__'):
        desc=pretty_token(stem[len('local_waterfalls__'):]);return f'Representative local explanations: {desc}.','The panels show leading contributions for patients near low, median, and high fitted probabilities. They illustrate model behavior and must not be used as patient-specific clinical recommendations.'
    if stem.startswith('method_agreement__'):
        desc=pretty_token(stem[len('method_agreement__'):]);return f'TreeSHAP and Kernel SHAP agreement: {desc}.','Features close to the diagonal receive similar magnitude ranks from the two explainers. High agreement supports ranking robustness to explainer choice but does not supply external validation.'
    if 'performance_and_calibration' in stem:return f'Expanded candidate-family performance and calibration for {pretty_token(stem.split("__")[0])}.','ROC, precision-recall, and decile calibration panels compare the candidate families using patient-averaged OOF predictions. The plots do not change the prespecified model hierarchy.'
    if 'performance_curves' in stem:return f'Prespecified-model performance curves for {pretty_token(stem.split("__")[0])}.','The curves compare the four prespecified regression models. Calibration uncertainty increases at sparsely populated probability extremes.'
    if 'permutation_importance' in stem:return f'Outer-test permutation importance for {pretty_token(stem.split("__")[0])}.','Bars show mean increase in outer-test log loss after permutation; intervals summarize variation across outer fits. Negative or near-zero values do not support stable incremental information.'
    if 'probability_distributions' in stem:return f'OOF probability distributions for {pretty_token(stem.split("__")[0])}.','The figure displays separation and prediction range by observed outcome across candidate families. Range alone is not evidence of calibration.'
    mapping={
      'outer_fold_stability__auroc':('Outer-fold AUROC stability.','Boxplots show variation across outer test folds; model ordering changes across samples.'),
      'outer_fold_stability__log_loss':('Outer-fold log-loss stability.','Lower values are better. Fold variation shows the uncertainty hidden by a single aggregate estimate.'),
      'performance_forest__auroc':('Candidate-family AUROC with patient-bootstrap intervals.','The expanded benchmark did not yield one family that dominated every endpoint.'),
      'performance_forest__average_precision':('Candidate-family average precision with patient-bootstrap intervals.','Average precision is interpreted against outcome prevalence and is particularly relevant for these 20% to 23% events.'),
      'performance_forest__brier':('Candidate-family Brier scores with patient-bootstrap intervals.','Lower values indicate better squared probability error.'),
      'performance_forest__log_loss':('Candidate-family log loss with patient-bootstrap intervals.','Lower values indicate better probability accuracy and penalize confident errors.'),
      'runtime_comparison':('Observed nested-validation fitting time.','Runtime is a computational property, not evidence of predictive validity.'),
      'subgroup_heterogeneity_auroc':('Prespecified subgroup heterogeneity audit.','Locked predictions were evaluated without subgroup refitting. Broad intervals limit claims about sex, age, or missingness-group differences.'),
      'domain_removal_paired_change':('Dependence on contemporaneous joint and anatomy information.','Negative paired changes indicate worse performance after domain removal, strongest for no hand-joint involvement.'),
      'locked_models_flexible_calibration':('Flexible calibration of locked OOF predictions.','Bootstrap bands widen at the tails. No clinical threshold was selected.'),
      'nested_family_selector_audit':('Fully nested model-family selection audit.','Family choice varied across outer samples, and paired gains over broad ridge were not consistent enough to replace the hierarchy.'),
      'patient_level_prediction_instability':('Patient-level prediction instability.','XGBoost probabilities varied more across outer repeats than broad ridge probabilities.'),
      'predictor_missingness_outcome_association':('Outcome-associated predictor missingness differences.','Missingness patterns differ by outcome and may encode assessment practice or case mix.'),
      'missingness_sensitivity_paired_change':('Locked missingness sensitivity comparisons.','Missingness-only models were weaker; near-complete and no-flag models were closer to the locked broad analyses.'),
      'outcome_prevalence_by_missingness_burden':('Superseded row-order missingness-tertile prevalence display.','This figure is retained only for audit history. Its row-order grouping was invalid and it is not used for scientific interpretation.'),
      'corrected_locked_model_missingness_group_auroc':('Corrected tie-preserving missingness-group performance.','The corrected groups are complete, greater than 0% to 5%, and greater than 5% missing. Estimates are exploratory and were not used for selection.'),
      'corrected_outcome_prevalence_by_missingness_group':('Corrected outcome prevalence by tie-preserving missingness group.','Prevalence differs materially across groups, supporting caution about transportability across assessment processes.'),
      'final_hyperparameter_selection':('Final full-cohort hyperparameter selection.','Repeated-CV log loss guided the frozen one-standard-error selection. The plot is not a performance estimate.'),
      'required_sample_size_current_complexity':('Formal sample-size requirement for broad candidate dimensions.','Required sample sizes substantially exceed N=820 across assumptions, which motivated the compact primary model.'),
      'supported_parameter_budget':('Supported complexity under the Riley criteria.','The available sample supports far fewer parameters than the broad encoded sets under conservative assumptions.'),
      '01_outcome_prevalence':('EDA outcome prevalence.','OnlyLargeJoints is displayed as an EDA-only historical outcome and was excluded from all subsequent primary and sensitivity modeling.'),
      '02_outcome_phi_heatmap':('EDA association among binary outcomes.','Pairwise association was descriptive and did not justify combining the three retained phenotypes.'),
      '03_missingness_barplot':('EDA predictor missingness.','Blank binary and comorbidity entries were treated as unknown rather than absence.'),
      '04_missingness_heatmap_top30':('EDA missingness-pattern heatmap.','The heatmap describes co-occurrence of missing fields and motivated fold-contained preprocessing.'),
      '05_numeric_distributions':('EDA numerical predictor distributions.','Skew and range were handled by prespecified transformations and training-fold preprocessing.'),
      '06_categorical_distributions':('EDA categorical predictor distributions.','Sparse categories contributed to the effective parameter count and were handled with fixed encoding.'),
      '07_spearman_redundancy_heatmap':('EDA numerical redundancy.','Correlation among predictors supports cautious interpretation of individual attributions.'),
    }
    if stem in mapping:return mapping[stem]
    if stem.startswith('08_associations_'):return f'EDA univariable associations for {pretty_token(stem[16:])}.','Associations are descriptive, unadjusted, and were not used as global preselection filters.'
    if stem.startswith('09_numeric_by_'):return f'EDA numerical distributions by {pretty_token(stem[14:])}.','The distributions show overlap between classes and do not estimate multivariable performance.'
    if stem.endswith('__oof_shap'):return f'Legacy OOF mean-absolute SHAP ranking for {pretty_token(stem[:-10])}.','This valid magnitude plot is supplemented by signed patient-level direction analysis. Magnitude alone cannot provide direction.'
    return pretty_token(stem).capitalize()+'.','The figure is retained as part of the complete analysis record and is interpreted with the corresponding supplementary results and limitations.'

def width_to_fit(path,max_w=6.7,max_h=8.0):
    from PIL import Image
    with Image.open(path) as im:w,h=im.size
    return min(max_w,max_h*w/h)

fig_paths=[]
# Original raster analysis figures. The calibration source is replaced by a clean
# title-free rendering so the Word caption cannot collide with an internal title.
for p in sorted((ROOT/'uploads').glob('*.png')):
    if p.name != 'locked_models_flexible_calibration.png':fig_paths.append(p)
fig_paths.append(ROOT/'manuscript_figure_renders/CLEAN_locked_models_flexible_calibration.png')
# SHAP PDFs are represented by the identically named high-quality notebook raster outputs.
for p in sorted((ROOT/'manuscript_figure_renders').glob('*.png')):
    if not p.name.startswith(('MAIN_','CLEAN_')):fig_paths.append(p)
seen=set();unique=[]
for p in fig_paths:
    if p.stem not in seen:seen.add(p.stem);unique.append(p)
for i,p in enumerate(unique,1):
    title,interp=fig_text(p.name)
    add_figure(supp,p,f'Supplementary Figure S{i}. {title}',interp,width=width_to_fit(p),page_break=True)

add_refs(supp);footer(supp)
supp_path=OUT/'RA_Phenotype_Models_Expanded_Supplementary_Material.docx';supp.save(supp_path)
print(main_path);print(supp_path)
