# Calcoli per singolo studio: nessun modello stimato e nessuna mutazione dei dati.
# Convenzioni confrontate con metafor::escalc; vedere docs/mzPj_meta_analysis.md.
def _pj_meta_vectors(arguments):
    vectors = {name: _pj_data_numeric(value, name).tolist()
               for name, value in arguments.items()}
    if len({len(value) for value in vectors.values()}) > 1:
        raise ValueError('All inputs must have the same number of rows; scalar recycling is not supported.')
    return vectors, len(next(iter(vectors.values()))) if vectors else 0


def _pj_meta_number(value, label, *, minimum=None, integer=False, strict=False):
    import math
    from numbers import Real
    if not isinstance(value, Real) or isinstance(value, (bool, np.bool_)) or not math.isfinite(value):
        raise ValueError(f'{label} must be a finite number.')
    if minimum is not None and (value <= minimum if strict else value < minimum):
        raise ValueError(f'{label} must be {">" if strict else ">="} {minimum}.')
    if integer and value != int(value):
        raise ValueError(f'{label} must be an integer count.')
    return float(value)


def _pj_meta_scipy():
    if stats is None:
        raise ImportError('This meta-analysis helper requires SciPy in the selected Python.')


def _pj_sampling_variance(*, sei=None, vi=None, ci_lower=None, ci_upper=None,
                          level=0.95, transform='identity'):
    import math
    _pj_meta_scipy()
    level = _pj_meta_number(level, 'level', minimum=0, strict=True)
    if level >= 1:
        raise ValueError('level must be between 0 and 1, for example 0.95.')
    if transform not in ('identity', 'log', 'fisher'):
        raise ValueError('transform must be identity, log or fisher.')
    modes = int(sei is not None) + int(vi is not None) + int(ci_lower is not None or ci_upper is not None)
    if modes != 1 or (ci_lower is None) != (ci_upper is None):
        raise ValueError('Supply exactly one source: sei, vi, or both ci_lower and ci_upper.')
    if transform != 'identity' and (sei is not None or vi is not None):
        raise ValueError('transform applies only to interval endpoints; sei and vi must already be on the analysis scale.')
    inputs = {'sei': sei} if sei is not None else {'vi': vi} if vi is not None else {'lo': ci_lower, 'hi': ci_upper}
    vectors, size = _pj_meta_vectors(inputs)
    z = float(stats.norm.ppf((1 + level) / 2))
    output = {'vi': [], 'sei': []}
    for row in range(size):
        values = {key: value[row] for key, value in vectors.items()}
        if any(math.isnan(value) for value in values.values()):
            variance = error = None
        else:
            if 'sei' in values:
                error = _pj_meta_number(values['sei'], 'sei', minimum=0)
                variance = error * error
            elif 'vi' in values:
                variance = _pj_meta_number(values['vi'], 'vi', minimum=0)
                error = math.sqrt(variance)
            else:
                lo, hi = values['lo'], values['hi']
                if lo >= hi:
                    raise ValueError(f'Row {row + 1}: ci_lower must be smaller than ci_upper.')
                if transform == 'log':
                    if lo <= 0:
                        raise ValueError('Log-scale confidence limits must be positive.')
                    lo, hi = math.log(lo), math.log(hi)
                elif transform == 'fisher':
                    if lo <= -1 or hi >= 1:
                        raise ValueError('Fisher confidence limits must lie strictly between -1 and 1.')
                    lo, hi = math.atanh(lo), math.atanh(hi)
                error = (hi - lo) / (2 * z)
                variance = error * error
            if error is not None and not all(math.isfinite(x) for x in (error, variance)):
                raise ValueError('Sampling variance overflow; check input magnitudes.')
        output['vi'].append(variance)
        output['sei'].append(error)
    return output


def _pj_effect_interval(yi, *, vi=None, sei=None, level=0.95, transform='identity'):
    import math
    if transform not in ('identity', 'exp', 'tanh', 'logistic', 'ahw', 'abt'):
        raise ValueError('transform must be identity, exp, tanh, logistic, ahw or abt.')
    uncertainty = _pj_sampling_variance(vi=vi, sei=sei, level=level)
    effects, size = _pj_meta_vectors({'yi': yi})
    if size != len(uncertainty['sei']):
        raise ValueError('yi and uncertainty must have the same number of rows.')
    z = float(stats.norm.ppf((1 + level) / 2))
    def convert(value):
        if transform == 'exp':
            return math.exp(value)
        if transform == 'tanh':
            return math.tanh(value)
        if transform == 'logistic':
            return 1 / (1 + math.exp(-value)) if value >= 0 else math.exp(value) / (1 + math.exp(value))
        if transform == 'ahw':
            return 1 - (1 - value) ** 3
        if transform == 'abt':
            return -math.expm1(-value)
        return value
    result = {'estimate': [], 'lower': [], 'upper': []}
    for row, value in enumerate(effects['yi']):
        error = uncertainty['sei'][row]
        if math.isnan(value) or error is None:
            values = (None, None, None)
        else:
            try:
                values = tuple(convert(x) for x in (value, value-z*error, value+z*error))
                if not all(math.isfinite(x) for x in values):
                    raise OverflowError()
            except OverflowError:
                raise ValueError(f'Row {row+1}: interval transformation overflow.') from None
        for key, item in zip(result, values):
            result[key].append(item)
    return result


def _pj_effect_size(measure, *, correction=0.5, to='only0', drop00=False,
                    correct=True, invalid='raise', **inputs):
    import math
    _pj_meta_scipy()
    required = {'OR': ('ai','bi','ci','di'), 'RR': ('ai','bi','ci','di'),
                'RD': ('ai','bi','ci','di'),
                'MD': ('m1i','sd1i','n1i','m2i','sd2i','n2i'),
                'SMD': ('m1i','sd1i','n1i','m2i','sd2i','n2i'),
                'COR': ('ri','ni'), 'ZCOR': ('ri','ni'),
                'PR': ('xi','ni'), 'PLO': ('xi','ni'),
                'ARAW': ('ai','mi','ni'), 'AHW': ('ai','mi','ni'), 'ABT': ('ai','mi','ni'),
                'GEN': ('yi','vi')}
    if measure not in required:
        raise ValueError('Supported measures: ' + ', '.join(required) + '.')
    if measure == 'GEN' and 'sei' in inputs and 'vi' not in inputs:
        inputs = dict(inputs)
        inputs['vi'] = _pj_sampling_variance(sei=inputs.pop('sei'))['vi']
    if set(inputs) != set(required[measure]):
        raise ValueError(f'{measure} requires exactly these vectors: ' + ', '.join(required[measure]) + '.')
    if invalid not in ('raise', 'missing') or to not in ('only0','all','none'):
        raise ValueError('invalid must be raise or missing; to must be only0, all or none.')
    if not isinstance(drop00, bool) or not isinstance(correct, bool):
        raise TypeError('drop00 and correct must be booleans.')
    if drop00 and measure not in ('OR','RR','RD'):
        raise ValueError('drop00 applies only to OR, RR and RD.')
    if not correct and measure != 'SMD':
        raise ValueError('correct=False applies only to SMD (uncorrected Cohen d).')
    correction = _pj_meta_number(correction, 'correction', minimum=0)
    vectors, size = _pj_meta_vectors(inputs)
    result = {'yi': [], 'vi': [], 'sei': [], 'status': []}
    for row in range(size):
        x = {name: values[row] for name, values in vectors.items()}
        effect = variance = None
        status = 'missing input'
        try:
            if not any(math.isnan(value) for value in x.values()):
                if measure in ('OR','RR','RD'):
                    a,b,c,d = (x[key] for key in ('ai','bi','ci','di'))
                    for name, value in x.items():
                        _pj_meta_number(value, name, minimum=0, integer=True)
                    if a+b == 0 or c+d == 0:
                        raise ValueError('Both groups must contain participants.')
                    if drop00 and ((a == 0 and c == 0) or (b == 0 and d == 0)):
                        status = 'excluded: double-zero or double-all-event study'
                    else:
                        if to == 'all' or (to == 'only0' and min(a,b,c,d) == 0):
                            a,b,c,d = (value+correction for value in (a,b,c,d))
                        n1,n2 = a+b,c+d
                        if measure == 'RD':
                            effect = a/n1-c/n2
                            variance = a*b/n1**3+c*d/n2**3
                        else:
                            if (min(a,b,c,d) if measure == 'OR' else min(a,c)) <= 0:
                                raise ValueError('Undefined log effect: use an explicit positive zero-cell correction.')
                            if measure == 'OR':
                                effect = math.log(a)+math.log(d)-math.log(b)-math.log(c)
                                variance = 1/a+1/b+1/c+1/d
                            else:
                                effect = math.log(a/n1)-math.log(c/n2)
                                variance = 1/a-1/n1+1/c-1/n2
                elif measure in ('MD','SMD'):
                    m1,s1,n1,m2,s2,n2 = (x[key] for key in required[measure])
                    for name in ('n1i','n2i'):
                        _pj_meta_number(x[name], name, minimum=1, strict=True, integer=True)
                    for name in ('sd1i','sd2i'):
                        _pj_meta_number(x[name], name, minimum=0)
                    if measure == 'MD':
                        effect,variance = m1-m2,s1*s1/n1+s2*s2/n2
                    else:
                        df = n1+n2-2
                        pooled = math.sqrt(((n1-1)*s1*s1+(n2-1)*s2*s2)/df)
                        if pooled <= 0:
                            raise ValueError('SMD requires a positive pooled standard deviation.')
                        # Correzione esatta J(df), varianza LS di metafor, gruppi indipendenti.
                        from scipy.special import gammaln
                        factor = math.exp(gammaln(df/2)-0.5*math.log(df/2)-gammaln((df-1)/2)) if correct else 1
                        effect = factor*(m1-m2)/pooled
                        variance = 1/n1+1/n2+effect*effect/(2*(n1+n2))
                elif measure in ('COR','ZCOR'):
                    r,n = x['ri'],x['ni']
                    _pj_meta_number(n, 'ni', minimum=3, strict=True, integer=True)
                    if not -1 < r < 1:
                        raise ValueError('Correlation must lie strictly between -1 and 1.')
                    effect,variance = (math.atanh(r),1/(n-3)) if measure == 'ZCOR' else (r,(1-r*r)**2/(n-1))
                elif measure in ('PR','PLO'):
                    events,n = x['xi'],x['ni']
                    _pj_meta_number(n, 'ni', minimum=0, strict=True, integer=True)
                    _pj_meta_number(events, 'xi', minimum=0, integer=True)
                    if events > n:
                        raise ValueError('xi must not exceed ni.')
                    nonevents = n-events
                    if to == 'all' or (to == 'only0' and min(events,nonevents) == 0):
                        events,nonevents = events+correction,nonevents+correction
                    n = events+nonevents
                    if measure == 'PR':
                        effect,variance = events/n,events*nonevents/n**3
                    else:
                        if min(events,nonevents) <= 0:
                            raise ValueError('Logit requires positive event and non-event counts after correction.')
                        effect,variance = math.log(events)-math.log(nonevents),1/events+1/nonevents
                elif measure in ('ARAW','AHW','ABT'):
                    alpha,items,n = x['ai'],x['mi'],x['ni']
                    _pj_meta_number(items, 'mi', minimum=1, strict=True, integer=True)
                    _pj_meta_number(n, 'ni', minimum=2, strict=True, integer=True)
                    if alpha >= 1:
                        raise ValueError('Alpha must be smaller than 1; negative estimates are allowed.')
                    if measure == 'ARAW':
                        effect,variance = alpha,2*items*(1-alpha)**2/((items-1)*(n-2))
                    elif measure == 'AHW':
                        effect = 1-(1-alpha)**(1/3)
                        variance = 18*items*(n-1)*(1-alpha)**(2/3)/((items-1)*(9*n-11)**2)
                    else:
                        effect,variance = -math.log1p(-alpha),2*items/((items-1)*(n-2))
                else:
                    effect = x['yi']
                    variance = _pj_meta_number(x['vi'], 'vi', minimum=0)
                if effect is not None:
                    if not math.isfinite(effect) or not math.isfinite(variance) or variance < 0:
                        raise ValueError('Non-finite effect or invalid sampling variance; check input magnitudes.')
                    status = 'ok' if variance > 0 else 'zero variance'
        except (ValueError, OverflowError, ZeroDivisionError) as error:
            if invalid == 'raise':
                raise ValueError(f'{measure}, row {row+1}: {error}') from None
            effect = variance = None
            status = 'invalid: ' + str(error)
        result['yi'].append(effect)
        result['vi'].append(variance)
        result['sei'].append(math.sqrt(variance) if variance is not None else None)
        result['status'].append(status)
    return result


def _pj_meta_weights(vi, *, tau2=0):
    import math
    tau2 = _pj_meta_number(tau2, 'tau2', minimum=0)
    vectors,size = _pj_meta_vectors({'vi': vi})
    weights = []
    for row, value in enumerate(vectors['vi']):
        if math.isnan(value):
            weights.append(None)
        else:
            _pj_meta_number(value, f'vi at row {row+1}', minimum=0)
            if value+tau2 <= 0:
                raise ValueError(f'Row {row+1}: vi + tau2 must be positive; zero-variance rows cannot receive infinite weight.')
            denominator = value+tau2
            if not math.isfinite(denominator):
                raise ValueError('Variance plus tau2 overflow; check input magnitudes.')
            weights.append(1/denominator)
    # Normalizzazione scalata per evitare overflow della somma dei pesi.
    maximum = max((w for w in weights if w is not None), default=0)
    if maximum and not math.isfinite(maximum):
        raise ValueError('Weight overflow; check variance magnitudes.')
    total = math.fsum(w/maximum for w in weights if w is not None) if maximum else 0
    return {'weight': weights, 'percent': [100*(w/maximum)/total if w is not None else None for w in weights]}
