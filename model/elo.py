def initialise_elo(drivers_ids):
    return {driver_id: 1000.0 for driver_id in drivers_ids}


def compute_elo_delta(composite_scores, K=32):
    n = len(composite_scores)
    delta = {}

    sorted_drivers =  sorted(composite_scores.items(), key=lambda item: item[1], reverse=True)
    for rank, (driver_id, score) in enumerate(sorted_drivers):
        delta[driver_id] = K * (0.5 - rank / (n - 1))
    return delta


def update_elo(current_elo, deltas):
    updated = current_elo.copy()

    for driver_id, delta in deltas.items():
        if driver_id in updated:
            updated[driver_id] += delta
        else:
            updated[driver_id] = 1000 + delta
    return updated

