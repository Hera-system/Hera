from app import app


@app.template_filter()
def nice_datetime(date):
    if date is None:
        return date
    try:
        return date.strftime("%d/%m/%Y, %H:%M:%S")
    except:  # noqa: E722
        return date
