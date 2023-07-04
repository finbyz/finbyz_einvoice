import click

from finbyz_einvoice.gst_india.constants import BUG_REPORT_URL
from finbyz_einvoice.gst_india.uninstall import before_uninstall as remove_gst
from finbyz_einvoice.income_tax_india.uninstall import (
    before_uninstall as remove_income_tax,
)


def before_uninstall():
    try:
        print("Removing Income Tax customizations...")
        remove_income_tax()

        print("Removing GST customizations...")
        remove_gst()

    except Exception as e:
        click.secho(
            (
                "Removing customizations for Finbyz Einvoice failed due to an error."
                " Please try again or"
                f" report the issue on {BUG_REPORT_URL} if not resolved."
            ),
            fg="bright_red",
        )
        raise e
