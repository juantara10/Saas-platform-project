def auth(client,email,org):
 r=client.post("/api/v1/auth/register",json={"email":email,"password":"VeryStrongPass123!","organization_name":org}); return r.json()["access_token"]
def test_owner_can_create_api_key(client):
 token=auth(client,"owner@example.com","Owner Team"); org=client.get("/api/v1/organizations",headers={"Authorization":f"Bearer {token}"}).json()[0]; r=client.post("/api/v1/api-keys",json={"name":"CI"},headers={"Authorization":f"Bearer {token}","X-Organization-ID":org["id"]}); assert r.status_code==201; assert r.json()["api_key"].startswith("atlas_")
