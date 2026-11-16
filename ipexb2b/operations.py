"""Declarative table of IPEX REST API operations (swagger 8.113.2).

One line per operation::

    name | METHOD | path | summary | query params | body

Query parameters marked with ``*`` are required. ``{placeholders}`` in the path
become required positional arguments. ``body`` is ``B`` when the operation
accepts a JSON body. The token endpoints (``/v1/token``, ``/v1/tokenBasic``,
``/v1/sso/*``, ``/v1/token/sendOTP``) are handled internally by
:class:`ipexb2b.client.ApiClient` and are deliberately not listed here.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Operation:
    name: str
    method: str
    path: str
    summary: str
    query: tuple[str, ...]
    required_query: tuple[str, ...]
    has_body: bool

    @property
    def path_params(self) -> tuple[str, ...]:
        import re

        return tuple(re.findall(r"{(\w+)}", self.path))

    @property
    def read_only(self) -> bool:
        return self.method == "GET"


_RAW = """
alive|GET|/alive|Alive check route||
health|GET|/health|Return status on dependent system||
get_calls|GET|/v1/calls|Call listing (výpis hovorů)|dateFrom*,dateTo,number,customerId,externId,typHistory,showCustomerId,showFreeUnits,showFlags,showCDRType,showVAT,showUID,showUnit|
get_calls_technical_overview|GET|/v1/calls/technical-overview|VoIP technical overview|number,dateFrom,dateTo|
list_connectors|GET|/v1/connectors|List of all connectors|customerId,type,connectorId,showPrice|
create_connector|POST|/v1/connectors|Automatic activation of a new connector||B
list_customers|GET|/v1/customers|Customer listing|id,fulltext,number,customerName,street,city,zipCode,note,login,tin,externId,type,hidden,ipex_zpusobFakturace,ipex_datumFakturaceOd,ipex_datumFakturaceDo,ipex_zvysenaPozornost,page,pageSize|
create_customer|POST|/v1/customers|Create a new customer||B
list_ict_price_lists|GET|/v1/ictPriceList|Get all pricelists|page,pageSize,orderBy,orderDir|
list_invoices|GET|/v1/invoices|Invoicing base data (list of services)|monthOffset,customerId*|
list_pbx|GET|/v1/pbx|PBX info|id,serviceId,customerId|
create_pbx|POST|/v1/pbx|Create new virtual PBX||B
list_phone_numbers_v1|GET|/v1/phone-numbers|Deprecated list of phone numbers|customerId,externalId,showOpid,number,limit,offset,search,orderBy,order|
list_requests|GET|/v1/requests|Order list|requestId,requestStatus,requestType,login,customerId,identifier,identifier2,insertedFrom,insertedTo,changedFrom,changedTo,detail|
get_rights|GET|/v1/rights|List of rights||
list_services|GET|/v1/services|List of services|containerId,number,status,paymentType,detail,result,customerId,numberType,externId|
list_wholesale_invoices|GET|/v1/wholesale-invoices|List of wholesale invoices|months,page,pageSize,orderBy,orderDir|
list_phone_numbers|GET|/v2/phone-numbers|List of phone numbers|customerId,externalId,showOpid,number,limit,offset,search,orderBy,order|
get_account|GET|/v1/accounts/{username}|Get provider user||
update_account|PUT|/v1/accounts/{username}|Update provider user||B
delete_account|DELETE|/v1/accounts/{username}|Delete provider user||
create_account|POST|/v1/accounts|Create provider user||B
get_connector_analysis|GET|/v1/analysis/connector|Connector analysis|periodFrom*,periodTo|
list_connector_invoices_all|GET|/v1/connectors/invoices|Billing list for all connectors|dateFrom*,dateTo*,detail|
get_connector|GET|/v1/connectors/{connectorId}|Connector detail||
update_connector|PUT|/v1/connectors/{connectorId}|Connector change||B
list_containers|GET|/v1/containers/{type}|List of containers (ústředny) by type||
get_customer|GET|/v1/customers/{id}|Customer detail||
update_customer|PUT|/v1/customers/{id}|Update customer parameters (full)||B
patch_customer|PATCH|/v1/customers/{id}|Update customer parameters (partial)||B
get_free_units_history|GET|/v1/freeUnits/history|Free units usage history|number,year*,month*|
get_helpdesk|GET|/v1/helpdesk/{id}|Get service helpdesk detail||
get_ict_price_list|GET|/v1/ictPriceList/{id}|Get pricelist detail||
patch_ict_price_list|PATCH|/v1/ictPriceList/{id}|Update pricelist name||B
list_internet_types|GET|/v1/internet/types|List internet service types||
get_internet|GET|/v1/internet/{id}|Get internet service detail||
list_invoice_item_ids|GET|/v1/invoiceItem/idList|List of inserted ids (hints)||
get_invoice_item|GET|/v1/invoiceItem/{id}|Get virtual service detail||
get_invoices_by_payment_type|GET|/v1/invoices/{paymentType}|Invoicing base data by payment type|monthOffset,analysis|
get_mobile|GET|/v1/mobile/{number}|Mobile number detail|iccid,detail|
get_provider_settings|GET|/v1/providers/settings|Provider settings||
get_report_customers|GET|/v1/reports/customers|Customer count||
get_report_numbers|GET|/v1/reports/numbers|Service count|show,status,paymentType,numberType,customerId|
get_request|GET|/v1/requests/{requestId}|Order detail||
cancel_request|DELETE|/v1/requests/{requestId}|Cancel an order||
search_ruian|GET|/v1/ruian/{fulltext}|Addresses found by fulltext (RUIAN)|detail|
search_services_fulltext|GET|/v1/services/fulltext|Service full text search|type,customerId,fullTextSearch|
list_shared_services|GET|/v1/services/shared|List of shared services|customerId|
get_service|GET|/v1/services/{serviceId}|Get service||
delete_service|DELETE|/v1/services/{serviceId}|Delete service||
get_support|GET|/v1/support/{id}|Get guaranteed support detail||
get_tariff_plan|GET|/v1/tariffPlans/{tariffPlanId}|Tariff plan detail|type|
check_ticketing_user|GET|/v1/ticketing/check-user|Get requestor user by username||
get_current_user|GET|/v1/users/me|Get the authenticated user|detail|
list_voip_profiles|GET|/v1/voip/profiles|List of landline profiles||
get_voip|GET|/v1/voip/{number}|Landline number detail|iccid,detail|
get_phone_number_diagnostic|GET|/v2/phone-numbers/diagnostic|Number diagnostic detail|number*,full|
list_connector_invoices|GET|/v1/connectors/{connectorId}/invoices|Billing list for one connector|dateFrom,dateTo,monthOffset,detail|
list_connector_phone_numbers|GET|/v1/connectors/{connectorId}/phoneNumbers|Phone numbers of a connector|number,status,paymentType,customerId,containerId,numberType,externId,category|
list_container_roaming_profiles|GET|/v1/containers/{containerId}/roamingProfiles|Roaming profiles of a container||
list_container_phone_numbers|GET|/v1/containers/{containerId}/phoneNumbers|Phone numbers of a container|number,status,paymentType,customerId,trunkId,numberType,externId,detail|
list_container_data_packs|GET|/v1/containers/{containerId}/dataPacks|Data packs of a container|tariffPlanId,type|
list_container_flat_packs|GET|/v1/containers/{containerId}/flatPacks|Flat packs of a container|tariffPlanId|
list_container_simcards|GET|/v1/containers/{containerId}/simcards|SIM cards of a container|fulltext,iccid,limit,status|
get_customer_name|GET|/v1/customers/customername/{id}|Customer name for the given id||
list_customer_users|GET|/v1/customers/{customerId}/users|All users of a customer||
get_ict_price_list_item|GET|/v1/ictPriceList/items/{itemId}|Get pricelist item||
patch_ict_price_list_item|PATCH|/v1/ictPriceList/items/{itemId}|Change pricelist item price||B
get_invoices_print|GET|/v1/invoices/{paymentType}/{fileFormat}|Printable output of invoicing base data|customerId,monthOffset,include|
list_mobile_portation_dates|GET|/v1/mobile/availablePortationDates/{cvop}|Possible porting days||
reset_mobile_postpaid_limit|PUT|/v1/mobile/{number}/resetPostpaidLimit|Reset postpaid limit of a mobile||
suspend_mobile|PUT|/v1/mobile/{number}/suspend|Suspend a mobile number||
reactivate_mobile|PUT|/v1/mobile/{number}/reactivate|Reactivate a mobile number||
get_mobile_credit|GET|/v1/mobile/{number}/credit|Credit history of a mobile||
add_mobile_credit|PUT|/v1/mobile/{number}/credit|Top up credit of a mobile||B
get_report_ctu|GET|/v1/reports/cz/ctu|ČTÚ statistics|byType,dateFrom,dateTo,statsType|
get_report_top_customers|GET|/v1/reports/providers/top-customers|Top customers|order,top|
get_ruian_address|GET|/v1/ruian/address/{ruianId}|Address detail (RUIAN)||
get_service_properties|GET|/v1/services/{serviceId}/properties|Get service properties||
update_service_properties|PUT|/v1/services/{serviceId}/properties|Update property in a service||B
get_sms_integration|GET|/v1/sms/integration/{serviceId}|Get SMS service detail||
update_sms_integration|PUT|/v1/sms/integration/{serviceId}|Update SMS service||B
get_sso_ticketing_token|GET|/v1/sso/ticketing/token|Token for the ticketing requestor||
get_tariff_plan_price|GET|/v1/tariffPlans/{tariffPlanId}/price|Price of a tariff plan|cdrType,number|
list_tariff_plan_trunk_types|GET|/v1/tariffPlans/{tariffPlanId}/trunkTypes|Price list of trunk types for a tariff|customer_price_higher|
get_voip_credit|GET|/v1/voip/{number}/credit|Credit history of a landline||
add_voip_credit|PUT|/v1/voip/{number}/credit|Top up credit of a landline||B
get_voip_state|GET|/v1/voip/{number}/state|Landline number state|iccid|
get_report_provider_customers_count|GET|/v1/reports/providers/customers/count|Customer count (provider)||
get_report_provider_requests_count|GET|/v1/reports/providers/requests/count|Order count (provider)|state|
get_report_zoom_provider|GET|/v1/reports/zoom/provider/{month}|Zoom call detail (provider)||
get_report_connector_phone_numbers_count|GET|/v1/reports/connectors/{connectorId}/phoneNumbers/count|Phone number count of a connector||
get_report_customer_services_count|GET|/v1/reports/customers/{customerId}/services/count|Service count of a customer|type|
get_report_customer_requests_count|GET|/v1/reports/customers/{customerId}/requests/count|Order count of a customer||
get_report_zoom_customer|GET|/v1/reports/zoom/customer/{customerId}/{month}|Zoom call detail (customer)||
get_report_customer_invoices_sum|GET|/v1/reports/customers/{customerId}/invoices/sum/{monthOffset}|Sum of invoices of a customer||
create_helpdesk|POST|/v1/helpdesk|Create a helpdesk service||B
create_internet|POST|/v1/internet|Create an internet service||B
create_mobile|POST|/v1/mobile|Create a mobile number||B
update_mobile|PUT|/v1/mobile|Modify a mobile number||B
send_sms|POST|/v1/sms|Send an SMS||B
create_support|POST|/v1/support|Create a guaranteed support service||B
create_voip|POST|/v1/voip|Create a landline||B
update_voip|PUT|/v1/voip|Modify landline settings||B
copy_ict_price_list|POST|/v1/ictPriceList/copy|Create a new pricelist as a copy||B
create_sms_integration|POST|/v1/sms/integration|Create an SMS service||B
port_in_connector|POST|/v1/connectors/{connectorId}/portIn|Import phone numbers into a connector||B
order_connector_block|POST|/v1/connectors/{connectorId}/orderNewBlock|Order a block of numbers into a connector||B
deactivate_connector|POST|/v1/connectors/{connectorId}/deactivate|Deactivate a connector||B
port_in_container|POST|/v1/containers/{containerId}/portIn|Port numbers into a container||B
check_calls_income_drop|POST|/v1/maintenance/calls/checkIncomeDrop|Check call price sums||B
create_phone_number_block|PUT|/v2/phone-numbers/block|Create a new number block||B
renew_mobile_sim|PUT|/v1/mobile/{number}/renew|Replace SIM card for a number||B
deactivate_mobile|PUT|/v1/mobile/{number}/deactivate|Terminate a mobile service||B
update_mobile_oku|PUT|/v1/mobile/{phoneNumber}/oku|Update OKU code||B
bind_system_user|PUT|/v1/services/{serviceId}/systemUserBinding|Allow integration for a PBX system user||B
deactivate_voip|PUT|/v1/voip/{number}/deactivate|Terminate a landline||B
update_connector_phone_number|PUT|/v1/connectors/{connectorId}/phoneNumbers/{number}|Edit a phone number in a connector||B
delete_pbx|DELETE|/v1/pbx/{serviceId}|Delete PBX||
patch_pbx|PATCH|/v1/pbx/{serviceId}|Update PBX parameters||B
patch_helpdesk|PATCH|/v1/helpdesk/{serviceId}|Change helpdesk properties||B
patch_internet|PATCH|/v1/internet/{serviceId}|Change internet type and properties||B
refresh_oku|PATCH|/v1/numbers/refresh-oku|Replace old OKU with a new one||B
patch_support|PATCH|/v1/support/{serviceId}|Change guaranteed support type or hours||B
"""


def _parse() -> tuple[Operation, ...]:
    ops: list[Operation] = []
    for line in _RAW.strip().splitlines():
        name, method, path, summary, query, body = line.split("|")
        params = [q for q in query.split(",") if q]
        ops.append(
            Operation(
                name=name,
                method=method,
                path=path,
                summary=summary,
                query=tuple(q.rstrip("*") for q in params),
                required_query=tuple(q.rstrip("*") for q in params if q.endswith("*")),
                has_body=body == "B",
            )
        )
    return tuple(ops)


OPERATIONS: tuple[Operation, ...] = _parse()
BY_NAME: dict[str, Operation] = {op.name: op for op in OPERATIONS}
