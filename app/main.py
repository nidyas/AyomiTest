from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .database import get_db
from .models import Operation
from sqlalchemy.orm import Session
import csv
from fastapi import Depends
from fastapi.responses import FileResponse




app = FastAPI()
# Pydantic schema for RPN request
class RPNRequest(BaseModel):
    expression: str

# Calculate RPN expression
@app.post("/calculate")
async def calculate_rpn(rpn_request: RPNRequest, db: Session = Depends(get_db)):
    expression = rpn_request.expression
    try:
        # Example logic for Reverse Polish Notation (RPN)
        stack = []
        for token in expression.split():
            if token.isdigit():
                stack.append(int(token))
            else:
                if len(stack) < 2:  
                    raise ValueError("Not enough operands for the operation.")

                b = stack.pop()
                a = stack.pop()

                if token == '+':
                    result = a + b
                elif token == '-':
                    result = a - b
                elif token == '*':
                    result = a * b
                elif token == '/':
                    if b == 0:  
                        raise ValueError("Division by zero is not allowed.")
                    result = a / b
                else:
                    raise ValueError(f"Invalid operator: {token}")
                
        # Save the operation and result in the database
        db_operation = Operation(expression=expression, result=result)
        db.add(db_operation)
        db.commit()

        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid expression: {str(e)}")

# Get all calculations in CSV format
@app.get("/get_csv")
def get_csv(db: Session = Depends(get_db)):
    csv_filename = 'calculations.csv'
    
    # Create the CSV file and write data to it
    with open(csv_filename, 'w', newline='') as csvfile:
        fieldnames = ['expression', 'result']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        operations = db.query(Operation).all()
        for op in operations:
            writer.writerow({'expression': op.expression, 'result': op.result})
    return FileResponse(csv_filename, media_type='text/csv', filename=csv_filename)