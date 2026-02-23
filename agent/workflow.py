import base64
import operator
from io import BytesIO
from typing import Annotated, TypedDict, List
from pdf2image import convert_from_path

from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
import tempfile

from agent.models import Quotation

# Define the state for the workflow
class WorkflowState(TypedDict):
    # Input
    pdf_path: str
    
    # Intermediate state
    base64_images: List[str]
    
    # Output
    quotation_data: Quotation
    
    # Error handling
    error: str

# 1. Node to convert PDF to base64 images
def convert_pdf_to_images(state: WorkflowState) -> WorkflowState:
    try:
        images = convert_from_path(state["pdf_path"])
        base64_images = []
        for img in images:
            # Convert PIL image to base64
            buffered = BytesIO()
            img.save(buffered, format="JPEG")
            img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
            base64_images.append(img_str)
            
        return {"base64_images": base64_images}
    except Exception as e:
        return {"error": f"Failed to convert PDF: {str(e)}"}

# 2. Node to extract details using Gemini 2.5 Flash
def extract_quotation_details(state: WorkflowState) -> WorkflowState:
    if state.get("error"):
        return state # Skip if already in error state
        
    try:
        # Initialize Gemini 2.5 Flash model
        # Note: You need to set GOOGLE_API_KEY environment variable
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
        
        # Enforce structured output to our Quotation schema
        structured_llm = llm.with_structured_output(Quotation)
        
        # Prepare messages
        content_parts = [
            {"type": "text", "text": "Extract the quotation details from the following images according to the provided schema. Pay close attention to extracting the customer's personal details, the project title and address, the total quotation amount, and a breakdown of the initial deposit and progressive payment terms. If a field is not present in the document, leave it as null. For boolean-like fields like has_gst, output 1 for true/yes, 0 for false/no."}
        ]
        
        for img_base64 in state["base64_images"]:
            content_parts.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}
            })
            
        message = HumanMessage(content=content_parts)
        
        # Invoke model
        result = structured_llm.invoke([message])
        
        return {"quotation_data": result}
    except Exception as e:
        return {"error": f"Failed to extract details: {str(e)}"}

# Define routing logic based on errors
def route_after_conversion(state: WorkflowState) -> str:
    if state.get("error"):
        return END
    return "extract"

# Build the Graph
builder = StateGraph(WorkflowState)
builder.add_node("convert", convert_pdf_to_images)
builder.add_node("extract", extract_quotation_details)

builder.set_entry_point("convert")
builder.add_conditional_edges("convert", route_after_conversion)
builder.add_edge("extract", END)

# Compile workflow
quotation_extractor_app = builder.compile()

# Helper function to run the workflow
def run_extraction_workflow(pdf_path: str) -> dict:
    initial_state = {"pdf_path": pdf_path, "base64_images": [], "error": None}
    
    # Run the workflow
    result_state = quotation_extractor_app.invoke(initial_state)
    
    if result_state.get("error"):
        return {"success": False, "error": result_state["error"]}
        
    quotation = result_state.get("quotation_data")
    if quotation:
        # Pydantic v2 dump
        return {"success": True, "data": quotation.model_dump()}
    else:
        return {"success": False, "error": "Unknown error during extraction."}
