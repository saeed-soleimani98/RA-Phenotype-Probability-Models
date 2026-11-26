import os
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, PageBreak,
    Table, TableStyle, KeepTogether, HRFlowable, LongTable
)
from reportlab.pdfgen import canvas
from pathlib import Path
from datetime import date

OUT = Path(os.environ.get('RA_OUTPUT_DIR','./outputs'))/'RA_dataset_issues_and_scientific_decisions.pdf'
OUT.parent.mkdir(parents=True, exist_ok=True)

# Fonts with broad Unicode support.
pdfmetrics.registerFont(TTFont('DejaVu', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DejaVu-Bold', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
pdfmetrics.registerFont(TTFont('DejaVuSerif-Bold', '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'))

NAVY = HexColor('#132A3A')
TEAL = HexColor('#146C72')
DARK_TEAL = HexColor('#0F4C5C')
GOLD = HexColor('#D49B28')
BURGUNDY = HexColor('#7A263A')
GREEN = HexColor('#2E6B4F')
SLATE = HexColor('#425466')
LIGHT_BLUE = HexColor('#DCE8EC')
LIGHT_GOLD = HexColor('#F4E7C5')
LIGHT_RED = HexColor('#F2DDE2')
LIGHT_GREEN = HexColor('#DCEADF')
OFF_WHITE = HexColor('#F7F8F6')
MID_GREY = HexColor('#D4DADF')
TEXT = HexColor('#1D2730')

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='CoverTitle', fontName='DejaVuSerif-Bold', fontSize=25, leading=31,
                          textColor=NAVY, alignment=TA_CENTER, spaceAfter=16))
styles.add(ParagraphStyle(name='CoverSub', fontName='DejaVu', fontSize=12, leading=18,
                          textColor=SLATE, alignment=TA_CENTER, spaceAfter=10))
styles.add(ParagraphStyle(name='H1x', fontName='DejaVu-Bold', fontSize=17, leading=21,
                          textColor=NAVY, spaceBefore=10, spaceAfter=9, keepWithNext=True))
styles.add(ParagraphStyle(name='H2x', fontName='DejaVu-Bold', fontSize=13, leading=17,
                          textColor=DARK_TEAL, spaceBefore=10, spaceAfter=6, keepWithNext=True))
styles.add(ParagraphStyle(name='H3x', fontName='DejaVu-Bold', fontSize=11, leading=15,
                          textColor=BURGUNDY, spaceBefore=7, spaceAfter=4, keepWithNext=True))
styles.add(ParagraphStyle(name='Bodyx', fontName='DejaVu', fontSize=9.4, leading=14,
                          textColor=TEXT, spaceAfter=6))
styles.add(ParagraphStyle(name='Smallx', fontName='DejaVu', fontSize=8, leading=11,
                          textColor=SLATE, spaceAfter=3))
styles.add(ParagraphStyle(name='Bulletx', fontName='DejaVu', fontSize=9.2, leading=13.2,
                          textColor=TEXT, leftIndent=14, firstLineIndent=-8, bulletIndent=4, spaceAfter=3))
styles.add(ParagraphStyle(name='Calloutx', fontName='DejaVu', fontSize=9.4, leading=14,
                          textColor=NAVY, backColor=LIGHT_BLUE, borderColor=TEAL,
                          borderWidth=0.8, borderPadding=9, spaceBefore=5, spaceAfter=9))
styles.add(ParagraphStyle(name='Warningx', fontName='DejaVu', fontSize=9.4, leading=14,
                          textColor=BURGUNDY, backColor=LIGHT_RED, borderColor=BURGUNDY,
                          borderWidth=0.8, borderPadding=9, spaceBefore=5, spaceAfter=9))
styles.add(ParagraphStyle(name='Decisionx', fontName='DejaVu', fontSize=9.4, leading=14,
                          textColor=GREEN, backColor=LIGHT_GREEN, borderColor=GREEN,
                          borderWidth=0.8, borderPadding=9, spaceBefore=5, spaceAfter=9))
styles.add(ParagraphStyle(name='TableHeader', fontName='DejaVu-Bold', fontSize=8, leading=10,
                          textColor=colors.white))
styles.add(ParagraphStyle(name='TableCell', fontName='DejaVu', fontSize=7.8, leading=10.2,
                          textColor=TEXT))
styles.add(ParagraphStyle(name='TableCellBold', fontName='DejaVu-Bold', fontSize=7.8, leading=10.2,
                          textColor=TEXT))


def P(text, style='Bodyx'):
    return Paragraph(text, styles[style])


def bullets(items):
    return [P('• ' + item, 'Bulletx') for item in items]


def section_issue(title, issue, decision, reason, implementation=None, status='CONFIRMED'):
    out = [P(title, 'H2x')]
    out.append(P(f'<b>The issue:</b> {issue}'))
    label = 'Agreed solution' if status == 'CONFIRMED' else 'Scientific recommendation'
    sty = 'Decisionx' if status == 'CONFIRMED' else 'Calloutx'
    out.append(P(f'<b>{label}:</b> {decision}', sty))
    out.append(P(f'<b>Why this is scientifically reasonable:</b> {reason}'))
    if implementation:
        out.append(P(f'<b>How it will be implemented:</b> {implementation}'))
    return out


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(total)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, total):
        if self._pageNumber == 1:
            return
        self.saveState()
        self.setStrokeColor(MID_GREY)
        self.line(1.6*cm, 1.35*cm, A4[0]-1.6*cm, 1.35*cm)
        self.setFont('DejaVu', 7.5)
        self.setFillColor(SLATE)
        self.drawString(1.6*cm, 0.9*cm, 'Atypical RA dataset: issues and scientific decisions')
        self.drawRightString(A4[0]-1.6*cm, 0.9*cm, f'Page {self._pageNumber} of {total}')
        self.restoreState()


def header_footer(canvas_obj, doc):
    if doc.page == 1:
        return
    canvas_obj.saveState()
    canvas_obj.setFillColor(NAVY)
    canvas_obj.rect(0, A4[1]-1.05*cm, A4[0], 1.05*cm, fill=1, stroke=0)
    canvas_obj.setFont('DejaVu-Bold', 8)
    canvas_obj.setFillColor(colors.white)
    canvas_obj.drawString(1.6*cm, A4[1]-0.68*cm, 'RA CLINICAL PREDICTION PROJECT')
    canvas_obj.setFont('DejaVu', 7.5)
    canvas_obj.drawRightString(A4[0]-1.6*cm, A4[1]-0.68*cm, 'Decision report | Stage 1 complete')
    canvas_obj.restoreState()


frame = Frame(1.6*cm, 1.55*cm, A4[0]-3.2*cm, A4[1]-2.95*cm, id='normal')
doc = BaseDocTemplate(str(OUT), pagesize=A4, rightMargin=1.6*cm, leftMargin=1.6*cm,
                      topMargin=1.4*cm, bottomMargin=1.55*cm,
                      title='Atypical RA Dataset: Issues and Scientific Decisions',
                      author='RA Clinical Prediction Project')
doc.addPageTemplates([PageTemplate(id='main', frames=frame, onPage=header_footer)])

story = []

# Cover
story += [Spacer(1, 2.0*cm), P('Atypical Presentations of Rheumatoid Arthritis', 'CoverTitle'),
          P('Dataset Issues, Agreed Scientific Solutions, and Reasons for Each Decision', 'CoverSub'),
          Spacer(1, 0.4*cm), HRFlowable(width='72%', thickness=2, color=TEAL, spaceBefore=8, spaceAfter=18),
          P('<b>Dataset:</b> 820 patients, 95 recorded columns', 'CoverSub'),
          P('<b>Current outcomes:</b> Seronegative RA, no hand-joint involvement, and asymmetric arthritis', 'CoverSub'),
          P('<b>Study type:</b> Cross-sectional clinical prediction study', 'CoverSub'),
          Spacer(1, 0.5*cm),
          P('Written in plain language for clinicians, researchers, reviewers, and readers without specialist knowledge of artificial intelligence.', 'Calloutx'),
          Spacer(1, 2.5*cm),
          P('<b>Report version:</b> 1.0<br/><b>Date:</b> 25 September 2026<br/><b>Status:</b> Data and analysis-method decisions recorded; final model family intentionally deferred.', 'CoverSub'),
          PageBreak()]

# Reader guide
story += [P('How to read this report', 'H1x'),
          P('Each section uses the same four questions: What is the problem? What did we decide? Why is that decision scientifically reasonable? How will it be applied? The report separates confirmed decisions from recommendations that still need a final choice.'),
          P('<b>Important:</b> A prediction model finds patterns that help classify patients. It does not automatically prove that a feature causes an atypical RA presentation.', 'Warningx'),
          P('Plain-language glossary', 'H2x')]

glossary = [
    [P('Term', 'TableHeader'), P('Meaning in simple words', 'TableHeader')],
    [P('Predictor', 'TableCellBold'), P('A patient feature used by a model, such as age, CRP/ESR status, smoking, or joint count.', 'TableCell')],
    [P('Outcome', 'TableCellBold'), P('The condition the model is trying to identify, such as seronegative RA.', 'TableCell')],
    [P('Data leakage', 'TableCellBold'), P('Giving the model information that directly contains the answer. This makes performance look better than it really is.', 'TableCell')],
    [P('Imputation', 'TableCellBold'), P('A planned method for handling a missing value without pretending that the missing value means “no.”', 'TableCell')],
    [P('Regularization', 'TableCellBold'), P('A method that limits how complex a model can become, reducing overfitting.', 'TableCell')],
    [P('Cross-validation', 'TableCellBold'), P('Repeatedly training on one part of the data and testing on patients not used for that training.', 'TableCell')],
    [P('Sensitivity analysis', 'TableCellBold'), P('A second analysis using another reasonable choice to check whether the conclusion changes.', 'TableCell')],
]
t = Table(glossary, colWidths=[3.3*cm, 13.2*cm], repeatRows=1)
t.setStyle(TableStyle([
    ('BACKGROUND',(0,0),(-1,0),NAVY), ('VALIGN',(0,0),(-1,-1),'TOP'),
    ('GRID',(0,0),(-1,-1),0.35,MID_GREY), ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,OFF_WHITE]),
    ('LEFTPADDING',(0,0),(-1,-1),6), ('RIGHTPADDING',(0,0),(-1,-1),6),
    ('TOPPADDING',(0,0),(-1,-1),5), ('BOTTOMPADDING',(0,0),(-1,-1),5),
]))
story += [t, Spacer(1, 0.25*cm), PageBreak()]

# Executive summary
story += [P('Executive summary', 'H1x'),
          P('The dataset can support careful internal prediction research, but it contains missing values, a few likely data-entry errors, overlapping variables, rare categories, and variables that nearly reveal the outcome. These issues do not make the dataset unusable. They require transparent rules before modeling.'),
          P('<b>Main scientific aim:</b> Build three separate models that classify atypical RA presentations at the same clinical visit. Because the data are cross-sectional, the models will not be described as predicting future disease or proving causation.', 'Calloutx')]

summary_data = [
    [P('Area', 'TableHeader'), P('Agreed direction', 'TableHeader')],
    [P('Outcomes', 'TableCellBold'), P('Analyze seronegative RA, no hand involvement, and asymmetric arthritis separately. Remove only-large-joint disease from this project.', 'TableCell')],
    [P('Data errors', 'TableCellBold'), P('Correct age 6 to 60 as investigator supplied; set four extreme grip values and one isolated TyG value to missing in a scripted cleaning step.', 'TableCell')],
    [P('Missing data', 'TableCellBold'), P('Do not treat blanks as “no.” Impute using training data only; run a more advanced imputation sensitivity analysis.', 'TableCell')],
    [P('Leakage', 'TableCellBold'), P('Remove variables that directly define each outcome from the primary model.', 'TableCell')],
    [P('Rare fields', 'TableCellBold'), P('Exclude binary fields with fewer than 10 observations in either category; do not invent clinically false category groupings.', 'TableCell')],
    [P('Validation', 'TableCellBold'), P('Use repeated nested five-fold cross-validation, not one train/test split.', 'TableCell')],
    [P('Model choice', 'TableCellBold'), P('Deferred by investigator. No final algorithm has been selected.', 'TableCell')],
]
t = Table(summary_data, colWidths=[3.5*cm, 13.0*cm], repeatRows=1)
t.setStyle(TableStyle([
    ('BACKGROUND',(0,0),(-1,0),TEAL), ('VALIGN',(0,0),(-1,-1),'TOP'),
    ('GRID',(0,0),(-1,-1),0.35,MID_GREY), ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,OFF_WHITE]),
    ('LEFTPADDING',(0,0),(-1,-1),6), ('RIGHTPADDING',(0,0),(-1,-1),6),
    ('TOPPADDING',(0,0),(-1,-1),5), ('BOTTOMPADDING',(0,0),(-1,-1),5),
]))
story += [t, Spacer(1, 0.3*cm)]

# Dataset at glance
story += [P('1. Dataset at a glance', 'H1x')]
info = [
    [P('Item', 'TableHeader'), P('Verified finding', 'TableHeader'), P('Why it matters', 'TableHeader')],
    [P('Patients', 'TableCellBold'), P('820', 'TableCell'), P('A moderate total sample, but positive outcome counts still limit model complexity.', 'TableCell')],
    [P('Columns', 'TableCellBold'), P('95, not 94', 'TableCell'), P('Project documents and flow diagrams must use the correct number.', 'TableCell')],
    [P('Patient identifier', 'TableCellBold'), P('820 unique VisitID values', 'TableCell'), P('One row per recorded patient; VisitID is for tracking only and must never be a predictor.', 'TableCell')],
    [P('Duplicate rows', 'TableCellBold'), P('None found', 'TableCell'), P('No exact duplicate patient rows were detected.', 'TableCell')],
    [P('Study timing', 'TableCellBold'), P('Cross-sectional', 'TableCell'), P('Features and outcomes were measured at the same visit, so the study cannot establish future risk or cause.', 'TableCell')],
]
t = Table(info, colWidths=[3.0*cm, 4.2*cm, 9.3*cm], repeatRows=1)
t.setStyle(TableStyle([
    ('BACKGROUND',(0,0),(-1,0),NAVY), ('VALIGN',(0,0),(-1,-1),'TOP'),
    ('GRID',(0,0),(-1,-1),0.35,MID_GREY), ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,OFF_WHITE]),
    ('LEFTPADDING',(0,0),(-1,-1),5), ('RIGHTPADDING',(0,0),(-1,-1),5),
    ('TOPPADDING',(0,0),(-1,-1),5), ('BOTTOMPADDING',(0,0),(-1,-1),5),
]))
story += [t]

# Outcome prevalence
story += [P('2. Outcome decisions and class balance', 'H1x')]
outcomes = [
    [P('Outcome', 'TableHeader'), P('Positive / evaluable', 'TableHeader'), P('Decision', 'TableHeader')],
    [P('NegRFandACCP', 'TableCellBold'), P('164 / 820 (20.0%)', 'TableCell'), P('Keep as a separate outcome.', 'TableCell')],
    [P('NoHandJointInvolvement', 'TableCellBold'), P('191 / 820 (23.3%)', 'TableCell'), P('Keep as a separate outcome.', 'TableCell')],
    [P('AsymmetricArthritis', 'TableCellBold'), P('190 / 820 (23.2%)', 'TableCell'), P('Keep as a separate outcome.', 'TableCell')],
    [P('OnlyLargeJoints', 'TableCellBold'), P('31 / 819 (3.8%)', 'TableCell'), P('Remove from this project.', 'TableCell')],
]
t = Table(outcomes, colWidths=[6.0*cm, 4.0*cm, 6.5*cm], repeatRows=1)
t.setStyle(TableStyle([
    ('BACKGROUND',(0,0),(-1,0),NAVY), ('VALIGN',(0,0),(-1,-1),'TOP'),
    ('GRID',(0,0),(-1,-1),0.35,MID_GREY), ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,OFF_WHITE]),
    ('BACKGROUND',(0,4),(-1,4),LIGHT_RED),
    ('LEFTPADDING',(0,0),(-1,-1),5), ('RIGHTPADDING',(0,0),(-1,-1),5),
    ('TOPPADDING',(0,0),(-1,-1),5), ('BOTTOMPADDING',(0,0),(-1,-1),5),
]))
story += [t]
story += section_issue('2.1 Why only-large-joint disease was removed',
    'Only 31 patients were positive. This gives too little information for a high-dimensional model and makes validation and feature explanations unstable.',
    'Remove `OnlyLargeJoints` from all further outcomes and do not include it as a predictor of the remaining outcomes.',
    'The decision reduces the risk of publishing unstable or misleading results. It also simplifies the multiple-outcome problem while preserving the three outcomes with about 164–191 positive patients each.',
    'Update all configuration files, tables, figures, and derived dataset manifests to contain only the three retained outcomes.')

story += section_issue('2.2 Why the remaining outcomes stay separate',
    'The three atypical presentations can occur alone or together, and they represent different clinical ideas.',
    'Fit one model per outcome rather than creating one combined “atypical RA” target.',
    'A combined target would hide which phenotype a feature is related to. Separate models are easier to interpret clinically and match the research question.',
    'Use the same scientific workflow for each outcome, but allow target-specific leakage exclusions.')

# Cross-sectional
story += section_issue('3. Cross-sectional design and wording',
    'Predictors and outcomes were recorded at the same visit. A variable may be a feature of the current phenotype rather than something that came before it.',
    'Use a leakage-controlled contemporaneous classification estimand.',
    'This honestly describes what the data can answer: whether current information helps classify the phenotype at the observed visit. It avoids unsupported claims about cause or future prognosis.',
    'Use manuscript terms such as “associated with,” “classified,” and “predicted at the observed visit.” Avoid “caused,” “future risk,” and “prognostic” unless another longitudinal dataset is used.')

# Data corrections
story += [PageBreak(), P('4. Data-quality corrections and unusual values', 'H1x'),
          P('The untouched source CSV must always be preserved. Every correction below should occur in a reproducible cleaning script and be recorded in a correction table containing VisitID, variable, old value, new value, reason, and source of confirmation.', 'Calloutx')]

corrections = [
    [P('VisitID', 'TableHeader'), P('Variable', 'TableHeader'), P('Recorded value', 'TableHeader'), P('Agreed analysis value', 'TableHeader'), P('Reason', 'TableHeader')],
    [P('2127', 'TableCell'), P('Age', 'TableCell'), P('6', 'TableCell'), P('60', 'TableCellBold'), P('Investigator supplied corrected value; source documentation should be retained.', 'TableCell')],
    [P('24594', 'TableCell'), P('Right / left grip', 'TableCell'), P('152 / 81', 'TableCell'), P('Missing / missing', 'TableCellBold'), P('Extreme and inconsistent with the main observed scale.', 'TableCell')],
    [P('10550', 'TableCell'), P('Right / left grip', 'TableCell'), P('40 / 40', 'TableCell'), P('Missing / missing', 'TableCellBold'), P('Outside the main observed scale; unit validity not established.', 'TableCell')],
    [P('10709', 'TableCell'), P('TyG', 'TableCell'), P('4.0704', 'TableCell'), P('Missing', 'TableCellBold'), P('Isolated value; next-lowest value is about 7.39.', 'TableCell')],
]
t = Table(corrections, colWidths=[1.5*cm, 3.3*cm, 2.7*cm, 3.2*cm, 5.8*cm], repeatRows=1)
t.setStyle(TableStyle([
    ('BACKGROUND',(0,0),(-1,0),BURGUNDY), ('VALIGN',(0,0),(-1,-1),'TOP'),
    ('GRID',(0,0),(-1,-1),0.35,MID_GREY), ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,OFF_WHITE]),
    ('LEFTPADDING',(0,0),(-1,-1),4), ('RIGHTPADDING',(0,0),(-1,-1),4),
    ('TOPPADDING',(0,0),(-1,-1),5), ('BOTTOMPADDING',(0,0),(-1,-1),5),
]))
story += [t]

story += section_issue('4.1 Why values are set to missing instead of guessed',
    'A suspicious number may be a decimal error, a unit error, or a real unusual value. The correct replacement is unknown without a source record.',
    'For the selected grip and TyG records, replace the value with missing rather than guessing a new number.',
    'Guessing creates invented patient data. Marking an unverified measurement as missing is transparent and allows the planned missing-data procedure to handle it.',
    'Apply the rule before splitting the data because it is a fixed quality-control rule based on the measurement itself, not on outcome information.')

story += section_issue('4.2 First-pregnancy age of 11',
    'One recorded first-pregnancy age is 11. It may be true, but it is sensitive and unusual.',
    'Exclude reproductive variables from the primary all-patient models; verify this value before any female-only secondary analysis.',
    'Reproductive variables have structural non-applicability in men and complex meanings for zero and missing values. Keeping them out of the primary model reduces bias and interpretation problems.',
    'Preserve the value in the source data and place it on the verification list for any future female-only analysis.')

# Leakage and labels
story += [P('5. Outcome definition and data leakage', 'H1x')]
story += section_issue('5.1 Seronegative outcome components',
    '`NegRFandACCP` is closely determined by anti-CCP and rheumatoid factor. Giving those measurements to the model would nearly give it the answer.',
    'Exclude `AntiCCPPosNeg` and `SerumRheumatoidFactorPositive` from the primary seronegative predictor set.',
    'This prevents a circular model. The goal is to identify other clinical and paraclinical features associated with seronegative presentation, not to reconstruct the definition from its components.',
    'The two serology fields may appear only in a clearly labeled reconstruction sensitivity analysis, not in the scientific primary model.')

story += section_issue('5.2 Eleven seronegative-label disagreements',
    'Among 625 patients with complete anti-CCP and RF fields, 11 recorded seronegative labels disagree with the simple “both negative” rule. Anti-CCP is missing in another 195 patients even though the outcome is complete.',
    'Use the recorded complete outcome in the primary analysis. Run a sensitivity analysis excluding the 11 discordant complete-serology records.',
    'Rebuilding the outcome would discard 195 patients and could introduce selection bias. The sensitivity analysis checks whether the 11 questionable records materially change the result.',
    'Report the disagreement count and the sensitivity result. If source adjudication later becomes available, update only documented errors.')

story += section_issue('5.3 No-hand outcome and hand markers',
    'A simple rule using DIP, hand PIP, MCP, and wrist fields agrees with the recorded outcome in only 81.6% of patients. The rule may omit joints or use a different examination time.',
    'Use all recorded `NoHandJointInvolvement` labels. Exclude the four direct hand markers from primary predictors.',
    'The available rule is not proven to be the formal definition, so replacing or excluding 151 labels would be unsafe. Removing the direct hand markers still protects the primary model from obvious leakage.',
    'Use the four hand markers only in an expanded contemporaneous-reconstruction sensitivity analysis.')

story += section_issue('5.4 Asymmetry and joint-pattern variables',
    '`JointInvolvementPattern` contains an explicitly asymmetric category. `PolyarticularType` and joint pattern also contain very rare categories.',
    'Move both `JointInvolvementPattern` and `PolyarticularType` to sensitivity analyses only.',
    'This prevents direct phenotype reconstruction, avoids unstable estimates from categories with only 7–9 patients, and avoids clinically false category merging.',
    'Exclude these fields from every journal-primary model, not only the asymmetry model, for a consistent and easily audited rule.')

# Missingness
story += [PageBreak(), P('6. Missing data', 'H1x'),
          P('Missing values are not evenly distributed. For example, anti-CCP and TyG availability differs between outcome groups. This means that “not recorded” may contain information about clinical workflow, recruitment period, or which tests a clinician ordered.', 'Warningx')]

missing_table = [
    [P('Variable', 'TableHeader'), P('Missing', 'TableHeader'), P('Primary status', 'TableHeader')],
    [P('Pregnancy age at first pregnancy', 'TableCell'), P('65.0%', 'TableCell'), P('Reproductive; excluded from primary all-patient models.', 'TableCell')],
    [P('TyG', 'TableCell'), P('35.0%', 'TableCell'), P('Retained by explicit investigator decision.', 'TableCell')],
    [P('BloodRH', 'TableCell'), P('34.0%', 'TableCell'), P('Sensitivity only.', 'TableCell')],
    [P('BloodGroup', 'TableCell'), P('32.9%', 'TableCell'), P('Sensitivity only.', 'TableCell')],
    [P('DLPObj', 'TableCell'), P('32.9%', 'TableCell'), P('Sensitivity only.', 'TableCell')],
    [P('AntiCCPPosNeg', 'TableCell'), P('23.8%', 'TableCell'), P('Excluded from seronegative primary model by leakage rule; target-specific status elsewhere.', 'TableCell')],
    [P('Platelet fields', 'TableCell'), P('22.4%', 'TableCell'), P('Eligible after rarity and target-specific checks.', 'TableCell')],
    [P('Leukopenia / anemia', 'TableCell'), P('18.5% / 18.2%', 'TableCell'), P('Eligible after rarity and target-specific checks.', 'TableCell')],
]
t = Table(missing_table, colWidths=[5.4*cm, 2.6*cm, 8.5*cm], repeatRows=1)
t.setStyle(TableStyle([
    ('BACKGROUND',(0,0),(-1,0),TEAL), ('VALIGN',(0,0),(-1,-1),'TOP'),
    ('GRID',(0,0),(-1,-1),0.35,MID_GREY), ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,OFF_WHITE]),
    ('LEFTPADDING',(0,0),(-1,-1),5), ('RIGHTPADDING',(0,0),(-1,-1),5),
    ('TOPPADDING',(0,0),(-1,-1),5), ('BOTTOMPADDING',(0,0),(-1,-1),5),
]))
story += [t]

story += section_issue('6.1 Primary missing-data method',
    'Treating a blank binary field as zero would incorrectly turn “unknown” into “no.” Deleting every patient with any missing value would waste many patients and could cause bias.',
    'Use training-fold median imputation for continuous/count variables; training-fold most-frequent imputation plus a missingness indicator for binary variables; and an explicit `Unknown` level for nominal categories.',
    'This approach is transparent, reproducible, and compatible with cross-validation. The missingness indicator allows the model to recognize that a value was unavailable without pretending the imputed number was observed.',
    'Fit the imputer and encoder separately inside every training fold. Never impute the full dataset before cross-validation.')

story += section_issue('6.2 More advanced missing-data sensitivity analysis',
    'A simple imputation method may not capture relationships among variables.',
    'Use multivariable or iterative imputation as a prespecified sensitivity analysis, also inside resampling.',
    'If conclusions remain similar under a more flexible missing-data method, confidence in robustness increases. Keeping it secondary avoids making the entire workflow difficult to audit and explain.',
    'Compare performance, calibration, and leading explanations with the primary imputation pipeline.')

story += section_issue('6.3 High-missingness rule',
    'Blood group, Rh, DLP, and TyG are each missing in about one third of patients. Results can depend heavily on assumptions about these missing values.',
    'Move `BloodGroup`, `BloodRH`, and `DLPObj` to sensitivity analysis. Retain TyG as a prespecified exception, with a missingness indicator and a sensitivity analysis that removes TyG.',
    'This reduces dependence on weakly supported imputations while respecting the investigator’s decision that TyG has sufficient biological importance to test in the primary model.',
    'Document the exception explicitly so the rule cannot be mistaken for outcome-driven variable selection.')

# Rare variables
story += [P('7. Rare and near-constant variables', 'H1x')]
story += section_issue('7.1 Constant fields',
    '`NowPregnant`, `Cancer`, and `NotCurrentlyClassifiableasRA2010` have no observed variation; every recorded value is zero.',
    'Exclude them from every model.',
    'A variable that never changes cannot distinguish outcomes. Its missing values must not be treated as positive cases.',
    'Retain these columns only in the source/audit dataset, not the model matrix.')

story += section_issue('7.2 Extremely rare binary predictors',
    '`InitialSiteExtraArticular` has one positive patient and `CNSCVA` has four.',
    'Exclude any binary predictor with fewer than 10 observations in either category from primary models.',
    'A model cannot estimate a stable pattern from one or four exposed patients. Such fields can produce extreme coefficients and misleading importance scores.',
    'Apply the rule before examining associations with outcomes. Keep excluded fields in a sensitivity manifest for transparency.')

story += section_issue('7.3 Rare categorical levels',
    'Some categories contain fewer than 10 patients. Combining categories only to increase numbers can create clinically meaningless groups.',
    'Combine rare levels only when a clinician can defend the grouping. Otherwise move the whole variable to sensitivity analysis.',
    'Clinical meaning is more important than a mechanical frequency threshold. This rule prevents false categories while protecting numerical stability.',
    'Record every category mapping in the preprocessing configuration before model fitting.')

# Redundancy
story += [PageBreak(), P('8. Overlapping and correlated predictors', 'H1x')]
correlations = [
    [P('Pair', 'TableHeader'), P('Correlation', 'TableHeader'), P('Agreed handling', 'TableHeader')],
    [P('Opium / IllicitDrug', 'TableCell'), P('0.935', 'TableCell'), P('Keep Opium in primary; use IllicitDrug as a replacement sensitivity analysis.', 'TableCell')],
    [P('Right / left grip', 'TableCell'), P('0.905', 'TableCell'), P('Use mean valid bilateral grip in primary.', 'TableCell')],
    [P('Sacroiliac / spine involvement', 'TableCell'), P('0.776', 'TableCell'), P('Keep both if target-eligible; use regularization and grouped interpretation.', 'TableCell')],
    [P('Tender / swollen joint count', 'TableCell'), P('0.622', 'TableCell'), P('Keep both if target-eligible; use regularization.', 'TableCell')],
    [P('Hand PIP / MCP involvement', 'TableCell'), P('0.553', 'TableCell'), P('Target-specific leakage rules take priority.', 'TableCell')],
]
t = Table(correlations, colWidths=[5.2*cm, 2.5*cm, 8.8*cm], repeatRows=1)
t.setStyle(TableStyle([
    ('BACKGROUND',(0,0),(-1,0),NAVY), ('VALIGN',(0,0),(-1,-1),'TOP'),
    ('GRID',(0,0),(-1,-1),0.35,MID_GREY), ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,OFF_WHITE]),
    ('LEFTPADDING',(0,0),(-1,-1),5), ('RIGHTPADDING',(0,0),(-1,-1),5),
    ('TOPPADDING',(0,0),(-1,-1),5), ('BOTTOMPADDING',(0,0),(-1,-1),5),
]))
story += [t]

story += section_issue('8.1 Opium and illicit-drug fields',
    'Every opium-positive patient is also coded illicit-drug positive. Only seven patients are illicit-drug positive without opium.',
    'Retain `Opium` and exclude `IllicitDrug` from primary models. Replace Opium with IllicitDrug in a sensitivity analysis.',
    'Including both would double-count almost the same information and make coefficient and SHAP attribution unstable. Opium is the more specific exposure chosen by the investigator.',
    'Never include both in the same primary model.')

story += section_issue('8.2 Bilateral grip summary',
    'Right and left grip contain almost the same information and can split importance arbitrarily.',
    'Create `MeanGripStrength` from valid hands after the agreed anomaly corrections.',
    'A bilateral mean reduces duplicate information and measurement noise while preserving the general functional signal.',
    'If both hands are valid, average them. If one is valid, use it. If both are missing, leave the summary missing and use the standard missingness process. Separate hands are sensitivity-only.')

story += section_issue('8.3 Other clinically distinct correlations',
    'Some related variables are correlated but do not mean exactly the same thing, such as tender versus swollen counts.',
    'Retain clinically distinct eligible variables, control them with regularization, and interpret importance by clinical domain as well as individual column.',
    'Deleting one variable only because of correlation can remove useful clinical information. Regularization reduces overfitting, while grouped interpretation acknowledges that correlated variables share predictive credit.',
    'Report correlation groups and do not claim that small differences in SHAP rank identify a uniquely important member of a correlated pair.')

# Predictor scope
story += [P('9. Predictor scope and complexity', 'H1x')]
story += section_issue('9.1 All eligible predictors without univariable screening',
    'Many candidate variables remain after quality and leakage rules. Selecting them because they look associated with an outcome in the full dataset would bias later validation.',
    'Retain all predictors that survive the prespecified outcome-independent rules and use regularization to control complexity.',
    'This avoids choosing variables based on chance patterns in the same data used for evaluation. It is more reproducible than p-value screening or stepwise selection.',
    'Any supervised selection or tuning must happen inside inner cross-validation. Do not use the EDA association ranking as a feature-selection list.')

story += section_issue('9.2 Concurrent clinical variables',
    'Joint counts, symptoms, disease activity, and other current findings may be close in time to the current phenotype.',
    'Allow current variables that do not directly define the target, because the agreed goal is contemporaneous classification.',
    'This matches the research question while preserving the leakage boundary. The cost is that results cannot be interpreted as future risk or cause.',
    'Clearly label direct target components, outcome-proximal sensitivity variables, and ordinary eligible predictors in each target manifest.')

# Imbalance and validation
story += [P('10. Class balance and model validation', 'H1x')]
story += section_issue('10.1 Moderate class imbalance',
    'The three retained outcomes are positive in about 20%–23% of patients. Accuracy alone can still hide poor detection of positive cases.',
    'Use unweighted training loss with stratified validation. Do not use SMOTE or undersampling in the primary analysis. Test class weighting only as a sensitivity analysis.',
    'Natural prevalence supports honest probability calibration. Synthetic or discarded observations are unnecessary for this moderate imbalance and can distort probabilities.',
    'Report AUROC, precision-recall AUC, sensitivity, specificity, predictive values, Brier score, and calibration—not accuracy alone.')

story += section_issue('10.2 Repeated nested cross-validation',
    'A single train/test split wastes data and may give a lucky or unlucky result. Tuning a model and evaluating it on the same folds is optimistic.',
    'Use five outer folds repeated 10 times, with five inner folds for tuning.',
    'The inner loop chooses settings; the untouched outer fold estimates performance. Repetition reduces dependence on one random split and gives every patient out-of-fold predictions.',
    'Average each patient’s 10 out-of-fold probabilities and use subject-level bootstrap confidence intervals. Keep split seeds and use identical splits for competing pipelines.')

# Explainability and pending decisions
story += [PageBreak(), P('11. Explainability and interpretation', 'H1x')]
story += section_issue('11.1 SHAP and feature importance',
    'Feature-importance plots can look precise even when importance changes across folds or is shared among correlated variables.',
    'Scientific recommendation: calculate SHAP only from out-of-fold predictions, group one-hot categories back to the original variable, and report stability across folds.',
    'An explanation for a patient should come from a model that did not train on that patient. Stability analysis prevents one attractive plot from being mistaken for a reliable result.',
    'Show global magnitude, direction, fold-to-fold rank stability, and grouped clinical-domain importance. State clearly that SHAP is not causal.', status='RECOMMENDED')

story += [P('12. Decisions intentionally left for later', 'H1x'),
          P('The investigator chose to postpone final model-family selection. This is appropriate: the data rules and scientific estimand should be settled before choosing an algorithm.', 'Calloutx')]
pending = [
    [P('Pending item', 'TableHeader'), P('Scientific options to compare later', 'TableHeader')],
    [P('Primary model family', 'TableCellBold'), P('Ridge logistic regression; elastic-net logistic regression; a constrained nonlinear comparator; or a prespecified hierarchy.', 'TableCell')],
    [P('Final probability threshold', 'TableCellBold'), P('Choose from a clinical use case, not from accuracy alone. Threshold selection must occur inside training data or be prespecified.', 'TableCell')],
    [P('Final SHAP protocol', 'TableCellBold'), P('Out-of-fold linear SHAP for logistic models or a validated equivalent for another selected model, with stability reporting.', 'TableCell')],
    [P('Multiplicity language', 'TableCellBold'), P('Define which comparisons are descriptive and whether formal inferential tests require false-discovery control.', 'TableCell')],
]
t = Table(pending, colWidths=[4.5*cm, 12.0*cm], repeatRows=1)
t.setStyle(TableStyle([
    ('BACKGROUND',(0,0),(-1,0),GOLD), ('VALIGN',(0,0),(-1,-1),'TOP'),
    ('GRID',(0,0),(-1,-1),0.35,MID_GREY), ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,OFF_WHITE]),
    ('LEFTPADDING',(0,0),(-1,-1),5), ('RIGHTPADDING',(0,0),(-1,-1),5),
    ('TOPPADDING',(0,0),(-1,-1),5), ('BOTTOMPADDING',(0,0),(-1,-1),5),
]))
story += [t]

# Decision register
story += [P('13. Confirmed decision register', 'H1x'),
          P('This table is the concise audit trail of choices made during the issue-by-issue discussion. The final model choice is not included because it has not been made.')]
decisions = [
    ('D01', 'Remove OnlyLargeJoints from the project.'),
    ('D02', 'Apply the investigator-supplied age correction recorded in the authorized correction specification; retain source evidence.'),
    ('D03', 'Set the documented unverified bilateral grip values to missing.'),
    ('D04', 'Set the documented isolated unverified TyG value to missing; keep TyG primary-eligible with imputation and indicator; test removal in sensitivity analysis.'),
    ('D05', 'Use recorded NegRFandACCP labels; sensitivity analysis excludes complete-serology discordant records.'),
    ('D06', 'Use recorded NoHandJointInvolvement labels; exclude direct hand markers from primary predictors.'),
    ('D07', 'Primary missing strategy: fold-contained simple imputation; iterative imputation sensitivity.'),
    ('D08', 'BloodGroup, BloodRH, and DLPObj are sensitivity-only; TyG is the documented >30% missingness exception.'),
    ('D09', 'Exclude primary binary predictors with fewer than 10 observations in either category; group rare categorical levels only when clinically defensible.'),
    ('D10', 'Keep Opium; remove IllicitDrug from primary; swap in sensitivity analysis.'),
    ('D11', 'Use mean valid bilateral grip in primary models.'),
    ('D12', 'Retain other correlated but distinct features with regularization and grouped interpretation.'),
    ('D13', 'Primary aim is leakage-controlled contemporaneous classification.'),
    ('D14', 'JointInvolvementPattern and PolyarticularType are sensitivity-only.'),
    ('D15', 'Use all eligible prespecified predictors with regularization; no univariable screening.'),
    ('D16', 'Use unweighted loss and stratified validation; class weighting is sensitivity-only.'),
    ('D17', 'Use repeated nested 5-fold CV: 10 outer repetitions and 5 inner folds.'),
]
rows = [[P('ID','TableHeader'), P('Confirmed decision','TableHeader')]] + [[P(i,'TableCellBold'), P(x,'TableCell')] for i,x in decisions]
t = LongTable(rows, colWidths=[1.5*cm, 15.0*cm], repeatRows=1)
t.setStyle(TableStyle([
    ('BACKGROUND',(0,0),(-1,0),GREEN), ('VALIGN',(0,0),(-1,-1),'TOP'),
    ('GRID',(0,0),(-1,-1),0.35,MID_GREY), ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,OFF_WHITE]),
    ('LEFTPADDING',(0,0),(-1,-1),5), ('RIGHTPADDING',(0,0),(-1,-1),5),
    ('TOPPADDING',(0,0),(-1,-1),4), ('BOTTOMPADDING',(0,0),(-1,-1),4),
]))
story += [t]

# Implementation checklist
story += [PageBreak(), P('14. Required implementation checklist', 'H1x'),
          P('The following items should be completed before any final model is trained or interpreted.')]
checks = [
    'Preserve the original CSV unchanged and calculate a file checksum.',
    'Create a scripted correction table for age, grip strength, and TyG.',
    'Update the analysis configuration to the three retained outcomes.',
    'Regenerate target-specific primary and sensitivity datasets and manifests.',
    'Remove VisitID from every model matrix while retaining it for tracing predictions.',
    'Apply constant, rarity, high-missingness, reproductive, pattern-variable, and target-leakage rules.',
    'Create MeanGripStrength only after the agreed value corrections.',
    'Fit every imputer, encoder, scaler, selector, and model inside the correct training fold.',
    'Create and save repeated nested cross-validation split indices.',
    'Use identical outer splits for fair model comparisons.',
    'Store out-of-fold probabilities for every patient and repetition.',
    'Report confidence intervals and calibration, not only discrimination.',
    'Keep primary and sensitivity findings clearly separated.',
    'Record the later model-family decision as a new version of this decision log.',
]
story += bullets([f'☐ {x}' for x in checks])

story += [P('15. Final scientific position', 'H1x'),
          P('The dataset is usable for an internally validated, cross-sectional clinical classification study after the agreed cleaning and eligibility rules are applied. Its main risks are not solved by choosing a more complex algorithm. They are solved by clear outcome definitions, prevention of leakage, honest handling of missing and rare data, repeated validation, and cautious interpretation.', 'Decisionx'),
          P('The strongest manuscript will emphasize transparent methods, calibration, uncertainty, and sensitivity analyses. A high apparent score is not valuable if it comes from direct outcome components, unverified values, or evaluation on patients used for training.'),
          Spacer(1, 0.3*cm), HRFlowable(width='100%', thickness=1, color=MID_GREY),
          P('<b>Document control:</b> This report records decisions made through Issue 16 of the discussion. Model-family choice was explicitly deferred and must be added in a later version. Any change to a confirmed decision should be dated, justified, and versioned.', 'Smallx')]

doc.build(story, canvasmaker=NumberedCanvas)
print(OUT)
