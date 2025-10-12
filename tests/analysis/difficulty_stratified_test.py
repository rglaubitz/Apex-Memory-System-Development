#!/usr/bin/env python3
"""
Difficulty-Stratified Performance Testing Script

Runs 250 queries across easy/medium/hard difficulty tiers through the query router
and collects stratified performance metrics with confusion matrix analysis.

Usage:
    python3 tests/analysis/difficulty_stratified_test.py [--test-suite PATH] [--use-hybrid]

Arguments:
    --test-suite PATH    Path to test suite JSON file (default: config/difficulty-stratified-queries.json)
    --use-hybrid         Enable hybrid classifier (keyword + embeddings cascade)

Outputs:
    - stratified_results.json: Detailed results for each query
    - stratified_summary.txt: Human-readable summary
    - confusion_matrix.txt: Intent prediction confusion analysis
"""

import argparse
import json
import time
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import statistics
from collections import defaultdict

# Configuration
API_BASE = "http://localhost:8000"
QUERY_ENDPOINT = f"{API_BASE}/api/v1/query/"
HEALTH_ENDPOINT = f"{API_BASE}/api/v1/query/health"
RESULTS_DIR = Path("/Users/richardglaubitz/Projects/apex-memory-system/monitoring/stratified")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def check_api_health() -> bool:
    """Verify API is healthy before testing."""
    try:
        response = requests.get(HEALTH_ENDPOINT, timeout=10)
        if response.status_code == 200:
            health = response.json()
            print(f"✅ API Health: {health['overall']}")
            for component, status in health['components'].items():
                print(f"   - {component}: {status['status']}")
            return health['overall'] == 'healthy'
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API health check error: {e}")
        return False


def run_query(query_data: Dict[str, Any], query_index: int, total: int, use_hybrid: bool = False) -> Dict[str, Any]:
    """Execute a single query and collect metrics."""
    query_text = query_data['query']
    expected_intent = query_data['intent']
    difficulty = query_data['difficulty']

    print(f"\n[{query_index}/{total}] ({difficulty.upper()}) Testing: {query_text[:60]}...")

    start_time = time.time()

    try:
        # Note: use_hybrid flag is for test reporting only.
        # Hybrid classification must be enabled at router initialization time.
        # To test hybrid mode, start the API with enable_hybrid_classification=True
        payload = {
            "query": query_text,
            "limit": 10,
            "use_cache": False
        }

        response = requests.post(
            QUERY_ENDPOINT,
            json=payload,
            timeout=30
        )

        end_time = time.time()
        latency = end_time - start_time

        if response.status_code == 200:
            result = response.json()

            actual_intent = result.get('intent', 'unknown')
            correct = (actual_intent == expected_intent)

            print(f"   {'✅' if correct else '❌'} Latency: {latency:.3f}s | Intent: {actual_intent} (expected: {expected_intent}) {'✓' if correct else '✗'}")

            return {
                "query_id": query_data.get('id', f"q{query_index}"),
                "query": query_text,
                "expected_intent": expected_intent,
                "actual_intent": actual_intent,
                "intent_correct": correct,
                "difficulty": difficulty,
                "difficulty_rationale": query_data.get('difficulty_rationale', ''),
                "databases_used": result.get('databases_used', []),
                "result_count": result.get('result_count', 0),
                "cached": result.get('cached', False),
                "latency_seconds": latency,
                "status": "success",
                "timestamp": datetime.now().isoformat()
            }
        else:
            print(f"   ❌ Error: {response.status_code}")
            return {
                "query_id": query_data.get('id', f"q{query_index}"),
                "query": query_text,
                "expected_intent": expected_intent,
                "difficulty": difficulty,
                "status": "error",
                "error_code": response.status_code,
                "error_message": response.text,
                "latency_seconds": time.time() - start_time,
                "timestamp": datetime.now().isoformat()
            }

    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        return {
            "query_id": query_data.get('id', f"q{query_index}"),
            "query": query_text,
            "expected_intent": expected_intent,
            "difficulty": difficulty,
            "status": "exception",
            "error_message": str(e),
            "latency_seconds": time.time() - start_time,
            "timestamp": datetime.now().isoformat()
        }


def calculate_confusion_matrix(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate intent classification confusion matrix."""
    intents = ['graph', 'temporal', 'semantic', 'metadata']
    confusion = {intent: {other: 0 for other in intents + ['unknown']} for intent in intents}

    successful = [r for r in results if r['status'] == 'success']

    for r in successful:
        expected = r['expected_intent']
        actual = r['actual_intent']
        if expected in confusion:
            if actual in confusion[expected]:
                confusion[expected][actual] += 1
            else:
                confusion[expected]['unknown'] += 1

    return confusion


def calculate_metrics(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate comprehensive metrics from test results."""
    successful = [r for r in results if r['status'] == 'success']

    if not successful:
        return {"error": "No successful queries"}

    latencies = [r['latency_seconds'] for r in successful]
    correct_intents = [r for r in successful if r.get('intent_correct', False)]

    # Overall metrics
    overall_metrics = {
        "total_queries": len(results),
        "successful_queries": len(successful),
        "failed_queries": len(results) - len(successful),
        "success_rate": (len(successful) / len(results)) * 100,
        "overall_accuracy": (len(correct_intents) / len(successful)) * 100,
        "correct_count": len(correct_intents),
        "total_count": len(successful)
    }

    # Latency metrics
    latency_metrics = {
        "p50_seconds": statistics.median(latencies),
        "p90_seconds": statistics.quantiles(latencies, n=10)[8] if len(latencies) > 1 else latencies[0],
        "p99_seconds": statistics.quantiles(latencies, n=100)[98] if len(latencies) > 2 else max(latencies),
        "mean_seconds": statistics.mean(latencies),
        "min_seconds": min(latencies),
        "max_seconds": max(latencies)
    }

    # Metrics by difficulty tier
    difficulty_metrics = {}
    for difficulty in ['easy', 'medium', 'hard']:
        tier_results = [r for r in successful if r.get('difficulty') == difficulty]
        if tier_results:
            tier_correct = [r for r in tier_results if r.get('intent_correct', False)]
            tier_latencies = [r['latency_seconds'] for r in tier_results]

            difficulty_metrics[difficulty] = {
                "total": len(tier_results),
                "correct": len(tier_correct),
                "accuracy": (len(tier_correct) / len(tier_results)) * 100,
                "avg_latency": statistics.mean(tier_latencies),
                "median_latency": statistics.median(tier_latencies)
            }

    # Metrics by intent within each difficulty tier
    intent_by_difficulty = {}
    for difficulty in ['easy', 'medium', 'hard']:
        intent_by_difficulty[difficulty] = {}
        for intent in ['graph', 'temporal', 'semantic', 'metadata']:
            intent_tier_results = [
                r for r in successful
                if r.get('difficulty') == difficulty and r['expected_intent'] == intent
            ]
            if intent_tier_results:
                correct = len([r for r in intent_tier_results if r.get('intent_correct', False)])
                intent_by_difficulty[difficulty][intent] = {
                    'total': len(intent_tier_results),
                    'correct': correct,
                    'accuracy': (correct / len(intent_tier_results)) * 100
                }

    # Overall intent accuracy (across all difficulties)
    intent_accuracy = {}
    for intent in ['graph', 'temporal', 'semantic', 'metadata']:
        intent_queries = [r for r in successful if r['expected_intent'] == intent]
        if intent_queries:
            correct = len([r for r in intent_queries if r.get('intent_correct', False)])
            intent_accuracy[intent] = {
                'total': len(intent_queries),
                'correct': correct,
                'accuracy': (correct / len(intent_queries)) * 100
            }

    # Confusion matrix
    confusion_matrix = calculate_confusion_matrix(results)

    # Database usage
    db_usage = {}
    for r in successful:
        for db in r.get('databases_used', []):
            db_usage[db] = db_usage.get(db, 0) + 1

    # Failure analysis (incorrect predictions by difficulty)
    failures = [r for r in successful if not r.get('intent_correct', False)]
    failure_analysis = {
        'total_failures': len(failures),
        'by_difficulty': {},
        'examples': []
    }

    for difficulty in ['easy', 'medium', 'hard']:
        diff_failures = [f for f in failures if f.get('difficulty') == difficulty]
        if diff_failures:
            failure_analysis['by_difficulty'][difficulty] = {
                'count': len(diff_failures),
                'percentage': (len(diff_failures) / len([r for r in successful if r.get('difficulty') == difficulty])) * 100
            }

    # Add failure examples (first 10)
    for f in failures[:10]:
        failure_analysis['examples'].append({
            'query': f['query'],
            'expected': f['expected_intent'],
            'actual': f['actual_intent'],
            'difficulty': f['difficulty'],
            'rationale': f.get('difficulty_rationale', '')
        })

    return {
        "overall": overall_metrics,
        "latency": latency_metrics,
        "by_difficulty": difficulty_metrics,
        "intent_by_difficulty": intent_by_difficulty,
        "intent_overall": intent_accuracy,
        "confusion_matrix": confusion_matrix,
        "database_routing": {
            "usage_counts": db_usage,
            "most_used": max(db_usage, key=db_usage.get) if db_usage else None
        },
        "failure_analysis": failure_analysis,
        "cache_performance": {
            "hit_rate": 0.0,
            "note": "Cache disabled for testing"
        }
    }


def format_confusion_matrix(confusion: Dict[str, Dict[str, int]]) -> str:
    """Format confusion matrix for display."""
    intents = ['graph', 'temporal', 'semantic', 'metadata']

    lines = []
    lines.append("\n" + "="*80)
    lines.append("CONFUSION MATRIX - Intent Classification")
    lines.append("="*80)
    lines.append("")
    lines.append("Predicted Intent (columns) vs Expected Intent (rows):")
    lines.append("")

    # Header
    header = "Expected      |"
    for intent in intents:
        header += f" {intent:10s} |"
    header += " unknown |"
    lines.append(header)
    lines.append("-" * len(header))

    # Rows
    for expected in intents:
        row = f"{expected:13s} |"
        for predicted in intents:
            count = confusion[expected].get(predicted, 0)
            row += f" {count:10d} |"
        unknown_count = confusion[expected].get('unknown', 0)
        row += f" {unknown_count:7d} |"
        lines.append(row)

    lines.append("")
    lines.append("Confusion Summary:")
    for expected in intents:
        incorrect = sum(confusion[expected].values()) - confusion[expected].get(expected, 0)
        if incorrect > 0:
            lines.append(f"\n{expected.capitalize()} queries misclassified as:")
            for predicted in intents + ['unknown']:
                if predicted != expected:
                    count = confusion[expected].get(predicted, 0)
                    if count > 0:
                        lines.append(f"  - {predicted}: {count} queries")

    lines.append("="*80)
    return "\n".join(lines)


def format_summary(metrics: Dict[str, Any]) -> str:
    """Format metrics into human-readable summary."""
    summary = []

    summary.append("="*80)
    summary.append("DIFFICULTY-STRATIFIED PERFORMANCE TEST RESULTS")
    summary.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    summary.append("="*80)
    summary.append("")

    # Overall metrics
    summary.append("📊 Overall Results")
    summary.append(f"   Total Queries:      {metrics['overall']['total_queries']}")
    summary.append(f"   Successful:         {metrics['overall']['successful_queries']} ({metrics['overall']['success_rate']:.1f}%)")
    summary.append(f"   Failed:             {metrics['overall']['failed_queries']}")
    summary.append(f"   Overall Accuracy:   {metrics['overall']['overall_accuracy']:.1f}% ({metrics['overall']['correct_count']}/{metrics['overall']['total_count']})")
    summary.append("")

    # Latency metrics
    summary.append("⚡ Query Latency")
    summary.append(f"   P50 (median):       {metrics['latency']['p50_seconds']:.3f}s")
    summary.append(f"   P90:                {metrics['latency']['p90_seconds']:.3f}s")
    summary.append(f"   P99:                {metrics['latency']['p99_seconds']:.3f}s")
    summary.append(f"   Mean:               {metrics['latency']['mean_seconds']:.3f}s")
    summary.append(f"   Range:              {metrics['latency']['min_seconds']:.3f}s - {metrics['latency']['max_seconds']:.3f}s")
    summary.append("")

    # Accuracy by difficulty tier
    summary.append("🎯 Accuracy by Difficulty Tier")
    for difficulty in ['easy', 'medium', 'hard']:
        tier = metrics['by_difficulty'].get(difficulty, {})
        if tier:
            emoji = "✅" if tier['accuracy'] >= 95 else "⚠️" if tier['accuracy'] >= 80 else "❌"
            summary.append(f"   {difficulty.capitalize():8s}: {emoji} {tier['accuracy']:.1f}% ({tier['correct']}/{tier['total']}) | Avg Latency: {tier['avg_latency']:.3f}s")
    summary.append("")

    # Intent accuracy by difficulty
    for difficulty in ['easy', 'medium', 'hard']:
        summary.append(f"📋 Intent Breakdown - {difficulty.capitalize()} Tier")
        intents = metrics['intent_by_difficulty'].get(difficulty, {})
        for intent, data in intents.items():
            emoji = "✅" if data['accuracy'] == 100 else "⚠️" if data['accuracy'] >= 80 else "❌"
            summary.append(f"   {intent:10s}: {emoji} {data['accuracy']:.1f}% ({data['correct']}/{data['total']})")
        summary.append("")

    # Overall intent accuracy
    summary.append("🎯 Overall Intent Accuracy (All Tiers)")
    for intent, data in metrics['intent_overall'].items():
        emoji = "✅" if data['accuracy'] >= 95 else "⚠️" if data['accuracy'] >= 80 else "❌"
        summary.append(f"   {intent:10s}: {emoji} {data['accuracy']:.1f}% ({data['correct']}/{data['total']})")
    summary.append("")

    # Database routing
    summary.append("🗄️  Database Routing")
    summary.append(f"   Most Used:          {metrics['database_routing']['most_used']}")
    summary.append("")
    summary.append("   Usage Distribution:")
    for db, count in sorted(metrics['database_routing']['usage_counts'].items(), key=lambda x: x[1], reverse=True):
        summary.append(f"      {db:12s}: {count} queries")
    summary.append("")

    # Failure analysis
    if metrics['failure_analysis']['total_failures'] > 0:
        summary.append("❌ Failure Analysis")
        summary.append(f"   Total Failures:     {metrics['failure_analysis']['total_failures']}")
        summary.append("")
        summary.append("   By Difficulty:")
        for difficulty, data in metrics['failure_analysis']['by_difficulty'].items():
            summary.append(f"      {difficulty.capitalize():8s}: {data['count']} failures ({data['percentage']:.1f}%)")
        summary.append("")

        if metrics['failure_analysis']['examples']:
            summary.append("   Example Failures:")
            for i, ex in enumerate(metrics['failure_analysis']['examples'][:5], 1):
                summary.append(f"\n   {i}. [{ex['difficulty'].upper()}] {ex['query']}")
                summary.append(f"      Expected: {ex['expected']} | Actual: {ex['actual']}")
                summary.append(f"      Rationale: {ex['rationale']}")
        summary.append("")

    # Success criteria evaluation
    summary.append("🎯 Success Criteria Evaluation")
    easy_acc = metrics['by_difficulty'].get('easy', {}).get('accuracy', 0)
    medium_acc = metrics['by_difficulty'].get('medium', {}).get('accuracy', 0)
    hard_acc = metrics['by_difficulty'].get('hard', {}).get('accuracy', 0)

    summary.append(f"   Easy tier ≥95%:     {'✅' if easy_acc >= 95 else '❌'} (actual: {easy_acc:.1f}%)")
    summary.append(f"   Medium tier ≥85%:   {'✅' if medium_acc >= 85 else '❌'} (actual: {medium_acc:.1f}%)")
    summary.append(f"   Hard tier ≥70%:     {'✅' if hard_acc >= 70 else '❌'} (actual: {hard_acc:.1f}%)")
    summary.append("")

    summary.append("="*80)

    return "\n".join(summary)


def main():
    """Main test execution."""
    # Parse arguments
    parser = argparse.ArgumentParser(
        description='Run difficulty-stratified query router performance tests'
    )
    parser.add_argument(
        '--test-suite',
        type=str,
        default='/Users/richardglaubitz/Projects/Apex-Memory-System-Development/tests/test-suites/difficulty-stratified-balanced-250.json',
        help='Path to test suite JSON file (default: difficulty-stratified-balanced-250.json)'
    )
    parser.add_argument(
        '--use-hybrid',
        action='store_true',
        help='Enable hybrid classifier (keyword + embeddings cascade)'
    )

    args = parser.parse_args()
    queries_path = Path(args.test_suite)
    use_hybrid = args.use_hybrid

    print("🚀 Starting Difficulty-Stratified Performance Testing")
    print("="*80)
    print(f"   Test Suite: {queries_path.name}")
    print(f"   Hybrid Classifier: {'✅ ENABLED' if use_hybrid else '❌ DISABLED (semantic only)'}")
    print("="*80)
    print("")

    # Check API health
    if not check_api_health():
        print("\n❌ API is not healthy. Exiting.")
        return

    print("")

    # Load queries
    print(f"📖 Loading queries from: {queries_path}")

    if not queries_path.exists():
        print(f"❌ Test suite not found: {queries_path}")
        return

    with open(queries_path, 'r') as f:
        data = json.load(f)

    queries = data['queries']
    print(f"✅ Loaded {len(queries)} test queries")
    print(f"   - Easy: {len([q for q in queries if q['difficulty'] == 'easy'])}")
    print(f"   - Medium: {len([q for q in queries if q['difficulty'] == 'medium'])}")
    print(f"   - Hard: {len([q for q in queries if q['difficulty'] == 'hard'])}")
    print("")

    print("🧪 Running stratified tests (cache disabled)...")
    print("="*80)

    # Run tests
    results = []
    for i, query_data in enumerate(queries, 1):
        result = run_query(query_data, i, len(queries), use_hybrid=use_hybrid)
        results.append(result)

        # Brief pause to avoid overwhelming API
        time.sleep(0.1)

    print("\n\n📊 Calculating metrics...")

    # Calculate metrics
    metrics = calculate_metrics(results)

    # Save detailed results
    results_file = RESULTS_DIR / "stratified_results.json"
    with open(results_file, 'w') as f:
        json.dump({
            "test_run": {
                "timestamp": datetime.now().isoformat(),
                "total_queries": len(queries),
                "test_suite": str(queries_path),
                "hybrid_classifier_enabled": use_hybrid,
                "api_endpoint": QUERY_ENDPOINT
            },
            "results": results,
            "metrics": metrics
        }, f, indent=2)

    print(f"✅ Detailed results saved to: {results_file}")

    # Save summary
    summary = format_summary(metrics)
    summary_file = RESULTS_DIR / "stratified_summary.txt"
    with open(summary_file, 'w') as f:
        f.write(summary)

    print(f"✅ Summary saved to: {summary_file}")

    # Save confusion matrix
    confusion_text = format_confusion_matrix(metrics['confusion_matrix'])
    confusion_file = RESULTS_DIR / "confusion_matrix.txt"
    with open(confusion_file, 'w') as f:
        f.write(confusion_text)

    print(f"✅ Confusion matrix saved to: {confusion_file}")
    print("")

    # Print summary to console
    print(summary)
    print(confusion_text)

    print(f"\n✅ Difficulty-stratified testing complete!")
    print(f"   - Detailed results: {results_file}")
    print(f"   - Summary report:   {summary_file}")
    print(f"   - Confusion matrix: {confusion_file}")
    print("")


if __name__ == "__main__":
    main()
