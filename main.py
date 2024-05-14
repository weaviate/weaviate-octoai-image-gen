# pip install -U weaviate-client
# pip install pillow


import os
import weaviate
import weaviate.classes as wvc

import base64
import io
import PIL.Image


API_KEY = ""  # insert your API key here
if API_KEY == "":
    API_KEY = os.getenv("OCTOAI_API_KEY")
binary_mac = "https://github.com/weaviate/weaviate-octoai-image-gen/releases/download/v0.0.1/weaviate-v1.25.0-48-g0d52f1622-darwin-all.zip"
binary_linux = "https://github.com/weaviate/weaviate-octoai-image-gen/releases/download/v0.0.1/weaviate-v1.25.0-linux-amd64.tar.gz"
try:
    # mac embedded
    client = weaviate.connect_to_embedded(
        version=binary_mac,
        environment_variables={"ENABLE_MODULES": "text2vec-octoai,generative-octoai"},
    )
    # # linux embedded
    # client = weaviate.connect_to_embedded(
    #         version=binary_linux,
    #         environment_variables={"ENABLE_MODULES": "text2vec-octoai,generative-octoai"}
    # )

    # weaviate in docker
    # client = weaviate.connect_to_local()
    client.collections.delete("Products")
    collection = client.collections.create(
        "Products",
        properties=[
            wvc.config.Property(name="name", data_type=wvc.config.DataType.TEXT),
            wvc.config.Property(name="description", data_type=wvc.config.DataType.TEXT),
        ],
        vectorizer_config=wvc.config.Configure.Vectorizer.text2vec_octoai(),
        generative_config=wvc.config.Configure.Generative.octoai(
            base_url="https://image.octoai.run"
        ),  # activates image generation
    )
    client.integrations.configure(wvc.config.Integrations.octoai(api_key=API_KEY))

    # Add data
    collection.data.insert_many(
        [
            {
                "name": "Sun-Kissed Fedora",
                "description": "A wide-brimmed hat woven from natural straw, casting playful shadows on sun-drenched beaches with a perfect advocado pattern.",
            },
            {
                "name": "Breezy Linen Shorts",
                "description": "Lightweight shorts with lemon pattern and a relaxed fit, perfect for strolling along boardwalks or sipping iced coffee",
            },
            {
                "name": "Frost-Tipped Beanie",
                "description": "A cozy knit hat adorned with frosty accents, keeping ears warm during chilly snowfall",
            },
            {
                "name": "Seaside Romper",
                "description": "An airy one-piece outfit featuring big spiral patterns and a cinched waist, reminiscent of salty ocean breezes",
            },
            {
                "name": "Mountain Explorer Parka",
                "description": "Insulated winter coat with faux fur trim, designed for conquering snowy peaks and frosty forests",
            },
            {
                "name": "Golden Hour Sunglasses",
                "description": "Oversized shades with gradient lenses, capturing the warm hues of sunset on city rooftops",
            },
            {
                "name": "Cozy Knit Sweater",
                "description": "A soft, oversized sweater made from warm knit fabric. Perfect for chilly days.",
            },
            {
                "name": "Denim Jacket",
                "description": "A classic blue denim jacket with button closures and front pockets. Versatile and timeless.",
            },
            {
                "name": "Floral Maxi Dress",
                "description": "A long, flowy dress adorned with vibrant floral patterns. Ideal for warm weather.",
            },
            {
                "name": "Tailored Blazer",
                "description": "A structured blazer in a neutral color, suitable for both professional and casual occasions.",
            },
            {
                "name": "Athletic Leggings",
                "description": "Stretchy, moisture-wicking leggings designed for workouts and active wear.",
            },
        ]
    )

    for text in ["summer"]:
        resp = collection.generate.near_text(
            query=text + " clothing",
            distance=0.2,
            limit=2,
            single_prompt="Generate an advert of the given product for a webshop. In the add include one adult person and show the full face and body. Create the image based on name: {name} and description: {description}.",
        )

        for i, obj in enumerate(resp.objects):
            ibytes = obj.generated
            img_bytes = base64.b64decode(ibytes)
            img = PIL.Image.open(io.BytesIO(img_bytes))
            img.load()
            name = obj.properties["name"]
            img.save(f"result_image_{text}_{name}.jpg")
finally:
    client.close()
