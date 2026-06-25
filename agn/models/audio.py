"""
AGN-SDK 语音模型
"""

from typing import Any

from pydantic import BaseModel, Field

# ==================== 语音转文字 ====================


class TranscriptionWord(BaseModel):
    """
    转写词级时间戳信息
    """

    word: str = Field(..., description="词文本")
    start: float = Field(..., description="开始时间（秒）")
    end: float = Field(..., description="结束时间（秒）")
    confidence: float | None = Field(None, description="置信度（0-1）")
    speaker: int | str | None = Field(
        None, description="说话人标识（说话人分离时使用）"
    )
    punctuated_word: str | None = Field(
        None, description="带标点的词（部分服务商提供）"
    )

    model_config = {"extra": "allow"}


class TranscriptionSegment(BaseModel):
    """
    转写分段信息（带时间戳）
    """

    id: int = Field(..., description="分段 ID")
    start: float = Field(..., description="开始时间（秒）")
    end: float = Field(..., description="结束时间（秒）")
    text: str = Field(..., description="分段文本")
    avg_logprob: float | None = Field(None, description="平均对数概率")
    compression_ratio: float | None = Field(None, description="压缩比")
    no_speech_prob: float | None = Field(None, description="无语音概率")
    temperature: float | None = Field(None, description="温度系数")
    tokens: list[int] | None = Field(None, description="Token ID 列表")
    seek: int | None = Field(None, description="Seek 偏移")
    confidence: float | None = Field(None, description="分段置信度（0-1）")
    speaker: int | str | None = Field(
        None, description="说话人标识（说话人分离时使用）"
    )
    channel: int | None = Field(None, description="声道索引（多声道音频）")

    model_config = {"extra": "allow"}


class TranscriptionResult(BaseModel):
    """
    语音转文字结果
    """

    text: str = Field(..., description="完整转写文本")
    language: str | None = Field(None, description="检测到的语言")
    duration: float | None = Field(None, description="音频时长（秒）")
    segments: list[TranscriptionSegment] | None = Field(None, description="分段信息")
    words: list[TranscriptionWord] | None = Field(None, description="词级时间戳")
    task: str | None = Field(
        "transcribe", description="任务类型（transcribe/translate）"
    )
    usage: dict[str, Any] | None = Field(None, description="使用统计")
    model: str | None = Field(None, description="使用的模型 ID")

    model_config = {"extra": "allow"}


# ==================== 文字转语音 ====================


class SpeechResult(BaseModel):
    """
    文字转语音结果
    """

    audio_data: bytes | None = Field(None, description="音频二进制数据")
    audio_url: str | None = Field(None, description="音频 URL（部分 Provider 返回）")
    audio_base64: str | None = Field(None, description="音频 Base64 编码")
    content_type: str = Field("audio/mpeg", description="音频 MIME 类型")
    format: str = Field("mp3", description="音频格式（mp3/wav/opus等）")
    duration: float | None = Field(None, description="估计音频时长（秒）")
    model: str | None = Field(None, description="使用的模型 ID")

    model_config = {"extra": "allow"}

    def get_audio_bytes(self) -> bytes | None:
        """
        获取音频二进制数据

        Returns:
            音频 bytes，如果没有数据则返回 None
        """
        import base64

        if self.audio_data:
            return self.audio_data
        if self.audio_base64:
            return base64.b64decode(self.audio_base64)
        return None

    def save_to_file(self, file_path: str) -> None:
        """
        保存音频到文件

        Args:
            file_path: 输出文件路径
        """
        data = self.get_audio_bytes()
        if data:
            with open(file_path, "wb") as f:
                f.write(data)


# ==================== 语音相关枚举 ====================


class AudioResponseFormat(str):
    """
    语音响应格式常量
    """

    # 转写响应格式
    TRANSCRIBE_JSON = "json"
    TRANSCRIBE_TEXT = "text"
    TRANSCRIBE_SRT = "srt"
    TRANSCRIBE_VTT = "vtt"
    TRANSCRIBE_VERBOSE_JSON = "verbose_json"

    # TTS 音频格式
    SPEECH_MP3 = "mp3"
    SPEECH_OPUS = "opus"
    SPEECH_AAC = "aac"
    SPEECH_FLAC = "flac"
    SPEECH_WAV = "wav"
    SPEECH_PCM = "pcm"


class SpeechVoice(str):
    """
    预定义 TTS 音色常量
    """

    # OpenAI 音色
    ALLOY = "alloy"
    ECHO = "echo"
    FABLE = "fable"
    ONYX = "onyx"
    NOVA = "nova"
    SHIMMER = "shimmer"
