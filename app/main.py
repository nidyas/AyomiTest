from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import sessionmaker
from typing import List
from .database import SessionLocal, engine
from .models import Operation
from .schemas import OperationCreate
from sqlalchemy.orm import Session
import csv
from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from fastapi.responses import FileResponse



app = FastAPI()

DATABASE_URL = "postgresql://postgres:postgres@db:5432/mydatabase"  # Connects to db service
# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
# Pydantic schema for RPN request
class RPNRequest(BaseModel):
    expression: str

# Calculate RPN expression
@app.post("/calculate/")
async def calculate_rpn(rpn_request: RPNRequest, db: Session = Depends(get_db)):
    expression = rpn_request.expression
    try:
        # Example logic for Reverse Polish Notation (RPN)
        stack = []
        for token in expression.split():
            if token.isdigit():
                stack.append(int(token))
            else:
                if len(stack) < 2:  # Check if there are at least two operands
                    raise ValueError("Not enough operands for the operation.")

                b = stack.pop()
                a = stack.pop()

                if token == '+':
                    stack.append(a + b)
                elif token == '-':
                    stack.append(a - b)
                elif token == '*':
                    stack.append(a * b)
                elif token == '/':
                    if b == 0:  # Check for division by zero
                        raise ValueError("Division by zero is not allowed.")
                    stack.append(a / b)
                else:
                    raise ValueError(f"Invalid operator: {token}")

        if len(stack) != 1:  # Ensure the final result is a single value
            raise ValueError("The expression is invalid. Please check your input.")

        result = stack.pop()

        # Save the operation and result in the database
        db_operation = Operation(expression=expression, result=result)
        db.add(db_operation)
        db.commit()

        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid expression: {str(e)}")

# Get all calculations in CSV format
@app.get("/get_csv/")
def get_csv():
    csv_filename = 'calculations.csv'
    
    # Create the CSV file and write data to it
    with open(csv_filename, 'w', newline='') as csvfile:
        fieldnames = ['expression', 'result']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        # Write operations from the database into the CSV
        db = next(get_db())
        operations = db.query(Operation).all()
        for op in operations:
            writer.writerow({'expression': op.expression, 'result': op.result})

    # Return the CSV file as a response
    return FileResponse(csv_filename, media_type='text/csv', filename=csv_filename)