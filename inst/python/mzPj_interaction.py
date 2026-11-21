"""OLS moderation with shared two-panel rendering; numerical work stays in Python."""

def _pj_interaction_fit(dataset, x, y, moderator, *, moderator_type='continuous',
                        covariates=None, unit=None, reference=None,
                        moderator_values=None, covariance='HC3', level=.95,
                        points=81, show_points=True):
    import math
    import numpy as numpy
    try:
        from scipy import stats as distributions
    except ImportError as error:
        raise ImportError('Interaction analysis requires NumPy and SciPy in the selected Python.') from error
    function = 'mzpjShowInteraction'
    if moderator_type not in ('continuous', 'binary'):
        raise ValueError('moderator_type must be continuous or binary.')
    if not isinstance(covariance, str) or covariance.upper() not in ('OLS', 'HC3'):
        raise ValueError('covariance must be OLS or HC3.')
    covariance = covariance.upper()
    if isinstance(level, bool) or not isinstance(level, (int, float)) or not 0 < level < 1:
        raise ValueError('level must be above 0 and below 1.')
    if isinstance(points, bool) or not isinstance(points, int) or not 21 <= points <= 201:
        raise ValueError('points must be an integer between 21 and 201.')
    if not isinstance(show_points, bool):
        raise TypeError('show_points must be True or False.')
    if any(not isinstance(v, str) or not v for v in (x, y, moderator)) or len({x,y,moderator}) != 3:
        raise ValueError('x, y and moderator must be three distinct column names.')
    if covariates is None:
        covariates = []
    if not isinstance(covariates, (list, tuple)) or any(not isinstance(c, str) or not c for c in covariates):
        raise TypeError('covariates must be a list or tuple of numeric column names.')
    covariates = list(covariates)
    if len(covariates) > 16 or len(set(covariates)) != len(covariates) or set(covariates) & {x,y,moderator}:
        raise ValueError('Use at most 16 distinct covariates, excluding x, y and moderator.')
    if moderator_type == 'continuous' and reference is not None:
        raise ValueError('reference is only used with a binary moderator.')
    if moderator_type == 'binary' and moderator_values is not None:
        raise ValueError('Binary moderators use both observed levels; choose reference instead of moderator_values.')
    n_input = _pj_plot_columns(dataset, [x,y,moderator,unit]+covariates, function)
    rows = []
    for i in range(n_input):
        xv = _pj_plot_number(dataset[x][i], x, i, function)
        yv = _pj_plot_number(dataset[y][i], y, i, function)
        mv = (_pj_plot_number(dataset[moderator][i], moderator, i, function)
              if moderator_type == 'continuous' else _pj_plot_category(dataset[moderator][i]))
        cv = [_pj_plot_number(dataset[c][i], c, i, function) for c in covariates]
        identity = _pj_plot_category(dataset[unit][i]) if unit else ('int', str(i+1))
        if xv is None or yv is None or mv is None or identity is None or any(v is None for v in cv):
            continue
        rows.append((xv,yv,mv,cv,identity,i+1))
    p = 4 + len(covariates)
    n = len(rows)
    if n <= p:
        raise ValueError(f'{function}(): need more than {p} complete independent observations.')
    if len({r[4] for r in rows}) != n:
        raise ValueError('Repeated unit identifiers detected. This OLS helper requires independent rows; use a mixed/repeated-measures model for dependent observations.')
    if show_points and n > 5000:
        raise ValueError('More than 5000 complete observations: set show_points=False to fit without drawing every point.')
    xv = numpy.array([r[0] for r in rows], dtype=float)
    yv = numpy.array([r[1] for r in rows], dtype=float)
    if len(set(xv)) < 3:
        raise ValueError('The continuous predictor x needs at least three distinct values.')
    groups = None
    if moderator_type == 'binary':
        mapping = _pj_plot_categories([r[2] for r in rows])
        if len(mapping) != 2:
            raise ValueError('A binary moderator must have exactly two complete-case levels.')
        keys = list(mapping)
        if reference is not None:
            key = _pj_plot_category(reference)
            if key not in mapping:
                raise ValueError('reference must identify an observed moderator level.')
            keys = [key] + [k for k in keys if k != key]
        groups = [mapping[k] for k in keys]
        mv = numpy.array([float(keys.index(r[2])) for r in rows])
        m0, ms = 0., 1.
        probe_values, probe_labels = [0.,1.], groups
    else:
        mv = numpy.array([r[2] for r in rows], dtype=float)
        if len(set(mv)) < 3:
            raise ValueError('A continuous moderator needs at least three distinct values; use moderator_type="binary" for two groups.')
        m0, ms = float(numpy.mean(mv)), float(numpy.std(mv))
        if moderator_values is None:
            probe_values = list(dict.fromkeys(float(v) for v in numpy.quantile(mv,[.16,.5,.84])))
            if len(probe_values) < 2:
                probe_values = [float(min(mv)),float(max(mv))]
        else:
            if not isinstance(moderator_values, (list,tuple)) or not 1 <= len(moderator_values) <= 5:
                raise ValueError('moderator_values must contain one to five observed-range numeric values.')
            probe_values = [_pj_plot_number(v,'moderator_values',i,function) for i,v in enumerate(moderator_values)]
            if any(v is None for v in probe_values) or len(set(probe_values)) != len(probe_values):
                raise ValueError('moderator_values must be finite and distinct.')
            if min(probe_values) < min(mv) or max(probe_values) > max(mv):
                raise ValueError('moderator_values must stay within the complete-case moderator range.')
        probe_labels = [f'{moderator} = {v:.5g}' for v in probe_values]
    with numpy.errstate(over='raise', invalid='raise', divide='raise'):
        x0, xs = float(numpy.mean(xv)), float(numpy.std(xv))
        if not all(math.isfinite(v) and v > 0 for v in (xs,ms)):
            raise ValueError('Predictor/moderator scale is zero or numerically unsupported.')
        cx, cm = (xv-x0)/xs, (mv-m0)/ms
        columns = [numpy.ones(n),cx,cm,cx*cm]
        centers, scales = [], []
        for j,name in enumerate(covariates):
            values = numpy.array([r[3][j] for r in rows])
            mean,sd = float(numpy.mean(values)),float(numpy.std(values))
            if not math.isfinite(sd) or sd <= 0:
                raise ValueError(f'Covariate {name!r} has no usable variation.')
            centers.append(mean);scales.append(sd);columns.append((values-mean)/sd)
        design = numpy.column_stack(columns)
        singular = numpy.linalg.svd(design, compute_uv=False)
        if singular[-1] <= singular[0]*max(design.shape)*numpy.finfo(float).eps or singular[0]/singular[-1] > 1e10:
            raise ValueError('The interaction design is rank-deficient or too ill-conditioned; remove redundant predictors/covariates.')
        q,r = numpy.linalg.qr(design, mode='reduced')
        inverse_r = numpy.linalg.solve(r,numpy.eye(p))
        beta = numpy.linalg.solve(r,q.T@yv)
        residual = yv-design@beta
        sse = float(residual@residual)
        total = float((yv-numpy.mean(yv))@(yv-numpy.mean(yv)))
        if not math.isfinite(sse) or sse <= 0 or not math.isfinite(total) or total <= 0:
            raise ValueError('A varying response and positive finite residual variance are required.')
        df = n-p
        if covariance == 'HC3':
            leverage = numpy.sum(q*q,axis=1)
            if numpy.max(leverage) >= 1-1e-10:
                raise ValueError('HC3 is unstable because an observation has leverage near one.')
            factor = (q@inverse_r.T)*(residual/(1-leverage))[:,None]
            critical = float(distributions.norm.ppf((1+level)/2))
            tail = distributions.norm.sf
            inference = 'asymptotic Normal (HC3 Wald)'
        else:
            factor = inverse_r.T*math.sqrt(sse/df)
            critical = float(distributions.t.ppf((1+level)/2,df))
            tail = lambda statistic: distributions.t.sf(statistic,df)
            inference = f'Student t ({df} residual df)'
        cov = factor.T@factor
        if not numpy.all(numpy.isfinite(beta)) or not numpy.all(numpy.isfinite(cov)):
            raise ValueError('The fitted coefficients/covariance are numerically unsupported.')
    def confidence(estimate, contrast):
        estimate = float(estimate)
        se = float(numpy.linalg.norm(factor@contrast))
        lo,hi = estimate-critical*se, estimate+critical*se
        if not all(math.isfinite(v) for v in (estimate,se,lo,hi)):
            raise ValueError('A fitted interval is outside the supported numeric range.')
        return dict(estimate=estimate,se=se,lower=lo,upper=hi)
    def interval(estimate, contrast):
        result = confidence(estimate,contrast)
        se,estimate = result['se'],result['estimate']
        if se == 0:
            pvalue = 1. if estimate == 0 else 0.
            statistic = 0. if estimate == 0 else None
        else:
            statistic = estimate/se
            pvalue = float(2*tail(abs(statistic)))
            if not math.isfinite(statistic):
                statistic = None
        if not math.isfinite(pvalue):
            raise ValueError('A fitted p-value is outside the supported numeric range.')
        return dict(**result,statistic=statistic,p=pvalue)
    def effect(value):
        c = numpy.zeros(p);c[1]=1/xs;c[3]=(value-m0)/(ms*xs)
        return dict(moderator=float(value),**interval(c@beta,c))
    raw_scale = numpy.array([1.,1/xs,1/ms,1/(xs*ms)]+[1/s for s in scales])
    raw_beta = beta*raw_scale
    raw_cov = cov*raw_scale[:,None]*raw_scale[None,:]
    if not numpy.all(numpy.isfinite(raw_cov)) or not numpy.all(numpy.isfinite(raw_beta)):
        raise ValueError('Raw-unit coefficients are outside the supported numeric range.')
    terms = [('Intercept (X at mean; reference '+groups[0]+')' if groups else 'Intercept (at centered predictors)'),x,moderator,f'{x} × {moderator}']+covariates
    coefficients = []
    for j,term in enumerate(terms):
        contrast = numpy.zeros(p);contrast[j]=raw_scale[j]
        coefficients.append(dict(term=term,**interval(raw_beta[j],contrast)))
    slopes = [dict(label=label,**effect(value)) for value,label in zip(probe_values,probe_labels)]
    moderator_grid = (probe_values if groups else numpy.linspace(float(min(mv)),float(max(mv)),points))
    effects = [effect(float(value)) for value in moderator_grid]
    x_grid = numpy.linspace(float(min(xv)),float(max(xv)),points)
    curves = []
    for value,label in zip(probe_values,probe_labels):
        curve = []
        for v in x_grid:
            c = numpy.zeros(p);c[:4]=[1.,(v-x0)/xs,(value-m0)/ms,(v-x0)/xs*(value-m0)/ms]
            curve.append(dict(x=float(v),**confidence(c@beta,c)))
        curves.append(dict(label=label,moderator=float(value),points=curve))
    roots,regions = [],[]
    if not groups:
        a = float(beta[3]**2-critical**2*cov[3,3])
        b = float(2*(beta[1]*beta[3]-critical**2*cov[1,3]))
        c = float(beta[1]**2-critical**2*cov[1,1])
        scale = max(abs(a),abs(b),abs(c),numpy.finfo(float).tiny)
        a,b,c = a/scale,b/scale,c/scale
        tolerance = 1e-12
        candidates = []
        if abs(a) <= tolerance:
            if abs(b) > tolerance:
                candidates = [-c/b]
        else:
            discriminant = b*b-4*a*c
            if discriminant >= -tolerance:
                discriminant = max(0.,discriminant)
                qvalue = -.5*(b+math.copysign(math.sqrt(discriminant),b))
                candidates = [qvalue/a,c/qvalue] if abs(qvalue)>numpy.finfo(float).tiny else [-b/(2*a)]
        lo,hi = float(min(mv)),float(max(mv))
        for value in sorted(set(float(m0+ms*v) for v in candidates if math.isfinite(v))):
            if lo < value < hi and not any(abs(value-old)<1e-9*(hi-lo) for old in roots):
                roots.append(value)
        bounds = [lo]+roots+[hi]
        for low,high in zip(bounds,bounds[1:]):
            result = effect(low+(high-low)/2)
            direction = 'positive' if result['lower']>0 else 'negative' if result['upper']<0 else 'includes zero'
            regions.append(dict(lower=low,upper=high,direction=direction))
    observed = [dict(x=float(r[0]),y=float(r[1]),moderator=float(mv[i]),
                     label=str(dataset[unit][r[5]-1]) if unit else f'Row {r[5]}') for i,r in enumerate(rows)] if show_points else []
    def extent(values,include_zero=False):
        values = list(values)+([0.] if include_zero else [])
        lo,hi = min(values),max(values)
        padding = (hi-lo)*.06 if hi>lo else max(1.,abs(lo)*.06)
        if not math.isfinite(hi+padding) or not math.isfinite(lo-padding):
            raise ValueError('The plot scale is outside the supported numeric range.')
        return [lo-padding,hi+padding]
    r2 = max(0.,min(1.,1-sse/total))
    model = dict(formula=f'{y} ~ {x} * {moderator}'+(' + '+' + '.join(covariates) if covariates else ''),moderator_type=moderator_type,n=n,excluded=n_input-n,n_input=n_input,df=df,parameters=p,r2=r2,
        adjusted_r2=1-(1-r2)*(n-1)/df,covariance=covariance,inference=inference,level=level,
        x_center=x0,moderator_center=m0,moderator_scale=ms,reference=groups[0] if groups else None,
        covariate_means=dict(zip(covariates,centers)),condition_number=float(singular[0]/singular[-1]),
        coefficients=coefficients,covariance_matrix=raw_cov.tolist(),slopes=slopes,
        johnson_neyman_roots=roots,johnson_neyman_regions=regions)
    note=(f'N = {n}; {n_input-n} rows excluded; R2 = {r2:.3f}; {covariance}, {inference}; '
          f'{level*100:g}% pointwise CIs for the fitted mean and conditional slope. '
          'Independent rows assumed; covariates held at complete-case means. '
          'Curves are model predictions, not observed group means. '
          'Intervals are pointwise, not simultaneous. '+
          ('Dotted lines: J-N crossings within the observed moderator range.' if not groups else 'Reference group: '+groups[0]+'.'))
    payload=dict(kind='interaction',title=f'{y}: interaction of {x} and {moderator}',
        xName=x,yName=y,moderatorName=moderator,moderatorType=moderator_type,
        xLabel=x,yLabel=y,groups=probe_labels,grouped=True,curves=curves,effects=effects,
        probes=slopes,observed=observed,roots=roots,regions=regions,binaryLabels=groups,
        xRange=[float(min(xv)),float(max(xv))],moderatorRange=[float(min(mv)),float(max(mv))],
        responseRange=extent([v[k] for curve in curves for v in curve['points'] for k in ('lower','upper')]+[v['y'] for v in observed]),
        effectRange=extent([v[k] for v in effects for k in ('lower','upper')],True),note=note)
    return model,payload


def _pj_show_interaction(dataset, x, y, moderator, *, moderator_type='continuous',
                         covariates=None, unit=None, reference=None, moderator_values=None,
                         covariance='HC3', level=.95, renderer='plotly', show_points=True,
                         tables=True, points=81, name=None, title=None, width=None, height=None, panel_layout='stacked',
                         result_type='html', accordion=True, expanded=True,
                         accordion_type='line', modebar=None, palette=None):
    """Fit Y ~ X * moderator + numeric covariates and draw two linked panels.

    Left: fitted-mean curves with pointwise CIs. Right: conditional X effect
    with pointwise CIs and observed-range Johnson-Neyman crossings. Binary
    moderators show both group slopes instead. HC3 uses asymptotic Normal
    inference; OLS uses residual-df Student t. Independent rows only: supplying
    unit rejects repeated identifiers. NumPy and SciPy are required.

    Return the numerical report; tables=True also displays coefficients and
    probe slopes. renderer is plotly or d3; result_type is html, svg or image.
    """
    if renderer not in ('plotly','d3'):
        raise ValueError('renderer must be plotly or d3.')
    if not isinstance(tables,bool):
        raise TypeError('tables must be True or False.')
    _pj_graphic_mode(result_type)
    _pj_accordion_options(accordion,expanded,accordion_type)
    if panel_layout not in ('stacked','side-by-side'):
        raise ValueError('panel_layout must be stacked or side-by-side.')
    if width is None:
        width = _pj_figure_dimension(FIGWIDTH, 600)
    if height is None:
        height = _pj_figure_dimension(FIGHEIGHT, 500)
    minimum_width = 400 if panel_layout == 'stacked' else 720
    if isinstance(width,bool) or not isinstance(width,int) or not minimum_width <= width <= 2400:
        raise ValueError(f'width must be an integer between {minimum_width} and 2400 pixels for {panel_layout} panels.')
    if isinstance(height,bool) or not isinstance(height,int) or not 440 <= height <= 1600:
        raise ValueError('height must be an integer between 440 and 1600 pixels.')
    if np is None or stats is None:
        raise ImportError('mzpjShowInteraction requires NumPy and SciPy in the selected Python; it does not install packages.')
    model,payload = _pj_interaction_fit(dataset,x,y,moderator,moderator_type=moderator_type,
        covariates=covariates,unit=unit,reference=reference,moderator_values=moderator_values,
        covariance=covariance,level=level,points=points,show_points=show_points)
    style = _pj_plotly_style(palette=palette,modebar=modebar)
    payload['panelLayout'] = panel_layout
    payload['colors'] = style['palette']
    if title is not None:
        payload['title'] = str(title)
    base = _pj_result_name(name,'interaction',_plot_counter)
    used = {item.get('name') for item in results['items']}
    while tables and any(base+suffix in used for suffix in ('_coefficients','_slopes')):
        if name is not None:
            raise ValueError('The interaction table names already exist; choose a different name.')
        base = _pj_result_name(None,'interaction',_plot_counter)
    if renderer == 'plotly':
        _pj_plotly_finish('interaction',payload,style,dict(name=base,title=payload['title'],
            height=height,export_width=width,result_type=result_type,accordion=accordion,
            expanded=expanded,accordion_type=accordion_type))
    else:
        _pj_plot_html(payload,base,width,height,accordion,expanded,style['palette'][0],result_type,accordion_type)
    if tables:
        rows=[{'Term':r['term'],'Estimate':r['estimate'],'SE':r['se'],
               'Lower CI':r['lower'],'Upper CI':r['upper'],'p':r['p']} for r in model['coefficients']]
        centering = (f'X centered at {model["x_center"]:.5g}; '+
            (f'moderator centered at {model["moderator_center"]:.5g}.' if moderator_type=='continuous' else f'reference group: {model["reference"]}.'))
        _pj_add_table(rows,name=base+'_coefficients',title='Interaction model coefficients',
                      notes=payload['note']+' '+centering+' Coefficients are in original units; numeric covariates are centered.',formats={'p':'pvalue','Estimate':'zto','SE':'zto','Lower CI':'zto','Upper CI':'zto'})
        rows=[{'Moderator':r['label'],'Effect of '+x:r['estimate'],'SE':r['se'],
               'Lower CI':r['lower'],'Upper CI':r['upper'],'p':r['p']} for r in model['slopes']]
        _pj_add_table(rows,name=base+'_slopes',title='Conditional effects of '+x,
            notes='Pointwise intervals; no multiplicity adjustment. Predictions hold numeric covariates at their complete-case means.',formats={'p':'pvalue','Effect of '+x:'zto','SE':'zto','Lower CI':'zto','Upper CI':'zto'})
    return model
