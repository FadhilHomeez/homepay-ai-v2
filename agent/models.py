from typing import List, Optional
from pydantic import BaseModel, Field

class PaymentTerm(BaseModel):
    amount: Optional[float] = Field(None, description="The monetary amount for this payment term.")
    title: Optional[str] = Field(None, description="The title or milestone for the payment (e.g., 'Upon confirmation').")
    percentage: Optional[float] = Field(None, description="The percentage of the total project cost this payment represents.")
    description: Optional[str] = Field(None, description="More detailed description of the payment milestone.")

class InitialDeposit(BaseModel):
    amount: Optional[float] = Field(None, description="The monetary amount of the initial deposit.")
    title: Optional[str] = Field(None, description="The title for the deposit (e.g., 'Booking Fee').")
    percentage: Optional[float] = Field(None, description="The percentage of the total project cost this deposit represents.")
    description: Optional[str] = Field(None, description="More detailed description of the deposit.")

class Quotation(BaseModel):
    project_title: Optional[str] = Field(None, description="Project details or description.")
    property_address: Optional[str] = Field(None, description="The address of the property to be renovated.")
    property_type: Optional[str] = Field(None, description="The type of the property (e.g., 'BTO 5 Room', 'Condo', 'HDB Apartment', etc.).")
    quotation_number: Optional[str] = Field(None, description="The unique identifier or reference number for the quotation.")
    quotation_date: Optional[str] = Field(None, description="The date the quotation was issued (e.g., '01 Jan 2024' or any date format present).")
    quotation_amount: Optional[float] = Field(None, description="The final total amount of the quotation.")
    
    user_first_name: Optional[str] = Field(None, description="The first name of the customer/client.")
    user_last_name: Optional[str] = Field(None, description="The last name of the customer/client.")
    user_email: Optional[str] = Field(None, description="The email address of the customer.")
    user_phone: Optional[str] = Field(None, description="The phone number of the customer.")
    user_address: Optional[str] = Field(None, description="The residential or billing address of the customer.")
    user_postal: Optional[str] = Field(None, description="The postal code of the customer.")
    
    has_gst: Optional[int] = Field(None, description="Whether the quotation includes GST (1 if yes, 0 if no).")
    
    initial_deposit: List[InitialDeposit] = Field(default_factory=list, description="List of initial deposits or booking fees.")
    payment_terms: List[PaymentTerm] = Field(default_factory=list, description="List of progressive payment terms or milestones.")

