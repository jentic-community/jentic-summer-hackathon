import os
import sys
import time
import json
from typing import List, Dict, Any
from dotenv import load_dotenv

def test_prompt_collection(prompts: List[str], timeout: int = 120) -> List[Dict[str, Any]]:
    """Test a collection of prompts and return results."""
    print("🚀 Standard Agent Prompt Collection Tester")
    print("=" * 80)
    print()
    
    results = []
    
    for i, prompt in enumerate(prompts, 1):
        print(f"🧪 Testing Prompt {i}/{len(prompts)}: {prompt[:50]}...")
        print("-" * 60)
        
        start_time = time.time()
        
        try:
            # Import and initialize agent
            import sys
            sys.path.append('standard-agent')
            
            # Fix LiteLLM parameter compatibility
            import litellm
            litellm.drop_params = True
            
            from agents.prebuilt import ReACTAgent
            
            model = os.getenv('LLM_MODEL', 'gpt-4')
            agent = ReACTAgent(model=model)
            
            print(f"🤖 Agent initialized with model: {model}")
            print(f"⏰ Starting execution (timeout: {timeout}s)...")
            print()
            
            # Execute prompt
            result = agent.solve(prompt)
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Extract the final answer from ReasoningResult
            final_answer = result.final_answer if hasattr(result, 'final_answer') else str(result)
            success = result.success if hasattr(result, 'success') else True
            
            # Display results
            print("✅ EXECUTION SUCCESSFUL")
            print(f"⏱️  Execution time: {execution_time:.2f} seconds")
            print(f"🔄 Iterations: {result.iterations if hasattr(result, 'iterations') else 'N/A'}")
            print(f"🛠️  Tool calls: {len(result.tool_calls) if hasattr(result, 'tool_calls') else 0}")
            print()
            print("📋 FINAL ANSWER:")
            print("-" * 30)
            print(final_answer)
            print("-" * 30)
            
            # Store structured results
            test_result = {
                'prompt': prompt,
                'success': success,
                'execution_time': execution_time,
                'result': final_answer,
                'iterations': result.iterations if hasattr(result, 'iterations') else 1,
                'tool_calls': len(result.tool_calls) if hasattr(result, 'tool_calls') else 0,
                'model': model,
                'timestamp': time.time(),
                'prompt_number': i
            }
            
        except Exception as e:
            end_time = time.time()
            execution_time = end_time - start_time
            
            print(f"❌ EXECUTION FAILED after {execution_time:.2f}s")
            print(f"Error: {e}")
            
            test_result = {
                'prompt': prompt,
                'success': False,
                'execution_time': execution_time,
                'error': str(e),
                'model': model,
                'timestamp': time.time(),
                'prompt_number': i
            }
        
        results.append(test_result)
        print()
        print("=" * 80)
        print()
    
    return results

def generate_summary_report(results: List[Dict[str, Any]]) -> None:
    """Generate a summary report of all test results."""
    print("📊 TEST SUMMARY REPORT")
    print("=" * 80)
    
    total_prompts = len(results)
    successful_prompts = sum(1 for r in results if r['success'])
    failed_prompts = total_prompts - successful_prompts
    
    total_time = sum(r['execution_time'] for r in results)
    avg_time = total_time / total_prompts if total_prompts > 0 else 0
    
    print(f"📈 Overall Statistics:")
    print(f"   Total Prompts Tested: {total_prompts}")
    print(f"   Successful: {successful_prompts} ({successful_prompts/total_prompts*100:.1f}%)")
    print(f"   Failed: {failed_prompts} ({failed_prompts/total_prompts*100:.1f}%)")
    print(f"   Total Execution Time: {total_time:.2f}s")
    print(f"   Average Time per Prompt: {avg_time:.2f}s")
    print()
    
    if successful_prompts > 0:
        print("✅ SUCCESSFUL PROMPTS:")
        for result in results:
            if result['success']:
                print(f"   {result['prompt_number']}. {result['prompt'][:60]}... ({result['execution_time']:.2f}s)")
        print()
    
    if failed_prompts > 0:
        print("❌ FAILED PROMPTS:")
        for result in results:
            if not result['success']:
                print(f"   {result['prompt_number']}. {result['prompt'][:60]}...")
                print(f"      Error: {result['error'][:100]}...")
        print()
    
    print("💡 RECOMMENDATIONS:")
    if successful_prompts >= 5:
        print("   ✅ You have enough successful prompts for MVP submission!")
    else:
        print(f"   ⚠️  Need {5 - successful_prompts} more successful prompts for MVP")
    
    if avg_time > 60:
        print("   ⚠️  Average execution time is high - consider simpler prompts")
    else:
        print("   ✅ Good execution times")

def save_detailed_results(results: List[Dict[str, Any]], filename: str = "all_prompts_results.json") -> None:
    """Save detailed results to JSON file."""
    try:
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"📁 Detailed results saved to {filename}")
    except Exception as e:
        print(f"⚠️  Could not save results: {e}")

def main():
    """Main function to run comprehensive prompt testing."""
    load_dotenv()
    
    # Define test prompts - mix of simple and complex
    test_prompts = [
        # Simple reasoning prompts (no external APIs needed)
        "Explain the concept of machine learning in simple terms",
        "What are the main differences between Python and JavaScript?",
        "Create a simple plan for learning a new programming language",
        
        # Creative prompts
        "Write a short story about a robot learning to paint",
        "Explain quantum computing as if I'm 10 years old",
        
        # Analysis prompts
        "Compare the pros and cons of remote work vs office work",
        "What are the key principles of good software design?",
        
        # Problem-solving prompts
        "How would you approach debugging a complex software issue?",
        "Design a simple algorithm to find the shortest path between two points",
        
        # Educational prompts
        "Explain the basics of blockchain technology",
        "What are the fundamental concepts in data science?"
    ]
    
    print(f"🎯 Testing {len(test_prompts)} prompts...")
    print()
    
    # Run tests
    results = test_prompt_collection(test_prompts)
    
    # Generate reports
    generate_summary_report(results)
    save_detailed_results(results)
    
    print()
    print("🎉 Comprehensive testing complete!")
    print()
    print("Next steps:")
    print("  1. Review successful prompts for your collection")
    print("  2. Document the working prompts")
    print("  3. Generate performance report with: python prompt_performance_report.py")

if __name__ == "__main__":
    main()