from datetime import datetime, timedelta
from flask import Flask, flash, redirect, request, render_template, url_for
import os

from db import DB

app = Flask(__name__)
app.secret_key = "very_secret_key"

db_config = {
    "host": os.environ["POSTGRES_HOST"],
    "database": os.environ["POSTGRES_DB"],
    "user": os.environ["POSTGRES_USER"],
    "password": os.environ["POSTGRES_PASSWORD"],
    "port": os.environ["POSTGRES_PORT"],
}

db = DB(db_config)


@app.route("/", methods=["GET"])
def index():
    delta = 90
    today = datetime.today().strftime("%Y-%m-%d")
    ninety_days_ago = (datetime.today() - timedelta(days=delta)).strftime("%Y-%m-%d")
    return render_template("results.html", start_date=ninety_days_ago, end_date=today)


@app.route("/query", methods=["GET"])
def query():
    submitter = request.args.get("submitter")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    if not submitter or not start_date or not end_date:
        return index()

    try:
        start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
        end_datetime = datetime.strptime(end_date, "%Y-%m-%d")
        delta = (end_datetime - start_datetime).days
    except ValueError:
        flash("Invalid date format. Please use YYYY-MM-DD format.")
        return redirect(url_for("query"))

    submissions = db.total_submissions(submitter, start_date, end_date)
    submissions_status = "✅" if submissions[0][0] == submissions[0][1] > 0 else "⚠️"

    batch_info = db.submissions_per_batch(submitter, start_date, end_date)
    batch_info_status = (
        "⚠️"
        if any(batch[3] == 0 or batch[4] > 0 or batch[5] > 0 for batch in batch_info)
        else "✅"
    )

    points_info = db.points_per_batch(submitter, start_date, end_date)
    points_info_status = "⚠️" if any(point[2] != 1 for point in points_info) else "✅"

    batches_without_points = db.batches_without_points(submitter, start_date, end_date)
    batches_without_points_status = "⚠️" if len(batches_without_points) > 0 else "✅"

    total_points = sum(point[2] for point in points_info)
    available_points = len(points_info)
    availability = total_points / available_points if available_points > 0 else 0
    total_points_status = "⚠️" if availability != 1 else "✅"

    bad_submissions = db.bad_submissions(submitter, start_date, end_date)

    return render_template(
        "results.html",
        submitter=submitter,
        start_date=start_date,
        end_date=end_date,
        delta=delta,
        submissions=submissions,
        submissions_status=submissions_status,
        batch_info=batch_info,
        batch_info_status=batch_info_status,
        total_points=total_points,
        available_points=available_points,
        total_points_status=total_points_status,
        availability=availability,
        points_info=points_info,
        points_info_status=points_info_status,
        bad_submissions=bad_submissions,
        batches_without_points=batches_without_points,
        batches_without_points_status=batches_without_points_status,
    )


if __name__ == "__main__":
    app.run(debug=True)
