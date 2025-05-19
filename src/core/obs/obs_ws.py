"""
Taken from DougDoug's ChatGodApp repo on github
https://github.com/DougDougGithub/ChatGodApp/blob/main/obs_websockets.py
"""

from dataclasses import dataclass
import time
import sys
from obswebsocket import obsws, requests  # noqa: E402


@dataclass
class OBSWebsocketsManagerSettings:
    host: str
    port: str
    password: str


class OBSWebsocketsManager:
    _ws = None

    def __init__(self, settings: OBSWebsocketsManagerSettings):
        # Connect to websockets
        self._settings = settings
        self._ws = obsws(settings.host, settings.port, settings.password)
        try:
            self._ws.connect()
        except:
            print(
                "\nPANIC!!\nCOULD NOT CONNECT TO OBS!\nDouble check that you have OBS open and that your websockets server is enabled in OBS."
            )
            time.sleep(10)
            sys.exit()
        print("Connected to OBS Websockets!\n")

    def disconnect(self):
        self._ws.disconnect()

    # Set the current scene
    def set_scene(self, new_scene):
        self._ws.call(requests.SetCurrentProgramScene(sceneName=new_scene))

    # Set the visibility of any source's filters
    def set_filter_visibility(self, source_name, filter_name, filter_enabled=True):
        self._ws.call(
            requests.SetSourceFilterEnabled(
                sourceName=source_name,
                filterName=filter_name,
                filterEnabled=filter_enabled,
            )
        )

    # Set the visibility of any source
    def set_source_visibility(self, scene_name, source_name, source_visible=True):
        response = self._ws.call(
            requests.GetSceneItemId(sceneName=scene_name, sourceName=source_name)
        )
        myItemID = response.datain["sceneItemId"]
        self._ws.call(
            requests.SetSceneItemEnabled(
                sceneName=scene_name,
                sceneItemId=myItemID,
                sceneItemEnabled=source_visible,
            )
        )

    # Returns the current text of a text source
    def get_text(self, source_name):
        response = self._ws.call(requests.GetInputSettings(inputName=source_name))
        return response.datain["inputSettings"]["text"]

    # Returns the text of a text source
    def set_text(self, source_name, new_text):
        self._ws.call(
            requests.SetInputSettings(
                inputName=source_name, inputSettings={"text": new_text}
            )
        )

    def get_source_transform(self, scene_name, source_name):
        response = self._ws.call(
            requests.GetSceneItemId(sceneName=scene_name, sourceName=source_name)
        )
        myItemID = response.datain["sceneItemId"]
        response = self._ws.call(
            requests.GetSceneItemTransform(sceneName=scene_name, sceneItemId=myItemID)
        )
        transform = {}
        transform["positionX"] = response.datain["sceneItemTransform"]["positionX"]
        transform["positionY"] = response.datain["sceneItemTransform"]["positionY"]
        transform["scaleX"] = response.datain["sceneItemTransform"]["scaleX"]
        transform["scaleY"] = response.datain["sceneItemTransform"]["scaleY"]
        transform["rotation"] = response.datain["sceneItemTransform"]["rotation"]
        transform["sourceWidth"] = response.datain["sceneItemTransform"][
            "sourceWidth"
        ]  # original width of the source
        transform["sourceHeight"] = response.datain["sceneItemTransform"][
            "sourceHeight"
        ]  # original width of the source
        transform["width"] = response.datain["sceneItemTransform"][
            "width"
        ]  # current width of the source after scaling, not including cropping. If the source has been flipped horizontally, this number will be negative.
        transform["height"] = response.datain["sceneItemTransform"][
            "height"
        ]  # current height of the source after scaling, not including cropping. If the source has been flipped vertically, this number will be negative.
        transform["cropLeft"] = response.datain["sceneItemTransform"][
            "cropLeft"
        ]  # the amount cropped off the *original source width*. This is NOT scaled, must multiply by scaleX to get current # of cropped pixels
        transform["cropRight"] = response.datain["sceneItemTransform"][
            "cropRight"
        ]  # the amount cropped off the *original source width*. This is NOT scaled, must multiply by scaleX to get current # of cropped pixels
        transform["cropTop"] = response.datain["sceneItemTransform"][
            "cropTop"
        ]  # the amount cropped off the *original source height*. This is NOT scaled, must multiply by scaleY to get current # of cropped pixels
        transform["cropBottom"] = response.datain["sceneItemTransform"][
            "cropBottom"
        ]  # the amount cropped off the *original source height*. This is NOT scaled, must multiply by scaleY to get current # of cropped pixels
        return transform

    # The transform should be a dictionary containing any of the following keys with corresponding values
    # positionX, positionY, scaleX, scaleY, rotation, width, height, sourceWidth, sourceHeight, cropTop, cropBottom, cropLeft, cropRight
    # e.g. {"scaleX": 2, "scaleY": 2.5}
    # Note: there are other transform settings, like alignment, etc, but these feel like the main useful ones.
    # Use get_source_transform to see the full list
    def set_source_transform(self, scene_name, source_name, new_transform):
        response = self._ws.call(
            requests.GetSceneItemId(sceneName=scene_name, sourceName=source_name)
        )
        myItemID = response.datain["sceneItemId"]
        self._ws.call(
            requests.SetSceneItemTransform(
                sceneName=scene_name,
                sceneItemId=myItemID,
                sceneItemTransform=new_transform,
            )
        )

    # Note: an input, like a text box, is a type of source. This will get *input-specific settings*, not the broader source settings like transform and scale
    # For a text source, this will return settings like its font, color, etc
    def get_input_settings(self, input_name):
        return self._ws.call(requests.GetInputSettings(inputName=input_name))

    # Get list of all the input types
    def get_input_kind_list(self):
        return self._ws.call(requests.GetInputKindList())

    # Get list of all items in a certain scene
    def get_scene_items(self, scene_name):
        return self._ws.call(requests.GetSceneItemList(sceneName=scene_name))
