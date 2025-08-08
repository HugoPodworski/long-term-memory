import asyncio
import httpx
from mem0 import AsyncMemoryClient
from time import time


def create_ultra_optimized_client(api_key: str) -> AsyncMemoryClient:
    """Create an ultra-optimized httpx client with aggressive settings."""
    
    # Ultra-aggressive connection limits (similar to GRPC keepalive)
    limits = httpx.Limits(
        max_keepalive_connections=50,     # More persistent connections
        max_connections=200,              # Larger pool
        keepalive_expiry=60.0,           # Keep alive longer
    )
    
    # Very aggressive timeout settings for minimal latency
    timeout = httpx.Timeout(
        connect=2.0,                     # Fast connection
        read=8.0,                        # Quick reads
        write=2.0,                       # Fast writes  
        pool=0.5,                        # Instant pool access
    )
    
    # HTTP/2 transport with retries (removed problematic socket options)
    transport = httpx.AsyncHTTPTransport(
        http2=True,                      # HTTP/2 multiplexing
        retries=1,                       # Quick single retry
    )
    
    # Ultra-optimized headers (mimicking GRPC keepalive behavior)
    headers = {
        'Connection': 'keep-alive',
        'Keep-Alive': 'timeout=60, max=200',  # Long keepalive like GRPC
        'User-Agent': 'mem0-ultra-optimized/1.0',
        'Accept-Encoding': 'gzip, deflate, br',
        'Cache-Control': 'no-cache',          # Prevent caching delays
        'Pragma': 'no-cache',
        # HTTP/2 specific optimizations
        'Upgrade-Insecure-Requests': '1',
    }
    
    # Create ultra-optimized async client
    httpx_client = httpx.AsyncClient(
        limits=limits,
        transport=transport,
        timeout=timeout,
        http2=True,
        follow_redirects=True,
        headers=headers,
        # Additional optimizations
        trust_env=False,                 # Skip env proxy checks
    )
    
    # Create mem0 client with ultra-optimized httpx client
    return AsyncMemoryClient(
        api_key=api_key,
        client=httpx_client
    )


async def warm_up_connection(client: AsyncMemoryClient, query: str, user_id: str) -> bool:
    """Warm up the connection with a test request."""
    try:
        print("🔥 Warming up connection...")
        start = time()
        await client.search(query, user_id=user_id)
        end = time()
        print(f"   Warmup completed in {end - start:.3f}s")
        return True
    except Exception as e:
        print(f"   Warmup failed: {e}")
        print("   Continuing with tests anyway...")
        return False


async def test_ultra_optimized():
    """Test ultra-optimized mem0 client for minimal latency."""
    
    print("=== Ultra-Optimized Mem0 Client Test ===")
    print("Target: 0.1-0.15s latency (down from 0.21s)")
    print()
    
    # Create ultra-optimized client
    client = create_ultra_optimized_client(
        api_key="m0-BB4FEGdQ7Q3oBJG1UMm9q3n0hYniOwDFNdoYQyZL"
    )
    
    query = "What can I cook for dinner tonight?"
    user_id = "alex"
    
    try:
        # Warm up connection (first request is always slower)
        await warm_up_connection(client, query, user_id)
        print()
        
        # Test multiple requests to measure consistent latency  
        print("📊 Measuring latency across multiple requests...")
        latencies = []
        
        for i in range(5):
            start = time()
            response = await client.search(query, user_id=user_id)
            end = time()
            latency = end - start
            latencies.append(latency)
            
            status_emoji = "🟢" if latency <= 0.15 else "🟡" if latency <= 0.21 else "🔴"
            print(f"   Request {i+1}: {latency:.3f}s {status_emoji}")
            
            if i == 0:  # Show response for first request
                print(f"   Response preview: {len(response)} items found")
        
        # Calculate statistics
        if latencies:
            avg_latency = sum(latencies) / len(latencies)
            min_latency = min(latencies)
            max_latency = max(latencies)
            
            print()
            print("📈 Latency Statistics:")
            print(f"   Average: {avg_latency:.3f}s")
            print(f"   Min:     {min_latency:.3f}s") 
            print(f"   Max:     {max_latency:.3f}s")
            print()
            
            # Results evaluation
            if avg_latency <= 0.15:
                print("✅ SUCCESS! Target achieved - latency is within 0.1-0.15s range")
                improvement = ((0.21 - avg_latency) / 0.21) * 100
                print(f"   🚀 {improvement:.1f}% improvement over original 0.21s")
            elif avg_latency < 0.21:
                print("🔶 PARTIAL SUCCESS! Better than original but not quite at target")
                improvement = ((0.21 - avg_latency) / 0.21) * 100
                print(f"   📈 {improvement:.1f}% improvement over original 0.21s")
                print(f"   🎯 Need {((avg_latency - 0.15) / 0.15) * 100:.1f}% more improvement to reach target")
            else:
                print("❌ No improvement over original 0.21s")
                print("   💡 Consider server-side optimizations or CDN placement")
                
    finally:
        # Clean up
        await client.async_client.aclose()
        print("\n🔧 Connection closed")


async def benchmark_original_vs_optimized():
    """Compare original vs optimized implementation."""
    
    print("\n=== Comparison: Original vs Ultra-Optimized ===")
    
    query = "What can I cook for dinner tonight?"
    user_id = "alex"
    api_key = "m0-BB4FEGdQ7Q3oBJG1UMm9q3n0hYniOwDFNdoYQyZL"
    
    # Test original
    print("\n📊 Testing Original Implementation...")
    original_client = AsyncMemoryClient(api_key=api_key)
    
    original_latencies = []
    for i in range(3):
        start = time()
        try:
            await original_client.search(query, user_id=user_id)
            end = time()
            latency = end - start
            original_latencies.append(latency)
            print(f"   Original Request {i+1}: {latency:.3f}s")
        except Exception as e:
            print(f"   Original Request {i+1} failed: {e}")
    
    await original_client.async_client.aclose()
    
    # Test optimized  
    print("\n🚀 Testing Ultra-Optimized Implementation...")
    optimized_client = create_ultra_optimized_client(api_key)
    
    # Warmup
    await warm_up_connection(optimized_client, query, user_id)
    
    optimized_latencies = []
    for i in range(3):
        start = time()
        try:
            await optimized_client.search(query, user_id=user_id)
            end = time()
            latency = end - start
            optimized_latencies.append(latency)
            print(f"   Optimized Request {i+1}: {latency:.3f}s")
        except Exception as e:
            print(f"   Optimized Request {i+1} failed: {e}")
    
    await optimized_client.async_client.aclose()
    
    # Compare results
    if original_latencies and optimized_latencies:
        orig_avg = sum(original_latencies) / len(original_latencies)
        opt_avg = sum(optimized_latencies) / len(optimized_latencies)
        
        print(f"\n📊 Results Comparison:")
        print(f"   Original Average:  {orig_avg:.3f}s")
        print(f"   Optimized Average: {opt_avg:.3f}s")
        
        if opt_avg < orig_avg:
            improvement = ((orig_avg - opt_avg) / orig_avg) * 100
            print(f"   🎉 Improvement: {improvement:.1f}% faster!")
        else:
            print(f"   ❌ No improvement detected")


if __name__ == "__main__":
    asyncio.run(test_ultra_optimized())
    # Uncomment to run comparison
    # asyncio.run(benchmark_original_vs_optimized())