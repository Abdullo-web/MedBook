specializations = []
doctors = []
patients = []
appointments = []

id_counters = {
    "specialization": 0,
    "doctor": 0,
    "patient": 0,
    "appointment": 0,
}


def next_id(entity: str) -> int:
    id_counters[entity] += 1
    return id_counters[entity]
