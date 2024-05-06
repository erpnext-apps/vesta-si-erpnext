import frappe
from vesta_si_erpnext.vesta_si_erpnext.page.payment_export.payment_export import make_line
from frappe import throw, _
from collections import defaultdict
import time
#from erpnextswiss.erpnextswiss.common_functions import get_building_number, get_street_name, get_pincode, get_city
import html              # used to escape xml content
from frappe.utils import flt, get_link_to_form, getdate, nowdate, now
from datetime import datetime

def get_cross_border_xml_file(payments ,payment_export_settings , posting_date , payment_type):
    payments = eval(payments)
    payments = list(filter(None, payments))

    content = make_line('<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.001.001.03" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="urn:iso:std:iso:20022:tech:xsd:pain.001.001.03 pain.001.001.03.xsd">')
    content += make_line("<CstmrCdtTrfInitn>")
    content += make_line("<GrpHdr>")
    content += make_line("  <MsgId>{0}</MsgId>".format(time.strftime("%Y%m%d%H%M%S")))
    content += make_line("  <CreDtTm>{0}</CreDtTm>".format(time.strftime("%Y-%m-%dT%H:%M:%S")))
    transaction_count = 0
    transaction_count_identifier = "<!-- $COUNT -->"
    
    content += make_line("  <NbOfTxs>{0}</NbOfTxs>".format(transaction_count_identifier))
    control_sum = 0.0
    control_sum_identifier = "<!-- $CONTROL_SUM -->"
    content += make_line("      <CtrlSum>{0}</CtrlSum>".format(control_sum_identifier))
    content += make_line("      <InitgPty>")
    content += make_line("      <Nm>{0}</Nm>".format(get_company_name(payments[0])))
    content += make_line("      <Id>")
    content += make_line("      <OrgId>")
    content += make_line("          <Othr>")
    content += make_line("              <Id>556036867100</Id>")
    content += make_line("              <SchmeNm>")
    content += make_line("                  <Cd>BANK</Cd>")
    content += make_line("              </SchmeNm>")
    content += make_line("          </Othr>")
    content += make_line("      </OrgId>")
    content += make_line("      </Id>")
    content += make_line("      </InitgPty>")
    content += make_line("</GrpHdr>")

    #payment info
    content += make_line("      <PmtInf>")
    content += make_line("          <PmtInfId>{0}</PmtInfId>".format(payments[0]))
    content += make_line("          <PmtMtd>TRF</PmtMtd>")
    content += make_line("          <NbOfTxs>{0}</NbOfTxs>".format(transaction_count_identifier))
    content += make_line("          <CtrlSum>{0}</CtrlSum>".format(control_sum_identifier))
    content += make_line("          <PmtTpInf>")
    content += make_line("              <SvcLvl>")
    content += make_line("                  <Cd>URGP</Cd>")
    content += make_line("              </SvcLvl>")
    content += make_line("          </PmtTpInf>")
    required_execution_date = posting_date
    content += make_line("          <ReqdExctnDt>{0}</ReqdExctnDt>".format(required_execution_date))
    
    #Dbtr
    content += make_line("          <Dbtr>")
    company_name = frappe.db.get_value('Payment Export Settings',payment_export_settings,'company_name')
    PES = frappe.get_doc('Payment Export Settings', payment_export_settings)

    content += make_line("              <Nm>{0}</Nm>".format(company_name))
    content += make_line("                  <PstlAdr>")
    content += make_line(f"                       <StrtNm>{PES.street_name}</StrtNm>")
    content += make_line("                       <PstCd>{0}</PstCd>".format(PES.post_code))
    content += make_line("                       <TwnNm>{0}</TwnNm>".format(PES.town_name))
    content += make_line("                       <Ctry>{0}</Ctry>".format(PES.country))
    content += make_line("                  </PstlAdr>")
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
    content += make_line("          </Dbtr>")
    content += make_line("          <DbtrAcct>")
    content += make_line("              <Id>")
    iban = frappe.db.get_value('Payment Export Settings',payment_export_settings,'iban_for_cross_border_payment') #new field
    if not iban: 
        frappe.throw("Please update <b>'Iban For Cross Border Payment'</b> in {0}".format(f"<a href='https://erpnext-skf-9150.frappe.cloud/app/payment-export-settings/{payment_export_settings}'>Payment Export Settings</a>"))
    bank_bic = frappe.db.get_value('Payment Export Settings',payment_export_settings,'bic') 
    content += make_line("                  <IBAN>{0}</IBAN>".format(iban))
    content += make_line("              </Id>")
    content += make_line("          </DbtrAcct>")
    content += make_line("          <DbtrAgt>")
    content += make_line("                 <FinInstnId>")
    content += make_line("                      <BIC>{0}</BIC>".format(bank_bic if bank_bic else ''))
    content += make_line("                      <PstlAdr>")
    content += make_line("                          <Ctry>SE</Ctry>")
    content += make_line("                      </PstlAdr>")
    content += make_line("                  </FinInstnId>")
    content += make_line("           </DbtrAgt>")
 
    for payment in payments:
        frappe.db.set_value("Payment Entry" , payment , "custom_xml_file_generated" , 1)
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
                frappe.db.get_value(payment_record.references[0].reference_doctype,payment_record.references[0].reference_name,"currency" ),
                payment_record.received_amount))
        content += make_line("              </Amt>")
        content += make_line("              <ChrgBr>DEBT</ChrgBr>")

        bank_bic = frappe.db.get_value('Supplier', payment_record.party, "bank_bic")

        content += make_line("              <CdtrAgt>")
        content += make_line("                  <FinInstnId>")
        content += make_line("                      <BIC>{0}</BIC>".format(bank_bic if bank_bic else ''))
        content += make_line("                      <Nm>{0}</Nm>".format(payment_record.party))
        content += make_line("                  </FinInstnId>")
        content += make_line("              </CdtrAgt>")


        content += make_line("              <!-- Note: Creditor Agent should not be used at all for IBAN only on Creditor side -->")
        
        if payment_record.party_type == "Employee":
            name = frappe.get_value("Employee", payment_record.party, "employee_name")
        if payment_record.party_type == "Supplier":
            name = frappe.db.get_value("Supplier",payment_record.party,"supplier_name")
            if '&' in name:
                new_name = name.replace('& ','')
                if new_name == name:
                    new_name = name.replace('&',' ')
                name = new_name
        content += make_line("<Cdtr>")
        content += make_line("<Nm>{0}</Nm>".format(name))

        addr = get_supplier_address(payment_record.party)

        content += make_line("<PstlAdr>")
        content += make_line("  <StrtNm>{0}</StrtNm>".format(addr.address_line1 if addr.address_line1 else ''))
        content += make_line("  <PstCd>{0}</PstCd>".format(addr.pincode if addr.pincode else ''))
        content += make_line("  <TwnNm>{0}</TwnNm>".format(addr.city if addr.city else ''))
        content += make_line("  <Ctry>{0}</Ctry>".format(addr.country if addr.country else ''))
        content += make_line("  <AdrLine>{0}</AdrLine>".format(addr.address_line2 if addr.address_line2 else ''))
        content += make_line("  </PstlAdr>")
        content += make_line("      <Id>")
        content += make_line("          <OrgId>")
        content += make_line("              <Othr>")
        content += make_line("              <Id>0008001879</Id>")
        content += make_line("              <!--  Vendor ID from system  -->")
        content += make_line("              </Othr>")
        content += make_line("          </OrgId>")
        content += make_line("      </Id>")
        content += make_line("</Cdtr>")
        

        iban_code = frappe.db.get_value("Supplier" , payment_record.party , 'iban_code')
        bban_code = frappe.db.get_value("Supplier" , payment_record.party , 'bank_code')
        if iban_code:
            content += make_line("<CdtrAcct>")
            content += make_line("  <Id>")
            content += make_line("      <IBAN>{0}</IBAN>".format(iban_code.strip() or ""))
            content += make_line("  </Id>")
            content += make_line("<Nm>{0}</Nm>".format(name))
            content += make_line("</CdtrAcct>")
        if not iban_code and bban_code:
            content += make_line("<CdtrAcct>")
            content += make_line("  <Id>")
            content += make_line("  <Othr>")
            content += make_line("      <Id>{0}</Id>".format(bban_code))
            content += make_line("          <SchmeNm>")
            content += make_line("              <Cd>BBAN</Cd>")
            content += make_line("          </SchmeNm>")
            content += make_line("      </Othr>")
            content += make_line("  </Id>")
            content += make_line("  <Nm>Fischer Connectors Ltd</Nm>")
            content += make_line("</CdtrAcct>")
        content += make_line("<RgltryRptg>")
        content += make_line("  <DbtCdtRptgInd>DEBT</DbtCdtRptgInd>")
        content += make_line("  <Dtls>")
        content += make_line("  <Cd>101</Cd>")
        content += make_line("  </Dtls>")
        content += make_line("</RgltryRptg>")
        content += make_line("              <RmtInf>")
        sup_invoice_no = ''
        if payment_record.references[0].reference_doctype == "Purchase Invoice":
            sup_invoice_no = frappe.db.get_value("Purchase Invoice" , payment_record.references[0].reference_name , 'bill_no')
        content += make_line("                  <Ustrd>{0}</Ustrd>".format(sup_invoice_no if sup_invoice_no else ""))
        content += make_line("              </RmtInf>")
        content += make_line("          </CdtTrfTxInf>")
        transaction_count += 1
        control_sum += payment_record.received_amount
    content += make_line("      </PmtInf>")
    content += make_line("  </CstmrCdtTrfInitn>")
    content += make_line("</Document>")
    content = content.replace(transaction_count_identifier, "{0}".format(transaction_count))
    content = content.replace(control_sum_identifier, "{:.2f}".format(control_sum))
    
    return content, transaction_count, control_sum

def get_company_name(payment_entry):
    return frappe.get_value('Payment Entry', payment_entry, 'company')

def get_supplier_address(party):
    addr_name = frappe.db.get_value('Dynamic Link', {"link_doctype":"Supplier", 'link_name':party }, ['parent'])
    addr_doc = frappe.get_doc('Address', addr_name)
    return addr_doc