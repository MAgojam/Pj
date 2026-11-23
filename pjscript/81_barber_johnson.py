# Hospital Barber–Johnson: four views, shared D3, no optional Python packages.
# SYNTHETIC teaching data; no hospital performance or recommended targets implied.
# Run in Pj or Pjp. The self-contained example needs no selected variables.
# To use your hospital data, set USE_JAMOVI_DATA=True and select ALL named
# columns in Pjp. One row = one ward in one period; ward + period must be unique.
# See docs/mzPj_barber_johnson.md and docs/mzPj_barber_johnson_it.md.
# Data Library examples are not needed. This script does not change data/dataext.

USE_JAMOVI_DATA = False
RESULT_TYPE = 'html'  # 'html', 'svg', 'image'; native outputs have no accordion.
VIEW = 'all'          # 'all', 'toi_alos', 'toi_bto', 'trajectory', 'faceted'
SHOW_TABLE = True

# Exact calendar quarters in 2025; capacity varies in Medicine in Q3/Q4.
ward = ['Medicine', 'Surgery', 'Rehabilitation']
days = [90, 91, 92, 92]
occupation = [[.89,.86,.78,.84],[.76,.81,.72,.79],[.91,.88,.85,.90]]
stay = [[8.5,8.0,7.6,7.8],[5.8,5.2,5.6,5.0],[18,17,16,16.5]]
example = {k:[] for k in ('unit','period','period_order','period_days',
                           'beds','occupied_bed_days','discharges','clinical_area')}
for w,unit in enumerate(ward):
    for q,duration in enumerate(days):
        beds = (32 if q < 2 else 28) if w == 0 else (24 if w == 1 else 20)
        occupied = round(beds * duration * occupation[w][q])
        exits = round(occupied / stay[w][q])
        values = [unit, '2025 Q'+str(q+1), q+1, duration, beds, occupied, exits,
                  'Medical' if w==0 else ('Surgical' if w==1 else 'Rehabilitation')]
        for key,value in zip(example,values):
            example[key].append(value)

dataset = data if USE_JAMOVI_DATA else example
# These references demonstrate user choices, not universal clinical standards.
# Change, add or remove scenarios (up to six). BOR values are proportions, NOT %.
references = [
    {'label':'Comparison band 75–85%', 'bor':[.75,.85], 'toi':[0.5,3]},
    {'label':'Occupancy reference 90%', 'bor':.90},
]
views = ['toi_alos','toi_bto','trajectory','faceted'] if VIEW=='all' else [VIEW]
titles = {'toi_alos':'Hospital bed utilisation: TOI and ALOS',
          'toi_bto':'Hospital bed utilisation: TOI and annualised BTO',
          'trajectory':'Ward trajectories: 2025 Q1 to Q4',
          'faceted':'Ward profiles on common scales'}
for index,view in enumerate(views):
    report = mzpjShowBarberJohnson(
        dataset, view=view, input_mode='raw',
        unit='unit', period='period', period_days='period_days',
        beds='beds', occupied_bed_days='occupied_bed_days', discharges='discharges',
        order='period_order', facet='unit', group='unit', turnover_days=365,
        occupancy_lines=[.5,.7,.8,.85,.9], turnover_lines=[10,20,30,40,60],
        alos_lines=[3,5,7,10,14,21], scenarios=references,
        size_by_beds=True, point_labels=False,
        max_toi=5, max_alos=24, max_bto=90,
        title=titles[view], name='hospital_'+view,
        width=800, height=380, result_type=RESULT_TYPE,
        tables=SHOW_TABLE and index==0)

# Html: hover/focus points for ALL four indicators; click/Enter pins, Escape clears.
# Legend buttons hide/show wards or reference scenarios. Reset restores figure
# size and clears the pinned point; it preserves your reference visibility choices.
# Plot-size slider enlarges the full figure AND its Results area, not the axes.
# Native Svg/Image: use jamovi resize or width/height arguments; no Html zoom.
# Faceted height is PER PANEL: 3 wards x 380 px, with the same axes in every panel.
# BTO per observed period is in the table/point details. BTO curves and TOI–BTO
# coordinates use turnover_days=365 for comparable quarters; this is NOT a forecast.
# ALOS here is occupied bed-days / period discharges, not a discharge-cohort LOS.
