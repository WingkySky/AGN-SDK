"""
AGN-SDK 多 Provider 示例

展示如何使用多个 Provider。
"""

import asyncio

from agn import Client, Router, load_env


async def agnes_example():
    """Agnes AI 示例"""
    print("=" * 60)
    print("Agnes AI 示例")
    print("=" * 60)

    client = Client(provider="agnes", api_key="your-agnes-key")

    async with client:
        print("\n1. 列出 Agnes AI 模型:")
        models = await client.list_models()
        for model in models:
            print(f"   - {model.id} ({model.type})")

        print("\n2. 文本对话 (claude-3-opus):")
        response = await client.chat(
            model="claude-3-opus",
            messages=[
                {"role": "user", "content": "What is AGN-SDK?"},
            ],
        )
        print(f"   Response: {response.choices[0].message.content[:100]}...")

        print("\n3. 图像生成 (dall-e-3):")
        result = await client.image_generate(
            model="dall-e-3",
            prompt="A futuristic city skyline at night",
        )
        print(f"   Generated {len(result.data)} image(s)")


async def openai_example():
    """OpenAI 示例"""
    print("\n" + "=" * 60)
    print("OpenAI 示例")
    print("=" * 60)

    client = Client(provider="openai", api_key="your-openai-key")

    async with client:
        print("\n1. 列出 OpenAI 模型:")
        models = await client.list_models()
        for model in models:
            print(f"   - {model.id} ({model.type})")

        print("\n2. 文本对话 (gpt-4o):")
        response = await client.chat(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": "Explain machine learning in simple terms"},
            ],
        )
        print(f"   Response: {response.choices[0].message.content[:100]}...")


async def azure_example():
    """Azure OpenAI 示例"""
    print("\n" + "=" * 60)
    print("Azure OpenAI 示例")
    print("=" * 60)

    client = Client(
        provider="azure",
        api_key="your-azure-key",
        resource_name="your-resource-name",
        deployment_id="your-deployment-id",
    )

    async with client:
        print("\n1. 列出 Azure 模型:")
        models = await client.list_models()
        for model in models:
            print(f"   - {model.id} ({model.type})")


async def router_example():
    """路由器示例（多 Provider）"""
    print("\n" + "=" * 60)
    print("路由器示例（多 Provider）")
    print("=" * 60)

    providers = [
        {"provider_type": "agnes", "api_key": "agnes-key"},
        {"provider_type": "openai", "api_key": "openai-key"},
        {"provider_type": "azure", "api_key": "azure-key", "resource_name": "azure-resource", "deployment_id": "azure-deployment"},
    ]

    router = Router(providers=providers)

    async with router:
        print("\n1. 列出所有 Provider 的模型:")
        models = await router.list_models()
        for model in models:
            print(f"   - {model.id} ({model.type}) from {model.provider}")

        print("\n2. 自动路由到 Agnes AI (claude-3-opus):")
        response = await router.chat(
            model="claude-3-opus",
            messages=[{"role": "user", "content": "Hello!"}],
        )
        print(f"   Provider: Agnes AI")
        print(f"   Response: {response.choices[0].message.content[:50]}...")

        print("\n3. 自动路由到 OpenAI (gpt-4o):")
        response = await router.chat(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Hello!"}],
        )
        print(f"   Provider: OpenAI")
        print(f"   Response: {response.choices[0].message.content[:50]}...")


async def main():
    """主函数"""
    print("AGN-SDK Multi-Provider Demo")
    print("=" * 60)
    print("Note: Replace 'your-xxx-key' with real API keys")
    print("=" * 60)

    try:
        await agnes_example()
        await openai_example()
        await azure_example()
        await router_example()
    except Exception as e:
        print(f"\nError: {e}")
        print("\nThis is just a demo. Replace with real API keys to run.")


if __name__ == "__main__":
    load_env()
    asyncio.run(main())
