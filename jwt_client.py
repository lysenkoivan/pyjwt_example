import os
import requests

base_url = os.getenv("AUTH_SVC","http://pyjwt.demo-project1.svc")

if __name__ == "__main__":
	r = requests.post(base_url + "/login", auth=("anylogin","password"))
	if not r.ok:
		print(r.status, r.content)

	token = r.json()
	print(token)

	r = requests.get(base_url + "/unprotected")
	print(r.content)
