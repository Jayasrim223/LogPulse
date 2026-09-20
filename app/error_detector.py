def detect_errors(df):
    errors = df[df["status"] != 200].copy()

    return errors


def error_summary(df):
    errors = detect_errors(df)

    return {
        "total_errors": len(errors),
        "server_errors": len(errors[errors["status"] >= 500]),
        "client_errors": len(
            errors[
                (errors["status"] >= 400)
                & (errors["status"] < 500)
            ]
        )
    }