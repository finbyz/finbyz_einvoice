import frappe
from frappe import _

from finbyz_einvoice.gst_india.api_classes.base import BaseAPI
import base64
import os
from frappe.utils.data import time_diff_in_seconds
from frappe.utils import now_datetime
from frappe.integrations.utils import make_request
from frappe.utils.password import get_decrypted_password
from frappe.utils.data import add_to_date

class PublicAPI(BaseAPI):
    API_NAME = "GST Public"
    BASE_PATH = "commonapi"

    def setup(self):
        if self.sandbox_mode:
            frappe.throw(
                _(
                    "Autofill Party Information based on GSTIN is not supported in sandbox mode"
                )
            )

    def get_gstin_info(self, gstin):
        self.BASE_PATH = "enriched/commonapi"
        self.gst_settings = frappe.get_cached_doc("GST Settings")
        self.default_headers = {
                "authorization": get_auth_token(self),
                "requestid": str(base64.b64encode(os.urandom(18))),
            }
        return self.get("search", params={"action": "TP", "gstin": gstin})

def get_auth_token(self):
	if time_diff_in_seconds(self.gst_settings.token_expiry, now_datetime()) < 150.0:
		fetch_auth_token(self)

	return self.gst_settings.auth_token

def fetch_auth_token(self):
	client_id, client_secret = get_client_details(self)
	headers = {"gspappid": client_id, "gspappsecret": client_secret}
	res = {}
	url = "https://gsp.adaequare.com/gsp/authenticate?grant_type=token"\

	res = make_request("post", url, headers = headers)
	self.gst_settings.auth_token = "{} {}".format(
		res.get("token_type"), res.get("access_token")
	)

	self.gst_settings.token_expiry = add_to_date(None, seconds=res.get("expires_in"))
	self.gst_settings.save(ignore_permissions=True)
	self.gst_settings.reload()

def get_client_details(self):
	if self.gst_settings.get('client_id') and self.gst_settings.get('client_secret'):
		return self.gst_settings.get('client_id'), get_decrypted_password("GST Settings", "GST Settings", fieldname = "client_secret")

	return frappe.conf.einvoice_client_id, frappe.conf.einvoice_client_secret

