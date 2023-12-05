from quart import Quart, request, jsonify
import httpx
import asyncio

app = Quart(__name__)

async def post_persona(prompt, z, happy, angry):
    async with httpx.AsyncClient() as client:
        data = {"prompt": prompt, "happy": happy, "angry": angry, "z": z}
        response = await client.post("https://mlq.anyapp.me/personas/", json=data)
        return response.json()

async def get_persona_status(id):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://mlq.anyapp.me/personas/{id}")
        print(response.text)
        return response.json()

@app.route('/profile', methods=['GET'])
async def profile():
    z = request.args.get('z', "dev")
    prompt = request.args.get('prompt', "headshot of an actress")
    happy = float(request.args.get('happy', 0))
    angry = float(request.args.get('angry', 0))

    # First async call
    response = await post_persona(prompt, z, happy, angry)
    persona_id = response["id"]

    # Polling loop
    while True:
        status_response = await get_persona_status(persona_id)
        if status_response.get("status") == "completed":
            print("got status_response", status_response)
            return status_response["image_url"]
        await asyncio.sleep(1)  # Delay between polls

@app.route("/", methods=["GET"])
async def home():
    return "persona online"

if __name__ == '__main__':
    app.run(port=10011)

