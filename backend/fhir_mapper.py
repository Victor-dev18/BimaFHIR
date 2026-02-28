import uuid
from fhir.resources.bundle import Bundle, BundleEntry
from fhir.resources.insuranceplan import (
    InsurancePlan, 
    InsurancePlanCoverage, 
    InsurancePlanCoverageBenefit
)
from fhir.resources.codeableconcept import CodeableConcept

def convert_to_fhir(extracted_data: dict) -> dict:
    print("Starting FHIR mapping process...")
    
    # 1. Initialize the main Insurance Plan resource
    plan_id = str(uuid.uuid4())
    
    # Combining insurer and plan name for the FHIR record
    full_plan_name = f"{extracted_data.get('insurer_name', 'Unknown')} - {extracted_data.get('plan_name', 'Health Plan')}"
    
    plan = InsurancePlan(
        id=plan_id,
        status="active",
        name=full_plan_name,
        # NHCX expects a specific code system for plan types
        type=[CodeableConcept(
            coding=[{
                "system": "https://nrces.in/ndhm/fhir/r4/CodeSystem/ndhm-insuranceplan-type", 
                "code": "01", 
                "display": "Hospitalisation Indemnity Policy"
            }]
        )]
    )

    # 2. Map the extracted Benefits into FHIR objects
    benefits_list = []
    
    for b in extracted_data.get('benefits', []):
        # Build the specific rules (requirements) for this benefit
        req_text = []
        if b.get('limit'):
            req_text.append(f"Limit: {b['limit']}")
        if b.get('waiting_period'):
            req_text.append(f"Waiting Period: {b['waiting_period']}")
            
        requirement_str = " | ".join(req_text) if req_text else "Covered as per standard policy terms."
        
        benefit_obj = InsurancePlanCoverageBenefit(
            type=CodeableConcept(text=b.get('benefit_name')),
            requirement=requirement_str
        )
        benefits_list.append(benefit_obj)
        
    # 3. Map the Exclusions (NHCX allows these to be listed as specific non-covered benefits)
    for e in extracted_data.get('exclusions', []):
        icd_codes = e.get('icd_codes', [])
        icd_text = f" - ICD Codes: {', '.join(icd_codes)}" if icd_codes else ""
        
        exclusion_obj = InsurancePlanCoverageBenefit(
            type=CodeableConcept(text=f"EXCLUSION: {e.get('exclusion_type')}"),
            requirement=f"This condition is explicitly excluded from coverage{icd_text}."
        )
        benefits_list.append(exclusion_obj)

    # 4. Attach all benefits and exclusions to the Plan Coverage
    coverage = InsurancePlanCoverage(
        type=CodeableConcept(text="Inpatient and Day Care Management"),
        benefit=benefits_list
    )
    plan.coverage = [coverage]

    # 5. Create the Bundle Entry
    entry = BundleEntry(
        fullUrl=f"urn:uuid:{plan_id}",
        resource=plan
    )

    # 6. Construct the Final NHCX-compliant Collection Bundle
    nhcx_bundle = Bundle(
        type="collection", 
        entry=[entry]
    )

    print("FHIR Bundle successfully generated!")
    
    # model_dump(exclude_none=True) ensures clean JSON without null clutter
    return nhcx_bundle.model_dump(exclude_none=True)