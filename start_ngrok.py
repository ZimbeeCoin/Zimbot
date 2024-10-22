from pyngrok import ngrok
import time

# Set your Ngrok auth token
ngrok.set_auth_token("2nj8Px5KKEv7bKz03tt3tnyWNDc_6BCERS5AezjXwa6Y7zbGu")  # Replace with your actual auth token

# Open a HTTP tunnel on port 8000
public_url = ngrok.connect(8000)
print(f"Public URL: {public_url}")

# Keep the tunnel open
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Tunnel closed")
    ngrok.disconnect(public_url)
    ngrok.kill()
