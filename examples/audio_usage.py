"""
AGN-SDK 语音功能使用示例

展示语音转文字（ASR）、语音翻译、文字转语音（TTS）的使用方法。
"""

import asyncio
import os

from agn import Client, SpeechOptions, SpeechVoice, TranscribeOptions


async def transcribe_example():
    """
    语音转文字示例

    支持的输入格式：
    - 本地文件路径
    - 音频 URL
    - base64 编码音频
    - bytes 二进制数据
    """
    print("=" * 60)
    print("1. 语音转文字（ASR）示例")
    print("=" * 60)

    client = Client(
        provider="openai",
        api_key=os.getenv("OPENAI_API_KEY", "your-api-key"),
    )

    async with client:
        # 方式1：简单调用（直接传文件路径）
        print("\n方式1：简单调用")
        result = await client.transcribe(
            model="whisper-1",
            file="/path/to/audio.mp3",
            language="zh",
            prompt="这是一段关于人工智能的对话",
        )
        print(f"   识别文本: {result.text}")
        print(f"   语言: {result.language}")
        print(f"   时长: {result.duration}秒")

        # 方式2：使用 TranscribeOptions（支持分段和词级时间戳）
        print("\n方式2：带时间戳的详细转写")
        options = TranscribeOptions(
            file="/path/to/audio.mp3",
            model="whisper-1",
            language="zh",
            response_format="verbose_json",
            timestamp_granularities=["word", "segment"],
            temperature=0.2,
        )
        result = await client.transcribe(
            model="whisper-1",
            file=options.file,
            options=options,
        )
        print(f"   完整文本: {result.text}")
        if result.segments:
            print("   分段信息:")
            for seg in result.segments[:3]:
                print(f"     [{seg.start:.1f}s-{seg.end:.1f}s] {seg.text[:50]}...")
        if result.words:
            print("   词级时间戳（前5个）:")
            for w in result.words[:5]:
                print(f"     [{w.start:.2f}s-{w.end:.2f}s] {w.word}")


async def translate_example():
    """
    语音翻译示例

    将任何语言的音频翻译为英文文本。
    """
    print("\n" + "=" * 60)
    print("2. 语音翻译示例（翻译为英文）")
    print("=" * 60)

    client = Client(
        provider="openai",
        api_key=os.getenv("OPENAI_API_KEY", "your-api-key"),
    )

    async with client:
        result = await client.translate(
            model="whisper-1",
            file="/path/to/chinese_audio.mp3",
            prompt="This is a technology discussion",
        )
        print(f"   翻译结果（英文）: {result.text}")
        print(f"   任务类型: {result.task}")


async def speech_example():
    """
    文字转语音（TTS）示例

    支持多种音色和输出格式。
    """
    print("\n" + "=" * 60)
    print("3. 文字转语音（TTS）示例")
    print("=" * 60)

    client = Client(
        provider="openai",
        api_key=os.getenv("OPENAI_API_KEY", "your-api-key"),
    )

    async with client:
        # 方式1：简单调用
        print("\n方式1：简单 TTS 调用")
        result = await client.speech(
            model="tts-1",
            input="你好，欢迎使用 AGN-SDK 多模态人工智能开发工具包！",
            voice=SpeechVoice.NOVA,
            response_format="mp3",
            speed=1.0,
        )

        # 保存到文件
        output_path = "output.mp3"
        result.save_to_file(output_path)
        print(f"   音频已保存到: {output_path}")
        print(f"   音频格式: {result.content_type}")

        # 方式2：使用 SpeechOptions（高清模型）
        print("\n方式2：高清 TTS（tts-1-hd）")
        options = SpeechOptions(
            input="Hello! This is a high definition text to speech demo.",
            voice=SpeechVoice.ALLOY,
            response_format="wav",
            speed=1.1,
        )
        result = await client.speech(
            model="tts-1-hd",
            input=options.input,
            voice=options.voice,
            options=options,
        )
        result.save_to_file("output_hd.wav")
        print("   高清音频已保存到: output_hd.wav")


async def list_audio_models():
    """列出可用的语音模型"""
    print("\n" + "=" * 60)
    print("4. 列出可用语音模型")
    print("=" * 60)

    client = Client(
        provider="openai",
        api_key=os.getenv("OPENAI_API_KEY", "your-api-key"),
    )

    async with client:
        models = await client.list_models(model_type="audio")
        print(f"\n共找到 {len(models)} 个语音模型:")
        for m in models:
            caps = ", ".join(m.capabilities)
            print(f"  - {m.id}")
            print(f"    名称: {m.name}")
            print(f"    能力: {caps}")
            print()


async def router_audio_example():
    """使用 Router 进行多 Provider 语音调用"""
    print("\n" + "=" * 60)
    print("5. Router 多 Provider 语音示例（带 Fallback）")
    print("=" * 60)

    from agn import Router

    providers = [
        {"provider_type": "openai", "api_key": os.getenv("OPENAI_API_KEY", "")},
        # 可以添加更多 Provider，会自动 Fallback
    ]

    router = Router(providers=providers, default_provider="openai")

    async with router:
        # 自动选择可用的 Provider
        result = await router.speech(
            model="tts-1",
            input="这是通过 Router 调用的语音合成",
            voice="alloy",
        )
        result.save_to_file("router_output.mp3")
        print("   音频已保存到: router_output.mp3")


async def main():
    """主函数"""
    print("AGN-SDK 语音功能 Demo")
    print()
    print("注意：运行此示例需要设置 OPENAI_API_KEY 环境变量")
    print("示例代码展示 API 用法，替换文件路径和 API Key 即可运行")

    # 以下示例已注释，取消注释并填入真实参数即可运行
    # await list_audio_models()
    # await transcribe_example()
    # await translate_example()
    # await speech_example()
    # await router_audio_example()

    print("\n" + "=" * 60)
    print("支持的语音模型:")
    print("  OpenAI:")
    print("    - whisper-1: 语音转文字 + 翻译")
    print("    - gpt-4o-transcribe: GPT-4o 增强转写")
    print("    - gpt-4o-mini-transcribe: GPT-4o Mini 快速转写")
    print("    - tts-1: 标准 TTS")
    print("    - tts-1-hd: 高清 TTS")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
