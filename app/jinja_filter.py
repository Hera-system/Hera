import datetime

from app import app


@app.template_filter()
def nice_datetime(date):
    if date is None:
        return date
    try:
        return date.strftime("%d/%m/%Y, %H:%M:%S")
    except:  # noqa: E722
        return date

@app.template_filter()
def webhook_active(webhook) -> bool:
    if not webhook.active:
        return False
    if (datetime.datetime.now() - webhook.time_connect).total_seconds() > app.config['WEBHOOK_ACTIVE_TIMEOUT']:
        return False
    return True