from typing import AnyStr

from gentopia.tools.gradio_tools.tools import BarkTextToSpeechTool, StableDiffusionTool, DocQueryDocumentAnsweringTool, \
    ImageCaptioningTool, TextToVideoTool, WhisperAudioTranscriptionTool, ClipInterrogatorTool
from gentopia.tools.basetool import *


class TTSArgs(BaseModel):
    text: str = Field(..., description="natural language texts. English prefered")


class TTS(BaseTool):
    name = "text-to-speech"
    description = "Converting text into sounds that sound like a human read it, the output is a local path where the generated audio is stored"
    args_schema: Optional[Type[BaseModel]] = TTSArgs

    def _run(self, text: AnyStr) -> Any:
        bk = BarkTextToSpeechTool()
        path = bk.run(text)
        ans = f"the audio file saved into: {path}"
        return ans

    async def _arun(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError


class ImageCaptionArgs(BaseModel):
    path_to_image: str = Field(..., description="path to the image file.")


class ImageCaption(BaseTool):
    name = "image_caption"
    description = "Generating a caption for an image, the output is caption text"
    args_schema: Optional[Type[BaseModel]] = ImageCaptionArgs

    def _run(self, path_to_image: AnyStr) -> Any:
        ans = ImageCaptioningTool().run(f"{path_to_image}")
        return ans

    async def _arun(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError


class TextToImageArgs(BaseModel):
    text: str = Field(..., description="a text descrption of the image to be generated")


class TextToImage(BaseTool):
    name = "text_to_image"
    description = "A tool to generate images based on text input, the output is a local path where the generated image is stored."
    args_schema: Optional[Type[BaseModel]] = TextToImageArgs

    def _run(self, text: AnyStr) -> Any:
        ans = StableDiffusionTool().run(text)
        return f"the image file saved into: {ans}"

    async def _arun(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError


class TextToVideoArgs(BaseModel):
    text: str = Field(..., description="a text descrption of the video to be generated")


class TextToVideo(BaseTool):
    name = "Text2Video"
    description = "generate videos based on text input"
    args_schema: Optional[Type[BaseModel]] = TextToVideoArgs

    def _run(self, text: AnyStr) -> Any:
        ans = TextToVideoTool().run(text)
        return f"the video file saved into: {ans}"

    async def _arun(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError


class ImageToPromptArgs(BaseModel):
    path_to_image: str = Field(..., description="local path to the image file")


class ImageToPrompt(BaseTool):
    name = "Image2Prompt"
    description = "creating a prompt for Stable Diffusion that matches the input image"
    args_schema: Optional[Type[BaseModel]] = ImageToPromptArgs

    def _run(self, path_to_image: AnyStr) -> Any:
        ans = ClipInterrogatorTool().run(path_to_image)
        return ans

    async def _arun(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError


if __name__ == "__main__":
    ans = TTS()._run("Please surprise me and speak in whatever voice you enjoy. Vielen Dank und Gesundheit!")
    # ans = ImageCaption()._run("tools/image.jpg")
    # ans = TextToImage()._run("an asian student wearing a black t-shirt")
    # ans = TextToVideo()._run("an asian student wearing a black t-shirt")
    # ans = ImageToPrompt()._run("image.jpg")
    print(ans)
