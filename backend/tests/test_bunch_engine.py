from datetime import datetime, timedelta
from app.services.bunch_engine import classify_gap, detect_bunching

def test_classify_bunching():
    assert classify_gap(2.0, 8.0, 3.0, 15.0)[0] == "bunching"

def test_classify_large():
    assert classify_gap(16.0, 8.0, 3.0, 15.0)[0] == "large_gap"

def test_classify_normal():
    assert classify_gap(8.0, 8.0, 3.0, 15.0)[0] == "normal"

def test_detect_bunching_events():
    base = datetime(2026, 1, 1, 8, 0)
    arrivals = [
        {"stop_name": "A", "trip_no": "T1", "actual_arrive": base},
        {"stop_name": "A", "trip_no": "T2", "actual_arrive": base + timedelta(minutes=2)},
        {"stop_name": "A", "trip_no": "T3", "actual_arrive": base + timedelta(minutes=20)},
    ]
    events = detect_bunching(arrivals, 8.0, 3.0, 15.0)
    assert len(events) == 2
    assert events[0].status == "bunching"
    assert events[1].status == "large_gap"

def test_same_vehicle_not_bunching():
    base = datetime(2026, 1, 1, 8, 0)
    arrivals = [
        {"stop_name": "A", "trip_no": "T1", "vehicle_no": "粤A1001", "actual_arrive": base},
        {"stop_name": "A", "trip_no": "T2", "vehicle_no": "粤A1001", "actual_arrive": base + timedelta(minutes=2)},
    ]
    events = detect_bunching(arrivals, 8.0, 3.0, 15.0)
    assert len(events) == 1
    assert events[0].status == "same_vehicle"
    assert events[0].same_vehicle is True

def test_same_vehicle_not_large_gap():
    base = datetime(2026, 1, 1, 8, 0)
    arrivals = [
        {"stop_name": "A", "trip_no": "T1", "vehicle_no": "粤A1001", "actual_arrive": base},
        {"stop_name": "A", "trip_no": "T2", "vehicle_no": "粤A1001", "actual_arrive": base + timedelta(minutes=20)},
    ]
    events = detect_bunching(arrivals, 8.0, 3.0, 15.0)
    assert len(events) == 1
    assert events[0].status == "same_vehicle"

def test_different_vehicles_still_judged():
    base = datetime(2026, 1, 1, 8, 0)
    arrivals = [
        {"stop_name": "A", "trip_no": "T1", "vehicle_no": "粤A1001", "actual_arrive": base},
        {"stop_name": "A", "trip_no": "T2", "vehicle_no": "粤A1002", "actual_arrive": base + timedelta(minutes=2)},
        {"stop_name": "A", "trip_no": "T3", "vehicle_no": "粤A1003", "actual_arrive": base + timedelta(minutes=20)},
    ]
    events = detect_bunching(arrivals, 8.0, 3.0, 15.0)
    assert [e.status for e in events] == ["bunching", "large_gap"]
    assert all(e.same_vehicle is False for e in events)

def test_empty_vehicle_no_not_matched():
    base = datetime(2026, 1, 1, 8, 0)
    arrivals = [
        {"stop_name": "A", "trip_no": "T1", "vehicle_no": "", "actual_arrive": base},
        {"stop_name": "A", "trip_no": "T2", "vehicle_no": "", "actual_arrive": base + timedelta(minutes=2)},
    ]
    events = detect_bunching(arrivals, 8.0, 3.0, 15.0)
    assert events[0].status == "bunching"
    assert events[0].same_vehicle is False
