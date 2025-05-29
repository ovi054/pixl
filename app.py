import requests
import json
import base64
import io
import os
from PIL import Image
import gradio as gr
import uuid
import sys
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s ' '- %(message)s',
    stream=sys.stdout,
)
# import tqdm
# import time
theme = gr.themes.Soft().set(
    body_background_fill='*primary_50',
    # block_border_width='*block_label_border_width',
    # block_border_width_dark='*checkbox_border_width',
    button_secondary_background_fill='*primary_500',
    # button_secondary_background_fill_dark='*primary_700',
    button_secondary_background_fill_hover='*primary_400',
    button_secondary_border_color='*primary_100',
    # button_secondary_border_color_dark='*primary_700',
    button_secondary_text_color='*button_primary_text_color'
)

init_html = '''<!doctype html>
<html>
<head>
    <style>
    

.sliding-puzzle-figure {
  margin: auto !important;
  height: 300px !important;
  width: 300px !important;
  max-height: 70vh !important;
  max-width: 70vh !important;
  }
  .sliding-puzzle-figure a {
    cursor: pointer; }
    .sliding-puzzle-figure a#shuffle {
      color: #E74C3C; }
    .sliding-puzzle-figure a#solve {
      color: #3498DB; }
  .sliding-puzzle-figure .sliding-puzzle {
    list-style-type: none;
    position: relative;
    margin-left: auto;
    margin-right: auto;
    width: 300px;
    height: 300px;
    box-sizing: border-box;
    background-clip: border-box;
    border: 37px solid #2C3E50;
    border-radius: 10px;
    background-color: #2C3E50; }
    .sliding-puzzle-figure .sliding-puzzle .tile {
      position: absolute;
      background-color: #7BC8F3;
      color: #1F1F1F;
      border-radius: 10px;
      cursor: pointer;
      width: 33%;
      height: 33%;
      display: flex;
      justify-content: center;
      align-items: center;
      font-size: 50px;
      left: 0%;
      top: 0%;
      transition: all 0.5s linear;
      transition-timing-function: ease;
      box-sizing: border-box;
      border: solid 2px;
      border-color: #7BC8F3;}
      .sliding-puzzle-figure .sliding-puzzle .tile.error {
        background-color: #F0867D;
        border-color: #F0867D;}
@media only screen and (max-width: 650px) {
  .sliding-puzzle-figure {
    width: 90vw;
    height: 90vw;
    max-height: 100vh; }
    .sliding-puzzle-figure .sliding-puzzle {
      border-width: 10px;
      border-radius: 14px; }
    .sliding-puzzle-figure .tile {
      font-size: 1em; } }
</style>

    <meta name="viewport" content="initial-scale=1.0, width=device-width">
</head>
<body>

    <figure class="sliding-puzzle-figure">

        <ul class="sliding-puzzle">
            <li class="tile" id="ans1">1</li>
            <li class="tile" id="ans2">2</li>
            <li class="tile" id="ans3">3</li>
            <li class="tile" id="ans4">4</li>
            <li class="tile" id="ans5">5</li>
            <li class="tile" id="ans6">6</li>
            <li class="tile" id="ans7">7</li>
            <li class="tile" id="ans8">8</li>
        </ul>

        <figcaption>
        <a id="shuffle"></a><a id="solve"></a>
        </figcaption>
    </figure>


</body>
</html>'''

js_payment = """
function pay() {
      const buttonContainer = document.getElementById("buttonContainer");
      const payButton = document.getElementById("payButton");

      // Set the href attribute
      payButton.href = "https://piczify.lemonsqueezy.com/checkout/custom/283c32f2-7635-4809-af0a-6adf8f853cda?signature=4b486a404cf7d5751e7fc8b38f15a63bef909028ccbfc1a97b5efb4121c1f9fd";
      payButton.textContent = "Click here to Pay 9.99$";

      // Apply button styles
      payButton.style.display = "inline-block";
      payButton.style.padding = "10px 20px";
      payButton.style.backgroundColor = "#007bff";
      payButton.style.color = "#fff";
      payButton.style.textDecoration = "none";
      payButton.style.border = "none";
      payButton.style.borderRadius = "5px";
      payButton.style.cursor = "pointer";
      payButton.style.fontSize = "16px";

      // Add the button to the container
      buttonContainer.appendChild(payButton);
    }
"""


scripts = """
function game() {


  var parentX = document.querySelector(".sliding-puzzle").clientHeight;
  var baseDistance = 34.5;
  var tileMap = {
    1: {
      tileNumber: 1,
      position: 1,
      top: 0,
      left: 0
    },
    2: {
      tileNumber: 2,
      position: 2,
      top: 0,
      left: baseDistance * 1
    },
    3: {
      tileNumber: 3,
      position: 3,
      top: 0,
      left: baseDistance * 2
    },
    4: {
      tileNumber: 4,
      position: 4,
      top: baseDistance,
      left: 0
    },
    5: {
      tileNumber: 5,
      position: 5,
      top: baseDistance,
      left: baseDistance
    },
    6: {
      tileNumber: 6,
      position: 6,
      top: baseDistance,
      left: baseDistance * 2
    },
    7: {
      tileNumber: 7,
      position: 7,
      top: baseDistance * 2,
      left: 0
    },
    8: {
      tileNumber: 8,
      position: 8,
      top: baseDistance * 2,
      left: baseDistance
    },
    empty: {
      position: 9,
      top: baseDistance * 2,
      left: baseDistance * 2
    }
  }

  var history = [];


  function movementMap(position) {
    if (position == 9) return [6, 8];
    if (position == 8) return [5, 7, 9];
    if (position == 7) return [4, 8];
    if (position == 6) return [3, 5, 9];
    if (position == 5) return [2, 4, 6, 8];
    if (position == 4) return [1, 5, 7];
    if (position == 3) return [2, 6];
    if (position == 2) return [1, 3, 5];
    if (position == 1) return [2, 4];
  }


  document.querySelector('#shuffle').addEventListener('click', shuffle , true);
  document.querySelector('#solve').addEventListener('click', solve , true);
  var tiles = document.querySelectorAll('.tile');
  var delay = -50;
  for(var i = 0; i < tiles.length; i++) {
    tiles[i].addEventListener('click', tileClicked ,true );

    var tileId = tiles[i].innerHTML;
    delay += 50;
    setTimeout(setup, delay, tiles[i]);
  }

  function setup(tile) {
    var tileId = tile.innerHTML;

    var xMovement = parentX * (tileMap[tileId].left/100);
    var yMovement = parentX * (tileMap[tileId].top/100);
    var translateString = "translateX(" + xMovement + "px) " + "translateY(" + yMovement + "px)"
    tile.style.webkitTransform = translateString;
    recolorTile(tile, tileId);
  }

  function tileClicked(event) {
    var tileNumber = event.target.innerHTML;
    moveTile(event.target);

    if (checkSolution()) {
      console.log("You win!");
    }
  }


  function moveTile(tile, recordHistory = true) {

    var tileNumber = tile.innerHTML;
    if (!tileMovable(tileNumber)) {
      console.log("Tile " + tileNumber + " can't be moved.");
      return;
    }


    if (recordHistory == true) {

      if (history.length >= 3) {
        if (history[history.length-1] != history[history.length-3]) history.push(tileNumber);
      } else {
        history.push(tileNumber);
      }
    }


    var emptyTop = tileMap.empty.top;
    var emptyLeft = tileMap.empty.left;
    var emptyPosition = tileMap.empty.position;
    tileMap.empty.top = tileMap[tileNumber].top;
    tileMap.empty.left = tileMap[tileNumber].left;
    tileMap.empty.position = tileMap[tileNumber].position;


    var xMovement = parentX * (emptyLeft/100);
    var yMovement = parentX * (emptyTop/100);
    var translateString = "translateX(" + xMovement + "px) " + "translateY(" + yMovement + "px)"
    tile.style.webkitTransform = translateString;

    tileMap[tileNumber].top = emptyTop;
    tileMap[tileNumber].left = emptyLeft;
    tileMap[tileNumber].position = emptyPosition;

    recolorTile(tile, tileNumber);
  }

  function tileMovable(tileNumber) {
    var selectedTile = tileMap[tileNumber];
    var emptyTile = tileMap.empty;
    var movableTiles = movementMap(emptyTile.position);

    if (movableTiles.includes(selectedTile.position)) {
      return true;
    } else {
      return false;
    }



  }

  function checkSolution() {
    if (tileMap.empty.position !== 9) return false;

    for (var key in tileMap) {
      if ((key != 1) && (key != "empty")) {
        if (tileMap[key].position < tileMap[key-1].position) return false;
      }
    }

    history = [];
    return true;
  }


  function recolorTile(tile, tileId) {
    if (tileId == tileMap[tileId].position) {
      tile.classList.remove("error");
    } else {
      tile.classList.add("error");
    }
  }


  shuffleTimeouts = [];
  function shuffle() {
    clearTimers(solveTimeouts);
    var boardTiles = document.querySelectorAll('.tile');
    var shuffleDelay = 200;
    shuffleLoop();

    var shuffleCounter = 0;
    while (shuffleCounter < 20) {
      shuffleDelay += 200;
      shuffleTimeouts.push(setTimeout(shuffleLoop, shuffleDelay));
      shuffleCounter++;
    }
  }

  var lastShuffled;

  function shuffleLoop() {
    var emptyPosition = tileMap.empty.position;
    var shuffleTiles = movementMap(emptyPosition);
    var tilePosition = shuffleTiles[Math.floor(Math.floor(Math.random()*shuffleTiles.length))];
    var locatedTile;
    for(var i = 1; i <= 8; i++) {
      if (tileMap[i].position == tilePosition) {
        var locatedTileNumber = tileMap[i].tileNumber;
        locatedTile = tiles[locatedTileNumber-1];
      }
    }
    if (lastShuffled != locatedTileNumber) {
      moveTile(locatedTile);
      lastShuffled = locatedTileNumber;
    } else {
      shuffleLoop();
    }

  }


  function clearTimers(timeoutArray) {
    for (var i = 0; i < timeoutArray.length; i++) {
      clearTimeout(timeoutArray[i])
    }
  }

  solveTimeouts = []
  function solve() {
    clearTimers(shuffleTimeouts);


    repeater = history.length;

    for (var i = 0; i < repeater; i++) {
      console.log("started");
      solveTimeouts.push(setTimeout(moveTile, i*100, tiles[history.pop()-1], false));
    }
  }


}
"""



# # GitHub repository details
# username = 'ovi054'
# repository = 'puzzle'
# access_token = os.getenv("GIT_TOKEN")


# # Function to upload a file to GitHub repository
# def upload_file(file_path, content):
#     url = f'https://api.github.com/repos/{username}/{repository}/contents/{file_path}'
#     headers = {'Authorization': f'token {access_token}'}
#     data = {
#         'message': f'Upload {file_path}',
#         'content': content,
#         'branch': 'main'
#     }
#     response = requests.put(url, headers=headers, json=data)
#     return response


def resize_to_square_by_cropping(image, max_size=500):
    # Get the dimensions of the image
    image_width, image_height = image.size

    # Determine the size of the square based on the minimum dimension
    square_size = min(image_width, image_height)

    # Calculate the coordinates for central cropping
    left = (image_width - square_size) / 2
    top = (image_height - square_size) / 2
    right = (image_width + square_size) / 2
    bottom = (image_height + square_size) / 2

    # Crop the image to a square
    cropped_image = image.crop((left, top, right, bottom))

    # If the square is larger than the maximum allowed size, resize it
    if square_size > max_size:
        cropped_image = cropped_image.resize((max_size, max_size), Image.Resampling.LANCZOS)

    return cropped_image


def perform_operations(image, email_id):
    # Get the contents of the 'avipal' folder
    # print(target_folder)
    # if(target_folder==""  or target_folder==None):
    logging.info(f"Email address is: {email_id}")
    # print(f"Email address is: {email_id}")
    uuid_code = str(uuid.uuid4())

    split_rows = 3
    split_cols = 3
    

    #Split the input image into sub-images and update the '1.png' to '9.png' in the 'avipal3/css' folder
    sub_image_list = []
    input_image = resize_to_square_by_cropping(image)
    image_width, image_height = input_image.size
    # print(image_width, image_height)
    sub_image_width = image_width // split_cols
    sub_image_height = image_height // split_rows

    for row in range(split_rows):
        for col in range(split_cols):
            left = col * sub_image_width
            upper = row * sub_image_height
            right = left + sub_image_width
            lower = upper + sub_image_height
            sub_image = input_image.crop((left, upper, right, lower))

            # Encode the sub-image as base64 string
            sub_image_byte_array = io.BytesIO()
            sub_image.save(sub_image_byte_array, format='PNG')
            sub_image_base64 = base64.b64encode(sub_image_byte_array.getvalue()).decode('utf-8')
            sub_image_list.append(sub_image_base64)

    url = "https://puzzle-image-db.avi-pal357.workers.dev/"


    payload = {
        "id": uuid_code,
        "image_1": "data:image/png;base64,"+sub_image_list[0],
        "image_2": "data:image/png;base64,"+sub_image_list[1],
        "image_3": "data:image/png;base64,"+sub_image_list[2],
        "image_4": "data:image/png;base64,"+sub_image_list[3],
        "image_5": "data:image/png;base64,"+sub_image_list[4],
        "image_6": "data:image/png;base64,"+sub_image_list[5],
        "image_7": "data:image/png;base64,"+sub_image_list[6],
        "image_8": "data:image/png;base64,"+sub_image_list[7]
    }
    response = requests.post(url, json=payload)
    logging.info(response.json())
    dbStored = False
    if response.status_code == 200:
        result = response.json()
        if result['success']:
            dbStored = True

    # file_path = f'{uuid_code}/index.html'
    # upload_file(file_path,base64.b64encode(git_html.encode('utf-8')).decode('utf-8'))
    base_url = "https://piczify.com/s/?id="
    target_folder_url = base_url + uuid_code
    return target_folder_url,sub_image_list, dbStored

with gr.Blocks(theme=theme) as demo:
    # start_btn = gr.Button(value="Preview?")
    # start_html = gr.HTML(start)
    # demo.load(None,None,None,_js=scripts)
    with gr.Row():
        image = gr.Image(label="Upload a square shaped image",
            height = 300,
            type = 'pil',
            interactive = True                                            
        )
    email = gr.Textbox(label="Email address")
    btn = gr.Button(value="Submit")
    test_html = gr.HTML()
    start_html = gr.HTML(init_html)
    demo.load(None,None,None,js=scripts)
    out = gr.HTML(init_html, visible=False)
    demo.load(None,None,None,js=scripts)
    # btn2 = gr.Button(value="Pay to Get URL",visible=False)
    pay_html = gr.HTML()

    def call_api(image, email_id):
    # Generate a UUID code
        # imgs = [None] * 100
        # for img in progress.tqdm(imgs, desc="Generating Puzzle"):
        #     time.sleep(0.1)
        yield {
            # btn2: gr.update(visible=True),
            out: init_html,
            test_html:  """
    <div style="display: flex; justify-content: center; align-items: center; font-weight: bold; color: #333;">
      Generating Puzzle...
    </div>
    """,
            pay_html: pay_html
        }
        receipt_link_url, sub_image_list, dbStored = perform_operations(image,email_id)
        logging.info(f"Cutom Puzzle Url is: {receipt_link_url}")
        # print(f"Cutom Puzzle Url is: {receipt_link_url}")
        redirect_url = "https://piczify.com/thank-you/"

        # print(sub_image_list)

        url = "https://api.lemonsqueezy.com/v1/checkouts"
        api_key = os.getenv("LEMON_ACTUAL_KEY")

        # Define the request headers
        headers = {
            'Authorization': f'Bearer {api_key}'
        }

        # Create the request body
        request_body = {
            "data": {
                "type": "checkouts",
                "attributes": {
                    "product_options": {
                        "enabled_variants": [],
                        "redirect_url": redirect_url,
                        "receipt_link_url": receipt_link_url,
                        "receipt_button_text": "Puzzle Link",
                        "receipt_thank_you_note": "Your custom Sliding Puzzle link is : " + str(receipt_link_url) + "\n Click on Puzzle Link button or go to the custom puzzle link to play your Puzzle.",
                    },
                    "checkout_options": {
                        "button_color": "#2DD272"
                    },
                    "checkout_data": {},
                    "preview": True
                },
                "relationships": {
                    "store": {
                        "data": {
                            "type": "stores",
                            "id": "33985"
                        }
                    },
                    "variant": {
                        "data": {
                            "type": "variants",
                            "id": "108876"
                        }
                    }
                }
            }
        }

        # Convert the request body to JSON string
        request_json = json.dumps(request_body)

        # Make the API call
        response = requests.post(url, headers=headers, data=request_json)

        # print(response)

        # Check the response status code
        # Check the response status code
        payment_html = f'''
            <html>
            <body>
                <p></p>
            </body>
            </html>
            '''
        if dbStored and response.status_code == 201:
            # Parse the API response JSON
            api_response = response.json()

            # Get the URL value from the response
            url_value = api_response["data"]["attributes"]["url"]

            logging.info(f"Checkout Url is: {url_value}")
            # print(f"Checkout Url is: {url_value}")

            payment_html = f"""<!DOCTYPE html>
<html>
<head>
  <style>
    .lemonsqueezy-button-container {{
      margin-top: 30px !important;
    }}

    .lemonsqueezy-button {{
      display: inline-block !important;
      padding: 15px 30px !important;
      background-color: #ED6524 !important;
      color: white !important;
      text-decoration: none !important;
      border: none !important;
      border-radius: 5px !important;
      font-size: 17px !important;
      margin-bottom: 10px !important; 
      font-weight: 700 !important;
      transition: color 0.3s !important;
    }}
    .lemonsqueezy-button:hover {{
      background-color: #ED6524 !important;
      border-color: #ED6524 !important;
      color:  #4c4e61 !important;
      }}
    .fix-align{{
        text-align: center !important;
    }}
  </style>
</head>
<body>
  <div class="fix-align">
  <!-- Container for centering the button horizontally -->
  <div class="lemonsqueezy-button-container" id="buttonContainer">
    <!-- Anchor tag with the class "lemonsqueezy-button" to apply the button styles -->
    <a href="{url_value}" target="_blank" class="lemonsqueezy-button" id="payButton">Get shareable link for $9.99</a>
    <p class="payment-text">Payments are secured via stripe</p>
        <div class="payment-icons">
          <i class="fab fa-cc-amex payment-icon amex"></i>
          <i class="fab fa-cc-visa payment-icon visa"></i>
          <i class="fab fa-cc-mastercard payment-icon mastercard"></i>
          <i class="fab fa-paypal payment-icon paypal"></i>
          <i class="fab fa-cc-amazon-pay payment-icon amazon-pay"></i>
          <i class="fab fa-google-pay payment-icon google-pay"></i>
          <i class="fab fa-apple-pay payment-icon apple-pay"></i>
        </div>
  </div>
  </div>
</body>
</html>
"""

        override_html = f"""<!doctype html>
<html>
<head>
    <style>

.sliding-puzzle-figure {{
  margin: auto !important;
  height: 300px !important;
  width: 300px !important;
  max-height: 70vh !important;
  max-width: 70vh !important;
  }}
  .sliding-puzzle-figure a {{
    cursor: pointer; }}
    .sliding-puzzle-figure a#shuffle {{
      color: #E74C3C; }}
    .sliding-puzzle-figure a#solve {{
      color: #3498DB; }}
  .sliding-puzzle-figure .sliding-puzzle {{
    list-style-type: none;
    position: relative;
    margin-left: auto;
    margin-right: auto;
    width: 300px;
    height: 300px;
    box-sizing: border-box;
    background-clip: border-box;
    border: 37px solid #2C3E50;
    border-radius: 10px;
    background-color: #2C3E50; }}
    .sliding-puzzle-figure .sliding-puzzle .tile {{
      position: absolute;
      background-color: #7BC8F3;
      color: #1F1F1F;
      border-radius: 10px;
      cursor: pointer;
      width: 33%;
      height: 33%;
      display: flex;
      justify-content: center;
      align-items: center;
      font-size: 0px;
      left: 0%;
      top: 0%;
      transition: all 0.5s linear;
      transition-timing-function: ease;
      box-sizing: border-box; 
      border: solid 2px; 
      border-color: #7BC8F3;}}
      .sliding-puzzle-figure .sliding-puzzle .tile#ans1 {{
      background-image: url(data:image/png;base64,{sub_image_list[0]});
      background-repeat: no-repeat;
      background-size: cover;
      background-position: center; }}
      .sliding-puzzle-figure .sliding-puzzle .tile#ans2 {{
      background-image: url(data:image/png;base64,{sub_image_list[1]});
      background-repeat: no-repeat;
      background-size: cover;
      background-position: center;}}
      .sliding-puzzle-figure .sliding-puzzle .tile#ans3 {{
      background-image: url(data:image/png;base64,{sub_image_list[2]});
      background-repeat: no-repeat;
      background-size: cover;
      background-position: center;}}
      .sliding-puzzle-figure .sliding-puzzle .tile#ans4 {{
      background-image: url(data:image/png;base64,{sub_image_list[3]});
      background-repeat: no-repeat;
      background-size: cover;
      background-position: center;}}
      .sliding-puzzle-figure .sliding-puzzle .tile#ans5 {{
      background-image: url(data:image/png;base64,{sub_image_list[4]});
      background-repeat: no-repeat;
      background-size: cover;
      background-position: center;}}
      .sliding-puzzle-figure .sliding-puzzle .tile#ans6 {{
      background-image: url(data:image/png;base64,{sub_image_list[5]});
      background-repeat: no-repeat;
      background-size: cover;
      background-position: center;}}
      .sliding-puzzle-figure .sliding-puzzle .tile#ans7 {{
      background-image: url(data:image/png;base64,{sub_image_list[6]});
      background-repeat: no-repeat;
      background-size: cover;
      background-position: center;}}
      .sliding-puzzle-figure .sliding-puzzle .tile#ans8 {{
      background-image: url(data:image/png;base64,{sub_image_list[7]});
      background-repeat: no-repeat;
      background-size: cover;
      background-position: center;}}
      .sliding-puzzle-figure .sliding-puzzle .tile.error {{
        background-color: #F0867D;
        border-color: #F0867D;}}
@media only screen and (max-width: 650px) {{
  .sliding-puzzle-figure {{
    width: 90vw;
    height: 90vw;
    max-height: 100vh; }}
    .sliding-puzzle-figure .sliding-puzzle {{
      border-width: 10px;
      border-radius: 14px; }}
    .sliding-puzzle-figure .tile {{
      font-size: 1em; }} }}
</style>

    <meta name="viewport" content="initial-scale=1.0, width=device-width">
</head>
<body>

    <figure class="sliding-puzzle-figure">

        <ul class="sliding-puzzle">
            <li class="tile" id="ans1">1</li>
            <li class="tile" id="ans2">2</li>
            <li class="tile" id="ans3">3</li>
            <li class="tile" id="ans4">4</li>
            <li class="tile" id="ans5">5</li>
            <li class="tile" id="ans6">6</li>
            <li class="tile" id="ans7">7</li>
            <li class="tile" id="ans8">8</li>
        </ul>

        <figcaption>
       A Sliding Puzzle | <a id="shuffle">Shuffle</a> | <a id="solve">Solve</a>
        </figcaption>
    </figure>


</body>
</html>"""

        yield {
            # btn2: gr.update(visible=True),
            out: override_html,
            test_html: "<html></html>",
            pay_html: payment_html
        }
        # return gr.Button.update(visible=True),gr.HTML(html2)
        # print("ok")
        # btn2.update(visible=True)
        # return html2
    # demo.load(None,None,None,_js=scripts)
    btn.click(call_api,inputs=[image,email],outputs=[out,test_html,pay_html])
    # btn2.click(None,None,None,_js=js_payment)
    # demo.load(None,None,None,_js=scripts)

demo.launch(debug=True, server_port=7680, server_name="0.0.0.0")
