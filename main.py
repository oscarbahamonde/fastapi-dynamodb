from pydantic import BaseModel, Field, EmailStr, validator
from uuid import uuid4
from typing import Optional, List, Dict
from datetime import datetime
from boto3 import resource
from dotenv import load_dotenv

load_dotenv()
from os import getenv

dynamodb = resource('dynamodb',
                    aws_access_key_id=getenv('AWS_ACCESS_KEY_ID'),
                    aws_secret_access_key=getenv('AWS_SECRET_ACCESS_KEY'),
                    region_name=getenv('AWS_REGION'))

def generate_id():
    return str(uuid4())

def generate_date():
    return str(datetime.now())


class User(BaseModel):
    id: str = Field(default_factory=generate_id)
    username: str = Field(...)
    fullname: Optional[str] = Field()
    email: EmailStr = Field(...)
    age: Optional[int] = Field()
    picture: List[str] = Field()
    created_at: str = Field(default_factory=generate_date)

class Product(BaseModel):
    id: str = Field(default_factory=generate_id)
    name: str = Field(...)
    description: str = Field(...)
    price: float = Field(...)
    category: str = Field(...)
    image: List[str] = Field(...)
    created_at: str = Field(default_factory=generate_date)
    stock: int = Field(...)

class Order(BaseModel):
    id: str = Field(default_factory=generate_id)
    user_id: str = Field(...)
    quotation:List[Dict[str, int]] = Field(...)
    created_at: str = Field(default_factory=generate_date)
    total: float = Field(...)
    status: str = Field()
    payment_method: str = Field()
    payment_id: str = Field()


from botocore.exceptions import ClientError
from starlette.responses import JSONResponse

usersTable = dynamodb.Table('users')
productsTable = dynamodb.Table('products')
ordersTable = dynamodb.Table('orders')

def create_user(user:dict):
    try:
        usersTable.put_item(Item=user)
        return user
    except ClientError as e:
        return JSONResponse(content = e.response['Error']['Message'], status_code = 500)

def get_user(id:str):
    try:
        response = usersTable.query(KeyConditionExpression=Key('id').eq(id))
        return response['Items']
    except ClientError as e:
        return JSONResponse(content = e.response['Error']['Message'], status_code = 500)

def get_users():
    try:
        response = usersTable.scan(
        Limit=20,
        AttributesToGet=['id','username','email','picture','created_at'])
        return response['Items']
    except ClientError as e:
            return JSONResponse(content = e.response['Error']['Message'], status_code = 500)

def delete_user(id:str):
    try:
        response = usersTable.delete_item(Key={'id': id})
        return response
    except ClientError as e:
        return JSONResponse(content = e.response['Error']['Message'], status_code = 500)

def update_user(id:str, user:dict):
    try:
        response = usersTable.update_item(Key={'id': id},
                          UpdateExpression="set email = :email,  = :password",
                          ExpressionAttributeValues={
                              ':email': user['email'],
                              ':username': user['username'],
                              ':picture': user['picture'],
                          },
                          ReturnValues="UPDATED_NEW")
        return response
    except ClientError as e:
        return JSONResponse(content = e.response['Error']['Message'], status_code = 500)

def create_products(products:dict):
    try:
        productsTable.put_item(Item=products)
        return products
    except ClientError as e:
        return JSONResponse(content = e.response['Error']['Message'], status_code = 500)

def get_product(id:str):
    try:
        response = productsTable.query(KeyConditionExpression=Key('id').eq(id))
        return response['Items']
    except ClientError as e:
        return JSONResponse(content = e.response['Error']['Message'], status_code = 500)

def get_products():
    try:
        response = productsTable.scan(
        Limit=30,
        AttributesToGet=['id','name', 'description', 'price', 'category' 'image', 'created_at', 'stock'])
        return response['Items']
    except ClientError as e:
            return JSONResponse(content = e.response['Error']['Message'], status_code = 500)    

def delete_product(id:str):
    try:
        response = productsTable.delete_item(Key={'id': id})
        return response
    except ClientError as e:
        return JSONResponse(content = e.response['Error']['Message'], status_code = 500)

def create_order(order:dict):
    try:
        ordersTable.put_item(Item=order)
        return order
    except ClientError as e:
        return JSONResponse(content = e.response['Error']['Message'], status_code = 500)

def get_order(id:str):
    try:
        response = ordersTable.query(KeyConditionExpression=Key('id').eq(id))
        return response['Items']
    except ClientError as e:
        return JSONResponse(content = e.response['Error']['Message'], status_code = 500)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])

@app.post('api/user/create', response_model=User)
def create(user:User):
    return create_user(user.dict())

@app.get('api/user/get/{id}')
def get(id:str):
    return get_user(id)

@app.get('api/user/get')
def getAll():
    return get_users()

@app.delete('api/user/delete/{id}')
def delete(id:str):
    return delete_user(id)

@app.put('api/user/update/{id}')
def update(id:str, user:User):
    return update_user(id, user.dict())

@app.post('api/product/create', response_model=Product)
def create(product:Product):
    return create_products(product.dict())

@app.get('api/product/get/{id}')
def get(id:str):
    return get_product(id)

@app.get('api/product/get')
def getAll():
    return get_products()

@app.delete('api/product/delete/{id}')
def delete(id:str):
    return delete_product(id)

@app.post('api/order/create', response_model=Order)
def create(order:Order):
    return create_order(order.dict())

@app.get('api/order/get/{id}')
def get(id:str):
    return get_order(id)

@app.get('/')
def index():
    return {'message': 'Hello World'}

from mangum import Mangum

handler = Mangum(app)