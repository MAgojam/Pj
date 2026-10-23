# Run in Pj or Pjp with either Python interpreter. No dataset is required.
# Compare staffing scenarios using identical simulated arrivals and service times.
import random
simpy = mzpjUseLibrary('simpy')
rng = random.Random(2026)
arrivals, services = [], []
clock = 0.0
for _ in range(80):
    clock += rng.expovariate(1 / 4)
    arrivals.append(clock)
    services.append(rng.uniform(3, 7))

def simulate(staff):
    env = simpy.Environment()
    resource = simpy.Resource(env, capacity=staff)
    waits = []

    def visitor(arrival, duration):
        yield env.timeout(arrival)
        with resource.request() as request:
            yield request
            waits.append(env.now - arrival)
            yield env.timeout(duration)
    for arrival, duration in zip(arrivals, services):
        env.process(visitor(arrival, duration))
    env.run()
    return waits

rows = []
for staff in (1, 2, 3):
    waits = simulate(staff)
    rows.append({'Staff': staff, 'Visitors': len(waits), 'Mean wait': sum(waits) / len(waits),
                 'Maximum wait': max(waits)})
mzpjShowTable(rows, name='queue_results', title='Waiting times under three staffing scenarios',
              notes='One reproducible simulation per scenario, not an inferential comparison.')
mzpjShowBar({'Staff': [str(row['Staff']) for row in rows],
             'Mean wait': [row['Mean wait'] for row in rows]},
            category='Staff', value='Mean wait', stat='identity',
            name='queue_plot', title='Mean waiting time by number of staff')
