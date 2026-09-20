from app.analyzer import load_logs
from app.error_detector import error_summary


def test_log_loading():
    df = load_logs("server.log")

    assert len(df) == 26
    assert "status" in df.columns
    assert "endpoint" in df.columns


def test_error_detection():
    df = load_logs("server.log")

    summary = error_summary(df)

    assert summary["total_errors"] == 12
    assert summary["server_errors"] == 4
    assert summary["client_errors"] == 8