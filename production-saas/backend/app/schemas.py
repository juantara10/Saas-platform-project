from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict
class RegisterIn(BaseModel):
 email:EmailStr; password:str=Field(min_length=12); organization_name:str=Field(min_length=2,max_length=120)
class TokenOut(BaseModel): access_token:str; token_type:str="bearer"
class UserOut(BaseModel):
 model_config=ConfigDict(from_attributes=True)
 id:str; email:EmailStr; is_active:bool; created_at:datetime
class OrgIn(BaseModel): name:str=Field(min_length=2,max_length=120)
class OrgOut(BaseModel):
 model_config=ConfigDict(from_attributes=True)
 id:str; name:str; slug:str; created_at:datetime
class MemberIn(BaseModel): email:EmailStr; role:str="member"
class MemberOut(BaseModel): user_id:str; email:EmailStr; role:str
class ApiKeyIn(BaseModel): name:str=Field(min_length=2,max_length=100)
class ApiKeyCreated(BaseModel): id:str; name:str; prefix:str; api_key:str
class CheckoutIn(BaseModel): organization_id:str
