"""Fictional demonstration case builder for LexVigil AI."""
import json
import time
from typing import Any, Dict
from sqlalchemy import text
from .cases import CaseManager
from .search_engine import CaseSearchIndex


DEMO_CASE_ID = "DEMO-CASE-APEX-METRO-2024"

DOC_AGREEMENT = """MASTER SERVICES AGREEMENT — CIVIL INFRASTRUCTURE
Section 4.2 Payment Period:
"Payment Period" shall mean thirty (30) calendar days from receipt of an undisputed tax invoice.
Section 8.1 Payment Obligation:
The Employer (Metro Rail Urban Development Corp.) shall pay the Contractor (Apex Infrastructure Ltd.) all certified progress invoices within the Payment Period defined in Section 4.2.
Section 12.4 Late-Payment Charge:
A statutory late-payment charge of 12% per annum applies to all sums remaining unpaid after thirty (30) calendar days from the invoice date.
Section 17.3 Amendment of Payment Terms:
By mutual supplementary accord dated 15 January 2024, the Payment Period defined in Section 4.2 is hereby amended from thirty (30) calendar days to forty-five (45) calendar days for all civil construction packages.
Section 22.1 Dispute Resolution:
All disputes arising out of or in connection with this contract shall be referred to arbitration seated in New Delhi under the Arbitration and Conciliation Act, 1996."""

DOC_INVOICE = """TAX INVOICE — APEX INFRASTRUCTURE LTD.
Invoice Number: INV-2024-884
Invoice Date: 15 March 2024
Customer: Metro Rail Urban Development Corp., Barakhamba Road, New Delhi.
Project: Underground Station Pier Construction — Package 3B.
Item 1: Milestone 3 Foundation Works (Certified by Engineer): INR 12,50,000
GST (18%): INR 2,25,000
Total Payable: INR 14,75,000 (Base Work Value: INR 12,50,000)
Due Date Recorded on Invoice: 14 April 2024 (Computed as 30 days).
Bank Details: State Bank of India, Commercial Branch, IFSC: SBIN0001234, Account: 9876543210."""

DOC_PAYMENT = """STATE BANK OF INDIA — RTGS REMITTANCE ADVICE
Transaction Reference (UTR): SBIN44018892314
Remittance Date: 10 May 2024
Remitter: Metro Rail Urban Development Corp. (Account No. 1122334455)
Beneficiary: Apex Infrastructure Ltd. (Account No. 9876543210)
Remitted Amount: INR 10,00,000 (Rupees Ten Lakh Only)
Narrative: Partial settlement against Invoice INV-2024-884 Milestone 3. Balance INR 2,50,000 retained subject to quality audit."""

DOC_DEMAND_NOTICE = """FORMAL LEGAL NOTICE OF DEFAULT & DEMAND
Date: 25 May 2024
To: The Managing Director, Metro Rail Urban Development Corp., New Delhi.
From: Legal Counsel for Apex Infrastructure Ltd.
Subject: Demand for balance payment of INR 2,50,000 with interest under Section 73 Indian Contract Act, 1872.
Take notice that Tax Invoice INV-2024-884 for INR 12,50,000 fell due on 29 April 2024 (giving full effect to the 45-day period under Section 17.3).
On 10 May 2024, your corporation remitted only INR 10,00,000, leaving an admitted shortfall of INR 2,50,000 without prior written notice or contractual sanction.
You are hereby called upon to pay the outstanding balance of INR 2,50,000 together with contractual interest within 15 days of this notice, failing which legal proceedings will be initiated."""

DOC_REPLY_NOTICE = """REPLY TO LEGAL NOTICE & STATEMENT OF DEFENCE
Date: 12 June 2024
(Transmitted via email timestamped 10 June 2024)
To: Apex Infrastructure Ltd., Counsel.
From: Metro Rail Urban Development Corp., Legal Directorate.
Subject: Rejection of demand regarding Invoice INV-2024-884.
1. The Corporation denies any default under the Master Agreement.
2. The deduction of INR 2,50,000 is an authorized retention under Section 14.1 due to discovered structural micro-cracks in Milestone 3 foundation piers.
3. Rectification costs incurred by the Corporation are preliminarily assessed at INR 3,00,000.
4. Without prejudice, the Corporation invites the Claimant to a joint inspection before any arbitral reference."""

DOC_JOINT_INSPECTION = """JOINT SITE INSPECTION & QUALITY CLEARANCE CERTIFICATE
Date: 10 March 2024
Location: Underground Station Pier 14-22.
Participants:
1. Mr. R. Sharma, Chief Resident Engineer, Metro Rail Urban Development Corp.
2. Mr. V. Patel, Project Director, Apex Infrastructure Ltd.
Findings:
The civil foundation concrete pour and 28-day compressive cube strength tests comply with Indian Standard IS 456:2000.
Milestone 3 works are hereby approved for commercial invoicing without defects or reservations."""


def load_fictional_demo_case(cm: CaseManager, owner: str) -> Dict[str, Any]:
    """Loads or resets the complete fictional payment dispute case for the user."""
    # First, safely clean any existing demo case for this owner to avoid duplicates
    existing = cm.get_case(DEMO_CASE_ID, owner)
    if existing:
        cm.delete_case(DEMO_CASE_ID, owner)

    now = time.time()
    # 1. Create Case
    with cm.db.begin() as con:
        con.execute(text("""
            INSERT INTO cases (id, owner, title, reference, category, parties_json, jurisdiction, court, description, status, tags_json, created_at, updated_at)
            VALUES (:id, :owner, :title, :reference, :category, :parties, :jurisdiction, :court, :description, 'active', :tags, :now, :now)
        """), {
            "id": DEMO_CASE_ID,
            "owner": owner,
            "title": "Apex Infrastructure Ltd. v. Metro Rail Urban Development Corp.",
            "reference": "ARB/2024/DEL/884",
            "category": "Commercial Civil Dispute (EPC Contract)",
            "parties": json.dumps(["Apex Infrastructure Ltd. (Contractor/Claimant)", "Metro Rail Urban Development Corp. (Employer/Respondent)"]),
            "jurisdiction": "New Delhi, India",
            "court": "Arbitral Tribunal / High Court of Delhi",
            "description": "Fictional civil payment dispute regarding unpaid balance of INR 2,50,000 under Milestone 3 civil works, involving conflicting payment amendment terms, partial payment withholding, and defect counterclaims.",
            "tags": json.dumps(["EPC", "Payment Dispute", "Section 73", "Arbitration", "Delayed Payment", "Demo"]),
            "now": now
        })

    # 2. Add Documents
    docs_to_add = [
        ("DOC-DEMO-01", "01_Master_Services_Agreement_2023.txt", "text/plain", len(DOC_AGREEMENT), DOC_AGREEMENT, "Agreement"),
        ("DOC-DEMO-02", "02_Tax_Invoice_INV_2024_884.txt", "text/plain", len(DOC_INVOICE), DOC_INVOICE, "Invoice"),
        ("DOC-DEMO-03", "03_Bank_Remittance_Advice_UTR_4401.txt", "text/plain", len(DOC_PAYMENT), DOC_PAYMENT, "Payment Record"),
        ("DOC-DEMO-04", "04_Demand_Notice_Section_73.txt", "text/plain", len(DOC_DEMAND_NOTICE), DOC_DEMAND_NOTICE, "Statutory Notice"),
        ("DOC-DEMO-05", "05_Respondent_Reply_Defect_Defense.txt", "text/plain", len(DOC_REPLY_NOTICE), DOC_REPLY_NOTICE, "Pleading / Reply"),
        ("DOC-DEMO-06", "06_Joint_Inspection_Clearance_Certificate.txt", "text/plain", len(DOC_JOINT_INSPECTION), DOC_JOINT_INSPECTION, "Inspection Certificate")
    ]

    for did, fname, ftype, fsize, ftext, fcat in docs_to_add:
        cm.add_document(DEMO_CASE_ID, owner, fname, ftype, fsize, ftext, [{"page": 1, "text": ftext}], {"category": fcat, "demo": True})

    # Fetch document IDs
    all_docs = cm.list_documents(DEMO_CASE_ID)
    doc_map = {d["filename"]: d["id"] for d in all_docs}

    # 3. Add Extracted Facts with Provenance
    facts_data = [
        (doc_map["01_Master_Services_Agreement_2023.txt"], 'Payment Period means 30 calendar days from receipt of an undisputed tax invoice', 'Metro Rail & Apex', 'Obligation', 'contract_clause', 1, 0.98),
        (doc_map["01_Master_Services_Agreement_2023.txt"], 'Payment Period amended from 30 days to 45 calendar days for all civil construction packages', 'Metro Rail & Apex', 'Amendment', 'contract_clause', 1, 0.95),
        (doc_map["01_Master_Services_Agreement_2023.txt"], 'Late-payment charge of 12% applies after 30 days from invoice date', 'Metro Rail', 'Obligation', 'contract_clause', 1, 0.90),
        (doc_map["02_Tax_Invoice_INV_2024_884.txt"], 'Milestone 3 Foundation Works billed at base value INR 12,50,000 on 15 March 2024', 'Apex Infrastructure Ltd.', 'Payment', 'invoice_billed', 1, 0.99),
        (doc_map["02_Tax_Invoice_INV_2024_884.txt"], 'Invoice records due date as 14 April 2024 based on 30-day formula', 'Apex Infrastructure Ltd.', 'Temporal', 'due_date', 1, 0.88),
        (doc_map["03_Bank_Remittance_Advice_UTR_4401.txt"], 'Metro Rail paid INR 10,00,000 via RTGS on 10 May 2024', 'Metro Rail Corp.', 'Payment', 'payment_made', 1, 0.99),
        (doc_map["03_Bank_Remittance_Advice_UTR_4401.txt"], 'Balance of INR 2,50,000 retained subject to quality audit', 'Metro Rail Corp.', 'Disputed Fact', 'retention', 1, 0.92),
        (doc_map["04_Demand_Notice_Section_73.txt"], 'Demand notice issued claiming INR 2,50,000 plus interest under Section 73 Indian Contract Act', 'Apex Counsel', 'Communication', 'demand_notice', 1, 0.95),
        (doc_map["05_Respondent_Reply_Defect_Defense.txt"], 'Respondent asserts structural micro-cracks and claims rectification costs of INR 3,00,000', 'Metro Rail Corp.', 'Claim', 'allegation', 1, 0.85),
        (doc_map["06_Joint_Inspection_Clearance_Certificate.txt"], 'Joint Site Inspection approved Milestone 3 works without defects on 10 March 2024', 'Joint Inspection Team', 'Event', 'inspection_clearance', 1, 0.98)
    ]

    for doc_id, text_span, entity, cat, ftype, page, conf in facts_data:
        cm.add_fact(DEMO_CASE_ID, doc_id, text_span, entity, cat, ftype, page, 0, len(text_span), "confirmed", conf)

    # 4. Add Evidence Items
    ev1 = cm.add_evidence_item(DEMO_CASE_ID, "Master Services Agreement (Payment Clauses §4.2, §17.3)", "Contract", "Contract defining 30-day initial term and 45-day amendment.", doc_map["01_Master_Services_Agreement_2023.txt"], 1)
    ev2 = cm.add_evidence_item(DEMO_CASE_ID, "Tax Invoice #INV-2024-884 for INR 12,50,000", "Invoice", "Original certified invoice submitted on 15 March 2024.", doc_map["02_Tax_Invoice_INV_2024_884.txt"], 1)
    ev3 = cm.add_evidence_item(DEMO_CASE_ID, "Bank Remittance Receipt for INR 10,00,000", "Payment", "Official bank proof showing partial payment on 10 May 2024.", doc_map["03_Bank_Remittance_Advice_UTR_4401.txt"], 1)
    ev4 = cm.add_evidence_item(DEMO_CASE_ID, "Statutory Demand Notice (25 May 2024)", "Communication", "Formal demand for unpaid balance of INR 2,50,000.", doc_map["04_Demand_Notice_Section_73.txt"], 1)
    ev5 = cm.add_evidence_item(DEMO_CASE_ID, "Respondent Reply Alleging Defective Works", "Pleading", "Letter alleging foundation micro-cracks and defect claim.", doc_map["05_Respondent_Reply_Defect_Defense.txt"], 1)
    ev6 = cm.add_evidence_item(DEMO_CASE_ID, "Joint Site Inspection Certificate (10 March 2024)", "Certificate", "Engineer sign-off confirming zero defects prior to invoice.", doc_map["06_Joint_Inspection_Clearance_Certificate.txt"], 1)

    # 5. Add Evidence Relationships (with graph edges)
    cm.add_evidence_relationship(DEMO_CASE_ID, ev1["id"], ev2["id"], "governs", "Agreement §4.2 and §17.3 govern payment obligations of Invoice INV-2024-884.")
    cm.add_evidence_relationship(DEMO_CASE_ID, ev2["id"], ev3["id"], "partially_satisfied_by", "Invoice was for INR 12,50,000; remittance was only INR 10,00,000.")
    cm.add_evidence_relationship(DEMO_CASE_ID, ev3["id"], ev4["id"], "triggered", "Unilateral shortfall of INR 2,50,000 directly provoked formal legal demand notice.")
    cm.add_evidence_relationship(DEMO_CASE_ID, ev4["id"], ev5["id"], "responded_by", "Reply notice refutes default and asserts defect counter-claim.")
    cm.add_evidence_relationship(DEMO_CASE_ID, ev6["id"], ev5["id"], "contradicts", "Clearance Certificate proves works were signed off with zero defects two months before alleged cracks.")
    cm.add_evidence_relationship(DEMO_CASE_ID, ev6["id"], ev2["id"], "supports", "Joint inspection clearance establishes entitlement to bill Milestone 3.")

    # 6. Add Timeline Events
    timeline = [
        ("2024-01-15", "Payment Term Amendment Signed", "Parties sign supplementary accord §17.3 extending payment period to 45 days.", doc_map["01_Master_Services_Agreement_2023.txt"], "Apex & Metro Rail", "verified"),
        ("2024-03-10", "Joint Inspection Clearance", "Resident engineers approve foundation works and sign clearance certificate IS 456.", doc_map["06_Joint_Inspection_Clearance_Certificate.txt"], "Joint Site Team", "verified"),
        ("2024-03-15", "Invoice INV-2024-884 Issued", "Apex issues Milestone 3 invoice for base value INR 12,50,000.", doc_map["02_Tax_Invoice_INV_2024_884.txt"], "Apex Infrastructure", "verified"),
        ("2024-04-14", "Unamended 30-Day Deadline", "Date indicated on invoice header as due date under unamended Clause 4.2.", doc_map["02_Tax_Invoice_INV_2024_884.txt"], "Apex Infrastructure", "unverified"),
        ("2024-04-29", "Amended 45-Day Deadline", "Effective contractual deadline under active amendment Clause 17.3.", doc_map["01_Master_Services_Agreement_2023.txt"], "Both Parties", "verified"),
        ("2024-05-10", "Partial Remittance (INR 10,00,000)", "Metro Rail transfers INR 10,00,000 withholding INR 2,50,000.", doc_map["03_Bank_Remittance_Advice_UTR_4401.txt"], "Metro Rail Corp.", "verified"),
        ("2024-05-25", "Legal Demand Notice Served", "Apex serves statutory notice demanding INR 2,50,000 balance plus interest.", doc_map["04_Demand_Notice_Section_73.txt"], "Apex Counsel", "verified"),
        ("2024-06-10", "Reply Email Transmitted", "Metro Rail transmits reply rejecting claim (email delivery date).", doc_map["05_Respondent_Reply_Defect_Defense.txt"], "Metro Rail Corp.", "verified"),
        ("2024-06-12", "Reply Notice Internal Date", "Internal date written on the physical letterhead of the Respondent reply.", doc_map["05_Respondent_Reply_Defect_Defense.txt"], "Metro Rail Corp.", "unverified")
    ]

    for dt, title, desc, doc_id, party, vstatus in timeline:
        cm.add_timeline_event(DEMO_CASE_ID, dt, title, desc, doc_id, party, vstatus)

    # 7. Add Inconsistencies
    cm.add_inconsistency(
        DEMO_CASE_ID, "Amount Discrepancy", "Unilateral Payment Deduction (INR 2,50,000)",
        "Tax Invoice INV-2024-884 is for INR 12,50,000 base amount, whereas Bank Remittance SBIN44018892314 confirms payment of only INR 10,00,000. An unexplained deficit of INR 2,50,000 remains unpaid.",
        ev2["id"], ev3["id"], "HIGH", "flagged"
    )
    cm.add_inconsistency(
        DEMO_CASE_ID, "Temporal Conflict", "Conflicting Due Date Formulas (30 vs 45 Days)",
        "Invoice printed due date is 14 April 2024 (using 30-day clause §4.2), while active amendment §17.3 specifies 45 calendar days (yielding 29 April 2024).",
        ev1["id"], ev2["id"], "MEDIUM", "flagged"
    )
    cm.add_inconsistency(
        DEMO_CASE_ID, "Factual Contradiction", "Quality Clearance vs Subsequent Defect Allegation",
        "Joint Inspection Certificate of 10 March 2024 certified zero defects and approved commercial invoicing, directly contradicting Respondent's reply alleging micro-cracks.",
        ev6["id"], ev5["id"], "HIGH", "flagged"
    )
    cm.add_inconsistency(
        DEMO_CASE_ID, "Date Discrepancy", "Notice Transmission Date Divergence",
        "Reply notice physical header states 12 June 2024, but electronic transmission metadata indicates 10 June 2024.",
        ev5["id"], ev5["id"], "LOW", "resolved"
    )

    # 8. Add Reasoning Rules
    cm.db.begin()
    with cm.db.begin() as con:
        con.execute(text("""
            INSERT INTO reasoning_rules (id, case_id, name, description, rule_json, created_at)
            VALUES (:id, :case_id, :name, :description, :rule_json, :now)
        """), {
            "id": "RULE-PAYMENT-DEFAULT",
            "case_id": DEMO_CASE_ID,
            "name": "Unjustified Payment Shortfall",
            "description": "If base amount is due under a certified invoice and payment is less than amount due without contract approval, flag default.",
            "rule_json": json.dumps({
                "premises": [
                    {"predicate": "invoice_billed", "args": ["?inv", "?billed_amt"]},
                    {"predicate": "payment_made", "args": ["?inv", "?paid_amt"]}
                ],
                "conclusion": {"predicate": "outstanding_balance", "args": ["?inv", "inr_2_50_000"]}
            }),
            "now": now
        })
        con.execute(text("""
            INSERT INTO reasoning_rules (id, case_id, name, description, rule_json, created_at)
            VALUES (:id, :case_id, :name, :description, :rule_json, :now)
        """), {
            "id": "RULE-DEFECT-ESTOPPEL",
            "case_id": DEMO_CASE_ID,
            "name": "Estoppel by Prior Certification",
            "description": "If works were approved by joint clearance certificate prior to billing, employer is estopped from asserting pre-existing defects without fresh inspection.",
            "rule_json": json.dumps({
                "premises": [
                    {"predicate": "inspection_clearance", "args": ["?work", "zero_defects"]},
                    {"predicate": "allegation", "args": ["?work", "?defect"]}
                ],
                "conclusion": {"predicate": "defect_claim_barred", "args": ["?work"]}
            }),
            "now": now
        })

    # 9. Add Arguments and Counterarguments
    cm.add_argument(
        DEMO_CASE_ID, "Contractual Entitlement to Balance INR 2,50,000",
        "Claimant is contractually entitled to the unpaid balance of INR 2,50,000 under Clause 8.1 and Section 73 Indian Contract Act, 1872. The works were certified by the Resident Engineer on 10 March 2024.",
        [ev1["id"], ev2["id"], ev3["id"], ev6["id"]],
        "Works were performed in accordance with specifications; Joint Inspection Certificate reflects true condition.",
        "Respondent claims right of equitable set-off under common law for structural defects discovered subsequently.",
        "verified"
    )
    cm.add_argument(
        DEMO_CASE_ID, "Rejection of Defect Counterclaim",
        "Respondent's defect defense is barred by estoppel and delay. Having signed the Joint Clearance Certificate IS 456 on 10 March 2024 and accepted the pier structures, Respondent cannot unilaterally withhold funds three months later.",
        [ev6["id"], ev5["id"]],
        "Joint Inspection was conclusive for milestone payment purposes.",
        "Respondent argues latent structural defects manifest only during curing over 90 days.",
        "proposed"
    )

    # 10. Add Legal Authorities
    cm.add_authority(
        DEMO_CASE_ID, "Indian Contract Act, 1872 — Section 73",
        "Sec. 73, Indian Contract Act (9 of 1872)", "India (Central)", "Statute",
        "https://www.indiacode.nic.in/handle/123456789/2187",
        "Governs compensation for breach of contract causing loss or damage naturally arising in the usual course of things.",
        "verified"
    )
    cm.add_authority(
        DEMO_CASE_ID, "Arbitration and Conciliation Act, 1996 — Section 9 & 11",
        "Sec. 9 & 11, Act 26 of 1996", "India (Central)", "Statute",
        "https://www.indiacode.nic.in/handle/123456789/1978",
        "Interim measures by Court and appointment of arbitrators for commercial disputes.",
        "verified"
    )
    cm.add_authority(
        DEMO_CASE_ID, "Mahanagar Telephone Nigam Ltd. v. Tata Communications Ltd. (2019)",
        "(2019) 5 SCC 341", "Supreme Court of India", "Judicial Precedent",
        "",
        "Holdings on unilateral deductions without contractual mechanism and requirement of liquidated damages proof.",
        "verified"
    )

    # 11. Add Saved Analysis
    cm.save_case_analysis(
        DEMO_CASE_ID, owner, "case_strategy_report", "Comprehensive Case Preparation Brief",
        {
            "case_id": DEMO_CASE_ID,
            "title": "Strategy Brief: Apex Infrastructure Ltd. v. Metro Rail Corp.",
            "summary": "Civil claim for INR 2,50,000 principal plus 12% interest. Strong affirmative evidence supported by Joint Clearance Certificate. Primary counter-risk is Respondent's latent defect defense.",
            "evidence_count": 6,
            "inconsistencies_flagged": 3,
            "recommended_next_steps": [
                "Issue Section 21 notice invoking arbitration under Clause 22.1.",
                "File Section 9 petition if Respondent attempts to encash performance bank guarantees.",
                "Seek appointment of independent structural expert from IIT Delhi to refute latent defect allegations."
            ]
        }
    )

    return cm.get_case(DEMO_CASE_ID, owner)
