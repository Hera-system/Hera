from app import app


@app.template_filter()
def nice_datetime(date):
    if date is None:
        return date
    return date.strftime("%d/%m/%Y, %H:%M:%S")
