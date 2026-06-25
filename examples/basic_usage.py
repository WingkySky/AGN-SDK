"""
AGN-SDK 基础用法示例

展示 SDK 的基本使用方法。
"""

import asyncio

from agn import Client, Router


async def basic_usage_example():
    """基础用法示例"""
    print("=" * 60)
    print("AGN-SDK 基础用法示例")
    print("=" * 60)

    # 创建客户端
    client = Client(
        provider="agnes",
        api_key="your-api-key",
        base_url="https://api.agnes.ai/v1",
    )

    async with client:
        # 列出可用模型
        print("\n1. 列出可用模型:")
        models = await client.list_models()
        for model in models:
            print(f"   - {model.id} ({model.type})")

        # 文本对话
        print("\n2. 文本对话:")
        response = await client.chat(
            model="claude-3-opus",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello! What can you do?"},
            ],
            temperature=0.7,
        )
        print(f"   Response: {response.choices[0].message.content[:100]}...")
        print(f"   Usage: {response.usage.total_tokens} tokens")

        # 图像生成
        print("\n3. 图像生成:")
        result = await client.image_generate(
            model="dall-e-3",
            prompt="A beautiful sunset over the ocean with dolphins jumping",
            size="1024x1024",
            n=1,
        )
        print(f"   Generated {len(result.data)} image(s)")
        if result.data:
            print(f"   URL: {result.data[0].url[:50]}...")

        # 视频生成
        print("\n4. 视频生成:")
        task = await client.video_create(
            model="video-gen-1",
            prompt="A cat walking through a forest",
            width=1280,
            height=720,
        )
        print(f"   Task ID: {task.task_id}")
        print(f"   Status: {task.status}")

        # 轮询视频状态
        print("\n5. 轮询视频状态:")
        status = await client.video_poll(task.task_id)
        print(f"   Status: {status.status}")
        if status.video_url:
            print(f"   URL: {status.video_url}")


async def router_example():
    """路由器示例"""
    print("\n" + "=" * 60)
    print("AGN-SDK 路由器示例")
    print("=" * 60)

    # 配置多个 Provider
    providers = [
        {"provider_type": "agnes", "api_key": "agnes-key"},
        {"provider_type": "openai", "api_key": "openai-key"},
    ]

    router = Router(providers=providers, default_provider="agnes")

    async with router:
        # 列出所有模型
        print("\n1. 列出所有可用模型:")
        models = await router.list_models()
        for model in models:
            print(f"   - {model.id} ({model.type}) from {model.provider}")


async def main():
    """主函数"""
    print("AGN-SDK Demo")
    print("=" * 60)

    try:
        await basic_usage_example()
        await router_example()
    except Exception as e:
        print(f"\nError: {e}")
        print("\nNote: This is just a demo. Replace 'your-api-key' with a real API key.")


if __name__ == "__main__":
    asyncio.run(main())
