import re

import frappe
from frappe import _
import base64
import os
from finbyz_einvoice.gst_india.api_classes.base import BaseAPI
from finbyz_einvoice.gst_india.constants import DISTANCE_REGEX
from finbyz_einvoice.gst_india.api_classes.public import get_auth_token

class EInvoiceAPI(BaseAPI):
    API_NAME = "e-Invoice"
    BASE_PATH = "ei/api"
    SENSITIVE_HEADERS = BaseAPI.SENSITIVE_HEADERS + ("password",)
    IGNORED_ERROR_CODES = {
        # Generate IRN errors
        "2150": "Duplicate IRN",
        # Get e-Invoice by IRN errors
        "2283": (
            "IRN details cannot be provided as it is generated more than 2 days ago"
        ),
        # Cancel IRN errors
        "9999": "Invoice is not active",
    }

    def setup(self, doc=None, *, company_gstin=None):
        self.BASE_PATH = "enriched/ei/api"
        if not self.settings.enable_e_invoice:
            frappe.throw(_("Please enable e-Waybill features in GST Settings first"))
        self.gst_settings = frappe.get_cached_doc("GST Settings")
        if doc:
            company_gstin = doc.company_gstin
            self.default_log_values.update(
                reference_doctype=doc.doctype,
                reference_name=doc.name,
            )

        if self.sandbox_mode:
            company_gstin = "05AAACG2115R1ZN"
            self.username = "05AAACG2115R1ZN"
            self.password = "abc123@@"

        elif not company_gstin:
            frappe.throw(_("Company GSTIN is required to use the e-Waybill API"))

        else:
            self.fetch_credentials(company_gstin, "e-Waybill / e-Invoice")

        self.default_headers.update(
            {
                "authorization": get_auth_token(self),
                "gstin": company_gstin,
                "user_name": self.username,
                "password": self.password,
                "requestid": str(base64.b64encode(os.urandom(18))),
            }
        )

    def handle_failed_response(self, response_json):
        message = response_json.get("message", "").strip()

        for error_code in self.IGNORED_ERROR_CODES:
            if message.startswith(error_code):
                response_json.error_code = error_code
                return True

    def get_e_invoice_by_irn(self, irn):
        return self.get(endpoint="invoice/irn", params={"irn": irn})

    def generate_irn(self, data):
        result = self.post(endpoint="invoice", json=data)

        # In case of Duplicate IRN, result is a list
        if isinstance(result, list):
            result = result[0]

        self.update_distance(result)
        return result

    def cancel_irn(self, data):
        return self.post(endpoint="invoice/cancel", json=data)

    def generate_e_waybill(self, data):
        result = self.post(endpoint="ewaybill", json=data)
        self.update_distance(result)
        return result

    def cancel_e_waybill(self, data):
        return self.post(endpoint="ewayapi", json=data)

    def update_distance(self, result):
        if not (info := self.response.get("info")):
            return

        alert = next((alert for alert in info if alert.get("InfCd") == "EWBPPD"), None)

        if (
            alert
            and (description := alert.get("Desc"))
            and (distance_match := re.search(DISTANCE_REGEX, description))
        ):
            result.distance = int(distance_match.group())
