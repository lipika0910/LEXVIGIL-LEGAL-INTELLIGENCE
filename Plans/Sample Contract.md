# SAMPLE CONTRACT 01 — SOFTWARE SERVICES AGREEMENT

## Purpose
Synthetic test contract for LexVigil: payment-term contradiction through a cross-reference and amendment.

## 1. Definitions
### 1.1 Payment Period
"Payment Period" means thirty (30) calendar days from the date of receipt of a valid invoice.

### 1.2 Business Day
"Business Day" means Monday through Friday, excluding public holidays.

## 2. Invoicing
### 2.1 Invoice Date
The Service Provider may issue an invoice upon completion of each monthly service period.

### 2.2 Payment Obligation
The Customer shall pay each undisputed invoice within the Payment Period.

## 3. Late Payment
### 3.1 Late Charges
Any amount not paid within thirty (30) days after receipt of a valid invoice shall be considered overdue and shall accrue interest at 1% per month.

## 4. Amendments
### 4.1 Amendment to Payment Period
With effect from 1 January 2027, the "Payment Period" defined in Section 1.1 is amended from thirty (30) days to forty-five (45) calendar days.

## 5. General
### 5.1 Continuing Effect
Except as expressly amended by this Agreement, all other provisions remain unchanged.

## Expected LexVigil Finding
Potential temporal contradiction: Section 4.1 changes the effective Payment Period to 45 days, while Section 3.1 retains a 30-day overdue/interest trigger.


# SAMPLE CONTRACT 02 — CONSULTING AGREEMENT

## Purpose
Synthetic test contract for incompatible liability caps.

## 1. Definitions
### 1.1 Aggregate Liability
"Aggregate Liability" means the maximum amount payable by either party for all claims arising under or in connection with this Agreement.

## 2. Limitation of Liability
### 2.1 General Cap
Except for claims expressly excluded below, each party's total aggregate liability shall not exceed INR 10,00,000 (Ten Lakh Rupees).

### 2.2 Exceptions
The cap in Section 2.1 does not apply to fraud, wilful misconduct, or breach of confidentiality.

## 3. Confidentiality
### 3.1 Confidentiality Liability
Notwithstanding Section 2.2, liability for any breach of confidentiality shall be limited to INR 5,00,000.

## 4. Amendment
### 4.1 Revised Aggregate Liability
The parties agree that "Aggregate Liability" is amended to INR 25,00,000 for all claims under this Agreement.

## Expected LexVigil Finding
Potential scope/precedence contradiction: Section 4.1 changes the aggregate cap to INR 25,00,000, while Section 3.1 independently sets confidentiality liability at INR 5,00,000 and uses "Notwithstanding Section 2.2".


# SAMPLE CONTRACT 03 — DISTRIBUTION AGREEMENT

## Purpose
Synthetic test contract for conflicting termination notice periods.

## 1. Definitions
### 1.1 Agreement
"Agreement" means this Distribution Agreement and all schedules and amendments.

## 2. Term
### 2.1 Initial Term
The Agreement begins on 1 April 2027 and continues for three years unless terminated earlier under this Agreement.

## 3. Termination
### 3.1 Convenience Termination
Either party may terminate this Agreement for convenience by giving sixty (60) days' prior written notice.

### 3.2 Immediate Termination
Either party may terminate immediately for a material uncured breach.

## 4. Renewal
### 4.1 Renewal Notice
A party that does not wish to renew shall provide ninety (90) days' written notice before expiry of the Initial Term.

## 5. Amendment
### 5.1 Revised Termination Notice
The parties amend Section 3.1 so that either party may terminate for convenience upon thirty (30) days' prior written notice.

## Expected LexVigil Finding
Potential semantic conflict: Section 5.1 amends convenience termination to 30 days, but Section 4.1 requires 90 days to avoid renewal. A correct system should distinguish termination during the term from non-renewal at expiry rather than automatically treating them as contradictory.


# SAMPLE CONTRACT 04 — PROCUREMENT AGREEMENT

## Purpose
Synthetic test for nested defined-term inconsistency.

## 1. Definitions
### 1.1 Working Day
"Working Day" means any day on which banks are open for business in Bengaluru.

### 1.2 Delivery Day
"Delivery Day" means a Working Day.

### 1.3 Notice Day
"Notice Day" means a calendar day.

## 2. Delivery
### 2.1 Delivery Deadline
The Supplier shall deliver the Goods within five (5) Delivery Days after receipt of the purchase order.

## 3. Notice
### 3.1 Delay Notice
The Supplier shall notify the Buyer within two (2) Notice Days after becoming aware of a delay.

## 4. Amendment
### 4.1 Revised Working Day
For purposes of this Agreement, "Working Day" shall mean any calendar day other than Sunday.

## Expected LexVigil Finding
Defined-term propagation change: Section 4.1 changes the meaning of Working Day, which transitively changes Delivery Day under Section 1.2 and therefore changes the effective interpretation of Section 2.1.


# SAMPLE CONTRACT 05 — CLOUD HOSTING AGREEMENT

## Purpose
Synthetic test for a general obligation versus an exception.

## 1. Security
### 1.1 Security Controls
The Provider shall maintain encryption at rest and in transit for all Customer Data.

## 2. Data Residency
### 2.1 Approved Regions
Customer Data shall be stored only in India, Singapore, or Germany.

## 3. Backup
### 3.1 Backup Location
All backups shall be stored only in India.

### 3.2 Disaster Recovery Exception
Notwithstanding Section 3.1, during a declared disaster-recovery event, the Provider may store encrypted backup copies in any country where an approved disaster-recovery facility is available.

## 4. Data Residency Amendment
### 4.1 New Residency Rule
With effect from 1 July 2027, Section 2.1 is amended so that Customer Data shall be stored only in India.

## Expected LexVigil Finding
Potential exception/general-rule interaction: Section 3.2 permits backup storage outside India during disaster recovery, while amended Section 2.1 restricts Customer Data storage to India. LexVigil should preserve the "Notwithstanding" relationship and classify this as an exception interaction rather than a simple duplicate-value conflict.


# SAMPLE CONTRACT 06 — MASTER SERVICES AGREEMENT

## Purpose
Synthetic test for an invalid or misdirected cross-reference.

## 1. Scope
### 1.1 Services
The Provider shall perform the Services described in Schedule A.

## 2. Acceptance
### 2.1 Acceptance Criteria
Acceptance shall be determined according to the criteria in Section 4.2.

### 2.2 Acceptance Window
The Customer shall have ten (10) Business Days to test the Deliverables.

## 3. Payment
### 3.1 Payment Trigger
Payment becomes due after acceptance under Section 2.1.

## 4. General
### 4.1 Business Days
"Business Day" means Monday through Friday, excluding public holidays.

### 4.2 Insurance
The Provider shall maintain professional indemnity insurance of INR 50,00,000.

## Expected LexVigil Finding
Cross-reference resolution issue: Section 2.1 points to Section 4.2 for "Acceptance Criteria", but Section 4.2 contains insurance requirements rather than acceptance criteria. The system should flag a broken/misdirected internal reference even though there may be no direct logical contradiction.


# SAMPLE CONTRACT 07 — CLEAN AGREEMENT

## Purpose
Negative-control test: contract intentionally designed with no contradiction.

## 1. Definitions
### 1.1 Payment Period
"Payment Period" means thirty (30) days from receipt of a valid invoice.

### 1.2 Business Day
"Business Day" means Monday through Friday, excluding public holidays.

## 2. Payment
### 2.1 Payment Obligation
The Customer shall pay undisputed invoices within the Payment Period.

### 2.2 Late Payment
Amounts unpaid after the Payment Period shall accrue interest at 1% per month.

## 3. Termination
### 3.1 Convenience
Either party may terminate for convenience upon sixty (60) days' prior written notice.

## Expected LexVigil Finding
No contradiction expected. This is a negative control for measuring false positives.
