#!/usr/bin/env python3
"""
Fine-Tune Embeddings for Logistics Query Routing

This script fine-tunes BAAI/bge-base-en-v1.5 on logistics-specific queries
using triplet loss to create domain-specialized embeddings.

Usage:
    python train_embeddings.py \
        --dataset ../../config/training-queries-v7.json \
        --output ../models/apex-logistics-embeddings-v1 \
        --epochs 3

Expected training time on M4: 5-10 minutes for 3 epochs
"""

import argparse
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple
import random

from sentence_transformers import SentenceTransformer, InputExample, losses
from sentence_transformers.evaluation import TripletEvaluator
from torch.utils.data import DataLoader

# Reason: Configure logging for training progress
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_logistics_dataset(dataset_path: str) -> Tuple[List[str], List[str], Dict]:
    """
    Load logistics dataset v7.0 from JSON.

    Args:
        dataset_path: Path to training-queries-v7.json

    Returns:
        Tuple of (route_queries, training_queries, route_definitions)
    """
    logger.info(f"Loading dataset from {dataset_path}")

    with open(dataset_path, 'r') as f:
        data = json.load(f)

    # Extract route definitions (80 queries)
    route_queries = []
    route_labels = {}

    for intent, intent_data in data['route_definitions'].items():
        for query in intent_data['utterances']:
            route_queries.append(query)
            route_labels[query] = intent

    # Extract training queries (234 queries)
    training_queries = data['training_data']['queries']
    training_labels = data['training_data']['labels']

    logger.info(f"Loaded {len(route_queries)} route definitions")
    logger.info(f"Loaded {len(training_queries)} training queries")
    logger.info(f"Dataset version: {data['metadata']['version']}")

    return route_queries, route_labels, training_queries, training_labels, data['route_definitions']


def create_triplet_examples(
    route_queries: List[str],
    route_labels: Dict[str, str],
    training_queries: List[str],
    training_labels: List[str]
) -> List[InputExample]:
    """
    Create triplet training examples: (anchor, positive, negative).

    For each training query:
    - Anchor: The training query
    - Positive: A route definition with the same intent
    - Negative: A route definition with a different intent

    Args:
        route_queries: List of route definition queries
        route_labels: Mapping of route query → intent label
        training_queries: List of training queries
        training_labels: List of intent labels for training queries

    Returns:
        List of InputExample triplets
    """
    logger.info("Creating triplet examples for training...")

    # Group route queries by intent
    routes_by_intent = {}
    for query, intent in route_labels.items():
        if intent not in routes_by_intent:
            routes_by_intent[intent] = []
        routes_by_intent[intent].append(query)

    triplets = []

    for query, label in zip(training_queries, training_labels):
        # Anchor: training query
        anchor = query

        # Positive: random route definition with same intent
        positive_routes = routes_by_intent.get(label, [])
        if not positive_routes:
            logger.warning(f"No route definitions for intent '{label}', skipping query: {query}")
            continue
        positive = random.choice(positive_routes)

        # Negative: random route definition with different intent
        other_intents = [intent for intent in routes_by_intent.keys() if intent != label]
        if not other_intents:
            logger.warning(f"No other intents to create negative for: {query}")
            continue
        negative_intent = random.choice(other_intents)
        negative = random.choice(routes_by_intent[negative_intent])

        # Create InputExample
        triplets.append(InputExample(texts=[anchor, positive, negative]))

    logger.info(f"Created {len(triplets)} triplet examples")
    return triplets


def train_model(
    base_model: str,
    triplets: List[InputExample],
    output_path: str,
    epochs: int = 3,
    batch_size: int = 16,
    warmup_steps: int = 10
):
    """
    Fine-tune sentence transformer using triplet loss.

    Args:
        base_model: HuggingFace model name (e.g., 'BAAI/bge-base-en-v1.5')
        triplets: List of triplet training examples
        output_path: Where to save the trained model
        epochs: Number of training epochs
        batch_size: Training batch size
        warmup_steps: Learning rate warmup steps
    """
    logger.info(f"Loading base model: {base_model}")
    model = SentenceTransformer(base_model)

    # Create DataLoader
    train_dataloader = DataLoader(triplets, shuffle=True, batch_size=batch_size)

    # Define loss function: BatchHardTripletLoss
    # Reason: Selects hardest negatives in batch for more effective learning
    train_loss = losses.BatchHardTripletLoss(
        model=model,
        distance_metric=losses.BatchHardTripletLossDistanceFunction.cosine_distance,
        margin=0.5
    )

    logger.info(f"Training configuration:")
    logger.info(f"  - Epochs: {epochs}")
    logger.info(f"  - Batch size: {batch_size}")
    logger.info(f"  - Warmup steps: {warmup_steps}")
    logger.info(f"  - Training examples: {len(triplets)}")
    logger.info(f"  - Steps per epoch: {len(train_dataloader)}")
    logger.info(f"  - Total steps: {len(train_dataloader) * epochs}")

    # Train the model
    logger.info("Starting training... (5-10 minutes on M4)")
    model.fit(
        train_objectives=[(train_dataloader, train_loss)],
        epochs=epochs,
        warmup_steps=warmup_steps,
        output_path=output_path,
        show_progress_bar=True,
        save_best_model=True
    )

    logger.info(f"✅ Training complete! Model saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Fine-tune embeddings for logistics query routing'
    )
    parser.add_argument(
        '--dataset',
        type=str,
        required=True,
        help='Path to training-queries-v7.json'
    )
    parser.add_argument(
        '--base-model',
        type=str,
        default='BAAI/bge-base-en-v1.5',
        help='Base model to fine-tune (default: BAAI/bge-base-en-v1.5)'
    )
    parser.add_argument(
        '--output',
        type=str,
        required=True,
        help='Output directory for trained model'
    )
    parser.add_argument(
        '--epochs',
        type=int,
        default=3,
        help='Number of training epochs (default: 3)'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=16,
        help='Training batch size (default: 16)'
    )
    parser.add_argument(
        '--warmup-steps',
        type=int,
        default=10,
        help='Learning rate warmup steps (default: 10)'
    )

    args = parser.parse_args()

    # Load dataset
    route_queries, route_labels, training_queries, training_labels, route_defs = load_logistics_dataset(
        args.dataset
    )

    # Create triplet examples
    triplets = create_triplet_examples(
        route_queries,
        route_labels,
        training_queries,
        training_labels
    )

    # Train model
    train_model(
        base_model=args.base_model,
        triplets=triplets,
        output_path=args.output,
        epochs=args.epochs,
        batch_size=args.batch_size,
        warmup_steps=args.warmup_steps
    )

    logger.info("🎉 Fine-tuning complete!")
    logger.info(f"Next steps:")
    logger.info(f"  1. Export model: python export_model.py --input {args.output}")
    logger.info(f"  2. Update semantic_classifier.py to use HuggingFaceEncoder")
    logger.info(f"  3. Run stratified test to validate improvements")


if __name__ == '__main__':
    main()
