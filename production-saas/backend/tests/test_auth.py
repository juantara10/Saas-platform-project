def test_register_login_and_me(client):
 r=client.post("/api/v1/auth/register",json={"email":"dev@example.com","password":"VeryStrongPass123!","organization_name":"Dev Team"}); assert r.status_code==201; token=r.json()["access_token"]
 me=client.get("/api/v1/users/me",headers={"Authorization":f"Bearer {token}"}); assert me.status_code==200; assert me.json()["email"]=="dev@example.com"
 login=client.post("/api/v1/auth/token",data={"username":"dev@example.com","password":"VeryStrongPass123!"}); assert login.status_code==200
def test_duplicate_email_rejected(client):
 body={"email":"dev@example.com","password":"VeryStrongPass123!","organization_name":"Dev Team"}; assert client.post("/api/v1/auth/register",json=body).status_code==201; assert client.post("/api/v1/auth/register",json=body).status_code==409
