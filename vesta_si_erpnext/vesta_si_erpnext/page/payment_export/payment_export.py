# -*- coding: utf-8 -*-
# Copyright (c) 2017-2018, libracore (https://www.libracore.com) and contributors
# License: AGPL v3. See LICENCE

from __future__ import unicode_literals
import frappe
from frappe import throw, _
from collections import defaultdict
import time
import json
#from erpnextswiss.erpnextswiss.common_functions import get_building_number, get_street_name, get_pincode, get_city
import html              # used to escape xml content
from frappe.utils import flt, get_link_to_form, getdate, nowdate, now, get_url
from datetime import datetime
from openpyxl import Workbook

@frappe.whitelist()
def get_payments(payment_type, payment_export_settings):
    payments = frappe.db.sql(""" Select pe.name, pe.posting_date, pe.paid_amount, pe.party, pe.party_name, pe.paid_from, pe.paid_to_account_currency, per.reference_doctype,
                                per.reference_name, pe.received_amount
                                From `tabPayment Entry` as pe 
                                Left Join `tabPayment Entry Reference` as per ON per.parent = pe.name
                                Where pe.docstatus = 0 and pe.payment_type = "Pay" and pe.party_type = "Supplier" and pe.custom_xml_file_generated = 0 and pe.custom_is_manual_payment_process = 0
                                order by posting_date
                                """,as_dict = 1)
    submitted_entry = None
    allow_after_submit = frappe.db.get_value("Payment Export Settings", payment_export_settings, "include_payment_in_xml_after_submit")
    
    if allow_after_submit:
        submitted_entry = frappe.db.sql(""" Select pe.name, pe.posting_date, pe.paid_amount, pe.party, pe.party_name, pe.paid_from, pe.paid_to_account_currency, per.reference_doctype,
                                    per.reference_name, pe.received_amount
                                    From `tabPayment Entry` as pe 
                                    Left Join `tabPayment Entry Reference` as per ON per.parent = pe.name
                                    Where pe.docstatus = 1 and pe.payment_type = "Pay" and pe.party_type = "Supplier" and pe.custom_xml_file_generated = 0 and pe.custom_include_in_xml_file = 1
                                    order by posting_date
                                    """,as_dict = 1)
    if submitted_entry:
        payments = payments + submitted_entry
    
    merged_data = defaultdict(list)
    for row in payments:
        key = row['name']
        merged_data[key].append(row['reference_name'])
    
    sorted_data = {}
    for key, values in merged_data.items():
        sorted_data.update({key:values}) 
    
    sort_list = []
    data = []
    for row in payments:
        if sorted_data.get(row.name):
            row.update({"reference_name":sorted_data.get(row.name)})
        if row.name not in sort_list:
            sort_list.append(row.name)
            data.append(row)
            
    _payments = []
    list_of_amount = []
    for row in data:
        payment = frappe.get_doc('Payment Entry', row.name)
        creditor_info = add_creditor_info(payment)
        if not creditor_info:
            continue
        if payment_type == "Domestic (Swedish) Payments (SEK)":
            if ((frappe.db.get_value("Supplier", row.party , 'plus_giro_number') or 
                frappe.db.get_value("Supplier", row.party , 'bank_giro_number')) and
                frappe.db.get_value("Supplier", row.party , 'custom_payment_type') == 'Domestic (Swedish) Payments (SEK)'):
                _payments.append(row)
                list_of_amount.append(row.paid_amount)
        if payment_type == "SEPA (EUR)" and frappe.db.get_value('Supplier', row.party, 'custom_payment_type') == 'SEPA (EUR)':
                flag = False
                for d in row.reference_name:
                    currency = frappe.db.get_value(row.reference_doctype, d, 'currency')
                    if currency == "EUR":
                        flag = True
                if flag:
                    _payments.append(row)
                    list_of_amount.append(row.paid_amount)
        if payment_type == "Cross Border Payments (USD)" and frappe.db.get_value('Supplier', row.party, 'custom_payment_type') == 'Cross Border Payments (USD)':
                row.update({"paid_amount":row.received_amount})
                _payments.append(row)
                list_of_amount.append(row.received_amount)
        if payment_type == "Cross Border Payments (EUR)" and frappe.db.get_value('Supplier', row.party, 'custom_payment_type') == 'Cross Border Payments (EUR)':
                row.update({"paid_amount":row.received_amount})
                _payments.append(row)
                list_of_amount.append(row.received_amount)
        if payment_type == "Cross Border Payments (OTHER)" and frappe.db.get_value('Supplier', row.party, 'custom_payment_type') == 'Cross Border Payments (OTHER)':
                row.update({"paid_amount":row.received_amount})
                _payments.append(row)
                list_of_amount.append(row.received_amount)
    
    return { 'payments': _payments, "total_paid_amount" : sum(list_of_amount)}

@frappe.whitelist()
def generate_payment_file(payments ,payment_export_settings , posting_date , payment_type , bank_account = None):
    if payment_type == "SEPA (EUR)":
        content, transaction_count, control_sum = genrate_file_for_sepa(payments ,payment_export_settings , posting_date , payment_type)
        current_time = now()
        original_date = datetime.strptime(str(current_time), '%Y-%m-%d %H:%M:%S.%f')
        formatted_date = original_date.strftime('%Y-%m-%d %H-%M-%S')
        formatted_date = formatted_date.replace(' ','-')
        payments = eval(payments)
        payments = list(filter(None, payments))
        gen_payment_export_log(content, transaction_count, control_sum, payments, 'EUR')
        
        return { 'content': content, 'skipped': 0 , 'time':formatted_date}

    if payment_type in ["Cross Border Payments (USD)" , "Cross Border Payments (EUR)", "Cross Border Payments (OTHER)"]:
        
        if payment_type == "Cross Border Payments (OTHER)" and not bank_account:
            frappe.throw("Bank Account is mandatory for payment type <b>Cross Border Payments (OTHER)</b>")
        
        from vesta_si_erpnext.vesta_si_erpnext.page.payment_export.cross_border_payment import get_cross_border_xml_file
        
        content, transaction_count, control_sum = get_cross_border_xml_file(payments ,payment_export_settings , posting_date , payment_type, bank_account)
        current_time = now()
        original_date = datetime.strptime(str(current_time), '%Y-%m-%d %H:%M:%S.%f')
        formatted_date = original_date.strftime('%Y-%m-%d %H-%M-%S')
        formatted_date = formatted_date.replace(' ','-')
        payments = eval(payments)
        payments = list(filter(None, payments))
        if payment_type == "Cross Border Payments (USD)":
            currency = "USD"
        if payment_type == "Cross Border Payments (EUR)":
            currency = "EUR"
        if payment_type == "Cross Border Payments (OTHER)":
            currency = None
        gen_payment_export_log(content, transaction_count, control_sum, payments, currency)
        
        return { 'content': content, 'skipped': 0 , 'time':formatted_date}
    

    # creates a pain.001 payment file from the selected payments
    try:
        # convert JavaScript parameter into Python array
        payments = eval(payments)
        # remove empty items in case there should be any (bigfix for issue #2)
        payments = list(filter(None, payments))
        
        # array for skipped payments
        skipped = []
        
        # create xml header
        content = make_line("<?xml version=\"1.0\" encoding=\"UTF-8\"?>")
        # define xml template reference
        content += make_line("<Document xmlns=\"urn:iso:std:iso:20022:tech:xsd:pain.001.001.03\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:schemaLocation=\"urn:iso:std:iso:20022:tech:xsd:pain.001.001.03 pain.001.001.03.xsd\">")
        # transaction holder
        content += make_line("  <CstmrCdtTrfInitn>")
        ### Group Header (GrpHdr, A-Level)
        # create group header
        content += make_line("    <GrpHdr>")
        # message ID (unique, SWIFT-characters only)
        content += make_line("      <MsgId>MSG-" + time.strftime("%Y%m%d%H%M%S") + "</MsgId>")
        # creation date and time ( e.g. 2010-02-15T07:30:00 )
        content += make_line("      <CreDtTm>" + time.strftime("%Y-%m-%dT%H:%M:%S") + "Z" + "</CreDtTm>")
        # number of transactions in the file
        transaction_count = 0
        transaction_count_identifier = "<!-- $COUNT -->"
        content += make_line("      <NbOfTxs>" + transaction_count_identifier + "</NbOfTxs>")
        # total amount of all transactions ( e.g. 15850.00 )  (sum of all amounts)
        control_sum = 0.0
        control_sum_identifier = "<!-- $CONTROL_SUM -->"
        content += make_line("      <CtrlSum>" + control_sum_identifier + "</CtrlSum>")
        # initiating party requires at least name or identification
        content += make_line("      <InitgPty>")
        # initiating party name ( e.g. MUSTER AG )
        content += make_line("        <Nm>" + get_company_name(payments[0]) + "</Nm>")
        content += make_line("        <Id>")                      
        content += make_line("        <OrgId>")
        content += make_line("        <Othr>")
        content += make_line("        <Id>556036867100</Id>")
        content += make_line("        <SchmeNm>")
        content += make_line("        <Cd>BANK</Cd>")
        content += make_line("        </SchmeNm>")
        content += make_line("        </Othr>")
        content += make_line("        </OrgId>")
        content += make_line("        </Id>")                                           
        content += make_line("      </InitgPty>")
        content += make_line("    </GrpHdr>")
        ### Payment Information (PmtInf, B-Level)
        # payment information records (1 .. 99'999)
        content += make_line("    <PmtInf>")
        # unique (in this file) identification for the payment ( e.g. PMTINF-01, PMTINF-PE-00005 )
        content += make_line("      <PmtInfId>" + payments[0] + "</PmtInfId>")
        content += make_line("      <PmtMtd>TRF</PmtMtd>")
        content += make_line("      <NbOfTxs>" + transaction_count_identifier + "</NbOfTxs>")
        content += make_line("      <CtrlSum>" + control_sum_identifier + "</CtrlSum>")
        content += make_line("      <PmtTpInf>")
        content += make_line("          <SvcLvl>")
        content += make_line("            <Prtry>MPNS</Prtry>")
        content += make_line("          </SvcLvl>")
        content += make_line("        </PmtTpInf>")
        required_execution_date = posting_date
        content += make_line("      <ReqdExctnDt>{0}</ReqdExctnDt>".format(required_execution_date))
        content += make_line("      <Dbtr>")
        company_name = frappe.db.get_value('Payment Export Settings',payment_export_settings,'company_name')
        content += make_line("      <Nm>{0}</Nm>".format(company_name))


        content += make_line("        <PstlAdr>")
        street_name = frappe.db.get_value('Payment Export Settings',payment_export_settings,'street_name')
        content += make_line("          <StrtNm>" + street_name + "</StrtNm>")
        post_code = frappe.db.get_value('Payment Export Settings',payment_export_settings,'post_code')
        content += make_line("          <PstCd>" + post_code + "</PstCd>")
        town_name = frappe.db.get_value('Payment Export Settings',payment_export_settings,'town_name')
        content += make_line("          <TwnNm>" + town_name + "</TwnNm>")
        country = frappe.db.get_value('Payment Export Settings',payment_export_settings,'country')
        content += make_line("          <Ctry>" + country + "</Ctry>")
        content += make_line("        </PstlAdr>")
        content += make_line("        <Id>")                      
        content += make_line("        <OrgId>")
        content += make_line("        <Othr>")
        content += make_line("        <Id>556036867100</Id>")
        content += make_line("        <SchmeNm>")
        content += make_line("        <Cd>BANK</Cd>")
        content += make_line("        </SchmeNm>")
        content += make_line("        </Othr>")
        content += make_line("        </OrgId>")
        content += make_line("        </Id>")                                           
        content += make_line("      </Dbtr>")  
        content += make_line("      <DbtrAcct>")
        content += make_line("        <Id>")  
        iban = frappe.db.get_value('Payment Export Settings',payment_export_settings,'iban_for_domestic_payment')
        content += make_line("          <IBAN>{0}</IBAN>".format(iban.replace(" ", "") ))        
        content += make_line("        </Id>")
        content += make_line("      </DbtrAcct>")

        content += make_line("      <DbtrAgt>")
        content += make_line("        <FinInstnId>")
        bic = frappe.db.get_value('Payment Export Settings',payment_export_settings,'bic')
        content += make_line("      <BIC>{0}</BIC>".format(bic))

        content += make_line("        <PstlAdr>")
        content += make_line("          <Ctry>" + country + "</Ctry>")        
        content += make_line("        </PstlAdr>")
        content += make_line("        </FinInstnId>")
        content += make_line("      </DbtrAgt>")

        for payment in payments:
            frappe.db.set_value("Payment Entry" , payment , "custom_xml_file_generated" , 1)
            frappe.db.set_value("Payment Entry" , payment , "custom_include_in_xml_file" , 0)
            payment_record = frappe.get_doc('Payment Entry', payment)
            workflow_state = frappe.db.get_value("Payment Export Settings",payment_export_settings , 'workflow_state')
            if workflow_state:
                for d in payment_record.references:
                    if d.reference_doctype == 'Purchase Invoice':
                        PI_doc = frappe.get_doc('Purchase Invoice' , d.reference_name)
                        PI_doc.db_set("workflow_state" , workflow_state)
            payment_content = ""
            payment_content += make_line("      <CdtTrfTxInf>")
            payment_content += make_line("        <PmtId>")
            # instruction identification 
            payment_content += make_line("          <InstrId>INSTRID-" + payment + "</InstrId>")
            # end-to-end identification (should be used and unique within B-level; payment entry name)
            payment_content += make_line("          <EndToEndId>" + payment.replace('-',"") + "</EndToEndId>")
            payment_content += make_line("        </PmtId>")
            payment_content += make_line("        <Amt>")
            payment_content += make_line("          <InstdAmt Ccy=\"{0}\">{1:.2f}</InstdAmt>".format(
                payment_record.paid_from_account_currency,
                payment_record.paid_amount))
            payment_content += make_line("        </Amt>")
            chrgbr = frappe.db.get_value('Payment Export Settings',payment_export_settings,'chrgbr')
            payment_content += make_line("      <ChrgBr>{0}</ChrgBr>".format(chrgbr))
            payment_content += make_line("        <CdtrAgt>")
            payment_content += make_line("          <FinInstnId>")
            payment_content += make_line("          <ClrSysMmbId>")
            payment_content += make_line("          <ClrSysId>")
            cd = frappe.db.get_value('Payment Export Settings',payment_export_settings,'cd')
            payment_content += make_line("            <Cd>{0}</Cd>".format(cd))
            payment_content += make_line("          </ClrSysId>")
            supplier_bank_giro = frappe.db.get_value('Supplier', payment_record.party,'bank_giro_number')
            supplier_plush_giro = frappe.db.get_value("Supplier", payment_record.party , 'plus_giro_number')
            if supplier_bank_giro:
                cmmbidd = frappe.db.get_value('Payment Export Settings',payment_export_settings,'mmbid_for_bank_giro_number')
            if supplier_plush_giro:
                cmmbidd = frappe.db.get_value('Payment Export Settings',payment_export_settings,'mmbid_for_plus_giro_number')
            payment_content += make_line("            <MmbId>{0}</MmbId>".format(cmmbidd))
            payment_content += make_line("          </ClrSysMmbId>")
            payment_content += make_line("          </FinInstnId>")
            payment_content += make_line("        </CdtrAgt>")

            creditor_info = add_creditor_info(payment_record)
            if creditor_info:
                payment_content += creditor_info
            else:
                # no address found, skip entry (not valid)
                content += add_invalid_remark( _("{0}: no address (or country) found").format(payment) )
                skipped.append(payment)
                continue
            payment_content += make_line("        <CdtrAcct>")
            payment_content += make_line("          <Id>")
            payment_content += make_line("            <Othr>")
            supplier_bank_giro = frappe.db.get_value('Supplier', payment_record.party,'bank_giro_number')
            supplier_plus_giro = frappe.db.get_value('Supplier', payment_record.party,'plus_giro_number')
            if supplier_bank_giro:
                payment_content += make_line("              <Id>{0}</Id>".format(supplier_bank_giro.replace("-" , "").strip() if supplier_bank_giro else '' ))
                payment_content += make_line("            <SchmeNm>")
                payment_content += make_line("                <Prtry>BGNR</Prtry>")
                payment_content += make_line("            </SchmeNm>")
            elif supplier_plus_giro:
                payment_content += make_line("              <Id>{0}</Id>".format(supplier_plus_giro.replace("-" , "").strip() if supplier_plus_giro else '' ))
                payment_content += make_line("            <SchmeNm>")
                payment_content += make_line("                <Cd>BBAN</Cd>")
                payment_content += make_line("            </SchmeNm>")
            payment_content += make_line("            </Othr>")
            payment_content += make_line("          </Id>")
            payment_content += make_line("        </CdtrAcct>")
            payment_content += make_line("        <RmtInf>")
            for reference in payment_record.references:
                if ocr_number := frappe.db.get_value(reference.reference_doctype , reference.reference_name , 'ocr_number'):
                    payment_content += make_line("        <Strd>")
                    payment_content += make_line("              <RfrdDocAmt>")
                    payment_content += make_line("                  <RmtdAmt Ccy=\"{0}\">{1:.2f}</RmtdAmt>".format(payment_record.paid_from_account_currency,reference.allocated_amount))
                    payment_content += make_line("              </RfrdDocAmt>")
                    payment_content += make_line("              <CdtrRefInf>")
                    payment_content += make_line("                  <Tp>")
                    payment_content += make_line("                      <CdOrPrtry>")
                    payment_content += make_line("                          <Cd>SCOR</Cd>")
                    payment_content += make_line("                      </CdOrPrtry>")
                    payment_content += make_line("                  </Tp>")
                    payment_content += make_line("                  <Ref>{0}</Ref>".format(ocr_number))
                    payment_content += make_line("              </CdtrRefInf>")
                    payment_content += make_line("        </Strd>")
                else:
                    payment_content += make_line("        <Strd>")
                    payment_content += make_line("          <RfrdDocInf>")
                    payment_content += make_line("              <Tp>")
                    payment_content += make_line("                  <CdOrPrtry>")
                    payment_content += make_line("                      <Cd>CINV</Cd>")
                    payment_content += make_line("                  </CdOrPrtry>")
                    payment_content += make_line("              </Tp>")
                    if reference.reference_doctype in ["Purchase Invoice" , "Purchase Receipt"]:
                        bill_no = frappe.db.get_value(reference.reference_doctype , reference.reference_name , 'bill_no')
                    if reference.reference_doctype == "Purchase Order":
                        bill_no = reference.reference_name
                    payment_content += make_line("        <Nb>{0}</Nb>".format(bill_no))
                    payment_content += make_line("        </RfrdDocInf>")
                    payment_content += make_line("              <RfrdDocAmt>")
                    payment_content += make_line("                  <RmtdAmt Ccy=\"{0}\">{1:.2f}</RmtdAmt>".format(payment_record.paid_from_account_currency,reference.allocated_amount))
                    payment_content += make_line("              </RfrdDocAmt>")
                    payment_content += make_line("        </Strd>")
            payment_content += make_line("        </RmtInf>")

            payment_content += make_line("      </CdtTrfTxInf>")
            content += payment_content
            transaction_count += 1
            control_sum += payment_record.paid_amount

        content += make_line("    </PmtInf>")
        content += make_line("  </CstmrCdtTrfInitn>")
        content += make_line("</Document>")
        # insert control numbers
        content = content.replace(transaction_count_identifier, "{0}".format(transaction_count))
        content = content.replace(control_sum_identifier, "{:.2f}".format(control_sum))
        gen_payment_export_log(content, transaction_count, control_sum, payments, 'SEK')
        return { 'content': content, 'skipped': skipped }
    except IndexError:
        frappe.msgprint( _("Please select at least one payment."), _("Information") )
        return
    except:
        frappe.throw( _("Error while generating xml. Make sure that you made required customisations to the DocTypes.") )
        return

def add_creditor_info(payment_record):
    payment_content = ""
    # creditor information
    payment_content += make_line("        <Cdtr>") 
    # name of the creditor/supplier
    name = payment_record.party
    if payment_record.party_type == "Employee":
        name = frappe.get_value("Employee", payment_record.party, "employee_name")
    if payment_record.party_type == "Supplier":
        name = frappe.db.get_value("Supplier",name,"supplier_name")
        if '&' in name:
            new_name = name.replace('& ','')
            if new_name == name:
                new_name = name.replace('&',' ')
            name = new_name
    payment_content += make_line("          <Nm>" + name  + "</Nm>")
    # address of creditor/supplier (should contain at least country and first address line
    # get supplier address
    if payment_record.party_type == "Supplier" or payment_record.party_type == "Customer":
        supplier_address = get_billing_address(payment_record.party, payment_record.party_type)
        if supplier_address == None:
            return None
        street = get_street_name(supplier_address.address_line1)
        plz = supplier_address.pincode
        city = supplier_address.city 
        # country (has to be a two-digit code)
        try:
            country_code = frappe.get_value('Country', supplier_address.country, 'code').upper()
        except:
            country_code = "CH"
    elif payment_record.party_type == "Employee":
        employee = frappe.get_doc("Employee", payment_record.party)
        if employee.permanent_address:
           address = employee.permanent_address
        elif employee.current_address:
            address = employee.current_address
        else:
            # no address found
            return None
        try:
            lines = address.split("\n")
            street = "Street" #get_street_name(lines[0])
            building = "Building" #get_building_number(lines[0])
            plz = "PIN" #get_pincode(lines[1])
            city = "City" #get_city(lines[1])
            country_code = "CH"                
        except:
            # invalid address
            return None
    else:
        # unknown supplier type
        return None
    payment_content += make_line("          <PstlAdr>")
    # street name
    payment_content += make_line("            <StrtNm>" + street + "</StrtNm>")
    # postal code
    payment_content += make_line("            <PstCd>{0}</PstCd>".format(plz))
    # town name
    payment_content += make_line("            <TwnNm>" + city + "</TwnNm>")
    payment_content += make_line("            <Ctry>" + country_code + "</Ctry>")
    payment_content += make_line("            <AdrLine>" + street + "</AdrLine>")
    payment_content += make_line("          </PstlAdr>")
    payment_content += make_line("        </Cdtr>") 
    return payment_content
            
def get_total_amount(payments):
    # get total amount from all payments
    total_amount = float(0)
    for payment in payments:
        payment_amount = frappe.get_value('Payment Entry', payment, 'paid_amount')
        total_amount += payment_amount
        
    return total_amount

def get_company_name(payment_entry):
    return frappe.get_value('Payment Entry', payment_entry, 'company')

# adds Windows-compatible line endings (to make the xml look nice)    
def make_line(line):
    return line + "\r\n"

# add a remark if a payment entry was skipped
def add_invalid_remark(remark):
    return make_line("    <!-- " + remark + " -->")
    
# try to find the optimal billing address
def get_billing_address(supplier_name, supplier_type="Supplier"):
    if supplier_type == "Customer":
        linked_addresses = frappe.get_all('Dynamic Link', 
        filters={
            'link_doctype': 'customer', 
            'link_name': supplier_name, 
            'parenttype': 'Address'
        }, 
        fields=['parent'])         
    else:
        linked_addresses = frappe.get_all('Dynamic Link', 
        filters={
            'link_doctype': 'supplier', 
            'link_name': supplier_name, 
            'parenttype': 'Address'
        }, 
        fields=['parent'])     
    if len(linked_addresses) > 0:
        if len(linked_addresses) > 1:
            for address_name in linked_addresses:
                address = frappe.get_doc('Address', address_name.parent)            
                if address.address_type == "Billing":
                    # this is a billing address, keep as option
                    billing_address = address
                    if address.is_primary_address == 1:
                        # this is the primary billing address
                        return address
                if address.is_primary_address == 1:
                    # this is a primary but not billing address
                    primary_address = address
            # evaluate best address found
            if billing_address:
                # found one or more billing address (but no primary)
                return billing_address
            elif primary_address:
                # found no billing but a primary address
                return primary_address
            else:
                # found neither billing nor a primary address
                return frappe.get_doc('Address', linked_addresses[0].parent)
        else:
            # return the one (and only) address 
            return frappe.get_doc('Address', linked_addresses[0].parent)
    else:
        # no address found
        return None

def get_building_number(address_line):
    parts = address_line.strip().split(" ")
    if len(parts) > 1:
        return parts[-1]
    else:
        return ""

def get_street_name(address_line):
    parts = address_line.strip().split(" ")
    if len(parts) > 1:
        return " ".join(parts[:-1])
    else:
        return address_line

# get pincode from address line
def get_pincode(address_line):
    parts = address_line.strip().split(" ")
    if len(parts) > 1:
        return parts[0]
    else:
        return ""

# get city from address line
def get_city(address_line):
    parts = address_line.strip().split(" ")
    if len(parts) > 1:
        return " ".join(parts[1:])
    else:
        return address_line

# get primary address
# target types: Customer, Supplier, Company
@frappe.whitelist()
def get_primary_address(target_name, target_type="Customer"):
    sql_query = """SELECT 
            `tabAddress`.`address_line1`, 
            `tabAddress`.`address_line2`, 
            `tabAddress`.`pincode`, 
            `tabAddress`.`city`, 
            `tabAddress`.`county`,
            `tabAddress`.`country`, 
            UPPER(`tabCountry`.`code`) AS `country_code`, 
            `tabAddress`.`is_primary_address`
        FROM `tabDynamic Link` 
        LEFT JOIN `tabAddress` ON `tabDynamic Link`.`parent` = `tabAddress`.`name`
        LEFT JOIN `tabCountry` ON `tabAddress`.`country` = `tabCountry`.`name`
        WHERE `link_doctype` = '{type}' AND `link_name` = '{name}'
        ORDER BY `tabAddress`.`is_primary_address` DESC
        LIMIT 1;""".format(type=target_type, name=target_name)
    try:
        return frappe.db.sql(sql_query, as_dict=True)[0]
    except:
        return None

def genrate_file_for_sepa( payments ,payment_export_settings , posting_date , payment_type):
    payments = eval(payments)
    # remove empty items in case there should be any (bigfix for issue #2)
    payments = list(filter(None, payments))
    content = make_line("<?xml version='1.0' encoding='UTF-8'?>")
    content += make_line("<!-- SEB ISO 20022 V03 MIG, 6.1 SEPA CT IBAN ONLY -->")
    content += make_line("<Document xmlns='urn:iso:std:iso:20022:tech:xsd:pain.001.001.03' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance'>")
    content += make_line("  <CstmrCdtTrfInitn>")
    content += make_line("      <GrpHdr>")
    content += make_line("          <MsgId>{0}</MsgId>".format(time.strftime("%Y%m%d%H%M%S")))
    content += make_line("          <CreDtTm>{0}</CreDtTm>".format(time.strftime("%Y-%m-%dT%H:%M:%S")))
    transaction_count = 0
    transaction_count_identifier = "<!-- $COUNT -->"
    content += make_line("          <NbOfTxs>{0}</NbOfTxs>".format(transaction_count_identifier))
    control_sum = 0.0
    control_sum_identifier = "<!-- $CONTROL_SUM -->"
    content += make_line("          <CtrlSum>{0}</CtrlSum>".format(control_sum_identifier))
    content += make_line("          <InitgPty>")
    content += make_line("              <Nm>{0}</Nm>".format(get_company_name(payments[0])))
    content += make_line("              <Id>")
    content += make_line("                  <OrgId>")
    content += make_line("                      <Othr>")
    content += make_line("                          <Id>556036867100</Id>")
    content += make_line("                          <SchmeNm>")
    content += make_line("                              <Cd>BANK</Cd>")
    content += make_line("                          </SchmeNm>")
    content += make_line("                      </Othr>")
    content += make_line("                  </OrgId>")
    content += make_line("              </Id>")
    content += make_line("          </InitgPty>")
    content += make_line("      </GrpHdr>")
    content += make_line("      <PmtInf>")
    content += make_line("          <PmtInfId>{0}</PmtInfId>".format(payments[0]))
    content += make_line("          <PmtMtd>TRF</PmtMtd>")
    content += make_line("          <BtchBookg>false</BtchBookg>")
    content += make_line("          <NbOfTxs>{0}</NbOfTxs>".format(transaction_count_identifier))
    
    content += make_line("          <CtrlSum>{0}</CtrlSum>".format(control_sum_identifier))
    content += make_line("          <PmtTpInf>")
    content += make_line("              <SvcLvl>")
    content += make_line("                  <Cd>SEPA</Cd>")
    content += make_line("              </SvcLvl>")
    content += make_line("          </PmtTpInf>")
    required_execution_date = posting_date
    content += make_line("          <ReqdExctnDt>{0}</ReqdExctnDt>".format(required_execution_date))
    content += make_line("          <Dbtr>")
    company_name = frappe.db.get_value('Payment Export Settings',payment_export_settings,'company_name')
    content += make_line("              <Nm>{0}</Nm>".format(company_name))
    content += make_line("              <Id>")
    content += make_line("                  <OrgId>")
    content += make_line("                      <Othr>")
    content += make_line("                          <Id>55667755110004</Id>")
    content += make_line("                          <SchmeNm>")
    content += make_line("                              <Cd>BANK</Cd>")
    content += make_line("                          </SchmeNm>")
    content += make_line("                      </Othr>")
    content += make_line("                  </OrgId>")
    content += make_line("              </Id>")
    content += make_line("              <CtryOfRes>SE</CtryOfRes>")
    content += make_line("          </Dbtr>")
    content += make_line("          <DbtrAcct>")
    content += make_line("              <Id>")
    iban = frappe.db.get_value('Payment Export Settings',payment_export_settings,'iban_for_sepa_payment')
    content += make_line("                  <IBAN>{0}</IBAN>".format(iban))
    content += make_line("              </Id>")
    content += make_line("              <Ccy>EUR</Ccy>")
    content += make_line("          </DbtrAcct>")
    content += make_line("          <DbtrAgt>")
    content += make_line("          <!-- Note: For IBAN only on Debtor side use Othr/Id: NOTPROVIDED - see below -->")
    content += make_line("              <FinInstnId>")
    content += make_line("                  <Othr>")
    content += make_line("                      <Id>NOTPROVIDED</Id>")
    content += make_line("                  </Othr>")
    content += make_line("              </FinInstnId>")
    content += make_line("          </DbtrAgt>")
    content += make_line("          <ChrgBr>SLEV</ChrgBr>")
    for payment in payments:
        frappe.db.set_value("Payment Entry" , payment , "custom_xml_file_generated" , 1)
        frappe.db.set_value("Payment Entry" , payment , "custom_include_in_xml_file" , 0)
        payment_record = frappe.get_doc('Payment Entry', payment)
        workflow_state = frappe.db.get_value("Payment Export Settings",payment_export_settings , 'workflow_state')
        if workflow_state:
            for d in payment_record.references:
                if d.reference_doctype == 'Purchase Invoice': 
                    PI_doc = frappe.get_doc('Purchase Invoice' , d.reference_name)
                    PI_doc.db_set("workflow_state" , workflow_state)
        content += make_line("          <CdtTrfTxInf>")
        content += make_line("              <PmtId>")
        content += make_line("                  <InstrId>{}</InstrId>".format(payment))
        content += make_line("                  <EndToEndId>{}</EndToEndId>".format(payment.replace('-',"")))
        content += make_line("              </PmtId>")
        content += make_line("              <Amt>")
        content += make_line("                  <InstdAmt Ccy=\"{0}\">{1:.2f}</InstdAmt>".format(
                payment_record.paid_from_account_currency,
                payment_record.paid_amount))
        content += make_line("              </Amt>")
        content += make_line("              <!-- Note: Creditor Agent should not be used at all for IBAN only on Creditor side -->")
        content += make_line("              <Cdtr>")
        if payment_record.party_type == "Employee":
            name = frappe.get_value("Employee", payment_record.party, "employee_name")
        if payment_record.party_type == "Supplier":
            name = frappe.db.get_value("Supplier",payment_record.party,"supplier_name")
            if '&' in name:
                new_name = name.replace('& ','')
                if new_name == name:
                    new_name = name.replace('&',' ')
                name = new_name
        content += make_line("                  <Nm>{0}</Nm>".format(name))
        content += make_line("              </Cdtr>")
        content += make_line("              <CdtrAcct>")
        content += make_line("                  <Id>")
        iban_code = frappe.db.get_value("Supplier" , payment_record.party , 'iban_code')
        content += make_line("                      <IBAN>{0}</IBAN>".format(iban_code.strip() or ""))
        content += make_line("                  </Id>")
        content += make_line("              </CdtrAcct>")
        content += make_line("              <RmtInf>")
        sup_invoice_no = ''
        if payment_record.references[0].reference_doctype == "Purchase Invoice":
            sup_invoice_no = frappe.db.get_value("Purchase Invoice" , payment_record.references[0].reference_name , 'bill_no')
        content += make_line("                  <Ustrd>{0}</Ustrd>".format(sup_invoice_no if sup_invoice_no else ""))
        content += make_line("              </RmtInf>")
        content += make_line("          </CdtTrfTxInf>")
        transaction_count += 1
        control_sum += payment_record.paid_amount
    content += make_line("      </PmtInf>")
    content += make_line("  </CstmrCdtTrfInitn>")
    content += make_line("</Document>")
    content = content.replace(transaction_count_identifier, "{0}".format(transaction_count))
    content = content.replace(control_sum_identifier, "{:.2f}".format(control_sum))
    
    return content, transaction_count, control_sum

@frappe.whitelist()
def validate_master_data(payment_type):
    payments = frappe.db.sql(""" Select pe.name, pe.posting_date, pe.paid_amount, pe.party, pe.party_name, pe.paid_from, pe.paid_to_account_currency, per.reference_doctype , 
                                per.reference_name
                            From `tabPayment Entry` as pe 
                            Left Join `tabPayment Entry Reference` as per ON per.parent = pe.name
                            Where pe.docstatus = 0 and pe.payment_type = "Pay" and pe.party_type = "Supplier" and pe.custom_xml_file_generated = 0
                            order by posting_date
                            """,as_dict = 1)

    merged_data = defaultdict(list)
    for row in payments:
        key = row['name']
        merged_data[key].append(row['reference_name'])
    
    sorted_data = {}
    for key, values in merged_data.items():
        sorted_data.update({key:values}) 
    
    sort_list = []
    data = []
    for row in payments:
        if sorted_data.get(row.name):
            row.update({"reference_name":sorted_data.get(row.name)})
        if row.name not in sort_list:
            sort_list.append(row.name)
            data.append(row)
            
    _payments = []
    list_of_amount = []
    error_docs = []
    message = f'Address is missing in below suppliers<br>'
    for row in data:
        payment = frappe.get_doc('Payment Entry', row.name)
        creditor_info = add_creditor_info(payment)
        if not creditor_info:
            message += f"<p>{ get_link_to_form('Supplier',payment.party) }</p>"
            error_docs.append(row)
    if error_docs:
        frappe.throw(message)        


def gen_payment_export_log(content, total_no_of_payments, total_paid_amount, payments, currency = None):
    doc = frappe.new_doc('Payment Export Log')
    doc.file_creation_time = now()
    doc.user =  frappe.session.user
    doc.total_paid_amount = total_paid_amount
    doc.total_no_of_payments = total_no_of_payments
    doc.content = content
    doc.flags.ignore_permissions = 1
    for row in payments:
        pay_doc = frappe.get_doc('Payment Entry', row)
        doc.append('logs',{
            'payment_entry' : row,
            'supplier' : pay_doc.party,
            'supplier_name':pay_doc.party_name,
            'paid_amount' : pay_doc.paid_amount,
            'status' : pay_doc.status,
            'posting_date':pay_doc.posting_date,
            'document_type':pay_doc.references[0].reference_doctype,
            'purchase_doc_no':pay_doc.references[0].reference_name,
            'account':pay_doc.paid_from,
            'due_date' : frappe.db.get_value(pay_doc.references[0].reference_doctype, pay_doc.references[0].reference_name, 'due_date') if pay_doc.references[0].reference_doctype != "Purchase Order" else '',
            'delay' : (getdate() - frappe.db.get_value(pay_doc.references[0].reference_doctype, pay_doc.references[0].reference_name, 'due_date')).days if pay_doc.references[0].reference_doctype != "Purchase Order" else 0
        })
    if not currency:
        doc.currency = frappe.db.get_value("Payment Entry", pay_doc.get('payment_entry'), "paid_to_account_currency")
    else:
        doc.currency = currency 
    doc.save()
    frappe.enqueue(
            submit_all_payment_entry, doc=doc, queue="long", enqueue_after_commit=True
        )
    enable = frappe.db.get_value("Payment Export Settings", "PES0001", "generate_excel_file")
    if enable:
        import pandas as pd
        json_data = []
        for row in doc.logs:
            data_ = {}
            data_["Payment Entry"] = row.get('payment_entry')
            data_["Posting date"] = frappe.db.get_value("Payment Entry", row.get('payment_entry'), "posting_date")
            data_["Supplier"] = row.get('supplier')
            data_["Supplier Name"] = frappe.db.get_value("Supplier", row.get('supplier'), 'supplier_name')
            data_["Paid Amount"] = row.get('paid_amount')
            data_["Currency"] = frappe.db.get_value("Payment Entry", row.get('payment_entry'), "paid_to_account_currency")
            data_["document_type"] = row.get('document_type')
            data_["Purchase Invoice"] = row.get('purchase_doc_no')
            data_["Account"] = row.get('account')
            json_data.append(data_)
        # Json to DataFrame
        df = pd.DataFrame(json_data)
        # DataFrame to Excel
        excel_file_path = str(frappe.utils.get_bench_path())+"/sites/"+str(frappe.utils.get_site_base_path()[2:])+"/private/files/{0}.xlsx".format(doc.name)

        
        df.to_excel(excel_file_path, index=False) 
        frappe.db.commit()
        frappe.msgprint(f"Payment Export Log <b>{get_link_to_form('Payment Export Log', doc.name)}</b>")
        file_doc = frappe.new_doc("File")
        file_doc.is_private = 0
        file_doc.file_url = "/private/files/{0}.xlsx".format(doc.name)
        file_doc.attached_to_doctype = "Payment Export Log"
        file_doc.attached_to_name = doc.name
        file_doc.file_name = "{0}.xlsx".format(doc.name)
        file_doc.save()

def submit_all_payment_entry(doc):
    submitted_entry = []
    error_docs = []
    pay_log = frappe.get_doc("Payment Export Log", doc.name)
    for row in pay_log.logs:
        payment_entry = frappe.get_doc("Payment Entry", row.payment_entry)
        try:
            payment_entry.submit()
            submitted_entry.append(row.payment_entry)
        except:
            error_docs.append(row.payment_entry)
    
    
    msg_for_this_recipient = "Hi {0}".format(frappe.db.get_value("User", pay_log.owner, 'full_name'))
    msg_for_this_recipient += "<br><br>"
    msg_for_this_recipient += "<h2>Successfully Submitted Payment Entry</h2>"
    msg_for_this_recipient += """<table>"""
    for row in submitted_entry:
        msg_for_this_recipient +="""    <tr>
                                            <td>{0}<td>
                                        </tr> 
                                """.format(row)
    msg_for_this_recipient += "</table>"

    msg_for_this_recipient += "<br><br>"
    if error_docs:
        msg_for_this_recipient += "<h2></h2>"
        msg_for_this_recipient += "<table>"
        for row in error_docs:
            msg_for_this_recipient +="""    <tr>
                                                <td>{0}<td>
                                            </tr> 
                                    """.format(row)
        msg_for_this_recipient += "</table>"

    frappe.sendmail(
        recipients=pay_log.owner,
        subject = "Submitted Payment Entry Details(ERPnext)",
        message=msg_for_this_recipient,
    )
